# games/chromatic.py
from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk

from games.base import GameBase


class ChromaticDrift(GameBase):
    game_id = "colors"
    title = "Chromatic Drift"
    allowed_nodes = ["N1"]  # restrict to node N1 (optional but recommended)

    def __init__(self, app):
        super().__init__(app)
        self.canvas = None
        self.running = False
        self.after_id = None
        self.palette = ["#ffd000", "#33dd66", "#33aaff", "#9b5cff", "#ff66cc", "#00ffd5"]
        self.tick = 0

    def mount(self, parent):
        super().mount(parent)

        ttk.Label(parent, text=self.title, font=("Segoe UI", 11, "bold")).pack(
            padx=12, pady=(12, 6), anchor="nw"
        )
        ttk.Label(
            parent,
            text="Right-panel placeholder UI.\nSolve via terminal: solve colors <MINUTES>",
            wraplength=420,
            justify="left",
        ).pack(padx=12, pady=(0, 10), anchor="nw")

        self.canvas = tk.Canvas(parent, width=440, height=310, bg="#0a0f1a", highlightthickness=1)
        self.canvas.pack(padx=12, pady=(0, 10), anchor="nw")

        row = ttk.Frame(parent)
        row.pack(padx=12, pady=(0, 12), anchor="nw")
        ttk.Button(row, text="Start", command=self.start_anim).pack(side="left")
        ttk.Button(row, text="Stop", command=self.stop_anim).pack(side="left", padx=(8, 0))

        self._draw_scene()

    def start(self):
        super().start()
        self.start_anim()

    def stop(self):
        self.stop_anim()

    def start_anim(self):
        if self.running:
            return
        self.running = True
        self._tick()

    def stop_anim(self):
        self.running = False
        if self.after_id and getattr(self.app, "root", None):
            try:
                self.app.root.after_cancel(self.after_id)
            except Exception:
                pass
        self.after_id = None

    def _draw_scene(self):
        if not self.canvas:
            return
        self.canvas.delete("all")
        self.canvas.create_rectangle(30, 40, 160, 120, fill="#ff3355", outline="")
        self.canvas.create_rectangle(180, 40, 310, 120, fill="#ff7a00", outline="")
        self.canvas.create_polygon(90, 160, 140, 250, 40, 250, fill=random.choice(self.palette), outline="")
        self.canvas.create_polygon(240, 160, 290, 250, 190, 250, fill=random.choice(self.palette), outline="")
        self.canvas.create_text(220, 285, text="(Animation placeholder)", fill="#00ff88", font=("Segoe UI", 9, "bold"))

    def _tick(self):
        if not self.running or not self.canvas:
            return
        self.tick += 1

        if self.tick % 2 == 0:
            for item in self.canvas.find_all():
                try:
                    if self.canvas.type(item) == "polygon":
                        self.canvas.itemconfig(item, fill=random.choice(self.palette))
                except Exception:
                    pass

        try:
            self.after_id = self.app.root.after(200, self._tick)
        except Exception:
            self.running = False