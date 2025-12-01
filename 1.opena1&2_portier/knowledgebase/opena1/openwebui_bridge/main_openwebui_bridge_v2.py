#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenWebUI Bridge (opena3) – Relay between Telegram, GitHub, and OpenWebUI API
- Port: 12347 (Port-Policy)
- Endpoints:
  * GET  /health
  * POST /message/relay (Telegram → OpenWebUI)
  * POST /github/webhook (GitHub → Notification)
  * GET  /status
- All interactions logged as Safepoints
"""

import os
import sys
import json
import time
import hashlib
import hmac
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import requests

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

PORT = 12347
HOST = "127.0.0.1"
BASE_ROOT = Path(os.getenv("BASE_ROOT", Path.cwd()))
ARCHIVE_DIR = BASE_ROOT / "1.opena1&2_portier" / "archivp_store"
INDEX_FILE = ARCHIVE_DIR / "index.jsonl"

# Services
OPENA2_URL = os.getenv("OPENA2_URL", "http://127.0.0.1:12345")
OPENA4_URL = os.getenv("OPENA4_URL", "http://127.0.0.1:12348")
OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://localhost:8080")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("opena3.bridge")

# FastAPI
app = FastAPI(
    title="OpenWebUI Bridge (opena3)",
    description="Relay and integration for Telegram, GitHub, and OpenWebUI",
    version="2.0.0"
)

startup_time = time.time()

# ──────────────────────────────────────────────────────────────────────────────
# Safepoint Utilities
# ──────────────────────────────────────────────────────────────────────────────

def write_safepoint(
    src: str,
    dst: str,
    kind: str,
    body: Dict[str, Any]
) -> Path:
    """Write safepoint to archive."""
    today = datetime.utcnow().strftime("%Y/%m/%d")
    target_dir = ARCHIVE_DIR / today
    target_dir.mkdir(parents=True, exist_ok=True)
    
    ts = int(time.time())
    name = f"SP{ts}_{src}→{dst}_{kind}.json"
    fpath = target_dir / name
    
    payload = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "src": src,
        "dst": dst,
        "kind": kind,
        "body": body,
        "strict": True
    }
    
    fpath.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Append to index
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with INDEX_FILE.open("a", encoding="utf-8") as idx:
        idx.write(json.dumps({
            "sp": name,
            "ts": payload["ts"],
            "src": src,
            "dst": dst,
            "kind": kind,
            "path": str(fpath)
        }) + "\n")
    
    logger.debug(f"Safepoint: {name}")
    return fpath


def _redact_secrets(obj: Any) -> Any:
    """Redact sensitive fields recursively."""
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            kl = str(k).lower()
            if any(x in kl for x in ["token", "secret", "key", "password", "api"]):
                result[k] = "***REDACTED***"
            else:
                result[k] = _redact_secrets(v)
        return result
    if isinstance(obj, list):
        return [_redact_secrets(x) for x in obj]
    return obj


# ──────────────────────────────────────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────────────────────────────────────

class MessageRelay(BaseModel):
    """Relay message from Telegram to OpenWebUI."""
    chat_id: int
    user_id: int
    text: str
    message_id: int


class GitHubWebhook(BaseModel):
    """GitHub webhook event (simplified)."""
    action: Optional[str] = None
    ref: Optional[str] = None
    repository: Optional[Dict[str, Any]] = None
    head_commit: Optional[Dict[str, Any]] = None


# ──────────────────────────────────────────────────────────────────────────────
# HTTP Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Health check."""
    uptime = time.time() - startup_time
    return {
        "status": "ok",
        "service": "opena3",
        "role": "openwebui_bridge",
        "port": PORT,
        "port_policy": {
            "window": "12344-12399",
            "forbidden": ["8080"]
        },
        "uptime_seconds": uptime,
        "strict": True
    }


@app.post("/message/relay")
async def relay_message(msg: MessageRelay):
    """Relay message from Telegram to OpenWebUI."""
    request_id = f"relay_{msg.message_id}_{int(time.time()*1000)}"
    
    try:
        # Log incoming message
        write_safepoint("opena4", "opena3", "MSG_RELAY_IN", {
            "message_id": msg.message_id,
            "chat_id": msg.chat_id,
            "user_id": msg.user_id,
            "text": msg.text
        })
        
        # Forward to OpenWebUI (if configured)
        response_data = {
            "request_id": request_id,
            "status": "received",
            "forwarded_to": "openwebui" if OPENWEBUI_URL else "queued"
        }
        
        if OPENWEBUI_URL:
            try:
                # Try to reach OpenWebUI API
                owui_resp = requests.post(
                    f"{OPENWEBUI_URL}/api/chat",
                    json={"message": msg.text},
                    timeout=5
                )
                if owui_resp.status_code == 200:
                    response_data["openwebui_response"] = owui_resp.json()
                    response_data["status"] = "processed"
            except requests.RequestException as e:
                logger.warning(f"OpenWebUI unreachable: {e}")
                response_data["warning"] = f"OpenWebUI not reached: {str(e)[:100]}"
        
        # Log outgoing result
        write_safepoint("opena3", "opena4", "MSG_RELAY_OUT", response_data)
        
        return {
            "ok": True,
            "request_id": request_id,
            "response": response_data,
            "strict": True
        }
    
    except Exception as e:
        logger.exception(f"Message relay error: {e}")
        write_safepoint("opena3", "opena3", "ERR", {
            "error": "relay_failed",
            "message": str(e),
            "request_id": request_id
        })
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/github/webhook")
async def github_webhook(req: Request):
    """GitHub webhook handler."""
    try:
        # Verify signature (if secret configured)
        if GITHUB_WEBHOOK_SECRET:
            signature = req.headers.get("X-Hub-Signature-256", "")
            body = await req.body()
            
            expected_sig = "sha256=" + hmac.new(
                GITHUB_WEBHOOK_SECRET.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_sig):
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        data = await req.json()
        event_type = req.headers.get("X-GitHub-Event", "unknown")
        
        # Extract key information
        repo = data.get("repository", {}).get("full_name", "unknown")
        ref = data.get("ref", "").replace("refs/heads/", "")
        action = data.get("action", "")
        commit_msg = ""
        
        if event_type == "push":
            commit_msg = data.get("head_commit", {}).get("message", "")
        elif event_type == "pull_request":
            pr = data.get("pull_request", {})
            commit_msg = pr.get("title", "")
        
        # Build notification message
        emoji_map = {
            "push": "📤",
            "pull_request": "🔀",
            "release": "🏷️",
            "workflow_run": "⚙️"
        }
        emoji = emoji_map.get(event_type, "📌")
        
        message = f"{emoji} GitHub {event_type}: {repo}"
        if action:
            message += f" ({action})"
        if ref:
            message += f" @ {ref}"
        if commit_msg:
            message += f"\n💬 {commit_msg.split(chr(10))[0][:80]}"
        
        # Log webhook
        write_safepoint("github", "opena3", "WEBHOOK", {
            "event_type": event_type,
            "action": action,
            "repo": repo,
            "ref": ref,
            "message": commit_msg[:200],
            "received_at": datetime.utcnow().isoformat() + "Z"
        })
        
        # Send notification to Telegram (if available)
        try:
            requests.post(
                f"{OPENA4_URL}/notify",
                json={"message": message},
                timeout=5
            )
            logger.info(f"GitHub webhook notification sent to Telegram: {message[:80]}")
        except requests.RequestException as e:
            logger.warning(f"Could not notify Telegram: {e}")
        
        return {
            "ok": True,
            "event": event_type,
            "message": message,
            "strict": True
        }
    
    except Exception as e:
        logger.exception(f"GitHub webhook error: {e}")
        write_safepoint("github", "opena3", "ERR", {
            "error": "webhook_failed",
            "message": str(e)
        })
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status():
    """Service status and recent safepoints."""
    try:
        recent_sps = []
        if INDEX_FILE.exists():
            with INDEX_FILE.open("r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-10:]:  # Last 10 entries
                    recent_sps.append(json.loads(line))
        
        return {
            "service": "opena3",
            "status": "operational",
            "role": "openwebui_bridge",
            "port": PORT,
            "archive_dir": str(ARCHIVE_DIR),
            "endpoints": {
                "opena2": OPENA2_URL,
                "opena4": OPENA4_URL,
                "openwebui": OPENWEBUI_URL
            },
            "recent_safepoints_count": len(recent_sps),
            "recent_safepoints": recent_sps,
            "strict": True
        }
    except Exception as e:
        logger.exception(f"Status error: {e}")
        return {
            "service": "opena3",
            "status": "error",
            "error": str(e)
        }


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting OpenWebUI Bridge @ {HOST}:{PORT}")
    logger.info(f"OpenWebUI: {OPENWEBUI_URL}")
    logger.info(f"Archive: {ARCHIVE_DIR}")
    
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        reload=False,
        access_log=False
    )
