# games/codeobs.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from games.base import GameBase


class CodeObservatory(GameBase):
    game_id = "codes"
    title = "Where Did Jack Go?"

    SNIPS = {
        "A": """dest = 'N2'
if 7 % 2 == 1:
    dest = 'N4'
print(dest)""",
        "B": """x = 20
if x > 10:
    next_node = 'N5'
else:
    next_node = 'N3'""",
        "C": """route = 'N1'
for _ in range(2):
    route = 'N6'
print(route)""",
    }

    def __init__(self, app):
        super().__init__(app)
        self.text = None
        self.current = None

    def mount(self, parent):
        super().mount(parent)

        ttk.Label(parent, text=self.title, font=("Segoe UI", 11, "bold")).pack(
            padx=12, pady=(12, 6), anchor="nw"
        )
        ttk.Label(
            parent,
            text=(
                "This is a 3-question routing test.\n"
                "Use: showcode A|B|C\n"
                "Answer each with: solve code <A|B|C> <N#>\n"
                "First wrong attempt on a question costs points."
            ),
            wraplength=420,
            justify="left",
        ).pack(padx=12, pady=(0, 8), anchor="nw")

        self.text = tk.Text(parent, height=18, bg="#0a0f1a", fg="#00ff88", insertbackground="#00ff88")
        self.text.pack(padx=12, pady=(0, 10), fill="both", expand=True, anchor="nw")
        self.text.insert("end", "Use: showcode A  (or B/C)\n")
        self.text.config(state="disabled")

    def show(self, key: str):
        key = (key or "").strip().upper()
        if key not in self.SNIPS:
            self.safe_print("[ERR] showcode expects A/B/C.")
            return
        self.current = key
        if not self.text:
            return
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("end", f"--- Snippet {key} ---\n\n{self.SNIPS[key]}\n")
        self.text.config(state="disabled")
        self.safe_print(f"[N3] Snippet {key} loaded.")
