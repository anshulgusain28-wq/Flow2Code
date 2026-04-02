import tkinter as tk
from src.utils.constants import NodeType, SHAPE_DEFAULTS, COLORS

class FlowchartShape:
    def __init__(self, canvas, node_type, x, y, text=""):
        self.canvas = canvas
        self.node_type = node_type
        self.x = x
        self.y = y
        self.text = text
        self.shape_id = None
        self.text_id = None
        self._selected = False

        defaults = SHAPE_DEFAULTS[node_type]
        self.width = defaults["width"]
        self.height = defaults["height"]
        self.color = defaults["color"]
        self.outline = defaults["outline"]

        self.draw()

    # ─────────── Drawing ───────────
    def draw(self):
        x1 = self.x - self.width / 2
        y1 = self.y - self.height / 2
        x2 = self.x + self.width / 2
        y2 = self.y + self.height / 2

        common_opts = {"fill": self.color, "outline": self.outline, "width": 2}

        if self.node_type in [NodeType.START, NodeType.END]:
            # Rounded pill (oval)
            self.shape_id = self.canvas.create_oval(x1, y1, x2, y2, **common_opts)

        elif self.node_type == NodeType.PROCESS:
            # Rounded rectangle via polygon (8-point)
            r = 10
            self.shape_id = self.canvas.create_polygon(
                x1+r, y1,  x2-r, y1,
                x2,   y1+r, x2, y2-r,
                x2-r, y2,  x1+r, y2,
                x1,   y2-r, x1, y1+r,
                smooth=True, **common_opts
            )

        elif self.node_type == NodeType.DECISION:
            # Diamond
            self.shape_id = self.canvas.create_polygon(
                self.x, y1,
                x2,     self.y,
                self.x, y2,
                x1,     self.y,
                **common_opts
            )

        elif self.node_type in [NodeType.INPUT, NodeType.OUTPUT]:
            skew = 22
            self.shape_id = self.canvas.create_polygon(
                x1+skew, y1,
                x2,      y1,
                x2-skew, y2,
                x1,      y2,
                **common_opts
            )

        # Label – always bright white, wrapped tightly
        text_width = self.width - 28
        font_spec = ("Segoe UI", 10, "bold")
        self.text_id = self.canvas.create_text(
            self.x, self.y,
            text=self.text,
            width=text_width,
            font=font_spec,
            fill=COLORS["shape_text"],
            justify="center"
        )

    # ─────────── Selection highlight ───────────
    def set_selected(self, selected: bool):
        if self._selected == selected:
            return
        self._selected = selected
        lw = 3 if selected else 2
        outline_color = "#FFFFFF" if selected else self.outline
        self.canvas.itemconfig(self.shape_id, outline=outline_color, width=lw)

    # ─────────── Edge anchor (for proper connection routing) ───────────
    def get_edge_point(self, direction: str):
        """Return (x, y) of the shape edge in a cardinal direction."""
        hw = self.width / 2
        hh = self.height / 2
        if direction == "top":
            return (self.x, self.y - hh)
        elif direction == "bottom":
            return (self.x, self.y + hh)
        elif direction == "left":
            return (self.x - hw, self.y)
        elif direction == "right":
            return (self.x + hw, self.y)
        return (self.x, self.y)

    def best_anchor(self, other):
        """Pick (from_x, from_y, to_x, to_y) using edge anchors based on relative position."""
        dx = other.x - self.x
        dy = other.y - self.y

        if abs(dy) >= abs(dx):
            # Mostly vertical
            if dy >= 0:
                a = self.get_edge_point("bottom")
                b = other.get_edge_point("top")
            else:
                a = self.get_edge_point("top")
                b = other.get_edge_point("bottom")
        else:
            # Mostly horizontal
            if dx >= 0:
                a = self.get_edge_point("right")
                b = other.get_edge_point("left")
            else:
                a = self.get_edge_point("left")
                b = other.get_edge_point("right")

        return a[0], a[1], b[0], b[1]

    # ─────────── Move ───────────
    def move(self, dx, dy):
        self.canvas.move(self.shape_id, dx, dy)
        self.canvas.move(self.text_id, dx, dy)
        self.x += dx
        self.y += dy

    def update_text(self, new_text):
        self.text = new_text
        self.canvas.itemconfig(self.text_id, text=self.text)

    def contains(self, x, y):
        x1 = self.x - self.width / 2
        y1 = self.y - self.height / 2
        x2 = self.x + self.width / 2
        y2 = self.y + self.height / 2
        return x1 <= x <= x2 and y1 <= y <= y2

    def delete(self):
        self.canvas.delete(self.shape_id)
        self.canvas.delete(self.text_id)
