import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QLabel,
    QSplitter,
    QLineEdit
)
from PyQt5.QtGui import QColor, QTextCharFormat, QTextCursor, QFont, QSyntaxHighlighter
from PyQt5.QtCore import Qt, QRegExp

from analizador_lexico import lexer
from analizador_sintactico import build_parser
from analizador_semantico import SemanticAnalyzer
from interprete import Interpreter as BaseInterpreter

parser = build_parser()



# CLASE PARA RESALTADO DE SINTAXIS PQEK

class PQEKHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []
        self.error_ranges = []

        keywords = [
            "Entero", "Texto", "Real", "Captura", "Mensaje",
            "Si", "Sino", "Mientras", "Fin", "Entonces",
            "Inicio", "Programa", "Verdadero", "Falso",
        ]

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#50fa7b"))
        keyword_format.setFontWeight(QFont.Bold)

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#f1fa8c"))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6272a4"))
        comment_format.setFontItalic(True)

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#bd93f9"))

        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#8be9fd"))
        function_format.setFontItalic(True)

        for word in keywords:
            self.rules.append((QRegExp(r"\b" + word + r"\b"), keyword_format))
        self.rules.append((QRegExp(r"\".*\""), string_format))
        self.rules.append((QRegExp(r"\b\d+(\.\d+)?\b"), number_format))
        self.rules.append((QRegExp(r"//[^\n]*"), comment_format))
        self.rules.append((QRegExp(r"\b[A-Za-z_]+\.[A-Za-z_]+\b"), function_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, fmt)
                index = expression.indexIn(text, index + length)

        # Resaltar errores
        for (line, start, end) in self.error_ranges:
            if self.currentBlock().blockNumber() == line:
                error_format = QTextCharFormat()
                error_format.setUnderlineColor(QColor("#ff5555"))
                error_format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
                self.setFormat(start, end - start, error_format)

    def clear_errors(self):
        self.error_ranges.clear()
        self.rehighlight()

    def add_error(self, line, start=0, end=None):
        if end is None:
            end = start + 3
        self.error_ranges.append((line, start, end))
        self.rehighlight()


# INTERPRETE ADAPTADO A GUI CON RESALTADO DE ERRORES

class Interpreter(BaseInterpreter):
    def _read_input_from_console(self):
        if not self.gui:
            return input(">> ")

        # Mostrar prompt en output
        cursor = self.gui.output_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#f8f8f2"))
        cursor.setCharFormat(fmt)
        cursor.insertText(">> ")
        self.gui.output_area.setTextCursor(cursor)

        # Esperar input
        self.gui.input_ready = False
        self.gui.input_line.setFocus()
        while not self.gui.input_ready:
            QApplication.processEvents()

        value = self.gui.input_value

        # Mostrar lo ingresado
        cursor = self.gui.output_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(value + "\n")
        self.gui.output_area.setTextCursor(cursor)

        self.gui.input_line.clear()
        return value

    def log_error_line(self, message, line_number):
        """Muestra el mensaje de error y subraya la línea en rojo"""
        self.log(f" Línea {line_number + 1}: {message}", error=True)
        if self.gui:
            self.gui.highlighter.add_error(line_number, 0, 1)



#  APLICACIÓN PRINCIPAL PQEK

class PQEKCompilerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Compilador Costeñol - Interfaz PyQt5")
        self.setGeometry(100, 100, 1000, 650)
        self.file_path = None

        font = QFont("Consolas", 12)

        # ---------- Editor ----------
        self.code_area = QTextEdit()
        self.code_area.setFont(font)
        self.code_area.setStyleSheet("background-color: #282a36; color: #f8f8f2;")
        self.highlighter = PQEKHighlighter(self.code_area.document())

        # ---------- Output ----------
        self.output_area = QTextEdit()
        self.output_area.setFont(font)
        self.output_area.setReadOnly(True)
        self.output_area.setStyleSheet("background-color: #11111b; color: #f8f8f2;")

        # ---------- Input ----------
        self.input_line = QLineEdit()
        self.input_line.setFont(font)
        self.input_line.setStyleSheet("background-color: #44475a; color: #f8f8f2;")
        self.input_line.returnPressed.connect(self._handle_input)
        self.input_ready = False
        self.input_value = ""

        # ---------- Botones ----------
        self.open_btn = QPushButton(" Abrir .pqek")
        self.save_btn = QPushButton(" Guardar")
        self.compile_btn = QPushButton(" Compilar")
        self.clear_btn = QPushButton(" Limpiar")

        button_layout = QHBoxLayout()
        for btn in [self.open_btn, self.save_btn, self.compile_btn, self.clear_btn]:
            btn.setFont(QFont("Consolas", 11, QFont.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #00ffaa;
                    border-radius: 6px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #00cc88;
                }
            """)
            button_layout.addWidget(btn)

        self.open_btn.clicked.connect(self.open_file)
        self.save_btn.clicked.connect(self.save_file)
        self.compile_btn.clicked.connect(self.compile_code)
        self.clear_btn.clicked.connect(self.clear_output)

        # ---------- Título ----------
        title = QLabel(" Compilador Costeñol 1.0")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Consolas", 18, QFont.Bold))
        title.setStyleSheet("color: #00ffff; margin: 10px;")

        # ---------- Splitter ----------
        splitter = QSplitter(Qt.Vertical)
        code_output_widget = QWidget()
        code_output_layout = QVBoxLayout()
        code_output_layout.addWidget(self.code_area)
        code_output_layout.addWidget(self.output_area)
        code_output_layout.addWidget(self.input_line)
        code_output_widget.setLayout(code_output_layout)
        splitter.addWidget(code_output_widget)
        splitter.setSizes([400, 200])

        # ---------- Layout principal ----------
        main_layout = QVBoxLayout()
        main_layout.addWidget(title)
        main_layout.addWidget(splitter)
        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        container.setStyleSheet("background-color: #1e1e2e;")
        self.setCentralWidget(container)


    # Funciones de archivos

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir archivo PQEK", "", "Archivos PQEK (*.pqek)")
        if path:
            self.file_path = path
            with open(path, "r", encoding="utf-8") as f:
                self.code_area.setText(f.read())
            self.print_message(f"Archivo abierto: {os.path.basename(path)}", "info")

    def save_file(self):
        if not self.file_path:
            path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", "", "Archivos PQEK (*.pqek)")
            if not path:
                return
            self.file_path = path
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(self.code_area.toPlainText())
        self.print_message(f"Archivo guardado: {os.path.basename(self.file_path)}", "success")


    # Compilar y ejecutar con resaltado de errores

    def compile_code(self):
        code = self.code_area.toPlainText().strip()
        if not code:
            self.print_message(" El código está vacío.", "error")
            return

        self.clear_output()
        self.highlighter.clear_errors()
        self.print_message("Compilando código PQEK...\n", "info")

        try:
            ast = parser.parse(code, lexer=lexer)
            self.print_message(" AST generado correctamente.\n", "success")

            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)
            self.print_message("Análisis semántico completado.\n", "success")

            interpreter = Interpreter(gui=self)
            self.print_message("Ejecutando programa...\n", "info")
            interpreter.run(ast)
            self.print_message(" Ejecución finalizada con éxito.\n", "success")

        except Exception as e:
            # Resaltar línea donde ocurrió error si es posible
            import traceback
            tb = traceback.format_exc().splitlines()
            self.print_message(f"Error: {str(e)}\n", "error")
            # Intento de resaltar línea de error en editor (si traceback indica línea)
            for line in tb:
                if "line" in line.lower():
                    parts = line.strip().split()
                    for i, p in enumerate(parts):
                        if p.lower() == "line":
                            try:
                                line_no = int(parts[i+1]) - 1
                                self.highlighter.add_error(line_no, 0)
                                break
                            except:
                                continue


    # Colores de salida

    def print_message(self, message, msg_type="info"):
        color_map = {
            "info": "#f8f8f2",
            "success": "#00ff99",
            "error": "#ff5555",
        }
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color_map.get(msg_type, "#f8f8f2")))
        cursor = self.output_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.output_area.setCurrentCharFormat(fmt)
        self.output_area.insertPlainText(message + "\n")
        self.output_area.moveCursor(QTextCursor.End)

    def clear_output(self):
        self.output_area.clear()
        self.highlighter.clear_errors()


    # Entrada desde consola interna

    def _handle_input(self):
        self.input_value = self.input_line.text()
        self.input_line.clear()
        self.input_ready = True

        # Mostrar lo que ingresó el usuario
        cursor = self.output_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(self.input_value + "\n")
        self.output_area.moveCursor(QTextCursor.End)

    def read_input(self):
        self.input_ready = False
        self.input_line.setFocus()
        while not self.input_ready:
            QApplication.processEvents()
        return self.input_value, True



# EJECUCIÓN PRINCIPAL

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PQEKCompilerApp()
    window.show()
    sys.exit(app.exec_())
# interfaz_compilador.py
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTextEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QLabel, QFileDialog, QMessageBox, QLineEdit
)
from PyQt5.QtGui import QColor, QTextCharFormat, QTextCursor, QFont, QSyntaxHighlighter
from PyQt5.QtCore import Qt, QRegExp

from analizador_lexico import lexer, listar_errores_lexicos
from analizador_sintactico import build_parser
from analizador_semantico import SemanticAnalyzer
from interprete import Interpreter


# HIGHLIGHTER

class PQEKHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.error_lines = set()

    def highlightBlock(self, text):
        line_num = self.currentBlock().blockNumber()
        if line_num in self.error_lines:
            fmt = QTextCharFormat()
            fmt.setBackground(QColor("#FF6B6B"))
            self.setFormat(0, len(text), fmt)

    def mark_error_line(self, line):
        self.error_lines.add(line)
        self.rehighlight()

    def clear_errors(self):
        self.error_lines.clear()
        self.rehighlight()



# INTERFAZ PRINCIPAL

class CompilerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PQEK – Compilador Costeño")
        self.setGeometry(100, 50, 900, 700)

        # EDITOR DE CÓDIGO

        self.editor = QTextEdit()
        self.editor.setFont(QFont("Consolas", 12))
        self.highlighter = PQEKHighlighter(self.editor.document())

        # SALIDA

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Consolas", 11))

        # BOTONES

        self.btn_lex = QPushButton("Analizar Léxico")
        self.btn_sin = QPushButton("Analizar Sintáctico")
        self.btn_sem = QPushButton("Analizar Semántico")
        self.btn_run = QPushButton("Ejecutar Código")
        self.btn_clean = QPushButton("Limpiar")

        self.btn_lex.clicked.connect(self.run_lexico)
        self.btn_sin.clicked.connect(self.run_sintactico)
        self.btn_sem.clicked.connect(self.run_semantico)
        self.btn_run.clicked.connect(self.run_program)
        self.btn_clean.clicked.connect(self.clean_all)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_lex)
        button_layout.addWidget(self.btn_sin)
        button_layout.addWidget(self.btn_sem)
        button_layout.addWidget(self.btn_run)
        button_layout.addWidget(self.btn_clean)


        # LAYOUT PRINCIPAL

        layout = QVBoxLayout()
        layout.addWidget(QLabel("EDITOR DE CÓDIGO"))
        layout.addWidget(self.editor)
        layout.addLayout(button_layout)
        layout.addWidget(QLabel("SALIDA"))
        layout.addWidget(self.output_area)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.parser = build_parser()


    # IMPRESIÓN EN SALIDA

    def print_message(self, msg, kind="info"):
        if kind == "error":
            color = "#FF3333"
        elif kind == "info":
            color = "#77A6F7"
        else:
            color = "#FFFFFF"

        self.output_area.append(f"<span style='color:{color}'>{msg}</span>")


    # LIMPIAR

    def clean_all(self):
        self.editor.clear()
        self.output_area.clear()
        self.highlighter.clear_errors()


    # ANALIZADOR LÉXICO

    def run_lexico(self):
        self.output_area.clear()
        self.highlighter.clear_errors()

        code = self.editor.toPlainText()

        if not code.strip():
            QMessageBox.warning(self, "Vacío",
                                "hey loco yo que? adivino?, escribe algo pa' poder analizar.")
            return

        lexer.input(code)
        listar_errores_lexicos.clear()

        try:
            while True:
                tok = lexer.token()
                if not tok:
                    break
                self.print_message(f"(TOKEN {tok.type}, '{tok.value}')")

            if listar_errores_lexicos:
                for (line, col, msg) in listar_errores_lexicos:
                    self.highlighter.mark_error_line(line)
                    self.print_message(msg, kind="error")
                return

            self.print_message("✔ Análisis léxico correcto")

        except Exception as e:
            self.print_message(str(e), kind="error")


    # SINTAXIS

    def run_sintactico(self):
        self.output_area.clear()
        self.highlighter.clear_errors()

        code = self.editor.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "Vacío",
                                "Nojoda llave, esa vaina no se entiende.")
            return

        try:
            ast = self.parser.parse(code, lexer=lexer)
            self.print_message("✔ Estructura sintáctica correcta")
            return ast

        except Exception as e:
            msg = str(e)
            self.print_message(msg, kind="error")
            QMessageBox.critical(self, "Error Sintáctico", msg)


    # ANÁLISIS SEMÁNTICO

    def run_semantico(self):
        self.output_area.clear()
        self.highlighter.clear_errors()

        code = self.editor.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "Vacío",
                                "hey loco, ¿que voy a analzar si no hay nah?")
            return

        try:
            ast = self.parser.parse(code, lexer=lexer)
            sem = SemanticAnalyzer()
            sem.analyze(ast)
            self.print_message("✔ Análisis semántico correcto")

        except Exception as e:
            msg = str(e)
            self.print_message(msg, kind="error")
            QMessageBox.critical(self, "Error Semántico", msg)


    # EJECUCIÓN

    def run_program(self):
        self.output_area.clear()
        self.highlighter.clear_errors()

        code = self.editor.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "Vacío",
                                " hey llave, esa vaina esta vacia. Escribe algo.")
            return

        try:
            ast = self.parser.parse(code, lexer=lexer)
            sem = SemanticAnalyzer()
            sem.analyze(ast)

            interp = Interpreter(gui=self)
            interp.run(ast)

        except Exception as e:
            msg = str(e)
            self.print_message(msg, kind="error")
            QMessageBox.critical(self, "Error al ejecutar", msg)


# EJECUCIÓN DIRECTA
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CompilerGUI()
    window.show()
    sys.exit(app.exec_())
