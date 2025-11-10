# path: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/opena1_app.py
"""
OpenA1 = Coordinator (kordp)
- Fester Port: 12344 (Port-Policy 12344–12399)
- Fester BASE_ROOT: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt
- Feste Endpunkte:
  * GET  /health
  * POST /log/opena1
  * POST /dispatch/kordp
  * POST /route/update  (von Copilot/Tools genutzt, um Transfers korrekt zu setzen)
- Keine Erstellung neuer Top-Level-Ordner.
- Safepoints werden an OpenA2 (archivp) übergeben.
"""
from __future__ import annotations

import json
import os
import socket
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, ConfigDict
import httpx

BASE_ROOT = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt").resolve()
ALLOWED_TOP = {
    "1.opena1&2_portier","2.opena3_openwebui","3.opena4_telegram","4.opena5_vscode","5.opena6_browser",
    "6.opena7_email","7.opena8_whatsapp","8.opena9_telephone","9.opena10_call_tracking","10.opena11_unlock",
    "11.opena12_social_media","12.opena13_influencer","13.opena14_calendar","14.opena15_html","15.opena16_shop",
    "16.opena17_homepagecreator","17.opena18_CMR","18.opena19_Aktien&Crypto","19.opena20_dashboard_agent",
    "20.opena21_workflow"
}
PORT = 12344
ARCHIVP_PORT = 12345  # OpenA2

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
    Delegiert Safepoint-Speicherung an OpenA2 (/store/archivp).
    """
    url = f"http://127.0.0.1:{ARCHIVP_PORT}/store/archivp"
    payload = {
        "src": "kordp",
        "dst": "archivp",
        "kind": kind,
        "body": body,
        "strict": True,
        "ts": _now()
    }
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()

@app.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "ok", **APP_META, "routes_count": len(ROUTES)}

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
    await _store_safepoint("DISPATCH", {"request_id": req.request_id, "agent": req.agent, "action": req.action, "data": req.data, "route": route})
    return {"ok": True, "routed_to": route, "request_id": req.request_id, "strict": True}

if __name__ == "__main__":
    # uvicorn Start nur, wenn explizit als Skript ausgeführt
    import uvicorn
    uvicorn.run("opena1_app:app", host="127.0.0.1", port=PORT, reload=False, access_log=False)
