# 🔐 OPENA11 Unlock Master Agent - PORTIER PAS-6.0
# RBAC Engine • Permission Store • WORM Audit • OpenAI Integration
# Port: 12357

import os
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("opena11_unlock")

# ============================================================
# Configuration
# ============================================================

class Config:
    """Agent configuration"""
    NAME = "opena11_unlock"
    VERSION = "6.0.0"
    PORT = int(os.getenv("OPENA11_PORT", "12357"))
    HOST = os.getenv("OPENA11_HOST", "0.0.0.0")
    KUERZEL = "unlockp"
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_OPENA11", os.getenv("OPENAI_API_KEY", ""))
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Security
    BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
    JWT_SECRET = os.getenv("JWT_SECRET_KEY", "unlock-secret-key")
    
    # Dashboard
    DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://127.0.0.1:12349")

# ============================================================
# Pydantic Models (strict)
# ============================================================

class CommandRequest(BaseModel):
    """Command request model"""
    action: str = Field(..., description="Action to execute: grant, revoke, check, list, ai_analyze")
    params: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    
    class Config:
        extra = "forbid"

class GrantParams(BaseModel):
    """Grant permission parameters"""
    subject: str = Field(..., description="User or entity ID")
    resource: str = Field(..., description="Resource path or identifier")
    action: str = Field(..., description="Permission action: read, write, delete, admin, *")
    expires: int = Field(default=0, description="Expiration timestamp (0 = never)")
    
    class Config:
        extra = "forbid"

class CheckParams(BaseModel):
    """Check permission parameters"""
    subject: str
    resource: str
    action: str
    
    class Config:
        extra = "forbid"

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    kuerzel: str
    version: str
    uptime_seconds: float
    permissions_count: int
    openai_connected: bool
    timestamp: str
    
    class Config:
        extra = "forbid"

# ============================================================
# Import Modules
# ============================================================

from modules.rbac_engine import RBACEngine
from modules.permission_store import PermissionStore
from modules.audit_log import AuditLog
from modules.metrics import UnlockMetrics, get_metrics
from modules.ai_unlock_engine import AIUnlockEngine

# ============================================================
# Application Lifecycle
# ============================================================

START_TIME = time.time()

# Initialize components
permission_store = PermissionStore()
rbac_engine = RBACEngine(permission_store)
audit_log = AuditLog()
metrics = get_metrics()
ai_engine = AIUnlockEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info(f"🔐 Starting {Config.NAME} v{Config.VERSION} on port {Config.PORT}")
    
    # Initialize AI engine
    await ai_engine.initialize()
    
    # Load persisted permissions
    await permission_store.load()
    
    logger.info(f"✅ {Config.NAME} ready - {permission_store.count()} permissions loaded")
    
    yield
    
    # Shutdown
    logger.info(f"🛑 Shutting down {Config.NAME}")
    await permission_store.persist()
    await audit_log.persist()

# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="OPENA11 Unlock Master",
    description="RBAC Engine • Permission Store • WORM Audit Log • AI Security Analysis",
    version=Config.VERSION,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """Verify Bearer token"""
    if not Config.BEARER_TOKEN:
        return True  # No token configured = open access
    if not credentials:
        return False
    return credentials.credentials == Config.BEARER_TOKEN

# ============================================================
# Routes
# ============================================================

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service=Config.NAME,
        kuerzel=Config.KUERZEL,
        version=Config.VERSION,
        uptime_seconds=round(time.time() - START_TIME, 2),
        permissions_count=permission_store.count(),
        openai_connected=ai_engine.is_connected(),
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/status")
async def status():
    """Detailed status endpoint"""
    return {
        "agent": Config.NAME,
        "kuerzel": Config.KUERZEL,
        "version": Config.VERSION,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "permissions": {
            "total": permission_store.count(),
            "subjects": permission_store.subject_count(),
            "summary": permission_store.summary()
        },
        "audit": {
            "total_events": audit_log.count(),
            "last_event": audit_log.last_event()
        },
        "ai_engine": {
            "connected": ai_engine.is_connected(),
            "model": Config.OPENAI_MODEL
        },
        "config": {
            "port": Config.PORT,
            "dashboard_url": Config.DASHBOARD_URL
        }
    }

@app.post("/command")
async def command(request: CommandRequest, authorized: bool = Depends(verify_token)):
    """Execute RBAC command"""
    action = request.action
    params = request.params
    
    logger.info(f"Command received: {action} with params: {params}")
    metrics.increment("commands_received")
    
    try:
        # GRANT - Add permission
        if action == "grant":
            grant_params = GrantParams(**params)
            result = await permission_store.grant(
                subject=grant_params.subject,
                resource=grant_params.resource,
                action=grant_params.action,
                expires=grant_params.expires
            )
            await audit_log.log("grant", params, result)
            metrics.increment("permissions_granted")
            return {"status": "success", "result": result}
        
        # REVOKE - Remove permission
        if action == "revoke":
            result = await permission_store.revoke(
                subject=params.get("subject"),
                resource=params.get("resource"),
                action=params.get("action")
            )
            await audit_log.log("revoke", params, result)
            metrics.increment("permissions_revoked")
            return {"status": "success", "result": result}
        
        # CHECK - Verify permission
        if action == "check":
            check_params = CheckParams(**params)
            allowed = rbac_engine.check(
                subject=check_params.subject,
                resource=check_params.resource,
                action=check_params.action
            )
            await audit_log.log("check", params, {"allowed": allowed})
            metrics.increment("permission_checks")
            return {"status": "success", "allowed": allowed}
        
        # LIST - List permissions for subject
        if action == "list":
            subject = params.get("subject")
            if subject:
                permissions = permission_store.get(subject)
            else:
                permissions = permission_store.dump()
            return {"status": "success", "permissions": permissions}
        
        # AI_ANALYZE - AI-powered security analysis
        if action == "ai_analyze":
            analysis = await ai_engine.analyze_permissions(
                permissions=permission_store.dump(),
                query=params.get("query", "Analysiere die Berechtigungsstruktur")
            )
            await audit_log.log("ai_analyze", params, {"analysis_performed": True})
            metrics.increment("ai_analyses")
            return {"status": "success", "analysis": analysis}
        
        # AI_RECOMMEND - Get AI recommendations
        if action == "ai_recommend":
            recommendations = await ai_engine.recommend_permissions(
                subject=params.get("subject"),
                context=params.get("context", ""),
                current_permissions=permission_store.get(params.get("subject", ""))
            )
            return {"status": "success", "recommendations": recommendations}
        
        # BULK_GRANT - Grant multiple permissions
        if action == "bulk_grant":
            grants = params.get("grants", [])
            results = []
            for grant in grants:
                result = await permission_store.grant(**grant)
                results.append(result)
                await audit_log.log("grant", grant, result)
            metrics.increment("permissions_granted", len(grants))
            return {"status": "success", "results": results, "count": len(results)}
        
        # CLEAR_SUBJECT - Remove all permissions for subject
        if action == "clear_subject":
            subject = params.get("subject")
            if not subject:
                raise HTTPException(status_code=400, detail="Subject required")
            result = await permission_store.clear_subject(subject)
            await audit_log.log("clear_subject", params, result)
            return {"status": "success", "result": result}
        
        # Unknown action
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
        
    except Exception as e:
        logger.error(f"Command error: {e}")
        metrics.increment("command_errors")
        await audit_log.log("error", params, {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_logs(limit: int = 100, event_type: Optional[str] = None):
    """Get audit logs"""
    logs = audit_log.read(limit=limit, event_type=event_type)
    return {
        "status": "success",
        "total": audit_log.count(),
        "returned": len(logs),
        "logs": logs
    }

@app.get("/metrics")
async def get_metrics_endpoint():
    """Get metrics"""
    return metrics.get_summary()

@app.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Get metrics in Prometheus format"""
    return metrics.to_prometheus_format()

@app.get("/config")
async def get_config():
    """Get agent configuration (non-sensitive)"""
    return {
        "name": Config.NAME,
        "kuerzel": Config.KUERZEL,
        "version": Config.VERSION,
        "port": Config.PORT,
        "openai_model": Config.OPENAI_MODEL,
        "dashboard_url": Config.DASHBOARD_URL
    }

# ============================================================
# Specialized Endpoints
# ============================================================

@app.post("/specialized/quick_grant")
async def quick_grant(subject: str, resource: str, action: str = "read"):
    """Quick grant endpoint"""
    result = await permission_store.grant(subject=subject, resource=resource, action=action)
    await audit_log.log("quick_grant", {"subject": subject, "resource": resource, "action": action}, result)
    return {"status": "success", "result": result}

@app.post("/specialized/quick_check")
async def quick_check(subject: str, resource: str, action: str = "read"):
    """Quick check endpoint"""
    allowed = rbac_engine.check(subject=subject, resource=resource, action=action)
    return {"allowed": allowed}

@app.get("/specialized/subject/{subject}")
async def get_subject_permissions(subject: str):
    """Get all permissions for a subject"""
    return {
        "subject": subject,
        "permissions": permission_store.get(subject),
        "count": len(permission_store.get(subject))
    }

@app.delete("/specialized/subject/{subject}")
async def delete_subject(subject: str):
    """Delete all permissions for a subject"""
    result = await permission_store.clear_subject(subject)
    await audit_log.log("delete_subject", {"subject": subject}, result)
    return {"status": "success", "result": result}

@app.post("/specialized/ai_security_scan")
async def ai_security_scan():
    """AI-powered security scan of all permissions"""
    scan_result = await ai_engine.security_scan(permission_store.dump())
    await audit_log.log("security_scan", {}, {"scan_completed": True})
    return {"status": "success", "scan": scan_result}

# ============================================================
# Static Files & Dashboard
# ============================================================

# Mount static files for dashboard
app.mount("/html", StaticFiles(directory="html"), name="html")

@app.get("/")
async def root():
    """Redirect to dashboard"""
    return FileResponse("html/index.html")

# ============================================================
# Main Entry Point
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=False,
        log_level="info"
    )
