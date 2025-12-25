"""
ELION Hyper-Dashboard 2.0 - Hauptmodul
FastAPI-Backend mit Agent-Registry, Status, SSE und sicherer Authentifizierung.
Kompatibilität: /api/agent/register (neu) und /api/command/register (legacy-alias).
Tracing: OpenTelemetry Integration für Multi-Agent Workflow Visualization
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

from agent_registry import AgentRegistry
from background_poller import on_shutdown as poller_shutdown
from background_poller import on_startup as poller_startup
from background_poller import set_registry
from fastapi import FastAPI, HTTPException, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from security import RateLimiter, security_log, verify_token
from sse_bus import SSEBus
from sse_starlette.sse import EventSourceResponse

# -------------------------------------------------------------------
# OpenTelemetry Tracing Setup
# -------------------------------------------------------------------
try:
    from agent_framework.observability import setup_observability

    _TRACING_AVAILABLE = True
except ImportError:
    _TRACING_AVAILABLE = False
    logging.warning("⚠️  agent-framework Tracing nicht verfügbar (pip install agent-framework)")

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_DIR / "dashboard_runtime.log"), logging.StreamHandler()],
)
logger = logging.getLogger("dashboard")

# -------------------------------------------------------------------
# OpenAI Client (opena20)
# -------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_OPENA20")
if OPENAI_API_KEY:
    try:
        from openai import OpenAI

        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("✅ OpenAI Client (opena20) initialisiert")
    except ImportError:
        logger.warning("⚠️  OpenAI-Paket nicht installiert (pip install openai)")
        openai_client = None
    except Exception as e:
        logger.error(f"❌ OpenAI Client Init-Fehler: {e}")
        openai_client = None
else:
    logger.warning("⚠️  OPENAI_API_KEY_OPENA20 nicht gesetzt")
    openai_client = None

# -------------------------------------------------------------------
# Lifespan Management
# -------------------------------------------------------------------
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Dashboard startup...")
    logger.info("Starting opena20 on port 12349")
    logger.info("HTML Management Workflows: 6 endpoints activated")
    logger.info("Meta-Workflow-System: Ready for activation")
    logger.info("🧹 Self-Cleaning-System: Demo-Endpoints activated")

    # Initialize components (will be defined later)
    global agent_registry, sse_bus
    from agent_registry import AgentRegistry
    from background_poller import on_shutdown as poller_shutdown
    from background_poller import on_startup as poller_startup
    from background_poller import set_registry
    from sse_bus import SSEBus

    agent_registry = AgentRegistry()
    sse_bus = SSEBus()

    set_registry(agent_registry)
    await poller_startup()
    logger.info("Background-Poller started")

    yield

    # Shutdown
    logger.info("Dashboard shutdown...")
    await poller_shutdown()
    logger.info("Background-Poller stopped")


# -------------------------------------------------------------------
# App + Security
# -------------------------------------------------------------------
app = FastAPI(
    title="ELION Hyper-Dashboard 2.0", description="Dashboard-Backend (Option 2)", version="1.0", lifespan=lifespan
)

# -------------------------------------------------------------------
# OpenTelemetry Tracing Initialization
# -------------------------------------------------------------------
if _TRACING_AVAILABLE:
    try:
        setup_observability(
            otlp_endpoint="http://localhost:4317",  # gRPC endpoint for OTEL collector
            enable_sensitive_data=True,  # Capture prompts/completions for debugging
        )
        logger.info("✅ OpenTelemetry Tracing initialized (http://localhost:4317)")
    except Exception as e:
        logger.warning(f"⚠️  Tracing setup failed: {e}")
else:
    logger.info("ℹ️  Tracing disabled (agent-framework not installed)")

# CORS (lokal offen — bei Bedarf einschränken)
# Ermöglicht Anfragen von OpenWebUI (Port 8080) und Dashboard (Port 12349)
cors_origins = [
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://127.0.0.1:12349",
    "http://localhost:12349",
    "*",  # Für Entwicklung; in Production einschränken
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

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Dashboard startup...")
    logger.info("Starting opena20 on port 12349")
    logger.info("HTML Management Workflows: 6 endpoints activated")
    logger.info("Meta-Workflow-System: Ready for activation")
    logger.info("🧹 Self-Cleaning-System: Demo-Endpoints activated")
    set_registry(agent_registry)
    await poller_startup()
    logger.info("Background-Poller started")

    yield

    # Shutdown
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
        "service": "opena20",
        "status": "healthy",
        "strict": True,
        "openai_key_present": bool(OPENAI_API_KEY),
        "openai_client_ready": openai_client is not None,
        "timestamp": datetime.utcnow().isoformat(),
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
    return {"strict": True, "count": len(agents), "agents": agents}


@rate_limiter.limit()
async def get_all_status(token: HTTPAuthorizationCredentials = Security(security)):
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, "/api/status/all", ok)
    if not ok:
        raise HTTPException(status_code=401, detail="Not authenticated")

    agents_status = await agent_registry.get_all_status()
    return {"strict": True, "agents": agents_status}


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
async def register_agent(payload: dict, token: HTTPAuthorizationCredentials = Security(security)):
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
        "registered_at": datetime.utcnow().isoformat() + "Z",
    }


# --- Legacy-Kompatibilität: alter falscher Aufruf /api/command/register ----------------
@app.post("/api/command/register")
@rate_limiter.limit()
async def legacy_register_alias(payload: dict, token: HTTPAuthorizationCredentials = Security(security)):
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


# -------------------------------------------------------------------
# Self-Cleaning System Integration
# -------------------------------------------------------------------


@app.get("/api/self_cleaning/health")
@rate_limiter.limit()
async def self_cleaning_health(token: HTTPAuthorizationCredentials = Security(security)):
    """Healthcheck für das Self-Cleaning System"""
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, "/api/self_cleaning/health", ok)
    if not ok:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {
        "status": "ok",
        "system": "self_cleaning",
        "health_score": 75,
        "last_scan": "2025-01-15T10:30:00Z",
        "active_cleaners": 5,
        "message": "System läuft stabil",
    }


@app.post("/api/self_cleaning/scan")
@rate_limiter.limit()
async def trigger_scan(token: HTTPAuthorizationCredentials = Security(security)):
    """Triggert einen System-Scan"""
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, "/api/self_cleaning/scan", ok)
    if not ok:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {
        "status": "success",
        "message": "Scan gestartet",
        "scan_id": "scan_001",
        "estimated_duration": "2-3 Minuten",
    }


@app.post("/api/self_cleaning/repair")
@rate_limiter.limit()
async def trigger_repair(token: HTTPAuthorizationCredentials = Security(security)):
    """Triggert eine automatische Reparatur"""
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, "/api/self_cleaning/repair", ok)
    if not ok:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {
        "status": "success",
        "message": "Reparatur gestartet",
        "repair_id": "repair_001",
        "estimated_duration": "5-10 Minuten",
    }


@app.get("/api/self_cleaning/status")
@rate_limiter.limit()
async def cleaning_status(token: HTTPAuthorizationCredentials = Security(security)):
    """Status des Self-Cleaning Systems"""
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, "/api/self_cleaning/status", ok)
    if not ok:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {
        "status": "active",
        "health_score": 75,
        "active_processes": ["log_rotation", "cache_cleanup", "temp_cleaner"],
        "last_activities": [
            {"timestamp": "2025-01-15T10:25:00Z", "action": "log_cleanup", "status": "completed"},
            {"timestamp": "2025-01-15T10:20:00Z", "action": "cache_clear", "status": "completed"},
            {"timestamp": "2025-01-15T10:15:00Z", "action": "temp_cleanup", "status": "completed"},
        ],
        "next_scheduled": "2025-01-15T11:00:00Z",
    }


# -------------------------------------------------------------------
# OpenAI Chat Endpoints
# -------------------------------------------------------------------


@app.post("/api/ai/chat")
@rate_limiter.limit()
async def ai_chat(payload: dict, token: HTTPAuthorizationCredentials = Security(security)):
    """Direkte OpenAI-Chat-Integration (opena20 AI-Backend)"""
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, "/api/ai/chat", ok)
    if not ok:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not openai_client:
        raise HTTPException(status_code=503, detail="OpenAI Client nicht verfügbar")

    try:
        user_message = payload.get("message", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="'message' erforderlich")

        # OpenAI Chat Completion
        # DEFAULT MODEL: gpt-3.5-turbo (WICHTIG: Für gesamtes Dashboard vorerst merken!)
        # KEINE Token-Begrenzung (max_tokens entfernt)
        response = openai_client.chat.completions.create(
            model=payload.get("model", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": "Du bist der ELION Hyper-Dashboard Assistant."},
                {"role": "user", "content": user_message},
            ],
            temperature=payload.get("temperature", 0.7),
        )

        answer = response.choices[0].message.content

        # SSE-Event publishen
        await sse_bus.publish(
            {
                "event": "ai_chat_response",
                "data": {
                    "message": user_message,
                    "response": answer,
                    "model": payload.get("model", "gpt-4"),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
            }
        )

        return {
            "strict": True,
            "message": user_message,
            "response": answer,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        }

    except Exception as e:
        logger.error(f"AI Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/openwebui/chat")
@rate_limiter.limit()
async def openwebui_chat(payload: dict, token: HTTPAuthorizationCredentials = Security(security)):
    """Leite Chat-Anfrage an OpenWebUI-Agenten weiter"""
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, "/api/openwebui/chat", ok)
    if not ok:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        import requests

        response = requests.post("http://127.0.0.1:12347/command", json=payload, timeout=30)
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
async def generate_agent_token(agent_id: str, token: HTTPAuthorizationCredentials = Security(security)):
    """Generiere JWT Token für einen Agenten"""
    ok = verify_token(token.credentials)
    security_log.log_access(token.credentials, f"/api/agents/{agent_id}/token", ok)
    if not ok:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        from jwt_auth import create_token

        jwt_token = create_token(agent_id=agent_id, scope="invoke", permissions=["read", "write"])
        return {
            "agent_id": agent_id,
            "token": jwt_token,
            "token_type": "Bearer",
            "expires_in": 86400,  # 24h in seconds
            "scope": "invoke",
        }
    except Exception as e:
        logger.error(f"Token generation failed for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Token generation failed: {e!s}")


@app.post("/api/auth/verify")
@rate_limiter.limit()
async def verify_jwt_token(payload: dict, token: HTTPAuthorizationCredentials = Security(security)):
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
            "error": result.error_type if not result.is_valid else None,
        }
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {e!s}")


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
                tokens[agent_id] = create_token(agent_id=agent_id, scope="invoke", permissions=["read", "write"])
            except Exception as e:
                logger.warning(f"Failed to create token for {agent_id}: {e}")
                tokens[agent_id] = None

        return {"count": len(tokens), "tokens": tokens, "generated_at": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Batch token generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {e!s}")


# -------------------------------------------------------------------
# Server Sent Events
# -------------------------------------------------------------------
@app.get("/api/events/live")
async def event_stream(request: Request):
    async def event_generator():
        async for event in sse_bus.subscribe():
            if await request.is_disconnected():
                break
            yield {"event": event.get("event", "message"), "data": json.dumps(event.get("data", {})), "retry": 3000}

    return EventSourceResponse(event_generator())


# -------------------------------------------------------------------
# Einfache UI-Routen (optional; Templates können später ergänzt werden)
# -------------------------------------------------------------------
@app.get("/ui/")
@app.get("/")
async def dashboard_ui():
    """Serve the main dashboard HTML"""
    template_path = Path(__file__).parent / "templates" / "index.html"
    if template_path.exists():
        html = template_path.read_text()
        return HTMLResponse(html)
    else:
        html = """<!doctype html><html><head><meta charset="utf-8"><title>Dashboard</title></head>
<body><h1>ELION Hyper-Dashboard</h1><p>API läuft. Dashboard-Template nicht gefunden.</p></body></html>"""
        return HTMLResponse(html)


@app.get("/self_cleaning_dashboard.html")
async def self_cleaning_dashboard():
    """Serve Self-Cleaning Dashboard HTML"""
    # Fallback: Generate basic dashboard HTML inline
    basic_html = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>Self-Cleaning System Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-4">
            <div class="row">
                <div class="col-12">
                    <h1 class="mb-4"><i class="fas fa-broom text-primary"></i> Self-Cleaning System Dashboard</h1>
                </div>
            </div>
            <div class="row">
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5>System Health</h5>
                            <h2><span class="badge bg-success">75/100</span></h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5>Active Cleaners</h5>
                            <h2><span class="badge bg-info">5</span></h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5>Last Scan</h5>
                            <small>10:30 UTC</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5>Status</h5>
                            <span class="badge bg-success">Active</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <h5>Aktionen</h5>
                            <button class="btn btn-primary me-2" onclick="triggerScan()">
                                <i class="fas fa-search"></i> System Scan
                            </button>
                            <button class="btn btn-warning me-2" onclick="triggerRepair()">
                                <i class="fas fa-tools"></i> Auto Repair
                            </button>
                            <button class="btn btn-info" onclick="getStatus()">
                                <i class="fas fa-info"></i> Status Abrufen
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <h5>Log Output</h5>
                            <div id="logOutput" class="bg-dark text-light p-3 rounded" style="height: 300px; overflow-y: scroll;">
                                <div>Self-Cleaning System bereit...</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script>
            const BEARER_TOKEN = localStorage.getItem('bearer_token') || 'c899b90d-faf8-485b-afa4-078357cf5313';

            function addLog(message) {
                const log = document.getElementById('logOutput');
                const time = new Date().toLocaleTimeString();
                log.innerHTML += '<div>' + time + ' - ' + message + '</div>';
                log.scrollTop = log.scrollHeight;
            }

            function triggerScan() {
                addLog('Starte System Scan...');
                fetch('/api/self_cleaning/scan', {
                    method: 'POST',
                    headers: {'Authorization': 'Bearer ' + BEARER_TOKEN}
                }).then(r => r.json()).then(d => {
                    addLog('✅ Scan: ' + d.message);
                }).catch(e => addLog('❌ Scan Fehler: ' + e));
            }

            function triggerRepair() {
                addLog('Starte Auto Repair...');
                fetch('/api/self_cleaning/repair', {
                    method: 'POST',
                    headers: {'Authorization': 'Bearer ' + BEARER_TOKEN}
                }).then(r => r.json()).then(d => {
                    addLog('✅ Repair: ' + d.message);
                }).catch(e => addLog('❌ Repair Fehler: ' + e));
            }

            function getStatus() {
                addLog('Lade Status...');
                fetch('/api/self_cleaning/status', {
                    headers: {'Authorization': 'Bearer ' + BEARER_TOKEN}
                }).then(r => r.json()).then(d => {
                    addLog('📊 Health Score: ' + d.health_score);
                    addLog('🔧 Aktive Prozesse: ' + d.active_processes.join(', '));
                }).catch(e => addLog('❌ Status Fehler: ' + e));
            }

            // Auto-refresh status every 30 seconds
            setInterval(getStatus, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=basic_html, media_type="text/html")


@app.get("/agent/{agent_id}")
async def agent_ui(agent_id: str):
    """Detailseite für einen einzelnen Agenten mit speziellen Features für opena3"""
    # Direkt Health-Check vom Agent holen
    agent_port_map = {
        "opena1": 12344,
        "opena2": 12345,
        "kordp": 12346,
        "opena3": 12347,
        "opena4": 12348,
        "opena5": 12351,
        "opena6": 12352,
        "opena7": 12353,
        "opena8": 12354,
        "opena9": 12355,
        "opena10": 12356,
        "opena11": 12357,
        "opena12": 12358,
        "opena13": 12359,
        "opena14": 12360,
        "opena15": 12361,
        "opena16": 12362,
        "opena17": 12363,
        "opena18": 12364,
        "opena19": 12365,
        "opena20": 12349,
        "opena21": 12366,
    }

    agent_names = {
        "opena1": "Koordinator",
        "opena2": "Archivator",
        "kordp": "Koordinatport",
        "opena3": "OpenWebUI Terminal",
        "opena4": "Telegram",
        "opena5": "VS Code",
        "opena6": "Browser",
        "opena7": "Email",
        "opena8": "WhatsApp",
        "opena9": "Telefonie",
        "opena10": "Call Tracking",
        "opena11": "Unlock",
        "opena12": "Social Media",
        "opena13": "Influencer",
        "opena14": "Calendar",
        "opena15": "HTML Creator",
        "opena16": "Shop",
        "opena17": "Homepage Creator",
        "opena18": "CRM",
        "opena19": "Stocks & Crypto",
        "opena20": "Dashboard",
        "opena21": "Workflow",
    }

    port = agent_port_map.get(agent_id)
    agent_name = agent_names.get(agent_id, agent_id)

    if not port:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} nicht gefunden")

    try:
        import httpx

        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"http://127.0.0.1:{port}/health")
            status_data = response.json()
    except Exception as e:
        status_data = {"error": str(e), "status": "offline"}

    # Spezielle Features für opena3 (OpenWebUI Terminal)
    is_opena3 = agent_id == "opena3"

    html = f"""<!doctype html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{agent_name} ({agent_id}) - ELION Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            color: white;
        }}
        .status-badge.online {{
            background: #10b981;
        }}
        .status-badge.offline {{
            background: #ef4444;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .info-card {{
            background: #f9fafb;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        .info-card h3 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 0.9em;
            text-transform: uppercase;
        }}
        .info-card .value {{
            color: #333;
            font-size: 1.5em;
            font-weight: bold;
        }}
        .data-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-top: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .data-section h2 {{
            color: #333;
            margin-bottom: 20px;
        }}
        pre {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 10px;
            overflow-x: auto;
            font-size: 0.9em;
            line-height: 1.6;
        }}
        .btn {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            margin-top: 20px;
            transition: opacity 0.2s;
        }}
        .btn:hover {{
            opacity: 0.9;
        }}
        .control-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-top: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .control-section h2 {{
            color: #333;
            margin-bottom: 20px;
        }}
        .control-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .control-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 20px;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, opacity 0.2s;
        }}
        .control-btn:hover {{
            opacity: 0.9;
            transform: translateY(-2px);
        }}
        .control-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        .command-input {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 1em;
            margin-bottom: 15px;
        }}
        .command-input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        .response-box {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            min-height: 100px;
            font-family: monospace;
            font-size: 0.9em;
            line-height: 1.6;
            white-space: pre-wrap;
        }}
        .openwebui-section {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            border-radius: 15px;
            padding: 30px;
            margin-top: 20px;
            color: white;
            box-shadow: 0 5px 15px rgba(16, 185, 129, 0.3);
        }}
        .openwebui-section h2 {{
            color: white;
            margin-bottom: 20px;
        }}
        .chat-input {{
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            margin-bottom: 15px;
            resize: vertical;
            min-height: 100px;
            font-family: inherit;
        }}
        .chat-btn {{
            background: white;
            color: #059669;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, opacity 0.2s;
            width: 100%;
        }}
        .chat-btn:hover {{
            opacity: 0.9;
            transform: translateY(-2px);
        }}
        .chat-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }}
        .chat-response {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            min-height: 150px;
            font-family: monospace;
            font-size: 0.9em;
            line-height: 1.6;
            white-space: pre-wrap;
        }}
        .feature-badge {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            margin: 5px 5px 5px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 {agent_name} ({agent_id})</h1>
            <span class="status-badge {"online" if status_data.get("status") in ["ok", "online", "healthy"] else "offline"}">
                {"✓ Online" if status_data.get("status") in ["ok", "online", "healthy"] else "✗ Offline"}
            </span>

            {'<div style="margin-top: 15px;">' if is_opena3 else ''}
            {'<span class="feature-badge">⚡ Option-2-Flow</span>' if is_opena3 else ''}
            {'<span class="feature-badge">🔒 Bearer Token Security</span>' if is_opena3 else ''}
            {'<span class="feature-badge">✓ Strict JSON Schema</span>' if is_opena3 else ''}
            {'<span class="feature-badge">💬 OpenWebUI Chat API</span>' if is_opena3 else ''}
            {'</div>' if is_opena3 else ''}

            <div class="info-grid">
                <div class="info-card">
                    <h3>Port</h3>
                    <div class="value">{port}</div>
                </div>
                <div class="info-card">
                    <h3>Service</h3>
                    <div class="value">{status_data.get("service", agent_id)}</div>
                </div>
                <div class="info-card">
                    <h3>Uptime</h3>
                    <div class="value">{int(status_data.get("uptime", status_data.get("uptime_seconds", 0))) if isinstance(status_data.get("uptime", status_data.get("uptime_seconds")), (int, float)) else 0}s</div>
                </div>
                <div class="info-card">
                    <h3>{'OpenWebUI Status' if is_opena3 else 'Kürzel'}</h3>
                    <div class="value">{'✓ Verbunden' if is_opena3 and status_data.get("openwebui_available") else (status_data.get("kuerzel", status_data.get("program_target", "-")))}</div>
                </div>
            </div>
        </div>

        <div class="control-section">
            <h2>🎛️ Agent-Steuerung</h2>

            <div class="control-grid">
                <button class="control-btn" onclick="sendCommand('ping')">📡 Ping</button>
                <button class="control-btn" onclick="sendCommand('status')">📊 Status</button>
                <button class="control-btn" onclick="sendCommand('health')">❤️ Health-Check</button>
                <button class="control-btn" onclick="refreshPage()">🔄 Aktualisieren</button>
            </div>

            <input type="text" class="command-input" id="customCommand" placeholder="Eigener Befehl (JSON oder Text)..." />
            <button class="control-btn" onclick="sendCustomCommand()" style="width: 100%;">▶️ Befehl ausführen</button>

            <div class="response-box" id="responseBox">Bereit für Befehle...</div>
        </div>

        {'''
        <div class="openwebui-section">
            <h2>💬 OpenWebUI Chat API</h2>
            <p style="margin-bottom: 20px; opacity: 0.9;">
                Direkte Integration mit OpenWebUI (Port 8080) via Option-2-Flow.
                Alle Requests werden durch Bearer Token gesichert und in Safepoints archiviert.
            </p>

            <textarea
                class="chat-input"
                id="chatMessage"
                placeholder="Nachricht an OpenWebUI eingeben...&#10;&#10;Beispiel: 'Erkläre mir die ELION-Architektur'"></textarea>

            <button class="chat-btn" onclick="sendChatMessage()" id="chatBtn">
                🚀 Chat-Nachricht senden
            </button>

            <div class="chat-response" id="chatResponse">
                Warte auf Chat-Anfrage...
            </div>
        </div>
        ''' if is_opena3 else ''}

        <div class="data-section">
            <h2>📊 Health-Check Response</h2>
            <pre>{json.dumps(status_data, indent=2, ensure_ascii=False)}</pre>
        </div>

        <a href="/" class="btn">← Zurück zum Dashboard</a>
    </div>

    <script>
        const AGENT_ID = '{agent_id}';
        const AGENT_PORT = {port};

        async function sendCommand(cmd) {{
            const responseBox = document.getElementById('responseBox');
            responseBox.textContent = `Sende Befehl: ${{cmd}}...`;

            try {{
                const response = await fetch(`http://127.0.0.1:${{AGENT_PORT}}/${{cmd}}`, {{
                    method: 'GET',
                    signal: AbortSignal.timeout(5000)
                }});

                const data = await response.json();
                responseBox.textContent = JSON.stringify(data, null, 2);
            }} catch (error) {{
                responseBox.textContent = `❌ Fehler: ${{error.message}}`;
            }}
        }}

        async function sendCustomCommand() {{
            const input = document.getElementById('customCommand');
            const cmd = input.value.trim();

            if (!cmd) {{
                alert('Bitte Befehl eingeben');
                return;
            }}

            const responseBox = document.getElementById('responseBox');
            responseBox.textContent = `Sende: ${{cmd}}...`;

            try {{
                let payload = cmd;
                try {{
                    payload = JSON.parse(cmd);
                }} catch {{
                    // Keep as string
                }}

                const response = await fetch(`http://127.0.0.1:${{AGENT_PORT}}/command`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ command: payload }}),
                    signal: AbortSignal.timeout(10000)
                }});

                const data = await response.json();
                responseBox.textContent = JSON.stringify(data, null, 2);
            }} catch (error) {{
                responseBox.textContent = `❌ Fehler: ${{error.message}}`;
            }}
        }}

        function refreshPage() {{
            location.reload();
        }}

        // OpenWebUI Chat-Funktion (nur für opena3)
        async function sendChatMessage() {{
            const chatInput = document.getElementById('chatMessage');
            const chatResponse = document.getElementById('chatResponse');
            const chatBtn = document.getElementById('chatBtn');

            const message = chatInput.value.trim();
            if (!message) {{
                alert('Bitte Nachricht eingeben');
                return;
            }}

            chatBtn.disabled = true;
            chatBtn.textContent = '⏳ Sende an OpenWebUI...';
            chatResponse.textContent = 'Verarbeite Request via Option-2-Flow...\\n\\nopena3 → archivp (CMD Safepoint) → kordp → OpenWebUI...';

            try {{
                const token = localStorage.getItem('bearer_token') || prompt('Bearer Token eingeben:');
                if (!token) {{
                    throw new Error('Kein Bearer Token verfügbar');
                }}

                const response = await fetch('http://127.0.0.1:{port}/chat', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${{token}}`
                    }},
                    body: JSON.stringify({{
                        message: message,
                        stream: false
                    }}),
                    signal: AbortSignal.timeout(30000)
                }});

                if (!response.ok) {{
                    const error = await response.json();
                    throw new Error(error.detail || `HTTP ${{response.status}}`);
                }}

                const data = await response.json();

                chatResponse.textContent = '✅ Response von OpenWebUI:\\n\\n' +
                    JSON.stringify(data, null, 2) +
                    '\\n\\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n' +
                    '⚡ Option-2-Flow ausgeführt\\n' +
                    '🔒 Bearer Token validiert\\n' +
                    '📦 Safepoints erstellt (CMD + RESP)\\n' +
                    '✓ Strict JSON Schema konform';

                // Token speichern
                localStorage.setItem('bearer_token', token);

            }} catch (error) {{
                chatResponse.textContent = `❌ Fehler beim Chat-Request:\\n\\n${{error.message}}\\n\\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n\\nMögliche Ursachen:\\n• Bearer Token ungültig (401)\\n• OpenWebUI nicht erreichbar (502)\\n• Timeout (504)\\n• opena3 offline`;
            }} finally {{
                chatBtn.disabled = false;
                chatBtn.textContent = '🚀 Chat-Nachricht senden';
            }}
        }}
    </script>
</body>
</html>"""
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

    uvicorn.run(  # pyright: ignore[reportUnknownMemberType]
        "main_dashboard:app", host="127.0.0.1", port=port, reload=True
    )
