"""
OpenWebUI Adapter – Relay-Modul für lokale OpenWebUI-Instanz (Port 8080)

Bietet FastAPI-Endpunkte für Weiterleitungen zu OpenWebUI.
"""

import logging
import os
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ============================================================================
# LOGGING SETUP
# ============================================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# ============================================================================
# KONFIGURATION
# ============================================================================
OPENWEBUI_BASE_URL = os.getenv("OPENWEBUI_URL", "http://127.0.0.1:8080")
OPENWEBUI_TIMEOUT = int(os.getenv("OPENWEBUI_TIMEOUT", "10"))  # Sekunden
ADAPTER_PORT = int(os.getenv("ADAPTER_PORT", "12350"))

# ============================================================================
# MODELS
# ============================================================================


class ChatRequest(BaseModel):
    """Chat-Request für OpenWebUI"""

    prompt: str
    context: dict[str, Any] = {}


class HealthResponse(BaseModel):
    """Health-Response"""

    status: str
    service: str = "openwebui_adapter"


# ============================================================================
# FASTAPI APP
# ============================================================================
app = FastAPI(title="OpenWebUI Adapter", description="Relay-Adapter für OpenWebUI-Integration", version="1.0.0")


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health-Check für Adapter"""
    try:
        resp = requests.get(f"{OPENWEBUI_BASE_URL}/health", timeout=OPENWEBUI_TIMEOUT)
        if resp.status_code == 200:
            return HealthResponse(status="ok")
        else:
            return HealthResponse(status="openwebui_unreachable")
    except (requests.Timeout, requests.ConnectionError) as e:
        logger.warning(f"OpenWebUI health check failed: {e}")
        return HealthResponse(status="openwebui_unreachable")
    except Exception as e:
        logger.error(f"Unexpected error in health check: {e}")
        return HealthResponse(status="error")


@app.get("/openwebui/health")
async def openwebui_health():
    """Proxy: GET /health von OpenWebUI"""
    try:
        resp = requests.get(f"{OPENWEBUI_BASE_URL}/health", timeout=OPENWEBUI_TIMEOUT)
        return resp.json()
    except requests.Timeout as e:
        logger.error(f"OpenWebUI health timeout: {e}")
        raise HTTPException(status_code=502, detail=f"OpenWebUI timeout after {OPENWEBUI_TIMEOUT}s")
    except requests.ConnectionError as e:
        logger.error(f"OpenWebUI connection error: {e}")
        raise HTTPException(status_code=502, detail="Cannot connect to OpenWebUI (ConnectionError)")
    except Exception as e:
        logger.error(f"Unexpected error proxying health: {e}")
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/openwebui/chat")
async def openwebui_chat(req: ChatRequest):
    """
    Proxy: POST /api/chat an OpenWebUI.

    Erwartet: {"prompt": "...", "context": {...}}
    Gibt JSON-Response von OpenWebUI zurück.
    """
    try:
        payload = {"prompt": req.prompt, "context": req.context}
        resp = requests.post(f"{OPENWEBUI_BASE_URL}/api/chat", json=payload, timeout=OPENWEBUI_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.Timeout as e:
        logger.error(f"OpenWebUI chat timeout: {e}")
        raise HTTPException(status_code=502, detail=f"OpenWebUI timeout after {OPENWEBUI_TIMEOUT}s")
    except requests.ConnectionError as e:
        logger.error(f"OpenWebUI connection error: {e}")
        raise HTTPException(status_code=502, detail="Cannot connect to OpenWebUI (ConnectionError)")
    except requests.HTTPError as e:
        logger.error(f"OpenWebUI HTTP error: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=f"OpenWebUI error: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(status_code=502, detail=str(e))


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting OpenWebUI Adapter on port {ADAPTER_PORT}")
    logger.info(f"OpenWebUI base URL: {OPENWEBUI_BASE_URL}")
    uvicorn.run(app, host="127.0.0.1", port=ADAPTER_PORT, log_level="info")
