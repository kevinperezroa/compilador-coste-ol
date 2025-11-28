# interprete.py
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QTextCursor


class Interpreter:
    def __init__(self, gui=None):
        self.memory = {}
        self.output_log = []
        self.gui = gui

    #   EJECUCIÓN DE NODOS

    def run(self, node):
        cls = node.__class__.__name__
        try:
            if cls == "Program":
                for s in node.stmts:
                    self.run(s)

            elif cls == "VarDecl":
                self.memory[node.name] = None
                self.log(f"Variable declarada: {node.name} ({node.tipo})")

            elif cls == "Assign":
                value = self.eval(node.expr)
                self.memory[node.name] = value
                self.log(f"{node.name} = {value}")

            elif cls == "Mensaje":
                self.log(f"{node.texto}")

            else:
                raise Exception(f"No puedo ejecutar nodo {cls}")

        except Exception as e:
            msg = f"Nojoda llave… error en ejecución ({cls}): {e}"
            self.log(msg, error=True)
            if self.gui:
                QMessageBox.critical(self.gui, "Error en ejecución", msg)


    #   EVALUACIÓN DE EXPRESIONES

    def eval(self, node):
        cls = node.__class__.__name__


        # OPERACIONES ( + - * / )

        if cls == "BinaryOp":
            left = self.eval(node.left)
            right = self.eval(node.right)

            # Convertir strings "1,5" → 1.5
            left_val = self._as_number(left)
            right_val = self._as_number(right)

            if node.op == "+":
                result = left_val + right_val
            elif node.op == "-":
                result = left_val - right_val
            elif node.op == "*":
                result = left_val * right_val
            elif node.op == "/":
                result = left_val / right_val
            else:
                raise Exception(f"Operador '{node.op}' inválido en operación.")

            # Convertir de vuelta a coma si es float
            if isinstance(result, float):
                return self._to_comma(result)

            return result


        # NÚMEROS

        elif cls == "Number":
            # p.ex. "12,5" o 7
            return node.value


        # CADENA

        elif cls == "String":
            return node.value


        # VARIABLES

        elif cls == "VarRef":
            if node.name not in self.memory:
                raise Exception(f"Variable '{node.name}' no existe.")
            if self.memory[node.name] is None:
                raise Exception(f"La variable '{node.name}' no tiene valor, llave.")
            return self.memory[node.name]

        # CAPTURA

        elif cls == "Captura":
            if self.gui:
                self.log(f"Ingresa un valor de tipo {node.tipo} y presiona Enter:", info=True)
                return self._read_input_from_output()
            else:
                return input(">> ")


        # DESCONOCIDO

        else:
            raise Exception(f"No hay eval para '{cls}'.")


    #   CONVERSIÓN DE NÚMEROS

    def _as_number(self, value):
        """Convierte '12,5' → 12.5 o '7' → 7 para operar."""
        if isinstance(value, str):
            if "," in value:
                return float(value.replace(",", "."))
            if value.isdigit():
                return int(value)
        return value

    def _to_comma(self, num):
        """Convierte 12.5 → '12,5'."""
        txt = str(num)
        if "." in txt:
            return txt.replace(".", ",")
        return txt


    #   LECTURA DESDE GUI

    def _read_input_from_output(self):
        if not self.gui:
            return input(">> ")

        cursor = self.gui.output_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(">> ")
        self.gui.output_area.setTextCursor(cursor)

        self.gui.input_ready = False
        self.gui.input_line.setFocus()

        while not self.gui.input_ready:
            QApplication.processEvents()

        text = self.gui.input_value

        cursor = self.gui.output_area.textCursor()
        cursor.insertText(text + "\n")

        return text

    #   LOG DE MENSAJES

    def log(self, text, error=False, info=False):
        self.output_log.append(text)
        if self.gui:
            msg_type = "error" if error else "info"
            self.gui.print_message(text, msg_type)
        else:
            print(text)
