# main_opena2.py
"""
ELION Archivator (opena2)
- Speichert Safepoints als Dateien unter ./ARCHIV/<YYYY>/<MM>/<DD>/<filename>.json
- Endpunkte:
    GET  /health
    POST /store/archivp      (Write)
    GET  /archiv/last?n=5    (Liste der neuesten Dateien)
    GET  /archiv/get?path=... (optional: Inhalt anzeigen)
"""

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

# --- Basis ---
app = FastAPI(title="ELION Archivator (opena2)", version="1.0")
logger = logging.getLogger("opena2")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - opena2 - %(levelname)s - %(message)s",
)

ARCHIV_ROOT = Path(os.environ.get("ARCHIV_ROOT", "./ARCHIV")).resolve()
ARCHIV_ROOT.mkdir(parents=True, exist_ok=True)


# --- Models ---
class WriteOp(BaseModel):
    op: str | None = "WRITE"
    path: str | None = None  # z.B. "2025/11/06/SP176214xxxx_kordp→opena2_CMD.json"
    content: Any


# --- Helpers ---
def _utcnow_iso() -> str:
    return datetime.now(UTC).isoformat()


def _safe_join(root: Path, rel_path: str) -> Path:
    # keine traversal-Angriffe zulassen
    p = (root / rel_path).resolve()
    if not str(p).startswith(str(root)):
        raise HTTPException(status_code=400, detail="Invalid path")
    return p


def _ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


# --- Routes ---
@app.get("/health")
def health():
    return {"service": "opena2", "status": "healthy", "strict": True, "timestamp": _utcnow_iso()}


@app.post("/store/archivp")
def store_archivp(payload: dict):
    """
    Akzeptiert zwei Formate:
    1) { "op":"WRITE", "path": "YYYY/MM/DD/NAME.json", "content": {...} }
    2) { "src":"kordp", "dst":"opena2", "kind":"CMD", "payload": {...} }  -> wir generieren path automatisch
    """
    # Pydantic-Validierung für Format 1
    try:
        if "op" in payload or "content" in payload:
            op = WriteOp(**payload)
            rel_path = op.path
            if rel_path is None:
                # Automatischer Dateiname, falls nicht gegeben
                datedir = datetime.now().strftime("%Y/%m/%d")
                rel_path = f"{datedir}/SP{int(datetime.now().timestamp())}_generic.json"
            # Pfad und Schreiben
            out = _safe_join(ARCHIV_ROOT, rel_path)
            _ensure_parent(out)
            with out.open("w", encoding="utf-8") as f:
                json.dump(op.content, f, ensure_ascii=False, indent=2)
            logger.info(f"WRITE -> {out}")
            return {"strict": True, "written": True, "path": str(out.relative_to(ARCHIV_ROOT))}
    except Exception as e:
        logger.error(f"WRITE-Format-1 Fehler: {e}")

    # Fallback: Format 2 (kordp-kompatibel)
    if {"src", "dst", "kind", "payload"}.issubset(payload.keys()):
        datedir = datetime.now().strftime("%Y/%m/%d")
        fname = f"SP{int(datetime.now().timestamp())}_{payload['src']}→{payload['dst']}_{payload['kind']}.json"
        rel_path = f"{datedir}/{fname}"
        out = _safe_join(ARCHIV_ROOT, rel_path)
        _ensure_parent(out)
        with out.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        logger.info(f"WRITE(kordp) -> {out}")
        return {"strict": True, "written": True, "path": str(out.relative_to(ARCHIV_ROOT))}

    raise HTTPException(status_code=400, detail="Unsupported payload format")


@app.get("/archiv/last")
def archiv_last(n: int = Query(5, ge=1, le=100)):
    """Liste die letzten n Dateien nach mtime (desc)"""
    files: list[Path] = []
    for p in ARCHIV_ROOT.rglob("*.json"):
        files.append(p)
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    out = []
    for p in files[:n]:
        st = p.stat()
        out.append(
            {
                "path": str(p.relative_to(ARCHIV_ROOT)),
                "size": st.st_size,
                "mtime": datetime.fromtimestamp(st.st_mtime, tz=UTC).isoformat(),
            }
        )
    return {"strict": True, "count": len(out), "items": out}


@app.get("/archiv/get")
def archiv_get(path: str):
    """Inhalt einer Datei ausgeben (relativer Pfad unter ARCHIV)"""
    p = _safe_join(ARCHIV_ROOT, path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Not Found")
    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        # falls keine JSON-Datei
        data = p.read_text(encoding="utf-8", errors="replace")
    return {"strict": True, "path": path, "content": data}


if __name__ == "__main__":
    # Starte fix auf 12345
    uvicorn.run("main_opena2:app", host="127.0.0.1", port=12345, reload=False)
