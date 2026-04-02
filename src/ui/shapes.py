from src.utils.constants import SHAPE_DEFAULTS

class FlowchartShape:
    def __init__(self, canvas, node_type, x, y, text):
        self.canvas = canvas
        self.node_type = node_type
        self.x = x
        self.y = y
        self.text = text
        self.shape_id = None
        self.text_id = None
        
        defaults = SHAPE_DEFAULTS[node_type]
        self.width = defaults["width"]
        self.height = defaults["height"]
        self.color = defaults["color"]
        self.outline = defaults["outline"]
        
        self.draw()

    def draw(self):
        x1 = self.x - self.width / 2
        y1 = self.y - self.height / 2
        x2 = self.x + self.width / 2
        y2 = self.y + self.height / 2
        
        # Thicker border for modern look
        common_opts = {"fill": self.color, "outline": self.outline, "width": 3}

        if self.node_type in [NodeType.START, NodeType.END]:
            self.shape_id = self.canvas.create_oval(x1, y1, x2, y2, **common_opts)
        elif self.node_type == NodeType.PROCESS:
            self.shape_id = self.canvas.create_rectangle(x1, y1, x2, y2, **common_opts)
        elif self.node_type == NodeType.DECISION:
            self.shape_id = self.canvas.create_polygon(
                self.x, y1, x2, self.y, self.x, y2, x1, self.y,
                **common_opts
            )
        elif self.node_type in [NodeType.INPUT, NodeType.OUTPUT]:
            skew = 25
            self.shape_id = self.canvas.create_polygon(
                x1 + skew, y1, x2, y1, x2 - skew, y2, x1, y2,
                **common_opts
            )

        # Crisp, modern font
        font_spec = ("Segoe UI", 11, "bold")
        self.text_id = self.canvas.create_text(self.x, self.y, text=self.text, width=self.width - 20, 
                                               font=font_spec, fill=COLORS["text"], justify="center")

    def move(self, dx, dy):
        if self.id:
            self.canvas.move(self.id, dx, dy)
        self.canvas.move(self.text_id, dx, dy)
        self.x += dx
        self.y += dy

    def update_text(self, new_text):
        self.text = new_text
        self.canvas.itemconfig(self.text_id, text=new_text)

    def contains(self, px, py):
        if not self.id:
            return False

        bbox = self.canvas.bbox(self.id)
        if not bbox:
            return False

        x1, y1, x2, y2 = bbox
        return x1 <= px <= x2 and y1 <= py <= y2

    def delete(self):
        if self.id:
            self.canvas.delete(self.id)
        self.canvas.delete(self.text_id)