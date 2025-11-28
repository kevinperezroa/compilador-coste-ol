from analizador_sintactico import *

class SemanticAnalyzer:
    def __init__(self):
        self.symbols = {}
        self.errors = []

    def analyze(self, node):
        self.visit(node)
        if self.errors:
            msg = "Ey llave… esa vaina está mala revisa bien:\n"
            for e in self.errors:
                msg += f"   ➤ {e}\n"
            raise Exception(msg)

    def visit(self, node):
        name = "visit_" + node.__class__.__name__
        func = getattr(self, name, self.generic_visit)
        return func(node)

    def generic_visit(self, node):
        self.errors.append(
            f"Nojoda, quedé mamando '{type(node).__name__}'."
        )

    def visit_Program(self, node):
        for s in node.stmts:
            self.visit(s)

    def visit_VarDecl(self, node):
        if node.name in self.symbols:
            self.errors.append(
                f"hey mi llave, ¿pa' qué declaras '{node.name}' otra vez? ¡Ya existe!"
            )
        else:
            self.symbols[node.name] = {"tipo": node.tipo, "valor": None}

    def visit_Assign(self, node):
        if node.name not in self.symbols:
            self.errors.append(
                f"hey loco, ¿y dónde declaraste '{node.name}'? Esa vaina ni existe."
            )
            return

        tipo_var = self.symbols[node.name]["tipo"]
        val, tipo_expr = self.visit(node.expr)

        if not self.type_compatible(tipo_var, tipo_expr):
            self.errors.append(
                f"Esa vaina no sirve, No puedes meter '{tipo_expr}' dentro de '{tipo_var}' en '{node.name}'."
            )
        else:
            self.symbols[node.name]["valor"] = val

    def visit_Captura(self, node):
        return f"Captura({node.tipo})", node.tipo

    def visit_Mensaje(self, node):
        return None, None

    def visit_BinaryOp(self, node):
        l, tl = self.visit(node.left)
        r, tr = self.visit(node.right)

        if tl not in ("Entero", "Real") or tr not in ("Entero", "Real"):
            self.errors.append(
                f"Aja llave… ¿cómo vas a operar '{tl}' con '{tr}'? ¡Eso no pega ni con gota magica!"
            )
            return None, None

        tipo = "Real" if "Real" in (tl, tr) else "Entero"
        return f"({l} {node.op} {r})", tipo

    def visit_Number(self, node):
        return node.value, node.kind.capitalize()

    def visit_String(self, node):
        return node.value, "Texto"

    def visit_VarRef(self, node):
        if node.name not in self.symbols:
            self.errors.append(
                f"hey loco, '{node.name}'¿esa vaina que?"
            )
            return None, None

        info = self.symbols[node.name]
        return info["valor"], info["tipo"]

    def type_compatible(self, esperado, recibido):
        if esperado == recibido:
            return True
        if {esperado, recibido} <= {"Entero", "Real"}:
            return True
        return False
