from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk

from games.base import GameBase


class ChromaticDrift(GameBase):
    game_id = "colors"
    title = "Chromatic Drift"
    allowed_nodes = ["N1"]

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
                "Observe both rows as colors cycle, then infer each row's rule.\n"
                "The clock helps define one pool size.\n"
                "Use: games -> play colors -> solve colors <COMBINATIONS>"
            ),
            wraplength=420,
            justify="left",
        ).pack(padx=12, pady=(0, 10), anchor="nw")

        self.canvas = tk.Canvas(parent, width=440, height=310, bg="#05111b", highlightthickness=0)
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
        self.canvas.create_rectangle(0, 0, 440, 310, fill="#05111b", outline="")
        self.canvas.create_oval(-90, -120, 220, 185, fill="#10324e", outline="")
        self.canvas.create_oval(250, -105, 560, 200, fill="#1a3555", outline="")
        self.canvas.create_rectangle(0, 248, 440, 310, fill="#0a1c2b", outline="")

        rect_colors = [random.choice(self.warm_palette) for _ in range(3)]
        tri_colors = random.sample(self.cool_palette, 3)

        self.canvas.create_rectangle(25, 42, 125, 112, fill=rect_colors[0], outline="", tags=("shape_rect",))
        self.canvas.create_rectangle(155, 42, 255, 112, fill=rect_colors[1], outline="", tags=("shape_rect",))
        self.canvas.create_rectangle(285, 42, 385, 112, fill=rect_colors[2], outline="", tags=("shape_rect",))

        self.canvas.create_polygon(65, 158, 112, 238, 18, 238, fill=tri_colors[0], outline="", tags=("shape_tri",))
        self.canvas.create_polygon(195, 158, 242, 238, 148, 238, fill=tri_colors[1], outline="", tags=("shape_tri",))
        self.canvas.create_polygon(325, 158, 372, 238, 278, 238, fill=tri_colors[2], outline="", tags=("shape_tri",))
        self.canvas.create_text(
            220,
            285,
            text="Two rows, six shapes: how many valid combinations?",
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
                rects = list(self.canvas.find_withtag("shape_rect"))
                tris = list(self.canvas.find_withtag("shape_tri"))

                for item in rects:
                    self.canvas.itemconfig(item, fill=random.choice(self.warm_palette))

                if len(tris) >= 3:
                    c1, c2, c3 = random.sample(self.cool_palette, 3)
                    self.canvas.itemconfig(tris[0], fill=c1)
                    self.canvas.itemconfig(tris[1], fill=c2)
                    self.canvas.itemconfig(tris[2], fill=c3)
            except Exception:
                pass

        try:
            self.after_id = self.app.root.after(1200, self._tick)
        except Exception:
            self.running = False
