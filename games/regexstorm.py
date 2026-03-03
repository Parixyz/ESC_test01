from __future__ import annotations

import csv
import os
import random
import re
import statistics
from dataclasses import dataclass
from tkinter import StringVar, Text, filedialog, ttk

from games.base import GameBase


@dataclass
class ScanStudentResult:
    student_id: str
    file_count: int
    match_count: int


class BaseStudentScanner:
    def __init__(self, root_path: str):
        self.root_path = root_path

    def iter_student_dirs(self):
        if not os.path.isdir(self.root_path):
            return []
        dirs = []
        for name in sorted(os.listdir(self.root_path)):
            full = os.path.join(self.root_path, name)
            if os.path.isdir(full):
                dirs.append((name, full))
        return dirs


class RegexStudentScanner(BaseStudentScanner):
    def scan(self, pattern: str):
        regex = re.compile(pattern)
        results: list[ScanStudentResult] = []
        blank_students: list[str] = []

        for student_id, folder in self.iter_student_dirs():
            file_count = 0
            match_count = 0
            for dirpath, _, filenames in os.walk(folder):
                for fname in filenames:
                    file_count += 1
                    fpath = os.path.join(dirpath, fname)
                    if regex.search(fname):
                        match_count += 1
                        continue
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                            text = fh.read()
                        if regex.search(text):
                            match_count += 1
                    except OSError:
                        continue
            if file_count == 0:
                blank_students.append(student_id)
            results.append(
                ScanStudentResult(student_id=student_id, file_count=file_count, match_count=match_count)
            )

        return results, blank_students


class RegexStorm(GameBase):
    game_id = "regex"
    title = "Pattern Storm"

    def __init__(self, app):
        super().__init__(app)
        self.running = False
        self.after_id = None
        self.samples_lbl = None
        self.opts = []

        self.path_var = StringVar(value="")
        self.regex_var = StringVar(value=r"\\d+")
        self.scheme_var = StringVar(value="No scheme loaded")
        self.grading_target_var = StringVar(value="All scheme rows")

        self.scheme_rows: list[dict[str, str]] = []
        self.scheme_targets: list[str] = ["All scheme rows"]
        self.stats_out: Text | None = None
        self.hist_canvas = None
        self.target_combo = None

    def mount(self, parent):
        super().mount(parent)

        ttk.Label(parent, text=self.title, font=("Segoe UI", 11, "bold")).pack(
            padx=12, pady=(12, 6), anchor="nw"
        )
        ttk.Label(
            parent,
            text=(
                "Watch 4 changing sample strings on the left.\n"
                "Pick the one regex that matches all shown variations.\n"
                "Solve: solve regex <1|2|3|4|5>  (4 rounds, +/- points each round)"
            ),
            wraplength=520,
            justify="left",
        ).pack(padx=12, pady=(0, 8), anchor="nw")

        self.samples_lbl = ttk.Label(parent, text="(generating samples...)", wraplength=520, justify="left")
        self.samples_lbl.pack(padx=12, pady=(0, 10), anchor="nw")

        box = ttk.Frame(parent)
        box.pack(padx=12, pady=(0, 12), fill="x")

        self.opts = []
        for i in range(5):
            lbl = ttk.Label(box, text=f"{i+1}) ...", wraplength=520, justify="left")
            lbl.pack(anchor="nw", pady=2)
            self.opts.append(lbl)

        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=12, pady=8)
        self._build_scanner_ui(parent)

        self.running = True
        self._tick()

    def _build_scanner_ui(self, parent):
        ttk.Label(parent, text="Regex Student Scanner", font=("Segoe UI", 10, "bold")).pack(
            padx=12, pady=(0, 6), anchor="nw"
        )

        path_row = ttk.Frame(parent)
        path_row.pack(fill="x", padx=12, pady=2)
        ttk.Label(path_row, text="Scan path:").pack(side="left")
        ttk.Entry(path_row, textvariable=self.path_var).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(path_row, text="Browse", command=self._pick_scan_path).pack(side="left")

        regex_row = ttk.Frame(parent)
        regex_row.pack(fill="x", padx=12, pady=2)
        ttk.Label(regex_row, text="Regex:").pack(side="left")
        ttk.Entry(regex_row, textvariable=self.regex_var).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(regex_row, text="Reset Regex", command=self._reset_regex).pack(side="left")

        scheme_row = ttk.Frame(parent)
        scheme_row.pack(fill="x", padx=12, pady=2)
        ttk.Button(scheme_row, text="Load Scheme CSV", command=self._load_scheme).pack(side="left")
        ttk.Label(scheme_row, textvariable=self.scheme_var).pack(side="left", padx=8)

        target_row = ttk.Frame(parent)
        target_row.pack(fill="x", padx=12, pady=2)
        ttk.Label(target_row, text="Grading target:").pack(side="left")
        self.target_combo = ttk.Combobox(target_row, textvariable=self.grading_target_var, state="readonly")
        self.target_combo.pack(side="left", fill="x", expand=True, padx=6)
        self.target_combo["values"] = self.scheme_targets

        action_row = ttk.Frame(parent)
        action_row.pack(fill="x", padx=12, pady=(4, 6))
        ttk.Button(action_row, text="Run Scan", command=self._run_scan).pack(side="left")

        self.hist_canvas = Text(parent, height=8, width=72)
        self.hist_canvas.pack(fill="x", padx=12, pady=(2, 4))

        self.stats_out = Text(parent, height=10, width=72)
        self.stats_out.pack(fill="both", expand=True, padx=12, pady=(2, 12))

    def _pick_scan_path(self):
        picked = filedialog.askdirectory()
        if picked:
            self.path_var.set(picked)

    def _reset_regex(self):
        self.regex_var.set(r"\\d+")
        self.safe_print("[REGEX] Reset scanner regex to default: \\d+")

    def _load_scheme(self):
        path = filedialog.askopenfilename(
            title="Select scheme CSV",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
        )
        if not path:
            return

        loaded_rows: list[dict[str, str]] = []
        with open(path, "r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                normalized = {k.strip(): (v or "").strip() for k, v in row.items() if k}
                if normalized:
                    loaded_rows.append(normalized)

        self.scheme_rows = loaded_rows
        name = os.path.basename(path)
        self.scheme_var.set(f"Loaded: {name} ({len(loaded_rows)} rows)")
        self._refresh_scheme_targets()

    def _refresh_scheme_targets(self):
        targets = ["All scheme rows"]
        for row in self.scheme_rows:
            qid = row.get("question_id", "")
            sub_id = row.get("sub_id", "")
            title = row.get("question_title", "")
            group = row.get("group", "")
            if qid:
                label = f"{qid}"
                if sub_id:
                    label += f":{sub_id}"
                if title:
                    label += f" {title}"
                if group:
                    label += f" [{group}]"
                targets.append(label)

        self.scheme_targets = targets
        if self.target_combo is not None:
            self.target_combo["values"] = targets
        self.grading_target_var.set(targets[0])

    def _build_histogram(self, values: list[int]) -> str:
        if not values:
            return "No histogram data."
        max_value = max(values)
        lines = ["Histogram (matches per student):"]
        for bucket in range(max_value + 1):
            count = sum(1 for v in values if v == bucket)
            if count == 0:
                continue
            bar = "#" * min(50, count)
            lines.append(f"{bucket:>3}: {bar} ({count})")
        return "\n".join(lines)

    def _run_scan(self):
        scan_root = self.path_var.get().strip()
        pattern = self.regex_var.get().strip()

        if not scan_root:
            self.safe_print("[ERR] Set a scan path first.")
            return
        if not pattern:
            self.safe_print("[ERR] Set a regex pattern first.")
            return

        try:
            scanner = RegexStudentScanner(scan_root)
            results, blank_students = scanner.scan(pattern)
        except re.error as exc:
            self.safe_print(f"[ERR] Invalid regex: {exc}")
            return

        student_count = len(results)
        found_students = sum(1 for r in results if r.match_count > 0)
        missing_students = student_count - found_students
        values = [r.match_count for r in results]
        mean_val = statistics.mean(values) if values else 0.0
        median_val = statistics.median(values) if values else 0.0
        stdev_val = statistics.pstdev(values) if len(values) > 1 else 0.0

        chosen_target = self.grading_target_var.get().strip()
        scheme_note = "No scheme loaded"
        if self.scheme_rows:
            scheme_note = f"Scheme rows: {len(self.scheme_rows)} | Target: {chosen_target}"

        stats_lines = [
            f"Scan root: {scan_root}",
            f"Regex pattern: {pattern}",
            scheme_note,
            "",
            f"Students scanned: {student_count}",
            f"Students with matches: {found_students}",
            f"Students without matches: {missing_students}",
            f"Blank student folders (no files): {len(blank_students)}",
            "",
            f"Mean matches: {mean_val:.2f}",
            f"Median matches: {median_val:.2f}",
            f"Std dev matches: {stdev_val:.2f}",
            "",
            "Students with no matches:",
        ]
        stats_lines.extend([f"- {r.student_id}" for r in results if r.match_count == 0][:40])
        if blank_students:
            stats_lines.append("")
            stats_lines.append("Blank folders:")
            stats_lines.extend([f"- {sid}" for sid in blank_students[:40]])

        if self.stats_out is not None:
            self.stats_out.delete("1.0", "end")
            self.stats_out.insert("1.0", "\n".join(stats_lines))

        if self.hist_canvas is not None:
            self.hist_canvas.delete("1.0", "end")
            self.hist_canvas.insert("1.0", self._build_histogram(values))

        self.safe_print(
            f"[SCAN] Completed. Students={student_count}, matches={found_students}, blanks={len(blank_students)}"
        )

    def stop(self):
        self.running = False
        if self.after_id and getattr(self.app, "root", None):
            try:
                self.app.root.after_cancel(self.after_id)
            except Exception:
                pass
        self.after_id = None

    def _new_samples(self):
        prefix = random.choice(["TIME", "NODE", "JACK", "ECHO", "TRACE"])
        suffix = random.choice(["A", "B", "C"])
        return [f"{prefix}-{random.randint(10, 9999)}{suffix}" for _ in range(4)]

    def _tick(self):
        if not self.running:
            return

        samples = self._new_samples()
        correct = r"^(TIME|NODE|JACK|ECHO|TRACE)-\d{2,4}[ABC]$"
        choices = [
            correct,
            r"^(TIME|NODE|JACK|ECHO|TRACE)\d{2,4}[ABC]$",
            r"^[A-Z]+-\d{5}[ABC]$",
            r"^[A-Z]+-\d{2,4}$",
            r"^\d{2,4}-[A-Z]+[ABC]$",
        ]
        random.shuffle(choices)

        if self.samples_lbl:
            block = "\n".join([f"• {s}" for s in samples])
            self.samples_lbl.config(text=f"Samples:\n{block}")

        for i, lbl in enumerate(self.opts):
            try:
                lbl.config(text=f"{i+1}) {choices[i]}")
            except Exception:
                pass

        try:
            self.app.state.setdefault("answers", {})
            self.app.state["answers"]["N4_regex_samples"] = samples
            self.app.state["answers"]["N4_regex_correct"] = correct
            self.app.state["answers"]["N4_regex_map"] = {str(i + 1): choices[i] for i in range(5)}
        except Exception:
            pass

        try:
            self.after_id = self.app.root.after(5500, self._tick)
        except Exception:
            self.running = False
