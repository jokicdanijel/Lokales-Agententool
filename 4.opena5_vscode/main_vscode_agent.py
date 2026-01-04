#!/usr/bin/env python3
"""
opena5 – VS Code Agent (Main Entry Point)
Production-ready VS Code integration with File-System-Watcher and Code-Analyse
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

PORT = int(os.getenv("OPENA5_PORT", "12365"))
HOST = os.getenv("OPENA5_HOST", "127.0.0.1")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

# Archivp (shared)
BASE_ROOT = Path(__file__).parent.parent
ARCHIVP_ROOT = os.getenv("ARCHIVP_ROOT", str(BASE_ROOT / "1.opena1&2_portier" / "archivp_store"))
ARCHIVP_DIR = Path(ARCHIVP_ROOT)
ARCHIVP_DIR.mkdir(parents=True, exist_ok=True)

# URLs (Option-2-Flow)
OPENA2_URL = os.getenv("OPENA2_URL", "http://127.0.0.1:12345/command")
KORDP_URL = os.getenv("KORDP_URL", "http://127.0.0.1:12346/dispatch")

# Port-Policy
ALLOWED_PORTS = list(range(12344, 12400))
FORBIDDEN_PORTS = [8080]

# Workspace
WORKSPACE_ROOT = Path(os.getenv("VSCODE_WORKSPACE", str(BASE_ROOT)))
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10 MB
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", ".py,.md,.json,.txt,.sh,.yml,.yaml").split(",")

# Logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_DIR / "opena5.log", encoding="utf-8")],
)
logger = logging.getLogger("opena5")

# ──────────────────────────────────────────────────────────────────────────────
# Port-Policy Enforcement
# ──────────────────────────────────────────────────────────────────────────────

if PORT in FORBIDDEN_PORTS:
    logger.error(f"❌ FATAL: Port {PORT} ist für Backend verboten (8080 nur für UI)!")
    sys.exit(1)

if PORT not in ALLOWED_PORTS:
    logger.warning(f"⚠️  Port {PORT} außerhalb erlaubtem Bereich {min(ALLOWED_PORTS)}-{max(ALLOWED_PORTS)}")

logger.info(f"✅ Port-Policy OK: {PORT} in Bereich {min(ALLOWED_PORTS)}-{max(ALLOWED_PORTS)}")

# ──────────────────────────────────────────────────────────────────────────────
# FastAPI App
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="opena5 – VS Code Agent",
    description="File-System-Watcher, Code-Analyse, Option-2-Flow-Compliance",
    version="1.0.0",
)

# Security
security = HTTPBearer()

# Startup timestamp
startup_time = time.time()

# Mount static HTML files
static_dir = Path(__file__).parent / "html"
if static_dir.exists():
    app.mount("/ui", StaticFiles(directory=str(static_dir), html=True), name="ui")
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ──────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas
# ──────────────────────────────────────────────────────────────────────────────


class FileReadRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = Field(..., description="Relative path from workspace root")
    encoding: str = Field("utf-8", description="File encoding")


class FileWriteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = Field(..., description="Relative path from workspace root")
    content: str = Field(..., description="File content to write")
    mode: str = Field("w", description="Write mode (w=overwrite, a=append)")


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pattern: str = Field(..., description="Search pattern (regex)")
    file_types: list[str] = Field(default_factory=list, description="File extensions to search (.py, .md)")
    max_results: int = Field(100, description="Maximum results")


class CommandRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(..., description="Unique request ID")
    command: str = Field(..., description="Command type")
    payload: dict[str, Any] = Field(default_factory=dict, description="Command payload")


# ──────────────────────────────────────────────────────────────────────────────
# Secret Masking
# ──────────────────────────────────────────────────────────────────────────────


def mask_secrets(data: Any) -> Any:
    """Mask secrets in data (recursive)"""
    if isinstance(data, dict):
        return {
            k: (
                "***"
                if any(s in k.lower() for s in ["token", "password", "secret", "key", "bearer"])
                else mask_secrets(v)
            )
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [mask_secrets(item) for item in data]
    elif isinstance(data, str) and len(data) > 100:
        return data[:100] + "... [truncated]"
    else:
        return data


# ──────────────────────────────────────────────────────────────────────────────
# Safepoint Persistence
# ──────────────────────────────────────────────────────────────────────────────


def write_safepoint(src: str, dst: str, kind: str, payload: dict[str, Any], request_id: str | None = None) -> Path:
    """Write safepoint to disk (append-only)"""
    ts = int(datetime.utcnow().timestamp())
    today = datetime.utcnow().strftime("%Y/%m/%d")
    archive_dir = ARCHIVP_DIR / today
    archive_dir.mkdir(parents=True, exist_ok=True)

    sp_name = f"SP{ts}_{src}→{dst}_{kind}.json"
    sp_path = archive_dir / sp_name

    safepoint_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "src": src,
        "dst": dst,
        "kind": kind,
        "payload": mask_secrets(payload),
        "strict": True,
    }

    # Write safepoint
    with open(sp_path, "w", encoding="utf-8") as f:
        json.dump(safepoint_data, f, indent=2, ensure_ascii=False)

    # Append to index
    index_file = ARCHIVP_DIR / "index.jsonl"
    with open(index_file, "a", encoding="utf-8") as idx:
        idx_entry = {
            "sp": sp_name,
            "src": src,
            "dst": dst,
            "kind": kind,
            "ts": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id,
        }
        idx.write(json.dumps(idx_entry, ensure_ascii=False) + "\n")

    logger.debug(f"Safepoint written: {sp_path}")
    return sp_path


# ──────────────────────────────────────────────────────────────────────────────
# Security
# ──────────────────────────────────────────────────────────────────────────────


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Bearer token"""
    if not BEARER_TOKEN:
        logger.warning("⚠️  BEARER_TOKEN nicht konfiguriert, Auth deaktiviert")
        return True

    if credentials.credentials != BEARER_TOKEN:
        logger.warning(f"❌ Ungültiger Token: {credentials.credentials[:10]}***")
        raise HTTPException(status_code=401, detail="Ungültiger Bearer Token")

    return True


def sanitize_path(path: str) -> Path:
    """Sanitize file path (prevent path traversal)"""
    # Entferne führende Slashes
    path = path.lstrip("/")

    # Resolve gegen Workspace-Root
    full_path = (WORKSPACE_ROOT / path).resolve()

    # Prüfe ob innerhalb Workspace
    if not str(full_path).startswith(str(WORKSPACE_ROOT.resolve())):
        raise HTTPException(status_code=400, detail="Path traversal detected")

    return full_path


# ──────────────────────────────────────────────────────────────────────────────
# HTTP Endpoints
# ──────────────────────────────────────────────────────────────────────────────


@app.get("/", tags=["info"])
async def root():
    """Root endpoint"""
    return {
        "agent": "opena5",
        "kuerzel": "vscop",
        "port": PORT,
        "status": "running",
        "description": "VS Code Agent mit File-System-Watcher, Code-Analyse, Option-2-Flow-Compliance",
        "version": "1.0.0",
        "workspace": str(WORKSPACE_ROOT),
    }


@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint"""
    uptime = time.time() - startup_time

    workspace_accessible = WORKSPACE_ROOT.exists() and WORKSPACE_ROOT.is_dir()

    return {
        "status": "ok",
        "agent": "opena5",
        "port": PORT,
        "uptime": round(uptime, 2),
        "workspace_accessible": workspace_accessible,
        "workspace_root": str(WORKSPACE_ROOT),
        "max_file_size": MAX_FILE_SIZE,
    }


@app.post("/command", tags=["commands"])
async def command_endpoint(req: CommandRequest, _: bool = Depends(verify_token)):
    """Command endpoint (Bearer-Auth required)"""
    try:
        logger.info(f"Command received: {req.command} (ID: {req.request_id})")

        # Write CMD safepoint
        write_safepoint("opena5", "kordp", "CMD", req.model_dump(), req.request_id)

        # Placeholder response
        resp_data = {
            "status": "executed",
            "command": req.command,
            "request_id": req.request_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "output": f"Command '{req.command}' würde hier ausgeführt (Placeholder)",
        }

        # Write RESP safepoint
        write_safepoint("kordp", "opena5", "RESP", resp_data, req.request_id)

        return JSONResponse(resp_data)

    except Exception as e:
        logger.exception("Command endpoint error")
        return JSONResponse(
            {"error": {"code": "COMMAND_ERROR", "message": str(e)}, "request_id": req.request_id}, status_code=500
        )


@app.post("/file/read", tags=["files"])
async def file_read(req: FileReadRequest, _: bool = Depends(verify_token)):
    """Read file from workspace"""
    try:
        full_path = sanitize_path(req.path)

        if not full_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {req.path}")

        if not full_path.is_file():
            raise HTTPException(status_code=400, detail=f"Not a file: {req.path}")

        # Size check
        file_size = full_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE})")

        # Read file
        content = full_path.read_text(encoding=req.encoding)

        request_id = f"read_{int(time.time())}"

        # Write CMD safepoint
        write_safepoint(
            "opena5", "kordp", "CMD", {"operation": "file_read", "path": req.path, "size": file_size}, request_id
        )

        resp_data = {
            "status": "success",
            "path": req.path,
            "content": content,
            "size": file_size,
            "encoding": req.encoding,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Write RESP safepoint (truncated content)
        write_safepoint(
            "kordp",
            "opena5",
            "RESP",
            {
                "status": "success",
                "path": req.path,
                "size": file_size,
                "content_preview": content[:200] + "..." if len(content) > 200 else content,
            },
            request_id,
        )

        return JSONResponse(resp_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"File read error: {req.path}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/file/write", tags=["files"])
async def file_write(req: FileWriteRequest, _: bool = Depends(verify_token)):
    """Write file to workspace"""
    try:
        full_path = sanitize_path(req.path)

        # Extension check
        if full_path.suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, detail=f"Extension '{full_path.suffix}' not allowed. Allowed: {ALLOWED_EXTENSIONS}"
            )

        # Size check
        content_size = len(req.content.encode("utf-8"))
        if content_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, detail=f"Content too large: {content_size} bytes (max: {MAX_FILE_SIZE})"
            )

        # Create parent directory
        full_path.parent.mkdir(parents=True, exist_ok=True)

        request_id = f"write_{int(time.time())}"

        # Write CMD safepoint
        write_safepoint(
            "opena5",
            "kordp",
            "CMD",
            {"operation": "file_write", "path": req.path, "size": content_size, "mode": req.mode},
            request_id,
        )

        # Write file
        if req.mode == "a":
            with open(full_path, "a", encoding="utf-8") as f:
                f.write(req.content)
        else:
            full_path.write_text(req.content, encoding="utf-8")

        resp_data = {
            "status": "success",
            "path": req.path,
            "size": content_size,
            "mode": req.mode,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Write RESP safepoint
        write_safepoint("kordp", "opena5", "RESP", resp_data, request_id)

        return JSONResponse(resp_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"File write error: {req.path}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", tags=["search"])
async def search(req: SearchRequest, _: bool = Depends(verify_token)):
    """Search in workspace files"""
    try:
        import re

        request_id = f"search_{int(time.time())}"

        # Write CMD safepoint
        write_safepoint(
            "opena5",
            "kordp",
            "CMD",
            {"operation": "search", "pattern": req.pattern, "file_types": req.file_types},
            request_id,
        )

        # Compile regex
        pattern = re.compile(req.pattern, re.IGNORECASE)

        results = []
        file_count = 0

        # Search in workspace
        for root, dirs, files in os.walk(WORKSPACE_ROOT):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for file in files:
                file_path = Path(root) / file

                # Extension filter
                if req.file_types and file_path.suffix not in req.file_types:
                    continue

                # Skip large files
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")

                    for line_num, line in enumerate(content.splitlines(), 1):
                        if pattern.search(line):
                            results.append(
                                {
                                    "file": str(file_path.relative_to(WORKSPACE_ROOT)),
                                    "line": line_num,
                                    "content": line.strip(),
                                }
                            )

                            if len(results) >= req.max_results:
                                break

                    file_count += 1

                    if len(results) >= req.max_results:
                        break

                except Exception:
                    continue

            if len(results) >= req.max_results:
                break

        resp_data = {
            "status": "success",
            "pattern": req.pattern,
            "results": results,
            "result_count": len(results),
            "files_searched": file_count,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Write RESP safepoint
        write_safepoint(
            "kordp",
            "opena5",
            "RESP",
            {"status": "success", "result_count": len(results), "files_searched": file_count},
            request_id,
        )

        return JSONResponse(resp_data)

    except Exception as e:
        logger.exception("Search error")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workspace/list", tags=["workspace"])
async def workspace_list(_: bool = Depends(verify_token)):
    """List files/folders in workspace"""
    try:
        items = []

        for item in WORKSPACE_ROOT.iterdir():
            if item.name.startswith("."):
                continue

            items.append(
                {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat() + "Z",
                }
            )

        return JSONResponse(
            {"status": "success", "workspace": str(WORKSPACE_ROOT), "items": items, "count": len(items)}
        )

    except Exception as e:
        logger.exception("Workspace list error")
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────────
# Main Entry Point
# ──────────────────────────────────────────────────────────────────────────────


def main():
    """Main entry point"""
    logger.info("🚀 opena5 (VS Code Agent) startet...")
    logger.info(f"   Port: {PORT}")
    logger.info(f"   Host: {HOST}")
    logger.info(f"   Workspace: {WORKSPACE_ROOT}")
    logger.info(f"   Archiv: {ARCHIVP_DIR}")
    logger.info(f"   Max File Size: {MAX_FILE_SIZE} bytes")
    logger.info("✅ opena5 bereit!")

    uvicorn.run(app, host=HOST, port=PORT, log_level="info", reload=False)


if __name__ == "__main__":
    main()
