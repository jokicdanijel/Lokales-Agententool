# path: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/opena2_app.py
"""
OpenA2 = Archivator (archivp)
- Fester Port: 12345
- Fester BASE_ROOT: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt
- Endpunkte:
  * GET  /health
  * POST /store/archivp
  * POST /finalize/opena2
- OpenAI-KEY-Integration (ENV):
  * Liest OPENAI_API_KEY/OPENAI_BASE_URL/OPENAI_ORG nur zur Präsenzanzeige/Redaction.
  * Speichert KEIN Secret; Redaction filtert sensible Felder weg.
- Speicherort: 1.opena1&2_portier/archivp_store/YYYY/MM/DD/SP<ts>_<src>→<dst>_<kind>.json
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
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict

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
PORT = 12345

ARCHIVE_DIR = ARCHIVP_STORE
INDEX_FILE = ARCHIVP_INDEX

# -------- OpenAI Key (ENV) --------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_ORG = os.getenv("OPENAI_ORG", "")

def _key_fingerprint(secret: str) -> str:
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
    if isinstance(obj, dict):
        san: Dict[str, Any] = {}
        for k, v in obj.items():
            kl = str(k).lower()
            if kl in REDACT_KEYS or "token" in kl or "secret" in kl or "key" in kl:
                san[k] = "***REDACTED***"
            else:
                san[k] = _redact_secrets(v)
        return san
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
    ts = int(time.time())
    name = f"SP{ts}_{item.src}→{item.dst}_{item.kind}.json"
    fpath = target_dir / name
    content = item.model_dump()
    content["body"] = _redact_secrets(content.get("body", {}))
    content.setdefault("strict", True)
    fpath.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with INDEX_FILE.open("a", encoding="utf-8") as idx:
        idx.write(json.dumps({"sp": name, "ts": item.ts, "src": item.src, "dst": item.dst, "kind": item.kind, "path": str(fpath)}) + "\n")
    return fpath

@app.get("/health")
async def health() -> Dict[str, Any]:
    count = 0
    if INDEX_FILE.exists():
        count = sum(1 for _ in INDEX_FILE.open("r", encoding="utf-8"))
    return {
        "status": "ok",
        "service": "opena2",
        "role": "archivp",
        "host": _hostname(),
        "base_root": str(BASE_ROOT),
        "port": PORT,
        "entries": count,
        "openai_key_present": OPENAI_PRESENT,
        "openai_fp": OPENAI_FP,
        "openai_base_url": OPENAI_BASE_URL,
        "strict": True
    }

@app.post("/store/archivp")
async def store(item: StoreIn) -> Dict[str, Any]:
    try:
        path = _write_safepoint(item)
        return {"ok": True, "stored": str(path), "strict": True}
    except PermissionError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/finalize/opena2")
async def finalize(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Accept CMD envelope from opena1, store as safepoint, return OK.
    Expected body: {request_id, timestamp, source, cmd{...}, strict}
    """
    req_id = body.get("request_id", "unknown")
    
    # Store CMD safepoint
    sp = StoreIn(
        src=body.get("source", "opena1"),
        dst="archivp",
        kind="CMD",
        body=body,
        strict=True
    )
    path = _write_safepoint(sp)
    
    # Return minimal OK response
    return {
        "ok": True,
        "request_id": req_id,
        "stored": str(path),
        "strict": True
    }

@app.post("/store/resp")
async def store_resp(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Store RESP safepoint from tool execution.
    Expected body: {request_id, timestamp, source, result{...}, strict}
    """
    req_id = body.get("request_id", "unknown")
    
    # Store RESP safepoint
    sp = StoreIn(
        src=body.get("source", "tool"),
        dst="opena1",
        kind="RESP",
        body=body,
        strict=True
    )
    path = _write_safepoint(sp)
    
    return {
        "ok": True,
        "request_id": req_id,
        "stored": str(path),
        "strict": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("opena2_app:app", host="127.0.0.1", port=PORT, reload=False, access_log=False)
