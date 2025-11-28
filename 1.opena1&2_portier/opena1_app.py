# path: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/opena1_app.py
"""
OpenA1 = Coordinator (kordp)
- Fester Port: 12344 (Port-Policy 12344–12399)
- Fester BASE_ROOT: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt
- Endpunkte:
  * GET  /health
  * POST /log/opena1
  * POST /dispatch/kordp
  * POST /route/update
- OpenAI-KEY-Integration (ENV):
  * Liest OPENAI_API_KEY/OPENAI_BASE_URL/OPENAI_ORG aus Umgebungsvariablen.
  * Validiert Präsenz (keine Ausführung, kein Loggen des Secrets).
  * Redaction-Filter verhindert, dass Keys in Safepoints/Logs landen.
"""
from __future__ import annotations

import hashlib
import json
import os
import socket
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
import httpx

# -------- PORTABLE PATHS (Server-Transfer Ready) --------
# Nutze zentrale paths_config.py für Single Source of Truth
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from paths_config import BASE_ROOT, PORTIER_DIR, ARCHIVP_STORE, ARCHIVP_INDEX
ALLOWED_TOP = {
    "1.opena1&2_portier","2.opena3_openwebui","3.opena4_telegram","4.opena5_vscode","5.opena6_browser",
    "6.opena7_email","7.opena8_whatsapp","8.opena9_telephone","9.opena10_call_tracking","10.opena11_unlock",
    "11.opena12_social_media","12.opena13_influencer","13.opena14_calendar","14.opena15_html","15.opena16_shop",
    "16.opena17_homepagecreator","17.opena18_CMR","18.opena19_Aktien&Crypto","19.opena20_dashboard_agent",
    "20.opena21_workflow"
}
PORT = 12344
ARCHIVP_PORT = 12345  # OpenA2

# -------- OpenAI Key (ENV) --------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_ORG = os.getenv("OPENAI_ORG", "")

def _key_fingerprint(secret: str) -> str:
    """Gibt eine kurze, nicht rückrechenbare Kennung zurück (sha256/8)."""
    if not secret:
        return ""
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()[:8]

OPENAI_PRESENT = bool(OPENAI_API_KEY)
OPENAI_FP = _key_fingerprint(OPENAI_API_KEY)

REDACT_KEYS = {
    "authorization", "openai_api_key", "api_key", "openai-key", "x-api-key",
    "OPENAI_API_KEY", "OPENAI_ORG", "OPENAI_BASE_URL", "bearer"
}

def _redact_secrets(obj: Any) -> Any:
    """Entfernt/verschleiert sicherheitsrelevante Felder rekursiv."""
    if isinstance(obj, dict):
        sanitized: Dict[str, Any] = {}
        for k, v in obj.items():
            kl = str(k).lower()
            if kl in REDACT_KEYS or "token" in kl or "secret" in kl or "key" in kl:
                sanitized[k] = "***REDACTED***"
            else:
                sanitized[k] = _redact_secrets(v)
        return sanitized
    if isinstance(obj, list):
        return [_redact_secrets(x) for x in obj]
    return obj

def _guard_path(p: Path) -> None:
    p = p.resolve()
    if not str(p).startswith(str(BASE_ROOT)):
        raise PermissionError("PATH_VIOLATION: outside BASE_ROOT")
    rel = p.relative_to(BASE_ROOT)
    top = rel.parts[0] if rel.parts else ""
    if top not in ALLOWED_TOP:
        raise PermissionError(f"DIR_NOT_WHITELISTED: {top}")

def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"

def _hostname() -> str:
    try:
        return socket.gethostname()
    except Exception:
        return "unknown-host"

class LogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source: str = Field(..., min_length=1)
    event: str = Field(..., min_length=1)
    payload: Dict[str, Any] = Field(default_factory=dict)
    strict: bool = True
    ts: str = Field(default_factory=_now)

class DispatchIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agent: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    data: Dict[str, Any] = Field(default_factory=dict)
    request_id: str = Field(default_factory=lambda: f"req-{int(time.time()*1000)}")
    strict: bool = True

class RouteUpdateIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agent: str
    agent_id: str
    port: int
    program: str
    archivator_port: int
    mapping_ts: str
    mapping: Dict[str, Any]

app = FastAPI(title="OpenA1 Coordinator (kordp)", version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROUTES: Dict[str, Dict[str, Any]] = {}
APP_META = {
    "service": "opena1",
    "role": "coordinator",
    "host": _hostname(),
    "base_root": str(BASE_ROOT),
    "port": PORT,
    "archivp_port": ARCHIVP_PORT,
    "strict": True,
}

async def _store_safepoint(kind: str, body: Dict[str, Any]) -> None:
    """
    Delegiert Safepoint-Speicherung an OpenA2 (/store/archivp) – mit Redaction.
    """
    url = f"http://127.0.0.1:{ARCHIVP_PORT}/store/archivp"
    payload = {
        "src": "kordp",
        "dst": "archivp",
        "kind": kind,
        "body": _redact_secrets(body),
        "strict": True,
        "ts": _now()
    }
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()

@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        **APP_META,
        "routes_count": len(ROUTES),
        "openai_key_present": OPENAI_PRESENT,
        "openai_fp": OPENAI_FP,
        "openai_base_url": OPENAI_BASE_URL,
    }

@app.post("/log/opena1")
async def log_event(entry: LogEntry) -> Dict[str, Any]:
    # Log an Archivp weiterreichen
    await _store_safepoint("LOG", entry.model_dump())
    return {"ok": True, "logged": True, "strict": True}

@app.post("/route/update")
async def route_update(info: RouteUpdateIn) -> Dict[str, Any]:
    # strikte Ports
    if not (12344 <= info.port <= 12399) or not (12344 <= info.archivator_port <= 12399):
        raise HTTPException(400, "PORT_POLICY_VIOLATION")
    ROUTES[info.agent] = {
        "agent_id": info.agent_id,
        "port": info.port,
        "program": info.program,
        "archivator_port": info.archivator_port,
        "mapping_ts": info.mapping_ts,
    }
    await _store_safepoint("ROUTE", {"agent": info.agent, "route": ROUTES[info.agent]})
    return {"ok": True, "route": ROUTES[info.agent], "strict": True}

@app.post("/dispatch/kordp")
async def dispatch_task(req: DispatchIn) -> Dict[str, Any]:
    """
    Akzeptiert einen Auftragsbefehl und leitet Metadaten als Safepoint an OpenA2 weiter.
    Die tatsächliche Ausführung kann durch Worker außerhalb erfolgen; hier wird nur die
    Dispatch-Registrierung und Routenauflösung erledigt.
    """
    route: Optional[Dict[str, Any]] = ROUTES.get(req.agent)
    if not route:
        raise HTTPException(404, f"no route for agent '{req.agent}'")
    # Sicherstellen, dass Key nicht im Payload steckt
    safe_data = _redact_secrets(req.data)
    await _store_safepoint("DISPATCH", {"request_id": req.request_id, "agent": req.agent, "action": req.action, "data": safe_data, "route": route})
    return {"ok": True, "routed_to": route, "request_id": req.request_id, "strict": True}

if __name__ == "__main__":
    # uvicorn Start nur, wenn explizit als Skript ausgeführt
    import uvicorn
    uvicorn.run("opena1_app:app", host="127.0.0.1", port=PORT, reload=False, access_log=False)
