#!/usr/bin/env python3
"""
opena4 - Security Module

Port: 12346
Kürzel: telep

PORTIER 3.0 Security Layer
"""

import logging
import os
import time
from collections import defaultdict
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

logger = logging.getLogger(__name__)

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
    if isinstance(data, dict):
        return {
            k: mask_value if any(secret in k.lower() for secret in SECRET_KEYS) else mask_secrets(v, mask_value)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [mask_secrets(item, mask_value) for item in data]
    return data


security = HTTPBearer(auto_error=False)


async def verify_token(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> str:
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Bearer Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials


async def optional_verify_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str | None:
    if not credentials:
        return None
    if credentials.credentials == BEARER_TOKEN:
        return credentials.credentials
    return None


class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list] = defaultdict(list)

    def _clean_old_requests(self, client_id: str) -> None:
        cutoff = time.time() - self.window_seconds
        self._requests[client_id] = [ts for ts in self._requests[client_id] if ts > cutoff]

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


default_limiter = RateLimiter(max_requests=100, window_seconds=60)
api_limiter = RateLimiter(max_requests=60, window_seconds=60)


class PortPolicyEnforcer:
    ALLOWED_RANGE = range(12344, 12400)
    FORBIDDEN_PORTS = [8080]

    @classmethod
    def validate_origin(cls, origin: str) -> bool:
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
    "PortPolicyEnforcer",
]
