# games/axislock.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from games.base import GameBase


class AxisLock(GameBase):
    game_id = "final"
    title = "Sequence Vault + CS Sudoku"

    def mount(self, parent):
        super().mount(parent)

        ttk.Label(parent, text=self.title, font=("Segoe UI", 11, "bold")).pack(
            padx=12, pady=(12, 6), anchor="nw"
        )
        ttk.Label(
            parent,
            text=(
                "1970 Sequence Vault (fun mode)\n"
                "Solve these for fun; unlocking still works either way.\n\n"
                "Riddle 1 (binary growth): 1, 2, 4, 8, 16, ?\n"
                "Riddle 2 (Fibonacci signal): 1, 1, 2, 3, 5, 8, ?\n"
                "Riddle 3 (hex ladder): 10, 16, 26, 42, ?\n"
                "Riddle 4 (cache stride): 3, 7, 15, 31, ?\n\n"
                "Bonus: Computer-science Sudoku board below\n"
                "(filled cells are milestone years in CS history).\n"
                "Type: unlock <anything> to continue to the goal node."
            ),
            wraplength=440,
            justify="left",
        ).pack(padx=12, pady=(0, 10), anchor="nw")

        canvas = tk.Canvas(parent, width=440, height=240, bg="#0a101c", highlightthickness=0)
        canvas.pack(padx=12, pady=(0, 12), anchor="nw")

        board = [
            [7, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 9, 0, 4, 0, 0, 8, 0, 0],
            [0, 0, 5, 0, 0, 0, 0, 6, 0],
            [0, 4, 0, 0, 7, 0, 0, 0, 9],
            [1, 0, 0, 9, 0, 6, 0, 0, 8],
            [6, 0, 0, 0, 2, 0, 0, 4, 0],
            [0, 6, 0, 0, 0, 0, 5, 0, 0],
            [0, 0, 2, 0, 0, 8, 0, 9, 0],
            [0, 0, 0, 0, 6, 0, 0, 0, 1],
        ]
        milestone = {
            1: "1941 Z3", 2: "1947 Transistor", 3: "1958 IC", 4: "1969 ARPANET",
            5: "1970 UNIX", 6: "1971 µP", 7: "1989 WWW", 8: "1991 Linux", 9: "2006 Cloud"
        }

        cell = 22
        ox, oy = 12, 12
        for r in range(9):
            for c in range(9):
                x1, y1 = ox + c * cell, oy + r * cell
                x2, y2 = x1 + cell, y1 + cell
                canvas.create_rectangle(x1, y1, x2, y2, fill="#101a2f", outline="#1f2b46")
                val = board[r][c]
                txt = str(val) if val else "."
                color = "#c9f0ff" if val else "#425c82"
                canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=txt, fill=color, font=("Consolas", 9, "bold"))

        for i in range(10):
            w = 3 if i % 3 == 0 else 1
            canvas.create_line(ox, oy + i * cell, ox + 9 * cell, oy + i * cell, fill="#4f78a3", width=w)
            canvas.create_line(ox + i * cell, oy, ox + i * cell, oy + 9 * cell, fill="#4f78a3", width=w)

        legend = "\n".join([f"{k}: {v}" for k, v in milestone.items()])
        canvas.create_text(
            235,
            14,
            text="CS Milestone Key\n" + legend,
            fill="#9de2ff",
            anchor="nw",
            justify="left",
            font=("Segoe UI", 8, "bold"),
        )
