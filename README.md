# Tabla_simbolos

Este proyecto implementa **una ETDS (Estructura de Traducción Dirigida por la Sintaxis)** para un **subconjunto reducido del lenguaje Python**, permitiendo:

* Procesar asignaciones.
* Procesar sentencias `print(expr)`.
* Procesar expresiones aritméticas con `+ - * /` y paréntesis.
* Construir **AST** (árbol sintáctico).
* Construir **tabla de símbolos**.
* Generar **código en tres direcciones (TAC)**.
* Mostrar la **gramática** usada.

Todo se realiza **sin ninguna librería externa**, únicamente con Python estándar.

# 1. Estructura del Proyecto

```
/Proyecto
- main.py
- funciones.py
- gramatica.py
- entrada.py     ← Código fuente a analizar

- ast.txt              ← AST resultante
- tabla_simbolos.txt   ← Tabla de símbolos resultante
- tac.txt              ← Código en tres direcciones
```

# 2. Descripción de cada archivo

## **gramatica.py**

Define la **Gramática Independiente de Contexto** utilizada por el parser.

Incluye:

* Producciones formales (GIC).
* Descripción de los tokens.
* No analiza nada: solo documenta la gramática.

Gramática usada:

```
Programa   -> ListaSentencias EOF
ListaSentencias -> Sentencia (NEWLINE Sentencia)* NEWLINE*
Sentencia  -> ID '=' Expresion
            | 'print' '(' Expresion ')'
Expresion  -> Termino (('+' | '-') Termino)*
Termino    -> Factor (('*' | '/') Factor)*
Factor     -> NUM
            | ID
            | '(' Expresion ')'
```

Es un **subconjunto de Python**, suficiente para asignaciones y `print(expr)`.

## **funciones.py**

Contiene toda la **lógica del compilador**:

### 1. **Lexer**

Convierte texto en una secuencia de tokens:

* ID
* NUM
* `+ - * / = ( )`
* NEWLINE
* PRINT
* EOF

El lexer:

* Ignora espacios.
* Conserva números como `float`.
* Identifica palabras reservadas (solo `print`).

### 2. **Parser**

Implementa un **analizador descendente recursivo** basado en la gramática.

Construye el **AST**:

* `Program`
* `Assign`
* `Print`
* `BinOp`
* `Num`
* `Var`

Si encuentra un error → lanza `ParserError`.

### 3. **EDTS: Atributos**

Genera la **tabla de símbolos** recorriendo el AST:

* Cada variable recibe:

  * tipo = `num`
  * ocurrencias = cuántas veces aparece

No se infieren tipos complejos porque el lenguaje lo permite.

### 4. **Código en Tres Direcciones (TAC)**

A partir del AST genera instrucciones:

```
t1 = 3.0
t2 = 4.0
t3 = 2.0
t4 = t2 * t3
t5 = t1 + t4
x = t5
```

Cada operación crea un temporal (`t1`, `t2`, …).

**Soporta:**

* Suma
* Resta
* Multiplicación
* División
* Uso de variables y constantes
* Sentencias print 

### 5. Funciones auxiliares

* Para convertir AST → texto.
* Para convertir tabla de símbolos → texto.
* Para convertir TAC → texto.

## **main.py**

Orquesta todo el proceso:

1. Lee `entrada.py`.
2. Ejecuta:

   * Lexer
   * Parser
   * Construcción de AST
   * Tabla de símbolos
   * TAC
3. Genera los archivos:

   * `ast.txt`
   * `tabla_simbolos.txt`
   * `tac.txt`

## **entrada.py**

Archivo que contiene el código fuente que quieres analizar.

Ejemplo:

```python
x = 3 + 4*2
y = x - 1
print(y)
```

Puedes escribir cualquier combinación válida según la gramática.


# 3. Cómo Ejecutar el Proyecto

### 1. Asegúrate de tener Python 3 instalado.

### 2. En la terminal, en la carpeta del proyecto:

```bash
python3 main.py
```

### 3. Se generan automáticamente los archivos:

* `ast.txt`
* `tabla_simbolos.txt`
* `tac.txt`

# 4. Qué Produce el Sistema

## **AST (ast.txt)**

Estructura jerárquica del programa.

Ejemplo:

```
Program
  Assign(name=x)
    BinOp(op=+)
      Num(3.0)
      BinOp(op=*)
        Num(4.0)
        Num(2.0)
```

## **Tabla de Símbolos (tabla_simbolos.txt)**

```
== Tabla de símbolos ==
x          tipo=num ocurrencias=2
y          tipo=num ocurrencias=2
```

## **Código en Tres Direcciones (tac.txt)**

```
== Código en tres direcciones ==
t1 = 3.0
t2 = 4.0
t3 = 2.0
t4 = t2 * t3
t5 = t1 + t4
x = t5
t6 = 1.0
t7 = x - t6
y = t7
print y
```
