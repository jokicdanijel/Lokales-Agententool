#!/usr/bin/env python3
"""
opena3 – OpenWebUI Terminal Agent (Portier 3.0 – Upgrade Version)
-----------------------------------------------------------------

Funktion:
- Option-2-kompatibler Tool-Agent
- Safepoint-fähige Kommunikation über opena2
- Dispatcher-Routing über kordp
- Direkter Bridge-Adapter für OpenWebUI (Port 8080)
- Health, CMD, RESP, native /chat Interface
- Strikte Schemas & Token-Security

Port: 12347
Service Target: openwebui3
Version: 2.0 (Production Upgrade)
"""

import logging
import os
from datetime import UTC, datetime
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

# ============================================================================
# CONFIG
# ============================================================================
AGENT_ID = "opena3"
SERVICE_TARGET = "openwebui3"

PORT = 12347

OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://127.0.0.1:3000")
TIMEOUT = float(os.getenv("OPENWEBUI_TIMEOUT", "15.0"))

OPENA2_URL = os.getenv("OPENA2_URL", "http://127.0.0.1:12345")  # Safepoint handler
KORDP_URL = os.getenv("KORDP_URL", "http://127.0.0.1:12346")  # Dispatcher
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://127.0.0.1:12349")

BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")


# ============================================================================
# LOGGING
# ============================================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(AGENT_ID)


# ============================================================================
# MODELS
# ============================================================================


class CMD(BaseModel):
    """Envelope vom Coordinator → opena3"""

    model_config = ConfigDict(extra="forbid")
    request_id: str
    timestamp: str
    source: str
    command: str
    payload: dict[str, Any]


class RESP(BaseModel):
    """Envelope von opena3 → Archivator"""

    model_config = ConfigDict(extra="forbid")
    request_id: str
    timestamp: str
    agent: str
    result: dict[str, Any]


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int = 800


class ChatResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    response: str
    model: str | None
    timestamp: str
    usage: dict[str, int]


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agent_id: str
    status: str
    openwebui: bool
    timestamp: str


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="opena3 Terminal Agent – Portier 3.0 Upgrade",
    version="2.0",
    description="OpenWebUI Integration mit Safepoints & Dispatcher Routing",
)


# ============================================================================
# HELPER
# ============================================================================


async def openwebui_health() -> bool:
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{OPENWEBUI_URL}/health", timeout=TIMEOUT)
            return r.status_code == 200
    except:
        return False


async def call_openwebui(req: ChatRequest) -> dict[str, Any]:
    """OpenWebUI ansprechen"""
    try:
        payload = {
            "message": req.prompt,
            "model": req.model,
            "temperature": req.temperature,
            "max_tokens": req.max_tokens,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{OPENWEBUI_URL}/api/chat/completions", json=payload, timeout=TIMEOUT)

        if resp.status_code != 200:
            raise HTTPException(502, f"OpenWebUI Error {resp.status_code}")

        return resp.json()

    except Exception as e:
        logger.error(f"OpenWebUI error: {e}")
        raise HTTPException(503, "OpenWebUI unreachable")


async def safepoint(category: str, body: dict[str, Any]):
    """Safepoint zu opena2 schreiben"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{OPENA2_URL}/store/{category}",
                json=body,
                headers={"Authorization": f"Bearer {BEARER_TOKEN}"},
                timeout=10.0,
            )
    except Exception as e:
        logger.error(f"Safepoint error: {e}")


# ============================================================================
# ROUTES
# ============================================================================


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        agent_id=AGENT_ID,
        status="ok",
        openwebui=await openwebui_health(),
        timestamp=datetime.now(UTC).isoformat(),
    )


# ----------------------------------------------------------------------------
# NATIVE CHAT API
# ----------------------------------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not await openwebui_health():
        raise HTTPException(503, "OpenWebUI offline")

    data = await call_openwebui(req)

    return ChatResponse(
        response=data.get("message", ""),
        model=data.get("model"),
        timestamp=datetime.now(UTC).isoformat(),
        usage=data.get("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}),
    )


# ----------------------------------------------------------------------------
# CMD INTERFACE (Option-2 kompatibel)
# ----------------------------------------------------------------------------
@app.post("/cmd", response_model=RESP)
async def run_cmd(envelope: CMD):
    """
    Dies ist der offizielle Portier-Kanal:
    opena1 → CMD → opena3 → RESP → opena2
    """

    # Safepoint: CMD Eingang
    await safepoint("CMD", envelope.model_dump())

    if envelope.command != "chat":
        raise HTTPException(400, f"Unsupported command: {envelope.command}")

    req = ChatRequest(**envelope.payload)

    result = await call_openwebui(req)

    resp = RESP(request_id=envelope.request_id, timestamp=datetime.now(UTC).isoformat(), agent=AGENT_ID, result=result)

    # Safepoint: RESP Ausgang
    await safepoint("RESP", resp.model_dump())

    return resp


# ----------------------------------------------------------------------------
# DISPATCH INTERFACE (kordp)
# ----------------------------------------------------------------------------
@app.post("/dispatch", response_model=dict[str, Any])
async def dispatch(payload: dict[str, Any]):
    """
    dispatcher → opena3
    """
    if payload.get("service_target") != SERVICE_TARGET:
        raise HTTPException(400, "Incorrect service_target")

    params = payload.get("payload", {})
    req = ChatRequest(**params)

    data = await call_openwebui(req)

    return {
        "service": AGENT_ID,
        "target": SERVICE_TARGET,
        "result": data,
        "timestamp": datetime.now(UTC).isoformat(),
    }


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Starting opena3 v2.0 on port {PORT}")
    logger.info(f"🔗 OpenWebUI: {OPENWEBUI_URL}")

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
