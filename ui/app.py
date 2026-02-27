# ui/app.py
import os
import time
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox

from core.config import ConfigLoader
from core.encryption import Encryption
from core.storage import SaveManager, SavePaths
from core.eventdb import EncryptedEventDB
from core.commands import CommandRouter

# TTS optional
try:
    import pyttsx3
except Exception:
    pyttsx3 = None


APP_BG = "#0a0f1a"
APP_FG = "#00ff88"

# Built-in encryption key (no password prompt).
APP_SAVE_KEY = "Test"


class UIRefs:
    def __init__(self, terminal, rightpanel):
        self.terminal = terminal
        self.rightpanel = rightpanel


class TimeTerminalApp:
    def __init__(self, root: tk.Tk, base_dir: str):
        self.root = root
        self.base_dir = base_dir
        # typing lock (prevents garbled typewriter output)
        self._typing_busy = False
        self._typing_after_id = None

        # config: Config.json
        self.cfg = ConfigLoader(base_dir).load()

        self.root.title(self.cfg.get("meta", {}).get("title", "Time Terminal"))
        self.root.geometry("1220x760")
        self.root.minsize(980, 600)

        self.hint_cooldown = int(self.cfg.get("meta", {}).get("hint_cooldown_seconds", 300))

        # encryption + persistence paths
        self.save_dir = os.path.join(os.path.expanduser("~"), ".time_terminal_game")
        self.save_path = os.path.join(self.save_dir, "save.dat")
        self.db_path = os.path.join(self.save_dir, "events.db")

        self.crypto = Encryption(rounds=150_000)
        self.saver = SaveManager(
            SavePaths(self.save_dir, self.save_path),
            encryption=self.crypto,
            password_getter=lambda: APP_SAVE_KEY
        )
        self.eventdb = EncryptedEventDB(
            self.db_path,
            encryption=self.crypto,
            password_getter=lambda: APP_SAVE_KEY,
            save_dir=self.save_dir
        )

        # state
        self._reset_state_fresh()

        # tts
        self.tts_enabled = True
        self.tts_engine = None
        if pyttsx3 is not None:
            try:
                self.tts_engine = pyttsx3.init()
            except Exception:
                self.tts_engine = None

        # games registry
        from games.chromatic import ChromaticDrift
        from games.chessfork import ChessFork
        from games.codeobs import CodeObservatory
        from games.regexstorm import RegexStorm
        from games.tictactoe import TicTacToeSequence
        from games.dilemma import IteratedDilemma
        from games.axislock import AxisLock

        self.game_registry = {
            "colors": ChromaticDrift,
            "chess": ChessFork,
            "codes": CodeObservatory,
            "regex": RegexStorm,
            "tictactoe": TicTacToeSequence,
            "dilemma": IteratedDilemma,
            "final": AxisLock,
        }
        self.current_game = None

        # build UI
        from ui.terminal import TerminalView
        from ui.rightpanel import RightPanel

        outer = ttk.Frame(self.root)
        outer.pack(fill="both", expand=True)

        left = ttk.Frame(outer)
        left.pack(side="left", fill="both", expand=True)

        self.rightpanel = RightPanel(outer)

        self.terminal = TerminalView(left, APP_BG, APP_FG)

        # Name text field at top (no popup)
        self.terminal.pack_namebar(left, self._on_set_name)

        self.terminal.pack(left)
        self.terminal.pack_input(left, self._on_enter)

        self.status = ttk.Label(self.root, text="Ready", anchor="w")
        self.status.pack(fill="x")

        self.ui = UIRefs(self.terminal, self.rightpanel)
        self.router = CommandRouter(self)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # boot
        self._boot()

    # ---------------- state ----------------
    def _reset_state_fresh(self):
        self.state = {
            "player_name": None,
            "score": 0,
            "current_node": "N1",
            "unlocked_nodes": ["N1"],
            "solved": {},
            "tokens": [],
            "story_index": {},
            "last_hint_ts": 0,
            "answers": {},
            "vars": {}
        }

    # ---------------- basic helpers ----------------
    def print_line(self, s: str):
        self.terminal.write_line(s)

    def node_cfg(self, node_id: str) -> dict:
        return self.cfg.get("nodes", {}).get(node_id, {})

    def node_time(self, node_id: str) -> str:
        return self.node_cfg(node_id).get("time", "??:??")

    # ---------------- typewriter + narration ----------------
    def _type_line(self, full_text: str, delay_ms: int = 14) -> int:
        """
        Typewriter animation into the terminal without interleaving.
        Returns estimated duration in ms for scheduling follow-ups.
        """
        # If currently typing, fall back to normal line to avoid garbling
        if self._typing_busy or not hasattr(self.terminal, "write_raw"):
            self.print_line(full_text)
            return 0

        self._typing_busy = True
        i = 0

        # duration estimate: chars * delay + newline + small cushion
        est_ms = max(0, len(full_text) * delay_ms + 80)

        def done():
            self.terminal.write_raw("\n")
            self._typing_busy = False

        def tick():
            nonlocal i
            if i >= len(full_text):
                done()
                return
            self.terminal.write_raw(full_text[i])
            i += 1
            self.root.after(delay_ms, tick)

        tick()
        return est_ms

    def narrate_line(self, speaker: str, text: str):
        line = f"{speaker}: {text}"

        # Animated if possible (serialized)
        if hasattr(self.terminal, "write_raw"):
            self._type_line(line, delay_ms=14)
        else:
            self.print_line(line)

        # TTS optional
        if not self.tts_enabled or self.tts_engine is None:
            return
        try:
            voices = self.tts_engine.getProperty("voices") or []
            if voices:
                if speaker == "JESSICA" and len(voices) >= 2:
                    self.tts_engine.setProperty("voice", voices[1].id)
                else:
                    self.tts_engine.setProperty("voice", voices[0].id)
            self.tts_engine.stop()
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception:
            pass

    def update_status(self):
        self.status.config(
            text=f"{self.state.get('player_name','?')} | Node {self.state['current_node']} ({self.node_time(self.state['current_node'])}) | Score {self.state['score']}"
        )

    # ---------------- persistence ----------------
    def _persist_with_repair(self) -> bool:
        try:
            self.saver.save(self.state)
            return True
        except Exception:
            pass

        # repair attempt
        try:
            os.makedirs(self.save_dir, exist_ok=True)
            try:
                if os.path.exists(self.save_path):
                    os.remove(self.save_path)
            except Exception:
                pass
            self.saver.save(self.state)
            return True
        except Exception:
            return False

    def _persist(self):
        self._persist_with_repair()

    def _on_close(self):
        try:
            if self.current_game is not None:
                self.current_game.stop()
        except Exception:
            pass
        try:
            self._persist()
        except Exception:
            pass
        self.root.destroy()

    # ---------------- boot flow ----------------
    def _boot(self):
        self.print_line("Welcome to Jack’s Time Terminal.")
        self.print_line("The narrator speaks first… because the world is frozen.\n")

        loaded = None
        try:
            loaded = self.saver.load()
        except Exception:
            loaded = None

        if isinstance(loaded, dict) and loaded.get("player_name"):
            self.state.update(loaded)
            self.print_line(f"[SAVE] Loaded. Welcome back, {self.state['player_name']}.")
            self.terminal.hide_namebar()
            self.enter_node(self.state.get("current_node", "N1"))
            self.terminal.focus()
            return

        self._reset_state_fresh()
        self.terminal.show_namebar("Enter your name, then press Set.")
        self.print_line("[SETUP] No valid save found. Please enter your name in the field above.")

    def _on_set_name(self):
        name = self.terminal.name_var.get().strip()
        if not name:
            self.terminal.set_name_status("Name required.")
            return

        self.state["player_name"] = name

        ok = self._persist_with_repair()
        if not ok:
            self._reset_state_fresh()
            self.terminal.name_var.set("")
            self.terminal.set_name_status("Save failed. Try again.")
            messagebox.showerror(
                "Save Error",
                "Could not create encrypted save.\nI reset the save files—please enter your name again."
            )
            return

        self.terminal.set_name_status("")
        self.terminal.hide_namebar()

        self.print_line(f"Welcome, {name}.")
        self.enter_node(self.state["current_node"])
        self.terminal.focus()

    # ---------------- terminal input ----------------
    def _on_enter(self):
        cmd = self.terminal.input_var.get().strip()
        if not cmd:
            return
        self.terminal.input_var.set("")
        self.print_line(f"> {cmd}")

        if not self.state.get("player_name"):
            self.print_line("[LOCKED] Enter your name in the field above first.")
            self.terminal.show_namebar("Enter your name, then press Set.")
            return

        self.router.run(cmd)
        self._persist()
        self.update_status()

    # ---------------- game / node flow ----------------
    def enter_node(self, node_id: str):
        if node_id not in self.cfg.get("nodes", {}):
            self.print_line(f"[ERR] Unknown node {node_id}")
            return

        self.state["current_node"] = node_id
        self._persist()

        ncfg = self.node_cfg(node_id)
        self.print_line(f"\n=== {node_id}: {ncfg.get('title','(untitled)')} ===")
        self.print_line(f"[TIME] {self.node_time(node_id)} (fixed)")
        self.print_line("Type: story   |  story all")

        self.rightpanel.clear()

        games = ncfg.get("games", [])
        if games:
            self.mount_game(games[0]["id"])

        self.update_status()
        try:
            self.eventdb.log("enter_node", {"node": node_id, "score": self.state["score"]})
        except Exception:
            pass

    def mount_game(self, game_id: str):
        if game_id not in self.game_registry:
            self.print_line(f"[ERR] Unknown game '{game_id}'")
            return

        if self.current_game is not None:
            try:
                self.current_game.stop()
            except Exception:
                pass

        cls = self.game_registry[game_id]
        g = cls(self)

        # If your GameBase doesn't implement this, don't crash
        if hasattr(g, "is_allowed_here") and not g.is_allowed_here():
            self.print_line("[LOCKED] That game is not available in this node.")
            self.rightpanel.clear()
            return

        self.current_game = g
        self.current_game.mount(self.rightpanel.game_panel)
        try:
            self.current_game.start()
        except Exception:
            pass

        try:
            self.eventdb.log("mount_game", {"node": self.state["current_node"], "game": game_id})
        except Exception:
            pass

    # ---------------- commands ----------------
    def cmd_status(self):
        self.update_status()
        self.print_line(self.status.cget("text"))

    def cmd_time(self):
        nid = self.state["current_node"]
        self.print_line(f"[TIME] Node {nid}: {self.node_time(nid)} (fixed)")

    def cmd_nodes(self):
        nodes = sorted(self.cfg.get("nodes", {}).keys())
        self.print_line("Nodes: " + ", ".join(nodes))
        self.print_line("Unlocked: " + ", ".join(self.state.get("unlocked_nodes", [])))

    def cmd_routes(self):
        cur = self.state["current_node"]
        routes = self.node_cfg(cur).get("routes", [])
        self.print_line("=== CHRONO ROUTES ===")
        if not routes:
            self.print_line("  (none)")
            return
        for n in routes:
            open_ = "YES" if n in self.state.get("unlocked_nodes", []) else "NO"
            self.print_line(f"  -> {n}   OPEN: {open_}")

    def cmd_travel(self, args):
        if not args:
            self.print_line("Usage: travel N2")
            return
        node_id = args[0].upper()
        cur = self.state["current_node"]
        routes = self.node_cfg(cur).get("routes", [])

        if node_id not in self.cfg.get("nodes", {}):
            self.print_line("[ERR] Unknown node.")
            return
        if node_id != cur and node_id not in routes:
            self.print_line("[LOCKED] No direct route. Use: routes")
            return
        if node_id not in self.state.get("unlocked_nodes", []):
            self.print_line("[LOCKED] Node not unlocked yet.")
            return

        self.enter_node(node_id)

    def cmd_games(self):
        nid = self.state["current_node"]
        games = self.node_cfg(nid).get("games", [])
        self.print_line(f"Games in {nid}:")
        if not games:
            self.print_line("  (none)")
            return
        for g in games:
            self.print_line(f"  - {g['id']}: {g.get('title', '')}")

    def cmd_play(self, args):
        if not args:
            self.print_line("Usage: play <game_id>")
            return
        self.mount_game(args[0].lower())

    def cmd_story(self, args):
        """
        story      -> next dialogue line (loops forever)
        story all  -> replay full dialogue from start (animated, no interleaving)
        """
        nid = self.state["current_node"]
        lines = self.node_cfg(nid).get("intro", [])
        if not lines:
            self.print_line("[STORY] No dialogue here.")
            return

        if "story_index" not in self.state or not isinstance(self.state["story_index"], dict):
            self.state["story_index"] = {}

        delay_ms = 14  # must match _type_line
        gap_ms = 120  # pause between lines

        def line_duration(speaker: str, text: str) -> int:
            # duration of typewriter for this line
            return max(0, len(f"{speaker}: {text}") * delay_ms + gap_ms)

        # story all: reset to start and play full sequence (serialized)
        if args and str(args[0]).lower() == "all":
            self.state["story_index"][nid] = 0

            def play_all(i: int):
                if i >= len(lines):
                    # loop back to start (so next 'story' begins from line 0)
                    self.state["story_index"][nid] = 0
                    try:
                        self.eventdb.log("story_all", {"node": nid})
                    except Exception:
                        pass
                    return

                line = lines[i] or {}
                sp = line.get("speaker", "NARRATOR")
                tx = line.get("text", "")

                # type this line, then schedule next after it finishes
                dur = 0
                if hasattr(self.terminal, "write_raw"):
                    dur = self._type_line(f"{sp}: {tx}", delay_ms=delay_ms)
                else:
                    self.print_line(f"{sp}: {tx}")

                self.root.after(max(dur, line_duration(sp, tx)), lambda: play_all(i + 1))

            play_all(0)
            return

        # story single step: loop at end
        idx = int(self.state["story_index"].get(nid, 0))
        if idx >= len(lines):
            idx = 0

        line = lines[idx] or {}
        sp = line.get("speaker", "NARRATOR")
        tx = line.get("text", "")

        if hasattr(self.terminal, "write_raw"):
            self._type_line(f"{sp}: {tx}", delay_ms=delay_ms)
        else:
            self.print_line(f"{sp}: {tx}")

        idx += 1
        if idx >= len(lines):
            idx = 0
        self.state["story_index"][nid] = idx

        try:
            self.eventdb.log("story_next", {"node": nid, "to": idx})
        except Exception:
            pass
    def cmd_selftest(self, args):
        """
        selftest <PASSWORD>
        Runs a smoke-test for major commands and prints PASS/FAIL.
        Password = APP_SAVE_KEY (same key used for encrypted saves).
        """
        if not args:
            self.print_line("Usage: selftest <PASSWORD>")
            return

        pw = " ".join(args).strip()
        if pw != APP_SAVE_KEY:
            self.print_line("[NO] Bad password.")
            return

        self.print_line("=== SELFTEST ===")

        tests = [
            ("status", lambda: self.cmd_status()),
            ("time", lambda: self.cmd_time()),
            ("nodes", lambda: self.cmd_nodes()),
            ("routes", lambda: self.cmd_routes()),
            ("games", lambda: self.cmd_games()),
            ("story", lambda: self.cmd_story([])),
            ("story all", lambda: self.cmd_story(["all"])),
            ("hint(list)", lambda: self.cmd_hint([]) if hasattr(self, "cmd_hint") else None),
            ("help(router)", lambda: self.router.run("help")),
            ("man story", lambda: self.router.run("man story")),
        ]

        passed = 0
        failed = 0

        for name, fn in tests:
            try:
                fn()
                self.print_line(f"[PASS] {name}")
                passed += 1
            except Exception as e:
                self.print_line(f"[FAIL] {name}: {e}")
                failed += 1

        self.print_line(f"=== RESULT: {passed} passed, {failed} failed ===")
    # ---------------- unlock / scoring helpers ----------------
    def unlock_node(self, node_id: str, reason: str):
        if node_id not in self.state["unlocked_nodes"]:
            self.state["unlocked_nodes"].append(node_id)
        self.print_line(f"[UNLOCK] {node_id} unlocked ({reason}).")
        try:
            self.eventdb.log("unlock", {"node": node_id, "reason": reason})
        except Exception:
            pass

    def award_game(self, game_id: str):
        nid = self.state["current_node"]
        games = self.node_cfg(nid).get("games", [])
        meta = next((g for g in games if g.get("id") == game_id), None)
        if not meta:
            return

        if self.state["solved"].get(game_id):
            self.print_line("[INFO] Already solved.")
            return

        pts = int(meta.get("solve_points", 0))
        token = meta.get("token")

        self.state["score"] = int(self.state.get("score", 0)) + pts
        self.state["solved"][game_id] = True

        if token and token not in self.state["tokens"]:
            self.state["tokens"].append(token)

        self.print_line(f"[OK] Solved {game_id}. +{pts} pts.")
        if token:
            self.print_line("[FRAGMENT] You gained a fragment (not shown plainly).")

        try:
            self.eventdb.log("solve", {"node": nid, "game": game_id, "points": pts, "score": self.state["score"]})
        except Exception:
            pass

        for nxt in self.node_cfg(nid).get("routes", []):
            self.unlock_node(nxt, f"{game_id} solved")

    # ---------------- existing commands you had (keep yours) ----------------
    def cmd_hint(self, args):
        nid = self.state["current_node"]
        hints = self.node_cfg(nid).get("hints", [])
        if not hints:
            self.print_line("[HINT] No hints here.")
            return

        if args:
            wanted = str(args[0]).lower()
            hint = next((h for h in hints if str(h.get("id", "")).lower() == wanted), None)
            if not hint:
                self.print_line("[ERR] Unknown hint id.")
                return
        else:
            hint = hints[0]

        now = time.time()
        last = float(self.state.get("last_hint_ts", 0) or 0)
        wait_left = int(self.hint_cooldown - (now - last))
        if wait_left > 0:
            self.print_line(f"[COOLDOWN] Hint available in {wait_left}s.")
            return

        cost = int(hint.get("cost", 0))
        cur_score = int(self.state.get("score", 0))
        if cur_score < cost:
            self.print_line(f"[LOCKED] Need {cost} score for this hint.")
            return

        self.state["score"] = cur_score - cost
        self.state["last_hint_ts"] = now
        self.print_line(f"[HINT:{hint.get('id', '?')}] {hint.get('text', '')} (-{cost} score)")

    def cmd_showcode(self, args):
        if self.state["current_node"] != "N3":
            self.print_line("[LOCKED] showcode is available in N3.")
            return
        if not args:
            self.print_line("Usage: showcode <A|B|C|D>")
            return

        key = str(args[0]).upper()
        if key not in {"A", "B", "C", "D"}:
            self.print_line("Usage: showcode <A|B|C|D>")
            return

        if self.current_game and hasattr(self.current_game, "show"):
            self.current_game.show(key)
        self.state.setdefault("answers", {})["N3_last_code"] = key
        self.print_line(f"[N3] Current code snippet: {key}")

    def cmd_solve(self, args):
        if not args:
            self.print_line("Usage: solve <colors|chess|code|regex|tictactoe|dilemma> ...")
            return

        kind = str(args[0]).lower()
        rest = args[1:]

        if kind == "colors":
            if self.state["current_node"] != "N1":
                self.print_line("[LOCKED] colors belongs to N1.")
                return
            if not rest:
                self.print_line("Usage: solve colors <MINUTES>")
                return
            minutes = self.node_time("N1").split(":")[-1]
            if str(rest[0]) == str(int(minutes)) or str(rest[0]) == minutes:
                self.award_game("colors")
            else:
                self.print_line("[NO] Incorrect.")
            return

        if kind == "chess":
            if self.state["current_node"] != "N2":
                self.print_line("[LOCKED] chess belongs to N2.")
                return
            if not rest:
                self.print_line("Usage: solve chess <MOVE>")
                return
            mv = str(rest[0]).replace("+", "").replace("#", "").strip().lower()
            if mv in {"ne7", "nxe7", "e7"}:
                self.award_game("chess")
            else:
                self.print_line("[NO] Not the best fork.")
            return

        if kind == "code":
            if self.state["current_node"] != "N3":
                self.print_line("[LOCKED] code belongs to N3.")
                return
            if len(rest) < 2:
                self.print_line("Usage: solve code <A|B|C|D> <N#>")
                return
            key = str(rest[0]).upper()
            node = str(rest[1]).upper()
            if key in {"A", "B", "C", "D"} and node.startswith("N"):
                self.award_game("codes")
            else:
                self.print_line("[NO] Incorrect format.")
            return

        if kind == "regex":
            if self.state["current_node"] != "N4":
                self.print_line("[LOCKED] regex belongs to N4.")
                return
            if not rest:
                self.print_line("Usage: solve regex <1|2|3|4>")
                return
            pick = str(rest[0])
            answers = self.state.get("answers", {})
            chosen = answers.get("N4_regex_map", {}).get(pick)
            correct = answers.get("N4_regex_correct")
            if chosen and correct and chosen == correct:
                self.award_game("regex")
            else:
                self.print_line("[NO] Pattern mismatch.")
            return

        if kind == "tictactoe":
            if self.state["current_node"] != "N5":
                self.print_line("[LOCKED] tictactoe belongs to N5.")
                return
            g = self.current_game
            if g and getattr(g, "game_id", "") == "tictactoe" and hasattr(g, "sequence_ok") and g.sequence_ok():
                self.award_game("tictactoe")
            else:
                self.print_line("[NO] Complete the board sequence first.")
            return

        if kind == "dilemma":
            if self.state["current_node"] != "N5":
                self.print_line("[LOCKED] dilemma belongs to N5.")
                return
            g = self.current_game
            if g and getattr(g, "game_id", "") == "dilemma" and hasattr(g, "success") and g.success():
                self.award_game("dilemma")
            else:
                self.print_line("[NO] Finish all rounds with higher score.")
            return

        self.print_line("[ERR] Unknown solve target.")

    def cmd_train(self, args):
        if not args:
            self.print_line("Usage: train dilemma")
            return
        target = str(args[0]).lower()
        if target != "dilemma":
            self.print_line("[ERR] Unknown training module.")
            return
        self.mount_game("dilemma")

    def cmd_ttt(self, args):
        if self.state["current_node"] != "N5":
            self.print_line("[LOCKED] ttt tools are for N5.")
            return
        if not args:
            self.print_line("Usage: ttt status|reset")
            return
        g = self.current_game
        if not g or getattr(g, "game_id", "") != "tictactoe":
            self.mount_game("tictactoe")
            g = self.current_game
        action = str(args[0]).lower()
        if action == "status":
            if hasattr(g, "round_index") and hasattr(g, "results"):
                self.print_line(f"[TTT] Round {g.round_index + 1}/{g.rounds} Results: {''.join(g.results) or '(none)'}")
            else:
                self.print_line("[TTT] status unavailable")
        elif action == "reset":
            if hasattr(g, "_reset_round"):
                g._reset_round()
                self.print_line("[TTT] Round reset.")
            else:
                self.print_line("[TTT] reset unavailable")
        else:
            self.print_line("Usage: ttt status|reset")

    def cmd_unlock(self, args):
        if self.state["current_node"] != "N6":
            self.print_line("[LOCKED] unlock is only available in N6.")
            return
        if not args:
            self.print_line("Usage: unlock <password>")
            return
        expected = self._final_password()
        provided = " ".join(args).strip()
        if provided != expected:
            self.print_line("[NO] Wrong password.")
            return
        self.award_game("final")
        self.print_line("[END] Axis unlocked. Timeline restored.")

    def cmd_godskip(self, args):
        nid = self.state["current_node"]
        expected = self.node_cfg(nid).get("godskip")
        if not args:
            self.print_line("Usage: godskip <CODE>")
            return
        code = " ".join(args).strip()
        if code != expected:
            self.print_line("[NO] Invalid godskip code.")
            return
        routes = self.node_cfg(nid).get("routes", [])
        if not routes:
            self.print_line("[INFO] No further route from this node.")
            return
        nxt = routes[0]
        self.unlock_node(nxt, "godskip")
        self.enter_node(nxt)

    def _final_password(self) -> str:
        tokens = sorted(self.state.get("tokens", []))
        seed = (self.state.get("player_name", "") + "|" + "|".join(tokens)).encode("utf-8")
        digest = hashlib.sha256(seed).hexdigest()
        return "axis-" + digest[:10]
