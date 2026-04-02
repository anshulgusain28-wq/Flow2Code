import re
from src.utils.constants import NodeType


class CodeGenerator:
    def __init__(self, graph, language="Python"):
        self.graph = graph
        self.language = language
        self.code = []
        self.visited = set()

    # ──────────────── ENTRY ────────────────────────────────────────────
    def generate(self):
        start = self.get_start_node()
        if not start:
            raise Exception("No START node found")

        self.code = []
        self.visited = set()

        if self.language == "C++":
            self.code.append("#include <bits/stdc++.h>")
            self.code.append("using namespace std;")
            self.code.append("")
            self.code.append("int main() {")

            # ── Auto-declare variables not declared via INPUT nodes ──
            auto_decls = self._infer_undeclared_cpp()
            for decl in auto_decls:
                self.code.append(f"    {decl}")
            if auto_decls:
                self.code.append("")   # blank line separator

            self.dfs(start, indent=1)
            self.code.append("    return 0;")
            self.code.append("}")
        else:  # Python
            self.dfs(start, indent=0)

        return "\n".join(self.code)

    # ──────────────── VARIABLE INFERENCE (C++ only) ────────────────────
    def _infer_undeclared_cpp(self):
        """
        Scan all graph nodes to find:
          - Variables declared by INPUT nodes  → already declared
          - LHS variables assigned in PROCESS nodes → may need declaration

        Returns a list of declaration strings like ["int a;", "double b;"]
        for variables used but not declared via INPUT.
        """
        # Step 1 – collect variables declared via INPUT nodes
        declared = set()
        for node, attr in self.graph.nodes(data=True):
            if attr["type"] == NodeType.INPUT:
                for v in attr["text"].split(","):
                    declared.add(v.strip())

        # Step 2 – scan PROCESS nodes for LHS assignments
        # Pattern: optional spaces, identifier, then = (not ==)
        assign_pattern = re.compile(r"^\s*([A-Za-z_]\w*)\s*=[^=]")
        undeclared_in_order = []   # preserve encounter order
        seen = set()

        for node, attr in self.graph.nodes(data=True):
            if attr["type"] == NodeType.PROCESS:
                text = attr["text"].strip()
                m = assign_pattern.match(text)
                if m:
                    var = m.group(1)
                    if var not in declared and var not in seen:
                        seen.add(var)
                        undeclared_in_order.append((var, text))

        # Step 3 – infer C++ type for each undeclared variable
        declarations = []
        for var, expr in undeclared_in_order:
            cpp_type = self._infer_cpp_type(expr)
            declarations.append(f"{cpp_type} {var};")

        return declarations

    def _infer_cpp_type(self, expr):
        """
        Heuristic type inference from assignment expression RHS.
          - Contains '.' literal  → double
          - Contains string literal → string
          - Otherwise             → int
        """
        # Extract RHS (part after the first =)
        rhs = expr.split("=", 1)[1] if "=" in expr else expr

        if re.search(r'\d+\.\d*|\.\d+', rhs):          # float literal
            return "double"
        if '"' in rhs or "'" in rhs:                    # string literal
            return "string"
        return "int"

    # ──────────────── FIND START ───────────────────────────────────────
    def get_start_node(self):
        for node, attr in self.graph.nodes(data=True):
            if attr["type"] == NodeType.START:
                return node
        return None

    # ──────────────── DFS ──────────────────────────────────────────────
    def dfs(self, node, indent):
        if node in self.visited:
            return
        self.visited.add(node)

        node_type = self.graph.nodes[node]["type"]
        text = self.graph.nodes[node]["text"]
        space = "    " * indent

        # ---- START ----
        if node_type == NodeType.START:
            pass

        # ---- END ----
        elif node_type == NodeType.END:
            if self.language == "Python":
                self.code.append(space + "# End")
            return

        # ---- PROCESS ----
        elif node_type == NodeType.PROCESS:
            if self.language == "C++":
                self.code.append(space + text + ";")
            else:
                self.code.append(space + text)

        # ---- INPUT ----
        elif node_type == NodeType.INPUT:
            vars_raw = [v.strip() for v in text.split(",")]
            if self.language == "C++":
                decl_vars = ", ".join(vars_raw)
                self.code.append(space + f"int {decl_vars};")
                cin_chain = " >> ".join(vars_raw)
                self.code.append(space + f"cin >> {cin_chain};")
            else:
                if len(vars_raw) == 1:
                    self.code.append(space + f"{vars_raw[0]} = int(input())")
                else:
                    lhs = ", ".join(vars_raw)
                    self.code.append(space + f"{lhs} = map(int, input().split())")

        # ---- OUTPUT ----
        elif node_type == NodeType.OUTPUT:
            vars_raw = [v.strip() for v in text.split(",")]
            if self.language == "C++":
                parts = ' << " " << '.join(vars_raw)
                self.code.append(space + f"cout << {parts} << endl;")
            else:
                args = ", ".join(vars_raw)
                self.code.append(space + f"print({args})")

        # ---- DECISION ----
        elif node_type == NodeType.DECISION:
            self.handle_decision(node, indent)
            return   # stop linear DFS here

        # ---- CONTINUE linear flow ----
        successors = list(self.graph.successors(node))
        if successors:
            self.dfs(successors[0], indent)

    # ──────────────── DECISION ─────────────────────────────────────────
    def handle_decision(self, node, indent):
        condition = self.graph.nodes[node]["text"]
        space = "    " * indent

        true_branch = None
        false_branch = None

        for neighbor in self.graph.successors(node):
            edge = self.graph.get_edge_data(node, neighbor)
            label = edge.get("label", "").upper()
            if label == "TRUE":
                true_branch = neighbor
            elif label == "FALSE":
                false_branch = neighbor

        if true_branch is None and false_branch is None:
            raise Exception("Decision node missing TRUE/FALSE branches")

        # ---- IF ----
        if self.language == "C++":
            self.code.append(space + f"if ({condition}) {{")
            if true_branch:
                self.dfs(true_branch, indent + 1)
            else:
                self.code.append(space + "    ;")
        else:
            self.code.append(space + f"if {condition}:")
            if true_branch:
                self.dfs(true_branch, indent + 1)
            else:
                self.code.append(space + "    pass")

        # ---- ELSE ----
        if false_branch:
            if self.language == "C++":
                self.code.append(space + "} else {")
                self.dfs(false_branch, indent + 1)
                self.code.append(space + "}")
            else:
                self.code.append(space + "else:")
                self.dfs(false_branch, indent + 1)
        else:
            if self.language == "C++":
                self.code.append(space + "}")