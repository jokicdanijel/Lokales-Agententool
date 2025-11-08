"""
Security-Modul für ELION Dashboard
Implementiert Token-Validierung, auto-Provisioning und Rate-Limiting.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
from fastapi.security import HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

ENV_FILE = Path(".env")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

def generate_token() -> str:
    import secrets
    return secrets.token_urlsafe(32)

def _ensure_token_file() -> str:
    if ENV_FILE.exists():
        content = ENV_FILE.read_text().strip()
        # Parse DASHBOARD_ADMIN_TOKEN=... format (nur erste Zeile)
        for line in content.split("\n"):
            if line.startswith("DASHBOARD_ADMIN_TOKEN="):
                tok = line.split("=", 1)[1].strip()
                if tok:
                    return tok
    # neu erzeugen
    tok = generate_token()
    ENV_FILE.write_text(f"DASHBOARD_ADMIN_TOKEN={tok}")
    logging.getLogger("security").info("Neuer Token generiert und in .env gespeichert.")
    return tok

_CURRENT_TOKEN = _ensure_token_file()

class RateLimiter:
    """Rate-Limiting pro Token (Sliding Window)"""
    def __init__(self, requests_per_minute: int = 60):
        self.rate_limit = requests_per_minute
        self.window_size = 60.0
        self._reqs: Dict[str, list[float]] = {}

    def _clean(self, t: str):
        now = time.time()
        if t in self._reqs:
            self._reqs[t] = [ts for ts in self._reqs[t] if now - ts < self.window_size]
            if not self._reqs[t]:
                self._reqs.pop(t, None)

    def is_allowed(self, token_like) -> bool:
        # token_like kann str oder HTTPAuthorizationCredentials sein
        if isinstance(token_like, HTTPAuthorizationCredentials):
            t = token_like.credentials
        else:
            t = str(token_like or "")
        if not t:
            return False

        self._clean(t)
        now = time.time()
        bucket = self._reqs.setdefault(t, [])
        if len(bucket) >= self.rate_limit:
            return False
        bucket.append(now)
        return True

    def limit(self):
        from functools import wraps
        from fastapi import HTTPException

        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                token_obj = kwargs.get("token", None)
                if not token_obj:
                    # Versuche aus *args* zu holen (FastAPI gibt Sicherheits-Param dort selten weiter)
                    for a in args:
                        if isinstance(a, HTTPAuthorizationCredentials):
                            token_obj = a
                            break
                if not token_obj:
                    raise HTTPException(status_code=401, detail="Token erforderlich")

                if not self.is_allowed(token_obj):
                    raise HTTPException(status_code=429, detail="Rate limit überschritten")

                return await func(*args, **kwargs)
            return wrapper
        return decorator

def verify_token(token: str) -> bool:
    ok = bool(token) and token == _CURRENT_TOKEN
    logging.getLogger("security").info(f"Tokenprüfung ok={ok}")
    return ok

class SecurityLog:
    """Protokolliert Sicherheitsereignisse"""
    def __init__(self):
        self.logger = logging.getLogger("security")
        fh = logging.FileHandler(LOG_DIR / "security.log")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(fh)
        self.logger.setLevel(logging.INFO)

    def log_access(self, token: str, endpoint: str, allowed: bool):
        tshort = (token or "")[:8]
        self.logger.info(f"Access: token={tshort} endpoint={endpoint} allowed={allowed}")

    def log_violation(self, details: str):
        self.logger.warning(f"Security violation: {details}")

security_log = SecurityLog()




rate_limiter = RateLimiter(requests_per_minute=60)
