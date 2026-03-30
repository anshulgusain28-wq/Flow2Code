from src.utils.constants import NodeType
import networkx as nx

class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    def __init__(self, graph):
        self.graph = graph

    def analyze(self):
        self.check_start_end()
        self.check_reachability()
        self.check_branching()

    def check_start_end(self):
        start_nodes = [n for n, attr in self.graph.nodes(data=True) if attr["type"] == NodeType.START]
        end_nodes = [n for n, attr in self.graph.nodes(data=True) if attr["type"] == NodeType.END]

        if len(start_nodes) == 0:
            raise SemanticError("Missing START node.")
        if len(start_nodes) > 1:
            raise SemanticError("Multiple START nodes found.")
        if len(end_nodes) == 0:
            raise SemanticError("Missing END node.")

    def check_reachability(self):
        # Simply check if all nodes are reachable from Start?
        # A simple check: every node (except Start) has in-degree > 0
        # and every node (except End) has out-degree > 0
        
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node]["type"]
            
            if node_type != NodeType.START:
                if self.graph.in_degree(node) == 0:
                    raise SemanticError(f"Unreachable node: {self.graph.nodes[node]['text']}")
            
            if node_type != NodeType.END:
                if self.graph.out_degree(node) == 0:
                    raise SemanticError(f"Dead-end node: {self.graph.nodes[node]['text']}")

    def check_branching(self):
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node]["type"]
            if node_type == NodeType.DECISION:
                out_edges = self.graph.out_edges(node)
                if len(out_edges) < 2:
                    # In a real app we'd check for exactly 2 (True/False)
                    # For now just warn or error if connection missing
                    raise SemanticError(f"Decision node '{self.graph.nodes[node]['text']}' must have at least 2 branches.")
