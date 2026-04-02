import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext, font as tkfont
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
        self.connections = []   # list of dicts: {node1, node2, line_id, label, label_bg, label_text}
        self.current_tool = "SELECT"
        self.selected_node = None
        self.connection_start_node = None

        # ── Layout ──────────────────────────────────────────────────────
        self.paned_window = tk.PanedWindow(
            root, orient=tk.HORIZONTAL,
            bg=COLORS["background"], sashwidth=6,
            sashrelief=tk.FLAT, sashpad=2
        )
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.toolbar_pane = tk.Frame(self.paned_window, bg=COLORS["panel"])
        self.toolbar = Toolbar(self.toolbar_pane, self.set_tool, self.on_drop)
        self.toolbar.pack(fill=tk.BOTH, expand=True)
        self.paned_window.add(self.toolbar_pane, minsize=260, width=300)

        # Canvas area
        self.canvas_pane = tk.Frame(self.paned_window, bg=COLORS["background"])
        self.canvas = tk.Canvas(
            self.canvas_pane,
            bg=COLORS["canvas_bg"],
            highlightthickness=0,
            relief=tk.FLAT
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        self.paned_window.add(self.canvas_pane, minsize=500)

        self.draw_grid()

        # ── Bindings ────────────────────────────────────────────────────
        self.canvas.bind("<Button-1>",        self.on_canvas_click)
        self.canvas.bind("<B1-Motion>",       self.on_canvas_drag)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Configure>",       self.on_resize)
        self.root.bind("<Delete>",            lambda e: self.delete_selected())
        self.root.bind("<Escape>",            lambda e: self._deselect_all())

    # ────────────── GRID ──────────────────────────────────────────────
    def draw_grid(self):
        self.canvas.delete("grid")
        w = self.canvas.winfo_width() or 1600
        h = self.canvas.winfo_height() or 1000
        step = 30

        for i in range(0, w, step):
            self.canvas.create_line(i, 0, i, h, fill="#E5E7EB", tags="grid")
        for i in range(0, h, step):
            self.canvas.create_line(0, i, w, i, fill="#E5E7EB", tags="grid")

        self.canvas.tag_lower("grid")

    def on_resize(self, event):
        self.draw_grid()

    # ────────────── TOOL SELECTION ────────────────────────────────────
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
        # Clear selection highlight when switching tool
        if tool != "SELECT":
            self._deselect_all()

    # ────────────── ADD NODE ──────────────────────────────────────────
    def on_drop(self, root_x, root_y, tool_type):
        canvas_x = root_x - self.canvas.winfo_rootx()
        canvas_y = root_y - self.canvas.winfo_rooty()
        if 0 <= canvas_x <= self.canvas.winfo_width() and 0 <= canvas_y <= self.canvas.winfo_height():
            self.add_node(tool_type, canvas_x, canvas_y)

    def add_node(self, node_type, x, y):
        defaults = {
            NodeType.START:    "Start",
            NodeType.END:      "End",
            NodeType.PROCESS:  "Process",
            NodeType.DECISION: "Condition",
            NodeType.INPUT:    "Input",
            NodeType.OUTPUT:   "Output",
        }
        text = defaults.get(node_type, "Node")
        node = FlowchartShape(self.canvas, node_type, x, y, text)
        self.nodes.append(node)

        if node_type in [NodeType.PROCESS, NodeType.DECISION, NodeType.INPUT, NodeType.OUTPUT]:
            self.prompt_node_text(node)

    def prompt_node_text(self, node):
        prompts = {
            NodeType.INPUT:    "Enter variable name:",
            NodeType.OUTPUT:   "Enter value to print:",
            NodeType.DECISION: "Enter condition (e.g. x > 5):",
        }
        prompt = prompts.get(node.node_type, "Enter code:")
        text = simpledialog.askstring("Edit Node", prompt, parent=self.root)
        if text:
            node.update_text(text)

    # ────────────── CLICK / DRAG ──────────────────────────────────────
    def on_canvas_click(self, event):
        node = self.find_node_at(event.x, event.y)

        if self.current_tool == "ARROW":
            if clicked_node:
                if self.connection_start_node is None:
                    self.connection_start_node = clicked_node
                    clicked_node.set_selected(True)
                else:
                    if clicked_node != self.connection_start_node:
                        self.connection_start_node.set_selected(False)
                        self.add_connection(self.connection_start_node, clicked_node)
                        self.connection_start_node = None
                        self.current_tool = "SELECT"
            else:
                if self.connection_start_node:
                    self.connection_start_node.set_selected(False)
                self.connection_start_node = None
        else:
            self._deselect_all()
            self.selected_node = clicked_node
            if clicked_node:
                clicked_node.set_selected(True)

    def _deselect_all(self):
        if self.selected_node:
            self.selected_node.set_selected(False)
            self.selected_node = None
        if self.connection_start_node:
            self.connection_start_node.set_selected(False)
            self.connection_start_node = None

    def on_canvas_drag(self, event):
        if self.selected_node and self.current_tool != "ARROW":
            dx = event.x - self.selected_node.x
            dy = event.y - self.selected_node.y
            self.selected_node.move(dx, dy)
            self.update_connections()

    def on_double_click(self, event):
        node = self.find_node_at(event.x, event.y)
        if node:
            self.prompt_node_text(node)

    # ────────────── CONNECTION ────────────────────────────────────────
    def add_connection(self, node1, node2):
        # Prevent duplicate
        for c in self.connections:
            if c["node1"] == node1 and c["node2"] == node2:
                return

        label = None
        if node1.node_type == NodeType.DECISION:
            label = simpledialog.askstring(
                "Branch Type",
                "Enter branch label (TRUE or FALSE):",
                parent=self.root
            )
            if not label or label.strip().upper() not in ["TRUE", "FALSE"]:
                messagebox.showerror("Error", "You must enter TRUE or FALSE")
                return
            label = label.strip().upper()

        # Calculate edge-to-edge anchor points
        ax, ay, bx, by = node1.best_anchor(node2)

        line_id = self.canvas.create_line(
            ax, ay, bx, by,
            arrow=tk.LAST,
            arrowshape=(14, 18, 6),
            width=2,
            fill=COLORS["arrow"],
            smooth=True,
            joinstyle=tk.ROUND
        )

        # Label with background pill
        label_bg_id = None
        label_text_id = None
        if label:
            mid_x = (ax + bx) / 2
            mid_y = (ay + by) / 2
            # background rounded rect
            pad_x, pad_y = 10, 4
            bg_x1 = mid_x - pad_x
            bg_y1 = mid_y - pad_y - 7
            bg_x2 = mid_x + pad_x
            bg_y2 = mid_y + pad_y - 7
            label_bg_id = self.canvas.create_rectangle(
                bg_x1, bg_y1, bg_x2, bg_y2,
                fill=COLORS["arrow_label_bg"],
                outline=COLORS["arrow"],
                width=1
            )
            label_text_id = self.canvas.create_text(
                mid_x, mid_y - 7,
                text=label,
                fill=COLORS["arrow_label_fg"],
                font=("Segoe UI", 9, "bold")
            )

        # Ensure shapes are always on top
        for node in self.nodes:
            self.canvas.tag_raise(node.shape_id)
            self.canvas.tag_raise(node.text_id)

        self.connections.append({
            "node1": node1,
            "node2": node2,
            "line_id": line_id,
            "label": label,
            "label_bg": label_bg_id,
            "label_text": label_text_id,
        })

    def update_connections(self):
        for c in self.connections:
            node1, node2 = c["node1"], c["node2"]
            ax, ay, bx, by = node1.best_anchor(node2)
            self.canvas.coords(c["line_id"], ax, ay, bx, by)

            # Move label & bg
            if c["label"] and c["label_text"]:
                mid_x = (ax + bx) / 2
                mid_y = (ay + by) / 2 - 7
                self.canvas.coords(c["label_text"], mid_x, mid_y)
                pad_x, pad_y = 10, 4
                self.canvas.coords(
                    c["label_bg"],
                    mid_x - pad_x, mid_y - pad_y,
                    mid_x + pad_x, mid_y + pad_y
                )

    # ────────────── FIND NODE ─────────────────────────────────────────
    def find_node_at(self, x, y):
        for node in reversed(self.nodes):
            if node.contains(x, y):
                return node
        return None

    # ────────────── AUTO CONNECT ──────────────────────────────────────
    def auto_connect(self):
        if len(self.nodes) < 2:
            return
        sorted_nodes = sorted(self.nodes, key=lambda n: n.y)
        for i in range(len(sorted_nodes) - 1):
            self.add_connection(sorted_nodes[i], sorted_nodes[i + 1])
        messagebox.showinfo("Auto Connect", "Nodes connected by vertical order.")

    # ────────────── DELETE / CLEAR ────────────────────────────────────
    def delete_selected(self):
        if not self.selected_node:
            return
        # Remove connected lines
        remaining = []
        for c in self.connections:
            if c["node1"] == self.selected_node or c["node2"] == self.selected_node:
                self.canvas.delete(c["line_id"])
                if c["label_bg"]:
                    self.canvas.delete(c["label_bg"])
                if c["label_text"]:
                    self.canvas.delete(c["label_text"])
            else:
                remaining.append(c)
        self.connections = remaining

        self.nodes.remove(self.selected_node)
        self.selected_node.delete()
        self.selected_node = None

    def clear_canvas(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.nodes = []
        self.connections = []

    # ────────────── CONVERT ───────────────────────────────────────────
    def convert_to_code(self):
        language = self.toolbar.get_language()
        try:
            # Build a simple connections list compatible with ASTBuilder
            conn_list = [(c["node1"], c["node2"], c["line_id"], c["label"]) for c in self.connections]
            builder = ASTBuilder(self.nodes, conn_list)
            graph = builder.build()
            analyzer = SemanticAnalyzer(graph)
            analyzer.analyze()
            generator = CodeGenerator(graph, language)
            code = generator.generate()
            self.show_code_window(code, language)
        except SemanticError as e:
            messagebox.showerror("Semantic Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ────────────── OUTPUT WINDOW ─────────────────────────────────────
    def show_code_window(self, code, language):
        win = tk.Toplevel(self.root)
        win.title(f"Generated {language} Code – Flow2Code")
        win.geometry("800x600")
        win.configure(bg=COLORS["background"])
        win.minsize(500, 400)

        # Title bar
        header = tk.Frame(win, bg=COLORS["primary_dark"], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(
            header,
            text=f"▶  {language} Output",
            bg=COLORS["primary_dark"],
            fg="white",
            font=("Segoe UI", 14, "bold"),
            padx=16
        ).pack(side=tk.LEFT, pady=10)

        # Code area
        frame = tk.Frame(win, bg=COLORS["surface"], padx=2, pady=2)
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        text_area = scrolledtext.ScrolledText(
            frame,
            font=("Cascadia Code", 12) if "Cascadia Code" in tkfont.families() else ("Consolas", 12),
            bg="#1E1E2E",
            fg="#CDD6F4",
            insertbackground="white",
            relief=tk.FLAT,
            wrap=tk.NONE,
            padx=12, pady=12,
            selectbackground=COLORS["primary"]
        )
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, code)
        text_area.config(state=tk.DISABLED)