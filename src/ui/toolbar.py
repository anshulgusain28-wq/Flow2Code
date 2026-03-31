import tkinter as tk
from tkinter import ttk
from src.utils.constants import NodeType, COLORS, ICONS

class ModernButton(tk.Label):
    def __init__(self, master, text, icon, command=None, bg=COLORS["surface"]):
        self.default_bg = bg
        self.hover_bg = "#E5E7EB"
        super().__init__(master, text=f"{icon}\n{text}", bg=self.default_bg, fg=COLORS["text"],
                         font=("Segoe UI", 11, "bold"), relief=tk.FLAT,
                         width=12, height=4, cursor="hand2")
        self.command = command
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        if command:
            self.bind("<Button-1>", lambda e: command())

    def on_enter(self, event):
        self.config(bg=self.hover_bg)

    def on_leave(self, event):
        self.config(bg=self.default_bg)

class DraggableCard(ModernButton):
    def __init__(self, master, text, icon, tool_type, on_drag_start, on_drag_end):
        super().__init__(master, text, icon, command=None)
        self.config(font=("Segoe UI", 12, "bold")) 
        self.tool_type = tool_type
        self.on_drag_start = on_drag_start
        self.on_drag_end = on_drag_end
        self.drag_win = None
        
        self.bind("<Button-1>", self.start_drag)
        self.bind("<B1-Motion>", self.do_drag)
        self.bind("<ButtonRelease-1>", self.end_drag)

    def start_drag(self, event):
        self.on_drag_start(self.tool_type)
        self.drag_win = tk.Toplevel()
        self.drag_win.overrideredirect(True)
        self.drag_win.attributes("-alpha", 0.7)
        self.drag_win.attributes("-topmost", True)
        
        frame = tk.Frame(self.drag_win, bg=COLORS["primary"], padx=10, pady=10)
        frame.pack()
        tk.Label(frame, text=self.cget("text"), bg=COLORS["primary"], fg="white", 
                 font=("Segoe UI", 14)).pack() 
        
        self.update_drag_win()

    def do_drag(self, event):
        self.update_drag_win()

    def update_drag_win(self):
        if self.drag_win:
            x = self.winfo_pointerx()
            y = self.winfo_pointery()
            self.drag_win.geometry(f"+{x+15}+{y+15}")

    def end_drag(self, event):
        if self.drag_win:
            self.drag_win.destroy()
            self.drag_win = None
        
        self.on_drag_end(self.winfo_pointerx(), self.winfo_pointery(), self.tool_type)

class Toolbar(tk.Frame):
    def __init__(self, master, on_tool_select, on_drop):
        super().__init__(master, bg=COLORS["background"])
        self.on_tool_select = on_tool_select
        self.on_drop = on_drop
        self.lang_var = tk.StringVar(value="Python")
        
        # Setup Scrollable Mechanism
        self.canvas = tk.Canvas(self, bg=COLORS["background"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS["background"])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", tags="frame")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Adjust frame width to canvas
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig("frame", width=e.width))

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Mousewheel
        self.bind_mousewheel(self.canvas)
        self.bind_mousewheel(self.scrollable_frame)

        self.create_widgets()

    def bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self.on_mousewheel)
        for child in widget.winfo_children():
            self.bind_mousewheel(child)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def create_widgets(self):
        # Header
        header = tk.Frame(self.scrollable_frame, bg=COLORS["primary"], height=80)
        header.pack(fill=tk.X)
        tk.Label(header, text="Flow2Code ✨", bg=COLORS["primary"], fg="white", 
                 font=("Segoe UI", 20, "bold")).pack(pady=20)

        # Padding container
        content = tk.Frame(self.scrollable_frame, bg=COLORS["background"])
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=20) # reduced padx slightly due to scrollbar

        # Language Selector
        tk.Label(content, text="TARGET LANGUAGE", bg=COLORS["background"], 
                 fg=COLORS["text_light"], font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground=COLORS["surface"], background=COLORS["surface"])
        
        lang_combo = ttk.Combobox(content, textvariable=self.lang_var, 
                                  values=["Python", "C++"], state="readonly", font=("Segoe UI", 12))
        lang_combo.pack(fill=tk.X, pady=(0, 25))

        # Shapes Grid
        tk.Label(content, text="SHAPES", bg=COLORS["background"], 
                 fg=COLORS["text_light"], font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))

        shapes_frame = tk.Frame(content, bg=COLORS["background"])
        shapes_frame.pack(fill=tk.X)

        shapes = [
            ("Start", NodeType.START),
            ("Process", NodeType.PROCESS),
            ("Decision", NodeType.DECISION),
            ("End", NodeType.END),
            ("Input", NodeType.INPUT),
            ("Output", NodeType.OUTPUT),
        ]
        
        shapes_frame.columnconfigure(0, weight=1)
        shapes_frame.columnconfigure(1, weight=1)

        for i, (text, tool_type) in enumerate(shapes):
            icon = ICONS[tool_type]
            btn = DraggableCard(shapes_frame, text, icon, tool_type, 
                                  on_drag_start=self.handle_drag_start,
                                  on_drag_end=self.handle_drag_end)
            # Rebind mousewheel for buttons
            self.bind_mousewheel(btn)
            row = i // 2
            col = i % 2
            btn.grid(row=row, column=col, padx=6, pady=6, sticky="ew")

        # Tools
        tk.Label(content, text="TOOLS & ACTIONS", bg=COLORS["background"], 
                 fg=COLORS["text_light"], font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(25, 8))
        
        tools_frame = tk.Frame(content, bg=COLORS["background"])
        tools_frame.pack(fill=tk.X)
        tools_frame.columnconfigure(0, weight=1)
        tools_frame.columnconfigure(1, weight=1)
        
        tools = [
            ("Connect", ICONS["ARROW"], lambda: self.on_tool_select("ARROW"), COLORS["surface"]),
            ("Delete", "🗑️", lambda: self.on_tool_select("DELETE"), "#FEE2E2"),
        ]
        
        for i, (text, icon, cmd, bg) in enumerate(tools):
             btn = ModernButton(tools_frame, text, icon, cmd, bg=bg)
             self.bind_mousewheel(btn)
             btn.grid(row=0, column=i, padx=6, pady=6, sticky="ew")

        # Full Width Buttons
        wide_tools = [
            ("Auto Connect", ICONS["AUTO"], lambda: self.on_tool_select("AUTO"), "#FEF3C7"),
            ("Compile", ICONS["CONVERT"], lambda: self.on_tool_select("CONVERT"), "#D1FAE5"),
            ("Clear All", "🔁", lambda: self.on_tool_select("CLEAR"), COLORS["surface"]),
        ]
        
        for i, (text, icon, cmd, bg) in enumerate(wide_tools):
            btn = ModernButton(tools_frame, text, icon, cmd, bg=bg)
            self.bind_mousewheel(btn)
            btn.grid(row=i+1, column=0, columnspan=2, padx=6, pady=6, sticky="ew")

    def get_language(self):
        return self.lang_var.get()

    def handle_drag_start(self, tool_type):
        pass

    def handle_drag_end(self, root_x, root_y, tool_type):
        self.on_drop(root_x, root_y, tool_type)
