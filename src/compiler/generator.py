from src.utils.constants import NodeType

class CodeGenerator:
    def __init__(self, graph, language="Python"):
        self.graph = graph
        self.language = language
        self.code = []
        self.visited = set()

   






   
    def get_start_node(self):
        for node, attr in self.graph.nodes(data=True):
            if attr["type"] == NodeType.START:
                return node
        return None

    # ---------------- DFS Traversal ----------------
    def dfs(self, node, indent):
        if node in self.visited:
            return
        self.visited.add(node)

        node_type = self.graph.nodes[node]["type"]
        text = self.graph.nodes[node]["text"]

        space = "    " * indent

        # ---- HANDLE NODE TYPES ----

        if node_type == NodeType.START:
            pass  # nothing to generate

        elif node_type == NodeType.END:
            self.code.append(space + "# End")
            return

        elif node_type == NodeType.PROCESS:
            self.code.append(space + text)

        elif node_type == NodeType.INPUT:
            self.code.append(space + f"{text} = input()")

        elif node_type == NodeType.OUTPUT:
            self.code.append(space + f"print({text})")

        elif node_type == NodeType.DECISION:
            self.handle_decision(node, indent)
            return  # important: stop normal flow here

        # ---- CONTINUE LINEAR FLOW ----
        successors = list(self.graph.successors(node))
        if successors:
            self.dfs(successors[0], indent)

    # ---------------- DECISION HANDLING ----------------
    def handle_decision(self, node, indent):
        condition = self.graph.nodes[node]["text"]
        space = "    " * indent

        true_branch = None
        false_branch = None

        # Identify branches using labels
        for neighbor in self.graph.successors(node):
            edge = self.graph.get_edge_data(node, neighbor)

            label = edge.get("label", "").upper()

            if label == "TRUE":
                true_branch = neighbor
            elif label == "FALSE":
                false_branch = neighbor

        # Safety check
        if true_branch is None and false_branch is None:
            raise Exception("Decision node missing TRUE/FALSE branches")

        # ---- IF ----
        self.code.append(space + f"if {condition}:")

        if true_branch:
            self.dfs(true_branch, indent + 1)
        else:
            self.code.append(space + "    pass")

        # ---- ELSE ----
        if false_branch:
            self.code.append(space + "else:")
            self.dfs(false_branch, indent + 1)

    # ---------------- OPTIONAL: DEBUG ----------------
    def print_graph(self):
        for node in self.graph.nodes:
            print(node, self.graph.nodes[node])
        for edge in self.graph.edges(data=True):
            print(edge)