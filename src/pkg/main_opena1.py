"""
Portier-Archivator (opena2) – FastAPI-Service auf Port 12348

Aufgaben:
- Entgegennahme, Persistenz und Ausgabe von Safepoints (archivp)
- Strikte Port-Policy (12344–12399; 8080 verboten)
- Gemeinsame Auth via .env (gleicher Token wie Dashboard/Koordinator)
- Savepoint-Format (bindend):
  Name: SP{epoch_secs}_{src}→{dst}_{kind}.json
  Ablage:  1.portier_openai/archivp/YYYY/MM/DD/<NAME>.json
  Index:   1.portier_openai/archivp/index.jsonl (append-only)

Fixe Labels/Endpoints (bindend):
- /store/archivp    (WRITE & READ)
- /finalize/opena2  (ACK/Bestätigung)
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Security, Request, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from security import verify_token, RateLimiter, _read_env_token

# -------------------------------------------------------------------
# Konfiguration/Policy
# -------------------------------------------------------------------
BASE_ROOT = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt").resolve()
ARCHIVP_ROOT = (BASE_ROOT / "1.portier_openai" / "archivp").resolve()
INDEX_FILE = ARCHIVP_ROOT / "index.jsonl"

ALLOWED_PORT_MIN = 12344
ALLOWED_PORT_MAX = 12399
FORBIDDEN_PORTS = {8080}

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - opena2 - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/opena2_runtime.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("opena2")

# -------------------------------------------------------------------
# App
# -------------------------------------------------------------------
app = FastAPI(title="Portier-Archivator (opena2)", version="1.0", description="Archivport für Safepoints")
security = HTTPBearer()
rate_limiter = RateLimiter(requests_per_minute=90)

# -------------------------------------------------------------------
# Middleware: Port-Policy
# -------------------------------------------------------------------
@app.middleware("http")
async def validate_port_policy(request: Request, call_next):
    port = request.url.port
    if port in FORBIDDEN_PORTS:
        raise HTTPException(status_code=403, detail=f"Port {port} ist verboten")
    if not (ALLOWED_PORT_MIN <= port <= ALLOWED_PORT_MAX):
        raise HTTPException(status_code=403, detail=f"Port {port} außerhalb {ALLOWED_PORT_MIN}–{ALLOWED_PORT_MAX}")
    return await call_next(request)

# -------------------------------------------------------------------
# Utils
# -------------------------------------------------------------------
def _ensure_dirs_for_today() -> Path:
    today = datetime.now()
    day_dir = ARCHIVP_ROOT / f"{today:%Y/%m/%d}"
    day_dir.mkdir(parents=True, exist_ok=True)
    ARCHIVP_ROOT.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not INDEX_FILE.exists():
        INDEX_FILE.write_text("", encoding="utf-8")
    return day_dir

def _safe_join_in_archivp(rel_path: str) -> Path:
    p = (ARCHIVP_ROOT / rel_path.lstrip("/")).resolve()
    if not str(p).startswith(str(ARCHIVP_ROOT)):
        raise HTTPException(400, "Pfad außerhalb von archivp")
    return p

def _write_index(sp_name: str, src: str, dst: str, kind: str, path: str) -> None:
    entry = {
        "sp": sp_name,
        "ts": datetime.now().isoformat(),
        "src": src,
        "dst": dst,
        "kind": kind,
        "path": path,
        "strict": True
    }
    with INDEX_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def _make_sp_name(src: str, dst: str, kind: str) -> str:
    ep = int(time.time())
    return f"SP{ep}_{src}→{dst}_{kind}.json"

# -------------------------------------------------------------------
# Lifecycle
# -------------------------------------------------------------------
@app.on_event("startup")
async def on_start():
    _ = _read_env_token()
    _ensure_dirs_for_today()
    logger.info("opena2 gestartet, Archivpfad: %s", ARCHIVP_ROOT)

# -------------------------------------------------------------------
# Endpunkte
# -------------------------------------------------------------------
@app.get("/health")
async def health():
    return {
        "service": "opena2",
        "status": "healthy",
        "strict": True,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/store/archivp")
@rate_limiter.limit()
async def store_archivp(
    body: Dict[str, Any],
    token: HTTPAuthorizationCredentials = Security(security)
):
    if not verify_token(token.credentials):
        raise HTTPException(status_code=401, detail="Ungültiger Token")

    src = (body or {}).get("src", "")
    dst = (body or {}).get("dst", "")
    kind = (body or {}).get("kind", "")
    data = (body or {}).get("data", {})
    relpath = (body or {}).get("relpath", "")

    if not (src and dst and kind and isinstance(data, dict)):
        raise HTTPException(status_code=400, detail="src/dst/kind/data erforderlich")

    sp_name = _make_sp_name(src, dst, kind)
    day_dir = _ensure_dirs_for_today()
    target_dir = day_dir
    if relpath:
        target_dir = _safe_join_in_archivp(relpath)
        target_dir.mkdir(parents=True, exist_ok=True)

    out_file = (target_dir / sp_name).resolve()
    content = dict(data)
    content.setdefault("strict", True)

    out_file.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_index(sp_name, src, dst, kind, str(out_file))

    return {
        "strict": True,
        "written": True,
        "sp_name": sp_name,
        "path": str(out_file)
    }

@app.get("/store/archivp")
@rate_limiter.limit()
async def read_archivp(
    path: str = Query(..., description="Pfad relativ zu archivp, z.B. '2025/11/06/SP...json'"),
    token: HTTPAuthorizationCredentials = Security(security)
):
    if not verify_token(token.credentials):
        raise HTTPException(status_code=401, detail="Ungültiger Token")

    p = _safe_join_in_archivp(path)
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="Safepoint nicht gefunden")

    try:
        text = p.read_text(encoding="utf-8")
        obj = json.loads(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lesefehler: {e}")

    return {"strict": True, "path": str(p), "content": obj}

@app.post("/finalize/opena2")
@rate_limiter.limit()
async def finalize(
    info: Dict[str, Any],
    token: HTTPAuthorizationCredentials = Security(security)
):
    if not verify_token(token.credentials):
        raise HTTPException(status_code=401, detail="Ungültiger Token")

    src = (info or {}).get("src", "unknown")
    ack_for = (info or {}).get("ack_for", "unknown")
    note = (info or {}).get("note", "")

    sp_name = _make_sp_name(src, "opena2", "RESP")
    day_dir = _ensure_dirs_for_today()
    out_file = (day_dir / sp_name).resolve()

    payload = {"ack_for": ack_for, "note": note, "strict": True}
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_index(sp_name, src, "opena2", "RESP", str(out_file))

    return {"strict": True, "status": "finalized", "sp_name": sp_name, "path": str(out_file)}

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    Path("logs").mkdir(parents=True, exist_ok=True)
    uvicorn.run("main_opena2:app", host="127.0.0.1", port=12348, reload=False)

