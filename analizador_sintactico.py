import ply.yacc as yacc
from analizador_lexico import tokens, lexer


# NODOS DEL AST


class Node:
    pass


class Program(Node):
    def __init__(self, stmts):
        self.stmts = stmts


class VarDecl(Node):
    def __init__(self, name, tipo):
        self.name, self.tipo = name, tipo


class Assign(Node):
    def __init__(self, name, expr):
        self.name, self.expr = name, expr


class Captura(Node):
    def __init__(self, tipo):
        self.tipo = tipo


class Mensaje(Node):
    def __init__(self, texto):
        self.texto = texto


class BinaryOp(Node):
    def __init__(self, op, left, right):
        self.op, self.left, self.right = op, left, right


class Number(Node):
    def __init__(self, value, kind):
        self.value, self.kind = value, kind


class String(Node):
    def __init__(self, value):
        self.value = value


class VarRef(Node):
    def __init__(self, name):
        self.name = name


# PRECEDENCIA

precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
)

start = "program"


# PRODUCCIONES

def p_program(p):
    "program : stmt_list"
    p[0] = Program(p[1])


def p_stmt_list_multi(p):
    "stmt_list : stmt_list statement"
    p[0] = p[1] + [p[2]]


def p_stmt_list_single(p):
    "stmt_list : statement"
    p[0] = [p[1]]


def p_statement(p):
    """statement : declaracion PUNTOYCOMA
                 | asignacion PUNTOYCOMA
                 | lectura PUNTOYCOMA
                 | escritura PUNTOYCOMA"""
    p[0] = p[1]


# DECLARACIÓN

def p_declaracion(p):
    "declaracion : ID TIPO"
    p[0] = VarDecl(p[1], p[2])


# ASIGNACIÓN

def p_asignacion(p):
    "asignacion : ID ASSIGN expresion"
    p[0] = Assign(p[1], p[3])


# LECTURA (Captura)

def p_lectura(p):
    "lectura : ID ASSIGN FUNCION PUNTO TIPO PAREN_A PAREN_C"
    p[0] = Assign(p[1], Captura(p[5]))


# ESCRITURA (Mensaje.Texto)

def p_escritura(p):
    "escritura : FUNCION PUNTO TIPO PAREN_A CADENA PAREN_C"
    txt = p[5][1:-1]  # remover comillas
    p[0] = Mensaje(txt)


# EXPRESIONES

def p_expresion_binaria(p):
    """expresion : expresion PLUS expresion
                 | expresion MINUS expresion
                 | expresion TIMES expresion
                 | expresion DIVIDE expresion"""
    p[0] = BinaryOp(p[2], p[1], p[3])


def p_expresion_paren(p):
    "expresion : PAREN_A expresion PAREN_C"
    p[0] = p[2]


def p_expresion_numero(p):
    """expresion : ENTERO
                 | REAL"""
    raw = p[1]

    if "," in raw:
        # Guarda reales como texto con coma (12,5)
        p[0] = Number(raw, "Real")
    else:
        # Enteros como int
        p[0] = Number(int(raw), "Entero")


def p_expresion_cadena(p):
    "expresion : CADENA"
    p[0] = String(p[1][1:-1])


def p_expresion_id(p):
    "expresion : ID"
    p[0] = VarRef(p[1])


# ERROR SINTÁCTICO

def p_error(p):
    if p:
        raise Exception(
            f"Aja llave… ¿y esa vaina qué? "
            f"Esa vaina '{p.value}' (tipo={p.type}) no va ahí, revise la línea {p.lineno}, llave."
        )
    else:
        raise Exception("Nojoda, como que te faltó algo por ahí.")



def build_parser(debug=False):
    return yacc.yacc(debug=debug)
