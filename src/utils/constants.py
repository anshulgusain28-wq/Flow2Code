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

# Vibrant Modern Palette
COLORS = {
    "primary": "#2563EB",    # Vibrant Blue
    "primary_hover": "#1D4ED8",
    "success": "#059669",    # Vibrant Green
    "success_hover": "#047857",
    "warning": "#D97706",    # Vibrant Amber
    "danger": "#DC2626",     # Vibrant Red
    "background": "#F0F2F5", # Clean Gray-White
    "surface": "#FFFFFF",    # Pure White
    "text": "#111827",       # Almost Black
    "text_light": "#6B7280", # Gray Text
    "grid": "#E5E7EB",       # Light Gray
    
    # Shape Fills (Pastel but colorful)
    "start_fill": "#D1FAE5", # Mint
    "end_fill": "#FEE2E2",   # Rose
    "process_fill": "#DBEAFE", # Blue
    "decision_fill": "#FEF3C7", # Amber
    "io_fill": "#E0E7FF",    # Indigo
    
    # Shape Outlines (Bold)
    "start_outline": "#059669",
    "end_outline": "#DC2626",
    "process_outline": "#2563EB",
    "decision_outline": "#D97706",
    "io_outline": "#4F46E5",
}

# Icons for UI
ICONS = {
    NodeType.START: "🟢",
    NodeType.END: "🛑",
    NodeType.PROCESS: "⚙️",
    NodeType.DECISION: "🔶",
    NodeType.INPUT: "📥",
    NodeType.OUTPUT: "📤",
    "ARROW": "🔗",
    "SELECT": "👆",
    "CONVERT": "▶️",
    "CLEAR": "🗑️",
    "AUTO": "⚡"
}

# Shape configurations
# SHAPE_DEFAULTS = {
#     NodeType.START: {"shape": "oval", "color": COLORS["start_fill"], "outline": COLORS["start_outline"], "width": 140, "height": 60},
#     NodeType.END: {"shape": "oval", "color": COLORS["end_fill"], "outline": COLORS["end_outline"], "width": 140, "height": 60},
#     NodeType.PROCESS: {"shape": "rectangle", "color": COLORS["process_fill"], "outline": COLORS["process_outline"], "width": 160, "height": 70},
#     NodeType.DECISION: {"shape": "diamond", "color": COLORS["decision_fill"], "outline": COLORS["decision_outline"], "width": 140, "height": 100},
#     NodeType.INPUT: {"shape": "parallelogram", "color": COLORS["io_fill"], "outline": COLORS["io_outline"], "width": 160, "height": 70},
#     NodeType.OUTPUT: {"shape": "parallelogram", "color": COLORS["io_fill"], "outline": COLORS["io_outline"], "width": 160, "height": 70},
# }


SHAPE_DEFAULTS = {
    NodeType.START: {
        "shape": "oval",
        "width": 120,
        "height": 50,
        "color": "#D1FAE5",
        "outline": "#059669"
    },
    NodeType.END: {
        "shape": "oval",
        "width": 120,
        "height": 50,
        "color": "#FEE2E2",
        "outline": "#DC2626"
    },
    NodeType.PROCESS: {
        "shape": "rectangle",
        "width": 140,
        "height": 60,
        "color": "#F3F4F6",
        "outline": "#374151"
    },
    NodeType.DECISION: {
        "shape": "diamond",
        "width": 140,
        "height": 100,
        "color": "#FEF3C7",
        "outline": "#D97706"
    },
    NodeType.INPUT: {
        "shape": "rectangle",
        "width": 140,
        "height": 60,
        "color": "#DBEAFE",
        "outline": "#2563EB"
    },
    NodeType.OUTPUT: {
        "shape": "rectangle",
        "width": 140,
        "height": 60,
        "color": "#E0E7FF",
        "outline": "#4338CA"
    }
}