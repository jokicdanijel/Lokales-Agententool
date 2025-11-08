"""
OpenWebUI Agent (opena3) – Wrapper für OpenWebUI mit Health-Check und Command-Processing
"""

from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
import requests
import os
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://127.0.0.1:8080")
TIMEOUT = 30


@app.get("/health")
async def health():
    """Health check für den OpenWebUI-Agenten"""
    return {
        "service": "opena3",
        "status": "ok",
        "ts": datetime.now(timezone.utc).isoformat()
    }


@app.post("/command")
async def command(request: dict):
    """
    Verarbeite Command über OpenWebUI
    
    Erwartet: {"prompt": "...", "context": {...}}
    Gibt zurück: {"response": "...", "ts": ISO}
    """
    try:
        prompt = request.get("prompt", "")
        context = request.get("context", {})
        
        if not prompt:
            raise HTTPException(status_code=400, detail="prompt erforderlich")
        
        # POST an OpenWebUI API
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            **context
        }
        
        response = requests.post(
            f"{OPENWEBUI_URL}/api/chat",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json()
        
        return {
            "response": result,
            "ts": datetime.now(timezone.utc).isoformat()
        }
        
    except requests.Timeout:
        logger.error("OpenWebUI Timeout")
        raise HTTPException(status_code=502, detail="OpenWebUI nicht erreichbar (Timeout)")
    except requests.ConnectionError:
        logger.error("OpenWebUI ConnectionError")
        raise HTTPException(status_code=502, detail="OpenWebUI nicht erreichbar")
    except Exception as e:
        logger.error(f"Fehler bei Command-Verarbeitung: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/invoke")
async def invoke(payload: dict):
    """FastAPI-Standard Invoke-Endpunkt (für Dashboard-Integration)"""
    return await command(payload)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "12347"))
    uvicorn.run(app, host="0.0.0.0", port=port)
