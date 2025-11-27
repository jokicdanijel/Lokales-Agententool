#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
opena3 – OpenWebUI Terminal Agent
Port: 12347 | Kürzel: owuip
Zweck: FastAPI-Wrapper für OpenWebUI-Interaktionen mit Option-2-Flow-Compliance
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, Extra
import requests
import uvicorn

# ══════════════════════════════════════════════════════════════════════════════
# Configuration (ENV-only, niemals hardcoded)
# ══════════════════════════════════════════════════════════════════════════════

PORT = int(os.getenv("OPENA3_PORT", "12347"))
HOST = os.getenv("OPENA3_HOST", "127.0.0.1")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://127.0.0.1:8080")
OPENWEBUI_ADAPTER_URL = os.getenv("OPENWEBUI_ADAPTER_URL", "http://127.0.0.1:12350")
TIMEOUT = int(os.getenv("OPENA3_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("OPENA3_MAX_RETRIES", "3"))

# Safepoint-Archiv
BASE_ROOT = Path(os.getenv("BASE_ROOT", Path.cwd().parent))
ARCHIVE_DIR = BASE_ROOT / "1.opena1&2_portier" / "archivp_store"
INDEX_FILE = ARCHIVE_DIR / "index.jsonl"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path("logs") / "opena3.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("opena3.agent")

# ══════════════════════════════════════════════════════════════════════════════
# FastAPI Application
# ══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="opena3 – OpenWebUI Terminal Agent",
    description="FastAPI-Wrapper für OpenWebUI mit Option-2-Flow-Compliance",
    version="1.0.0",
    docs_url="/docs" if os.getenv("DEV_MODE") == "true" else None
)

security = HTTPBearer()
startup_time = time.time()

# ══════════════════════════════════════════════════════════════════════════════
# Pydantic Models (Strict JSON mit extra="forbid")
# ══════════════════════════════════════════════════════════════════════════════

class CommandRequest(BaseModel):
    """Command-Execution-Request"""
    command: str = Field(..., description="Auszuführender Befehl")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optionaler Kontext")
    timeout: Optional[int] = Field(default=30, description="Timeout in Sekunden")
    
    class Config:
        extra = Extra.forbid  # Strict Mode: Keine zusätzlichen Felder erlaubt


class InvokeRequest(BaseModel):
    """Direct Tool Invocation Request"""
    tool: str = Field(..., description="Tool-Name")
    parameters: Dict[str, Any] = Field(..., description="Tool-Parameter")
    
    class Config:
        extra = Extra.forbid


class ChatRequest(BaseModel):
    """Chat-Request an OpenWebUI"""
    message: str = Field(..., description="Chat-Nachricht")
    model: Optional[str] = Field(default=None, description="Modell-ID")
    stream: bool = Field(default=False, description="Stream-Modus")
    
    class Config:
        extra = Extra.forbid


class HealthResponse(BaseModel):
    """Health-Check-Response"""
    status: str
    agent: str
    port: int
    uptime: float
    openwebui_available: bool


class ErrorResponse(BaseModel):
    """Standard-Fehlerantwort"""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None


# ══════════════════════════════════════════════════════════════════════════════
# Safepoint Utilities (Append-Only Archivierung)
# ══════════════════════════════════════════════════════════════════════════════

def write_safepoint(src: str, dst: str, kind: str, body: Dict[str, Any]) -> Path:
    """
    Schreibt Safepoint in YYYY/MM/DD-Struktur mit Unicode-Pfeil →
    Naming: SP<timestamp>_src→dst_{CMD|RESP}.json
    """
    today = datetime.utcnow().strftime("%Y/%m/%d")
    target_dir = ARCHIVE_DIR / today
    target_dir.mkdir(parents=True, exist_ok=True)
    
    ts = int(time.time() * 1000)  # Millisekunden für Eindeutigkeit
    name = f"SP{ts}_{src}→{dst}_{kind}.json"
    fpath = target_dir / name
    
    payload = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "src": src,
        "dst": dst,
        "kind": kind,
        "body": body,
        "strict": True
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
            "path": str(fpath.relative_to(ARCHIVE_DIR.parent))
        }
        idx.write(json.dumps(idx_entry, ensure_ascii=False) + "\n")
    
    logger.info(f"✅ Safepoint erstellt: {name}")
    return fpath


def mask_secrets(data: Any) -> Any:
    """Maskiert sensible Daten in Logs/Safepoints"""
    if isinstance(data, dict):
        return {k: "***MASKED***" if k.lower() in ["token", "password", "secret", "key", "bearer"] else mask_secrets(v) for k, v in data.items()}
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
    
    return HealthResponse(
        status="ok",
        agent="opena3",
        port=PORT,
        uptime=round(uptime, 2),
        openwebui_available=openwebui_available
    )


@app.get("/")
async def root():
    """Root-Endpoint mit Agent-Info"""
    return {
        "agent": "opena3",
        "kuerzel": "owuip",
        "port": PORT,
        "status": "running",
        "description": "OpenWebUI Terminal Agent – FastAPI-Wrapper mit Option-2-Flow-Compliance"
    }


# ══════════════════════════════════════════════════════════════════════════════
# Command & Invoke Endpoints (Option-2-Flow-konform)
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/command")
async def execute_command(request: CommandRequest, authorized: bool = Depends(verify_token)):
    """
    Command-Execution-Endpoint
    Erzeugt CMD-Safepoint, führt Befehl aus, erzeugt RESP-Safepoint
    """
    logger.info(f"📥 Command erhalten: {request.command}")
    
    # CMD-Safepoint
    cmd_body = {
        "command": request.command,
        "context": mask_secrets(request.context) if request.context else {},
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    write_safepoint("kordp", "opena3", "CMD", cmd_body)
    
    try:
        # Simuliere Befehlsausführung (später: echte OpenWebUI-Integration)
        result = {
            "status": "executed",
            "command": request.command,
            "output": f"Command '{request.command}' würde hier ausgeführt (Placeholder)",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # RESP-Safepoint
        write_safepoint("opena3", "kordp", "RESP", result)
        
        return JSONResponse(content=result, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Command-Fehler: {e}")
        error = {
            "error_code": "COMMAND_EXECUTION_FAILED",
            "message": str(e),
            "details": {"command": request.command}
        }
        write_safepoint("opena3", "kordp", "RESP", error)
        raise HTTPException(status_code=500, detail=error)


@app.post("/invoke")
async def invoke_tool(request: InvokeRequest, authorized: bool = Depends(verify_token)):
    """
    Direct Tool Invocation
    Ruft OpenWebUI-Adapter für Tool-Ausführung
    """
    logger.info(f"🔧 Tool-Invoke: {request.tool}")
    
    # CMD-Safepoint
    cmd_body = {
        "tool": request.tool,
        "parameters": mask_secrets(request.parameters),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    write_safepoint("kordp", "opena3", "CMD", cmd_body)
    
    try:
        # Forward zu OpenWebUI-Adapter (Port 12350)
        resp = requests.post(
            f"{OPENWEBUI_ADAPTER_URL}/tool/invoke",
            json={"tool": request.tool, "parameters": request.parameters},
            timeout=TIMEOUT
        )
        
        result = resp.json()
        
        # RESP-Safepoint
        write_safepoint("opena3", "kordp", "RESP", result)
        
        return JSONResponse(content=result, status_code=resp.status_code)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Adapter unreachable: {e}")
        error = {
            "error_code": "ADAPTER_UNREACHABLE",
            "message": f"OpenWebUI-Adapter (Port 12350) nicht erreichbar: {str(e)}",
            "details": {"tool": request.tool}
        }
        write_safepoint("opena3", "kordp", "RESP", error)
        raise HTTPException(status_code=502, detail=error)


@app.post("/chat")
async def chat(request: ChatRequest, authorized: bool = Depends(verify_token)):
    """
    Chat-Endpoint für OpenWebUI-Interaktion
    Leitet Chat-Anfragen an OpenWebUI weiter (via Adapter)
    """
    logger.info(f"💬 Chat-Request: {request.message[:50]}...")
    
    # CMD-Safepoint
    cmd_body = {
        "message": request.message,
        "model": request.model,
        "stream": request.stream,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    write_safepoint("dashboard", "opena3", "CMD", cmd_body)
    
    try:
        # Forward zu OpenWebUI-Adapter
        resp = requests.post(
            f"{OPENWEBUI_ADAPTER_URL}/openwebui/chat",
            json={"message": request.message, "model": request.model, "stream": request.stream},
            timeout=TIMEOUT
        )
        
        result = resp.json()
        
        # RESP-Safepoint
        write_safepoint("opena3", "dashboard", "RESP", result)
        
        return JSONResponse(content=result, status_code=resp.status_code)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Chat-Fehler: {e}")
        error = {
            "error_code": "CHAT_FAILED",
            "message": str(e),
            "details": {"message": request.message[:100]}
        }
        write_safepoint("opena3", "dashboard", "RESP", error)
        raise HTTPException(status_code=502, detail=error)


# ══════════════════════════════════════════════════════════════════════════════
# Startup & Main
# ══════════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    """Startup-Event: Validierung & Initialisierung"""
    logger.info("=" * 80)
    logger.info("🚀 opena3 (OpenWebUI Terminal Agent) startet...")
    logger.info(f"   Port: {PORT}")
    logger.info(f"   Host: {HOST}")
    logger.info(f"   OpenWebUI URL: {OPENWEBUI_URL}")
    logger.info(f"   Adapter URL: {OPENWEBUI_ADAPTER_URL}")
    logger.info(f"   Archiv: {ARCHIVE_DIR}")
    logger.info("=" * 80)
    
    # Prüfe Port-Policy (12344-12399 erlaubt, 8080 verboten)
    if PORT == 8080:
        logger.error("❌ FATAL: Port 8080 ist für Backend verboten (nur UI)!")
        sys.exit(1)
    
    if not (12344 <= PORT <= 12399):
        logger.warning(f"⚠️  Port {PORT} außerhalb erlaubter Range (12344-12399)")
    
    # Erstelle Archiv-Struktur
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.touch(exist_ok=True)
    
    logger.info("✅ opena3 bereit!")


if __name__ == "__main__":
    # PID-File schreiben
    pid_file = Path("logs") / "opena3.pid"
    pid_file.parent.mkdir(exist_ok=True)
    pid_file.write_text(str(os.getpid()))
    
    logger.info(f"📝 PID {os.getpid()} geschrieben nach {pid_file}")
    
    # Start uvicorn
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level=LOG_LEVEL.lower(),
        access_log=True
    )
