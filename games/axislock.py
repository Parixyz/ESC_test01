# stub
# games/axislock.py
from __future__ import annotations

from tkinter import ttk

from games.base import GameBase


class AxisLock(GameBase):
    game_id = "final"
    title = "Axis Lock"

    def mount(self, parent):
        super().mount(parent)

        ttk.Label(parent, text=self.title, font=("Segoe UI", 11, "bold")).pack(
            padx=12, pady=(12, 6), anchor="nw"
        )
        ttk.Label(
            parent,
            text="Final node placeholder UI.\nUnlock via terminal: unlock <PASSWORD>",
            wraplength=420,
            justify="left",
        ).pack(padx=12, pady=(0, 12), anchor="nw")