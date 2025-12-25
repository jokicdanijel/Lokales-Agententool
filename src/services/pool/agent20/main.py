#!/usr/bin/env python3
"""
Agent20 — Pool Service (Port 12369)
Skalierbare Service-Instanz basierend auf Generic Template
"""

import os
from datetime import UTC, datetime
from socket import gethostname
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

# ────────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────────

SERVICE_NAME = os.getenv("SERVICE_NAME", "agent20")
PROGRAM_TARGET = os.getenv("PROGRAM_TARGET", "agent20p")
PORT = int(os.getenv("PORT", "12369"))
COORDINATOR_PORT = 12344
ARCHIVP_PORT = 12345
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

security = HTTPBearer()

# Stats
STATS = {
    "requests_received": 0,
    "actions_processed": 0,
    "errors": 0,
}

# ────────────────────────────────────────────────────────────────────
# Models
# ────────────────────────────────────────────────────────────────────


class ActionRequest(BaseModel):
    """Action request model."""

    action: str = Field(..., description="Action name")
    params: dict[str, Any] = Field(default_factory=dict, description="Action parameters")

    class Config:
        extra = "forbid"


class EchoRequest(BaseModel):
    """Echo request model."""

    msg: str = Field(..., description="Message to echo")

    class Config:
        extra = "forbid"


class HealthResponse(BaseModel):
    """Health response model."""

    status: str
    service: str
    program_target: str
    port: int
    stats: dict[str, Any]
    timestamp: str


# ────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────


def _hostname() -> str:
    """Get hostname."""
    try:
        return gethostname()
    except Exception:
        return "unknown"


def _now() -> str:
    """Current timestamp (ISO 8601 UTC)."""
    return datetime.now(UTC).isoformat()


async def _store_safepoint(kind: str, body: dict[str, Any]) -> None:
    """Store safepoint via OpenA2 (archivp)."""
    url = f"http://127.0.0.1:{ARCHIVP_PORT}/store/archivp"
    payload = {"src": PROGRAM_TARGET, "dst": "archivp", "kind": kind, "body": body, "strict": True, "ts": _now()}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(url, json=payload)
    except Exception as e:
        print(f"⚠️  Safepoint storage failed: {e}")
        STATS["errors"] += 1


def _verify_token(credentials: HTTPAuthorizationCredentials) -> None:
    """Verify bearer token."""
    if BEARER_TOKEN and credentials.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid bearer token")


# ────────────────────────────────────────────────────────────────────
# FastAPI App
# ────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=f"{SERVICE_NAME.upper()} — {PROGRAM_TARGET}", description="Pool Service Agent20 (Port 12369)", version="1.0.0"
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint (no auth required)."""
    STATS["requests_received"] += 1

    await _store_safepoint(
        "HEALTH",
        {
            "service": SERVICE_NAME,
            "port": PORT,
            "hostname": _hostname(),
        },
    )

    return HealthResponse(
        status="healthy", service=SERVICE_NAME, program_target=PROGRAM_TARGET, port=PORT, stats=STATS, timestamp=_now()
    )


@app.post("/echo")
async def echo(req: EchoRequest, credentials: HTTPAuthorizationCredentials = Security(security)) -> dict[str, Any]:
    """Echo endpoint (auth required)."""
    _verify_token(credentials)
    STATS["requests_received"] += 1

    await _store_safepoint(
        "ECHO",
        {
            "msg": req.msg,
            "service": SERVICE_NAME,
        },
    )

    return {
        "status": "success",
        "service": SERVICE_NAME,
        "program_target": PROGRAM_TARGET,
        "echo": req.msg,
        "timestamp": _now(),
    }


@app.post("/action")
async def action(req: ActionRequest, credentials: HTTPAuthorizationCredentials = Security(security)) -> dict[str, Any]:
    """Generic action endpoint (auth required)."""
    _verify_token(credentials)
    STATS["requests_received"] += 1
    STATS["actions_processed"] += 1

    await _store_safepoint(
        "ACTION",
        {
            "action": req.action,
            "params": req.params,
        },
    )

    # Simulate action processing
    result = {
        "status": "success",
        "service": SERVICE_NAME,
        "action": req.action,
        "result": f"Action '{req.action}' processed successfully by {PROGRAM_TARGET}",
        "params_received": req.params,
        "timestamp": _now(),
    }

    return result


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint with service info."""
    return {
        "service": SERVICE_NAME,
        "program_target": PROGRAM_TARGET,
        "port": PORT,
        "status": "online",
        "endpoints": {"health": "/health", "echo": "POST /echo", "action": "POST /action"},
    }


# ────────────────────────────────────────────────────────────────────
# Entry Point
# ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    print(f"🚀 Starting {SERVICE_NAME} ({PROGRAM_TARGET}) on port {PORT}")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=PORT,
        reload=False,
        access_log=True,
    )
