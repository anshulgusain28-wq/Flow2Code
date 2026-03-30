import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from src.ui.toolbar import Toolbar
from src.ui.shapes import FlowchartShape
from src.utils.constants import NodeType, COLORS
from src.compiler.ast_builder import ASTBuilder
from src.compiler.semantic import SemanticAnalyzer, SemanticError
from src.compiler.generator import CodeGenerator

class FlowchartEditor:
    def __init__(self, root):
        self.root = root
        self.nodes = [] 
        self.connections = [] 
        self.current_tool = "SELECT"
        self.selected_node = None
        self.connection_start_node = None
        
        # Use PanedWindow for resizability
        self.paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg=COLORS["grid"], sashwidth=4, sashrelief=tk.RAISED)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Toolbar Pane
        self.toolbar_pane = tk.Frame(self.paned_window, bg=COLORS["background"])
        self.toolbar = Toolbar(self.toolbar_pane, self.set_tool, self.on_drop)
        self.toolbar.pack(fill=tk.BOTH, expand=True) # Scrollbar needs to expand
        self.paned_window.add(self.toolbar_pane, minsize=250, width=320) # Default width
        
        # Canvas Pane
        self.canvas_pane = tk.Frame(self.paned_window, bg=COLORS["grid"])
        self.canvas = tk.Canvas(self.canvas_pane, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.paned_window.add(self.canvas_pane, minsize=400)
        
        self.draw_grid()

        # Events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Configure>", self.on_resize)
        self.root.bind("<Delete>", lambda e: self.delete_selected())

    def draw_grid(self):
        self.canvas.delete("grid")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        step = 25
        for i in range(0, w, step):
            width = 2 if i % 100 == 0 else 1
            self.canvas.create_line(i, 0, i, h, fill=COLORS["grid"], width=width, tags="grid")
        for i in range(0, h, step):
            width = 2 if i % 100 == 0 else 1
            self.canvas.create_line(0, i, w, i, fill=COLORS["grid"], width=width, tags="grid")
        self.canvas.tag_lower("grid")

    def on_resize(self, event):
        self.draw_grid()

    def set_tool(self, tool):
        if tool == "CLEAR":
            self.clear_canvas()
            return
        elif tool == "CONVERT":
            self.convert_to_code()
            return
        elif tool == "AUTO_CONNECT":
            self.auto_connect()
            self.current_tool = "SELECT"
            return
        elif tool == "DELETE":
            self.delete_selected()
            self.current_tool = "SELECT"
            return

        self.current_tool = tool
        self.connection_start_node = None
        print(f"Tool selected: {tool}")

    def on_drop(self, root_x, root_y, tool_type):
        canvas_x = root_x - self.canvas.winfo_rootx()
        canvas_y = root_y - self.canvas.winfo_rooty()
        if 0 <= canvas_x <= self.canvas.winfo_width() and 0 <= canvas_y <= self.canvas.winfo_height():
            self.add_node(tool_type, canvas_x, canvas_y)

    def add_node(self, node_type, x, y):
        text = "Start" if node_type == NodeType.START else \
               "End" if node_type == NodeType.END else \
               "Process" if node_type == NodeType.PROCESS else \
               "Condition" if node_type == NodeType.DECISION else \
               "Input" if node_type == NodeType.INPUT else \
               "Output"

        node = FlowchartShape(self.canvas, node_type, x, y, text)
        self.nodes.append(node)
        
        if node_type in [NodeType.PROCESS, NodeType.DECISION, NodeType.INPUT, NodeType.OUTPUT]:
            self.prompt_node_text(node)

    def prompt_node_text(self, node):
        prompt = "Enter code/statement:"
        if node.node_type == NodeType.INPUT: prompt = "Enter variable name:"
        elif node.node_type == NodeType.OUTPUT: prompt = "Enter value to print:"
        elif node.node_type == NodeType.DECISION: prompt = "Enter condition (e.g. x > 5):"
            
        new_text = simpledialog.askstring("Edit Node", prompt, initialvalue=node.text, parent=self.root)
        if new_text:
            node.update_text(new_text)

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        clicked_node = self.find_node_at(x, y)

        if self.current_tool == "ARROW":
            if clicked_node:
                if self.connection_start_node is None:
                    self.connection_start_node = clicked_node
                else:
                    if clicked_node != self.connection_start_node:
                        self.add_connection(self.connection_start_node, clicked_node)
                        self.connection_start_node = None
                        self.current_tool = "SELECT"
            else:
                self.connection_start_node = None
                self.current_tool = "SELECT"
        else:
            self.selected_node = clicked_node

    def on_canvas_drag(self, event):
        if self.selected_node:
            dx = event.x - self.selected_node.x
            dy = event.y - self.selected_node.y
            self.selected_node.move(dx, dy)
            self.update_connections()

    def on_double_click(self, event):
        node = self.find_node_at(event.x, event.y)
        if node:
            self.prompt_node_text(node)

    def find_node_at(self, x, y):
        for node in reversed(self.nodes):
            if node.contains(x, y):
                return node
        return None

    def add_connection(self, node1, node2):
        for n1, n2, _ in self.connections:
            if n1 == node1 and n2 == node2:
                return
        line_id = self.canvas.create_line(node1.x, node1.y, node2.x, node2.y, arrow=tk.LAST, width=3, fill=COLORS["text"], smooth=True)
        self.connections.append((node1, node2, line_id))

    def update_connections(self):
        for node1, node2, line_id in self.connections:
            self.canvas.coords(line_id, node1.x, node1.y, node2.x, node2.y)
            self.canvas.tag_lower(line_id)
            self.canvas.tag_lower("grid")

    def auto_connect(self):
        if len(self.nodes) < 2: return
        sorted_nodes = sorted(self.nodes, key=lambda n: n.y)
        for i in range(len(sorted_nodes) - 1):
            current = sorted_nodes[i]
            next_node = sorted_nodes[i+1]
            has_outgoing = any(n1 == current for n1, n2, _ in self.connections)
            if not has_outgoing:
                self.add_connection(current, next_node)
        messagebox.showinfo("Auto Connect", "Connected nodes successfully!")

    def delete_selected(self):
        if self.selected_node:
            conns_to_remove = [c for c in self.connections if c[0] == self.selected_node or c[1] == self.selected_node]
            for c in conns_to_remove:
                self.canvas.delete(c[2])
            
            self.connections = [c for c in self.connections if c not in conns_to_remove]
            self.selected_node.delete()
            self.nodes.remove(self.selected_node)
            self.selected_node = None
        else:
            messagebox.showinfo("Info", "Select a node first to delete.")

    def clear_canvas(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.nodes = []
        self.connections = []

    def convert_to_code(self):
        language = self.toolbar.get_language()
        try:
            builder = ASTBuilder(self.nodes, self.connections)
            graph = builder.build()
            analyzer = SemanticAnalyzer(graph)
            analyzer.analyze()
            generator = CodeGenerator(graph, language=language)
            code = generator.generate()
            self.show_code_window(code, language)
        except SemanticError as e:
            messagebox.showerror("Semantic Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_code_window(self, code, language):
        win = tk.Toplevel(self.root)
        win.title(f"Generated {language} Code")
        win.geometry("600x500")
        text_area = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Consolas", 10))
        text_area.pack(expand=True, fill=tk.BOTH)
        text_area.insert(tk.END, code)
        text_area.config(state=tk.DISABLED)
