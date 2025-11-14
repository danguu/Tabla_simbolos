from funciones import (
    analizar_codigo_fuente,
    ast_a_string,
    tabla_simbolos_a_string,
    tac_a_string,
)
from gramatica import GRAMATICA


def main():
    # 1) Leer el código fuente (subconjunto de Python) desde entrada.py
    with open("entrada.py", "r", encoding="utf-8") as f:
        fuente = f.read()

    # 2) Analizar (EDTS: AST, tabla de símbolos, código 3 direcciones)
    ast, tabla, tac_code = analizar_codigo_fuente(fuente)

    # 3) Generar y guardar el AST decorado en texto
    with open("ast.txt", "w", encoding="utf-8") as f_ast:
        f_ast.write("== Gramática ==\n")
        f_ast.write(GRAMATICA)
        f_ast.write("\n\n== AST ==\n")
        f_ast.write(ast_a_string(ast))

    # 4) Guardar tabla de símbolos
    with open("tabla_simbolos.txt", "w", encoding="utf-8") as f_ts:
        f_ts.write(tabla_simbolos_a_string(tabla))

    # 5) Guardar código en tres direcciones
    with open("tac.txt", "w", encoding="utf-8") as f_tac:
        f_tac.write(tac_a_string(tac_code))


main()
