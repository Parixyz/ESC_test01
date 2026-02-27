# games/base.py
from __future__ import annotations

from typing import Optional, List


class GameBase:
    """
    Base class for right-panel games.

    Convention:
      - game_id: unique id string, e.g. "colors"
      - title: display title
      - allowed_nodes: list of node ids where this game is allowed (None or [] => allowed everywhere)

    Methods:
      - mount(parent): build right-panel UI
      - start(): optional hook
      - stop(): optional hook
      - on_command(cmd, args): return True if the game consumed the command
    """

    game_id: str = "base"
    title: str = "Base Game"
    allowed_nodes: Optional[List[str]] = None

    def __init__(self, app):
        self.app = app

    def safe_print(self, msg: str):
        """Best-effort terminal print helper for game callbacks."""
        try:
            self.app.print_line(msg)
        except Exception:
            pass

    # ---- permissions ----
    def is_allowed_here(self) -> bool:
        """
        Enforce 'Some games are built-in but only playable in their node'.
        If allowed_nodes is None or empty => allowed in all nodes.
        """
        nodes = getattr(self, "allowed_nodes", None)
        if not nodes:
            return True
        cur = self.app.state.get("current_node")
        return cur in nodes

    # ---- lifecycle ----
    def mount(self, parent):
        # clear right-panel area (safe default)
        for w in parent.winfo_children():
            w.destroy()

    def start(self):
        self.app.print_line(f"[GAME] {self.title} started.")

    def stop(self):
        pass

    # ---- command interception (optional) ----
    def on_command(self, cmd: str, args: list[str]) -> bool:
        return False
