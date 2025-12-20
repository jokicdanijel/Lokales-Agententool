#!/usr/bin/env python3
"""
Shared Security Module

Reusable security components for all PORTIER 3.0 agents.
This module consolidates the duplicated security.py files
across all agent directories into a single, maintainable implementation.

Usage:
    from src.pkg.shared.security import (
        verify_token, mask_secrets, RateLimiter, PortPolicyEnforcer
    )
    
    # In FastAPI endpoint
    @app.get("/protected")
    async def protected_route(token: str = Depends(verify_token)):
        return {"status": "authorized"}
"""

import os
import time
import logging
from typing import Dict, Any, Optional, Set
from functools import wraps
from collections import defaultdict

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


logger = logging.getLogger(__name__)


# Environment configuration
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"


# Secret key patterns for masking
SECRET_KEYS: Set[str] = {
    "token", "auth", "password", "apikey", "api_key", "key",
    "secret", "credentials", "bearer", "authorization",
    "access_token", "refresh_token", "private_key", "session"
}


def mask_secrets(data: Any, mask_value: str = "***MASKED***") -> Any:
    """Recursively mask sensitive data in dictionaries and lists.
    
    Args:
        data: Data structure to mask (dict, list, or primitive)
        mask_value: String to use for masked values
        
    Returns:
        Masked copy of the data
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


# FastAPI security scheme
security = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """Verify bearer token authentication.
    
    Args:
        credentials: HTTP bearer credentials from request
        
    Returns:
        Valid token string
        
    Raises:
        HTTPException: If token is missing or invalid
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Bearer Token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return credentials.credentials


async def optional_verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """Optional token verification (allows anonymous access).
    
    Args:
        credentials: HTTP bearer credentials from request
        
    Returns:
        Token string if valid, None if missing or invalid
    """
    if not credentials:
        return None
    if credentials.credentials == BEARER_TOKEN:
        return credentials.credentials
    return None


class RateLimiter:
    """Sliding window rate limiter."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = defaultdict(list)
    
    def _clean_old_requests(self, client_id: str) -> None:
        """Remove requests outside the time window.
        
        Args:
            client_id: Client identifier
        """
        cutoff = time.time() - self.window_seconds
        self._requests[client_id] = [
            ts for ts in self._requests[client_id] if ts > cutoff
        ]
    
    def is_allowed(self, request: Request) -> bool:
        """Check if request is allowed under rate limit.
        
        Args:
            request: FastAPI request object
            
        Returns:
            True if request is allowed, False otherwise
        """
        client_id = self._get_client_id(request)
        self._clean_old_requests(client_id)
        if len(self._requests[client_id]) >= self.max_requests:
            return False
        self._requests[client_id].append(time.time())
        return True
    
    def _get_client_id(self, request: Request) -> str:
        """Extract client identifier from request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Client IP address or "unknown"
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


# Default rate limiter instances
default_limiter = RateLimiter(max_requests=100, window_seconds=60)
api_limiter = RateLimiter(max_requests=60, window_seconds=60)


class PortPolicyEnforcer:
    """PORTIER 3.0 Port Policy Enforcement."""
    
    ALLOWED_RANGE = range(12344, 12400)
    FORBIDDEN_PORTS = [8080]
    
    @classmethod
    def validate_origin(cls, origin: str) -> bool:
        """Validate if origin port is allowed.
        
        Args:
            origin: Origin header value
            
        Returns:
            True if origin is valid, False otherwise
        """
        if not origin:
            return True
        try:
            if ":" in origin:
                port_str = origin.split(":")[-1]
                if port_str.isdigit():
                    port = int(port_str)
                    return port in cls.ALLOWED_RANGE or port == 8080
        except (ValueError, IndexError):
            pass
        return True


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
    "api_limiter",
    "PortPolicyEnforcer"
]
