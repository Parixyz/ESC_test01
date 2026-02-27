import json
import os
import sqlite3
import time

class EncryptedEventDB:
    def __init__(self, db_path: str, encryption, password_getter, save_dir: str):
        self.db_path = db_path
        self.encryption = encryption
        self.password_getter = password_getter
        os.makedirs(save_dir, exist_ok=True)
        self._init_db()

    def _init_db(self):
        con = sqlite3.connect(self.db_path)
        try:
            cur = con.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS events(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts INTEGER NOT NULL,
                    kind TEXT NOT NULL,
                    payload BLOB NOT NULL
                )
            """)
            con.commit()
        finally:
            con.close()

    def log(self, kind: str, obj: dict):
        pw = self.password_getter()
        if not pw:
            return
        try:
            ts = int(time.time())
            raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            enc = self.encryption.encrypt_bytes(raw, pw)
            con = sqlite3.connect(self.db_path)
            try:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO events(ts, kind, payload) VALUES(?,?,?)",
                    (ts, kind, enc)
                )
                con.commit()
            finally:
                con.close()
        except Exception:
            pass
