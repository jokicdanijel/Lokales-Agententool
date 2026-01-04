"""
portier/main.py — Coordinator Gateway (kordp)
- Route Registration: `/route/update`
- Task Dispatch: `/dispatch/kordp`
- Health: `/health`

Port: 12344 (Policy-bound, fixed)
Integration: OpenA1 (same as opena1_app.py from Phase 7b)
"""

import hashlib
import os
import socket
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field

# Metrics Exporter (Phase 17 Monitoring)
# Note: metrics_exporter.py is in "19.opena20_dashboard_agent/" which starts with a digit,
# so we use importlib.util to load it instead of normal import
METRICS_ENABLED = False
try:
    import importlib.util

    metrics_path = (
        Path(__file__).resolve().parent.parent.parent.parent / "19.opena20_dashboard_agent" / "metrics_exporter.py"
    )
    spec = importlib.util.spec_from_file_location("metrics_exporter", metrics_path)
    if spec and spec.loader:
        metrics_module = importlib.util.module_from_spec(spec)  # type: ignore
        spec.loader.exec_module(metrics_module)  # type: ignore
        get_exporter = metrics_module.get_exporter
        METRICS_ENABLED = True
except Exception as e:
    print(f"⚠️  Metrics exporter not available: {e}")

# ────────────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────────────

PORT = 12344
ARCHIVP_PORT = 12345  # OpenA2 (Archivator)
SERVICE_NAME = "portier"
PROGRAM_TARGET = "kordp"

# OpenAI Environment (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_ORG = os.getenv("OPENAI_ORG", "")


def _key_fingerprint(secret: str) -> str:
    """Return non-reversible fingerprint (sha256/8)."""
    if not secret:
        return ""
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()[:8]


OPENAI_PRESENT = bool(OPENAI_API_KEY)
OPENAI_FP = _key_fingerprint(OPENAI_API_KEY)

REDACT_KEYS = {
    "authorization",
    "openai_api_key",
    "api_key",
    "openai-key",
    "x-api-key",
    "OPENAI_API_KEY",
    "OPENAI_ORG",
    "OPENAI_BASE_URL",
    "bearer",
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


class RouteUpdateIn(BaseModel):
    """Register a service route."""

    model_config = ConfigDict(extra="forbid")
    agent: str = Field(..., min_length=1)
    agent_id: str = Field(..., min_length=1)
    port: int = Field(..., ge=12344, le=12399)  # Port-Policy
    program: str = Field(..., min_length=1)
    archivator_port: int = Field(default=12345)
    mapping_ts: str = Field(default_factory=_now)
    mapping: dict[str, Any] = Field(default_factory=dict)
    strict: bool = True


class DispatchIn(BaseModel):
    """Dispatch a task to a service."""

    model_config = ConfigDict(extra="forbid")
    agent: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    data: dict[str, Any] = Field(default_factory=dict)
    request_id: str = Field(default_factory=lambda: f"req-{int(time.time()*1000)}")
    strict: bool = True


class LogEntryIn(BaseModel):
    """Log an event."""

    model_config = ConfigDict(extra="forbid")
    source: str = Field(..., min_length=1)
    event: str = Field(..., min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    strict: bool = True
    ts: str = Field(default_factory=_now)


# ────────────────────────────────────────────────────────────────────────
# FastAPI App
# ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=f"Portier — {PROGRAM_TARGET.upper()}",
    description="Coordinator Gateway for Multi-Agent Orchestration",
    version="1.0.0",
)

# In-memory route registry
ROUTES: dict[str, dict[str, Any]] = {}
APP_META = {
    "service": SERVICE_NAME,
    "program_target": PROGRAM_TARGET,
    "role": "coordinator",
    "host": _hostname(),
    "port": PORT,
    "archivp_port": ARCHIVP_PORT,
    "strict": True,
}


# ────────────────────────────────────────────────────────────────────────
# Startup Event: Initialize Metrics Exporter (Phase 17)
# ────────────────────────────────────────────────────────────────────────


@app.on_event("startup")
async def startup_metrics():
    """Initialize metrics exporter on app startup."""
    if METRICS_ENABLED:
        exporter = get_exporter()
        exporter.register_service("portier", 12344)
        exporter.register_service("opena2", 12345)
        exporter.register_service("telegram", 12346)
        exporter.register_service("inference", 12346)
        print("✅ Metrics exporter initialized (9090 metrics will be available)")


# ────────────────────────────────────────────────────────────────────────
# Helper: Store Safepoint (delegate to OpenA2)
# ────────────────────────────────────────────────────────────────────────


async def _store_safepoint(kind: str, body: dict[str, Any]) -> None:
    """Delegate safepoint storage to OpenA2 (/store/archivp)."""
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


# ────────────────────────────────────────────────────────────────────────
# Endpoints
# ────────────────────────────────────────────────────────────────────────


@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        **APP_META,
        "routes_count": len(ROUTES),
        "openai_key_present": OPENAI_PRESENT,
        "openai_fp": OPENAI_FP,
        "openai_base_url": OPENAI_BASE_URL,
        "status": "ok",
    }


@app.get("/metrics")
async def metrics() -> Response:
    """Prometheus metrics endpoint (Phase 17 Monitoring)."""
    if not METRICS_ENABLED:
        return Response("# Metrics not available (prometheus-client not installed)", media_type="text/plain")

    exporter = get_exporter()
    return Response(exporter.get_metrics_text(), media_type="text/plain")


@app.get("/api/health/metrics")
async def health_metrics() -> dict[str, Any]:
    """JSON health summary with metrics (Phase 17 Monitoring)."""
    if not METRICS_ENABLED:
        return {"error": "Metrics not available (prometheus-client not installed)"}

    exporter = get_exporter()
    return exporter.get_health_summary()


@app.post("/route/update")
async def route_update(info: RouteUpdateIn) -> dict[str, Any]:
    """Register or update a service route."""
    # Validate port policy
    if not (12344 <= info.port <= 12399):
        raise HTTPException(400, "PORT_POLICY_VIOLATION: port must be 12344-12399")

    # Store route in registry
    ROUTES[info.agent] = {
        "agent_id": info.agent_id,
        "port": info.port,
        "program": info.program,
        "archivator_port": info.archivator_port,
        "mapping_ts": info.mapping_ts,
    }

    # Log to archive
    await _store_safepoint(
        "ROUTE",
        {
            "agent": info.agent,
            "agent_id": info.agent_id,
            "port": info.port,
            "program": info.program,
        },
    )

    return {
        "ok": True,
        "route": ROUTES[info.agent],
        "strict": True,
    }


@app.post("/dispatch/kordp")
async def dispatch_task(req: DispatchIn) -> dict[str, Any]:
    """Dispatch a task to a registered service."""
    route: dict[str, Any] | None = ROUTES.get(req.agent)
    if not route:
        raise HTTPException(404, f"no route for agent '{req.agent}'")

    # Log dispatch to archive (redact sensitive data)
    safe_data = _redact_secrets(req.data)
    await _store_safepoint(
        "DISPATCH",
        {
            "request_id": req.request_id,
            "agent": req.agent,
            "action": req.action,
            "data": safe_data,
            "route": route,
        },
    )

    return {
        "ok": True,
        "routed_to": route,
        "request_id": req.request_id,
        "strict": True,
    }


@app.post("/log/portier")
async def log_event(entry: LogEntryIn) -> dict[str, Any]:
    """Log an event to archive."""
    await _store_safepoint("LOG", entry.model_dump())
    return {
        "ok": True,
        "logged": True,
        "strict": True,
    }


# ────────────────────────────────────────────────────────────────────────
# Entry Point
# ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=False, access_log=False, log_level="info")
