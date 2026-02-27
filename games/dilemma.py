# games/dilemma.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from games.base import GameBase


class IteratedDilemma(GameBase):
    game_id = "dilemma"
    title = "Nim Lab"

    def __init__(self, app):
        super().__init__(app)
        self.stones = 21
        self.turn = "you"
        self.won = False

        self.lbl = None
        self.log = None
        self.btn1 = None
        self.btn2 = None
        self.btn3 = None

    def mount(self, parent):
        super().mount(parent)

        ttk.Label(parent, text=self.title, font=("Segoe UI", 11, "bold")).pack(
            padx=12, pady=(12, 6), anchor="nw"
        )
        ttk.Label(
            parent,
            text=(
                "Take 1, 2, or 3 stones each turn.\n"
                "Whoever takes the LAST stone loses.\n"
                "Hint: first-vs-second matters in Nim. Plan ahead.\n"
                "Solve via terminal: solve dilemma"
            ),
            wraplength=420,
            justify="left",
        ).pack(padx=12, pady=(0, 8), anchor="nw")

        self.lbl = ttk.Label(parent, text=self._status(), wraplength=420, justify="left")
        self.lbl.pack(padx=12, pady=(0, 8), anchor="nw")

        row = ttk.Frame(parent)
        row.pack(padx=12, pady=(0, 10), anchor="nw")
        self.btn1 = ttk.Button(row, text="Take 1", command=lambda: self._choose(1))
        self.btn2 = ttk.Button(row, text="Take 2", command=lambda: self._choose(2))
        self.btn3 = ttk.Button(row, text="Take 3", command=lambda: self._choose(3))
        self.btn1.pack(side="left")
        self.btn2.pack(side="left", padx=(8, 0))
        self.btn3.pack(side="left", padx=(8, 0))

        self.log = tk.Text(parent, height=10, bg="#0a0f1a", fg="#00ff88", insertbackground="#00ff88", wrap="word")
        self.log.pack(padx=12, pady=(0, 10), fill="both", expand=True, anchor="nw")
        self.log.insert("end", "Nim started with 21 stones.\n")
        self.log.config(state="disabled")

    def _status(self):
        return f"Stones left: {self.stones} | Turn: {self.turn.upper()}"

    def _append(self, s):
        self.log.config(state="normal")
        self.log.insert("end", s + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def _set_buttons(self, disabled: bool):
        state = ["disabled"] if disabled else ["!disabled"]
        self.btn1.state(state)
        self.btn2.state(state)
        self.btn3.state(state)

    def _bot_move(self):
        # leave 1 modulo 4 whenever possible
        target = 1
        take = (self.stones - target) % 4
        if take == 0:
            take = 1
        take = min(max(take, 1), 3, self.stones)
        self.stones -= take
        self._append(f"Bot takes {take}. Stones left: {self.stones}")

        if self.stones == 0:
            # bot took last => bot loses, you win
            self.won = True
            self._append("Bot took the last stone and loses. You win.")
            self.turn = "done"
            self._set_buttons(True)
            self.lbl.config(text=self._status())
            if hasattr(self.app, "safe_autosave"):
                self.app.safe_autosave()
            return

        self.turn = "you"
        self.lbl.config(text=self._status())
        if hasattr(self.app, "safe_autosave"):
            self.app.safe_autosave()

    def _choose(self, take: int):
        if self.turn != "you" or self.stones <= 0:
            return
        if take < 1 or take > 3 or take > self.stones:
            return

        self.stones -= take
        self._append(f"You take {take}. Stones left: {self.stones}")

        if self.stones == 0:
            # you took last => you lose
            self.won = False
            self._append("You took the last stone and lose this run.")
            self.turn = "done"
            self._set_buttons(True)
            self.lbl.config(text=self._status())
            if hasattr(self.app, "safe_autosave"):
                self.app.safe_autosave()
            return

        self.turn = "bot"
        self.lbl.config(text=self._status())
        if hasattr(self.app, "safe_autosave"):
            self.app.safe_autosave()
        self.app.root.after(220, self._bot_move)

    def success(self):
        return self.turn == "done" and self.won
