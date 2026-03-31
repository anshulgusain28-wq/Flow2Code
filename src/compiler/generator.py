from src.utils.constants import NodeType

class CodeGenerator:
    def __init__(self, graph, language="Python"):
        self.graph = graph
        self.language = language
        self.code = []
        self.visited = set()
        self.loop_nodes = set()

    # ---------------- ENTRY ----------------
    def generate(self):
        start = self.get_start_node()
        if not start:
            raise Exception("No START node found")

        self.code = []
        self.visited = set()
        self.loop_nodes = set()

        if self.language == "C++":
            self.code.append("#include <bits/stdc++.h>")
            self.code.append("using namespace std;")
            self.code.append("")
            self.code.append("int main() {")
            self.dfs(start, indent=1)
            self.code.append("    return 0;")
            self.code.append("}")
        else:
            self.dfs(start, indent=0)

        return "\n".join(self.code)

    # ---------------- FIND START ----------------
    def get_start_node(self):
        for node, attr in self.graph.nodes(data=True):
            if attr["type"] == NodeType.START:
                return node
        return None

    # ---------------- LOOP DETECTION ----------------
    def is_loop(self, decision_node, branch_node):
        stack = [branch_node]
        visited = set()

        while stack:
            curr = stack.pop()
            if curr == decision_node:
                return True

            if curr in visited:
                continue
            visited.add(curr)

            for nxt in self.graph.successors(curr):
                stack.append(nxt)

        return False

    # ---------------- DFS ----------------
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
            if self.language == "C++":
                self.code.append(space + f"int {text};")
                self.code.append(space + f"cin >> {text};")
            else:
                self.code.append(space + f"{text} = int(input())")

        # ---- OUTPUT ----
        elif node_type == NodeType.OUTPUT:
            if self.language == "C++":
                self.code.append(space + f"cout << {text} << endl;")
            else:
                self.code.append(space + f"print({text})")

        # ---- DECISION ----
        elif node_type == NodeType.DECISION:
            self.handle_decision(node, indent)
            return

        # ---- CONTINUE (FIXED: traverse all successors) ----
        for nxt in self.graph.successors(node):
            self.dfs(nxt, indent)

    # ---------------- DECISION ----------------
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

        # ---------------- LOOP CHECK ----------------
        is_loop = False
        if true_branch and self.is_loop(node, true_branch):
            is_loop = True

        # ---------------- WHILE LOOP ----------------
        if is_loop:
            self.loop_nodes.add(node)

            if self.language == "C++":
                self.code.append(space + f"while ({condition}) {{")
                self.dfs(true_branch, indent + 1)
                self.code.append(space + "}")
            else:
                self.code.append(space + f"while {condition}:")
                self.dfs(true_branch, indent + 1)

            # After loop → follow FALSE branch
            if false_branch:
                self.dfs(false_branch, indent)

            return

        # ---------------- NORMAL IF ----------------
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