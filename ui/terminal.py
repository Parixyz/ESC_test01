import tkinter as tk
from tkinter import ttk


class TerminalView:
    def __init__(self, root_unused, bg: str, fg: str):
        self.bg = bg
        self.fg = fg

        self.input_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self._name_status_var = tk.StringVar()

        self.output = None
        self.entry = None
        self._namebar = None
        self._name_entry = None

        self._typing_job = None
        self._typing_active = False

    def pack_namebar(self, parent, on_set_name):
        if self._namebar is not None:
            return

        bar = ttk.Frame(parent)
        bar.pack(fill="x", padx=10, pady=(10, 0))

        ttk.Label(bar, text="Name:").pack(side="left")
        name_entry = ttk.Entry(bar, textvariable=self.name_var, width=28)
        name_entry.pack(side="left", padx=(8, 8))
        ttk.Button(bar, text="Set", command=on_set_name).pack(side="left")

        name_entry.bind("<Return>", lambda e: on_set_name())

        status = ttk.Label(bar, textvariable=self._name_status_var)
        status.pack(side="left", padx=(12, 0))

        self._namebar = bar
        self._name_entry = name_entry
        self.hide_namebar()

    def show_namebar(self, status_text: str = ""):
        if self._namebar is None:
            return
        self._namebar.pack_forget()
        self._namebar.pack(fill="x", padx=10, pady=(10, 0))
        self._name_status_var.set(status_text or "")
        try:
            self._name_entry.focus_set()
        except Exception:
            pass

    def hide_namebar(self):
        if self._namebar is None:
            return
        self._namebar.pack_forget()
        self._name_status_var.set("")

    def set_name_status(self, text: str):
        self._name_status_var.set(text or "")

    def pack(self, parent):
        if self.output is not None:
            return

        container = ttk.Frame(parent)
        container.pack(fill="both", expand=True, padx=10, pady=(10, 6))

        self.output = tk.Text(
            container,
            bg=self.bg,
            fg=self.fg,
            insertbackground=self.fg,
            wrap="word"
        )
        self.output.config(state="disabled")

        sc = ttk.Scrollbar(container, command=self.output.yview)
        self.output.configure(yscrollcommand=sc.set)

        self.output.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")

    def pack_input(self, parent, on_enter):
        row = ttk.Frame(parent)
        row.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Label(row, text="> ").pack(side="left")
        self.entry = ttk.Entry(row, textvariable=self.input_var)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", lambda e: on_enter())
        ttk.Button(row, text="Send", command=on_enter).pack(side="left", padx=(8, 0))

    def focus(self):
        if self.entry is not None:
            self.entry.focus_set()

    def write_line(self, s: str):
        if self.output is None:
            return
        self._cancel_typing()
        self.output.config(state="normal")
        self.output.insert("end", s + "\n")
        self.output.see("end")
        self.output.config(state="disabled")

    def clear(self):
        if self.output is None:
            return
        self._cancel_typing()
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.config(state="disabled")

    def _cancel_typing(self):
        self._typing_active = False
        if self._typing_job is not None and self.output is not None:
            try:
                self.output.after_cancel(self._typing_job)
            except Exception:
                pass
        self._typing_job = None

    def typewriter(self, root: tk.Misc, text: str, delay_ms: int = 14, newline: bool = True):
        """
        Writes text character-by-character reliably.
        - Enables the Text widget once for the whole animation.
        - Cancels any previous animation to prevent interleaving.
        """
        if self.output is None:
            return

        self._cancel_typing()
        self._typing_active = True

        self.output.config(state="normal")

        i = 0

        def step():
            nonlocal i
            if not self._typing_active or self.output is None:
                return

            if i >= len(text):
                if newline:
                    self.output.insert("end", "\n")
                self.output.see("end")
                self.output.config(state="disabled")
                self._typing_job = None
                self._typing_active = False
                return

            self.output.insert("end", text[i])
            self.output.see("end")
            i += 1
            self._typing_job = root.after(delay_ms, step)

        step()
