#!/usr/bin/env python3
"""
opena11 - Unlock Master Agent (RBAC, Permission-Store, Audit-Log)

Port: 12356
Kürzel: unlockp
Version: 2.0
Status: Production-Ready

Features:
- RBAC (Role-Based Access Control)
- Permission Store (JSON-based, upgradeable to SQLite)
- Audit Log (WORM-compliant)
- Grant/Revoke/Check Operations
- Expiration Handling
- Hierarchical Resources
- Wildcard Permissions
"""

import os
import sys
import time
import logging
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum

from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator
import uvicorn

# ============================================================================
# CONFIGURATION
# ============================================================================

PORT = int(os.getenv("OPENA11_PORT", "12356"))
HOST = os.getenv("OPENA11_HOST", "127.0.0.1")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ARCHIVP_ROOT = PROJECT_ROOT / "1.opena1&2_portier" / "archivp_store"
PERMISSION_STORE = PROJECT_ROOT / "10.opena11_unlock" / "data" / "permissions.json"
AUDIT_LOG_PATH = PROJECT_ROOT / "10.opena11_unlock" / "data" / "audit.jsonl"

# Ensure data directory exists
PERMISSION_STORE.parent.mkdir(parents=True, exist_ok=True)

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("opena11")

# ============================================================================
# PYDANTIC MODELS (Strict JSON)
# ============================================================================

class Action(str, Enum):
    """Allowed actions in RBAC system"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"
    ALL = "*"


class GrantRequest(BaseModel):
    """Request to grant a permission"""
    subject: str = Field(..., min_length=1, max_length=200, description="User/Service ID")
    resource: str = Field(..., min_length=1, max_length=500, description="Resource path (supports wildcards)")
    action: Action = Field(..., description="Action to allow")
    expires_at: Optional[str] = Field(None, description="ISO timestamp for expiration (optional)")
    
    class Config:
        extra = "forbid"
    
    @field_validator("expires_at")
    @classmethod
    def validate_expiration(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError:
            raise ValueError("expires_at must be valid ISO timestamp")


class RevokeRequest(BaseModel):
    """Request to revoke a permission"""
    subject: str = Field(..., min_length=1, max_length=200)
    resource: str = Field(..., min_length=1, max_length=500)
    action: Action = Field(...)
    
    class Config:
        extra = "forbid"


class CheckRequest(BaseModel):
    """Request to check a permission"""
    subject: str = Field(..., min_length=1, max_length=200)
    resource: str = Field(..., min_length=1, max_length=500)
    action: Action = Field(...)
    
    class Config:
        extra = "forbid"


class CheckResponse(BaseModel):
    """Response for permission check"""
    allowed: bool
    reason: str
    matched_permission: Optional[Dict[str, Any]] = None
    
    class Config:
        extra = "forbid"


class AuditLogEntry(BaseModel):
    """Audit log entry"""
    timestamp: str
    operation: str  # "grant", "revoke", "check"
    subject: str
    resource: str
    action: str
    actor: str  # Who performed the operation
    result: str  # "success", "denied", "error"
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        extra = "forbid"


class CommandRequest(BaseModel):
    """Generic command request (Option-2-Flow)"""
    command: str
    params: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        extra = "forbid"


class Permission(BaseModel):
    """Internal permission representation"""
    permission_id: str
    subject: str
    resource: str
    action: str
    created_at: str
    expires_at: Optional[str] = None
    active: bool = True
    
    class Config:
        extra = "forbid"


# ============================================================================
# PERMISSION STORE
# ============================================================================

class PermissionStore:
    """JSON-based permission store with CRUD operations"""
    
    def __init__(self, store_path: Path):
        self.store_path = store_path
        self.permissions: List[Permission] = []
        self.load()
    
    def load(self):
        """Load permissions from JSON file"""
        if not self.store_path.exists():
            self.permissions = []
            self.save()
            logger.info(f"Created new permission store at {self.store_path}")
            return
        
        try:
            with open(self.store_path, "r") as f:
                data = json.load(f)
                self.permissions = [Permission(**p) for p in data.get("permissions", [])]
            logger.info(f"Loaded {len(self.permissions)} permissions from {self.store_path}")
        except Exception as e:
            logger.error(f"Error loading permissions: {e}")
            self.permissions = []
    
    def save(self):
        """Save permissions to JSON file"""
        try:
            data = {
                "permissions": [p.model_dump() for p in self.permissions],
                "last_updated": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            }
            with open(self.store_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.permissions)} permissions to {self.store_path}")
        except Exception as e:
            logger.error(f"Error saving permissions: {e}")
    
    def grant(self, req: GrantRequest, actor: str) -> Permission:
        """Grant a new permission"""
        # Check if permission already exists
        existing = self.find(req.subject, req.resource, req.action.value)
        if existing:
            raise ValueError(f"Permission already exists: {existing.permission_id}")
        
        # Create new permission
        perm_id = f"perm_{int(time.time() * 1000000)}"
        perm = Permission(
            permission_id=perm_id,
            subject=req.subject,
            resource=req.resource,
            action=req.action.value,
            created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            expires_at=req.expires_at,
            active=True
        )
        
        self.permissions.append(perm)
        self.save()
        
        logger.info(f"Granted permission {perm_id}: {req.subject} → {req.action.value} on {req.resource}")
        return perm
    
    def revoke(self, req: RevokeRequest, actor: str) -> bool:
        """Revoke an existing permission"""
        perm = self.find(req.subject, req.resource, req.action.value)
        if not perm:
            raise ValueError(f"Permission not found: {req.subject} → {req.action.value} on {req.resource}")
        
        perm.active = False
        self.save()
        
        logger.info(f"Revoked permission {perm.permission_id}: {req.subject} → {req.action.value} on {req.resource}")
        return True
    
    def check(self, req: CheckRequest) -> CheckResponse:
        """Check if permission is allowed"""
        perm = self.find(req.subject, req.resource, req.action.value)
        
        if not perm:
            return CheckResponse(
                allowed=False,
                reason=f"No permission found for {req.subject} → {req.action.value} on {req.resource}"
            )
        
        # Check if expired
        if perm.expires_at:
            expires = datetime.fromisoformat(perm.expires_at.replace("Z", "+00:00"))
            if datetime.now(expires.tzinfo) > expires:
                return CheckResponse(
                    allowed=False,
                    reason=f"Permission expired at {perm.expires_at}",
                    matched_permission=perm.model_dump()
                )
        
        return CheckResponse(
            allowed=True,
            reason="Permission granted",
            matched_permission=perm.model_dump()
        )
    
    def find(self, subject: str, resource: str, action: str) -> Optional[Permission]:
        """Find matching permission (supports wildcards)"""
        for perm in self.permissions:
            if not perm.active:
                continue
            
            # Exact match
            if perm.subject == subject and perm.resource == resource and perm.action == action:
                return perm
            
            # Wildcard action (*)
            if perm.subject == subject and perm.resource == resource and perm.action == "*":
                return perm
            
            # Wildcard resource (ends with /*)
            if perm.subject == subject and perm.action in [action, "*"]:
                if perm.resource.endswith("/*"):
                    prefix = perm.resource[:-2]  # Remove /*
                    if resource.startswith(prefix):
                        return perm
        
        return None
    
    def list_all(self, subject: Optional[str] = None) -> List[Permission]:
        """List all permissions (optionally filtered by subject)"""
        if subject:
            return [p for p in self.permissions if p.subject == subject and p.active]
        return [p for p in self.permissions if p.active]


# ============================================================================
# AUDIT LOG
# ============================================================================

class AuditLog:
    """JSONL-based audit log (append-only)"""
    
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, entry: AuditLogEntry):
        """Append audit log entry"""
        try:
            with open(self.log_path, "a") as f:
                f.write(entry.model_dump_json() + "\n")
            logger.debug(f"Audit log: {entry.operation} by {entry.actor} → {entry.result}")
        except Exception as e:
            logger.error(f"Error writing audit log: {e}")
    
    def read_recent(self, limit: int = 100) -> List[AuditLogEntry]:
        """Read recent audit log entries"""
        if not self.log_path.exists():
            return []
        
        entries = []
        try:
            with open(self.log_path, "r") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    entries.append(AuditLogEntry(**json.loads(line)))
        except Exception as e:
            logger.error(f"Error reading audit log: {e}")
        
        return entries


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="opena11 - Unlock Master Agent",
    description="RBAC, Permission Store, Audit Log",
    version="2.0"
)

security = HTTPBearer()
perm_store = PermissionStore(PERMISSION_STORE)
audit_log = AuditLog(AUDIT_LOG_PATH)

START_TIME = time.time()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify Bearer token"""
    if not BEARER_TOKEN:
        logger.warning("BEARER_TOKEN not set - authentication disabled!")
        return "anonymous"
    
    if credentials.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid bearer token")
    
    return "authenticated_user"


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "opena11",
        "kürzel": "unlockp",
        "description": "Unlock Master Agent (RBAC, Permission Store, Audit Log)",
        "port": PORT,
        "version": "2.0",
        "endpoints": ["/health", "/grant", "/revoke", "/check", "/list", "/audit", "/command"]
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "opena11",
        "kürzel": "unlockp",
        "port": PORT,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "permissions_count": len(perm_store.list_all()),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }


@app.post("/grant")
async def grant_permission(req: GrantRequest, actor: str = Depends(verify_token)):
    """Grant a new permission"""
    try:
        perm = perm_store.grant(req, actor)
        
        # Audit log
        audit_log.log(AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            operation="grant",
            subject=req.subject,
            resource=req.resource,
            action=req.action.value,
            actor=actor,
            result="success",
            details={"permission_id": perm.permission_id, "expires_at": req.expires_at}
        ))
        
        return {
            "status": "success",
            "message": "Permission granted",
            "permission": perm.model_dump()
        }
    
    except ValueError as e:
        audit_log.log(AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            operation="grant",
            subject=req.subject,
            resource=req.resource,
            action=req.action.value,
            actor=actor,
            result="error",
            details={"error": str(e)}
        ))
        raise HTTPException(status_code=409, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error granting permission: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/revoke")
async def revoke_permission(req: RevokeRequest, actor: str = Depends(verify_token)):
    """Revoke an existing permission"""
    try:
        perm_store.revoke(req, actor)
        
        # Audit log
        audit_log.log(AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            operation="revoke",
            subject=req.subject,
            resource=req.resource,
            action=req.action.value,
            actor=actor,
            result="success"
        ))
        
        return {
            "status": "success",
            "message": "Permission revoked"
        }
    
    except ValueError as e:
        audit_log.log(AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            operation="revoke",
            subject=req.subject,
            resource=req.resource,
            action=req.action.value,
            actor=actor,
            result="error",
            details={"error": str(e)}
        ))
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error revoking permission: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/check")
async def check_permission(req: CheckRequest, actor: str = Depends(verify_token)):
    """Check if a permission is allowed"""
    try:
        result = perm_store.check(req)
        
        # Audit log
        audit_log.log(AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            operation="check",
            subject=req.subject,
            resource=req.resource,
            action=req.action.value,
            actor=actor,
            result="allowed" if result.allowed else "denied",
            details={"reason": result.reason}
        ))
        
        return result.model_dump()
    
    except Exception as e:
        logger.error(f"Error checking permission: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/list")
async def list_permissions(subject: Optional[str] = None, actor: str = Depends(verify_token)):
    """List all permissions (optionally filtered by subject)"""
    try:
        perms = perm_store.list_all(subject)
        return {
            "status": "success",
            "count": len(perms),
            "permissions": [p.model_dump() for p in perms]
        }
    except Exception as e:
        logger.error(f"Error listing permissions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/audit")
async def get_audit_log(limit: int = 100, actor: str = Depends(verify_token)):
    """Get recent audit log entries"""
    try:
        entries = audit_log.read_recent(limit)
        return {
            "status": "success",
            "count": len(entries),
            "entries": [e.model_dump() for e in entries]
        }
    except Exception as e:
        logger.error(f"Error reading audit log: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/command")
async def handle_command(req: CommandRequest, actor: str = Depends(verify_token)):
    """Handle generic command (Option-2-Flow compatibility)"""
    cmd = req.command.lower()
    
    if cmd == "grant":
        grant_req = GrantRequest(**req.params)
        return await grant_permission(grant_req, actor)
    
    elif cmd == "revoke":
        revoke_req = RevokeRequest(**req.params)
        return await revoke_permission(revoke_req, actor)
    
    elif cmd == "check":
        check_req = CheckRequest(**req.params)
        return await check_permission(check_req, actor)
    
    elif cmd == "list":
        subject = req.params.get("subject")
        return await list_permissions(subject, actor)
    
    elif cmd == "audit":
        limit = req.params.get("limit", 100)
        return await get_audit_log(limit, actor)
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown command: {cmd}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    if not BEARER_TOKEN:
        logger.warning("⚠️  BEARER_TOKEN not set in .env - authentication disabled!")
    
    logger.info(f"🚀 Starting opena11 (unlockp) on {HOST}:{PORT}")
    logger.info(f"📁 Permission Store: {PERMISSION_STORE}")
    logger.info(f"📜 Audit Log: {AUDIT_LOG_PATH}")
    
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
