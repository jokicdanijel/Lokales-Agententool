#!/usr/bin/env python3
"""
opena20 - Dashboard Agent
Security Module

Port: 12349
Kürzel: dashp

PORTIER 3.0 Security Layer
- Bearer Token Authentication
- Rate Limiting
- Request Validation
- Secret Masking
"""

import logging
import os
import time
from collections import defaultdict
from collections.abc import Callable
from functools import wraps
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# ==================== Configuration ====================

BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

logger = logging.getLogger(__name__)


# ==================== Secret Masking ====================

SECRET_KEYS: set[str] = {
    "token",
    "auth",
    "password",
    "apikey",
    "api_key",
    "key",
    "secret",
    "credentials",
    "bearer",
    "authorization",
    "access_token",
    "refresh_token",
    "private_key",
    "session",
}


def mask_secrets(data: Any, mask_value: str = "***MASKED***") -> Any:
    """
    Maskiert Secrets in Dictionaries rekursiv.
    PORTIER 3.0 Spezifikation für Logging & Archivierung.
    """
    if isinstance(data, dict):
        return {
            k: mask_value if any(secret in k.lower() for secret in SECRET_KEYS) else mask_secrets(v, mask_value)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [mask_secrets(item, mask_value) for item in data]
    return data


# ==================== Bearer Token Authentication ====================

security = HTTPBearer(auto_error=False)


async def verify_token(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> str:
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
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.credentials != BEARER_TOKEN:
        logger.warning("Ungültiger Token-Versuch von IP: [masked]")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Bearer Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials


async def optional_verify_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str | None:
    """
    Optionale Token-Verifizierung (für Endpoints mit optionaler Auth).
    """
    if not credentials:
        return None

    if credentials.credentials == BEARER_TOKEN:
        return credentials.credentials

    return None


# ==================== Rate Limiting ====================


class RateLimiter:
    """
    Simple In-Memory Rate Limiter.

    Args:
        max_requests: Maximale Requests pro Zeitfenster
        window_seconds: Zeitfenster in Sekunden
    """

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list] = defaultdict(list)

    def _clean_old_requests(self, client_id: str) -> None:
        """Entfernt abgelaufene Requests"""
        cutoff = time.time() - self.window_seconds
        self._requests[client_id] = [ts for ts in self._requests[client_id] if ts > cutoff]

    def is_allowed(self, request: Request) -> bool:
        """
        Prüft ob Request erlaubt ist.

        Args:
            request: FastAPI Request Objekt

        Returns:
            True wenn erlaubt, False sonst
        """
        client_id = self._get_client_id(request)
        self._clean_old_requests(client_id)

        if len(self._requests[client_id]) >= self.max_requests:
            return False

        self._requests[client_id].append(time.time())
        return True

    def _get_client_id(self, request: Request) -> str:
        """Ermittelt Client-Identifikator"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def get_remaining(self, request: Request) -> int:
        """Gibt verbleibende Requests zurück"""
        client_id = self._get_client_id(request)
        self._clean_old_requests(client_id)
        return max(0, self.max_requests - len(self._requests[client_id]))

    def get_reset_time(self, request: Request) -> float:
        """Gibt Reset-Zeit in Sekunden zurück"""
        client_id = self._get_client_id(request)
        if not self._requests[client_id]:
            return 0
        oldest = min(self._requests[client_id])
        return max(0, (oldest + self.window_seconds) - time.time())


# Rate Limiters für verschiedene Endpoint-Typen
default_limiter = RateLimiter(max_requests=100, window_seconds=60)
api_limiter = RateLimiter(max_requests=60, window_seconds=60)
sse_limiter = RateLimiter(max_requests=10, window_seconds=60)


def rate_limit(limiter: RateLimiter = default_limiter):
    """
    Decorator für Rate Limiting.

    Usage:
        @app.get("/endpoint")
        @rate_limit(api_limiter)
        async def endpoint():
            ...
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            if not limiter.is_allowed(request):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={"Retry-After": str(int(limiter.get_reset_time(request))), "X-RateLimit-Remaining": "0"},
                )
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


# ==================== Port Policy Enforcement ====================


class PortPolicyEnforcer:
    """Erzwingt PORTIER 3.0 Port-Policy"""

    ALLOWED_RANGE = range(12344, 12400)
    FORBIDDEN_PORTS = [8080]

    @classmethod
    def validate_origin(cls, origin: str) -> bool:
        """
        Validiert Origin gegen Port-Policy.

        Args:
            origin: Origin Header

        Returns:
            True wenn erlaubt
        """
        if not origin:
            return True  # Kein Origin = Server-zu-Server

        try:
            # Parse port aus origin
            if ":" in origin:
                port_str = origin.split(":")[-1]
                if port_str.isdigit():
                    port = int(port_str)
                    return port in cls.ALLOWED_RANGE or port == 8080
        except (ValueError, IndexError):
            pass

        return True  # Standard-Ports erlauben

    @classmethod
    def validate_target_port(cls, port: int) -> bool:
        """
        Validiert Ziel-Port für Dispatching.

        Args:
            port: Ziel-Port

        Returns:
            True wenn erlaubt
        """
        return port in cls.ALLOWED_RANGE and port not in cls.FORBIDDEN_PORTS


# ==================== Request Validation ====================


async def validate_request(request: Request) -> bool:
    """
    Validiert eingehenden Request.

    Args:
        request: FastAPI Request

    Returns:
        True wenn valide

    Raises:
        HTTPException: Wenn Request ungültig
    """
    # Content-Type Prüfung für POST/PUT
    if request.method in ("POST", "PUT", "PATCH"):
        content_type = request.headers.get("content-type", "")
        if content_type and "application/json" not in content_type:
            if "multipart/form-data" not in content_type:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Content-Type muss application/json sein"
                )

    # Origin Policy (optional)
    origin = request.headers.get("origin")
    if origin and not PortPolicyEnforcer.validate_origin(origin):
        logger.warning(f"Origin Policy Violation: {origin}")
        # Nicht blockieren, nur loggen

    return True


# ==================== Security Headers Middleware ====================


class SecurityHeadersMiddleware:
    """Middleware für Security Headers"""

    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Cache-Control": "no-store, max-age=0",
    }

    async def __call__(self, request: Request, call_next):
        response = await call_next(request)

        for header, value in self.SECURITY_HEADERS.items():
            response.headers[header] = value

        return response


# ==================== Audit Logging ====================


def log_security_event(event_type: str, request: Request, details: dict[str, Any] | None = None) -> None:
    """
    Loggt Security-Events.

    Args:
        event_type: Art des Events (auth_success, auth_failure, rate_limit, etc.)
        request: FastAPI Request
        details: Zusätzliche Details
    """
    client_ip = request.client.host if request.client else "unknown"

    log_data = {
        "event_type": event_type,
        "client_ip": client_ip,
        "path": str(request.url.path),
        "method": request.method,
        "timestamp": time.time(),
        "details": mask_secrets(details or {}),
    }

    if event_type in ("auth_failure", "rate_limit", "policy_violation"):
        logger.warning(f"Security Event: {log_data}")
    else:
        logger.info(f"Security Event: {log_data}")


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
    "api_limiter",
    "sse_limiter",
    "rate_limit",
    "PortPolicyEnforcer",
    "validate_request",
    "SecurityHeadersMiddleware",
    "log_security_event",
]
