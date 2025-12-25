#!/usr/bin/env python3
"""
opena19 - Stocks & Crypto Agent
Security Module - PORTIER 3.0 Compliant

Bearer Token Validation, Rate Limiting, API Key Management
"""

import hashlib
import os
import time
from datetime import UTC, datetime
from typing import Any

from fastapi import Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# ================== BEARER TOKEN ==================

BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials) -> str:
    """Verifiziert Bearer Token"""
    if credentials.credentials != BEARER_TOKEN:
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
    return credentials.credentials


async def verify_bearer_token(authorization: str | None = Header(None)) -> str:
    """Bearer Token Validierung (Header-basiert)"""
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header fehlt")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Ungültiger Token")

    return token


# ================== RATE LIMITER ==================


class RateLimiter:
    """Rate Limiter für API Calls"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list] = {}

    def _get_client_id(self, request: Request) -> str:
        """Ermittelt Client-ID"""
        client_ip = request.client.host if request.client else "unknown"
        return hashlib.md5(client_ip.encode()).hexdigest()[:16]

    def is_allowed(self, request: Request) -> bool:
        """Prüft ob Request erlaubt ist"""
        client_id = self._get_client_id(request)
        now = time.time()
        cutoff = now - self.window_seconds

        if client_id not in self.requests:
            self.requests[client_id] = []

        self.requests[client_id] = [ts for ts in self.requests[client_id] if ts > cutoff]

        if len(self.requests[client_id]) >= self.max_requests:
            return False

        self.requests[client_id].append(now)
        return True


# Rate Limiter Instanzen
rate_limiter_default = RateLimiter(max_requests=100, window_seconds=60)
rate_limiter_prices = RateLimiter(max_requests=30, window_seconds=60)
rate_limiter_alerts = RateLimiter(max_requests=10, window_seconds=60)


# ================== SECRET MASKING ==================

SECRET_KEYS = {"token", "auth", "password", "apikey", "key", "secret", "credentials", "api_key"}


def mask_secrets(data: Any, depth: int = 0) -> Any:
    """Maskiert Secrets in Datenstrukturen"""
    if depth > 10:
        return data

    if isinstance(data, dict):
        return {
            k: "***MASKED***" if any(s in k.lower() for s in SECRET_KEYS) else mask_secrets(v, depth + 1)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [mask_secrets(item, depth + 1) for item in data]
    return data


# ================== API KEY MANAGER ==================


class APIKeyManager:
    """Verwaltet externe API Keys (Alpha Vantage, CoinGecko)"""

    def __init__(self):
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_KEY", "demo")
        self.coingecko_key = os.getenv("COINGECKO_API_KEY", "")
        self._api_call_counts: dict[str, int] = {}
        self._last_reset: float = time.time()

    def get_alpha_vantage_key(self) -> str:
        """Alpha Vantage API Key (mit Rate Limit Tracking)"""
        self._track_call("alpha_vantage")
        return self.alpha_vantage_key

    def get_coingecko_key(self) -> str | None:
        """CoinGecko API Key (optional, public API verfügbar)"""
        self._track_call("coingecko")
        return self.coingecko_key if self.coingecko_key else None

    def _track_call(self, api_name: str) -> None:
        """Trackt API Calls"""
        now = time.time()
        # Reset nach 24h
        if now - self._last_reset > 86400:
            self._api_call_counts = {}
            self._last_reset = now

        if api_name not in self._api_call_counts:
            self._api_call_counts[api_name] = 0
        self._api_call_counts[api_name] += 1

    def get_usage_stats(self) -> dict[str, int]:
        """Gibt API Usage Statistiken zurück"""
        return self._api_call_counts.copy()

    def check_rate_limit(self, api_name: str) -> bool:
        """Prüft ob API Rate Limit erreicht"""
        limits = {"alpha_vantage": 5, "coingecko": 50}  # 5 calls/min for free tier  # 50 calls/min for free tier
        # Simplified check
        return self._api_call_counts.get(api_name, 0) < limits.get(api_name, 100)


# Singleton API Key Manager
api_key_manager = APIKeyManager()


# ================== CORS CONFIG ==================

CORS_CONFIG = {
    "allow_origins": [
        "http://127.0.0.1:12349",
        "http://127.0.0.1:12344",
        "http://localhost:12349",
        "http://localhost:12344",
    ],
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["*"],
}


def setup_cors(app):
    """Konfiguriert CORS für App"""
    app.add_middleware(CORSMiddleware, **CORS_CONFIG)
