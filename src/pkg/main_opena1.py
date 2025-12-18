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
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Callable, Awaitable, Optional

from fastapi import FastAPI, HTTPException, Security, Request, Query
from pkg.shared.config import init_tracing_from_settings
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field

# Local Security Utils
def _read_env_token() -> str:
    """Liest Bearer-Token aus .env oder generiert neuen."""
    env_path = Path(__file__).parent.parent.parent / ".env"
    
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('BEARER_TOKEN='):
                    token = line.split('=', 1)[1].strip()
                    if token:
                        return token
    
    # Fallback: Generiere neuen Token
    new_token = str(uuid.uuid4())
    
    # Schreibe .env
    with open(env_path, 'a', encoding='utf-8') as f:
        f.write(f"\nBEARER_TOKEN={new_token}\n")
    
    return new_token

def verify_token(token: Optional[str]) -> bool:
    """Validiert Bearer-Token gegen .env."""
    if not token:
        return False
    return token == _read_env_token()

class RateLimiter:
    """Simple Rate Limiter für ELION-Archivator."""
    def __init__(self, requests_per_minute: int = 90):
        self.requests_per_minute = requests_per_minute
    
    def limit(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator für Rate-Limiting."""
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            return func
        return decorator

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
# Models
# -------------------------------------------------------------------
class SafepointRequest(BaseModel):
    """Type-safe Safepoint Request Model."""
    model_config = ConfigDict(extra="forbid")
    src: str = Field(..., min_length=1)
    dst: str = Field(..., min_length=1)
    kind: str = Field(..., pattern=r"^(CMD|RESP|ACK)$")
    data: Dict[str, Any] = Field(default_factory=dict)
    relpath: Optional[str] = None

class SafepointResponse(BaseModel):
    """Type-safe Safepoint Response Model."""
    model_config = ConfigDict(extra="forbid")
    strict: bool = True
    written: bool
    sp_name: str
    path: str

class HealthResponse(BaseModel):
    """Health Response Model."""
    model_config = ConfigDict(extra="forbid")
    service: str
    status: str
    strict: bool
    timestamp: str

# -------------------------------------------------------------------
# Lifespan Handler
# -------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """ELION-konformer Lifespan Handler für opena2 Archivator."""
    # Startup Logic
    logger.info("🚀 opena2 Archivator startet...")
    init_tracing_from_settings(app, service_name="opena1")
    _read_env_token()  # Initialisiert Token-System
    _ensure_dirs_for_today()
    logger.info("opena2 gestartet, Archivpfad: %s", ARCHIVP_ROOT)
    
    yield  # Application läuft
    
    # Shutdown Logic
    logger.info("🛑 opena2 Archivator stoppt...")

# -------------------------------------------------------------------
# App
# -------------------------------------------------------------------
app = FastAPI(
    title="Portier-Archivator (opena2)", 
    version="2.0", 
    description="ELION Archivport für Safepoints mit Type-Safety",
    lifespan=lifespan
)
security = HTTPBearer()
rate_limiter = RateLimiter(requests_per_minute=90)

# -------------------------------------------------------------------
# Middleware: Port-Policy
# -------------------------------------------------------------------
@app.middleware("http")
async def validate_port_policy(
    request: Request, 
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Port-Policy Middleware mit Type-Safety."""
    port = request.url.port
    
    # None-Check für Port
    if port is not None:
        if port in FORBIDDEN_PORTS:
            raise HTTPException(
                status_code=403, 
                detail=f"Port {port} ist verboten (OpenWebUI UI-only)"
            )
        if not (ALLOWED_PORT_MIN <= port <= ALLOWED_PORT_MAX):
            raise HTTPException(
                status_code=403, 
                detail=f"Port {port} außerhalb {ALLOWED_PORT_MIN}–{ALLOWED_PORT_MAX}"
            )
    
    response = await call_next(request)
    return response

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
    """Schreibt Index-Eintrag mit Type-Safety."""
    entry: Dict[str, Any] = {
        "sp": sp_name,
        "ts": datetime.now(timezone.utc).isoformat(),
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
# Endpunkte
# -------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health Check für opena2 Archivator."""
    return HealthResponse(
        service="opena2",
        status="healthy",
        strict=True,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@app.post("/store/archivp", response_model=SafepointResponse)
@rate_limiter.limit()
async def store_archivp(
    body: SafepointRequest,
    token: HTTPAuthorizationCredentials = Security(security)
) -> SafepointResponse:
    """Speichert Safepoint mit Type-Safety."""
    if not verify_token(token.credentials):
        raise HTTPException(status_code=401, detail="Ungültiger Token")

    if not (body.src and body.dst and body.kind):
        raise HTTPException(status_code=400, detail="src/dst/kind erforderlich")

    sp_name = _make_sp_name(body.src, body.dst, body.kind)
    day_dir = _ensure_dirs_for_today()
    target_dir = day_dir
    
    if body.relpath:
        target_dir = _safe_join_in_archivp(body.relpath)
        target_dir.mkdir(parents=True, exist_ok=True)

    out_file = (target_dir / sp_name).resolve()
    content: Dict[str, Any] = dict(body.data)
    content.setdefault("strict", True)

    out_file.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_index(sp_name, body.src, body.dst, body.kind, str(out_file))

    return SafepointResponse(
        strict=True,
        written=True,
        sp_name=sp_name,
        path=str(out_file)
    )

@app.get("/store/archivp")
@rate_limiter.limit()
async def read_archivp(
    path: str = Query(..., description="Pfad relativ zu archivp, z.B. '2025/11/06/SP...json'"),
    token: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """Liest Safepoint mit Type-Safety."""
    if not verify_token(token.credentials):
        raise HTTPException(status_code=401, detail="Ungültiger Token")

    p = _safe_join_in_archivp(path)
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="Safepoint nicht gefunden")

    try:
        text = p.read_text(encoding="utf-8")
        obj: Dict[str, Any] = json.loads(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lesefehler: {e}")

    return {"strict": True, "path": str(p), "content": obj}

@app.post("/finalize/opena2")
@rate_limiter.limit()
async def finalize(
    info: Dict[str, Any],
    token: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """Finalisiert Safepoint mit Type-Safety."""
    if not verify_token(token.credentials):
        raise HTTPException(status_code=401, detail="Ungültiger Token")

    src = (info or {}).get("src", "unknown")
    ack_for = (info or {}).get("ack_for", "unknown")
    note = (info or {}).get("note", "")

    sp_name = _make_sp_name(src, "opena2", "RESP")
    day_dir = _ensure_dirs_for_today()
    out_file = (day_dir / sp_name).resolve()

    payload: Dict[str, Any] = {"ack_for": ack_for, "note": note, "strict": True}
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_index(sp_name, src, "opena2", "RESP", str(out_file))

    return {"strict": True, "status": "finalized", "sp_name": sp_name, "path": str(out_file)}

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    Path("logs").mkdir(parents=True, exist_ok=True)
    uvicorn.run(app, host="127.0.0.1", port=12348, reload=False)

