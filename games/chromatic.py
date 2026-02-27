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
        self.cool_palette = [
            "#89ddff",
            "#4fc3f7",
            "#64ffda",
            "#7aa2ff",
            "#5eead4",
            "#8b9dff",
            "#7dd3fc",
            "#93c5fd",
            "#c4b5fd",
            "#67e8f9",
        ]
        self.warm_palette = ["#ff3b30", "#ff8c00", "#ffd60a"]
        self.tick = 0

    def mount(self, parent):
        super().mount(parent)

        ttk.Label(parent, text=self.title, font=("Segoe UI", 11, "bold")).pack(
            padx=12, pady=(12, 6), anchor="nw"
        )
        ttk.Label(
            parent,
            text=(
                "Riddle: count every valid color combination.\n"
                "Rectangles can be red/orange/yellow (repeats allowed).\n"
                "Triangles use cold colors and can never match each other.\n"
                "Node minutes hint how many triangle colors exist.\n"
                "Solve via terminal: solve colors <COMBINATIONS>"
            ),
            wraplength=420,
            justify="left",
        ).pack(padx=12, pady=(0, 10), anchor="nw")

        self.canvas = tk.Canvas(parent, width=440, height=310, bg="#07131f", highlightthickness=0)
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
        self.canvas.create_rectangle(0, 0, 440, 310, fill="#07131f", outline="")
        self.canvas.create_oval(-80, -110, 220, 180, fill="#0b2740", outline="")
        self.canvas.create_oval(250, -100, 540, 190, fill="#11243d", outline="")

        r1 = random.choice(self.warm_palette)
        r2 = random.choice(self.warm_palette)
        t1 = random.choice(self.cool_palette)
        t2_choices = [c for c in self.cool_palette if c != t1]
        t2 = random.choice(t2_choices)

        self.canvas.create_rectangle(30, 40, 160, 120, fill=r1, outline="")
        self.canvas.create_rectangle(180, 40, 310, 120, fill=r2, outline="")
        self.canvas.create_polygon(90, 160, 140, 250, 40, 250, fill=t1, outline="")
        self.canvas.create_polygon(240, 160, 290, 250, 190, 250, fill=t2, outline="")
        self.canvas.create_text(
            220,
            285,
            text="How many combinations can exist?",
            fill="#d7f7ff",
            font=("Segoe UI", 10, "bold"),
        )

    def _tick(self):
        if not self.running or not self.canvas:
            return
        try:
            if not int(self.canvas.winfo_exists()):
                self.running = False
                self.canvas = None
                return
        except Exception:
            self.running = False
            self.canvas = None
            return

        self.tick += 1

        if self.tick % 2 == 0:
            try:
                items = self.canvas.find_all()
            except Exception:
                self.running = False
                self.canvas = None
                return
            try:
                rects = [i for i in items if self.canvas.type(i) == "rectangle"]
                tris = [i for i in items if self.canvas.type(i) == "polygon"]

                for item in rects[-2:]:
                    # rectangles: warm colors and duplicates allowed
                    self.canvas.itemconfig(item, fill=random.choice(self.warm_palette))

                # triangles: cold colors and no duplicates
                if len(tris) >= 2:
                    c1 = random.choice(self.cool_palette)
                    c2 = random.choice([c for c in self.cool_palette if c != c1])
                    self.canvas.itemconfig(tris[0], fill=c1)
                    self.canvas.itemconfig(tris[1], fill=c2)
            except Exception:
                pass

        try:
            self.after_id = self.app.root.after(900, self._tick)
        except Exception:
            self.running = False
