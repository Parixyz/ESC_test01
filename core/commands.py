# core/commands.py
# Fully working CommandRouter (no stubs inside this file).
# Note: this router assumes your app implements methods like:
#   cmd_status, cmd_time, cmd_nodes, cmd_routes, cmd_travel, cmd_games, cmd_play,
#   cmd_story, cmd_hint, cmd_showcode, cmd_solve, cmd_train, cmd_ttt, cmd_unlock, cmd_godskip
# and has: app.print_line(str), app.ui.terminal.clear(), app.state (dict), app.enter_node(node_id), etc.

from __future__ import annotations

import shlex
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional


@dataclass(frozen=True)
class CommandSpec:
    name: str
    usage: str
    short: str
    long: str
    fn: Callable  # fn(app, args) -> None


class CommandRouter:
    def __init__(self, app):
        self.app = app

        # simple aliases (single-token)
        self.aliases: Dict[str, str] = {
            "?": "help",
            "cls": "clear",
            "q": "quit",     # optional: closes the app window
            "exit": "quit",
        }

        self.history: List[str] = []
        self.cmds: Dict[str, CommandSpec] = {}

        self._register_builtin()
        self._register_app_hooks()

    # ---------------- registration ----------------

    def _register(self, spec: CommandSpec) -> None:
        self.cmds[spec.name] = spec

    def _register_builtin(self) -> None:
        self._register(CommandSpec(
            name="help",
            usage="help [command]",
            short="List commands or show help for one command.",
            long="Examples:\n  help\n  help travel\n  help solve",
            fn=self._help
        ))
        self._register(CommandSpec(
            name="man",
            usage="man <command>",
            short="Man-page style help for a command.",
            long="Example:\n  man solve",
            fn=self._man
        ))
        self._register(CommandSpec(
            name="clear",
            usage="clear",
            short="Clear terminal output.",
            long="Clears the left terminal text area.",
            fn=self._clear
        ))
        self._register(CommandSpec(
            name="history",
            usage="history [n]",
            short="Show recent command history.",
            long="Examples:\n  history\n  history 20",
            fn=self._history
        ))
        self._register(CommandSpec(
            name="alias",
            usage="alias            | alias name=value | alias -d name",
            short="List/set/delete aliases.",
            long="Examples:\n  alias\n  alias n=nodes\n  alias -d n",
            fn=self._alias
        ))
        self._register(CommandSpec(
            name="sleep",
            usage="sleep <seconds>",
            short="Pause briefly (dramatic effect).",
            long="Caps at 5 seconds.",
            fn=self._sleep
        ))
        self._register(CommandSpec(
            name="echo",
            usage="echo <text...>",
            short="Print text.",
            long="Example:\n  echo hello world",
            fn=self._echo
        ))
        self._register(CommandSpec(
            name="whoami",
            usage="whoami",
            short="Show player name.",
            long="Reads player_name from encrypted save state.",
            fn=self._whoami
        ))
        self._register(CommandSpec(
            name="vars",
            usage="vars",
            short="List terminal variables (state['vars']).",
            long="Use `set` and `get` to manage variables.",
            fn=self._vars
        ))
        self._register(CommandSpec(
            name="set",
            usage="set <key> <value...>",
            short="Set a terminal variable.",
            long="Example:\n  set key AURORA",
            fn=self._set
        ))
        self._register(CommandSpec(
            name="get",
            usage="get <key>",
            short="Get a terminal variable.",
            long="Example:\n  get key",
            fn=self._get
        ))
        self._register(CommandSpec(
            name="del",
            usage="del <key>",
            short="Delete a terminal variable.",
            long="Example:\n  del key",
            fn=self._del
        ))
        self._register(CommandSpec(
            name="quit",
            usage="quit",
            short="Exit the game.",
            long="Closes the window. Your save should persist via app close handler.",
            fn=self._quit
        ))

    def _register_app_hooks(self) -> None:
        """
        These hook into your existing app methods.
        Router is "complete" in the sense it routes cleanly;
        gameplay logic lives in app.cmd_* handlers.
        """
        hooks = [
            ("status",   "status",                 "Show status line.",                         lambda a, x: a.cmd_status()),
            ("score",    "score",                  "Show score.",                               lambda a, x: a.print_line(f"Score: {a.state.get('score', 0)}")),
            ("time",     "time",                   "Show current node time.",                   lambda a, x: a.cmd_time()),
            ("nodes",    "nodes",                  "List nodes and unlocked nodes.",            lambda a, x: a.cmd_nodes()),
            ("routes",   "routes",                 "Show routes from current node.",            lambda a, x: a.cmd_routes()),
            ("travel",   "travel <N#>",            "Travel to an unlocked connected node.",      lambda a, x: a.cmd_travel(x)),
            ("games",    "games",                  "List games in current node.",               lambda a, x: a.cmd_games()),
            ("play",     "play <game_id>",         "Mount a game (if allowed in node).",        lambda a, x: a.cmd_play(x)),
            ("story",    "story | story all",      "Advance dialogue.",                         lambda a, x: a.cmd_story(x)),
            ("hint",     "hint | hint h1",         "Use a hint (cooldown + score cost).",       lambda a, x: a.cmd_hint(x)),
            ("showcode", "showcode <A|B|C|D>",     "Show a code snippet (N3).",                 lambda a, x: a.cmd_showcode(x)),
            ("solve",    "solve ...",              "Solve puzzles.",                            lambda a, x: a.cmd_solve(x)),
            ("train",    "train dilemma",          "Training module.",                          lambda a, x: a.cmd_train(x)),
            ("ttt",      "ttt status|reset",       "TicTacToe utilities (N5).",                 lambda a, x: a.cmd_ttt(x)),
            ("unlock",   "unlock <password>",      "Final unlock (N6).",                        lambda a, x: a.cmd_unlock(x)),
            ("godskip",  "godskip <CODE>",         "Dev skip.",                                 lambda a, x: a.cmd_godskip(x)),
            ("selftest", "selftest <PASSWORD>", "Run internal smoke tests (password required).",
             lambda a, x: a.cmd_selftest(x)),
        ]

        for name, usage, short, fn in hooks:
            self._register(CommandSpec(
                name=name,
                usage=usage,
                short=short,
                long=short,
                fn=lambda app, args, _fn=fn: _fn(app, args)  # capture fn safely
            ))

    # ---------------- public API ----------------

    def run(self, raw: str) -> None:
        raw = (raw or "").strip()
        if not raw:
            return

        self.history.append(raw)

        # parse like a shell (supports quotes)
        try:
            parts = shlex.split(raw)
        except Exception:
            self.app.print_line("[ERR] Could not parse command (bad quotes?).")
            return

        cmd = parts[0]
        args = parts[1:]

        # alias expansion (single-token alias)
        if cmd in self.aliases:
            expanded = self.aliases[cmd]
            new_raw = (expanded + " " + " ".join(args)).strip()
            return self.run(new_raw)

        # let active game consume command first (optional)
        try:
            if getattr(self.app, "current_game", None) and self.app.current_game.on_command(cmd, args):
                return
        except Exception:
            # never let a game crash the terminal
            pass

        spec = self.cmds.get(cmd)
        if not spec:
            self.app.print_line("Unknown command. Type `help`.")
            return

        try:
            spec.fn(self.app, args)
        except Exception as e:
            self.app.print_line(f"[ERR] command failed: {e}")

    # ---------------- builtins ----------------

    def _help(self, app, args) -> None:
        if args:
            name = args[0]
            spec = self.cmds.get(name)
            if not spec:
                app.print_line("[ERR] Unknown command.")
                return
            app.print_line(f"{spec.name} — {spec.short}")
            app.print_line(f"Usage: {spec.usage}")
            return

        app.print_line("Commands:")
        for k in sorted(self.cmds.keys()):
            app.print_line(f"  {k:<10} - {self.cmds[k].short}")
        app.print_line("Tip: `man <cmd>` for details. Use quotes like a shell.")

    def _man(self, app, args) -> None:
        if not args:
            app.print_line("Usage: man <command>")
            return
        name = args[0]
        spec = self.cmds.get(name)
        if not spec:
            app.print_line("[ERR] Unknown command.")
            return
        app.print_line(f"=== MAN {spec.name} ===")
        app.print_line(f"USAGE: {spec.usage}")
        app.print_line(f"INFO:  {spec.long}")

    def _clear(self, app, args) -> None:
        app.ui.terminal.clear()

    def _history(self, app, args) -> None:
        n = 50
        if args:
            try:
                n = max(1, min(200, int(args[0])))
            except Exception:
                app.print_line("[ERR] history n must be a number.")
                return

        start_idx = max(0, len(self.history) - n)
        for i, h in enumerate(self.history[start_idx:], start=start_idx + 1):
            app.print_line(f"{i:>3}: {h}")

    def _alias(self, app, args) -> None:
        if not args:
            app.print_line("Aliases:")
            for k in sorted(self.aliases.keys()):
                app.print_line(f"  {k} = {self.aliases[k]}")
            return

        # delete
        if args[0] == "-d":
            if len(args) < 2:
                app.print_line("Usage: alias -d name")
                return
            k = args[1].strip()
            if k in self.aliases:
                del self.aliases[k]
                app.print_line(f"[OK] alias deleted: {k}")
            else:
                app.print_line("[ERR] alias not found.")
            return

        # set
        s = args[0]
        if "=" not in s:
            app.print_line("Usage: alias name=value  (or: alias -d name)")
            return
        k, v = s.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k or not v:
            app.print_line("[ERR] Bad alias.")
            return
        self.aliases[k] = v
        app.print_line(f"[OK] alias {k}={v}")

    def _sleep(self, app, args) -> None:
        if not args:
            app.print_line("Usage: sleep <seconds>")
            return
        try:
            sec = float(args[0])
        except Exception:
            app.print_line("[ERR] seconds must be a number.")
            return
        sec = max(0.0, min(sec, 5.0))
        app.print_line(f"[...] sleeping {sec}s")
        time.sleep(sec)
        app.print_line("[OK] awake")

    def _echo(self, app, args) -> None:
        app.print_line(" ".join(args))

    def _whoami(self, app, args) -> None:
        name = (app.state or {}).get("player_name") or "?"
        app.print_line(f"{name}")

    def _vars(self, app, args) -> None:
        vars_ = (app.state or {}).get("vars") or {}
        if not vars_:
            app.print_line("(no vars set)")
            return
        for k in sorted(vars_.keys()):
            app.print_line(f"{k} = {vars_[k]}")

    def _set(self, app, args) -> None:
        if len(args) < 2:
            app.print_line("Usage: set <key> <value...>")
            return
        k = args[0]
        v = " ".join(args[1:])
        app.state.setdefault("vars", {})[k] = v
        app.print_line(f"[OK] {k} set")

    def _get(self, app, args) -> None:
        if len(args) < 1:
            app.print_line("Usage: get <key>")
            return
        k = args[0]
        v = (app.state or {}).get("vars", {}).get(k)
        if v is None:
            app.print_line("(null)")
        else:
            app.print_line(str(v))

    def _del(self, app, args) -> None:
        if len(args) < 1:
            app.print_line("Usage: del <key>")
            return
        k = args[0]
        vars_ = app.state.setdefault("vars", {})
        if k in vars_:
            del vars_[k]
            app.print_line(f"[OK] deleted {k}")
        else:
            app.print_line("[ERR] no such var")

    def _quit(self, app, args) -> None:
        # closes the window; your app WM_DELETE should save.
        try:
            app.print_line("[OK] quitting...")
        except Exception:
            pass
        try:
            app.root.destroy()
        except Exception:
            pass