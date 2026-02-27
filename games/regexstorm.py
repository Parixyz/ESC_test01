from __future__ import annotations

import random
from tkinter import ttk

from games.base import GameBase


class RegexStorm(GameBase):
    game_id = "regex"
    title = "Pattern Storm"

    def __init__(self, app):
        super().__init__(app)
        self.running = False
        self.after_id = None
        self.samples_lbl = None
        self.opts = []

    def mount(self, parent):
        super().mount(parent)

        ttk.Label(parent, text=self.title, font=("Segoe UI", 11, "bold")).pack(
            padx=12, pady=(12, 6), anchor="nw"
        )
        ttk.Label(
            parent,
            text=(
                "Watch 4 changing sample strings on the left.\n"
                "Pick the one regex that matches all shown variations.\n"
                "Solve: solve regex <1|2|3|4|5>  (4 rounds, +/- points each round)"
            ),
            wraplength=420,
            justify="left",
        ).pack(padx=12, pady=(0, 8), anchor="nw")

        self.samples_lbl = ttk.Label(parent, text="(generating samples...)", wraplength=420, justify="left")
        self.samples_lbl.pack(padx=12, pady=(0, 10), anchor="nw")

        box = ttk.Frame(parent)
        box.pack(padx=12, pady=(0, 12), fill="x")

        self.opts = []
        for i in range(5):
            lbl = ttk.Label(box, text=f"{i+1}) ...", wraplength=420, justify="left")
            lbl.pack(anchor="nw", pady=2)
            self.opts.append(lbl)

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

    def _new_samples(self):
        prefix = random.choice(["TIME", "NODE", "JACK", "ECHO", "TRACE"])
        suffix = random.choice(["A", "B", "C"])
        return [f"{prefix}-{random.randint(10, 9999)}{suffix}" for _ in range(4)]

    def _tick(self):
        if not self.running:
            return

        samples = self._new_samples()
        correct = r"^(TIME|NODE|JACK|ECHO|TRACE)-\d{2,4}[ABC]$"
        choices = [
            correct,
            r"^(TIME|NODE|JACK|ECHO|TRACE)\d{2,4}[ABC]$",
            r"^[A-Z]+-\d{5}[ABC]$",
            r"^[A-Z]+-\d{2,4}$",
            r"^\d{2,4}-[A-Z]+[ABC]$",
        ]
        random.shuffle(choices)

        if self.samples_lbl:
            block = "\n".join([f"• {s}" for s in samples])
            self.samples_lbl.config(text=f"Samples:\n{block}")

        for i, lbl in enumerate(self.opts):
            try:
                lbl.config(text=f"{i+1}) {choices[i]}")
            except Exception:
                pass

        try:
            self.app.state.setdefault("answers", {})
            self.app.state["answers"]["N4_regex_samples"] = samples
            self.app.state["answers"]["N4_regex_correct"] = correct
            self.app.state["answers"]["N4_regex_map"] = {str(i + 1): choices[i] for i in range(5)}
        except Exception:
            pass

        try:
            self.after_id = self.app.root.after(5500, self._tick)
        except Exception:
            self.running = False
