#!/usr/bin/env python3
"""
ELION Hyper-Dashboard – opena4 (Telegram Agent)
================================================
Port: 12346
Role: Telegram Bot Integration & Message Management
Plan: Basic

Features:
- Send messages via Telegram Bot API
- Receive and process incoming messages
- Manage bot commands
- Group/Channel integration
- Message scheduling
- Media support (photos, documents, etc.)

Dependencies:
- python-telegram-bot (for Telegram API)
- fastapi (for REST API)
- asyncpg (for database)
- redis (for caching)
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import asyncpg
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# ============================================================================
# CONFIGURATION
# ============================================================================

# CANONICAL PORT (from manifest) - DO NOT CHANGE
PORT = 12346

AGENT_ID = "opena4"
AGENT_NAME = "Telegram Agent"
AGENT_ROLE = "Telegram Bot Integration"

# Environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "eden")
DB_USER = os.getenv("DB_USER", "eden_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "change_me_in_production")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
OPENA1_URL = os.getenv("OPENA1_URL", "http://localhost:12344")

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============================================================================
# DATABASE & REDIS CONNECTION
# ============================================================================

db_pool: asyncpg.Pool | None = None
redis_client: redis.Redis | None = None
telegram_app: Application | None = None


async def init_database():
    """Initialize database connection pool"""
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(
            host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, min_size=2, max_size=10
        )
        logger.info("✓ Database connection pool established")

        # Create tables if not exist
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS telegram_messages (
                    message_id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    user_id BIGINT,
                    text TEXT,
                    sent_at TIMESTAMP DEFAULT NOW(),
                    direction VARCHAR(20) DEFAULT 'outgoing',
                    status VARCHAR(20) DEFAULT 'sent'
                )
            """
            )
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS telegram_chats (
                    chat_id BIGINT PRIMARY KEY,
                    chat_type VARCHAR(20),
                    title TEXT,
                    username TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    last_activity TIMESTAMP DEFAULT NOW()
                )
            """
            )
        logger.info("✓ Database tables initialized")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        raise


async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_url = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
        redis_client = redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
        logger.info("✓ Redis connection established")
    except Exception as e:
        logger.error(f"✗ Redis initialization failed: {e}")
        raise


async def init_telegram():
    """Initialize Telegram Bot"""
    global telegram_app
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("⚠ TELEGRAM_BOT_TOKEN not set - bot functionality disabled")
        return

    try:
        telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        # Register handlers
        telegram_app.add_handler(CommandHandler("start", handle_start_command))
        telegram_app.add_handler(CommandHandler("help", handle_help_command))
        telegram_app.add_handler(CommandHandler("status", handle_status_command))
        telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Start bot in background
        await telegram_app.initialize()
        await telegram_app.start()
        logger.info("✓ Telegram bot initialized")
    except Exception as e:
        logger.error(f"✗ Telegram bot initialization failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    # Startup
    logger.info(f"🚀 Starting {AGENT_NAME} on port {PORT}")
    await init_database()
    await init_redis()
    await init_telegram()
    yield
    # Shutdown
    logger.info(f"🛑 Shutting down {AGENT_NAME}")
    if db_pool:
        await db_pool.close()
    if redis_client:
        await redis_client.close()
    if telegram_app:
        await telegram_app.stop()
        await telegram_app.shutdown()


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(title=AGENT_ID, description=f"{AGENT_NAME} - {AGENT_ROLE}", version="1.0.0", lifespan=lifespan)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class SendMessageRequest(BaseModel):
    chat_id: int = Field(..., description="Telegram chat ID")
    text: str = Field(..., description="Message text", max_length=4096)
    parse_mode: str | None = Field(None, description="Message formatting (Markdown, HTML)")
    disable_notification: bool = Field(False, description="Silent message")


class SendMessageResponse(BaseModel):
    success: bool
    message_id: int | None = None
    error: str | None = None


class GetChatsResponse(BaseModel):
    chats: list[dict[str, Any]]
    total: int


class GetMessagesResponse(BaseModel):
    messages: list[dict[str, Any]]
    total: int


# ============================================================================
# TELEGRAM BOT HANDLERS
# ============================================================================


async def handle_start_command(update: Update, context):
    """Handle /start command"""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"👋 Willkommen beim ELION Telegram Bot!\n\n"
        f"Ich bin mit dem ELION Hyper-Dashboard verbunden.\n"
        f"Chat-ID: {chat_id}\n\n"
        f"Verwenden Sie /help für weitere Befehle."
    )

    # Store chat info
    if db_pool:
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO telegram_chats (chat_id, chat_type, title, username)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (chat_id) DO UPDATE SET last_activity = NOW()
            """,
                chat_id,
                update.effective_chat.type,
                update.effective_chat.title,
                update.effective_chat.username,
            )


async def handle_help_command(update: Update, context):
    """Handle /help command"""
    await update.message.reply_text(
        "🤖 ELION Telegram Bot - Befehle:\n\n"
        "/start - Bot starten\n"
        "/help - Diese Hilfe anzeigen\n"
        "/status - Bot-Status anzeigen\n\n"
        "Senden Sie einfach eine Nachricht, um mit dem System zu interagieren."
    )


async def handle_status_command(update: Update, context):
    """Handle /status command"""
    status = {
        "agent": AGENT_ID,
        "port": PORT,
        "connected": True,
        "database": db_pool is not None,
        "redis": redis_client is not None,
    }

    await update.message.reply_text(
        f"✅ Bot Status:\n\n"
        f"Agent: {status['agent']}\n"
        f"Port: {status['port']}\n"
        f"Database: {'✓' if status['database'] else '✗'}\n"
        f"Redis: {'✓' if status['redis'] else '✗'}"
    )


async def handle_message(update: Update, context):
    """Handle incoming text messages"""
    chat_id = update.effective_chat.id
    text = update.message.text
    user_id = update.effective_user.id

    # Store message in database
    if db_pool:
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO telegram_messages (chat_id, user_id, text, direction)
                VALUES ($1, $2, $3, 'incoming')
            """,
                chat_id,
                user_id,
                text,
            )

    # Echo response (можете заменить на свою логику)
    await update.message.reply_text(f"✓ Nachricht empfangen: {text[:50]}{'...' if len(text) > 50 else ''}")


# ============================================================================
# REST API ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health check endpoint (REQUIRED)"""
    return {
        "status": "ok",
        "agent": AGENT_ID,
        "port": PORT,
        "role": AGENT_ROLE,
        "telegram_bot": telegram_app is not None,
        "database": db_pool is not None,
        "redis": redis_client is not None,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/send", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest):
    """
    Send a message via Telegram

    **Plan Gate:** Basic (opena4 is in Basic plan)
    """
    if not telegram_app:
        raise HTTPException(status_code=503, detail="Telegram bot not initialized")

    try:
        bot = telegram_app.bot
        message = await bot.send_message(
            chat_id=request.chat_id,
            text=request.text,
            parse_mode=request.parse_mode,
            disable_notification=request.disable_notification,
        )

        # Store message in database
        if db_pool:
            async with db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO telegram_messages (chat_id, text, direction, status)
                    VALUES ($1, $2, 'outgoing', 'sent')
                """,
                    request.chat_id,
                    request.text,
                )

        logger.info(f"✓ Message sent to chat {request.chat_id}")

        return SendMessageResponse(success=True, message_id=message.message_id)

    except Exception as e:
        logger.error(f"✗ Failed to send message: {e}")
        return SendMessageResponse(success=False, error=str(e))


@app.get("/chats", response_model=GetChatsResponse)
async def get_chats(limit: int = 50, offset: int = 0):
    """
    Get list of chats

    **Plan Gate:** Basic
    """
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT chat_id, chat_type, title, username, created_at, last_activity
                FROM telegram_chats
                ORDER BY last_activity DESC
                LIMIT $1 OFFSET $2
            """,
                limit,
                offset,
            )

            total = await conn.fetchval("SELECT COUNT(*) FROM telegram_chats")

        chats = [dict(row) for row in rows]

        return GetChatsResponse(chats=chats, total=total)

    except Exception as e:
        logger.error(f"✗ Failed to fetch chats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/messages/{chat_id}", response_model=GetMessagesResponse)
async def get_messages(chat_id: int, limit: int = 100, offset: int = 0):
    """
    Get message history for a chat

    **Plan Gate:** Basic
    **Limit:** Read-only (editing requires Pro+)
    """
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT message_id, chat_id, user_id, text, sent_at, direction, status
                FROM telegram_messages
                WHERE chat_id = $1
                ORDER BY sent_at DESC
                LIMIT $2 OFFSET $3
            """,
                chat_id,
                limit,
                offset,
            )

            total = await conn.fetchval("SELECT COUNT(*) FROM telegram_messages WHERE chat_id = $1", chat_id)

        messages = [dict(row) for row in rows]

        return GetMessagesResponse(messages=messages, total=total)

    except Exception as e:
        logger.error(f"✗ Failed to fetch messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/messages/{message_id}")
async def delete_message(message_id: int):
    """
    Delete a message from history

    **Plan Gate:** Pro+ (Basic has read-only access)
    """
    # This would be gated by entitlements in production
    raise HTTPException(
        status_code=403, detail="Message deletion requires Pro plan or higher. Upgrade to unlock this feature."
    )


@app.get("/stats")
async def get_stats():
    """
    Get Telegram bot statistics

    **Plan Gate:** Basic
    """
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        async with db_pool.acquire() as conn:
            total_chats = await conn.fetchval("SELECT COUNT(*) FROM telegram_chats")
            total_messages = await conn.fetchval("SELECT COUNT(*) FROM telegram_messages")
            today_messages = await conn.fetchval(
                """
                SELECT COUNT(*) FROM telegram_messages
                WHERE sent_at >= CURRENT_DATE
            """
            )

        return {
            "total_chats": total_chats,
            "total_messages": total_messages,
            "messages_today": today_messages,
            "agent": AGENT_ID,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"✗ Failed to fetch stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/capabilities")
async def get_capabilities():
    """
    Get agent capabilities (used by opena20 for dashboard generation)

    This endpoint is used by the discovery system to generate accurate dashboards.
    """
    return {
        "agent_id": AGENT_ID,
        "name": AGENT_NAME,
        "port": PORT,
        "role": AGENT_ROLE,
        "plan": "basic",
        "features": {
            "send_messages": True,
            "receive_messages": True,
            "message_history": True,
            "chat_management": True,
            "delete_messages": False,  # Requires Pro+
        },
        "endpoints": ["POST /send", "GET /chats", "GET /messages/{chat_id}", "GET /stats", "GET /health"],
        "limits": {"messages_history": "read_only", "workflow_limit": 4},  # Basic plan limit
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Starting {AGENT_NAME} ({AGENT_ID})")
    logger.info(f"📡 Port: {PORT}")
    logger.info(f"🎯 Role: {AGENT_ROLE}")

    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
