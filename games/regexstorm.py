# stub
# games/regexstorm.py
from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk

from games.base import GameBase


class RegexStorm(GameBase):
    game_id = "regex"
    title = "Pattern Storm"

    def __init__(self, app):
        super().__init__(app)
        self.running = False
        self.after_id = None
        self.lbl = None
        self.opts = []

    def mount(self, parent):
        super().mount(parent)

        ttk.Label(parent, text=self.title, font=("Segoe UI", 11, "bold")).pack(
            padx=12, pady=(12, 6), anchor="nw"
        )
        ttk.Label(
            parent,
            text="Text changes every ~3 seconds.\nSolve: solve regex <1|2|3|4>",
            wraplength=420,
            justify="left",
        ).pack(padx=12, pady=(0, 8), anchor="nw")

        self.lbl = ttk.Label(parent, text="(generating...)", wraplength=420, justify="left")
        self.lbl.pack(padx=12, pady=(0, 10), anchor="nw")

        box = ttk.Frame(parent)
        box.pack(padx=12, pady=(0, 12), fill="x")

        self.opts = []
        for i in range(4):
            l = ttk.Label(box, text=f"{i+1}) ...", wraplength=420, justify="left")
            l.pack(anchor="nw", pady=2)
            self.opts.append(l)

        self.running = True
        self._tick()

    def stop(self):
        self.running = False
        if self.after_id and getattr(self.app, "root", None):
            try:
                self.app.root.after_cancel(self.after_id)
            except Exception:
                pass
        self.after_id = None

    def _tick(self):
        if not self.running:
            return

        prefix = random.choice(["TIME", "NODE", "JACK", "ECHO"])
        digits = random.randint(10, 9999)
        suffix = random.choice(["A", "B", "C"])
        text = f"{prefix}-{digits}{suffix}"

        patterns = [
            r"^(TIME|NODE|JACK|ECHO)-\d+[ABC]$",
            r"^[A-Z]{4}-\d{2,4}[ABC]$",
            r"^(TIME|NODE)-\d+[A-C]$",
            r"^[A-Z]+-\d+[A-Z]$",
        ]
        distractors = [
            r"^(TIME|NODE|JACK|ECHO)\d+[ABC]$",
            r"^[A-Z]{4}-\d{5}[ABC]$",
            r"^(TIME|NODE|JACK|ECHO)-[A-Z]+[ABC]$",
            r"^\d+-[A-Z]{4}[ABC]$",
            r"^[A-Z]{4}-\d{2,4}$",
            r"^(TIME|NODE|JACK|ECHO)-\d+$",
        ]

        correct = random.choice(patterns)
        choices = [correct]
        random.shuffle(distractors)
        for d in distractors:
            if d not in choices:
                choices.append(d)
            if len(choices) == 4:
                break
        random.shuffle(choices)

        if self.lbl:
            self.lbl.config(text=f"TEXT:  {text}")
        for i, l in enumerate(self.opts):
            try:
                l.config(text=f"{i+1}) {choices[i]}")
            except Exception:
                pass

        # optionally store for solve-checking (if your app uses these keys)
        try:
            self.app.state.setdefault("answers", {})
            self.app.state["answers"]["N4_regex_text"] = text
            self.app.state["answers"]["N4_regex_correct"] = correct
            self.app.state["answers"]["N4_regex_map"] = {str(i+1): choices[i] for i in range(4)}
        except Exception:
            pass

        try:
            self.after_id = self.app.root.after(3000, self._tick)
        except Exception:
            self.running = False