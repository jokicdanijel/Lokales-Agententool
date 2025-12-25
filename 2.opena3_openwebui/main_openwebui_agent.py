#!/usr/bin/env python3
"""
opena3 – OpenWebUI Terminal Agent
Port: 12347 | Kürzel: owuip
Zweck: FastAPI-Wrapper für OpenWebUI-Interaktionen mit Option-2-Flow-Compliance

Version: 2.0 (erweitert mit SSE-Streaming, Multi-Model, Rate-Limiting, Retry)
"""

import asyncio
import json
import logging
import logging.handlers
import os
import sys
import time
from collections import defaultdict
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Import erweiterte Config-Module
from config import (  # type: ignore
    ModelInfo,
    PortPolicy,
    get_logging_config,
    get_model_registry,
    get_rate_limit_config,
    get_retry_config,
    load_config,
)

# ══════════════════════════════════════════════════════════════════════════════
# Configuration (ENV-only, niemals hardcoded)
# ══════════════════════════════════════════════════════════════════════════════

# Lade Config-Objekte
config = load_config()
model_registry = get_model_registry()
rate_limit_config = get_rate_limit_config()
retry_config = get_retry_config()
logging_config = get_logging_config()

PORT = config.port
HOST = os.getenv("OPENA3_HOST", "127.0.0.1")
BEARER_TOKEN = config.bearer_token
OPENWEBUI_URL = config.openwebui_url
OPENWEBUI_ADAPTER_URL = config.adapter_url
LOCALAGENT_URL = config.localagent_url
TIMEOUT = config.timeout
STREAM_TIMEOUT = config.stream_timeout

# Safepoint-Archiv
BASE_ROOT = Path(os.getenv("BASE_ROOT", Path.cwd().parent))
ARCHIVE_DIR = BASE_ROOT / "1.opena1&2_portier" / "archivp_store"
INDEX_FILE = ARCHIVE_DIR / "index.jsonl"

# ══════════════════════════════════════════════════════════════════════════════
# Logging Setup (konfigurierbar)
# ══════════════════════════════════════════════════════════════════════════════


def setup_logging():
    """Konfiguriert Logging basierend auf LoggingConfig"""
    log_config = get_logging_config()
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    handlers = []

    # Console Handler
    if log_config.log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_config.get_numeric_level())

        if log_config.json_logging:
            console_handler.setFormatter(JsonFormatter())
        else:
            console_handler.setFormatter(logging.Formatter(log_config.format))

        handlers.append(console_handler)

    # File Handler mit Rotation
    if log_config.log_to_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / log_config.log_file_name,
            maxBytes=log_config.max_file_size_mb * 1024 * 1024,
            backupCount=log_config.backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(log_config.get_numeric_level())

        if log_config.json_logging:
            file_handler.setFormatter(JsonFormatter())
        else:
            file_handler.setFormatter(logging.Formatter(log_config.format))

        handlers.append(file_handler)

    # Root-Logger konfigurieren
    logging.basicConfig(level=log_config.get_numeric_level(), handlers=handlers, force=True)

    return logging.getLogger("opena3.agent")


class JsonFormatter(logging.Formatter):
    """JSON-Formatter für strukturiertes Logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Extra-Felder hinzufügen (ohne sensible Daten)
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "context"):
            log_entry["context"] = record.context

        return json.dumps(log_entry, ensure_ascii=False)


logger = setup_logging()


# ══════════════════════════════════════════════════════════════════════════════
# Lifespan Handler (ersetzt @app.on_event)
# ══════════════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app):
    """
    Lifespan-Handler für FastAPI.
    Startup-Logik vor yield, Shutdown-Logik nach yield.
    """
    # === STARTUP ===
    logger.info("=" * 80)
    logger.info("🚀 opena3 (OpenWebUI Terminal Agent) v2.0 startet...")
    logger.info(f"   Port: {PORT}")
    logger.info(f"   Host: {HOST}")
    logger.info(f"   OpenWebUI URL: {OPENWEBUI_URL}")
    logger.info(f"   LocalAgent URL: {LOCALAGENT_URL}")
    logger.info(f"   Adapter URL: {OPENWEBUI_ADAPTER_URL}")
    logger.info(f"   Archiv: {ARCHIVE_DIR}")
    logger.info(f"   Modelle: {len(model_registry.available_aliases)} konfiguriert")
    logger.info(f"   Rate-Limiting: {'aktiviert' if rate_limit_config.enabled else 'deaktiviert'}")
    logger.info(f"   Max-Retries: {retry_config.max_retries}")
    logger.info(f"   Log-Level: {logging_config.level}")
    logger.info("=" * 80)

    # Prüfe Port-Policy (12344-12399 erlaubt, 8080 verboten)
    if PORT == 8080:
        logger.error("❌ FATAL: Port 8080 ist für Backend verboten (nur UI)!")
        sys.exit(1)

    if not PortPolicy.is_valid_port(PORT):
        logger.warning(f"⚠️  Port {PORT} außerhalb erlaubter Range (12344-12399)")

    # Erstelle Archiv-Struktur
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.touch(exist_ok=True)

    # Log verfügbare Modelle
    for alias in model_registry.available_aliases:
        model = model_registry.get_model(alias)
        if model:
            default_marker = " (default)" if model.default else ""
            logger.info(f"   📦 {alias} → {model.id}{default_marker}")

    logger.info("✅ opena3 bereit!")

    yield

    # === SHUTDOWN ===
    logger.info("🛑 opena3 wird beendet...")


# ══════════════════════════════════════════════════════════════════════════════
# FastAPI Application
# ══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="opena3 – OpenWebUI Terminal Agent",
    description="FastAPI-Wrapper für OpenWebUI mit Option-2-Flow-Compliance",
    version="2.0.0",
    docs_url="/docs" if os.getenv("DEV_MODE") == "true" else None,
    lifespan=lifespan,
)

security = HTTPBearer(auto_error=False)
startup_time = time.time()

# Rate-Limit Tracker (In-Memory, für Production: Redis empfohlen)
rate_limit_tracker: dict[str, dict[str, Any]] = defaultdict(lambda: {"count": 0, "reset_at": 0})


# ══════════════════════════════════════════════════════════════════════════════
# Rate-Limiting Middleware
# ══════════════════════════════════════════════════════════════════════════════


async def check_rate_limit(request: Request, endpoint: str = "default") -> bool:
    """
    Prüft Rate-Limit für Client.
    Gibt True zurück wenn erlaubt, wirft HTTPException bei Überschreitung.
    """
    if not rate_limit_config.enabled:
        return True

    # Client-Identifikation (IP oder API-Key)
    client_id = request.client.host if request.client else "unknown"
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        # Verwende Hash des Tokens als Client-ID
        client_id = f"token:{hash(auth_header)}"

    key = f"{client_id}:{endpoint}"
    now = time.time()

    # Wähle Limit basierend auf Endpoint
    if endpoint == "chat":
        limit = rate_limit_config.chat_requests_per_minute
    elif endpoint == "stream":
        limit = rate_limit_config.stream_requests_per_minute
    else:
        limit = rate_limit_config.client_requests_per_minute

    tracker = rate_limit_tracker[key]

    # Reset wenn Minute abgelaufen
    if now > tracker["reset_at"]:
        tracker["count"] = 0
        tracker["reset_at"] = now + 60

    tracker["count"] += 1

    if tracker["count"] > limit:
        retry_after = int(tracker["reset_at"] - now)
        logger.warning(f"⚠️ Rate-Limit überschritten für {client_id} auf {endpoint}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Zu viele Anfragen. Limit: {limit}/min",
                    "retry_after": retry_after,
                }
            },
            headers={"Retry-After": str(retry_after)},
        )

    return True


# ══════════════════════════════════════════════════════════════════════════════
# HTTP Client mit Retry & Exponential Backoff
# ══════════════════════════════════════════════════════════════════════════════


def http_request_with_retry(method: str, url: str, **kwargs) -> requests.Response:
    """
    HTTP-Request mit konfigurierbarem Retry und Exponential Backoff.

    HINWEIS: Verwendet synchrones `requests`-Modul.
    Für echte High-Load-Szenarien wäre `httpx.AsyncClient` sinnvoll.
    Aktuell bewusst sync, da LocalAgent-Pro/Ollama-Backend ebenfalls sync.

    Args:
        method: HTTP-Methode (GET, POST, etc.)
        url: Ziel-URL
        **kwargs: Weitere Argumente für requests

    Returns:
        Response-Objekt

    Raises:
        HTTPException: Bei nicht-retriable Fehlern oder nach max. Retries
    """
    last_exception = None

    for attempt in range(retry_config.max_retries + 1):
        try:
            # Timeout setzen falls nicht vorhanden
            if "timeout" not in kwargs:
                kwargs["timeout"] = TIMEOUT

            response = requests.request(method, url, **kwargs)

            # Erfolg oder nicht-retryable Status
            if response.status_code not in retry_config.retryable_status_codes:
                return response

            # Retryable Status-Code
            if attempt < retry_config.max_retries:
                delay = retry_config.get_delay(attempt)
                logger.warning(
                    f"🔄 Retry {attempt + 1}/{retry_config.max_retries} für {url} "
                    f"(Status: {response.status_code}, Delay: {delay:.1f}s)"
                )
                time.sleep(delay)
            else:
                # Letzter Versuch fehlgeschlagen
                return response

        except requests.exceptions.Timeout as e:
            last_exception = e
            if retry_config.retry_on_timeout and attempt < retry_config.max_retries:
                delay = retry_config.get_delay(attempt)
                logger.warning(f"🔄 Retry {attempt + 1}/{retry_config.max_retries} nach Timeout ({delay:.1f}s)")
                time.sleep(delay)
            else:
                logger.error(f"❌ Timeout nach {retry_config.max_retries + 1} Versuchen: {url}")
                raise HTTPException(
                    status_code=504,
                    detail={
                        "error": {
                            "code": "GATEWAY_TIMEOUT",
                            "message": f"Upstream-Timeout nach {kwargs.get('timeout', TIMEOUT)}s",
                            "url": url,
                        }
                    },
                )

        except requests.exceptions.ConnectionError as e:
            last_exception = e
            if retry_config.retry_on_connection_error and attempt < retry_config.max_retries:
                delay = retry_config.get_delay(attempt)
                logger.warning(
                    f"🔄 Retry {attempt + 1}/{retry_config.max_retries} nach Connection-Error ({delay:.1f}s)"
                )
                time.sleep(delay)
            else:
                logger.error(f"❌ Connection-Error nach {retry_config.max_retries + 1} Versuchen: {url}")
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": {
                            "code": "SERVICE_UNAVAILABLE",
                            "message": f"Upstream nicht erreichbar: {url}",
                            "details": str(e),
                        }
                    },
                )

    # Sollte nicht erreicht werden
    raise HTTPException(status_code=500, detail="Unexpected error in retry logic")


def handle_upstream_error(response: requests.Response, context: str = "") -> None:
    """
    Behandelt Upstream-Fehler mit strukturiertem Error-Mapping.
    Wirft HTTPException mit passenden Status-Codes.
    """
    status = response.status_code

    # Versuche JSON-Body zu parsen
    try:
        upstream_body = response.json()
    except:
        upstream_body = {"raw": response.text[:500]}

    error_detail = {
        "error": {
            "code": f"UPSTREAM_ERROR_{status}",
            "message": f"Upstream-Fehler bei {context}",
            "upstream_status": status,
            "upstream_body": upstream_body,
        }
    }

    # Status-Code Mapping
    if status >= 500:
        raise HTTPException(status_code=502, detail=error_detail)
    elif status == 404:
        raise HTTPException(status_code=404, detail=error_detail)
    elif status == 401:
        raise HTTPException(status_code=401, detail=error_detail)
    elif status == 429:
        raise HTTPException(status_code=429, detail=error_detail)
    else:
        raise HTTPException(status_code=status, detail=error_detail)


# ══════════════════════════════════════════════════════════════════════════════
# Pydantic Models (Strict JSON mit extra="forbid")
# ══════════════════════════════════════════════════════════════════════════════


class CommandRequest(BaseModel):
    """Command-Execution-Request"""

    model_config = ConfigDict(extra="forbid")

    command: str = Field(..., description="Auszuführender Befehl")
    context: dict[str, Any] | None = Field(default=None, description="Optionaler Kontext")
    timeout: int | None = Field(default=30, description="Timeout in Sekunden")


class InvokeRequest(BaseModel):
    """Direct Tool Invocation Request"""

    model_config = ConfigDict(extra="forbid")

    tool: str = Field(..., description="Tool-Name")
    parameters: dict[str, Any] = Field(..., description="Tool-Parameter")


class ChatRequest(BaseModel):
    """Chat-Request an OpenWebUI"""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(..., description="Chat-Nachricht")
    model: str | None = Field(default=None, description="Modell-Alias (z.B. 'llama3.1', 'gpt-4')")
    stream: bool = Field(default=False, description="Stream-Modus")

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str | None) -> str | None:
        """Validiert Modell-Alias gegen Registry"""
        if v is None:
            return v
        registry = get_model_registry()
        if v not in registry.available_aliases:
            available = ", ".join(registry.available_aliases)
            raise ValueError(f"Unbekanntes Modell: '{v}'. Verfügbar: {available}")
        return v


class StreamChatRequest(BaseModel):
    """SSE-Stream Chat-Request"""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(..., description="Chat-Nachricht")
    model: str | None = Field(default=None, description="Modell-Alias")
    context: dict[str, Any] | None = Field(default=None, description="Optionaler Kontext")

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str | None) -> str | None:
        if v is None:
            return v
        registry = get_model_registry()
        if v not in registry.available_aliases:
            available = ", ".join(registry.available_aliases)
            raise ValueError(f"Unbekanntes Modell: '{v}'. Verfügbar: {available}")
        return v


class HealthResponse(BaseModel):
    """Health-Check-Response"""

    status: str
    agent: str
    port: int
    uptime: float
    openwebui_available: bool
    models_count: int = 0


class ModelListResponse(BaseModel):
    """Response für /models/list"""

    models: list[dict[str, Any]]
    count: int
    default_model: str | None = None


class ErrorResponse(BaseModel):
    """Standard-Fehlerantwort"""

    error: dict[str, Any]


# ══════════════════════════════════════════════════════════════════════════════
# Safepoint Utilities (Append-Only Archivierung)
# ══════════════════════════════════════════════════════════════════════════════


def write_safepoint(src: str, dst: str, kind: str, body: dict[str, Any]) -> Path:
    """
    Schreibt Safepoint in YYYY/MM/DD-Struktur mit Unicode-Pfeil →
    Naming: SP<timestamp>_src→dst_{CMD|RESP}.json
    """
    today = datetime.now(UTC).strftime("%Y/%m/%d")
    target_dir = ARCHIVE_DIR / today
    target_dir.mkdir(parents=True, exist_ok=True)

    ts = int(time.time() * 1000)  # Millisekunden für Eindeutigkeit
    name = f"SP{ts}_{src}→{dst}_{kind}.json"
    fpath = target_dir / name

    payload = {
        "ts": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "src": src,
        "dst": dst,
        "kind": kind,
        "body": body,
        "strict": True,
    }

    # Schreibe Safepoint
    fpath.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Append to index (JSONL)
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with INDEX_FILE.open("a", encoding="utf-8") as idx:
        idx_entry = {
            "sp_id": f"SP{ts}",
            "timestamp": payload["ts"],
            "src": src,
            "dst": dst,
            "type": kind,
            "path": str(fpath.relative_to(ARCHIVE_DIR.parent)),
        }
        idx.write(json.dumps(idx_entry, ensure_ascii=False) + "\n")

    logger.info(f"✅ Safepoint erstellt: {name}")
    return fpath


def mask_secrets(data: Any) -> Any:
    """Maskiert sensible Daten in Logs/Safepoints"""
    if isinstance(data, dict):
        return {
            k: (
                "***MASKED***"
                if isinstance(k, str) and k.lower() in ["token", "password", "secret", "key", "bearer"]
                else mask_secrets(v)
            )
            for k, v in data.items()  # type: ignore[misc]
        }
    elif isinstance(data, list):
        return [mask_secrets(item) for item in data]
    return data


# ══════════════════════════════════════════════════════════════════════════════
# Auth Middleware
# ══════════════════════════════════════════════════════════════════════════════


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validiert Bearer Token (ENV-only)"""
    if not BEARER_TOKEN:
        logger.warning("⚠️  BEARER_TOKEN nicht gesetzt! Auth deaktiviert.")
        return True

    if credentials.credentials != BEARER_TOKEN:
        logger.error("❌ Ungültiger Token")
        raise HTTPException(status_code=401, detail="Ungültiger Token")

    return True


# ══════════════════════════════════════════════════════════════════════════════
# Health & Utility Endpoints
# ══════════════════════════════════════════════════════════════════════════════


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health-Check-Endpoint (Port-Policy-konform)"""
    uptime = time.time() - startup_time

    # Prüfe OpenWebUI-Verfügbarkeit
    openwebui_available = False
    try:
        resp = requests.get(f"{OPENWEBUI_URL}/health", timeout=5)
        openwebui_available = resp.status_code == 200
    except Exception as e:
        logger.debug(f"OpenWebUI-Check fehlgeschlagen: {e}")

    # Count available models
    models_count = 0
    try:
        if hasattr(model_registry, "available_aliases"):
            models_count = len(list(model_registry.available_aliases))
    except Exception:
        models_count = 0

    return HealthResponse(
        status="ok",
        agent="opena3",
        port=int(PORT),
        uptime=round(uptime, 2),
        openwebui_available=openwebui_available,
        models_count=models_count,
    )


@app.get("/")
async def root() -> dict[str, Any]:
    """Root-Endpoint mit Agent-Info"""
    return {
        "agent": "opena3",
        "kuerzel": "owuip",
        "port": PORT,
        "status": "running",
        "version": "2.0.0",
        "description": "OpenWebUI Terminal Agent – FastAPI-Wrapper mit Option-2-Flow-Compliance",
        "features": ["multi-model", "rate-limiting", "sse-streaming", "retry-backoff"],
    }


# ══════════════════════════════════════════════════════════════════════════════
# Models Endpoint (NEU)
# ══════════════════════════════════════════════════════════════════════════════


@app.get("/models/list", response_model=ModelListResponse)
@app.get("/v1/models", response_model=ModelListResponse)
async def list_models(
    request: Request, include_backend: bool = Query(default=True, description="Backend-Modelle einbeziehen")
) -> ModelListResponse:
    """
    Listet alle verfügbaren Modelle auf.
    Kombiniert Config-Modelle mit optionalen Backend-Modellen.

    Alias-Routes: /models/list, /v1/models (OpenAI-kompatibel)
    """
    await check_rate_limit(request, "default")

    models_list: list[dict[str, Any]] = list(model_registry.list_models())

    # Optional: Backend-Modelle hinzufügen (LocalAgent-Pro / Ollama)
    if include_backend:
        try:
            # LocalAgent-Pro Modelle
            resp = http_request_with_retry("GET", f"{LOCALAGENT_URL}/v1/models", timeout=5)
            if resp.status_code == 200:
                backend_models_data = resp.json().get("data", [])
                if isinstance(backend_models_data, list):
                    for bm in backend_models_data:
                        if isinstance(bm, dict):
                            # Prüfe ob bereits in Registry
                            model_id: str = bm.get("id", "")
                            if model_id and not any(m.get("id") == model_id for m in models_list):
                                models_list.append(
                                    {
                                        "alias": model_id,
                                        "id": model_id,
                                        "name": model_id,
                                        "type": "llm",
                                        "tags": ["backend", "ollama"],
                                        "default": False,
                                        "backend": "localagent",
                                    }
                                )
        except HTTPException:
            logger.debug("Backend-Modelle konnten nicht abgerufen werden")
        except Exception as e:
            logger.debug(f"Backend-Modelle Fehler: {e}")

    # Default-Modell ermitteln
    default_alias: str | None = None
    default_model_obj = model_registry.get_default_model()

    if default_model_obj is not None:
        available_aliases: list[str] = (
            list(model_registry.available_aliases) if hasattr(model_registry, "available_aliases") else []
        )
        for alias in available_aliases:
            model_info = model_registry.get_model(alias)
            if model_info is not None and isinstance(model_info, ModelInfo):
                if getattr(model_info, "default", False):
                    default_alias = alias
                    break

    return ModelListResponse(models=models_list, count=len(models_list), default_model=default_alias)


# ══════════════════════════════════════════════════════════════════════════════
# SSE-Streaming Chat Endpoint (NEU)
# ══════════════════════════════════════════════════════════════════════════════


async def generate_sse_stream(
    message: str, model_alias: str | None, context: dict[str, Any] | None, write_resp_safepoint: bool = True
) -> AsyncGenerator[str, None]:
    """
    Generator für SSE-Events.
    Streamt Antworten vom Backend zum Client.

    HINWEIS: Verwendet synchrones `requests.post` innerhalb async Generator.
    Für echte High-Load-Szenarien wäre `httpx.AsyncClient` sinnvoll.

    Args:
        message: Chat-Nachricht
        model_alias: Optional Modell-Alias
        context: Optionaler Kontext
        write_resp_safepoint: Ob RESP-Safepoint geschrieben werden soll

    Yields:
        SSE-formatierte Events (start, chunk, end, error)
    """
    # Modell-ID auflösen
    model_id = None
    backend = "localagent"

    if model_alias:
        model_info = model_registry.get_model(model_alias)
        if model_info:
            model_id = model_info.id
            backend = model_info.backend

    if not model_id:
        default = model_registry.get_default_model()
        model_id = default.id if default else "llama3.1:8b"

    # SSE-Event: Start
    yield f"event: start\ndata: {json.dumps({'model': model_id, 'backend': backend})}\n\n"

    try:
        # Request an Backend (LocalAgent-Pro)
        response = requests.post(
            f"{LOCALAGENT_URL}/v1/chat/completions",
            json={
                "model": model_id,
                "messages": [{"role": "user", "content": message}],
                "stream": False,  # LocalAgent-Pro unterstützt aktuell kein echtes Streaming
            },
            timeout=STREAM_TIMEOUT,
            stream=False,
        )

        if response.status_code != 200:
            error_msg = f"Backend-Fehler: {response.status_code}"
            yield f"event: error\ndata: {json.dumps({'error': error_msg})}\n\n"
            return

        data = response.json()
        content = ""

        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0].get("message", {}).get("content", "")

        # Simuliere Streaming durch chunk-weise Ausgabe
        chunk_size = 20
        for i in range(0, len(content), chunk_size):
            chunk = content[i : i + chunk_size]
            yield f"event: chunk\ndata: {json.dumps({'content': chunk, 'index': i})}\n\n"
            await asyncio.sleep(0.02)  # Kleine Pause für realistisches Streaming

        # SSE-Event: End
        yield f"event: end\ndata: {json.dumps({'total_length': len(content), 'model': model_id})}\n\n"

        # RESP-Safepoint für erfolgreichen Stream
        if write_resp_safepoint:
            resp_body = {
                "model": model_id,
                "backend": backend,
                "total_length": len(content),
                "status": "ok",
                "preview": content[:100] if content else "",
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            }
            write_safepoint("opena3", "dashboard", "RESP", resp_body)

    except requests.exceptions.Timeout:
        yield f"event: error\ndata: {json.dumps({'error': 'Timeout', 'code': 'GATEWAY_TIMEOUT'})}\n\n"
        # RESP-Safepoint für Timeout-Error
        if write_resp_safepoint:
            write_safepoint(
                "opena3",
                "dashboard",
                "RESP",
                {
                    "model": model_id,
                    "status": "error",
                    "error_code": "GATEWAY_TIMEOUT",
                    "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                },
            )
    except requests.exceptions.ConnectionError:
        yield f"event: error\ndata: {json.dumps({'error': 'Backend nicht erreichbar', 'code': 'SERVICE_UNAVAILABLE'})}\n\n"
        # RESP-Safepoint für Connection-Error
        if write_resp_safepoint:
            write_safepoint(
                "opena3",
                "dashboard",
                "RESP",
                {
                    "model": model_id,
                    "status": "error",
                    "error_code": "SERVICE_UNAVAILABLE",
                    "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                },
            )
    except Exception as e:
        logger.error(f"SSE-Stream Fehler: {e}")
        yield f"event: error\ndata: {json.dumps({'error': str(e), 'code': 'INTERNAL_ERROR'})}\n\n"
        # RESP-Safepoint für generischen Error
        if write_resp_safepoint:
            write_safepoint(
                "opena3",
                "dashboard",
                "RESP",
                {
                    "model": model_id,
                    "status": "error",
                    "error_code": "INTERNAL_ERROR",
                    "error_message": str(e)[:200],
                    "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                },
            )


@app.post("/chat/stream")
async def chat_stream(request: Request, body: StreamChatRequest):
    """
    SSE-basierter Chat-Stream.
    Streamt Antworten als Server-Sent Events.

    Event-Typen:
    - start: Stream beginnt (model, backend info)
    - chunk: Text-Chunk (content, index)
    - end: Stream beendet (total_length, model)
    - error: Fehler aufgetreten (error, code)
    """
    await check_rate_limit(request, "stream")

    logger.info(f"🌊 Stream-Request: {body.message[:50]}... (model: {body.model})")

    # CMD-Safepoint
    cmd_body = {
        "message": body.message[:200],
        "model": body.model,
        "stream": True,
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    write_safepoint("dashboard", "opena3", "CMD", cmd_body)

    return StreamingResponse(
        generate_sse_stream(body.message, body.model, body.context),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


# ══════════════════════════════════════════════════════════════════════════════
# Command & Invoke Endpoints (Option-2-Flow-konform)
# ══════════════════════════════════════════════════════════════════════════════


@app.post("/command")
async def execute_command(request: Request, body: CommandRequest, authorized: bool = Depends(verify_token)):
    """
    Command-Execution-Endpoint
    Erzeugt CMD-Safepoint, führt Befehl aus, erzeugt RESP-Safepoint
    """
    await check_rate_limit(request, "default")

    logger.info(f"📥 Command erhalten: {body.command}")

    # CMD-Safepoint
    cmd_body = {
        "command": body.command,
        "context": mask_secrets(body.context) if body.context else {},
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    write_safepoint("kordp", "opena3", "CMD", cmd_body)

    try:
        # Simuliere Befehlsausführung (später: echte OpenWebUI-Integration)
        result = {
            "status": "executed",
            "command": body.command,
            "output": f"Command '{body.command}' würde hier ausgeführt (Placeholder)",
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }

        # RESP-Safepoint
        write_safepoint("opena3", "kordp", "RESP", result)

        return JSONResponse(content=result, status_code=200)

    except Exception as e:
        logger.error(f"❌ Command-Fehler: {e}")
        error = {"error": {"code": "COMMAND_EXECUTION_FAILED", "message": str(e), "details": {"command": body.command}}}
        write_safepoint("opena3", "kordp", "RESP", error)
        raise HTTPException(status_code=500, detail=error)


@app.post("/invoke")
async def invoke_tool(request: Request, body: InvokeRequest, authorized: bool = Depends(verify_token)):
    """
    Direct Tool Invocation
    Ruft OpenWebUI-Adapter für Tool-Ausführung
    """
    await check_rate_limit(request, "default")

    logger.info(f"🔧 Tool-Invoke: {body.tool}")

    # CMD-Safepoint
    cmd_body = {
        "tool": body.tool,
        "parameters": mask_secrets(body.parameters),
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    write_safepoint("kordp", "opena3", "CMD", cmd_body)

    try:
        # Forward zu OpenWebUI-Adapter mit Retry
        resp = http_request_with_retry(
            "POST",
            f"{OPENWEBUI_ADAPTER_URL}/tool/invoke",
            json={"tool": body.tool, "parameters": body.parameters},
            timeout=TIMEOUT,
        )

        if resp.status_code >= 400:
            handle_upstream_error(resp, f"Tool-Invoke: {body.tool}")

        result = resp.json()

        # RESP-Safepoint
        write_safepoint("opena3", "kordp", "RESP", result)

        return JSONResponse(content=result, status_code=resp.status_code)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Invoke-Fehler: {e}")
        error = {"error": {"code": "INVOKE_FAILED", "message": str(e), "details": {"tool": body.tool}}}
        write_safepoint("opena3", "kordp", "RESP", error)
        raise HTTPException(status_code=500, detail=error)


@app.post("/chat")
@app.post("/v1/chat/completions")
async def chat(request: Request, body: ChatRequest, authorized: bool = Depends(verify_token)):
    """
    Chat-Endpoint für OpenWebUI-Interaktion
    Leitet Chat-Anfragen an LocalAgent-Pro weiter mit Multi-Model-Support

    Alias-Routes: /chat, /v1/chat/completions (OpenAI-kompatibel)

    HINWEIS: Verwendet synchrones `requests`-Modul für Backend-Calls.
    Für echte High-Load-Szenarien wäre `httpx.AsyncClient` sinnvoll.
    """
    await check_rate_limit(request, "chat")

    logger.info(f"💬 Chat-Request: {body.message[:50]}... (model: {body.model})")

    # Modell-ID auflösen
    model_id = None
    if body.model:
        model_info = model_registry.get_model(body.model)
        if model_info:
            model_id = model_info.id

    if not model_id:
        default = model_registry.get_default_model()
        model_id = default.id if default else "llama3.1:8b"

    # CMD-Safepoint
    cmd_body = {
        "message": body.message[:200],  # Truncate für Safepoint
        "model": model_id,
        "stream": body.stream,
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    write_safepoint("dashboard", "opena3", "CMD", cmd_body)

    try:
        # Forward zu LocalAgent-Pro mit Retry
        resp = http_request_with_retry(
            "POST",
            f"{LOCALAGENT_URL}/v1/chat/completions",
            json={"model": model_id, "messages": [{"role": "user", "content": body.message}]},
            timeout=TIMEOUT,
        )

        if resp.status_code >= 400:
            handle_upstream_error(resp, "Chat-Request")

        result = resp.json()

        # Extrahiere Content für Safepoint
        content = ""
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0].get("message", {}).get("content", "")

        # RESP-Safepoint
        resp_body = {
            "model": model_id,
            "content_length": len(content),
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }
        write_safepoint("opena3", "dashboard", "RESP", resp_body)

        return JSONResponse(content=result, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Chat-Fehler: {e}")
        error = {"error": {"code": "CHAT_FAILED", "message": str(e), "details": {"message": body.message[:100]}}}
        write_safepoint("opena3", "dashboard", "RESP", error)
        raise HTTPException(status_code=500, detail=error)


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # PID-File schreiben
    pid_file = Path("logs") / "opena3.pid"
    pid_file.parent.mkdir(exist_ok=True)
    pid_file.write_text(str(os.getpid()))

    logger.info(f"📝 PID {os.getpid()} geschrieben nach {pid_file}")

    # Start uvicorn
    uvicorn.run(app, host=HOST, port=PORT, log_level=logging_config.level.lower(), access_log=True)
