import networkx as nx
from src.utils.constants import NodeType

class ASTBuilder:
    def __init__(self, ui_nodes, ui_connections):
        """
        ui_nodes: List of FlowchartShape objects
        ui_connections: List of tuples (from_node, to_node, line_id)
        """
        self.ui_nodes = ui_nodes
        self.ui_connections = ui_connections
        self.graph = nx.DiGraph()

    def build(self):
        # Add nodes
        for node in self.ui_nodes:
            # We use the memory address or a unique ID as the graph node attributes
            # For simplicity, let's use the object itself as the key, or its index
            self.graph.add_node(node, type=node.node_type, text=node.text)

        # Add edges
        for from_node, to_node, _ in self.ui_connections:
            self.graph.add_edge(from_node, to_node)

        return self.graph

    def get_start_node(self):
        start_nodes = [n for n, attr in self.graph.nodes(data=True) if attr.get("type") == NodeType.START]
        if len(start_nodes) == 1:
            return start_nodes[0]
        return None
