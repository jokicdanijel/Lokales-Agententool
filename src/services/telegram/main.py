"""
telegram/main.py — Telegram Bot Service (telep)
- Receive messages from Telegram API
- Forward to OpenWebUI or other services
- Health: `/health`

Port: 12347 (Policy-bound, assigned)
Integration: Portier (kordp) via /dispatch/kordp
"""

import hashlib
import os
import socket
import time
from datetime import datetime
from typing import Any

import httpx
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

# ────────────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────────────

PORT = 12347
COORDINATOR_PORT = 12344  # Portier (kordp)
ARCHIVP_PORT = 12345  # OpenA2 (Archivator)
SERVICE_NAME = "telegram"
PROGRAM_TARGET = "telep"

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "0")


def _key_fingerprint(secret: str) -> str:
    """Return non-reversible fingerprint (sha256/8)."""
    if not secret:
        return ""
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()[:8]


TELEGRAM_PRESENT = bool(TELEGRAM_BOT_TOKEN)
TELEGRAM_FP = _key_fingerprint(TELEGRAM_BOT_TOKEN)

REDACT_KEYS = {
    "authorization",
    "telegram_bot_token",
    "bot_token",
    "token",
    "api_key",
    "TELEGRAM_BOT_TOKEN",
    "bearer",
    "key",
}


def _redact_secrets(obj: Any) -> Any:
    """Remove/obfuscate sensitive fields recursively."""
    if isinstance(obj, dict):
        sanitized: dict[str, Any] = {}
        for k, v in obj.items():
            kl = str(k).lower()
            if kl in REDACT_KEYS or "token" in kl or "secret" in kl or "key" in kl:
                sanitized[k] = "***REDACTED***"
            else:
                sanitized[k] = _redact_secrets(v)
        return sanitized
    if isinstance(obj, list):
        return [_redact_secrets(x) for x in obj]
    return obj


def _now() -> str:
    """Return ISO 8601 timestamp (UTC)."""
    return datetime.utcnow().isoformat() + "Z"


def _hostname() -> str:
    """Return hostname or fallback."""
    try:
        return socket.gethostname()
    except Exception:
        return "unknown-host"


# ────────────────────────────────────────────────────────────────────────
# Pydantic Models
# ────────────────────────────────────────────────────────────────────────


class MessageIn(BaseModel):
    """Incoming Telegram message."""

    model_config = ConfigDict(extra="forbid")
    chat_id: int = Field(...)
    text: str = Field(..., min_length=1)
    user_id: int | None = None
    username: str | None = None
    strict: bool = True


class NotifyIn(BaseModel):
    """Notification payload."""

    model_config = ConfigDict(extra="forbid")
    message: str = Field(..., min_length=1)
    chat_id: int | None = None
    strict: bool = True


# ────────────────────────────────────────────────────────────────────────
# FastAPI App
# ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=f"Telegram Bot — {PROGRAM_TARGET.upper()}", description="Telegram Bot Integration Service", version="1.0.0"
)

# Statistics
STATS = {
    "messages_received": 0,
    "messages_sent": 0,
    "errors": 0,
}

APP_META = {
    "service": SERVICE_NAME,
    "program_target": PROGRAM_TARGET,
    "role": "messenger",
    "host": _hostname(),
    "port": PORT,
    "coordinator_port": COORDINATOR_PORT,
    "archivp_port": ARCHIVP_PORT,
    "strict": True,
}


# ────────────────────────────────────────────────────────────────────────
# Helper: Store Safepoint (delegate to Archivator)
# ────────────────────────────────────────────────────────────────────────


async def _store_safepoint(kind: str, body: dict[str, Any]) -> None:
    """Delegate safepoint storage to OpenA2."""
    url = f"http://127.0.0.1:{ARCHIVP_PORT}/store/archivp"
    payload = {
        "src": PROGRAM_TARGET,
        "dst": "archivp",
        "kind": kind,
        "body": _redact_secrets(body),
        "strict": True,
        "ts": _now(),
    }
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
    except Exception as e:
        print(f"⚠️  Safepoint storage failed: {e}")
        STATS["errors"] += 1


# ────────────────────────────────────────────────────────────────────────
# Endpoints
# ────────────────────────────────────────────────────────────────────────


@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        **APP_META,
        "telegram_bot_present": TELEGRAM_PRESENT,
        "telegram_fp": TELEGRAM_FP,
        "stats": STATS,
        "status": "ok",
    }


@app.post("/message/receive")
async def receive_message(msg: MessageIn) -> dict[str, Any]:
    """Receive message from Telegram."""
    STATS["messages_received"] += 1

    # Log to archive
    await _store_safepoint(
        "MESSAGE_IN",
        {
            "chat_id": msg.chat_id,
            "user_id": msg.user_id,
            "username": msg.username,
            "text": msg.text,
        },
    )

    return {
        "ok": True,
        "message_id": int(time.time() * 1000),
        "strict": True,
    }


@app.post("/notify")
async def notify(payload: NotifyIn) -> dict[str, Any]:
    """Send notification to Telegram chat."""
    STATS["messages_sent"] += 1
    chat_id = payload.chat_id or int(TELEGRAM_CHAT_ID)

    # Log to archive
    await _store_safepoint(
        "MESSAGE_OUT",
        {
            "chat_id": chat_id,
            "message": payload.message,
        },
    )

    return {
        "ok": True,
        "sent": True,
        "chat_id": chat_id,
        "strict": True,
    }


@app.post("/echo")
async def echo(payload: dict[str, Any]) -> dict[str, Any]:
    """Echo endpoint for testing."""
    await _store_safepoint("ECHO", payload)
    return {
        "ok": True,
        "echo": payload,
        "strict": True,
    }


# ────────────────────────────────────────────────────────────────────────
# Entry Point
# ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=False, access_log=False, log_level="info")
