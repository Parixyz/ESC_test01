from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from games.base import GameBase


UNICODE_PIECES = {
    "K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙",
    "k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟",
}


class ChessFork(GameBase):
    game_id = "chess"
    title = "Forked Timeline"

    def __init__(self, app):
        super().__init__(app)
        self.canvas = None
        self.position = {
            "f5": "N",
            "g8": "k",
            "e8": "q",
            "c8": "r",
            "a1": "K",
            "h8": "r",
        }

    def mount(self, parent):
        super().mount(parent)

        ttk.Label(parent, text=self.title, font=("Segoe UI", 11, "bold")).pack(
            padx=12, pady=(12, 6), anchor="nw"
        )
        ttk.Label(
            parent,
            text="Placeholder board.\nSolve via terminal: solve chess <MOVE>  (e.g., Ne7)",
            wraplength=420,
            justify="left",
        ).pack(padx=12, pady=(0, 10), anchor="nw")

        self.canvas = tk.Canvas(parent, width=440, height=440, bg="#0a0f1a", highlightthickness=1)
        self.canvas.pack(padx=12, pady=(0, 10), anchor="nw")
        self._draw_board()

    def _draw_board(self):
        if not self.canvas:
            return
        self.canvas.delete("all")
        tile = 52
        ox, oy = 12, 12
        light = "#1a2438"
        dark = "#0f182b"

        for r in range(8):
            for c in range(8):
                x1 = ox + c * tile
                y1 = oy + r * tile
                x2 = x1 + tile
                y2 = y1 + tile
                color = light if (r + c) % 2 == 0 else dark
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#0a0f1a")

        for i, file_ in enumerate("abcdefgh"):
            self.canvas.create_text(ox + i * tile + tile/2, oy + 8 * tile + 10,
                                    text=file_, fill="#00ff88", font=("Segoe UI", 9))
        for i, rank in enumerate("87654321"):
            self.canvas.create_text(ox - 10, oy + i * tile + tile/2,
                                    text=rank, fill="#00ff88", font=("Segoe UI", 9))

        for sq, p in self.position.items():
            c = ord(sq[0]) - ord("a")
            rank = int(sq[1])
            r = 8 - rank
            x = ox + c * tile + tile/2
            y = oy + r * tile + tile/2
            glyph = UNICODE_PIECES.get(p, p)
            self.canvas.create_text(x, y, text=glyph, fill="#cfe", font=("Segoe UI Symbol", 24, "bold"))

        self.canvas.create_text(230, 430, text="White to move", fill="#00ff88", font=("Segoe UI", 10, "bold"))
