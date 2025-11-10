# path: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/opena2_app.py
"""
OpenA2 = Archivator (archivp)
- Fester Port: 12345
- Fester BASE_ROOT: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt
- Feste Endpunkte:
  * GET  /health
  * POST /store/archivp    (Safepoints/Logs speichern)
  * POST /finalize/opena2  (Abschlussmeldung/Audit)
- Speichert unter: 1.opena1&2_portier/archivp_store/YYYY/MM/DD/SP<ts>_<src>→<dst>_<kind>.json
- Keine Erstellung neuer Top-Level-Ordner.
"""
from __future__ import annotations

import json
import os
import socket
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict

BASE_ROOT = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt").resolve()
ALLOWED_TOP = {
    "1.opena1&2_portier","2.opena3_openwebui","3.opena4_telegram","4.opena5_vscode","5.opena6_browser",
    "6.opena7_email","7.opena8_whatsapp","8.opena9_telephone","9.opena10_call_tracking","10.opena11_unlock",
    "11.opena12_social_media","12.opena13_influencer","13.opena14_calendar","14.opena15_html","15.opena16_shop",
    "16.opena17_homepagecreator","17.opena18_CMR","18.opena19_Aktien&Crypto","19.opena20_dashboard_agent",
    "20.opena21_workflow"
}
PORT = 12345

ARCHIVE_DIR = BASE_ROOT / "1.opena1&2_portier" / "archivp_store"
INDEX_FILE = BASE_ROOT / "1.opena1&2_portier" / "archivp_store" / "index.jsonl"

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

class StoreIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    src: str
    dst: str
    kind: str
    body: Dict[str, Any] = Field(default_factory=dict)
    strict: bool = True
    ts: str = Field(default_factory=_now)

class FinalizeIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ticket: str
    status: str
    notes: str | None = None
    strict: bool = True
    ts: str = Field(default_factory=_now)

app = FastAPI(title="OpenA2 Archivator (archivp)", version="1.0.0")

def _write_safepoint(item: StoreIn) -> Path:
    day = datetime.utcnow()
    target_dir = ARCHIVE_DIR / f"{day:%Y/%m/%d}"
    _guard_path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    # Dateiname: SP<ts>_<src>→<dst>_<kind>.json
    ts = int(time.time())
    name = f"SP{ts}_{item.src}→{item.dst}_{item.kind}.json"
    fpath = target_dir / name
    content = item.model_dump()
    content.setdefault("strict", True)
    fpath.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    # Index aktualisieren
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with INDEX_FILE.open("a", encoding="utf-8") as idx:
        idx.write(json.dumps({"sp": name, "ts": item.ts, "src": item.src, "dst": item.dst, "kind": item.kind, "path": str(fpath)}) + "\n")
    return fpath

@app.get("/health")
async def health() -> Dict[str, Any]:
    count = 0
    if INDEX_FILE.exists():
        count = sum(1 for _ in INDEX_FILE.open("r", encoding="utf-8"))
    return {"status": "ok", "service": "opena2", "role": "archivp", "host": _hostname(), "base_root": str(BASE_ROOT), "port": PORT, "entries": count, "strict": True}

@app.post("/store/archivp")
async def store(item: StoreIn) -> Dict[str, Any]:
    try:
        path = _write_safepoint(item)
        return {"ok": True, "stored": str(path), "strict": True}
    except PermissionError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/finalize/opena2")
async def finalize(fin: FinalizeIn) -> Dict[str, Any]:
    # Abschluss-Safepoint
    sp = StoreIn(src="finalizer", dst="archivp", kind="FINALIZE", body={"ticket": fin.ticket, "status": fin.status, "notes": fin.notes})
    path = _write_safepoint(sp)
    return {"ok": True, "finalized": fin.ticket, "stored": str(path), "strict": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("opena2_app:app", host="127.0.0.1", port=PORT, reload=False, access_log=False)
