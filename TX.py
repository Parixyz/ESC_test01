

from pathlib import Path
import json

PROJECT_TREE = {
    "core": [
        "__init__.py",
        "encryption.py",
        "storage.py",
        "eventdb.py",
        "commands.py",
        "config.py",
    ],
    "ui": [
        "__init__.py",
        "app.py",
        "terminal.py",
        "rightpanel.py",
    ],
    "games": [
        "__init__.py",
        "base.py",
        "chromatic.py",
        "chessfork.py",
        "codeobs.py",
        "regexstorm.py",
        "tictactoe.py",
        "dilemma.py",
        "axislock.py",
    ],
}

MAIN_PY_STUB = """\
def main():
    pass

if __name__ == "__main__":
    main()
"""

CONFIG_JSON_STUB = {
    "meta": {
        "title": "Time Terminal (Config)",
        "hint_cooldown_seconds": 300
    },
    "nodes": {
    }
}

GITIGNORE = """\
__pycache__/
*.pyc
*.pyo
*.pyd
.env
.venv/
venv/
.dist/
build/
dist/
.time_terminal_game/
"""

def write_file(path: Path, content: str, overwrite: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return
    path.write_text(content, encoding="utf-8")

def touch_stub(path: Path, overwrite: bool = False) -> None:
    """
    Creates an empty/stub file.
    - __init__.py: empty
    - others: minimal comment header so file isn't truly blank
    """
    if path.exists() and not overwrite:
        return
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.name == "__init__.py":
        path.write_text("", encoding="utf-8")
    else:
        path.write_text("# stub\n", encoding="utf-8")

def main() -> None:
    root = Path.cwd()

    write_file(root / "main.py", MAIN_PY_STUB, overwrite=False)

    cfg_path = root / "Config.json"
    if not cfg_path.exists():
        cfg_path.write_text(json.dumps(CONFIG_JSON_STUB, indent=2), encoding="utf-8")

    write_file(root / ".gitignore", GITIGNORE, overwrite=False)

    for folder, files in PROJECT_TREE.items():
        for fname in files:
            touch_stub(root / folder / fname, overwrite=False)

    print("OK: scaffold created.")
    print(f"Root: {root}")
    print("Created: main.py, Config.json, .gitignore, core/, ui/, games/")

if __name__ == "__main__":
    main()
