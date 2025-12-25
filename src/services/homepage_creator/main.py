#!/usr/bin/env python3
"""
Generic Service Template — Reusable for all scalable services
- Health checks, safepoint logging, echo endpoints
- Zero-config deployment: PORT + SERVICE_NAME env variables
"""

import os
from datetime import datetime
from socket import gethostname
from typing import Any

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

# ────────────────────────────────────────────────────────────────────
# Configuration (from environment)
# ────────────────────────────────────────────────────────────────────

SERVICE_NAME = os.getenv("SERVICE_NAME", "homepage_creator")
PROGRAM_TARGET = os.getenv("PROGRAM_TARGET", "svc")
PORT = int(os.getenv("PORT", "12358"))
COORDINATOR_PORT = 12344
ARCHIVP_PORT = 12345

# Stats
STATS = {
    "requests_received": 0,
    "errors": 0,
}


# ────────────────────────────────────────────────────────────────────
# Models
# ────────────────────────────────────────────────────────────────────


class EchoRequest(BaseModel):
    """Echo request."""

    msg: str


class HealthResponse(BaseModel):
    """Health response."""

    status: str
    service: str
    program_target: str
    port: int
    stats: dict[str, Any]


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
    """Current timestamp (ISO 8601)."""
    return datetime.utcnow().isoformat() + "Z"


async def _store_safepoint(kind: str, body: dict[str, Any]) -> None:
    """Delegate safepoint storage to OpenA2."""
    url = f"http://127.0.0.1:{ARCHIVP_PORT}/store/archivp"
    payload = {"src": PROGRAM_TARGET, "dst": "archivp", "kind": kind, "body": body, "strict": True, "ts": _now()}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(url, json=payload)
    except Exception as e:
        print(f"⚠️  Safepoint failed: {e}")
        STATS["errors"] += 1


# ────────────────────────────────────────────────────────────────────
# FastAPI App
# ────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=f"{SERVICE_NAME} — {PROGRAM_TARGET}", description="Generic scalable service template", version="1.0.0"
)


@app.get("/health")
async def health() -> HealthResponse:
    """Health check."""
    STATS["requests_received"] += 1

    await _store_safepoint(
        "HEALTH",
        {
            "service": SERVICE_NAME,
            "port": PORT,
            "timestamp": _now(),
        },
    )

    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        program_target=PROGRAM_TARGET,
        port=PORT,
        stats=STATS,
    )


@app.post("/echo")
async def echo(req: EchoRequest) -> dict[str, Any]:
    """Echo endpoint for testing."""
    STATS["requests_received"] += 1

    await _store_safepoint(
        "ECHO",
        {
            "msg": req.msg,
            "echo_time": _now(),
        },
    )

    return {
        "ok": True,
        "service": SERVICE_NAME,
        "program_target": PROGRAM_TARGET,
        "echo": req.msg,
        "timestamp": _now(),
        "strict": True,
    }


@app.post("/action")
async def action(payload: dict[str, Any]) -> dict[str, Any]:
    """Generic action endpoint."""
    STATS["requests_received"] += 1

    action_name = payload.get("action", "unknown")

    await _store_safepoint(
        "ACTION",
        {
            "action": action_name,
            "payload": payload,
        },
    )

    return {
        "ok": True,
        "service": SERVICE_NAME,
        "action": action_name,
        "result": f"Action '{action_name}' processed by {PROGRAM_TARGET}",
        "strict": True,
    }


# ────────────────────────────────────────────────────────────────────
# Entry Point
# ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=PORT,
        reload=False,
        access_log=False,
    )
