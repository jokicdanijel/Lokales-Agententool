#!/usr/bin/env python3
"""
opena18 - CRM Agent
Security Module - PORTIER 3.0 Compliant

Bearer Token Validation, Rate Limiting, GDPR Compliance
"""

import os
import time
import hashlib
import functools
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timezone

from fastapi import HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict

# ================== BEARER TOKEN ==================

BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")


async def verify_bearer_token(authorization: Optional[str] = Header(None)) -> str:
    """Bearer Token Validierung nach PORTIER 3.0"""
    if authorization is None:
        raise HTTPException(
            status_code=401, 
            detail={
                "error": {
                    "code": "MISSING_AUTH",
                    "message": "Authorization header fehlt",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        )
    
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "INVALID_SCHEME",
                    "message": "Invalid authentication scheme - Bearer erwartet",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        )
    
    if token != BEARER_TOKEN:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "Ungültiger Bearer Token",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        )
    
    return token


# ================== RATE LIMITER ==================

class RateLimiter:
    """Simple In-Memory Rate Limiter"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}
    
    def _get_client_id(self, request: Request) -> str:
        """Ermittelt Client-ID"""
        client_ip = request.client.host if request.client else "unknown"
        auth = request.headers.get("authorization", "")
        return hashlib.md5(f"{client_ip}:{auth}".encode()).hexdigest()[:16]
    
    def _cleanup_old_requests(self, client_id: str) -> None:
        """Entfernt alte Requests"""
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


# Rate Limiter Instanzen
rate_limiter_default = RateLimiter(max_requests=100, window_seconds=60)
rate_limiter_write = RateLimiter(max_requests=30, window_seconds=60)
rate_limiter_export = RateLimiter(max_requests=5, window_seconds=60)


# ================== SECRET MASKING ==================

SECRET_KEYS = {"token", "auth", "password", "apikey", "key", "secret", "credentials", "bearer", "ssn", "tax_id"}


def mask_secrets(data: Any, depth: int = 0) -> Any:
    """Maskiert Secrets in Datenstrukturen"""
    if depth > 10:
        return data
    
    if isinstance(data, dict):
        return {
            k: "***MASKED***" if any(s in k.lower() for s in SECRET_KEYS)
            else mask_secrets(v, depth + 1)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [mask_secrets(item, depth + 1) for item in data]
    return data


# ================== GDPR COMPLIANCE ==================

class GDPRComplianceManager:
    """GDPR Compliance Manager für CRM"""
    
    def __init__(self):
        self.consent_registry: Dict[str, Dict[str, Any]] = {}
        self.deletion_requests: Dict[str, Dict[str, Any]] = {}
    
    def record_consent(
        self, 
        contact_id: str, 
        consent_type: str, 
        granted: bool,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Zeichnet Consent auf"""
        consent = {
            "contact_id": contact_id,
            "consent_type": consent_type,
            "granted": granted,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ip_address": ip_address or "unknown"
        }
        
        if contact_id not in self.consent_registry:
            self.consent_registry[contact_id] = {}
        
        self.consent_registry[contact_id][consent_type] = consent
        return consent
    
    def check_consent(self, contact_id: str, consent_type: str) -> bool:
        """Prüft Consent"""
        if contact_id not in self.consent_registry:
            return False
        return self.consent_registry[contact_id].get(consent_type, {}).get("granted", False)
    
    def request_deletion(self, contact_id: str, reason: str = "") -> Dict[str, Any]:
        """Registriert Löschantrag (GDPR Art. 17)"""
        request = {
            "contact_id": contact_id,
            "reason": reason,
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
            "processed_at": None
        }
        self.deletion_requests[contact_id] = request
        return request
    
    def export_contact_data(self, contact_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Exportiert Kontaktdaten (GDPR Art. 20)"""
        return {
            "export_id": hashlib.md5(f"{contact_id}{time.time()}".encode()).hexdigest()[:12],
            "contact_id": contact_id,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "data": data,
            "format": "json"
        }
    
    def anonymize_contact(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymisiert Kontaktdaten"""
        anonymized = contact.copy()
        anonymized["first_name"] = "ANONYMIZED"
        anonymized["last_name"] = "ANONYMIZED"
        anonymized["email"] = f"anon-{contact.get('contact_id', 'unknown')}@deleted.local"
        anonymized["phone"] = "ANONYMIZED"
        anonymized["notes"] = None
        anonymized["anonymized_at"] = datetime.now(timezone.utc).isoformat()
        return anonymized


# Singleton GDPR Manager
gdpr_manager = GDPRComplianceManager()


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
