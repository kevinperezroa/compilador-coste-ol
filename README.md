# Compilador Costeñol   
### *Un compilador educativo hecho con Python, PLY y PyQt5*

Este proyecto implementa un compilador completo , que implementa los errores en expresiones costeñas de la costa colombiana.  
El compilador incluye análisis léxico, sintáctico, semántico, generación de AST, un intérprete funcional y una interfaz gráfica moderna.

---

## Características principales

- ✔ Analizador léxico construido con **PLY**
- ✔ Analizador sintáctico basado en una gramática completa
- ✔ Árbol de Sintaxis Abstracta (AST)
- ✔ Análisis semántico con tabla de símbolos
- ✔ Intérprete funcional con evaluación de expresiones
- ✔ Interfaz gráfica desarrollada con **PyQt5**
- ✔ Syntax highlighting incluido
- ✔ Subrayado automático de errores en el editor
- ✔ Consola interactiva integrada
- ✔ Mensajes de error “costeños” para un toque divertido

---

## Estructura del proyecto
│── analizador_lexico.py
│── analizador_sintactico.py
│── analizador_semantico.py
│── interprete.py
│── interfaz_compilador.py

---

## Instalación

1. Clona el repositorio:

git clone https://github.com/kevinperezroa/compilador-coste-ol
cd compilador-coste-ol

2. crea un entorno virtual:
   
   python -m venv (nombre del entorno)

4. Instala las dependencias necesarias:
   
   pip install -r requirements.txt
   
5. ejecuta la interfaz virtual:

   python interfaz_compilador.py
   
---
## Componentes del compilador

✔Analizador Léxico (analizador_lexico.py)

Define los tokens y detecta errores léxicos con mensajes como:
“Nojoda llave, esa vaina está mala…”

✔Analizador Sintáctico (analizador_sintactico.py)

Construye el AST

Verifica la estructura según la gramática

Detecta errores sintácticos

✔Analizador Semántico (analizador_semantico.py)

Valida:

Declaraciones duplicadas

Variables no declaradas

Tipos incompatibles

Operaciones inválidas

✔Intérprete (interprete.py)

Recorre el AST ejecutando cada instrucción

Evalúa expresiones matemáticas

Maneja entrada mediante Captura

Envía mensajes a la consola o GUI

✔Interfaz gráfica (interfaz_compilador.py)

Incluye:

Editor con resaltado de sintaxis

Subrayado automático de errores

Consola integrada

Entrada de usuario

Botones de flujo de compilación

---

## ejemplo de la sintaxis del lenguaje 

nombre Texto;
edad Entero;

nombre = Captura.Texto();
edad = Captura.Entero();

Mensaje.Texto("Bienvenido llave, tu nombre es:");
Mensaje.Texto(nombre);

Mensaje.Texto("Y tu edad es:");
Mensaje.Texto(edad);


