from gramatica import GRAMATICA, DESCRIPCION_TOKENS  # noqa: F401

#  Definición de tokens

TT_ID = "ID"
TT_NUM = "NUM"
TT_EQ = "="
TT_PLUS = "+"
TT_MINUS = "-"
TT_MUL = "*"
TT_DIV = "/"
TT_LPAREN = "("
TT_RPAREN = ")"
TT_NEWLINE = "NEWLINE"
TT_EOF = "EOF"
TT_PRINT = "PRINT"

KEYWORDS = {
    "print": TT_PRINT,
}


class Token:
    def __init__(self, type_, value=None, line=1, col=1):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        if self.value is None:
            return f"{self.type}"
        return f"{self.type}({self.value})"


#  LEXER (análisis léxico)


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1

    def current_char(self):
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def advance(self):
        ch = self.current_char()
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.pos += 1

    def skip_whitespace(self):
        while self.current_char() is not None and self.current_char() in " \t\r":
            self.advance()

    def number(self):
        start_line, start_col = self.line, self.col
        num_str = ""
        while self.current_char() is not None and (
            self.current_char().isdigit() or self.current_char() == "."
        ):
            num_str += self.current_char()
            self.advance()
        return Token(TT_NUM, float(num_str), start_line, start_col)

    def identifier(self):
        start_line, start_col = self.line, self.col
        ident = ""
        while self.current_char() is not None and (
            self.current_char().isalnum() or self.current_char() == "_"
        ):
            ident += self.current_char()
            self.advance()
        if ident in KEYWORDS:
            return Token(KEYWORDS[ident], ident, start_line, start_col)
        return Token(TT_ID, ident, start_line, start_col)

    def get_tokens(self):
        tokens = []
        while True:
            ch = self.current_char()
            if ch is None:
                tokens.append(Token(TT_EOF, None, self.line, self.col))
                break

            if ch in " \t\r":
                self.skip_whitespace()
                continue

            if ch == "\n":
                tokens.append(Token(TT_NEWLINE, None, self.line, self.col))
                self.advance()
                continue

            if ch.isdigit():
                tokens.append(self.number())
                continue

            if ch.isalpha() or ch == "_":
                tokens.append(self.identifier())
                continue

            if ch == "=":
                tokens.append(Token(TT_EQ, ch, self.line, self.col))
                self.advance()
                continue

            if ch == "+":
                tokens.append(Token(TT_PLUS, ch, self.line, self.col))
                self.advance()
                continue

            if ch == "-":
                tokens.append(Token(TT_MINUS, ch, self.line, self.col))
                self.advance()
                continue

            if ch == "*":
                tokens.append(Token(TT_MUL, ch, self.line, self.col))
                self.advance()
                continue

            if ch == "/":
                tokens.append(Token(TT_DIV, ch, self.line, self.col))
                self.advance()
                continue

            if ch == "(":
                tokens.append(Token(TT_LPAREN, ch, self.line, self.col))
                self.advance()
                continue

            if ch == ")":
                tokens.append(Token(TT_RPAREN, ch, self.line, self.col))
                self.advance()
                continue

            # Caracter no reconocido
            raise Exception(
                "Caracter ilegal %r en linea %d, columna %d" % (ch, self.line, self.col)
            )

        return tokens


#  AST (árbol de sintaxis abstracta)


class Node:
    pass


class Program(Node):
    def __init__(self, statements):
        self.statements = statements


class Assign(Node):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr


class Print(Node):
    def __init__(self, expr):
        self.expr = expr


class BinOp(Node):
    def __init__(self, op, left, right):
        self.op = op  # tipo de token: TT_PLUS, TT_MINUS, etc.
        self.left = left
        self.right = right


class Num(Node):
    def __init__(self, value):
        self.value = value


class Var(Node):
    def __init__(self, name):
        self.name = name


#  PARSER (análisis sintáctico / EDTS base)


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos]

    def eat(self, type_):
        tok = self.current()
        if tok.type == type_:
            self.pos += 1
            return tok
        raise ParserError(
            "Se esperaba %s y se encontró %s (linea %d, col %d)"
            % (type_, tok.type, tok.line, tok.col)
        )

    def parse(self):
        """
        Programa -> ListaSentencias EOF
        """
        stmts = self.parse_stmt_list()
        if self.current().type != TT_EOF:
            raise ParserError("Entrada extra después del fin del programa")
        return Program(stmts)

    def parse_stmt_list(self):
        """
        ListaSentencias -> Sentencia (NEWLINE Sentencia)* NEWLINE*
        """
        stmts = []

        # Saltar NEWLINE iniciales
        while self.current().type == TT_NEWLINE:
            self.eat(TT_NEWLINE)

        while self.current().type in (TT_ID, TT_PRINT):
            stmts.append(self.parse_stmt())
            # Consumir uno o más NEWLINE
            while self.current().type == TT_NEWLINE:
                self.eat(TT_NEWLINE)

        return stmts

    def parse_stmt(self):
        """
        Sentencia -> ID '=' Expresion
                   | 'print' '(' Expresion ')'
        """
        tok = self.current()

        if tok.type == TT_ID:
            name = self.eat(TT_ID).value
            self.eat(TT_EQ)
            expr = self.parse_expr()
            return Assign(name, expr)

        if tok.type == TT_PRINT:
            self.eat(TT_PRINT)
            self.eat(TT_LPAREN)
            expr = self.parse_expr()
            self.eat(TT_RPAREN)
            return Print(expr)

        raise ParserError(
            "Inicio de sentencia inesperado: %s (linea %d)" % (tok.type, tok.line)
        )

    def parse_expr(self):
        """
        Expresion -> Termino (('+' | '-') Termino)*
        """
        node = self.parse_term()
        while self.current().type in (TT_PLUS, TT_MINUS):
            op_tok = self.current()
            if op_tok.type == TT_PLUS:
                self.eat(TT_PLUS)
            else:
                self.eat(TT_MINUS)
            right = self.parse_term()
            node = BinOp(op_tok.type, node, right)
        return node

    def parse_term(self):
        """
        Termino -> Factor (('*' | '/') Factor)*
        """
        node = self.parse_factor()
        while self.current().type in (TT_MUL, TT_DIV):
            op_tok = self.current()
            if op_tok.type == TT_MUL:
                self.eat(TT_MUL)
            else:
                self.eat(TT_DIV)
            right = self.parse_factor()
            node = BinOp(op_tok.type, node, right)
        return node

    def parse_factor(self):
        """
        Factor -> NUM
                | ID
                | '(' Expresion ')'
        """
        tok = self.current()

        if tok.type == TT_NUM:
            self.eat(TT_NUM)
            return Num(tok.value)

        if tok.type == TT_ID:
            self.eat(TT_ID)
            return Var(tok.value)

        if tok.type == TT_LPAREN:
            self.eat(TT_LPAREN)
            expr = self.parse_expr()
            self.eat(TT_RPAREN)
            return expr

        raise ParserError(
            "Factor inesperado %s (linea %d, col %d)" % (tok.type, tok.line, tok.col)
        )


#  TABLA DE SÍMBOLOS (atributos)


def construir_tabla_simbolos(ast):
    """
    Recorre el AST y construye una tabla de símbolos muy simple.
    name -> { 'tipo': 'num', 'ocurrencias': N }
    """
    tabla = {}

    def visitar(nodo):
        if isinstance(nodo, Program):
            for s in nodo.statements:
                visitar(s)

        elif isinstance(nodo, Assign):
            info = tabla.get(nodo.name)
            if info is None:
                info = {"tipo": "num", "ocurrencias": 0}
                tabla[nodo.name] = info
            info["ocurrencias"] += 1
            visitar(nodo.expr)

        elif isinstance(nodo, Print):
            visitar(nodo.expr)

        elif isinstance(nodo, BinOp):
            visitar(nodo.left)
            visitar(nodo.right)

        elif isinstance(nodo, Var):
            info = tabla.get(nodo.name)
            if info is None:
                info = {"tipo": "num", "ocurrencias": 0}
                tabla[nodo.name] = info
            info["ocurrencias"] += 1

        elif isinstance(nodo, Num):
            # No se agrega a la tabla de símbolos
            pass

    visitar(ast)
    return tabla


#  GENERACIÓN DE CÓDIGO EN TRES DIRECCIONES


class TacGenerator:
    def __init__(self):
        self.temp_count = 0
        self.code = []

    def nuevo_temp(self):
        self.temp_count += 1
        return "t%d" % self.temp_count

    def generar(self, ast):
        self.code = []
        if isinstance(ast, Program):
            for stmt in ast.statements:
                self.gen_stmt(stmt)
        else:
            self.gen_stmt(ast)
        return self.code

    def gen_stmt(self, nodo):
        if isinstance(nodo, Assign):
            place = self.gen_expr(nodo.expr)
            self.code.append("%s = %s" % (nodo.name, place))

        elif isinstance(nodo, Print):
            place = self.gen_expr(nodo.expr)
            self.code.append("print %s" % place)

        else:
            raise Exception("Sentencia desconocida en TAC")

    def gen_expr(self, nodo):
        if isinstance(nodo, Num):
            tmp = self.nuevo_temp()
            self.code.append("%s = %s" % (tmp, nodo.value))
            return tmp

        if isinstance(nodo, Var):
            # El "place" de una variable es su propio nombre
            return nodo.name

        if isinstance(nodo, BinOp):
            left_place = self.gen_expr(nodo.left)
            right_place = self.gen_expr(nodo.right)
            tmp = self.nuevo_temp()

            if nodo.op == TT_PLUS:
                op = "+"
            elif nodo.op == TT_MINUS:
                op = "-"
            elif nodo.op == TT_MUL:
                op = "*"
            elif nodo.op == TT_DIV:
                op = "/"
            else:
                raise Exception("Operador desconocido en TAC")

            self.code.append("%s = %s %s %s" % (tmp, left_place, op, right_place))
            return tmp

        raise Exception("Nodo de expresión desconocido en TAC")


#  Funciones de utilidad para imprimir AST / tabla / TAC


def ast_a_string(ast, indent=""):
    """
    Devuelve una representación en texto del AST (para ast.txt).
    """
    espacio = indent
    if isinstance(ast, Program):
        s = espacio + "Program\n"
        for stmt in ast.statements:
            s += ast_a_string(stmt, indent + "  ")
        return s

    if isinstance(ast, Assign):
        s = espacio + "Assign(name=%s)\n" % ast.name
        s += ast_a_string(ast.expr, indent + "  ")
        return s

    if isinstance(ast, Print):
        s = espacio + "Print\n"
        s += ast_a_string(ast.expr, indent + "  ")
        return s

    if isinstance(ast, BinOp):
        s = espacio + "BinOp(op=%s)\n" % ast.op
        s += ast_a_string(ast.left, indent + "  ")
        s += ast_a_string(ast.right, indent + "  ")
        return s

    if isinstance(ast, Num):
        return espacio + "Num(%s)\n" % ast.value

    if isinstance(ast, Var):
        return espacio + "Var(%s)\n" % ast.name

    return espacio + "Nodo_desconocido\n"


def tabla_simbolos_a_string(tabla):
    """
    Convierte la tabla de símbolos en texto (para tabla_simbolos.txt).
    """
    lineas = []
    lineas.append("== Tabla de símbolos ==")
    for nombre in sorted(tabla.keys()):
        info = tabla[nombre]
        lineas.append(
            "%-10s tipo=%s ocurrencias=%d" % (nombre, info["tipo"], info["ocurrencias"])
        )
    return "\n".join(lineas) + "\n"


def tac_a_string(tac_code):
    """
    Convierte la lista de instrucciones TAC en texto (para tac.txt).
    """
    lineas = ["== Código en tres direcciones =="]
    for inst in tac_code:
        lineas.append(inst)
    return "\n".join(lineas) + "\n"


#  Función principal de análisis (EDTS completa)


def analizar_codigo_fuente(texto_fuente):
    """
    Ejecuta todo el pipeline:
      - Lexer
      - Parser (construcción del AST)
      - Tabla de símbolos
      - Código de tres direcciones

    Devuelve: (ast, tabla_simbolos, tac_code)
    """
    lexer = Lexer(texto_fuente)
    tokens = lexer.get_tokens()

    parser = Parser(tokens)
    ast = parser.parse()

    tabla = construir_tabla_simbolos(ast)

    generador_tac = TacGenerator()
    tac_code = generador_tac.generar(ast)

    return ast, tabla, tac_code
