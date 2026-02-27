# stub
import base64
import hashlib
import hmac
import os

class Encryption:
    """
    KEEP EXACT STYLE: PBKDF2 + HMAC + XOR keystream
    """
    def __init__(self, rounds: int = 150_000):
        self.rounds = rounds

    def _pbkdf2_key(self, password: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, self.rounds, dklen=32
        )

    def _keystream(self, key: bytes, nbytes: int) -> bytes:
        out = bytearray()
        counter = 0
        while len(out) < nbytes:
            msg = counter.to_bytes(8, "big")
            out.extend(hashlib.sha256(key + msg).digest())
            counter += 1
        return bytes(out[:nbytes])

    def encrypt_bytes(self, plaintext: bytes, password: str) -> bytes:
        salt = os.urandom(16)
        key = self._pbkdf2_key(password, salt)
        ks = self._keystream(key, len(plaintext))
        ct = bytes([p ^ k for p, k in zip(plaintext, ks)])
        mac = hmac.new(key, salt + ct, hashlib.sha256).digest()
        blob = salt + mac + ct
        return base64.urlsafe_b64encode(blob)

    def decrypt_bytes(self, ciphertext_b64: bytes, password: str) -> bytes:
        blob = base64.urlsafe_b64decode(ciphertext_b64)
        if len(blob) < 16 + 32:
            raise ValueError("Corrupt save")
        salt = blob[:16]
        mac = blob[16:48]
        ct = blob[48:]
        key = self._pbkdf2_key(password, salt)
        mac2 = hmac.new(key, salt + ct, hashlib.sha256).digest()
        if not hmac.compare_digest(mac, mac2):
            raise ValueError("Wrong password or tampered save")
        ks = self._keystream(key, len(ct))
        pt = bytes([c ^ k for c, k in zip(ct, ks)])
        return pt