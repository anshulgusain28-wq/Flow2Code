from src.utils.constants import SHAPE_DEFAULTS

class FlowchartShape:
    def __init__(self, canvas, node_type, x, y, text):
        self.canvas = canvas
        self.node_type = node_type
        self.x = x
        self.y = y
        self.text = text

        self.id = None  # safety

        config = SHAPE_DEFAULTS[node_type]
        w = config["width"]
        h = config["height"]

        left = x - w // 2
        right = x + w // 2
        top = y - h // 2
        bottom = y + h // 2

        shape_type = config.get("shape")

        # ---- DRAW SHAPE ----
        if shape_type == "rectangle":
            self.id = canvas.create_rectangle(
                left, top, right, bottom,
                fill=config["color"], outline=config["outline"], width=2
            )

        elif shape_type == "oval":
            self.id = canvas.create_oval(
                left, top, right, bottom,
                fill=config["color"], outline=config["outline"], width=2
            )

        elif shape_type == "diamond":
            self.id = canvas.create_polygon(
                x, top,
                right, y,
                x, bottom,
                left, y,
                fill=config["color"], outline=config["outline"], width=2
            )

        else:
            # fallback
            self.id = canvas.create_rectangle(
                left, top, right, bottom,
                fill="gray", outline="black", width=2
            )

        # ---- TEXT ----
        self.text_id = canvas.create_text(
            x, y,
            text=text,
            font=("Arial", 10, "bold")
        )

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