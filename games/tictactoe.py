# stub
# games/tictactoe.py
from __future__ import annotations

import random
from tkinter import ttk

from games.base import GameBase


class TicTacToeSequence(GameBase):
    game_id = "tictactoe"
    title = "Win/Lose Sequence"

    def __init__(self, app):
        super().__init__(app)
        self.buttons = []
        self.board = [""] * 9
        self.turn = "X"
        self.rounds = 4
        self.round_index = 0
        self.results = []
        self.status_lbl = None

    def mount(self, parent):
        super().mount(parent)

        ttk.Label(parent, text=self.title, font=("Segoe UI", 11, "bold")).pack(
            padx=12, pady=(12, 6), anchor="nw"
        )
        ttk.Label(
            parent,
            text="Placeholder TicTacToe.\nPlay here; solve via terminal: solve tictactoe",
            wraplength=420,
            justify="left",
        ).pack(padx=12, pady=(0, 8), anchor="nw")

        grid = ttk.Frame(parent)
        grid.pack(padx=12, pady=(0, 10), anchor="nw")

        self.buttons = []
        for i in range(9):
            b = ttk.Button(grid, text=" ", width=4, command=lambda idx=i: self._player_move(idx))
            b.grid(row=i // 3, column=i % 3, padx=4, pady=4)
            self.buttons.append(b)

        self.status_lbl = ttk.Label(parent, text=self._status_text(), wraplength=420, justify="left")
        self.status_lbl.pack(padx=12, pady=(0, 10), anchor="nw")

        ttk.Button(parent, text="Reset", command=self._reset_round).pack(padx=12, pady=(0, 12), anchor="nw")

    def _status_text(self):
        return f"Round {self.round_index+1}/{self.rounds} | Results: {''.join(self.results) or '(none)'}"

    def _update_status(self):
        if self.status_lbl:
            self.status_lbl.config(text=self._status_text())

    def _reset_round(self):
        self.board = [""] * 9
        self.turn = "X"
        for b in self.buttons:
            b.config(text=" ")
            b.state(["!disabled"])
        self._update_status()

    def _player_move(self, idx):
        if self.round_index >= self.rounds:
            return
        if self.turn != "X" or self.board[idx]:
            return
        self.board[idx] = "X"
        self.buttons[idx].config(text="X")

        w = self._winner()
        if w:
            self._end_round(w); return

        self.turn = "O"
        try:
            self.app.root.after(150, self._bot_move)
        except Exception:
            self._bot_move()

    def _bot_move(self):
        if self.round_index >= self.rounds or self.turn != "O":
            return
        moves = [i for i, v in enumerate(self.board) if not v]
        if not moves:
            self._end_round("D"); return
        m = random.choice(moves)
        self.board[m] = "O"
        self.buttons[m].config(text="O")
        w = self._winner()
        if w:
            self._end_round(w); return
        self.turn = "X"

    def _winner(self):
        b = self.board
        lines = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        for a, c, d in lines:
            if b[a] and b[a] == b[c] == b[d]:
                return b[a]
        if all(b):
            return "D"
        return None

    def _end_round(self, winner):
        out = "W" if winner == "X" else ("L" if winner == "O" else "D")
        self.results.append(out)
        self.round_index += 1

        for b in self.buttons:
            b.state(["disabled"])

        self.safe_print(f"[TTT] Round ended: {out}")
        self._update_status()

    def sequence_ok(self):
        # placeholder: accept any completed run for now
        return self.round_index >= self.rounds