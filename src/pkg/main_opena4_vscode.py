"""
opena4_VSCode: Remote VS Code Integration Agent
Orchestrates file operations and terminal execution via SSH
"""

import json
import logging
import os
import sys
import urllib.request
from datetime import datetime

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from vscode_ssh import VSCodeSSH, init_ssh

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(title="opena4_VSCode", version="1.0.0", description="Remote VS Code Integration Agent")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 12352
TOKEN = "MEIN_SUPER_TOKEN_123"
ARCHIVE_PORT = 12345

# SSH Configuration
SSH_HOST = os.getenv("SSH_HOST", "167.235.207.100")
SSH_USER = os.getenv("SSH_USER", "root")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", "/root/.ssh/id_rsa")

# Global SSH instance
ssh: VSCodeSSH | None = None

# ============================================================================
# DATA MODELS
# ============================================================================


class FileReadRequest(BaseModel):
    path: str
    lines: tuple[int, int] | None = None


class FileWriteRequest(BaseModel):
    path: str
    content: str


class TerminalExecRequest(BaseModel):
    cmd: str
    timeout_sec: int = 30


class DirectoryListRequest(BaseModel):
    path: str


class FileDeleteRequest(BaseModel):
    path: str


# ============================================================================
# LIFECYCLE
# ============================================================================


@app.on_event("startup")
async def startup():
    """Initialize SSH connection on startup"""
    global ssh
    try:
        ssh = await init_ssh(SSH_HOST, SSH_USER, SSH_KEY_PATH)
        logger.info("✅ opena4_VSCode startup complete")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown():
    """Close SSH connection on shutdown"""
    global ssh
    if ssh:
        await ssh.close()
        logger.info("✅ opena4_VSCode shutdown complete")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _validate_token(auth_header: str | None):
    """Validate Bearer token"""
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = auth_header.replace("Bearer ", "").strip()
    if token != TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")


async def _archive(payload: dict) -> dict:
    """Archive operation to opena2"""
    try:
        data = {
            "src": "opena4_vscode",
            "dst": "opena2",
            "kind": "FILE_OP",
            "payload": {**payload, "ts": datetime.utcnow().isoformat() + "Z"},
        }

        req = urllib.request.Request(
            f"http://127.0.0.1:{ARCHIVE_PORT}/store/archivp",
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=5) as r:
            result = json.loads(r.read().decode())
            logger.info(f"✅ Archived: {payload.get('op')}")
            return result
    except Exception as e:
        logger.warning(f"⚠️ Archive failed (non-fatal): {e}")
        return {"written": False}


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "opena4_VSCode",
        "port": PORT,
        "ssh_connected": ssh.is_connected() if ssh else False,
        "ts": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/file/read")
async def read_file(req: FileReadRequest, authorization: str = Header(None)):
    """Read file from remote server"""
    _validate_token(authorization)

    if not ssh or not ssh.is_connected():
        raise HTTPException(status_code=503, detail="SSH connection not available")

    try:
        content = await ssh.read_file(req.path)

        # Apply line filtering if requested
        if req.lines:
            start, end = req.lines
            lines = content.split("\n")
            content = "\n".join(lines[start - 1 : end])

        # Archive
        await _archive({"op": "FILE_READ", "path": req.path, "bytes": len(content), "lines": len(content.split("\n"))})

        return {
            "strict": True,
            "path": req.path,
            "content": content,
            "bytes": len(content),
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"❌ File read failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/file/write")
async def write_file(req: FileWriteRequest, authorization: str = Header(None)):
    """Write file to remote server"""
    _validate_token(authorization)

    if not ssh or not ssh.is_connected():
        raise HTTPException(status_code=503, detail="SSH connection not available")

    try:
        success = await ssh.write_file(req.path, req.content)

        # Archive
        await _archive({"op": "FILE_WRITE", "path": req.path, "bytes": len(req.content), "success": success})

        return {
            "strict": True,
            "written": success,
            "path": req.path,
            "bytes": len(req.content),
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"❌ File write failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/file/delete")
async def delete_file(req: FileDeleteRequest, authorization: str = Header(None)):
    """Delete file from remote server"""
    _validate_token(authorization)

    if not ssh or not ssh.is_connected():
        raise HTTPException(status_code=503, detail="SSH connection not available")

    try:
        success = await ssh.delete_file(req.path)

        # Archive
        await _archive({"op": "FILE_DELETE", "path": req.path, "success": success})

        return {"strict": True, "deleted": success, "path": req.path, "ts": datetime.utcnow().isoformat() + "Z"}
    except Exception as e:
        logger.error(f"❌ File delete failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/file/list")
async def list_directory(req: DirectoryListRequest, authorization: str = Header(None)):
    """List directory contents"""
    _validate_token(authorization)

    if not ssh or not ssh.is_connected():
        raise HTTPException(status_code=503, detail="SSH connection not available")

    try:
        items = await ssh.list_dir(req.path)

        # Archive
        await _archive({"op": "DIR_LIST", "path": req.path, "count": len(items)})

        return {
            "strict": True,
            "path": req.path,
            "items": items,
            "count": len(items),
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"❌ Directory list failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/terminal/exec")
async def exec_terminal(req: TerminalExecRequest, authorization: str = Header(None)):
    """Execute terminal command on remote server"""
    _validate_token(authorization)

    if not ssh or not ssh.is_connected():
        raise HTTPException(status_code=503, detail="SSH connection not available")

    try:
        output = await ssh.exec_cmd(req.cmd, timeout=req.timeout_sec)

        # Archive
        await _archive(
            {
                "op": "TERMINAL_EXEC",
                "cmd": req.cmd,
                "result_lines": len(output.splitlines()),
                "timeout_sec": req.timeout_sec,
            }
        )

        return {
            "strict": True,
            "cmd": req.cmd,
            "output": output,
            "lines": len(output.splitlines()),
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except TimeoutError:
        logger.error(f"❌ Command timeout: {req.cmd}")
        raise HTTPException(status_code=504, detail=f"Command timeout after {req.timeout_sec}s")
    except Exception as e:
        logger.error(f"❌ Command execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status(authorization: str = Header(None)):
    """Get agent status"""
    _validate_token(authorization)

    return {
        "service": "opena4_VSCode",
        "version": "1.0.0",
        "port": PORT,
        "ssh_host": SSH_HOST,
        "ssh_connected": ssh.is_connected() if ssh else False,
        "endpoints": 6,
        "ts": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Starting opena4_VSCode on port {PORT}")
    logger.info(f"SSH Target: {SSH_USER}@{SSH_HOST}")

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
