import sys
import re
from collections import namedtuple

# Definición de la clase Token
Token = namedtuple('Token', ['tipo', 'valor', 'linea', 'columna'])

# Definición de los patrones para los tokens
especificacion_tokens = [
    ('DEF',      r'\bdef\b'),                           # Palabra clave 'def' para definir funciones
    ('IF',       r'\bif\b'),                            # Palabra clave 'if' para estructuras condicionales
    ('ELSE',     r'\belse\b'),                          # Palabra clave 'else' para estructuras condicionales
    ('FOR',      r'\bfor\b'),                           # Palabra clave 'for' para bucles
    ('WHILE',    r'\bwhile\b'),                         # Palabra clave 'while' para bucles
    ('BREAK',    r'\bbreak\b'),                         # Palabra clave 'break' para salir de bucles
    ('CONTINUE', r'\bcontinue\b'),                      # Palabra clave 'continue' para saltar iteraciones de bucles
    ('RETURN',   r'\breturn\b'),                        # Palabra clave 'return' para devolver valores en funciones
    ('PRINT',    r'\bprint\b'),                         # Palabra clave 'print' para imprimir valores
    ('IN',       r'\bin\b'),                            # Palabra clave 'in' para bucles y membresía
    ('ARROW',    r'->'),                                # Flecha para anotación de tipo de retorno en funciones
    ('NUMBER',   r'\d+(\.\d*)?'),                       # Números enteros o decimales
    ('OP',       r'==|!=|>=|<=|>|<|\+|\-|\*|\/|%|\band\b|\bor\b|\bnot\b'),  # Operadores
    ('ASSIGN',   r'='),                                 # Operador de asignación
    ('COLON',    r':'),                                 # Dos puntos
    ('COMMA',    r','),                                 # Coma
    ('LPAREN',   r'\('),                                # Paréntesis izquierdo
    ('RPAREN',   r'\)'),                                # Paréntesis derecho
    ('LBRACKET', r'\['),                                # Corchete izquierdo
    ('RBRACKET', r'\]'),                                # Corchete derecho
    ('STRING',   r'(\'\'\'[\s\S]*?\'\'\'|"""[\s\S]*?"""|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')'),  # Cadenas
    ('NEWLINE',  r'\n'),                                # Nueva línea
    ('SKIP',     r'[ \t]+'),                            # Espacios y tabulaciones
    ('COMMENT',  r'\#.*'),                              # Comentarios
    ('ID',       r'[A-Za-z_]\w*'),                      # Identificadores
    ('MISMATCH', r'.'),                                 # Cualquier otro carácter
]

def tokenizar(codigo):
    tokens = []
    numero_linea = 1
    inicio_linea = 0
    pila_indentacion = [0]
    regex_tokens = '|'.join('(?P<%s>%s)' % par for par in especificacion_tokens)
    obtener_token = re.compile(regex_tokens).match
    pos = 0
    mo = obtener_token(codigo, pos)
    while mo is not None:
        tipo = mo.lastgroup
        valor = mo.group(tipo)
        if tipo == 'NEWLINE':
            tokens.append(Token(tipo, valor, numero_linea, mo.start()-inicio_linea))
            pos = mo.end()
            numero_linea += 1
            inicio_linea = pos
            coincidencia_indentacion = re.match(r'[ \t]*', codigo[pos:])
            if coincidencia_indentacion:
                indentacion = coincidencia_indentacion.group(0)
                nivel_indentacion = len(indentacion.replace('\t', '    '))
                pos += len(indentacion)
                if nivel_indentacion > pila_indentacion[-1]:
                    pila_indentacion.append(nivel_indentacion)
                    tokens.append(Token('INDENT', indentacion, numero_linea, 0))
                elif nivel_indentacion < pila_indentacion[-1]:
                    while nivel_indentacion < pila_indentacion[-1]:
                        pila_indentacion.pop()
                        tokens.append(Token('DEDENT', '', numero_linea, 0))
                    if nivel_indentacion != pila_indentacion[-1]:
                        raise SyntaxError(f'<{numero_linea},{nivel_indentacion}> Error de indentación')
            mo = obtener_token(codigo, pos)
            continue
        elif tipo == 'SKIP' or tipo == 'COMMENT':
            pos = mo.end()
            mo = obtener_token(codigo, pos)
            continue
        elif tipo == 'MISMATCH':
            raise SyntaxError(f'<{numero_linea},{mo.start()-inicio_linea}> Error léxico: "{valor}"')
        else:
            tokens.append(Token(tipo, valor, numero_linea, mo.start()-inicio_linea))
        pos = mo.end()
        mo = obtener_token(codigo, pos)
    while len(pila_indentacion) > 1:
        pila_indentacion.pop()
        tokens.append(Token('DEDENT', '', numero_linea, 0))
    tokens.append(Token('EOF', '', numero_linea, pos - inicio_linea))
    return tokens

class AnalizadorSintactico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.actual = 0
        self.error = None

    def analizar(self):
        try:
            while self.actual < len(self.tokens):
                if self.ver_actual().tipo == 'EOF':
                    break
                self.declaracion()
            return True
        except SyntaxError as e:
            self.error = str(e)
            return False

    def declaracion(self):
        token = self.ver_actual()
        if token.tipo == 'DEF':
            self.def_funcion()
        elif token.tipo == 'IF':
            self.declaracion_if()
        elif token.tipo == 'FOR':
            self.declaracion_for()
        elif token.tipo == 'WHILE':
            self.declaracion_while()
        elif token.tipo == 'PRINT':
            self.declaracion_print()
        elif token.tipo == 'ID':
            # Verificar si es una asignación
            if self.ver_siguiente().tipo == 'ASSIGN':
                self.asignacion()
            else:
                self.expresion()
        elif token.tipo == 'RETURN':
            self.declaracion_return()
        elif token.tipo == 'BREAK' or token.tipo == 'CONTINUE':
            self.avanzar()
        elif token.tipo == 'NEWLINE':
            self.avanzar()
        else:
            self.error_inesperado(token, ['def', 'if', 'for', 'while', 'print', 'return', 'break', 'continue', 'expression'])

    def def_funcion(self):
        self.esperar('DEF')
        self.esperar('ID')
        self.esperar('LPAREN')
        self.parametros()
        self.esperar('RPAREN')
        if self.ver_actual().tipo == 'ARROW':
            self.avanzar()
            self.esperar('ID')
        self.esperar('COLON')
        self.bloque()

    def parametros(self):
        if self.ver_actual().tipo == 'RPAREN':
            return
        self.parametro()
        while self.ver_actual().tipo == 'COMMA':
            self.esperar('COMMA')
            self.parametro()

    def parametro(self):
        self.esperar('ID')
        if self.ver_actual().tipo == 'COLON':
            self.esperar('COLON')
            self.anotacion_tipo()

    def anotacion_tipo(self):
        if self.ver_actual().tipo == 'LBRACKET':
            self.esperar('LBRACKET')
            self.esperar('ID')
            self.esperar('RBRACKET')
        else:
            self.esperar('ID')

    def bloque(self):
        self.esperar('NEWLINE')
        self.esperar('INDENT')
        while self.ver_actual().tipo != 'DEDENT' and self.ver_actual().tipo != 'EOF':
            self.declaracion()
        self.esperar('DEDENT')

    def declaracion_if(self):
        self.esperar('IF')
        self.expresion()
        self.esperar('COLON')
        self.bloque()
        if self.ver_actual().tipo == 'ELSE':
            self.esperar('ELSE')
            self.esperar('COLON')
            self.bloque()

    def declaracion_for(self):
        self.esperar('FOR')
        self.esperar('ID')
        self.esperar('IN')
        self.expresion()
        self.esperar('COLON')
        self.bloque()

    def declaracion_while(self):
        self.esperar('WHILE')
        self.expresion()
        self.esperar('COLON')
        self.bloque()

    def declaracion_print(self):
        self.esperar('PRINT')
        self.esperar('LPAREN')
        self.lista_argumentos()
        self.esperar('RPAREN')

    def lista_argumentos(self):
        """
        Procesa una lista de argumentos separados por comas.
        """
        self.expresion()
        while self.ver_actual().tipo == 'COMMA':
            self.esperar('COMMA')
            self.expresion()

    def declaracion_return(self):
        self.esperar('RETURN')
        if self.ver_actual().tipo != 'NEWLINE' and self.ver_actual().tipo != 'DEDENT':
            self.expresion()

    def asignacion(self):
        self.esperar('ID')
        self.esperar('ASSIGN')
        self.expresion()

    def expresion(self):
        self.termino()
        while self.ver_actual().tipo == 'OP':
            self.esperar('OP')
            self.termino()

    def termino(self):
        token = self.ver_actual()
        if token.tipo == 'ID':
            self.avanzar()
            if self.ver_actual().tipo == 'LPAREN':
                self.esperar('LPAREN')
                if self.ver_actual().tipo != 'RPAREN':
                    self.lista_argumentos()
                self.esperar('RPAREN')
        elif token.tipo in ('NUMBER', 'STRING'):
            self.avanzar()
        elif token.tipo == 'LPAREN':
            self.esperar('LPAREN')
            self.expresion()
            self.esperar('RPAREN')
        elif token.tipo == 'LBRACKET':
            self.esperar('LBRACKET')
            if self.ver_actual().tipo != 'RBRACKET':
                self.lista_argumentos()
            self.esperar('RBRACKET')
        else:
            self.error_inesperado(token, ['IDENTIFICADOR', 'NÚMERO', 'CADENA', '(', '['])

    def ver_actual(self):
        if self.actual < len(self.tokens):
            return self.tokens[self.actual]
        else:
            return Token('EOF', '', -1, -1)

    def ver_siguiente(self):
        if self.actual + 1 < len(self.tokens):
            return self.tokens[self.actual + 1]
        else:
            return Token('EOF', '', -1, -1)

    def avanzar(self):
        self.actual += 1

    def esperar(self, tipo, valor=None):
        token = self.ver_actual()
        if token.tipo == tipo and (valor is None or token.valor == valor):
            self.avanzar()
        else:
            esperado = valor if valor else tipo
            self.error_inesperado(token, [esperado])

    def error_inesperado(self, token, esperado):
        encontrado = 'EOF' if token.tipo == 'EOF' else token.valor
        linea, columna = token.linea, token.columna
        esperado_str = ', '.join(f'"{e}"' for e in esperado)
        raise SyntaxError(f'<{linea},{columna}> Error sintactico: se encontro: "{encontrado}"; se esperaba: {esperado_str}')

def main():
    if len(sys.argv) != 2:
        print("Uso: python parser.py <archivo_entrada.py>")
        return

    archivo_entrada = sys.argv[1]
    archivo_salida = 'salida.txt'

    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            codigo = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo {archivo_entrada} no existe.")
        return

    try:
        tokens = tokenizar(codigo)
    except SyntaxError as e:
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(str(e))
        return

    parser = AnalizadorSintactico(tokens)
    exito = parser.analizar()

    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write("El analisis sintactico ha finalizado exitosamente." if exito else parser.error)

if __name__ == '__main__':
    main()
