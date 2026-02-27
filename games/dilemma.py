# stub
# games/dilemma.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from games.base import GameBase


class IteratedDilemma(GameBase):
    game_id = "dilemma"
    title = "Iterated Dilemma"

    def __init__(self, app):
        super().__init__(app)
        self.rounds = 6
        self.r = 0
        self.your_score = 0
        self.opp_score = 0
        self.last_you = None

        self.lbl = None
        self.log = None
        self.btnC = None
        self.btnD = None

    def mount(self, parent):
        super().mount(parent)

        ttk.Label(parent, text=self.title, font=("Segoe UI", 11, "bold")).pack(
            padx=12, pady=(12, 6), anchor="nw"
        )
        ttk.Label(
            parent,
            text="Pick C or D each round.\nSolve via terminal: solve dilemma",
            wraplength=420,
            justify="left",
        ).pack(padx=12, pady=(0, 8), anchor="nw")

        self.lbl = ttk.Label(parent, text=self._status(), wraplength=420, justify="left")
        self.lbl.pack(padx=12, pady=(0, 8), anchor="nw")

        row = ttk.Frame(parent)
        row.pack(padx=12, pady=(0, 10), anchor="nw")
        self.btnC = ttk.Button(row, text="C", command=lambda: self._choose("C"))
        self.btnD = ttk.Button(row, text="D", command=lambda: self._choose("D"))
        self.btnC.pack(side="left")
        self.btnD.pack(side="left", padx=(8, 0))

        self.log = tk.Text(parent, height=10, bg="#0a0f1a", fg="#00ff88", insertbackground="#00ff88", wrap="word")
        self.log.pack(padx=12, pady=(0, 10), fill="both", expand=True, anchor="nw")
        self.log.insert("end", "Click C/D to begin.\n")
        self.log.config(state="disabled")

    def _status(self):
        return f"Round {self.r+1}/{self.rounds} | You {self.your_score} - Opp {self.opp_score}"

    def _append(self, s):
        self.log.config(state="normal")
        self.log.insert("end", s + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def _opp_move(self):
        # simple Tit-for-Tat placeholder
        if self.r == 0:
            return "C"
        return self.last_you or "C"

    def _choose(self, you):
        if self.r >= self.rounds:
            return

        opp = self._opp_move()
        if you == "C" and opp == "C":
            ys, os_ = 3, 3
        elif you == "D" and opp == "C":
            ys, os_ = 5, 0
        elif you == "C" and opp == "D":
            ys, os_ = 0, 5
        else:
            ys, os_ = 1, 1

        self.your_score += ys
        self.opp_score += os_
        self._append(f"R{self.r+1}: You={you}, Opp={opp} -> (+{ys}, +{os_})")
        self.last_you = you
        self.r += 1

        if self.r >= self.rounds:
            self._append("Done. Now type: solve dilemma")
            self.btnC.state(["disabled"])
            self.btnD.state(["disabled"])

        self.lbl.config(text=self._status())

    def success(self):
        return self.r >= self.rounds and self.your_score > self.opp_score