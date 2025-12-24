import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException

app = FastAPI(title="Portier FS Bridge")

BASE_DIR = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt").resolve()
ALLOWED_PORTS = [12344, 12345, 12346, 12347, 12348, 12349]
FORBIDDEN_PORTS = [8080]


def _safe_join(rel: str) -> Path:
    p = (BASE_DIR / rel.lstrip("/")).resolve()
    if not str(p).startswith(str(BASE_DIR)):
        raise HTTPException(400, "Path outside BASE_DIR")
    return p


def _sp(kind: str, payload: dict):
    now = datetime.now()
    adir = BASE_DIR / "1.opena1&2_portier" / "archivp" / f"{now:%Y/%m/%d}"
    adir.mkdir(parents=True, exist_ok=True)
    name = f"SP{int(now.timestamp())}_opena1→opena2_{kind}.json"
    (adir / name).write_text(json.dumps({**payload, "strict": True}, ensure_ascii=False, indent=2), encoding="utf-8")


@app.get("/health")
def health():
    return {
        "service": "portier_fs_bridge",
        "status": "healthy",
        "base": str(BASE_DIR),
        "ts": datetime.utcnow().isoformat() + "Z",
        "port_policy": {"allowed": ALLOWED_PORTS, "forbidden": FORBIDDEN_PORTS},
    }


@app.get("/files")
def list_files(path: str = ".", recursive: bool = True):
    root = _safe_join(path)
    if not root.exists():
        raise HTTPException(404, "Path not found")
    items = []
    if recursive:
        for p in root.rglob("*"):
            items.append({"path": str(p.relative_to(BASE_DIR)), "type": "dir" if p.is_dir() else "file"})
    else:
        for p in root.iterdir():
            items.append({"path": str(p.relative_to(BASE_DIR)), "type": "dir" if p.is_dir() else "file"})
    _sp("CMD", {"op": "LIST", "root": str(root.relative_to(BASE_DIR)), "count": len(items)})
    return {"base": str(BASE_DIR), "count": len(items), "items": items, "strict": True}


@app.post("/file/read")
def read_file(body: dict):
    rel = body.get("path", "")
    p = _safe_join(rel)
    if not p.exists() or not p.is_file():
        raise HTTPException(404, "File not found")
    text = p.read_text(encoding="utf-8", errors="ignore")
    _sp("CMD", {"op": "READ", "path": rel, "size": len(text)})
    return {"path": rel, "content": text, "strict": True}


@app.post("/file/write")
def write_file(body: dict):
    rel = body.get("path", "")
    content = body.get("content", "")
    p = _safe_join(rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    _sp("CMD", {"op": "WRITE", "path": rel, "size": len(content)})
    return {"path": rel, "written": True, "size": len(content), "strict": True}
