#!/usr/bin/env python3
"""
opena21 - Workflow Engine Agent
Security Module

Port: 12364
Kürzel: workflowp

PORTIER 3.0 Security Layer
"""

import os
import time
import logging
from typing import Dict, Any, Optional, Set, Callable
from functools import wraps
from collections import defaultdict

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# ==================== Configuration ====================

BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

logger = logging.getLogger(__name__)


# ==================== Secret Masking ====================

SECRET_KEYS: Set[str] = {
    "token", "auth", "password", "apikey", "api_key", "key", 
    "secret", "credentials", "bearer", "authorization",
    "access_token", "refresh_token", "private_key", "session"
}


def mask_secrets(data: Any, mask_value: str = "***MASKED***") -> Any:
    """
    Maskiert Secrets in Dictionaries rekursiv.
    PORTIER 3.0 Spezifikation für Logging & Archivierung.
    """
    if isinstance(data, dict):
        return {
            k: mask_value if any(secret in k.lower() for secret in SECRET_KEYS)
            else mask_secrets(v, mask_value)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [mask_secrets(item, mask_value) for item in data]
    return data


# ==================== Bearer Token Authentication ====================

security = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Verifiziert Bearer Token für geschützte Endpoints.
    
    Raises:
        HTTPException: 401 wenn Token ungültig
    """
    if DEV_MODE and not credentials:
        logger.warning("DEV_MODE: Authentifizierung übersprungen")
        return "dev-mode"
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer Token erforderlich",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if credentials.credentials != BEARER_TOKEN:
        logger.warning(f"Ungültiger Token-Versuch")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Bearer Token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return credentials.credentials


async def optional_verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """Optionale Token-Verifizierung"""
    if not credentials:
        return None
    
    if credentials.credentials == BEARER_TOKEN:
        return credentials.credentials
    
    return None


# ==================== Rate Limiting ====================

class RateLimiter:
    """Simple In-Memory Rate Limiter"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = defaultdict(list)
    
    def _clean_old_requests(self, client_id: str) -> None:
        cutoff = time.time() - self.window_seconds
        self._requests[client_id] = [
            ts for ts in self._requests[client_id] if ts > cutoff
        ]
    
    def is_allowed(self, request: Request) -> bool:
        client_id = self._get_client_id(request)
        self._clean_old_requests(client_id)
        
        if len(self._requests[client_id]) >= self.max_requests:
            return False
        
        self._requests[client_id].append(time.time())
        return True
    
    def _get_client_id(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def get_remaining(self, request: Request) -> int:
        client_id = self._get_client_id(request)
        self._clean_old_requests(client_id)
        return max(0, self.max_requests - len(self._requests[client_id]))


# Rate Limiters
default_limiter = RateLimiter(max_requests=100, window_seconds=60)
workflow_limiter = RateLimiter(max_requests=20, window_seconds=60)  # Strenger für Workflows


# ==================== Workflow Security ====================

class WorkflowSecurityManager:
    """
    Security Manager für Workflow Execution.
    
    Validiert:
    - Agent-Targets
    - Action-Types
    - Parameter-Sanitization
    """
    
    ALLOWED_ACTIONS = {
        "call_agent", "transform_data", "condition", "wait",
        "parallel", "sequence", "retry", "timeout"
    }
    
    ALLOWED_AGENTS = {
        "opena1", "opena2", "opena3", "opena4", "opena5",
        "opena6", "opena7", "opena8", "opena9", "opena10",
        "opena11", "opena12", "opena13", "opena14", "opena15",
        "opena16", "opena17", "opena18", "opena19", "opena20",
        "kordp", "archivp"
    }
    
    DANGEROUS_PATTERNS = {
        "__import__", "eval(", "exec(", "compile(",
        "os.system", "subprocess", "shell=True"
    }
    
    @classmethod
    def validate_action(cls, action: str) -> bool:
        """Validiert Action-Type"""
        return action in cls.ALLOWED_ACTIONS
    
    @classmethod
    def validate_agent(cls, agent: str) -> bool:
        """Validiert Agent-Target"""
        return agent in cls.ALLOWED_AGENTS
    
    @classmethod
    def sanitize_params(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitized Parameter-Dictionary.
        Entfernt gefährliche Patterns.
        """
        sanitized = {}
        for key, value in params.items():
            if isinstance(value, str):
                # Check for dangerous patterns
                if any(pattern in value for pattern in cls.DANGEROUS_PATTERNS):
                    logger.warning(f"Dangerous pattern detected in param: {key}")
                    continue
                sanitized[key] = value
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_params(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    cls.sanitize_params(v) if isinstance(v, dict) else v
                    for v in value
                ]
            else:
                sanitized[key] = value
        return sanitized
    
    @classmethod
    def validate_workflow_definition(cls, workflow: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Vollständige Workflow-Definition-Validierung.
        
        Returns:
            (is_valid, error_message)
        """
        if "name" not in workflow:
            return False, "Workflow name is required"
        
        if "steps" not in workflow or not workflow["steps"]:
            return False, "Workflow must have at least one step"
        
        for i, step in enumerate(workflow["steps"]):
            if "name" not in step:
                return False, f"Step {i} missing name"
            
            if "action" not in step:
                return False, f"Step '{step.get('name', i)}' missing action"
            
            if not cls.validate_action(step["action"]):
                return False, f"Invalid action in step '{step.get('name', i)}': {step['action']}"
            
            if step.get("agent") and not cls.validate_agent(step["agent"]):
                return False, f"Invalid agent in step '{step.get('name', i)}': {step['agent']}"
        
        return True, None


# ==================== Audit Logging ====================

def log_workflow_event(
    event_type: str,
    workflow_id: str,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Loggt Workflow-Events für Audit.
    
    Args:
        event_type: Art des Events
        workflow_id: Workflow ID
        details: Zusätzliche Details
    """
    log_data = {
        "event_type": event_type,
        "workflow_id": workflow_id,
        "timestamp": time.time(),
        "details": mask_secrets(details or {})
    }
    
    if event_type in ("workflow_failed", "security_violation", "timeout"):
        logger.warning(f"Workflow Event: {log_data}")
    else:
        logger.info(f"Workflow Event: {log_data}")


# ==================== Export ====================

__all__ = [
    "BEARER_TOKEN",
    "DEV_MODE",
    "SECRET_KEYS",
    "mask_secrets",
    "security",
    "verify_token",
    "optional_verify_token",
    "RateLimiter",
    "default_limiter",
    "workflow_limiter",
    "WorkflowSecurityManager",
    "log_workflow_event",
]
