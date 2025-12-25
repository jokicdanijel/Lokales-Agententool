#!/usr/bin/env python3
"""
opena17 - Homepage Creator Agent
Security Module - PORTIER 3.0 Compliant

Bearer Token Validation, Rate Limiting, CORS
"""

import functools
import hashlib
import os
import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from fastapi import Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

# ================== BEARER TOKEN ==================

BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")


async def verify_bearer_token(authorization: str | None = Header(None)) -> str:
    """Bearer Token Validierung nach PORTIER 3.0"""
    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "MISSING_AUTH",
                    "message": "Authorization header fehlt",
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            },
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "INVALID_SCHEME",
                    "message": "Invalid authentication scheme - Bearer erwartet",
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            },
        )

    if token != BEARER_TOKEN:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "Ungültiger Bearer Token",
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            },
        )

    return token


# ================== PORT POLICY MIDDLEWARE ==================


class PortPolicyMiddleware:
    """Middleware für Port-Policy Enforcement (12344-12399)"""

    ALLOWED_PORTS = range(12344, 12400)
    FORBIDDEN_PORTS = [8080]

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Port-Check aus Server-Headers (falls verfügbar)
            server_port = scope.get("server", [None, None])[1]

            if server_port and server_port not in self.ALLOWED_PORTS:
                # Rejecting non-compliant ports
                response = {
                    "error": {
                        "code": "PORT_POLICY_VIOLATION",
                        "message": f"Port {server_port} ist nicht erlaubt",
                        "allowed_range": "12344-12399",
                    }
                }
                # Send error response
                await send(
                    {
                        "type": "http.response.start",
                        "status": 403,
                        "headers": [[b"content-type", b"application/json"]],
                    }
                )
                import json

                await send(
                    {
                        "type": "http.response.body",
                        "body": json.dumps(response).encode(),
                    }
                )
                return

        await self.app(scope, receive, send)


# ================== RATE LIMITER ==================


class RateLimiter:
    """Simple In-Memory Rate Limiter"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list] = {}

    def _get_client_id(self, request: Request) -> str:
        """Ermittelt Client-ID (IP + Token Hash)"""
        client_ip = request.client.host if request.client else "unknown"
        auth = request.headers.get("authorization", "")
        return hashlib.md5(f"{client_ip}:{auth}".encode()).hexdigest()[:16]

    def _cleanup_old_requests(self, client_id: str) -> None:
        """Entfernt alte Requests außerhalb des Fensters"""
        if client_id not in self.requests:
            return

        cutoff = time.time() - self.window_seconds
        self.requests[client_id] = [ts for ts in self.requests[client_id] if ts > cutoff]

    def is_allowed(self, request: Request) -> bool:
        """Prüft ob Request erlaubt ist"""
        client_id = self._get_client_id(request)
        self._cleanup_old_requests(client_id)

        if client_id not in self.requests:
            self.requests[client_id] = []

        if len(self.requests[client_id]) >= self.max_requests:
            return False

        self.requests[client_id].append(time.time())
        return True

    def get_remaining(self, request: Request) -> int:
        """Gibt verbleibende Requests zurück"""
        client_id = self._get_client_id(request)
        self._cleanup_old_requests(client_id)

        current = len(self.requests.get(client_id, []))
        return max(0, self.max_requests - current)


# Rate Limiter Instanzen
rate_limiter_default = RateLimiter(max_requests=100, window_seconds=60)
rate_limiter_generate = RateLimiter(max_requests=10, window_seconds=60)
rate_limiter_export = RateLimiter(max_requests=5, window_seconds=60)


def rate_limit(limiter: RateLimiter = rate_limiter_default):
    """Decorator für Rate Limiting"""

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            if not limiter.is_allowed(request):
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": "Zu viele Anfragen - bitte warten",
                            "retry_after_seconds": 60,
                            "timestamp": datetime.now(UTC).isoformat(),
                        }
                    },
                )
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


# ================== CORS CONFIG ==================

CORS_CONFIG = {
    "allow_origins": [
        "http://127.0.0.1:12349",  # Dashboard
        "http://127.0.0.1:12344",  # Portier
        "http://localhost:12349",
        "http://localhost:12344",
    ],
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["*"],
    "expose_headers": ["X-Request-ID", "X-RateLimit-Remaining"],
}


def setup_cors(app):
    """Konfiguriert CORS für App"""
    app.add_middleware(CORSMiddleware, **CORS_CONFIG)


# ================== SECRET MASKING ==================

SECRET_KEYS = {"token", "auth", "password", "apikey", "key", "secret", "credentials", "bearer"}


def mask_secrets(data: Any, depth: int = 0) -> Any:
    """Maskiert Secrets in Datenstrukturen (für Logging)"""
    if depth > 10:  # Prevent infinite recursion
        return data

    if isinstance(data, dict):
        return {
            k: "***MASKED***" if any(s in k.lower() for s in SECRET_KEYS) else mask_secrets(v, depth + 1)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [mask_secrets(item, depth + 1) for item in data]
    return data


# ================== REQUEST VALIDATION ==================


class RequestValidator:
    """Validiert eingehende Requests"""

    MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MB
    ALLOWED_CONTENT_TYPES = ["application/json", "multipart/form-data"]

    @classmethod
    async def validate_request(cls, request: Request) -> None:
        """Validiert Request-Parameter"""
        # Content-Length Check
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > cls.MAX_BODY_SIZE:
            raise HTTPException(
                status_code=413,
                detail={
                    "error": {
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": f"Request zu groß (max {cls.MAX_BODY_SIZE} bytes)",
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                },
            )

        # Content-Type Check (für POST/PUT)
        if request.method in ["POST", "PUT"]:
            content_type = request.headers.get("content-type", "")
            if not any(ct in content_type for ct in cls.ALLOWED_CONTENT_TYPES):
                raise HTTPException(
                    status_code=415,
                    detail={
                        "error": {
                            "code": "UNSUPPORTED_MEDIA_TYPE",
                            "message": "Content-Type nicht unterstützt",
                            "allowed": cls.ALLOWED_CONTENT_TYPES,
                            "timestamp": datetime.now(UTC).isoformat(),
                        }
                    },
                )
