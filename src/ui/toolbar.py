import tkinter as tk
from tkinter import ttk
from src.utils.constants import NodeType, COLORS, ICONS


class ModernButton(tk.Frame):
    """A pill-shaped button with icon + label and hover animation."""

    def __init__(self, master, text, icon, command=None,
                bg=None, accent=None, width=None):
        _bg = bg or COLORS["surface"]
        _accent = accent or COLORS["primary"]
        super().__init__(master, bg=_bg, cursor="hand2",
                        highlightthickness=1,
                        highlightbackground=COLORS["border"],
                        highlightcolor=_accent)

        self._bg = _bg
        self._accent = _accent
        self._hover_bg = COLORS["surface_hover"]
        self.command = command

        inner = tk.Frame(self, bg=_bg, padx=8, pady=10)
        inner.pack(fill=tk.BOTH, expand=True)
        self._inner = inner

        self._icon_lbl = tk.Label(
            inner, text=icon,
            bg=_bg, fg=_accent,
            font=("Segoe UI", 18)
        )
        self._icon_lbl.pack()

        self._text_lbl = tk.Label(
            inner, text=text,
            bg=_bg, fg=COLORS["text"],
            font=("Segoe UI", 9, "bold")
        )
        self._text_lbl.pack()

        for w in (self, inner, self._icon_lbl, self._text_lbl):
            w.bind("<Enter>",    self._on_enter)
            w.bind("<Leave>",    self._on_leave)
            w.bind("<Button-1>", self._on_click)

    def _on_enter(self, _=None):
        self._set_bg(self._hover_bg)
        self.config(highlightbackground=self._accent)

    def _on_leave(self, _=None):
        self._set_bg(self._bg)
        self.config(highlightbackground=COLORS["border"])

    def _on_click(self, _=None):
        if self.command:
            self.command()

    def _set_bg(self, color):
        self.config(bg=color)
        self._inner.config(bg=color)
        self._icon_lbl.config(bg=color)
        self._text_lbl.config(bg=color)


class DraggableCard(ModernButton):
    """A shape card that can be dragged onto the canvas."""

    def __init__(self, master, text, icon, tool_type, on_drag_start, on_drag_end, accent=None):
        super().__init__(master, text, icon, command=None,
                        bg=COLORS["surface"], accent=accent or COLORS["primary"])
        self.tool_type = tool_type
        self.on_drag_start = on_drag_start
        self.on_drag_end = on_drag_end
        self.drag_win = None

        for w in (self, self._inner, self._icon_lbl, self._text_lbl):
            w.bind("<Button-1>",       self.start_drag)
            w.bind("<B1-Motion>",      self.do_drag)
            w.bind("<ButtonRelease-1>", self.end_drag)

    def start_drag(self, event):
        self.on_drag_start(self.tool_type)
        self.drag_win = tk.Toplevel()
        self.drag_win.overrideredirect(True)
        self.drag_win.attributes("-alpha", 0.85)
        self.drag_win.attributes("-topmost", True)

        frame = tk.Frame(self.drag_win, bg=self._accent, padx=14, pady=10)
        frame.pack()
        tk.Label(frame,
                text=f"{self._icon_lbl.cget('text')}  {self._text_lbl.cget('text')}",
                bg=self._accent, fg="white",
                font=("Segoe UI", 13, "bold")).pack()
        self._update_drag_win()

    def do_drag(self, event):
        self._update_drag_win()

    def _update_drag_win(self):
        if self.drag_win:
            x = self.winfo_pointerx()
            y = self.winfo_pointery()
            self.drag_win.geometry(f"+{x + 14}+{y + 14}")

    def end_drag(self, event):
        if self.drag_win:
            self.drag_win.destroy()
            self.drag_win = None
        self.on_drag_end(self.winfo_pointerx(), self.winfo_pointery(), self.tool_type)


class Toolbar(tk.Frame):
    def __init__(self, master, on_tool_select, on_drop):
        super().__init__(master, bg=COLORS["panel"])
        self.on_tool_select = on_tool_select
        self.on_drop = on_drop
        self.lang_var = tk.StringVar(value="Python")

        # Scrollable container
        self._canvas = tk.Canvas(self, bg=COLORS["panel"], highlightthickness=0)
        self._scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._frame = tk.Frame(self._canvas, bg=COLORS["panel"])

        self._frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        )
        self._window_id = self._canvas.create_window((0, 0), window=self._frame, anchor="nw", tags="frame")
        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig("frame", width=e.width))

        self._canvas.pack(side="left", fill="both", expand=True)
        self._scrollbar.pack(side="right", fill="y")

        self._bind_mousewheel(self._canvas)
        self._bind_mousewheel(self._frame)
        self._build()

    def _bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel)
        for child in widget.winfo_children():
            self._bind_mousewheel(child)

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ── Build sidebar layout ──────────────────────────────────────────
    def _build(self):
        f = self._frame   # shortcut

        # ── App Header ──────────────────────────────────────────
        header = tk.Frame(f, bg=COLORS["primary_dark"])
        header.pack(fill=tk.X)
        tk.Label(
            header, text="Flow2Code",
            bg=COLORS["primary_dark"], fg="white",
            font=("Segoe UI", 18, "bold"), pady=16
        ).pack()
        tk.Label(
            header, text="Visual Flowchart Compiler",
            bg=COLORS["primary_dark"], fg="#93C5FD",
            font=("Segoe UI", 9), pady=0
        ).pack(pady=(0, 14))

        # ── Body ────────────────────────────────────────────────
        body = tk.Frame(f, bg=COLORS["panel"])
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        # ── Language Selector ───────────────────────────────────
        self._section_label(body, "TARGET LANGUAGE")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dark.TCombobox",
            fieldbackground=COLORS["surface"],
            background=COLORS["surface"],
            foreground=COLORS["text"],
            selectbackground=COLORS["primary_dark"],
            selectforeground="white",
            arrowcolor=COLORS["text"],
            bordercolor=COLORS["border"],
        )
        lang_combo = ttk.Combobox(
            body, textvariable=self.lang_var,
            values=["Python", "C++"],
            state="readonly",
            font=("Segoe UI", 11),
            style="Dark.TCombobox"
        )
        lang_combo.pack(fill=tk.X, pady=(4, 18))

        # ── Shapes Grid ─────────────────────────────────────────
        self._section_label(body, "SHAPES  (drag onto canvas)")

        shapes_frame = tk.Frame(body, bg=COLORS["panel"])
        shapes_frame.pack(fill=tk.X, pady=(4, 0))
        shapes_frame.columnconfigure(0, weight=1)
        shapes_frame.columnconfigure(1, weight=1)

        shape_accents = {
            NodeType.START:    COLORS["start_outline"],
            NodeType.END:      COLORS["end_outline"],
            NodeType.PROCESS:  COLORS["process_outline"],
            NodeType.DECISION: COLORS["decision_outline"],
            NodeType.INPUT:    COLORS["io_outline"],
            NodeType.OUTPUT:   COLORS["io_outline"],
        }

        shapes = [
            ("Start",    NodeType.START),
            ("Process",  NodeType.PROCESS),
            ("Decision", NodeType.DECISION),
            ("End",      NodeType.END),
            ("Input",    NodeType.INPUT),
            ("Output",   NodeType.OUTPUT),
        ]

        for i, (text, tool_type) in enumerate(shapes):
            card = DraggableCard(
                shapes_frame, text, ICONS[tool_type], tool_type,
                on_drag_start=self._drag_start,
                on_drag_end=self._drag_end,
                accent=shape_accents[tool_type]
            )
            self._bind_mousewheel(card)
            card.grid(row=i // 2, column=i % 2, padx=5, pady=5, sticky="ew")

        # ── Divider ─────────────────────────────────────────────
        self._divider(body)

        # ── Actions ─────────────────────────────────────────────
        self._section_label(body, "TOOLS & ACTIONS")

        tools_frame = tk.Frame(body, bg=COLORS["panel"])
        tools_frame.pack(fill=tk.X, pady=(4, 0))
        tools_frame.columnconfigure(0, weight=1)
        tools_frame.columnconfigure(1, weight=1)

        pair_tools = [
            ("Connect",  ICONS["ARROW"],   "ARROW",  COLORS["primary"]),
            ("Delete",   "✕",              "DELETE", COLORS["danger"]),
        ]
        for i, (text, icon, action, accent) in enumerate(pair_tools):
            btn = ModernButton(
                tools_frame, text, icon,
                command=lambda a=action: self.on_tool_select(a),
                accent=accent
            )
            self._bind_mousewheel(btn)
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")

        wide_tools = [
            ("Auto Connect", ICONS["AUTO"], lambda: self.on_tool_select("AUTO_CONNECT"), "#FEF3C7"),
            ("Compile", ICONS["CONVERT"], lambda: self.on_tool_select("CONVERT"), "#D1FAE5"),
            ("Clear All", "🔁", lambda: self.on_tool_select("CLEAR"), COLORS["surface"]),
        ]
        for i, (text, icon, action, accent) in enumerate(wide_tools):
            btn = ModernButton(
                tools_frame, text, icon,
                command=lambda a=action: self.on_tool_select(a),
                accent=accent
            )
            self._bind_mousewheel(btn)
            btn.grid(row=i + 1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # ── Footer tip ──────────────────────────────────────────
        self._divider(body)
        tk.Label(
            body,
            text="Tip: Double-click a shape to edit its text.\nPress Delete to remove selected.",
            bg=COLORS["panel"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 8),
            justify="left",
            wraplength=230
        ).pack(anchor="w", pady=(4, 0))

    # ── Helpers ───────────────────────────────────────────────────────
    def _section_label(self, parent, text):
        tk.Label(
            parent, text=text,
            bg=COLORS["panel"],
            fg=COLORS["text_light"],
            font=("Segoe UI", 8, "bold"),
            anchor="w"
        ).pack(fill=tk.X, pady=(12, 0))

    def _divider(self, parent):
        tk.Frame(parent, bg=COLORS["border"], height=1).pack(fill=tk.X, pady=10)

    def get_language(self):
        return self.lang_var.get()

    def _drag_start(self, tool_type):
        pass

    def _drag_end(self, root_x, root_y, tool_type):
        self.on_drop(root_x, root_y, tool_type)
