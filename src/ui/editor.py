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

        # Layout
        self.paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg=COLORS["grid"])
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Toolbar
        self.toolbar_pane = tk.Frame(self.paned_window, bg=COLORS["background"])
        self.toolbar = Toolbar(self.toolbar_pane, self.set_tool, self.on_drop)
        self.toolbar.pack(fill=tk.BOTH, expand=True)
        self.paned_window.add(self.toolbar_pane, minsize=250, width=320)

        # Canvas
        self.canvas_pane = tk.Frame(self.paned_window, bg=COLORS["grid"])
        self.canvas = tk.Canvas(self.canvas_pane, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.paned_window.add(self.canvas_pane, minsize=400)

        self.draw_grid()

        # Bindings
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)

    # ---------------- GRID ----------------
    def draw_grid(self):
        self.canvas.delete("grid")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        step = 25

        for i in range(0, w, step):
            self.canvas.create_line(i, 0, i, h, fill="#E5E7EB", tags="grid")
        for i in range(0, h, step):
            self.canvas.create_line(0, i, w, i, fill="#E5E7EB", tags="grid")

        self.canvas.tag_lower("grid")

    # ---------------- TOOL ----------------
    def set_tool(self, tool):
        if tool == "CLEAR":
            self.clear_canvas()
            return
        elif tool == "CONVERT":
            self.convert_to_code()
            return
        elif tool == "AUTO":
            self.auto_connect_nodes()
            return

        self.current_tool = tool
        self.connection_start_node = None



    def get_connection_point(self, shape, direction):
        x, y = shape.x, shape.y
        w = 60
        h = 40

        if direction == "TOP":
            return (x, y - h)
        elif direction == "BOTTOM":
            return (x, y + h)
        elif direction == "LEFT":
            return (x - w, y)
        elif direction == "RIGHT":
            return (x + w, y)

        return (x, y)


     # ---------------- SMART EDGE ----------------
    def draw_edge(self, node1, node2, label=None):
        start_dir = "BOTTOM"
        end_dir = "TOP"
    
        # Decision handling
        if node1.node_type.name == "DECISION":
            if label == "TRUE":
                start_dir = "BOTTOM"
            elif label == "FALSE":
                start_dir = "RIGHT"
    
        # Loop detection (back edge)
        if node2.y < node1.y:
            start_dir = "LEFT"
            end_dir = "LEFT"
    
        start = self.get_connection_point(node1, start_dir)
        end = self.get_connection_point(node2, end_dir)
    
        mid_x = (start[0] + end[0]) // 2
    
        line_id = self.canvas.create_line(
            start[0], start[1],
            mid_x, start[1],
            mid_x, end[1],
            end[0], end[1],
            arrow=tk.LAST,
            width=2,
            fill="#374151"
        )
    
        # Label
        if label:
            color = "green" if label == "TRUE" else "red"
            self.canvas.create_text(
                mid_x,
                (start[1] + end[1]) // 2,
                text=label,
                fill=color,
                font=("Arial", 9, "bold")
            )
    
        return line_id








    def auto_connect_nodes(self):
        if len(self.nodes) < 2:
            return
    
        # Sort top → bottom
        sorted_nodes = sorted(self.nodes, key=lambda n: (n.y, n.x))
    
        X_THRESHOLD = 120   # max horizontal distance allowed
    
        for i in range(len(sorted_nodes) - 1):
            n1 = sorted_nodes[i]
    
            # ❌ Skip decision node
            if n1.node_type == NodeType.DECISION:
                continue
    
            # Find nearest valid next node BELOW
            best_candidate = None
            min_dy = float('inf')
    
            for j in range(i + 1, len(sorted_nodes)):
                n2 = sorted_nodes[j]
    
                dy = n2.y - n1.y
                dx = abs(n2.x - n1.x)
    
                # Only downward
                if dy <= 0:
                    continue
    
                # Only near vertical alignment
                if dx > X_THRESHOLD:
                    continue
    
                if dy < min_dy:
                    min_dy = dy
                    best_candidate = n2
    
            if not best_candidate:
                continue
    
            # Avoid duplicate connection
            exists = any(c[0] == n1 and c[1] == best_candidate for c in self.connections)
            if exists:
                continue
    
            line_id = self.draw_edge(n1, best_candidate)
            self.connections.append((n1, best_candidate, line_id, None))







    # ---------------- ANCHOR ----------------
    def get_anchor(self, node_from, node_to):
        dx = node_to.x - node_from.x
        dy = node_to.y - node_from.y

    # Get bounding box of shapes
        bbox_from = self.canvas.bbox(node_from.id)
        bbox_to = self.canvas.bbox(node_to.id)

        if not bbox_from or not bbox_to:
            return (node_from.x, node_from.y)

        x1f, y1f, x2f, y2f = bbox_from
        x1t, y1t, x2t, y2t = bbox_to

    # Vertical connection
        if abs(dx) < abs(dy):
            if dy > 0:
            # going down
                return (node_from.x, y2f)   # bottom of from-node
            else:
                # going up
                return (node_from.x, y1f)   # top of from-node

    # Horizontal connection
        else:
            if dx > 0:
                return (x2f, node_from.y)   # right side
            else:
                return (x1f, node_from.y)   # left side

    # ---------------- ADD NODE ----------------
    def on_drop(self, root_x, root_y, tool_type):
        canvas_x = root_x - self.canvas.winfo_rootx()
        canvas_y = root_y - self.canvas.winfo_rooty()

        # Better spacing grid
        grid_x = 150
        grid_y = 100

        canvas_x = (canvas_x // grid_x) * grid_x
        canvas_y = (canvas_y // grid_y) * grid_y

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
        prompt = "Enter code:"
        if node.node_type == NodeType.INPUT:
            prompt = "Enter variable:"
        elif node.node_type == NodeType.OUTPUT:
            prompt = "Enter output:"
        elif node.node_type == NodeType.DECISION:
            prompt = "Enter condition (x > 5):"

        text = simpledialog.askstring("Edit Node", prompt, parent=self.root)
        if text:
            node.update_text(text)


    











    # ---------------- SMART ARROW ----------------
    def draw_smart_arrow(self, x1, y1, x2, y2):

        # Straight vertical
        if abs(x1 - x2) < 10:
            return self.canvas.create_line(
                x1, y1, x2, y2,
                arrow=tk.LAST,
                width=2,
                fill="#374151",
                arrowshape=(12, 14, 6)
            )

        # Straight horizontal
        if abs(y1 - y2) < 10:
            return self.canvas.create_line(
                x1, y1, x2, y2,
                arrow=tk.LAST,
                width=2,
                fill="#374151",
                arrowshape=(12, 14, 6)
            )

        # Clean elbow
        mid_y = (y1 + y2) // 2

        return self.canvas.create_line(
            x1, y1,
            x1, mid_y,
            x2, mid_y,
            x2, y2,
            arrow=tk.LAST,
            width=2,
            fill="#374151",
            joinstyle="round",
            arrowshape=(12, 14, 6)
        )

    # ---------------- CLICK ----------------
    def on_canvas_click(self, event):
        node = self.find_node_at(event.x, event.y)

        if self.current_tool == "ARROW":
            if node:
                if not self.connection_start_node:
                    self.connection_start_node = node
                else:
                    self.add_connection(self.connection_start_node, node)
                    self.connection_start_node = None
                    self.current_tool = "SELECT"
        else:
            self.selected_node = node

    def find_node_at(self, x, y):
        for node in reversed(self.nodes):
            if node.contains(x, y):
                return node
        return None

    # ---------------- DRAG ----------------
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

    # ---------------- CONNECTION ----------------
    def add_connection(self, node1, node2):
        label = None

        if node1.node_type == NodeType.DECISION:
            label = simpledialog.askstring("Branch", "TRUE or FALSE?")
            if not label or label.upper() not in ["TRUE", "FALSE"]:
                messagebox.showerror("Error", "Enter TRUE or FALSE")
                return
            label = label.upper()

        x1, y1 = self.get_anchor(node1, node2)
        x2, y2 = self.get_anchor(node2, node1)

        line_id = self.draw_smart_arrow(x1, y1, x2, y2)

        if label:
            color = "green" if label == "TRUE" else "red"

            offset_x = 20 if label == "TRUE" else -20
            offset_y = -10

            self.canvas.create_text(
                (x1 + x2) / 2 + offset_x,
                (y1 + y2) / 2 + offset_y,
                text=label,
                fill=color,
                font=("Arial", 9, "bold")
            )

        self.connections.append((node1, node2, line_id, label))

    def update_connections(self):
        for node1, node2, line_id, _ in self.connections:
            x1, y1 = self.get_anchor(node1, node2)
            x2, y2 = self.get_anchor(node2, node1)

            if abs(x1 - x2) < 10 or abs(y1 - y2) < 10:
                self.canvas.coords(line_id, x1, y1, x2, y2)
            else:
                mid_y = (y1 + y2) // 2
                self.canvas.coords(line_id, x1, y1, x1, mid_y, x2, mid_y, x2, y2)

    # ---------------- CLEAR ----------------
    def clear_canvas(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.nodes = []
        self.connections = []

    # ---------------- CONVERT ----------------
    def convert_to_code(self):
        try:
            builder = ASTBuilder(self.nodes, self.connections)
            graph = builder.build()

            analyzer = SemanticAnalyzer(graph)
            analyzer.analyze()

            generator = CodeGenerator(graph, self.toolbar.get_language())
            code = generator.generate()

            self.show_code_window(code)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_code_window(self, code):
        win = tk.Toplevel(self.root)
        text = scrolledtext.ScrolledText(win)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, code)