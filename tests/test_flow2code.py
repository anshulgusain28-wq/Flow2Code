import unittest
from unittest.mock import MagicMock
import sys
import os

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.constants import NodeType
from src.ui.shapes import FlowchartShape
from src.compiler.ast_builder import ASTBuilder
from src.compiler.semantic import SemanticAnalyzer
from src.compiler.generator import CodeGenerator

class MockCanvas:
    def create_oval(self, *args, **kwargs): return 1
    def create_rectangle(self, *args, **kwargs): return 1
    def create_polygon(self, *args, **kwargs): return 1
    def create_text(self, *args, **kwargs): return 1
    def create_line(self, *args, **kwargs): return 1
    def delete(self, *args): pass

class TestFlow2Code(unittest.TestCase):
    def setUp(self):
        self.canvas = MockCanvas()
        self.nodes = []
        self.connections = []

    def create_node(self, ntype, text, x=0, y=0):
        node = FlowchartShape(self.canvas, ntype, x, y, text)
        self.nodes.append(node)
        return node
    
    def connect(self, n1, n2):
        self.connections.append((n1, n2, None))

    def run_pipeline(self, language="Python"):
        builder = ASTBuilder(self.nodes, self.connections)
        graph = builder.build()
        analyzer = SemanticAnalyzer(graph)
        analyzer.analyze()
        generator = CodeGenerator(graph, language=language)
        return generator.generate()

    def test_cpp_generation(self):
        """Test C++ Code Generation"""
        start = self.create_node(NodeType.START, "Start")
        out = self.create_node(NodeType.OUTPUT, "\"Hello World\"")
        end = self.create_node(NodeType.END, "End")
        
        self.connect(start, out)
        self.connect(out, end)
        
        code = self.run_pipeline(language="C++")
        print("\n--- Test C++ Generation ---")
        print(code)
        
        self.assertIn("#include <iostream>", code)
        self.assertIn("int main() {", code)
        self.assertIn("cout << \"Hello World\" << endl;", code)
        self.assertIn("return 0;", code)

    def test_python_generation(self):
        """Test Python Code Generation"""
        start = self.create_node(NodeType.START, "Start")
        out = self.create_node(NodeType.OUTPUT, "'Hello'")
        end = self.create_node(NodeType.END, "End")
        
        self.connect(start, out)
        self.connect(out, end)
        
        code = self.run_pipeline("Python")
        
        self.assertIn("print('Hello')", code)
        self.assertIn("exit()", code)

if __name__ == '__main__':
    unittest.main()
