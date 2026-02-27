# stub
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class SavePaths:
    save_dir: str
    save_path: str

class SaveManager:
    def __init__(self, paths: SavePaths, encryption, password_getter):
        self.paths = paths
        self.encryption = encryption
        self.password_getter = password_getter
        os.makedirs(self.paths.save_dir, exist_ok=True)

    def load(self) -> Optional[Dict[str, Any]]:
        pw = self.password_getter()
        if not pw:
            return None
        if not os.path.exists(self.paths.save_path):
            return None
        try:
            with open(self.paths.save_path, "rb") as f:
                blob = f.read()
            pt = self.encryption.decrypt_bytes(blob, pw)
            return json.loads(pt.decode("utf-8"))
        except Exception:
            return None

    def save(self, state: Dict[str, Any]) -> None:
        pw = self.password_getter()
        if not pw:
            return
        os.makedirs(self.paths.save_dir, exist_ok=True)
        raw = json.dumps(state, ensure_ascii=False).encode("utf-8")
        blob = self.encryption.encrypt_bytes(raw, pw)
        with open(self.paths.save_path, "wb") as f:
            f.write(blob)