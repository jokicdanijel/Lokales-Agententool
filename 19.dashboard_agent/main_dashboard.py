"""
ELION Hyper-Dashboard 2.0 - Hauptmodul
FastAPI-Backend mit Agent-Registry, Status, SSE und sicherer Authentifizierung.
Kompatibilität: /api/agent/register (neu) und /api/command/register (legacy-alias).
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Security, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sse_starlette.sse import EventSourceResponse
from datetime import datetime

from agent_registry import AgentRegistry
from sse_bus import SSEBus
from security import verify_token, RateLimiter, security_log

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "dashboard_runtime.log"),
        logging.StreamHandler()
    ],
)
logger = logging.getLogger("dashboard")

# -------------------------------------------------------------------
# App + Security
# -------------------------------------------------------------------
app = FastAPI(
    title="ELION Hyper-Dashboard 2.0",
    description="Dashboard-Backend (Option 2)",
    version="1.0",
)

# CORS (lokal offen — bei Bedarf einschränken)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

security = HTTPBearer()
rate_limiter = RateLimiter(requests_per_minute=60)

# Komponenten
agent_registry = AgentRegistry()
sse_bus = SSEBus()

# -------------------------------------------------------------------
# Middleware: Port-Policy (nur Dashboard-Eingang kontrollieren)
# -------------------------------------------------------------------
@app.middleware("http")
async def validate_port_policy(request: Request, call_next):
    port = request.url.port
    # Wenn kein Port (selten), einfach durchlassen
    if port is None:
        return await call_next(request)

    if port == 8080:
        logger.error("Port 8080 ist verboten!")
        raise HTTPException(status_code=403, detail="Port 8080 ist verboten")

    if not (12344 <= port <= 12399 or port == 8000):
        # 8000 erlauben, falls lokal getestet wird
        logger.error(f"Port {port} außerhalb des erlaubten Bereichs")
        raise HTTPException(status_code=403, detail="Port muss zwischen 12344 und 12399 liegen")

    return await call_next(request)

# -------------------------------------------------------------------
# Health
# -------------------------------------------------------------------
@app.get("/health")
async def health_check():
    return {
        "service": "opena19",
        "status": "healthy",
        "strict": True,
        "timestamp": datetime.utcnow().isoformat()
    }

# -------------------------------------------------------------------
# Agent Registry API
# -------------------------------------------------------------------
@app.get("/api/status/all")
@rate_limiter.limit()
async def get_all_status(token: HTTPAuthorizationCredentials = Security(security)):
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, "/api/status/all", ok)
    if not ok:
        raise HTTPException(status_code=401, detail="Not authenticated")

    agents_status = await agent_registry.get_all_status()
    return {
        "strict": True,
        "agents": agents_status
    }

@app.get("/api/status/{agent_id}")
@rate_limiter.limit()
async def get_agent_status(agent_id: str, token: HTTPAuthorizationCredentials = Security(security)):
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, f"/api/status/{agent_id}", ok)
    if not ok:
        raise HTTPException(status_code=401, detail="Not authenticated")

    status = await agent_registry.get_agent_status(agent_id)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} nicht gefunden")

    return {"strict": True, "agent": agent_id, "status": status}

@app.post("/api/agent/register")
@rate_limiter.limit()
async def register_agent(payload: Dict, token: HTTPAuthorizationCredentials = Security(security)):
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, "/api/agent/register", ok)
    if not ok:
        raise HTTPException(status_code=401, detail="Not authenticated")

    agent_id = payload.get("agent_id")
    endpoint = payload.get("endpoint")
    if not agent_id or not endpoint:
        raise HTTPException(status_code=400, detail="agent_id und endpoint sind erforderlich")

    await agent_registry.register(agent_id, endpoint)
    await sse_bus.publish({"event": "agent_registered", "data": {"agent": agent_id, "endpoint": endpoint}})

    return {
        "strict": True,
        "agent": agent_id,
        "endpoint": endpoint,
        "registered_at": datetime.utcnow().isoformat() + "Z"
    }

# --- Legacy-Kompatibilität: alter falscher Aufruf /api/command/register ----------------
@app.post("/api/command/register")
@rate_limiter.limit()
async def legacy_register_alias(payload: Dict, token: HTTPAuthorizationCredentials = Security(security)):
    # Viele alte Skripte riefen fälschlich /api/command/register auf.
    # Wir leiten kompatibel auf /api/agent/register um.
    return await register_agent(payload, token)

# -------------------------------------------------------------------
# OpenWebUI Integration (opena3)
# -------------------------------------------------------------------
@app.get("/api/openwebui/status")
@rate_limiter.limit()
async def get_openwebui_status(token: HTTPAuthorizationCredentials = Security(security)):
    """Abfrage der Gesundheit des OpenWebUI-Agenten (opena3)"""
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, "/api/openwebui/status", ok)
    if not ok:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        import requests
        response = requests.get("http://127.0.0.1:12347/health", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"OpenWebUI Status error: {e}")
        raise HTTPException(status_code=502, detail="OpenWebUI Agent nicht erreichbar")


@app.post("/api/openwebui/chat")
@rate_limiter.limit()
async def openwebui_chat(payload: Dict, token: HTTPAuthorizationCredentials = Security(security)):
    """Leite Chat-Anfrage an OpenWebUI-Agenten weiter"""
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, "/api/openwebui/chat", ok)
    if not ok:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        import requests
        response = requests.post(
            "http://127.0.0.1:12347/command",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        await sse_bus.publish({"event": "openwebui_chat", "data": {"prompt": payload.get("prompt")}})
        return result
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="OpenWebUI timeout")
    except Exception as e:
        logger.error(f"OpenWebUI Chat error: {e}")
        raise HTTPException(status_code=502, detail="OpenWebUI Agent Fehler")

# -------------------------------------------------------------------
# Server Sent Events
# -------------------------------------------------------------------
@app.get("/api/events/live")
async def event_stream(request: Request):
    async def event_generator():
        async for event in sse_bus.subscribe():
            if await request.is_disconnected():
                break
            yield {
                "event": event.get("event", "message"),
                "data": json.dumps(event.get("data", {})),
                "retry": 3000
            }
    return EventSourceResponse(event_generator())

# -------------------------------------------------------------------
# Einfache UI-Routen (optional; Templates können später ergänzt werden)
# -------------------------------------------------------------------
@app.get("/ui/")
async def dashboard_ui():
    html = """<!doctype html><html><head><meta charset="utf-8"><title>Dashboard</title></head>
<body><h1>ELION Hyper-Dashboard</h1><p>API läuft. Verwende /api/status/all mit Bearer Token.</p></body></html>"""
    return HTMLResponse(html)

@app.get("/agent/{agent_id}")
async def agent_ui(agent_id: str):
    status = agent_registry.get_agent_status(agent_id)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} nicht gefunden")
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Agent {agent_id}</title></head>
<body><h2>Agent {agent_id}</h2><pre>{json.dumps(status, indent=2, ensure_ascii=False)}</pre></body></html>"""
    return HTMLResponse(html)

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    # Port aus Datei zulassen, sonst fallback 12349
    runtime_port_file = Path(".runtime/port")
    if runtime_port_file.exists():
        port = int(runtime_port_file.read_text().strip())
    else:
        port = 12349

    uvicorn.run(
        "main_dashboard:app",
        host="127.0.0.1",
        port=port,
        reload=True
    )

