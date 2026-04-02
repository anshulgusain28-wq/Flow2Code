from enum import Enum

class NodeType(Enum):
    START = "START"
    END = "END"
    PROCESS = "PROCESS"      # Statement
    DECISION = "DECISION"    # Condition (Diamond)
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

class TokenType(Enum):
    IDENTIFIER = "IDENTIFIER"
    KEYWORD = "KEYWORD"
    OPERATOR = "OPERATOR"
    LITERAL = "LITERAL"
    UNKNOWN = "UNKNOWN"

# Modern Dark Theme Palette
COLORS = {
    "primary":          "#4F8EF7",   # Bright Blue
    "primary_dark":     "#2563EB",
    "primary_hover":    "#3B72D9",
    "success":          "#34D399",   # Emerald
    "success_dark":     "#059669",
    "warning":          "#FBBF24",   # Amber
    "warning_dark":     "#D97706",
    "danger":           "#F87171",   # Rose
    "danger_dark":      "#DC2626",
    "background":       "#1A1D27",   # Deep Navy
    "panel":            "#21263A",   # Sidebar Panel
    "surface":          "#2C3249",   # Card Surface
    "surface_hover":    "#353D5C",   # Card Hover
    "border":           "#3B4262",   # Subtle border
    "text":             "#E2E8F0",   # Near White
    "text_light":       "#94A3B8",   # Muted Blue-Gray
    "text_dim":         "#64748B",
    "grid":             "#252A3D",   # Very subtle dark grid line
    "canvas_bg":        "#1E2133",   # Canvas background

    # Shape Fills – rich, saturated but not blinding
    "start_fill":       "#064E3B",   # Dark Emerald
    "end_fill":         "#7F1D1D",   # Dark Rose
    "process_fill":     "#1E3A5F",   # Deep Blue
    "decision_fill":    "#451A03",   # Deep Amber
    "io_fill":          "#1E1B4B",   # Deep Indigo

    # Shape text color (always bright so it's readable on dark fills)
    "shape_text":       "#F1F5F9",

    # Shape Outlines (Bold, vibrant)
    "start_outline":    "#34D399",   # Emerald
    "end_outline":      "#F87171",   # Rose
    "process_outline":  "#4F8EF7",   # Blue
    "decision_outline": "#FBBF24",   # Amber
    "io_outline":       "#818CF8",   # Indigo

    # Connection arrow
    "arrow":            "#60A5FA",   # Sky Blue
    "arrow_label_bg":   "#2C3249",
    "arrow_label_fg":   "#FBBF24",
}

# Icons for UI
ICONS = {
    NodeType.START:    "▶",
    NodeType.END:      "⏹",
    NodeType.PROCESS:  "⚙",
    NodeType.DECISION: "◆",
    NodeType.INPUT:    "⬇",
    NodeType.OUTPUT:   "⬆",
    "ARROW":           "⤴",
    "SELECT":          "↖",
    "CONVERT":         "▶",
    "CLEAR":           "↺",
    "AUTO":            "⚡",
}

# Shape configurations
SHAPE_DEFAULTS = {
    NodeType.START: {"shape": "oval", "color": COLORS["start_fill"], "outline": COLORS["start_outline"], "width": 140, "height": 60},
    NodeType.END: {"shape": "oval", "color": COLORS["end_fill"], "outline": COLORS["end_outline"], "width": 140, "height": 60},
    NodeType.PROCESS: {"shape": "rectangle", "color": COLORS["process_fill"], "outline": COLORS["process_outline"], "width": 160, "height": 70},
    NodeType.DECISION: {"shape": "diamond", "color": COLORS["decision_fill"], "outline": COLORS["decision_outline"], "width": 140, "height": 100},
    NodeType.INPUT: {"shape": "parallelogram", "color": COLORS["io_fill"], "outline": COLORS["io_outline"], "width": 160, "height": 70},
    NodeType.OUTPUT: {"shape": "parallelogram", "color": COLORS["io_fill"], "outline": COLORS["io_outline"], "width": 160, "height": 70},
}
