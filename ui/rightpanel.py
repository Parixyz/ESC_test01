# stub
from tkinter import ttk

class RightPanel:
    def __init__(self, parent):
        self.panel = ttk.Frame(parent, width=520)
        self.panel.pack(side="right", fill="y")
        self.panel.pack_propagate(False)

        self.game_panel = ttk.Frame(self.panel)
        self.game_panel.pack(fill="both", expand=True, padx=10, pady=10)

    def clear(self):
        for w in self.game_panel.winfo_children():
            w.destroy()
        ttk.Label(self.game_panel, text="Right Panel: Node games appear here.", foreground="#666").pack(
            padx=12, pady=12, anchor="nw"
        )

    def message(self, parent, text: str):
        for w in parent.winfo_children():
            w.destroy()
        ttk.Label(parent, text=text, foreground="#666", wraplength=420, justify="left").pack(
            padx=12, pady=12, anchor="nw"
        )