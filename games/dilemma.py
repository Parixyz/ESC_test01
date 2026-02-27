from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from games.base import GameBase


class IteratedDilemma(GameBase):
    game_id = "dilemma"
    title = "Nim Lab"

    def __init__(self, app):
        super().__init__(app)
        self.wins_needed = 3
        self.wins = 0
        self.run_no = 1

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
                "Nim gauntlet: win 3 runs to clear this node.\n"
                "Take 1, 2, or 3 stones each turn.\n"
                "Whoever takes the LAST stone loses.\n"
                "Solve via terminal when ready: solve dilemma"
            ),
            wraplength=430,
            justify="left",
        ).pack(padx=12, pady=(0, 8), anchor="nw")

        self.lbl = ttk.Label(parent, text=self._status(), wraplength=430, justify="left")
        self.lbl.pack(padx=12, pady=(0, 8), anchor="nw")

        row = ttk.Frame(parent)
        row.pack(padx=12, pady=(0, 10), anchor="nw")
        self.btn1 = ttk.Button(row, text="Take 1", command=lambda: self._choose(1))
        self.btn2 = ttk.Button(row, text="Take 2", command=lambda: self._choose(2))
        self.btn3 = ttk.Button(row, text="Take 3", command=lambda: self._choose(3))
        self.btn1.pack(side="left")
        self.btn2.pack(side="left", padx=(8, 0))
        self.btn3.pack(side="left", padx=(8, 0))
        ttk.Button(row, text="Next Run", command=self._next_run).pack(side="left", padx=(10, 0))

        self.log = tk.Text(parent, height=10, bg="#0a0f1a", fg="#00ff88", insertbackground="#00ff88", wrap="word")
        self.log.pack(padx=12, pady=(0, 10), fill="both", expand=True, anchor="nw")
        self.log.insert("end", "Nim gauntlet started: Run 1 with 21 stones.\n")
        self.log.config(state="disabled")

    def _status(self):
        return (
            f"Run {self.run_no} | Wins {self.wins}/{self.wins_needed} | "
            f"Stones left: {self.stones} | Turn: {self.turn.upper()}"
        )

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

    def _persist(self):
        if hasattr(self.app, "safe_autosave"):
            self.app.safe_autosave()

    def _next_run(self):
        if self.wins >= self.wins_needed:
            self._append("Gauntlet already complete. Use solve dilemma.")
            return
        if self.turn != "done":
            self._append("Finish current run first.")
            return
        self.run_no += 1
        self.stones = 21
        self.turn = "you"
        self.won = False
        self._set_buttons(False)
        self.lbl.config(text=self._status())
        self._append(f"Run {self.run_no} begins with 21 stones.")
        self._persist()

    def _bot_move(self):
        target = 1
        take = (self.stones - target) % 4
        if take == 0:
            take = 1
        take = min(max(take, 1), 3, self.stones)
        self.stones -= take
        self._append(f"Bot takes {take}. Stones left: {self.stones}")

        if self.stones == 0:
            self.won = True
            self.wins += 1
            self._append(f"Bot took the last stone and loses. You win run {self.run_no}.")
            self.turn = "done"
            self._set_buttons(True)
            if self.wins >= self.wins_needed:
                self._append("Nim gauntlet complete: 3 wins achieved.")
            else:
                self._append("Use Next Run for another trial.")
            self.lbl.config(text=self._status())
            self._persist()
            return

        self.turn = "you"
        self.lbl.config(text=self._status())
        self._persist()

    def _choose(self, take: int):
        if self.turn != "you" or self.stones <= 0:
            return
        if take < 1 or take > 3 or take > self.stones:
            return

        self.stones -= take
        self._append(f"You take {take}. Stones left: {self.stones}")

        if self.stones == 0:
            self.won = False
            self._append(f"You took the last stone and lose run {self.run_no}.")
            self.turn = "done"
            self._set_buttons(True)
            self._append("Use Next Run to try again.")
            self.lbl.config(text=self._status())
            self._persist()
            return

        self.turn = "bot"
        self.lbl.config(text=self._status())
        self._persist()
        self.app.root.after(220, self._bot_move)

    def success(self):
        return self.wins >= self.wins_needed
