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
from background_poller import on_startup as poller_startup, on_shutdown as poller_shutdown, set_registry

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
# Ermöglicht Anfragen von OpenWebUI (Port 8080) und Dashboard (Port 12349)
cors_origins = [
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://127.0.0.1:12349",
    "http://localhost:12349",
    "*"  # Für Entwicklung; in Production einschränken
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()
rate_limiter = RateLimiter(requests_per_minute=60)

# Komponenten
agent_registry = AgentRegistry()
sse_bus = SSEBus()

# ─ Startup/Shutdown Events ───────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Starte Background-Poller beim App-Start"""
    logger.info("Dashboard startup...")
    set_registry(agent_registry)
    await poller_startup()
    logger.info("Background-Poller started")


@app.on_event("shutdown")
async def shutdown_event():
    """Stoppe Background-Poller beim App-Shutdown"""
    logger.info("Dashboard shutdown...")
    await poller_shutdown()
    logger.info("Background-Poller stopped")

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
# Diagnostics
# -------------------------------------------------------------------
@app.get("/api/diagnostics/poller")
@rate_limiter.limit()
async def get_poller_status(token: HTTPAuthorizationCredentials = Security(security)):
    """Debug: Status des Background-Pollers"""
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, "/api/diagnostics/poller", ok)
    if not ok:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    from background_poller import get_status
    return {"poller": get_status()}

# -------------------------------------------------------------------
# Agent Registry API
# -------------------------------------------------------------------
@app.get("/api/agent/list")
@rate_limiter.limit()
async def list_agents(token: HTTPAuthorizationCredentials = Security(security)):
    """Alle registrierten Agenten aufzählen"""
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, "/api/agent/list", ok)
    if not ok:
        raise HTTPException(status_code=401, detail="Not authenticated")

    agents = agent_registry.get_all_agents()
    return {
        "strict": True,
        "count": len(agents),
        "agents": agents
    }
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
# JWT Token Management (Secure Agent Authentication)
# -------------------------------------------------------------------

@app.post("/api/agents/{agent_id}/token")
@rate_limiter.limit()
async def generate_agent_token(
    agent_id: str,
    token: HTTPAuthorizationCredentials = Security(security)
):
    """Generiere JWT Token für einen Agenten"""
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, f"/api/agents/{agent_id}/token", ok)
    if not ok:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        from jwt_auth import create_token
        jwt_token = create_token(
            agent_id=agent_id,
            scope="invoke",
            permissions=["read", "write"]
        )
        return {
            "agent_id": agent_id,
            "token": jwt_token,
            "token_type": "Bearer",
            "expires_in": 86400,  # 24h in seconds
            "scope": "invoke"
        }
    except Exception as e:
        logger.error(f"Token generation failed for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Token generation failed: {str(e)}")


@app.post("/api/auth/verify")
@rate_limiter.limit()
async def verify_jwt_token(payload: Dict, token: HTTPAuthorizationCredentials = Security(security)):
    """Validiere einen JWT Token (Admin-Only)"""
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, "/api/auth/verify", ok)
    if not ok:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        from jwt_auth import verify_token as verify_jwt
        token_to_verify = payload.get("token")
        if not token_to_verify:
            raise HTTPException(status_code=400, detail="'token' field required")
        
        result = verify_jwt(token_to_verify)
        return {
            "valid": result.is_valid,
            "agent_id": result.agent_id,
            "scope": result.scope,
            "permissions": result.permissions,
            "expires_at": result.exp,
            "error": result.error_type if not result.is_valid else None
        }
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@app.get("/api/agents/tokens/all")
@rate_limiter.limit()
async def get_all_agent_tokens(token: HTTPAuthorizationCredentials = Security(security)):
    """Generiere Tokens für ALLE registrierten Agenten (Admin-Only)"""
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, "/api/agents/tokens/all", ok)
    if not ok:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        from jwt_auth import create_token
        agents = agent_registry.get_all_agents()
        tokens = {}
        
        for agent_id in agents.keys():
            try:
                tokens[agent_id] = create_token(
                    agent_id=agent_id,
                    scope="invoke",
                    permissions=["read", "write"]
                )
            except Exception as e:
                logger.warning(f"Failed to create token for {agent_id}: {e}")
                tokens[agent_id] = None
        
        return {
            "count": len(tokens),
            "tokens": tokens,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Batch token generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")

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

