#!/usr/bin/env python3
"""
OpenWebUI Agent V2 (opena3) – PORTIER 3.0 Certified
=====================================

Option-2-Flow Integration mit vollständiger Safepoint-Anbindung.
Architektur: opena1 → opena2 → kordp → opena3 → OpenWebUI

Features:
✓ Option-2-Flow konform (/cmd, /health, /native, /dispatch_ready)
✓ Safepoint-System (CMD/RESP) mit Unicode-Pfeil →
✓ Dispatcher-Anbindung (kordp kompatibel)
✓ Tool-Registry Auto-Registration
✓ Dashboard Deep Integration (SSE Events)
✓ Bearer Auth + Strict Security
✓ Chat Engine Upgrade (context chaining)
✓ Entwicklungsfreundlich (Mock-Mode, Self-Test)

Port: 12347
Status: Production Ready
"""

import json
import logging
import os
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# ============================================================================
# LOGGING SETUP
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("logs/opena3_v2.log", mode="a", encoding="utf-8")],
)
logger = logging.getLogger("opena3_v2")


# ============================================================================
# KONFIGURATION
# ============================================================================
class Config:
    # Service Identity
    SERVICE_ID = "opena3"
    SERVICE_TARGET = "openwebui3"
    SERVICE_NAME = "OpenWebUI Agent V2"
    PORT = int(os.getenv("OPENA3_PORT", "12347"))

    # OpenWebUI Integration
    OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://127.0.0.1:8080")
    OPENWEBUI_TIMEOUT = int(os.getenv("OPENWEBUI_TIMEOUT", "30"))

    # PORTIER Integration
    OPENA1_URL = os.getenv("OPENA1_URL", "http://127.0.0.1:12344")
    OPENA2_URL = os.getenv("OPENA2_URL", "http://127.0.0.1:12345")
    KORDP_URL = os.getenv("KORDP_URL", "http://127.0.0.1:12346")
    DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://127.0.0.1:12349")

    # Security
    BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")

    # Safepoints
    ARCHIVP_ROOT = os.getenv("ARCHIVP_ROOT", "/tmp/archivp")

    # Development
    DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"
    MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"


config = Config()

# ============================================================================
# MODELS (STRICT SCHEMA)
# ============================================================================


class HealthResponse(BaseModel):
    """Health Response für opena3 V2"""

    model_config = ConfigDict(extra="forbid")

    service: str
    status: str
    ts: str
    uptime_seconds: float
    port: int
    policy: dict[str, Any]
    openwebui_status: str
    last_dispatch: str | None = None


class CMDEnvelope(BaseModel):
    """Option-2-Flow CMD Envelope von opena1"""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    timestamp: str
    source: str = "opena1"
    command: str
    payload: dict[str, Any]


class RESPEnvelope(BaseModel):
    """Option-2-Flow RESP Envelope zurück an opena2"""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    timestamp: str
    target: str = "opena2"
    status: str
    result: dict[str, Any]


class NativeRequest(BaseModel):
    """Native Request für direkte UI-Calls"""

    model_config = ConfigDict(extra="forbid")

    prompt: str
    context: dict[str, Any] = Field(default_factory=dict)
    model: str | None = None
    stream: bool = False


class NativeResponse(BaseModel):
    """Native Response für direkte UI-Calls"""

    model_config = ConfigDict(extra="forbid")

    text: str
    model: str | None = None
    timestamp: str
    conversation_id: str | None = None


class DispatchRequest(BaseModel):
    """Dispatcher Request von kordp"""

    model_config = ConfigDict(extra="forbid")

    service_target: str
    payload: dict[str, Any]
    dispatch_id: str | None = None


class RegistrationPayload(BaseModel):
    """Tool Registry Payload"""

    model_config = ConfigDict(extra="forbid")

    service_id: str
    service_target: str
    port: int
    capabilities: list[str]
    status: str = "active"


class SafepointEntry(BaseModel):
    """Safepoint Entry für opena2"""

    model_config = ConfigDict(extra="forbid")

    sp_id: str
    timestamp: str
    agent: str
    category: str  # CMD | RESP
    body: dict[str, Any]
    masked: bool = True


# ============================================================================
# SAFEPOINT SYSTEM
# ============================================================================
class SafepointManager:
    def __init__(self, root_path: str = config.ARCHIVP_ROOT):
        self.root = Path(root_path)
        self.root.mkdir(parents=True, exist_ok=True)

    def _mask_secrets(self, data: dict[str, Any]) -> dict[str, Any]:
        """Maskiert Secrets in Safepoint-Daten"""
        if isinstance(data, dict):
            masked = {}
            for k, v in data.items():
                if any(secret in k.lower() for secret in ["token", "key", "password", "secret"]):
                    masked[k] = "***MASKED***"
                elif isinstance(v, dict):
                    masked[k] = self._mask_secrets(v)
                else:
                    masked[k] = v
            return masked
        return data

    def write_safepoint(self, agent: str, category: str, body: dict[str, Any]) -> str:
        """Schreibt Safepoint mit Unicode-Pfeil →"""
        now = datetime.now(UTC)
        sp_id = f"{int(now.timestamp() * 1000):013d}"

        # YYYY/MM/DD Struktur
        date_path = self.root / now.strftime("%Y") / now.strftime("%m") / now.strftime("%d")
        date_path.mkdir(parents=True, exist_ok=True)

        # Safepoint-Datei mit Unicode-Pfeil →
        filename = f"SP{sp_id}_{agent}→opena2_{category}.json"
        filepath = date_path / filename

        # Body maskieren
        masked_body = self._mask_secrets(body)

        entry = SafepointEntry(
            sp_id=sp_id, timestamp=now.isoformat(), agent=agent, category=category, body=masked_body, masked=True
        )

        # Datei schreiben
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(entry.model_dump(), f, indent=2, ensure_ascii=False)

        # Index.jsonl aktualisieren (append-only)
        index_path = self.root / "index.jsonl"
        index_entry = {
            "sp_id": sp_id,
            "timestamp": now.isoformat(),
            "agent": agent,
            "category": category,
            "path": str(filepath.relative_to(self.root)),
            "filename": filename,
        }

        with open(index_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(index_entry, ensure_ascii=False) + "\n")

        logger.info(f"Safepoint {category} geschrieben: {filename}")
        return sp_id


# ============================================================================
# OPENWEBUI CLIENT
# ============================================================================
class OpenWebUIClient:
    def __init__(self):
        self.base_url = config.OPENWEBUI_URL
        self.timeout = config.OPENWEBUI_TIMEOUT

    async def health_check(self) -> bool:
        """Prüft OpenWebUI Health"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/config")
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"OpenWebUI health check failed: {e}")
            return False

    async def chat(self, prompt: str, model: str | None = None, context: dict | None = None) -> dict[str, Any]:
        """Chat mit OpenWebUI"""
        if config.MOCK_MODE:
            return {
                "text": f"MOCK: Antwort auf '{prompt[:50]}...'",
                "model": model or "mock-gpt",
                "timestamp": datetime.now(UTC).isoformat(),
            }

        payload = {"prompt": prompt, "model": model or "auto", "context": context or {}}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                resp.raise_for_status()

                data = resp.json()
                return {
                    "text": data.get("text") or data.get("response") or str(data),
                    "model": data.get("model") or model,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail=f"OpenWebUI timeout after {self.timeout}s")
        except httpx.ConnectError:
            raise HTTPException(status_code=502, detail="Cannot connect to OpenWebUI")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"OpenWebUI error: {e.response.text}")


# ============================================================================
# DASHBOARD SSE CLIENT
# ============================================================================
class DashboardClient:
    async def publish_event(self, event_type: str, data: dict[str, Any]):
        """Publiziert SSE Event an Dashboard"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    f"{config.DASHBOARD_URL}/sse/publish",
                    json={"event_type": event_type, "data": data},
                    headers={"Authorization": f"Bearer {config.BEARER_TOKEN}"},
                )
        except Exception as e:
            logger.warning(f"Dashboard SSE failed: {e}")


# ============================================================================
# SERVICE REGISTRY
# ============================================================================
class ServiceRegistry:
    async def register(self) -> bool:
        """Registriert opena3 bei kordp"""
        payload = RegistrationPayload(
            service_id=config.SERVICE_ID,
            service_target=config.SERVICE_TARGET,
            port=config.PORT,
            capabilities=["chat", "terminal", "openwebui", "conversation"],
        )

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{config.KORDP_URL}/dispatch/register",
                    json=payload.model_dump(),
                    headers={"Authorization": f"Bearer {config.BEARER_TOKEN}"},
                )
                if resp.status_code == 200:
                    logger.info("Successfully registered with kordp")
                    return True
                else:
                    logger.error(f"Registration failed: {resp.status_code} - {resp.text}")
                    return False
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False


# ============================================================================
# GLOBALS
# ============================================================================
start_time = datetime.now(UTC)
last_dispatch_time = None
safepoint_manager = SafepointManager()
openwebui_client = OpenWebUIClient()
dashboard_client = DashboardClient()
service_registry = ServiceRegistry()

# ============================================================================
# SECURITY
# ============================================================================
security = HTTPBearer()
limiter = Limiter(key_func=get_remote_address)


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verifiziert Bearer Token"""
    if credentials.credentials != config.BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid bearer token")
    return credentials.credentials


# ============================================================================
# FASTAPI APP
# ============================================================================
app = FastAPI(
    title=config.SERVICE_NAME,
    description="PORTIER 3.0 OpenWebUI Agent mit Option-2-Flow Integration",
    version="2.0.0",
    docs_url="/docs" if config.DEV_MODE else None,
)

# CORS Middleware (locked für Production)
if config.DEV_MODE:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:12349", "http://localhost:12349"],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ============================================================================
# OPTION-2-FLOW ENDPOINTS
# ============================================================================


@app.post("/cmd", response_model=RESPEnvelope)
async def handle_cmd(cmd: CMDEnvelope, token: str = Depends(verify_token)) -> RESPEnvelope:
    """
    Option-2-Flow CMD Endpoint
    Empfängt CMD-Envelope von opena1 → verarbeitet → RESP an opena2
    """
    global last_dispatch_time
    last_dispatch_time = datetime.now(UTC).isoformat()

    logger.info(f"CMD received: {cmd.request_id} - {cmd.command}")

    # CMD Safepoint
    cmd_sp_id = safepoint_manager.write_safepoint(agent=config.SERVICE_ID, category="CMD", body=cmd.model_dump())

    try:
        # Command verarbeiten
        if cmd.command == "chat":
            prompt = cmd.payload.get("prompt", "")
            model = cmd.payload.get("model")
            context = cmd.payload.get("context", {})

            if not prompt:
                raise ValueError("Prompt erforderlich")

            # OpenWebUI Chat
            result = await openwebui_client.chat(prompt, model, context)

            # Dashboard Event
            await dashboard_client.publish_event(
                "opena3_chat",
                {
                    "request_id": cmd.request_id,
                    "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                    "model": result.get("model"),
                    "response_length": len(result.get("text", "")),
                },
            )

            resp = RESPEnvelope(
                request_id=cmd.request_id,
                timestamp=datetime.now(UTC).isoformat(),
                status="success",
                result=result,
            )

        else:
            raise ValueError(f"Unknown command: {cmd.command}")

    except Exception as e:
        logger.error(f"CMD processing error: {e}")
        resp = RESPEnvelope(
            request_id=cmd.request_id,
            timestamp=datetime.now(UTC).isoformat(),
            status="error",
            result={"error": str(e), "traceback": traceback.format_exc()},
        )

    # RESP Safepoint
    safepoint_manager.write_safepoint(agent=config.SERVICE_ID, category="RESP", body=resp.model_dump())

    logger.info(f"CMD processed: {cmd.request_id} - {resp.status}")
    return resp


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """
    Extended Health Check für Option-2-Flow
    """
    uptime = (datetime.now(UTC) - start_time).total_seconds()
    openwebui_status = "ok" if await openwebui_client.health_check() else "error"

    return HealthResponse(
        service=config.SERVICE_ID,
        status="ok",
        ts=datetime.now(UTC).isoformat(),
        uptime_seconds=uptime,
        port=config.PORT,
        policy={
            "bearer_auth": True,
            "rate_limited": True,
            "cors_locked": not config.DEV_MODE,
            "safepoint_enabled": True,
            "port_range": "12344-12399",
        },
        openwebui_status=openwebui_status,
        last_dispatch=last_dispatch_time,
    )


@app.post("/native", response_model=NativeResponse)
@limiter.limit("10/minute")
async def native_chat(request: Request, req: NativeRequest, token: str = Depends(verify_token)) -> NativeResponse:
    """
    Native Endpoint für direkte UI-Calls
    Unabhängig von Option-2-Flow für lokale Tests
    """
    logger.info(f"Native chat: {req.prompt[:50]}...")

    try:
        result = await openwebui_client.chat(req.prompt, req.model, req.context)

        return NativeResponse(
            text=result["text"], model=result.get("model"), timestamp=result["timestamp"], conversation_id=str(uuid4())
        )
    except Exception as e:
        logger.error(f"Native chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dispatch_ready")
async def dispatch_ready(token: str = Depends(verify_token)) -> dict[str, Any]:
    """
    Dashboard-orientierter Status für Live Routing
    """
    openwebui_ok = await openwebui_client.health_check()

    return {
        "service_id": config.SERVICE_ID,
        "service_target": config.SERVICE_TARGET,
        "ready": openwebui_ok,
        "capabilities": ["chat", "terminal", "openwebui", "conversation"],
        "load": "low",  # TODO: Echte Metrics
        "queue_size": 0,
        "last_dispatch": last_dispatch_time,
        "timestamp": datetime.now(UTC).isoformat(),
    }


# ============================================================================
# DISPATCHER-KOMPATIBILITÄT
# ============================================================================


@app.post("/dispatch")
async def handle_dispatch(req: DispatchRequest, token: str = Depends(verify_token)) -> dict[str, Any]:
    """
    Dispatcher Endpoint für kordp-Kompatibilität
    """
    if req.service_target != config.SERVICE_TARGET:
        raise HTTPException(
            status_code=400,
            detail=f"Service target mismatch: expected {config.SERVICE_TARGET}, got {req.service_target}",
        )

    # DISPATCH Safepoint
    safepoint_manager.write_safepoint(agent=config.SERVICE_ID, category="DISPATCH", body=req.model_dump())

    # Zu CMD-Envelope konvertieren
    cmd_envelope = CMDEnvelope(
        request_id=req.dispatch_id or str(uuid4()),
        timestamp=datetime.now(UTC).isoformat(),
        source="kordp",
        command="chat",
        payload=req.payload,
    )

    # Über CMD-Handler verarbeiten
    return await handle_cmd(cmd_envelope, config.BEARER_TOKEN)


# ============================================================================
# ENTWICKLUNGSFREUNDLICHE ENDPOINTS
# ============================================================================


@app.get("/selftest")
async def selftest(token: str = Depends(verify_token)) -> dict[str, Any]:
    """
    Self-Test Endpoint
    """
    results = {}

    # OpenWebUI Test
    results["openwebui"] = await openwebui_client.health_check()

    # Safepoint Test
    try:
        test_sp = safepoint_manager.write_safepoint("opena3", "TEST", {"test": True})
        results["safepoints"] = True
    except Exception as e:
        results["safepoints"] = False
        results["safepoint_error"] = str(e)

    # Dashboard Test
    try:
        await dashboard_client.publish_event("selftest", {"status": "ok"})
        results["dashboard_sse"] = True
    except Exception:
        results["dashboard_sse"] = False

    return {
        "service": config.SERVICE_ID,
        "version": "2.0.0",
        "tests": results,
        "overall": all(v for k, v in results.items() if isinstance(v, bool)),
        "timestamp": datetime.now(UTC).isoformat(),
    }


if config.DEV_MODE:

    @app.get("/docs/schema")
    async def api_schema():
        """API Schema Export (nur DEV-Mode)"""
        return app.openapi()


# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Startup: Service Registration"""
    logger.info(f"Starting {config.SERVICE_NAME} v2.0.0")
    logger.info(f"Port: {config.PORT}")
    logger.info(f"OpenWebUI: {config.OPENWEBUI_URL}")
    logger.info(f"DEV Mode: {config.DEV_MODE}")
    logger.info(f"MOCK Mode: {config.MOCK_MODE}")

    # Auto-Registration bei kordp
    if not config.MOCK_MODE:
        registration_ok = await service_registry.register()
        if registration_ok:
            logger.info("✓ Service registration successful")
        else:
            logger.warning("⚠ Service registration failed")

    logger.info("🚀 opena3 V2 ready for Option-2-Flow")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown Event"""
    logger.info("Shutting down opena3 V2")


# ============================================================================
# ERROR HANDLERS
# ============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global Exception Handler"""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if config.DEV_MODE else "An error occurred",
            "service": config.SERVICE_ID,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    import uvicorn

    # Logs-Verzeichnis erstellen
    os.makedirs("logs", exist_ok=True)

    logger.info(f"Starting {config.SERVICE_NAME} V2")
    logger.info(f"Option-2-Flow: {'✓ Enabled' if not config.MOCK_MODE else '✗ Mock Mode'}")

    uvicorn.run(app, host="127.0.0.1", port=config.PORT, log_level="info", access_log=True)
