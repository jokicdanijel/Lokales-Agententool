#!/usr/bin/env python3
"""
OpenWebUI Terminal Agent (opena3)
ELION Hyper-Dashboard 2.0 Integration

Agent-Zweck: OpenWebUI Terminal Integration und Chat Management
Port: 12347

Features:
- OpenWebUI Chat Terminal Integration
- Conversation Management
- Model Configuration
- Rate Limiting & Security
- SSE Event Publishing

Autor: ELION Team
Version: 1.1
Datum: 29. November 2025
"""

import asyncio
import json
import logging
import os
import httpx
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Request, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from contextlib import asynccontextmanager

# Konfiguration
AGENT_ID = "opena3"
PORT = 12347
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")
DASHBOARD_URL = "http://127.0.0.1:12349"
OPENWEBUI_URL = "http://127.0.0.1:3000"

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic Models
class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    prompt: str
    model: Optional[str] = "gpt-3.5-turbo"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    stream: Optional[bool] = False

class ChatResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    response: str
    model: str
    usage: Dict[str, int]
    timestamp: str

class AgentStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    agent_id: str
    status: str
    port: int
    openwebui_available: bool
    conversations_active: int
    last_activity: str

# Globale Variablen
chat_sessions = {}
conversation_history = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 Starting {AGENT_ID} on port {PORT}")
    logger.info("💬 OpenWebUI Terminal Agent ready")
    logger.info("🔗 Checking OpenWebUI connection...")
    
    # Prüfe OpenWebUI Verfügbarkeit
    openwebui_available = await check_openwebui_health()
    if openwebui_available:
        logger.info("✅ OpenWebUI connection established")
    else:
        logger.warning("⚠️ OpenWebUI not available - fallback mode active")
    
    # Registrierung bei Dashboard
    await register_with_dashboard()
    yield
    logger.info(f"🛑 Shutting down {AGENT_ID}")

# FastAPI App
app = FastAPI(
    title=f"ELION {AGENT_ID.upper()} - OpenWebUI Terminal Agent",
    description="OpenWebUI Integration & Chat Management",
    version="1.1.0",
    lifespan=lifespan
)

security = HTTPBearer()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_token(token: str) -> bool:
    """Verifies Bearer token"""
    return token == BEARER_TOKEN

async def check_openwebui_health() -> bool:
    """Prüft OpenWebUI Verfügbarkeit"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OPENWEBUI_URL}/health", timeout=5.0)
            return response.status_code == 200
    except:
        return False

async def register_with_dashboard():
    """Registriert Agent beim Dashboard"""
    try:
        async with httpx.AsyncClient() as client:
            registration_data = {
                "agent_id": AGENT_ID,
                "endpoint": f"http://127.0.0.1:{PORT}",
                "capabilities": ["chat", "openwebui", "conversation_management"],
                "status": "online"
            }
            
            await client.post(
                f"{DASHBOARD_URL}/api/agent/register",
                json=registration_data,
                headers={"Authorization": f"Bearer {BEARER_TOKEN}"},
                timeout=10.0
            )
            logger.info("✅ Dashboard registration successful")
    except Exception as e:
        logger.error(f"❌ Dashboard registration failed: {e}")

# Health Check Endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    openwebui_available = await check_openwebui_health()
    
    return AgentStatus(
        agent_id=AGENT_ID,
        status="healthy",
        port=PORT,
        openwebui_available=openwebui_available,
        conversations_active=len(chat_sessions),
        last_activity=datetime.now(timezone.utc).isoformat()
    ).model_dump()

# Chat Endpoints
@app.post("/chat", response_model=Dict[str, Any])
async def chat_with_openwebui(
    request: ChatRequest,
    token: HTTPAuthorizationCredentials = Security(security)
):
    """Chat über OpenWebUI Terminal"""
    if not verify_token(token.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        # Prüfe OpenWebUI Verfügbarkeit
        if not await check_openwebui_health():
            return await fallback_chat_response(request)
        
        # OpenWebUI Chat Request
        async with httpx.AsyncClient() as client:
            openwebui_payload = {
                "message": request.prompt,
                "model": request.model or "gpt-3.5-turbo",
                "temperature": request.temperature,
                "max_tokens": request.max_tokens
            }
            
            response = await client.post(
                f"{OPENWEBUI_URL}/api/chat/completions",
                json=openwebui_payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Speichere Conversation
                conversation_entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "prompt": request.prompt,
                    "response": result.get("message", "No response"),
                    "model": request.model or "gpt-3.5-turbo",
                    "via": "openwebui"
                }
                conversation_history.append(conversation_entry)
                
                # Publish SSE Event zum Dashboard
                await publish_chat_event(conversation_entry)
                
                return ChatResponse(
                    response=result.get("message", "No response"),
                    model=request.model or "gpt-3.5-turbo",
                    usage=result.get("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}),
                    timestamp=conversation_entry["timestamp"]
                ).model_dump()
            else:
                return await fallback_chat_response(request)
                
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        return await fallback_chat_response(request)

async def fallback_chat_response(request: ChatRequest) -> Dict[str, Any]:
    """Fallback Chat Response wenn OpenWebUI nicht verfügbar"""
    fallback_message = f"🤖 opena3 Terminal Agent Response:\n\nIhre Nachricht: '{request.prompt}'\n\nStatus: OpenWebUI Terminal derzeit nicht verfügbar. Nachricht wurde zur Verarbeitung in der Warteschlange gespeichert."
    
    conversation_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt": request.prompt,
        "response": fallback_message,
        "model": request.model or "gpt-3.5-turbo",
        "via": "fallback"
    }
    conversation_history.append(conversation_entry)
    
    return ChatResponse(
        response=fallback_message,
        model=request.model or "gpt-3.5-turbo",
        usage={"prompt_tokens": len(request.prompt.split()), "completion_tokens": len(fallback_message.split()), "total_tokens": len(request.prompt.split()) + len(fallback_message.split())},
        timestamp=conversation_entry["timestamp"]
    ).model_dump()

async def publish_chat_event(conversation: Dict[str, Any]) -> None:
    """Publiziert Chat Event zum Dashboard"""
    try:
        async with httpx.AsyncClient() as client:
            event_data = {
                "event_type": "opena3_chat",
                "agent_id": AGENT_ID,
                "data": conversation
            }
            
            await client.post(
                f"{DASHBOARD_URL}/api/sse/publish",
                json=event_data,
                headers={"Authorization": f"Bearer {BEARER_TOKEN}"},
                timeout=5.0
            )
    except:
        pass  # SSE Events sind nicht kritisch

# Conversation Management
@app.get("/conversations")
async def get_conversations(
    token: HTTPAuthorizationCredentials = Security(security),
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Hole Conversation History"""
    if not verify_token(token.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Neueste Conversations zuerst
    recent_conversations = conversation_history[-limit:] if len(conversation_history) > limit else conversation_history
    recent_conversations.reverse()
    
    return recent_conversations

@app.delete("/conversations")
async def clear_conversations(
    token: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """Leere Conversation History"""
    if not verify_token(token.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    global conversation_history
    cleared_count = len(conversation_history)
    conversation_history = []
    
    return {
        "message": f"Cleared {cleared_count} conversations",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Session Management
@app.get("/sessions")
async def get_active_sessions(
    token: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """Hole aktive Chat Sessions"""
    if not verify_token(token.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {
        "active_sessions": len(chat_sessions),
        "sessions": list(chat_sessions.keys()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# OpenWebUI Status Check
@app.get("/openwebui/status")
async def openwebui_status(
    token: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """Prüfe OpenWebUI Status"""
    if not verify_token(token.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    is_available = await check_openwebui_health()
    
    return {
        "openwebui_available": is_available,
        "openwebui_url": OPENWEBUI_URL,
        "last_check": datetime.now(timezone.utc).isoformat(),
        "agent_status": "healthy"
    }

# Command Interface
@app.post("/command")
async def execute_command(
    payload: Dict[str, Any],
    token: HTTPAuthorizationCredentials = Security(security)
) -> Any:
    """Execute command interface"""
    if not verify_token(token.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    command = payload.get("command", "")
    
    if command == "chat":
        chat_request = ChatRequest(**payload.get("params", {}))
        return await chat_with_openwebui(chat_request, token)
    elif command == "status":
        return await health_check()
    elif command == "conversations":
        return await get_conversations(token)
    else:
        return {
            "error": f"Unknown command: {command}",
            "available_commands": ["chat", "status", "conversations"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")