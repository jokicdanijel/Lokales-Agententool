"""
src/services/openwebui/service.py
OpenA3: OpenWebUI Agent (openweb)
Port: 12346 (Policy 12344-12349)
Endpunkte: /health, /openwebui/ping, /openwebui/call
Startup: Registriere Route bei OpenA1 + Safepoint bei OpenA2
"""
from __future__ import annotations

import asyncio
import os
import time
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
import httpx

PORT = 12346
OPENA1 = "http://127.0.0.1:12344"
OPENA2 = "http://127.0.0.1:12345"

app = FastAPI(title="OpenA3 OpenWebUI (openweb)", version="1.0.0")

REDACT_KEYS = {
    "authorization", "openai_api_key", "api_key", "openai-key", "x-api-key",
    "bearer", "openai_org", "openai_base_url"
}


def _now() -> str:
    """ISO 8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat() + "Z"


def _redact(obj: Any) -> Any:
    """Redact secrets recursively."""
    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for k, v in obj.items():
            kl = str(k).lower()
            if kl in REDACT_KEYS or "token" in kl or "secret" in kl or "key" in kl:
                out[k] = "***REDACTED***"
            else:
                out[k] = _redact(v)
        return out
    if isinstance(obj, list):
        return [_redact(x) for x in obj]
    return obj


async def _route_register() -> None:
    """Register this agent at OpenA1 + write ROUTE safepoint to OpenA2."""
    payload = {
        "agent": "openwebui",
        "agent_id": "opena3",
        "port": PORT,
        "program": "openweb",
        "archivator_port": 12345,
        "mapping_ts": _now(),
        "mapping": {}
    }
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Register route at OpenA1
            r = await client.post(f"{OPENA1}/route/update", json=payload)
            r.raise_for_status()
            
            # Write ROUTE safepoint to OpenA2
            sp = {
                "src": "openweb",
                "dst": "archivp",
                "kind": "ROUTE",
                "body": payload,
                "strict": True
            }
            await client.post(f"{OPENA2}/store/archivp", json=_redact(sp))
    except Exception as e:
        print(f"⚠️  Route registration failed: {e}")


@app.on_event("startup")
async def startup():
    """Startup: register route."""
    await _route_register()


@app.get("/health")
async def health() -> Dict[str, Any]:
    """Health check."""
    return {
        "status": "ok",
        "component": "openwebui",
        "port": PORT,
        "service": "opena3",
        "program_target": "openweb",
        "strict": True
    }


@app.get("/openwebui/ping")
async def ping() -> Dict[str, Any]:
    """Ping endpoint."""
    return {
        "ok": True,
        "pong": "openweb",
        "ts": _now(),
        "strict": True
    }


@app.post("/openwebui/call")
async def call(body: Dict[str, Any]) -> Dict[str, Any]:
    """Call endpoint: process action (prompt)."""
    action = body.get("action")
    data = body.get("data", {})
    
    if action != "prompt":
        raise HTTPException(400, "unsupported action")
    
    # Prepare payload for archivation (redacted)
    payload = {
        "action": action,
        "data": _redact(data)
    }
    
    # Write CALL safepoint to OpenA2
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            sp = {
                "src": "openweb",
                "dst": "archivp",
                "kind": "CALL",
                "body": payload,
                "strict": True
            }
            await client.post(f"{OPENA2}/store/archivp", json=sp)
    except Exception as e:
        print(f"⚠️  Safepoint write failed: {e}")
    
    # Echo response (text from data without secrets)
    return {
        "ok": True,
        "echo": data.get("text", ""),
        "strict": True
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.services.openwebui.service:app",
        host="127.0.0.1",
        port=PORT,
        reload=False,
        access_log=False
    )
