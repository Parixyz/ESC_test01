import os
import tkinter as tk
from ui.app import TimeTerminalApp

def main():
    root = tk.Tk()
    try:
        import tkinter.ttk as ttk
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass

    base_dir = os.path.dirname(__file__)
    app = TimeTerminalApp(root, base_dir)
    root.mainloop()

if __name__ == "__main__":
    main()
