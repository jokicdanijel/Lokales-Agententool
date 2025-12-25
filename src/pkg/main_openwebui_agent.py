"""
OpenWebUI Agent (opena3) – FastAPI-Agent für OpenWebUI Integration

Dieser Agent läuft auf Port 12347 und koordiniert Anfragen
an die lokale OpenWebUI-Instanz (Port 8080).
"""

import logging
import os
from datetime import datetime
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ============================================================================
# LOGGING
# ============================================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# ============================================================================
# KONFIGURATION
# ============================================================================
OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://127.0.0.1:8080")
OPENWEBUI_TIMEOUT = int(os.getenv("OPENWEBUI_TIMEOUT", "15"))
AGENT_PORT = int(os.getenv("OPENWEBUI_AGENT_PORT", "12347"))
SERVICE_NAME = "opena3"

# ============================================================================
# MODELS
# ============================================================================


class HealthResponse(BaseModel):
    """Health-Response für opena3"""

    service: str
    status: str
    ts: str


class CommandRequest(BaseModel):
    """Command-Request an opena3"""

    prompt: str
    context: dict[str, Any] = {}
    model: str | None = None


class CommandResponse(BaseModel):
    """Command-Response von opena3"""

    text: str
    model: str | None = None
    ts: str


# ============================================================================
# FASTAPI APP
# ============================================================================
app = FastAPI(title="OpenWebUI Agent (opena3)", description="Agent für OpenWebUI-Integration", version="1.0.0")


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """
    Health-Check für opena3

    Returns:
        HealthResponse mit Status und ISO-Timestamp
    """
    return HealthResponse(service=SERVICE_NAME, status="ok", ts=datetime.utcnow().isoformat() + "Z")


@app.post("/command", response_model=CommandResponse)
async def execute_command(req: CommandRequest) -> CommandResponse:
    """
    Execute command via OpenWebUI.

    Nimmt einen Prompt an und ruft OpenWebUI API auf.

    Args:
        req: CommandRequest mit prompt, context, optional model

    Returns:
        CommandResponse mit text, model, timestamp

    Raises:
        HTTPException (502): Bei Verbindungsfehler zu OpenWebUI
        HTTPException (500): Bei unerwarteten Fehlern
    """
    try:
        # Payload für OpenWebUI zusammenstellen
        payload = {"prompt": req.prompt, "context": req.context}
        if req.model:
            payload["model"] = req.model

        # Request an OpenWebUI
        logger.info(f"Calling OpenWebUI with prompt: {req.prompt[:50]}...")
        resp = requests.post(f"{OPENWEBUI_URL}/api/chat", json=payload, timeout=OPENWEBUI_TIMEOUT)
        resp.raise_for_status()

        # Response parsen
        data = resp.json()
        text = data.get("text") or data.get("response") or str(data)
        model = data.get("model") or req.model

        logger.info(f"OpenWebUI response received (model: {model})")
        return CommandResponse(text=text, model=model, ts=datetime.utcnow().isoformat() + "Z")

    except requests.Timeout as e:
        logger.error(f"OpenWebUI timeout: {e}")
        raise HTTPException(status_code=502, detail=f"OpenWebUI timeout after {OPENWEBUI_TIMEOUT}s")
    except requests.ConnectionError as e:
        logger.error(f"OpenWebUI connection error: {e}")
        raise HTTPException(status_code=502, detail="Cannot connect to OpenWebUI")
    except requests.HTTPError as e:
        logger.error(f"OpenWebUI HTTP error: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"OpenWebUI error: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/invoke")
async def invoke(payload: dict[str, Any]):
    """
    Invoke endpoint (kompatibel mit anderen Agenten).

    Erwartet: {"prompt": "...", "context": {...}}
    Gibt zurück: JSON-Response
    """
    try:
        prompt = payload.get("prompt") or payload.get("msg", "")
        if not prompt:
            raise HTTPException(status_code=400, detail="prompt erforderlich")

        context = payload.get("context", {})
        model = payload.get("model")

        cmd_req = CommandRequest(prompt=prompt, context=context, model=model)
        return await execute_command(cmd_req)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in invoke: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting {SERVICE_NAME} on port {AGENT_PORT}")
    logger.info(f"OpenWebUI URL: {OPENWEBUI_URL}")
    logger.info(f"OpenWebUI timeout: {OPENWEBUI_TIMEOUT}s")

    uvicorn.run(app, host="127.0.0.1", port=AGENT_PORT, log_level="info")
