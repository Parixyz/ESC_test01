# games/axislock.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from games.base import GameBase


class AxisLock(GameBase):
    game_id = "final"
    title = "Terminal Comedy Gauntlet"

    def mount(self, parent):
        super().mount(parent)

        ttk.Label(parent, text=self.title, font=("Segoe UI", 11, "bold")).pack(
            padx=12, pady=(12, 6), anchor="nw"
        )
        ttk.Label(
            parent,
            text=(
                "Final node: a stack of funny computer riddles.\n"
                "1) Why do devs hate nature? Too many bugs.\n"
                "2) Why did cache break up with RAM? Too clingy.\n"
                "3) Why was the keyboard sleepy? It had two shifts.\n"
                "4) Why did the loop stop? It needed a break.\n"
                "5) Why was the function calm? It had closure.\n"
                "6) Why did the bug visit therapy? Stack trauma.\n"
                "7) Why did the byte blush? It saw a naked pointer.\n"
                "8) Why did the server sing? It had uptime confidence.\n"
                "9) Why did recursion fail standup? Same punchline forever.\n"
                "10) Why was SQL dramatic? Too many joins.\n"
                "11) Why did the IDE meditate? To reduce exceptions.\n"
                "12) Why did the process nap? It was waiting on I/O.\n\n"
                "Bonus visual: Binary Sudoku board below.\n"
                "Type: unlock <anything>  (you win anyway)."
            ),
            wraplength=420,
            justify="left",
        ).pack(padx=12, pady=(0, 10), anchor="nw")

        canvas = tk.Canvas(parent, width=420, height=220, bg="#0b1220", highlightthickness=0)
        canvas.pack(padx=12, pady=(0, 12), anchor="nw")

        board = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]
        cell = 22
        ox, oy = 12, 12
        for r in range(9):
            for c in range(9):
                x1, y1 = ox + c * cell, oy + r * cell
                x2, y2 = x1 + cell, y1 + cell
                canvas.create_rectangle(x1, y1, x2, y2, fill="#101a2f", outline="#1f2b46")
                val = board[r][c]
                txt = str(val) if val else "."
                color = "#d0f0ff" if val else "#4e6a8f"
                canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=txt, fill=color, font=("Consolas", 9, "bold"))

        for i in range(10):
            w = 3 if i % 3 == 0 else 1
            canvas.create_line(ox, oy + i * cell, ox + 9 * cell, oy + i * cell, fill="#4f78a3", width=w)
            canvas.create_line(ox + i * cell, oy, ox + i * cell, oy + 9 * cell, fill="#4f78a3", width=w)

        canvas.create_text(260, 112,
                           text=("Computer Science Ending:\n"
                                 "From logic gates to algorithms,\n"
                                 "from memory to machines,\n"
                                 "you learned to reason under uncertainty."),
                           fill="#9de2ff", anchor="w", justify="left", font=("Segoe UI", 9, "bold"))
