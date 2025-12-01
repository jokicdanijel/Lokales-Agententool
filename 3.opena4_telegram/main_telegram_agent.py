#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
opena4 – Telegram Agent (Main Entry Point)
Production-ready Telegram bot with Safepoint persistence and port-policy enforcement
"""

import os
import sys
import json
import logging
import logging.config
import asyncio
import time
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from argparse import ArgumentParser

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

# Import local modules
try:
    from schemas import Command71, Response71, Safepoint, ErrorSchema83, TelegramMessage, HealthResponse
    from config import get_config
except ImportError:
    from .schemas import Command71, Response71, Safepoint, ErrorSchema83, TelegramMessage, HealthResponse
    from .config import get_config


# ──────────────────────────────────────────────────────────────────────────────
# Initialization
# ──────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger("opena4")
config = get_config()

# Configure logging
logging.config.dictConfig(config.get_logging_config())

# FastAPI app (for webhooks and HTTP endpoints)
app = FastAPI(
    title="opena4 – Telegram Agent",
    description="Portier Telegram interface with Safepoint persistence",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Telegram bot (initialized later)
telegram_app = None
telegram_mode = "disabled"  # "polling", "webhook", or "disabled"

# Startup timestamp
startup_time = time.time()


# ────────────────────────────────────────────────────────────────────────────
# Secret Masking
# ────────────────────────────────────────────────────────────────────────────

def mask_secrets(data: Any) -> Any:
    """Mask secrets in data (recursive)"""
    if isinstance(data, dict):
        return {k: "***" if any(s in k.lower() for s in ["token", "password", "secret", "key", "bearer"]) else mask_secrets(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [mask_secrets(item) for item in data]
    else:
        return data


# ──────────────────────────────────────────────────────────────────────────────
# Safepoint Persistence
# ──────────────────────────────────────────────────────────────────────────────

def get_archive_dir() -> Path:
    """Get today's archive directory"""
    today = datetime.now(timezone.utc).strftime("%Y/%m/%d")
    archive_dir = config.archiv_dir / today
    archive_dir.mkdir(parents=True, exist_ok=True)
    return archive_dir


def write_safepoint(
    src: str,
    dst: str,
    kind: str,
    payload: Dict[str, Any],
    request_id: Optional[str] = None
) -> Path:
    """Write safepoint to disk (append-only)"""
    now = datetime.now(timezone.utc)
    ts = now.isoformat()
    sp_name = f"SP{int(now.timestamp())}_{src}→{dst}_{kind}.json"
    archive_dir = get_archive_dir()
    sp_path = archive_dir / sp_name
    
    safepoint_data = {
        "timestamp": ts,
        "src": src,
        "dst": dst,
        "kind": kind,
        "payload": mask_secrets(payload),  # Mask secrets
        "strict": True
    }
    
    # Write safepoint
    with open(sp_path, "w", encoding="utf-8") as f:
        json.dump(safepoint_data, f, indent=2, ensure_ascii=False)
    
    # Append to index
    index_file = config.archiv_dir / "index.jsonl"
    with open(index_file, "a", encoding="utf-8") as idx:
        idx_entry = {
            "sp": sp_name,
            "src": src,
            "dst": dst,
            "kind": kind,
            "ts": ts,
            "request_id": request_id
        }
        idx.write(json.dumps(idx_entry, ensure_ascii=False) + "\n")
    
    logger.debug(f"Safepoint written: {sp_path}")
    return sp_path


def create_error_response_83(
    error_code: str,
    message: str,
    request_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create standard error response (schema 8.3)"""
    ts = datetime.now(timezone.utc).isoformat()
    return {
        "request_id": request_id,
        "timestamp": ts,
        "source": "opena4",
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {}
        },
        "strict": True
    }


# ────────────────────────────────────────────────────────────────────────────
# Security
# ────────────────────────────────────────────────────────────────────────────

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Bearer token"""
    if not config.bearer_token:
        logger.warning("⚠️  BEARER_TOKEN nicht konfiguriert, Auth deaktiviert")
        return True
    
    if credentials.credentials != config.bearer_token:
        logger.warning(f"❌ Ungültiger Token: {credentials.credentials[:10]}***")
        raise HTTPException(status_code=401, detail="Ungültiger Bearer Token")
    
    return True


# ────────────────────────────────────────────────────────────────────────────
# HTTP Endpoints (FastAPI)
# ────────────────────────────────────────────────────────────────────────────

@app.get("/", tags=["info"])
async def root():
    """Root endpoint"""
    return {
        "agent": "opena4",
        "kuerzel": "tgap",
        "port": config.port,
        "status": "running",
        "telegram_mode": telegram_mode,
        "description": "Telegram Gateway Agent mit Webhook-Support, Message-Queue, Option-2-Flow-Compliance",
        "version": "1.0.0"
    }


@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint"""
    uptime = time.time() - startup_time
    
    # Check Telegram API availability
    telegram_available = bool(telegram_app and config.telegram_bot_token)
    
    return {
        "status": "ok",
        "agent": "opena4",
        "kuerzel": "tgap",
        "port": config.port,
        "uptime": round(uptime, 2),
        "telegram_available": telegram_available,
        "telegram_mode": telegram_mode,
        "telegram_users_configured": len(config.telegram_allowed_users) if config.telegram_allowed_users else 0
    }


@app.post("/command", tags=["telegram"])
async def command_endpoint(req: Request, _: bool = Depends(verify_token)):
    """Command endpoint (Bearer-Auth required)"""
    try:
        data = await req.json()
        request_id = data.get("request_id", f"cmd_{int(time.time())}")
        command = data.get("command", "UNKNOWN")
        
        logger.info(f"Command received: {command} (ID: {request_id})")
        
        # Write CMD safepoint
        write_safepoint("opena4", "kordp", "CMD", data, request_id)
        
        # Placeholder response
        resp_data = {
            "status": "executed",
            "command": command,
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "output": f"Command '{command}' würde hier ausgeführt (Placeholder)"
        }
        
        # Write RESP safepoint
        write_safepoint("kordp", "opena4", "RESP", resp_data, request_id)
        
        return JSONResponse(resp_data)
    
    except Exception as e:
        logger.exception("Command endpoint error")
        error_resp = create_error_response_83("COMMAND_ERROR", str(e))
        return JSONResponse(error_resp, status_code=500)


@app.post("/telegram/message", tags=["telegram"])
async def receive_telegram_message(req: Request):
    """Receive Telegram message (webhook or polling)"""
    try:
        data = await req.json()
        msg_data = TelegramMessage(**data)
        
        # Check user authorization
        if config.telegram_allowed_users and msg_data.user_id not in config.telegram_allowed_users:
            write_safepoint("opena4", "opena4", "ERR", {
                "error": "unauthorized_user",
                "user_id": msg_data.user_id
            }, str(msg_data.message_id))
            return JSONResponse({
                "ok": False,
                "error": "User not authorized"
            }, status_code=403)
        
        # Parse command from message text
        request_id = f"{msg_data.message_id}_{int(time.time())}"
        cmd = Command71(
            request_id=request_id,
            timestamp=msg_data.timestamp,
            command="TELEGRAM_MSG",
            payload={
                "chat_id": msg_data.chat_id,
                "user_id": msg_data.user_id,
                "text": msg_data.text
            },
            project={"name": "telegram_relay"}
        )
        
        # Write CMD safepoint
        write_safepoint("opena4", "opena2", "CMD", cmd.model_dump(), request_id)
        
        # Forward to opena2
        try:
            resp = requests.post(config.opena2_url, json=cmd.model_dump(), timeout=30)
            resp.raise_for_status()
            resp_data = resp.json()
            
            # Write RESP safepoint
            write_safepoint("opena4", "opena2", "RESP", resp_data, request_id)
            
            return JSONResponse({
                "ok": True,
                "request_id": request_id,
                "response": resp_data
            })
        except requests.RequestException as e:
            error_resp = create_error_response_83(
                "FORWARD_ERROR",
                f"Failed to forward to opena2: {str(e)}",
                request_id
            )
            write_safepoint("opena4", "opena2", "ERR", error_resp, request_id)
            return JSONResponse(error_resp, status_code=502)
    
    except ValidationError as e:
        error_resp = create_error_response_83(
            "SCHEMA_VIOLATION",
            "Invalid message schema",
            details={"validation_errors": [{"field": err.get("loc", ["unknown"])[0], "message": str(err.get("msg", "Unknown error"))} for err in e.errors()]}
        )
        write_safepoint("opena4", "opena4", "ERR", error_resp)
        return JSONResponse(error_resp, status_code=400)
    
    except Exception as e:
        logger.exception("Unexpected error in receive_telegram_message")
        error_resp = create_error_response_83(
            "INTERNAL_ERROR",
            f"Server error: {str(e)}"
        )
        write_safepoint("opena4", "opena4", "ERR", error_resp)
        return JSONResponse(error_resp, status_code=500)


@app.post("/github/webhook", tags=["webhooks"])
async def github_webhook(req: Request):
    """GitHub webhook handler for CI/CD notifications"""
    try:
        data = await req.json()
        
        # Extract event details
        event_type = req.headers.get("X-GitHub-Event", "unknown")
        repo = data.get("repository", {}).get("full_name", "unknown")
        ref = data.get("ref", "unknown")
        commit_msg = data.get("head_commit", {}).get("message", "").split("\n")[0]
        
        # Create notification
        message = f"🛠️ GitHub {event_type}: {repo} @ {ref}\n{commit_msg[:100]}"
        
        # Write safepoint
        write_safepoint("github", "opena4", "WEBHOOK", {
            "event_type": event_type,
            "repo": repo,
            "ref": ref,
            "message": commit_msg
        })
        
        logger.info(f"GitHub webhook: {message}")
        return JSONResponse({"ok": True, "message": message})
    
    except Exception as e:
        logger.exception("Error processing GitHub webhook")
        error_resp = create_error_response_83(
            "WEBHOOK_ERROR",
            f"GitHub webhook error: {str(e)}"
        )
        return JSONResponse(error_resp, status_code=500)


@app.get("/status", tags=["status"])
async def status():
    """Service status with recent safepoints"""
    try:
        index_file = config.archiv_dir / "index.jsonl"
        recent_sps = []
        
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-10:]:  # Last 10 entries
                    recent_sps.append(json.loads(line))
        
        return {
            "service": "opena4",
            "status": "operational",
            "config": config.to_dict(),
            "recent_safepoints": recent_sps
        }
    except Exception as e:
        logger.exception("Error in status endpoint")
        return JSONResponse(
            create_error_response_83("STATUS_ERROR", str(e)),
            status_code=500
        )


# ──────────────────────────────────────────────────────────────────────────────
# Telegram Bot Handlers
# ──────────────────────────────────────────────────────────────────────────────

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    if config.telegram_allowed_users and user_id not in config.telegram_allowed_users:
        await update.message.reply_text("❌ Sie sind nicht autorisiert.")
        return
    
    await update.message.reply_text(
        "🤖 Portier Telegram-Agent aktiv!\n\n"
        "Befehle:\n"
        "/browse <url> – Seite analysieren\n"
        "/analyze <file> – Datei analysieren\n"
        "/status – Status anzeigen\n"
        "/help – Hilfe"
    )


async def browse_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /browse command"""
    user_id = update.effective_user.id
    if config.telegram_allowed_users and user_id not in config.telegram_allowed_users:
        await update.message.reply_text("❌ Nicht autorisiert.")
        return
    
    if not context.args:
        await update.message.reply_text("Bitte URL angeben: /browse <url>")
        return
    
    url = " ".join(context.args)
    request_id = f"browse_{int(time.time())}"
    
    try:
        cmd = Command71(
            request_id=request_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            command="BROWSE",
            payload={"url": url},
            routing={"resolved_path": url},
            project={"name": "telegram_relay"}
        )
        
        write_safepoint("opena4", "opena2", "CMD", cmd.model_dump(), request_id)
        
        resp = requests.post(config.opena2_url, json=cmd.model_dump(), timeout=30)
        resp.raise_for_status()
        resp_data = resp.json()
        
        write_safepoint("opena4", "opena2", "RESP", resp_data, request_id)
        
        preview = resp_data.get("preview", str(resp_data))[:800]
        await update.message.reply_text(f"📄 {url}\n\n{preview}")
    
    except Exception as e:
        logger.exception(f"Browse error for {url}")
        error_resp = create_error_response_83("BROWSE_ERROR", str(e), request_id)
        write_safepoint("opena4", "opena2", "ERR", error_resp, request_id)
        await update.message.reply_text(f"❌ Fehler: {str(e)[:100]}")


async def analyze_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /analyze command"""
    user_id = update.effective_user.id
    if config.telegram_allowed_users and user_id not in config.telegram_allowed_users:
        await update.message.reply_text("❌ Nicht autorisiert.")
        return
    
    if not context.args:
        await update.message.reply_text("Bitte Datei angeben: /analyze <file>")
        return
    
    file = " ".join(context.args)
    request_id = f"analyze_{int(time.time())}"
    
    try:
        cmd = Command71(
            request_id=request_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            command="ANALYZE_FILE",
            payload={"file": file},
            routing={"resolved_path": file},
            project={"name": "telegram_relay"}
        )
        
        write_safepoint("opena4", "opena2", "CMD", cmd.model_dump(), request_id)
        
        resp = requests.post(config.opena2_url, json=cmd.model_dump(), timeout=60)
        resp.raise_for_status()
        resp_data = resp.json()
        
        write_safepoint("opena4", "opena2", "RESP", resp_data, request_id)
        
        result = resp_data.get("result", str(resp_data))[:800]
        await update.message.reply_text(f"🧠 Analyse: {file}\n\n{result}")
    
    except Exception as e:
        logger.exception(f"Analyze error for {file}")
        error_resp = create_error_response_83("ANALYZE_ERROR", str(e), request_id)
        write_safepoint("opena4", "opena2", "ERR", error_resp, request_id)
        await update.message.reply_text(f"❌ Fehler: {str(e)[:100]}")


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    try:
        await update.message.reply_text(
            f"✅ opena4 läuft auf Port {config.port}\n"
            f"Verbunden mit opena2 @ {config.opena2_url}\n"
            f"Archive: {config.archiv_dir}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        "📖 Portier Telegram-Agent Hilfe:\n\n"
        "/start – Willkommen\n"
        "/browse <url> – Seite via Browser öffnen\n"
        "/analyze <file> – Datei analysieren\n"
        "/status – Service-Status\n"
        "/help – Diese Hilfe\n\n"
        "Nachrichten werden automatisch in das Portier-System weitergeleitet."
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages"""
    user_id = update.effective_user.id
    if config.telegram_allowed_users and user_id not in config.telegram_allowed_users:
        await update.message.reply_text("❌ Nicht autorisiert.")
        return
    
    text = update.message.text
    request_id = f"msg_{update.message.message_id}_{int(time.time())}"
    
    try:
        cmd = Command71(
            request_id=request_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            command="TELEGRAM_MESSAGE",
            payload={"text": text, "chat_id": update.effective_chat.id},
            project={"name": "telegram_relay"}
        )
        
        write_safepoint("opena4", "opena2", "CMD", cmd.model_dump(), request_id)
        
        # Echo for now
        await update.message.reply_text(f"✓ Nachricht erhalten: {text[:50]}")
    
    except Exception as e:
        logger.exception(f"Message handler error")
        await update.message.reply_text(f"❌ Error: {str(e)[:100]}")


# ──────────────────────────────────────────────────────────────────────────────
# Main Entry Point
# ──────────────────────────────────────────────────────────────────────────────

def main():
    """Main entry point"""
    parser = ArgumentParser(description="opena4 – Telegram Agent")
    parser.add_argument("--port", type=int, default=config.port, help="HTTP server port")
    parser.add_argument("--host", default=config.host, help="HTTP server host")
    parser.add_argument("--telegram-polling", action="store_true", help="Use Telegram polling instead of webhook")
    parser.add_argument("--no-telegram", action="store_true", help="Disable Telegram bot (HTTP only)")
    
    args = parser.parse_args()
    
    # Override config if provided
    if args.port != config.port:
        config.port = args.port
    if args.host != config.host:
        config.host = args.host
    
    logger.info(f"Starting opena4 @ {args.host}:{args.port}")
    
    # Initialize Telegram bot (if enabled and token provided)
    global telegram_mode
    if not args.no_telegram and config.telegram_bot_token:
        try:
            logger.info("Initializing Telegram bot...")
            global telegram_app
            telegram_app = (
                ApplicationBuilder()
                .token(config.telegram_bot_token)
                .build()
            )
            
            # Add handlers
            telegram_app.add_handler(CommandHandler("start", start_handler))
            telegram_app.add_handler(CommandHandler("browse", browse_handler))
            telegram_app.add_handler(CommandHandler("analyze", analyze_handler))
            telegram_app.add_handler(CommandHandler("status", status_handler))
            telegram_app.add_handler(CommandHandler("help", help_handler))
            telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
            
            if args.telegram_polling:
                telegram_mode = "polling"
                logger.info("🚀 Starting Telegram bot (polling mode) in background thread...")
                
                def run_telegram_polling():
                    """Run Telegram polling in background thread"""
                    try:
                        telegram_app.run_polling(drop_pending_updates=True)
                    except Exception as e:
                        logger.error(f"❌ Telegram polling error: {e}")
                
                telegram_thread = threading.Thread(target=run_telegram_polling, daemon=True)
                telegram_thread.start()
                logger.info("✅ Telegram bot (polling) started successfully")
            else:
                telegram_mode = "webhook"
                logger.info("✅ Telegram bot initialized (webhook mode - manual setup required)")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Telegram bot: {e}")
            telegram_mode = "error"
            if config.telegram_bot_token:
                sys.exit(1)
    else:
        telegram_mode = "disabled"
        if args.no_telegram:
            logger.info("⚠️  Telegram bot disabled via --no-telegram")
        elif not config.telegram_bot_token:
            logger.warning("⚠️  TELEGRAM_BOT_TOKEN nicht gesetzt - Bot deaktiviert")
    
    # Start FastAPI server
    logger.info(f"Starting FastAPI server @ {args.host}:{args.port}")
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level=config.log_level.lower(),
        reload=False
    )


if __name__ == "__main__":
    main()
