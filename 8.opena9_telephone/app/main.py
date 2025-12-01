# 📞 Telephone Agent 6.0 - PORTIER PAS-6.0 (opena9)
# Advanced Telephony & Voice Call Automation with AI Integration
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false

import os
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules with proper error handling
TelephonyCore: Any = None
TelephonyAPI: Any = None
AIVoiceEngine: Any = None
SpeechToText: Any = None
TelephonyMetrics: Any = None

try:
    from modules.telephony_core import TelephonyCore  # type: ignore
    from modules.telephony_api import TelephonyAPI  # type: ignore
    from modules.ai_voice_engine import AIVoiceEngine  # type: ignore
    from modules.speech_to_text import SpeechToText  # type: ignore
    from modules.metrics import TelephonyMetrics  # type: ignore
except ImportError as e:
    print(f"❌ Module import error: {e}")

# Security
security = HTTPBearer()
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "fallback-token-telephone-6.0")

# Global instances
core: Any = None
api: Any = None
ai_engine: Any = None
stt_engine: Any = None
metrics: Any = None

# ===============================================
# 🔐 Security & Authentication
# ===============================================

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Bearer token authentication"""
    if credentials.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return credentials.credentials

# ===============================================
# 📋 Pydantic Models
# ===============================================

class CommandRequest(BaseModel):
    """Standard command request model"""
    command: str = Field(..., description="Telephony command to execute")
    args: Dict[str, Any] = Field(default_factory=dict, description="Command arguments")
    
    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "command": "make_call",
                "args": {
                    "to": "+49123456789",
                    "script": "Hello, this is an automated call from Telephone Agent 6.0"
                }
            }
        }

class SpecializedRequest(BaseModel):
    """AI specialized request model"""
    action: str = Field(..., description="AI voice action to perform")
    text: Optional[str] = Field(None, description="Text for TTS generation")
    call_id: Optional[str] = Field(None, description="Call ID for context")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "action": "generate_voice_reply",
                "text": "Thank you for calling. How can I help you today?",
                "context": {"tone": "professional", "language": "english"}
            }
        }

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    port: int = Field(..., description="Service port")
    timestamp: str = Field(..., description="Current timestamp")
    telephony_status: str = Field(..., description="Telephony API connection status")
    openai_status: str = Field(..., description="OpenAI API status")

# ===============================================
# 🚀 Application Lifecycle
# ===============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle"""
    global core, api, ai_engine, stt_engine, metrics
    
    print("🚀 Starting Telephone Agent 6.0...")
    
    try:
        # Initialize modules if available
        if TelephonyCore:
            core = TelephonyCore()
            await core.initialize()
        if TelephonyAPI:
            api = TelephonyAPI()
            await api.initialize()
        if AIVoiceEngine:
            ai_engine = AIVoiceEngine()
            await ai_engine.initialize()
        if SpeechToText:
            stt_engine = SpeechToText()
        if TelephonyMetrics:
            metrics = TelephonyMetrics()
        
        print("✅ Telephone Agent 6.0 initialized successfully")
        
        yield
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
    finally:
        print("🛑 Shutting down Telephone Agent 6.0...")
        if api:
            await api.close()
        if metrics:
            await metrics.save_stats()

# ===============================================
# 📞 FastAPI Application
# ===============================================

app = FastAPI(
    title="opena9_telephone",
    description="Telephone & Voice Call Agent with AI Integration - PORTIER PAS-6.0",
    version="6.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "health", "description": "Health and status endpoints"},
        {"name": "telephony", "description": "Phone call operations"},
        {"name": "ai", "description": "AI-powered voice functions"},
        {"name": "metrics", "description": "Performance and usage metrics"},
        {"name": "system", "description": "System configuration and logs"}
    ]
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for dashboard
app.mount("/html", StaticFiles(directory="html"), name="html")

# ===============================================
# 🔍 Core API Endpoints
# ===============================================

@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Comprehensive health check with Telephony and OpenAI status"""
    try:
        telephony_status = "connected" if api and await api.test_connection() else "disconnected"
        openai_status = "connected" if ai_engine and await ai_engine.test_connection() else "disconnected"
        
        return HealthResponse(
            status="ok",
            service="opena9_telephone",
            version="6.0.0",
            port=12355,
            timestamp=datetime.now().isoformat(),
            telephony_status=telephony_status,
            openai_status=openai_status
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.get("/status", tags=["health"])
async def detailed_status(token: str = Depends(verify_token)):
    """Detailed agent status with configuration info"""
    if not core:
        raise HTTPException(status_code=503, detail="Core module not initialized")
    
    try:
        status_data = await core.get_status()
        status_data.update({
            "metrics": await metrics.get_current_stats() if metrics else {},
            "ai_engine_status": await ai_engine.get_status() if ai_engine else "unavailable",
            "telephony_api_status": await api.get_status() if api else "unavailable"
        })
        return status_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

@app.post("/command", tags=["telephony"])
async def execute_command(
    request: CommandRequest, 
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """Execute telephony operations with background metrics tracking"""
    if not core:
        raise HTTPException(status_code=503, detail="Core module not initialized")
    
    try:
        # Log command execution
        if metrics:
            background_tasks.add_task(metrics.log_command, request.command)
        
        result = await core.execute_command(request.command, request.args)
        
        # Log success
        if metrics:
            background_tasks.add_task(metrics.log_success, request.command)
            
        return {
            "status": "success",
            "command": request.command,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        # Log error
        if metrics:
            background_tasks.add_task(metrics.log_error, request.command, str(e))
        
        raise HTTPException(status_code=400, detail=f"Command execution failed: {str(e)}")

@app.post("/specialized", tags=["ai"])
async def ai_specialized(
    request: SpecializedRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """AI-powered voice and telephony functions"""
    if not ai_engine:
        raise HTTPException(status_code=503, detail="AI engine not initialized")
    
    try:
        # Log AI function usage
        if metrics:
            background_tasks.add_task(metrics.log_ai_function, request.action)
        
        result = await ai_engine.handle_specialized_request(request.action, {
            "text": request.text,
            "call_id": request.call_id,
            **request.context
        })
        
        return {
            "status": "success",
            "action": request.action,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        if metrics:
            background_tasks.add_task(metrics.log_error, f"ai_{request.action}", str(e))
        
        raise HTTPException(status_code=400, detail=f"AI function failed: {str(e)}")

@app.get("/metrics", tags=["metrics"])
async def get_metrics(token: str = Depends(verify_token)):
    """Performance and usage metrics"""
    if not metrics:
        raise HTTPException(status_code=503, detail="Metrics module not initialized")
    
    try:
        return await metrics.get_comprehensive_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")

@app.get("/logs", tags=["system"])
async def get_logs(token: str = Depends(verify_token)):
    """Recent system logs"""
    if not core:
        raise HTTPException(status_code=503, detail="Core module not initialized")
    
    try:
        return await core.get_recent_logs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Log retrieval failed: {str(e)}")

@app.get("/config", tags=["system"])
async def get_config(token: str = Depends(verify_token)):
    """Current agent configuration"""
    if not core:
        raise HTTPException(status_code=503, detail="Core module not initialized")
    
    try:
        config = await core.get_configuration()
        # Remove sensitive information
        config.pop("twilio_auth_token", None)
        config.pop("openai_api_key", None)
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration retrieval failed: {str(e)}")

# ===============================================
# 🌐 Dashboard Routes
# ===============================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Redirect to dashboard"""
    return """<html><head><meta http-equiv="refresh" content="0; url=/html/index.html"></head></html>"""

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Alternative dashboard access"""
    try:
        with open("html/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """<html><body><h1>Telephone Agent 6.0</h1><p>Dashboard not available</p></body></html>"""

# ===============================================
# 🚀 Application Entry Point
# ===============================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Telephone Agent 6.0")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=12355, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")
    
    args = parser.parse_args()
    
    print(f"🚀 Starting Telephone Agent 6.0 on {args.host}:{args.port}")
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )