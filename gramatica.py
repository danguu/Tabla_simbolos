GRAMATICA = """
Programa   -> ListaSentencias EOF

ListaSentencias -> Sentencia (NEWLINE Sentencia)* NEWLINE*

Sentencia  -> ID '=' Expresion
            | 'print' '(' Expresion ')'

Expresion  -> Termino (('+' | '-') Termino)*

Termino    -> Factor (('*' | '/') Factor)*

Factor     -> NUM
            | ID
            | '(' Expresion ')'
"""

DESCRIPCION_TOKENS = """
Tokens:
  ID       : identificadores (letras, dígitos, '_', empezando por letra o '_')
  NUM      : números reales (ej: 3, 4.5, 10.0)
  '='      : asignación
  '+' '-'  : suma y resta
  '*' '/'  : multiplicación y división
  '(' ')'  : paréntesis
  NEWLINE  : fin de línea (separa sentencias)
  PRINT    : palabra reservada 'print'
  EOF      : fin de entrada
"""
