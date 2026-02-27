# games/axislock.py
from __future__ import annotations

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
                "Type: unlock <anything>  (you win anyway)."
            ),
            wraplength=420,
            justify="left",
        ).pack(padx=12, pady=(0, 12), anchor="nw")
