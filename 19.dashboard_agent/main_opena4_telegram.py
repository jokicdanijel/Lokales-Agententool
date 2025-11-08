"""
ELION opena4_telegram – Telegram-Bridge Agent (Port 12348)
FastAPI-basierter Service für Telegram Bot Webhook + Message Routing.

Architektur:
- Telegram Bot Webhook empfängt Messages
- Routing zu opena_finance (Port 12347) für Financial Commands
- Alternative Routing zu opena1 (Port 12344) für andere Commands
- Archiv zu opena2 (Port 12345) für alle Messages
- Port: 12348
- Auth: Webhook-Secret (TELEGRAM_WEBHOOK_SECRET aus .env)
"""

import asyncio
import json
import logging
import re
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ===== CONFIG =====
PORT = 12348
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
ENV_FILE = Path(".env")

# Service Endpoints
OPENA_FINANCE = "http://127.0.0.1:12347"
OPENA1 = "http://127.0.0.1:12344"
OPENA2_ARCHIVE = "http://127.0.0.1:12345/store/archivp"

# ===== LOGGING =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "opena4_telegram.log"),
        logging.StreamHandler()
    ],
)
logger = logging.getLogger("opena4_telegram")

# ===== APP =====
app = FastAPI(
    title="ELION Telegram-Bridge (opena4)",
    version="1.0",
    description="Telegram Bot Webhook + Message Router",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== CONFIGURATION =====
def _read_env() -> Dict[str, str]:
    """Lese alle Werte aus .env"""
    config = {}
    if ENV_FILE.exists():
        lines = ENV_FILE.read_text().strip().split('\n')
        for line in lines:
            if '=' in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    return config

_CONFIG = _read_env()
TELEGRAM_BOT_TOKEN = _CONFIG.get("TELEGRAM_BOT_TOKEN", "123456:ABCDEF_example_do_not_use")
TELEGRAM_WEBHOOK_SECRET = _CONFIG.get("TELEGRAM_WEBHOOK_SECRET", "webhook_secret_16plus_chars_min")
TELEGRAM_ALLOWED_USERS = _CONFIG.get("TELEGRAM_ALLOWED_USERS", "123456789,987654321").split(",")
DASHBOARD_TOKEN = _CONFIG.get("DASHBOARD_ADMIN_TOKEN", "MEIN_SUPER_TOKEN_123")

# ===== HELPER FUNCTIONS =====
def _get_now() -> str:
    """ISO 8601 Timestamp"""
    return datetime.utcnow().isoformat() + "Z"

async def _archive_write(payload: Dict[str, Any]) -> bool:
    """Schreibe zu opena2 (Archivator)"""
    try:
        data = {
            "src": "opena4_telegram",
            "dst": "opena2",
            "kind": "MESSAGE",
            "payload": payload
        }
        req = urllib.request.Request(
            OPENA2_ARCHIVE,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            result = json.loads(r.read().decode())
            logger.info(f"Archive write OK")
            return result.get("written", False)
    except Exception as e:
        logger.error(f"Archive write failed: {e}")
        return False

def _parse_command(text: str) -> tuple[str, List[str]]:
    """Parse Telegram message (command + arguments)"""
    parts = text.strip().split()
    if not parts:
        return ("help", [])
    
    cmd = parts[0].lstrip("/").lower()
    args = parts[1:]
    return (cmd, args)

async def _send_telegram_message(chat_id: int, text: str) -> bool:
    """Sende Nachricht zurück zu Telegram (via Bot API)"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = json.dumps({"chat_id": chat_id, "text": text})
        req = urllib.request.Request(
            url,
            data=data.encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            result = json.loads(r.read().decode())
            return result.get("ok", False)
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False

async def _route_to_finance(command: str, args: List[str], user_id: int) -> str:
    """Route command zu opena_finance"""
    try:
        # Beispiel-Commands:
        # /balance → GET /dashboard
        # /account NAME TYPE BALANCE → POST /account/create
        # /transaction ACCOUNT AMOUNT DESC → POST /transaction/add
        
        if command == "balance":
            req = urllib.request.Request(
                f"{OPENA_FINANCE}/dashboard",
                headers={"Authorization": f"Bearer {DASHBOARD_TOKEN}"},
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=5) as r:
                result = json.loads(r.read().decode())
                accounts = result.get("accounts", {})
                total = accounts.get("total_balance", 0)
                count = accounts.get("count", 0)
                return f"💰 Your Portfolio:\n• Accounts: {count}\n• Total Balance: €{total:,.2f}"
        
        elif command == "accounts":
            req = urllib.request.Request(
                f"{OPENA_FINANCE}/accounts",
                headers={"Authorization": f"Bearer {DASHBOARD_TOKEN}"},
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=5) as r:
                result = json.loads(r.read().decode())
                accounts = result.get("accounts", [])
                if not accounts:
                    return "📋 No accounts found."
                
                text = "📋 Your Accounts:\n"
                for acc in accounts:
                    text += f"• {acc['name']} ({acc['type']}) – €{acc['balance']:,.2f}\n"
                return text
        
        elif command == "transactions":
            if not args or not args[0]:
                return "❌ Usage: /transactions ACCOUNT_ID"
            
            account_id = args[0]
            req = urllib.request.Request(
                f"{OPENA_FINANCE}/transactions?account_id={account_id}",
                headers={"Authorization": f"Bearer {DASHBOARD_TOKEN}"},
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=5) as r:
                result = json.loads(r.read().decode())
                txs = result.get("transactions", [])
                if not txs:
                    return "📊 No transactions found."
                
                text = "📊 Recent Transactions:\n"
                for tx in txs[:5]:  # Last 5
                    text += f"• {tx['description']} – €{tx['amount']:+.2f}\n"
                return text
        
        else:
            return f"❓ Unknown finance command: /{command}"
    
    except Exception as e:
        logger.error(f"Finance routing error: {e}")
        return f"❌ Finance service error: {str(e)}"

# ===== ENDPOINTS =====

@app.get("/health")
async def health():
    """Health Check"""
    return {
        "status": "healthy",
        "service": "opena4_telegram",
        "port": PORT,
        "bot_token": TELEGRAM_BOT_TOKEN[:10] + "...",
        "timestamp": _get_now()
    }

@app.get("/config")
async def config():
    """Configuration (public)"""
    return {
        "service": "opena4_telegram",
        "webhook_secret_length": len(TELEGRAM_WEBHOOK_SECRET),
        "allowed_users": len(TELEGRAM_ALLOWED_USERS),
        "finance_endpoint": OPENA_FINANCE,
        "archive_endpoint": OPENA2_ARCHIVE
    }

@app.post("/webhook/telegram")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(None)
) -> Dict[str, str]:
    """Telegram Webhook Handler (POST from Telegram Bot API)"""
    
    # Validiere Webhook Secret
    if x_telegram_bot_api_secret_token != TELEGRAM_WEBHOOK_SECRET:
        logger.warning("Invalid webhook secret!")
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    
    # Parse Telegram Update
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"JSON parse error: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Extract message
    message = body.get("message")
    if not message:
        logger.debug("No message in update")
        return {"status": "ok"}
    
    chat_id = message.get("chat", {}).get("id")
    user_id = message.get("from", {}).get("id")
    text = message.get("text", "").strip()
    
    if not all([chat_id, user_id, text]):
        logger.warning("Missing required fields in message")
        return {"status": "ok"}
    
    logger.info(f"Telegram message from {user_id}: {text[:50]}")
    
    # Check user allowed
    if str(user_id) not in TELEGRAM_ALLOWED_USERS:
        logger.warning(f"User {user_id} not allowed")
        await _send_telegram_message(chat_id, "❌ You are not authorized to use this bot.")
        return {"status": "ok"}
    
    # Parse command
    cmd, args = _parse_command(text)
    
    # Archive incoming message
    await _archive_write({
        "direction": "incoming",
        "user_id": user_id,
        "chat_id": chat_id,
        "command": cmd,
        "args": args,
        "text": text,
        "timestamp": _get_now(),
        "strict": True
    })
    
    # Route command
    response_text = None
    
    if cmd in ["balance", "accounts", "transactions"]:
        # Finance commands
        response_text = await _route_to_finance(cmd, args, user_id)
    
    elif cmd == "help":
        response_text = """🤖 ELION Telegram Bot – Finance Integration

**Finance Commands:**
/balance – Show total portfolio
/accounts – List all accounts
/transactions ACCOUNT_ID – Show recent transactions

**Example:**
/balance
/accounts
/transactions d4c7969f-0e23-4049-a897-bc7192e9fb19

**Status:**
/health – Bot status
/config – Bot configuration
"""
    
    elif cmd == "health":
        response_text = f"✅ Bot is healthy (Port {PORT})"
    
    elif cmd == "config":
        response_text = f"⚙️ Configuration:\n• Finance Endpoint: {OPENA_FINANCE}\n• Archive Endpoint: {OPENA2_ARCHIVE}"
    
    else:
        response_text = f"❓ Unknown command: /{cmd}\nType /help for available commands."
    
    # Send response
    if response_text:
        sent = await _send_telegram_message(chat_id, response_text)
        
        # Archive outgoing message
        await _archive_write({
            "direction": "outgoing",
            "user_id": user_id,
            "chat_id": chat_id,
            "command": cmd,
            "response": response_text,
            "sent": sent,
            "timestamp": _get_now(),
            "strict": True
        })
    
    return {"status": "ok"}

@app.post("/message/send")
async def send_message(
    chat_id: int,
    text: str,
    token: str = None
) -> Dict[str, Any]:
    """Programmatic message sending (for integrations)"""
    
    if token != DASHBOARD_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        sent = await _send_telegram_message(chat_id, text)
        return {
            "sent": sent,
            "chat_id": chat_id,
            "timestamp": _get_now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/messages/recent")
async def recent_messages(
    limit: int = 10,
    token: str = None
) -> Dict[str, Any]:
    """Fetch recent messages from archive (read-only)"""
    
    if token != DASHBOARD_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        req = urllib.request.Request(
            f"{OPENA2_ARCHIVE}/archiv/last?n={limit}",
            headers={"Content-Type": "application/json"},
            method="GET"
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            result = json.loads(r.read().decode())
            
            # Filter für Telegram messages
            items = result.get("items", [])
            telegram_msgs = [
                item for item in items
                if "opena4_telegram" in item.get("path", "")
            ]
            
            return {
                "count": len(telegram_msgs),
                "messages": telegram_msgs[:limit]
            }
    except Exception as e:
        logger.error(f"Archive fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== MAIN =====
if __name__ == "__main__":
    logger.info(f"🚀 Starting opena4_telegram on port {PORT}")
    logger.info(f"Webhook Secret length: {len(TELEGRAM_WEBHOOK_SECRET)}")
    logger.info(f"Allowed users: {len(TELEGRAM_ALLOWED_USERS)}")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
