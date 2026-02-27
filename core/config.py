# stub
import json
import os

DEFAULT_CONFIG = {
    "meta": {"title": "Jack’s Time Terminal", "hint_cooldown_seconds": 300},
    "nodes": {}
}

class ConfigLoader:
    def __init__(self, base_dir: str, filename: str = "Config.json"):
        self.path = os.path.join(base_dir, filename)

    def load(self) -> dict:
        if not os.path.exists(self.path):
            # You asked: load Config.json instead.
            # If missing, create a minimal one so you don't crash.
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
            return DEFAULT_CONFIG

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            if "nodes" not in cfg:
                cfg["nodes"] = {}
            if "meta" not in cfg:
                cfg["meta"] = DEFAULT_CONFIG["meta"]
            return cfg
        except Exception:
            return DEFAULT_CONFIG