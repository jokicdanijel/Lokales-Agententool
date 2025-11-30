#!/usr/bin/env python3
"""
OpenWebUI Terminal Agent (opena3)
ELION Hyper-Dashboard 2.0 Integration

Agent-Zweck:
- Direkte Terminal-Schnittstelle zu OpenWebUI (Port 8080)
- Chat-Routing
- Health-Check
- Standardisiertes Command-Interface für Portier 3.0
- Keine Abhängigkeit zu opena1/opena2

Port: 12347
Version: 1.1 (clean, portier-konform)
"""

import os
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict


# ============================================================================
# KONFIGURATION
# ============================================================================
AGENT_ID = "opena3"
PORT = 12347

OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://127.0.0.1:8080")
TIMEOUT = float(os.getenv("OPENWEBUI_TIMEOUT", "15.0"))


# ============================================================================
# LOGGING
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(AGENT_ID)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================
class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 800


class ChatResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    response: str
    model: Optional[str]
    timestamp: str
    usage: Dict[str, int]


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    service: str
    status: str
    timestamp: str


# ============================================================================
# FASTAPI APP
# ============================================================================
app = FastAPI(
    title="OpenWebUI Terminal Agent (opena3)",
    version="1.1",
    description="Portier 3.0 – direkter OpenWebUI-Terminaladapter"
)


# ============================================================================
# HELFERFUNKTIONS
# ============================================================================
async def openwebui_health() -> bool:
    """Prüft OpenWebUI-Verfügbarkeit (Port 8080)."""
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{OPENWEBUI_URL}/health", timeout=TIMEOUT)
            return res.status_code == 200
    except:
        return False


async def call_openwebui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Sendet Chat-Prompt an OpenWebUI."""
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{OPENWEBUI_URL}/api/chat/completions",
                json=payload,
                timeout=TIMEOUT
            )
        if res.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"OpenWebUI Error {res.status_code}"
            )
        return res.json()

    except Exception as e:
        logger.error(f"OpenWebUI Request Error: {e}")
        raise HTTPException(status_code=502, detail="OpenWebUI not reachable")


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health-Endpoint für Dashboard & Supervisor."""
    return HealthResponse(
        service=AGENT_ID,
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Chat-Entry: Direkter Prompt → OpenWebUI."""
    if not await openwebui_health():
        raise HTTPException(status_code=503, detail="OpenWebUI offline")

    payload = {
        "message": req.prompt,
        "model": req.model,
        "temperature": req.temperature,
        "max_tokens": req.max_tokens
    }

    data = await call_openwebui(payload)

    return ChatResponse(
        response=data.get("message", ""),
        model=data.get("model"),
        timestamp=datetime.now(timezone.utc).isoformat(),
        usage=data.get("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
    )


@app.post("/command", response_model=Dict[str, Any])
async def command(payload: Dict[str, Any]):
    """
    Portier-kompatibles Command-Interface:
    {
      "command": "chat",
      "params": { "prompt": "Hello" }
    }
    """
    cmd = payload.get("command")

    if cmd == "chat":
        params = payload.get("params", {})
        req = ChatRequest(**params)
        return await chat(req)

    if cmd == "health":
        return (await health()).model_dump()

    return {
        "error": f"Unknown command: {cmd}",
        "available": ["chat", "health"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ============================================================================
# MAIN / UVICORN
# ============================================================================
if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Starting {AGENT_ID} on port {PORT}")
    logger.info(f"🔗 OpenWebUI URL: {OPENWEBUI_URL}")
    logger.info(f"⏱️ Timeout: {TIMEOUT}s")

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")