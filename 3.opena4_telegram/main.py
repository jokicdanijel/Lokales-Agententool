#!/usr/bin/env python3
"""
🔥 PORTIER 3.0 - opena4_telegram FastAPI Agent
Enterprise-Grade Telegram Mobile Integration
"""

import os
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import httpx
import structlog
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ===============================================
# Configuration & Environment
# ===============================================

class Config:
    """PORTIER 3.0 Configuration"""
    
    # Core Settings
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")
    PORT = int(os.getenv("PORT", 12348))
    PORTIER_MODE = os.getenv("PORTIER_MODE", "production")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # PORTIER Stack URLs
    OPENA1_URL = os.getenv("OPENA1_URL", "http://127.0.0.1:12344")
    OPENA2_URL = os.getenv("OPENA2_URL", "http://127.0.0.1:12345") 
    KORDP_URL = os.getenv("KORDP_URL", "http://127.0.0.1:12346")
    DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://127.0.0.1:12349")
    
    # Advanced Settings
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))
    MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", 4096))
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", 30))
    RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", 3))
    AUTO_RETRY = os.getenv("AUTO_RETRY", "true").lower() == "true"

config = Config()

# ===============================================
# Logging Setup
# ===============================================

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = structlog.get_logger("opena4_telegram")

# ===============================================
# Pydantic Models
# ===============================================

class HealthResponse(BaseModel):
    status: str = "ok"
    agent: str = "opena4_telegram"
    port: int = config.PORT
    telegram_connected: bool
    portier_mode: str = config.PORTIER_MODE
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class TelegramMessage(BaseModel):
    chat_id: int
    text: str = Field(max_length=config.MAX_MESSAGE_LENGTH)
    parse_mode: Optional[str] = None

class TelegramResponse(BaseModel):
    status: str
    message_id: Optional[int] = None
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class CommandRequest(BaseModel):
    command: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

class CommandResponse(BaseModel):
    status: str
    result: Any
    execution_time_ms: float
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class MetricsResponse(BaseModel):
    telegram_messages_sent_total: int = 0
    telegram_messages_received_total: int = 0
    telegram_errors_total: int = 0
    response_time_seconds: float = 0.0
    uptime_seconds: float = 0.0
    active_chats: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0

# ===============================================
# FastAPI App Setup
# ===============================================

app = FastAPI(
    title="PORTIER 3.0 - opena4_telegram",
    description="Enterprise-Grade Telegram Mobile Integration Agent",
    version="3.0.0",
    docs_url="/docs" if config.PORTIER_MODE == "development" else None,
    redoc_url="/redoc" if config.PORTIER_MODE == "development" else None
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:12349", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# ===============================================
# Global State & Metrics
# ===============================================

class AgentState:
    """Global agent state"""
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.message_count = 0
        self.error_count = 0
        self.response_times = []
        self.active_chats = set()
        
    def add_message(self):
        self.message_count += 1
        
    def add_error(self):
        self.error_count += 1
        
    def add_response_time(self, time_ms: float):
        self.response_times.append(time_ms)
        if len(self.response_times) > 100:  # Keep only last 100
            self.response_times = self.response_times[-100:]
    
    def get_avg_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def get_uptime_seconds(self) -> float:
        return (datetime.utcnow() - self.start_time).total_seconds()

agent_state = AgentState()

# ===============================================
# Authentication
# ===============================================

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Bearer token"""
    if credentials.credentials != config.BEARER_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    return credentials.credentials

# ===============================================
# Telegram Bot Setup
# ===============================================

telegram_bot: Optional[Bot] = None
telegram_app: Optional[Application] = None

async def initialize_telegram():
    """Initialize Telegram bot"""
    global telegram_bot, telegram_app
    
    if not config.TELEGRAM_TOKEN:
        logger.warning("No Telegram token provided - bot disabled")
        return False
        
    try:
        telegram_bot = Bot(token=config.TELEGRAM_TOKEN)
        telegram_app = Application.builder().token(config.TELEGRAM_TOKEN).build()
        
        # Test connection
        bot_info = await telegram_bot.get_me()
        logger.info(f"✅ Telegram bot initialized: @{bot_info.username}")
        
        # Add handlers
        telegram_app.add_handler(CommandHandler("start", handle_start_command))
        telegram_app.add_handler(MessageHandler(filters.TEXT, handle_message))
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Telegram bot: {e}")
        return False

async def handle_start_command(update: Update, context):
    """Handle /start command"""
    await update.message.reply_text(
        "🤖 PORTIER 3.0 - opena4_telegram\n"
        "Enterprise Telegram Agent aktiv!\n\n"
        f"Agent Port: {config.PORT}\n"
        f"Mode: {config.PORTIER_MODE}\n"
        f"Status: ✅ Online"
    )
    agent_state.active_chats.add(update.message.chat_id)

async def handle_message(update: Update, context):
    """Handle incoming messages"""
    agent_state.add_message()
    agent_state.active_chats.add(update.message.chat_id)
    
    logger.info(f"Received message from {update.message.from_user.username}: {update.message.text[:50]}")
    
    # Echo response (can be customized)
    await update.message.reply_text(f"✅ Message received: {update.message.text}")

# ===============================================
# PORTIER Integration Functions
# ===============================================

async def register_with_portier():
    """Register agent with PORTIER stack"""
    registration_data = {
        "agent_id": "opena4_telegram",
        "port": config.PORT,
        "specialization": "mobile_communication",
        "capabilities": [
            "telegram_messaging",
            "mobile_notifications", 
            "chat_management",
            "media_handling"
        ],
        "endpoints": [
            "/health",
            "/api/send_message",
            "/api/get_updates", 
            "/api/chat_history",
            "/metrics"
        ],
        "status": "active",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{config.OPENA1_URL}/register_agent",
                json=registration_data,
                headers={"Authorization": f"Bearer {config.BEARER_TOKEN}"}
            )
            if response.status_code == 200:
                logger.info("✅ Successfully registered with PORTIER stack")
                return True
            else:
                logger.warning(f"⚠️ Registration failed: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Failed to register with PORTIER: {e}")
        return False

async def archive_to_opena2(request_data: dict, response_data: dict):
    """Archive interaction to opena2"""
    archive_data = {
        "agent": "opena4_telegram",
        "request": request_data,
        "response": response_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f"{config.OPENA2_URL}/archive",
                json=archive_data,
                headers={"Authorization": f"Bearer {config.BEARER_TOKEN}"}
            )
    except Exception as e:
        logger.warning(f"Failed to archive to opena2: {e}")

# ===============================================
# API Routes
# ===============================================

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        telegram_connected=telegram_bot is not None,
        portier_mode=config.PORTIER_MODE
    )

@app.post("/api/send_message", response_model=TelegramResponse)
async def send_message(
    message: TelegramMessage,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """Send Telegram message"""
    start_time = datetime.utcnow()
    
    if not telegram_bot:
        agent_state.add_error()
        raise HTTPException(500, "Telegram bot not initialized")
    
    try:
        sent_message = await telegram_bot.send_message(
            chat_id=message.chat_id,
            text=message.text,
            parse_mode=message.parse_mode
        )
        
        agent_state.add_message()
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        agent_state.add_response_time(execution_time)
        
        response_data = {
            "status": "sent", 
            "message_id": sent_message.message_id
        }
        
        # Archive in background
        background_tasks.add_task(
            archive_to_opena2,
            message.dict(),
            response_data
        )
        
        return TelegramResponse(**response_data)
        
    except Exception as e:
        agent_state.add_error()
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(500, f"Failed to send message: {str(e)}")

@app.post("/api/command", response_model=CommandResponse)
async def execute_command(
    command: CommandRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """Execute agent command"""
    start_time = datetime.utcnow()
    
    try:
        result = await process_command(command.command, command.parameters)
        
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        agent_state.add_response_time(execution_time)
        
        response_data = {
            "status": "success",
            "result": result,
            "execution_time_ms": execution_time
        }
        
        # Archive in background
        background_tasks.add_task(
            archive_to_opena2,
            command.dict(),
            response_data
        )
        
        return CommandResponse(**response_data)
        
    except Exception as e:
        agent_state.add_error()
        logger.error(f"Command execution failed: {e}")
        raise HTTPException(500, f"Command failed: {str(e)}")

async def process_command(command: str, parameters: dict) -> Any:
    """Process specific commands"""
    if command == "get_bot_info":
        if telegram_bot:
            bot_info = await telegram_bot.get_me()
            return {
                "username": bot_info.username,
                "first_name": bot_info.first_name,
                "id": bot_info.id
            }
        return {"error": "Bot not initialized"}
    
    elif command == "get_chat_count":
        return {"active_chats": len(agent_state.active_chats)}
    
    elif command == "health_check":
        return {
            "telegram_connected": telegram_bot is not None,
            "uptime_seconds": agent_state.get_uptime_seconds(),
            "message_count": agent_state.message_count
        }
    
    else:
        raise ValueError(f"Unknown command: {command}")

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get agent metrics (Prometheus compatible)"""
    import psutil
    process = psutil.Process()
    
    return MetricsResponse(
        telegram_messages_sent_total=agent_state.message_count,
        telegram_errors_total=agent_state.error_count,
        response_time_seconds=agent_state.get_avg_response_time() / 1000.0,
        uptime_seconds=agent_state.get_uptime_seconds(),
        active_chats=len(agent_state.active_chats),
        memory_usage_mb=process.memory_info().rss / 1024 / 1024,
        cpu_usage_percent=process.cpu_percent()
    )

@app.get("/status")
async def get_detailed_status():
    """Get detailed agent status"""
    return {
        "agent": "opena4_telegram",
        "port": config.PORT,
        "mode": config.PORTIER_MODE,
        "telegram_connected": telegram_bot is not None,
        "uptime_seconds": agent_state.get_uptime_seconds(),
        "messages_sent": agent_state.message_count,
        "errors": agent_state.error_count,
        "active_chats": len(agent_state.active_chats),
        "avg_response_time_ms": agent_state.get_avg_response_time(),
        "config": {
            "rate_limit": config.RATE_LIMIT_PER_MINUTE,
            "max_message_length": config.MAX_MESSAGE_LENGTH,
            "timeout_seconds": config.TIMEOUT_SECONDS
        }
    }

# ===============================================
# Startup & Lifecycle
# ===============================================

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info(f"🚀 Starting PORTIER 3.0 - opena4_telegram on port {config.PORT}")
    
    # Initialize Telegram
    await initialize_telegram()
    
    # Register with PORTIER stack
    await register_with_portier()
    
    logger.info("✅ opena4_telegram agent fully initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("🛑 Shutting down opena4_telegram agent")
    
    if telegram_app:
        await telegram_app.shutdown()

# ===============================================
# Main Entry Point
# ===============================================

if __name__ == "__main__":
    # Validate required config
    if not config.TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_TOKEN environment variable is required!")
        exit(1)
    
    logger.info(f"🔥 PORTIER 3.0 - opena4_telegram Enterprise Agent")
    logger.info(f"📱 Telegram Token: {'✅ Configured' if config.TELEGRAM_TOKEN else '❌ Missing'}")
    logger.info(f"🔐 Bearer Token: {config.BEARER_TOKEN[:8]}...")
    logger.info(f"🌐 Port: {config.PORT}")
    logger.info(f"⚙️ Mode: {config.PORTIER_MODE}")
    
    # Run FastAPI server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.PORT,
        log_level=config.LOG_LEVEL.lower(),
        reload=config.PORTIER_MODE == "development",
        access_log=True
    )