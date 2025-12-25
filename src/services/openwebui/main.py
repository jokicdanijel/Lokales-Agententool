"""
openwebui/main.py — Open Web UI Service (openweb)
- Inference gateway to Open Web UI API
- Model selection & chat completion
- Health: `/health`

Port: 12346 (Policy-bound, assigned)
Integration: Portier (kordp) via /dispatch/kordp
"""

import hashlib
import os
import socket
from datetime import datetime
from typing import Any

import httpx
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

# ────────────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────────────

PORT = 12346
COORDINATOR_PORT = 12344  # Portier (kordp)
ARCHIVP_PORT = 12345  # OpenA2 (Archivator)
SERVICE_NAME = "openwebui"
PROGRAM_TARGET = "openweb"

# Open Web UI Configuration
OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://localhost:8080")
OPENWEBUI_API_KEY = os.getenv("OPENWEBUI_API_KEY", "")
DEFAULT_MODEL = os.getenv("OPENWEBUI_DEFAULT_MODEL", "llama2")


def _key_fingerprint(secret: str) -> str:
    """Return non-reversible fingerprint (sha256/8)."""
    if not secret:
        return ""
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()[:8]


OPENWEBUI_PRESENT = bool(OPENWEBUI_API_KEY)
OPENWEBUI_FP = _key_fingerprint(OPENWEBUI_API_KEY)

REDACT_KEYS = {"authorization", "openwebui_api_key", "api_key", "token", "OPENWEBUI_API_KEY", "bearer", "key"}


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


class ChatCompletionIn(BaseModel):
    """Chat completion request."""

    model_config = ConfigDict(extra="forbid")
    model: str = Field(default=DEFAULT_MODEL)
    messages: list[dict[str, str]] = Field(...)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int | None = None
    strict: bool = True


class ModelListResponse(BaseModel):
    """Model list response."""

    models: list[str] = Field(...)
    available: int = Field(...)


# ────────────────────────────────────────────────────────────────────────
# FastAPI App
# ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=f"Open Web UI Gateway — {PROGRAM_TARGET.upper()}",
    description="Inference Gateway for Open Web UI",
    version="1.0.0",
)

# Statistics
STATS = {
    "completions_requested": 0,
    "tokens_processed": 0,
    "errors": 0,
}

APP_META = {
    "service": SERVICE_NAME,
    "program_target": PROGRAM_TARGET,
    "role": "inference_gateway",
    "host": _hostname(),
    "port": PORT,
    "coordinator_port": COORDINATOR_PORT,
    "archivp_port": ARCHIVP_PORT,
    "openwebui_url": OPENWEBUI_URL,
    "strict": True,
}


# ────────────────────────────────────────────────────────────────────────
# Helper: Store Safepoint
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
        "openwebui_present": OPENWEBUI_PRESENT,
        "openwebui_fp": OPENWEBUI_FP,
        "default_model": DEFAULT_MODEL,
        "stats": STATS,
        "status": "ok",
    }


@app.get("/models")
async def list_models() -> ModelListResponse:
    """List available models from Open Web UI."""
    # Mock response (replace with real API call if OpenWebUI is running)
    models = [DEFAULT_MODEL, "gpt-4", "claude-2", "mistral"]

    await _store_safepoint(
        "MODEL_LIST",
        {
            "models_count": len(models),
            "models": models,
        },
    )

    return ModelListResponse(models=models, available=len(models))


@app.post("/chat/completions")
async def chat_completion(req: ChatCompletionIn) -> dict[str, Any]:
    """Request chat completion from Open Web UI."""
    STATS["completions_requested"] += 1

    # Mock response (replace with real API call if OpenWebUI is running)
    completion = f"Mock response from {req.model}: processed {len(req.messages)} messages"

    await _store_safepoint(
        "COMPLETION",
        {
            "model": req.model,
            "messages_count": len(req.messages),
            "temperature": req.temperature,
        },
    )

    return {
        "ok": True,
        "model": req.model,
        "completion": completion,
        "tokens": len(completion.split()),
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
