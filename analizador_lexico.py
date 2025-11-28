# analizador_lexico.py
import ply.lex as lex  # se importa lex del paquete ply para el analizador léxico

# Listas para errores léxicos
listar_errores_lexicos = []      # guarda (linea, columna, mensaje)
errores_Desc = []                # mensajes descriptivos

# Lista de tokens
tokens = [
    "CADENA",
    "REAL",
    "ENTERO",
    "TIPO",
    "FUNCION",
    "ID",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "ASSIGN",
    "PUNTO",
    "PAREN_A",
    "PAREN_C",
    "PUNTOYCOMA",
]

# Ignorar espacios y tabulaciones
t_ignore = " \t"

# Palabras reservadas
reserved = {
    "Entero": "TIPO",
    "Real": "TIPO",
    "Texto": "TIPO",
    "Captura": "FUNCION",
    "Mensaje": "FUNCION",
}

# Reglas regulares simples
t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_ASSIGN = r"="
t_PUNTO = r"\."
t_PAREN_A = r"\("
t_PAREN_C = r"\)"
t_PUNTOYCOMA = r";"

# Reglas regulares con acciones
def t_CADENA(t):
    r'"[^"]*"'
    return t

def t_REAL(t):
    r"\d+,\d+"
    return t

def t_ENTERO(t):
    r"\d+"
    return t

def t_ID(t):
    r"[A-Za-z_][A-Za-z0-9_]*"
    if t.value in reserved:
        t.type = reserved[t.value]
    return t

# Ignorar saltos de línea
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

# Manejo de errores léxicos con mensaje costeño
def t_error(t):
    error_char = t.value[0]
    mensaje = (
        f" Nojoda llave, esa vaina está mala: "
        f"esa vaina '{error_char}' no va ahí {t.lexpos}"
    )
    listar_errores_lexicos.append((t.lineno - 1, t.lexpos, mensaje))
    errores_Desc.append(mensaje)
    t.lexer.skip(1)

# Crear el analizador léxico
lexer = lex.lex()
