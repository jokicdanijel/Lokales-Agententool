"""
OpenWebUI Adapter – Weiterleitung von Chat-Anfragen an OpenWebUI-Instanz (Port 8080)
"""

from fastapi import FastAPI, HTTPException
import requests
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

OPENWEBUI_URL = "http://127.0.0.1:8080"
TIMEOUT = 30


@app.get("/health")
async def health():
    """Health check für den Adapter"""
    return {"service": "openwebui_adapter", "status": "ok"}


@app.post("/openwebui/chat")
async def chat(request: dict):
    """
    Leitet Chat-Anfrage an OpenWebUI weiter
    
    Erwartet: {"prompt": "...", "context": {...}}
    Gibt zurück: JSON von OpenWebUI
    """
    try:
        prompt = request.get("prompt", "")
        context = request.get("context", {})
        
        if not prompt:
            raise HTTPException(status_code=400, detail="prompt erforderlich")
        
        # POST an OpenWebUI
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
        return response.json()
        
    except requests.Timeout:
        logger.error("OpenWebUI Timeout")
        raise HTTPException(status_code=502, detail="OpenWebUI nicht erreichbar (Timeout)")
    except requests.ConnectionError:
        logger.error("OpenWebUI ConnectionError")
        raise HTTPException(status_code=502, detail="OpenWebUI nicht erreichbar")
    except Exception as e:
        logger.error(f"Fehler bei OpenWebUI-Aufruf: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/openwebui/health")
async def openwebui_health():
    """Prüfe Gesundheit der OpenWebUI-Instanz"""
    try:
        response = requests.get(
            f"{OPENWEBUI_URL}/health",
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"OpenWebUI nicht erreichbar: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=12350)
