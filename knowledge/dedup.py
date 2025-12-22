import hashlib
import os
import threading
from typing import Optional


def content_sha256(text: str) -> str:
    # normalize whitespace and compute sha256
    norm = " ".join(text.strip().split())
    return hashlib.sha256(norm.encode('utf-8')).hexdigest()


class DedupIndex:
    """Simple deduplication index backed by a newline-delimited file of hex hashes.

    - On add: if path provided, append hash+"\n" and fsync
    - In-memory set used for fast checks
    - Thread-safe
    """

    def __init__(self, path: Optional[str] = None):
        self.path = path
        self._set = set()
        self._lock = threading.RLock()
        if path and os.path.exists(path):
            self._load_from_file()

    def _load_from_file(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            for line in f:
                h = line.strip()
                if h:
                    self._set.add(h)

    def seen(self, content_hash: str) -> bool:
        with self._lock:
            return content_hash in self._set

    def add(self, content_hash: str) -> bool:
        """Add hash to index. Returns True if added (was new), False if already present."""
        with self._lock:
            if content_hash in self._set:
                return False
            self._set.add(content_hash)
            if self.path:
                # append and fsync
                os.makedirs(os.path.dirname(self.path), exist_ok=True)
                with open(self.path, 'a', encoding='utf-8') as f:
                    f.write(content_hash + '\n')
                    f.flush()
                    os.fsync(f.fileno())
            return True

    def size(self) -> int:
        with self._lock:
            return len(self._set)
