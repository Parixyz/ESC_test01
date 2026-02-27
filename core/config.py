import json
import os

DEFAULT_CONFIG = {
    "meta": {"title": "Jack’s Time Terminal", "hint_cooldown_seconds": 300},
    "nodes": {}
}

class ConfigLoader:
    def __init__(self, base_dir: str, filename: str = "nodes.json"):
        self.base_dir = base_dir
        self.filename = filename

    def _candidate_paths(self):
        primary = os.path.join(self.base_dir, self.filename)
        legacy = os.path.join(self.base_dir, "Config.json")
        if primary == legacy:
            return [primary]
        return [primary, legacy]

    def load(self) -> dict:
        for path in self._candidate_paths():
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                if "nodes" not in cfg:
                    cfg["nodes"] = {}
                if "meta" not in cfg:
                    cfg["meta"] = DEFAULT_CONFIG["meta"]
                return cfg
            except Exception:
                continue

        target = os.path.join(self.base_dir, self.filename)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        return DEFAULT_CONFIG
