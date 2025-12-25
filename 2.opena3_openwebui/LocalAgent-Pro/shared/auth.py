#!/usr/bin/env python3
"""
PORTIER 3.0 Authentication Module
Centralized Bearer Token validation and management
v3.0.0 - Production Ready
"""

import hashlib
import json
import os
import time
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

# ============================================================================
# SECTION 1: Bearer Token Configuration
# ============================================================================

# Bearer Token Format: sk_openaX_purpose_v3_mode
# Example: sk_opena1_coordinator_v3_production

VALID_TOKENS = {
    # Core Services
    "sk_opena1_coordinator_v3_production": {"agent": "opena1", "role": "coordinator", "mode": "production", "priority": 10},
    "sk_opena2_archivator_v3_production": {"agent": "opena2", "role": "archivator", "mode": "production", "priority": 10},
    "sk_opena3_gateway_v3_production": {"agent": "opena3", "role": "gateway", "mode": "production", "priority": 10},
    "sk_opena20_dashboard_v3_production": {"agent": "opena20", "role": "dashboard", "mode": "production", "priority": 9},
}

# Generate tokens for compute agents 4-19
for i in range(4, 20):
    token = f"sk_opena{i}_compute_v3_production"
    VALID_TOKENS[token] = {"agent": f"opena{i}", "role": "compute", "mode": "production", "priority": 5}

# Development/Test tokens
VALID_TOKENS.update({
    "sk_test_dev_v3_development": {"agent": "test", "role": "testing", "mode": "development", "priority": 1},
})

# ============================================================================
# SECTION 2: Token Validator Class
# ============================================================================

class TokenValidator:
    """Validates and manages Bearer tokens with advanced features"""

    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            config_dir = str(Path(__file__).parent.parent / "config")

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.token_cache: Dict[str, Dict] = {}
        self.blacklist: List[str] = []
        self.token_metadata: Dict[str, Dict] = {}

        self.load_blacklist()
        self.load_metadata()

    def load_blacklist(self):
        """Load revoked tokens from file"""
        blacklist_file = self.config_dir / "token_blacklist.json"
        if blacklist_file.exists():
            try:
                with open(blacklist_file, 'r') as f:
                    data = json.load(f)
                    self.blacklist = data.get("revoked_tokens", [])
            except Exception as e:
                print(f"⚠️ Failed to load blacklist: {e}")
                self.blacklist = []

    def load_metadata(self):
        """Load token metadata (creation, expiry, etc)"""
        metadata_file = self.config_dir / "token_metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    self.token_metadata = json.load(f)
            except Exception as e:
                print(f"⚠️ Failed to load metadata: {e}")
                self.token_metadata = {}

    def is_valid_token(self, token: str) -> bool:
        """Check if token is valid and not blacklisted"""
        if not token or not isinstance(token, str):
            return False

        # Check blacklist
        if token in self.blacklist:
            return False

        # Check against valid tokens
        if token in VALID_TOKENS:
            return True

        # Validate format: sk_openaX_purpose_v3_mode
        parts = token.split("_")
        if len(parts) != 5:
            return False

        if parts[0] != "sk" or parts[3] != "v3":
            return False

        # Extract agent number
        try:
            agent_part = parts[1]
            if agent_part.startswith("opena"):
                agent_num = int(agent_part[5:])
                if agent_num < 1 or agent_num > 20:
                    return False
        except (ValueError, IndexError):
            return False

        return True

    def get_token_info(self, token: str) -> Optional[Dict]:
        """Get information about a token"""
        return VALID_TOKENS.get(token)

    def validate_and_get_client_id(self, token: str) -> Optional[str]:
        """Validate token and return client ID (agent name)"""
        if not self.is_valid_token(token):
            return None

        info = self.get_token_info(token)
        if info:
            return info.get("agent", "unknown")

        # Extract agent from token format
        parts = token.split("_")
        if len(parts) >= 2:
            return parts[1]

        return None

    def get_token_priority(self, token: str) -> int:
        """Get priority level of token (higher = more privileges)"""
        info = self.get_token_info(token)
        if info:
            return info.get("priority", 0)
        return 0

    def revoke_token(self, token: str) -> bool:
        """Add token to blacklist"""
        if token not in self.blacklist:
            self.blacklist.append(token)
            self._save_blacklist()
            return True
        return False

    def _save_blacklist(self):
        """Save blacklist to file"""
        blacklist_file = self.config_dir / "token_blacklist.json"
        try:
            with open(blacklist_file, 'w') as f:
                json.dump({
                    "revoked_tokens": self.blacklist,
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save blacklist: {e}")

# ============================================================================
# SECTION 3: Rate Limiter Class
# ============================================================================

class RateLimiter:
    """Rate limiting per client with sliding window"""

    def __init__(self, max_requests: int = 1000, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests: Dict[str, List[float]] = {}

    def is_allowed(self, client_id: str) -> bool:
        """Check if client is within rate limit"""
        now = time.time()

        if client_id not in self.requests:
            self.requests[client_id] = []

        # Remove old requests outside window
        self.requests[client_id] = [
            t for t in self.requests[client_id]
            if now - t < self.window
        ]

        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(now)
            return True

        return False

    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client"""
        now = time.time()
        if client_id not in self.requests:
            return self.max_requests

        valid_requests = [
            t for t in self.requests[client_id]
            if now - t < self.window
        ]
        return max(0, self.max_requests - len(valid_requests))

# ============================================================================
# SECTION 4: Audit Logger Class
# ============================================================================

class AuditLogger:
    """Comprehensive authentication and access logging"""

    def __init__(self, log_dir: Optional[str] = None):
        if log_dir is None:
            log_dir = str(Path(__file__).parent.parent / "logs")

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "auth_audit.log"

    def log_access(self, client_id: str, token: str, endpoint: str, status: str,
                   ip: str = "0.0.0.0", method: str = "GET", response_code: int = 200):
        """Log successful authentication event"""
        timestamp = datetime.now().isoformat()
        redacted_token = self._redact_token(token)

        log_entry = {
            "timestamp": timestamp,
            "event_type": "auth_success",
            "client_id": client_id,
            "token": redacted_token,
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "response_code": response_code,
            "ip": ip
        }        self._write_log(log_entry)

    def log_failed_attempt(self, token: str, endpoint: str, reason: str,
                          ip: str = "0.0.0.0", method: str = "GET"):
        """Log failed authentication attempt"""
        timestamp = datetime.now().isoformat()
        redacted_token = self._redact_token(token) if token else "MISSING"

        log_entry = {
            "timestamp": timestamp,
            "event_type": "auth_failed",
            "token": redacted_token,
            "endpoint": endpoint,
            "method": method,
            "status": "failed",
            "reason": reason,
            "ip": ip
        }

        self._write_log(log_entry)

    def log_rate_limit(self, client_id: str, token: str, ip: str = "0.0.0.0"):
        """Log rate limit exceeded"""
        timestamp = datetime.now().isoformat()
        redacted_token = self._redact_token(token)

        log_entry = {
            "timestamp": timestamp,
            "event_type": "rate_limit",
            "client_id": client_id,
            "token": redacted_token,
            "ip": ip
        }

        self._write_log(log_entry)

    def log_token_revocation(self, token: str, reason: str):
        """Log token revocation"""
        timestamp = datetime.now().isoformat()
        redacted_token = self._redact_token(token)

        log_entry = {
            "timestamp": timestamp,
            "event_type": "token_revoked",
            "token": redacted_token,
            "reason": reason
        }

        self._write_log(log_entry)

    @staticmethod
    def _redact_token(token: str) -> str:
        """Redact sensitive token data"""
        if not token or len(token) <= 20:
            return "***REDACTED***"
        return token[:10] + "..." + token[-10:]

    def _write_log(self, log_entry: Dict):
        """Write log entry to file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"⚠️ Failed to write audit log: {e}")

# ============================================================================
# SECTION 5: Utility Functions
# ============================================================================

def extract_bearer_token(auth_header: Optional[str]) -> Optional[str]:
    """Extract Bearer token from Authorization header"""
    if not auth_header or not isinstance(auth_header, str):
        return None

    parts = auth_header.split()
    if len(parts) != 2:
        return None

    if parts[0].lower() != "bearer":
        return None

    return parts[1]

# ============================================================================
# SECTION 6: FastAPI Integration
# ============================================================================

class HTTPException(Exception):
    """HTTP Exception for error responses"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

async def verify_bearer_token(request) -> str:
    """
    FastAPI dependency for Bearer token verification
    Returns client_id on success, raises HTTPException on failure
    """
    auth_header = request.headers.get("Authorization")
    token = extract_bearer_token(auth_header)

    if not token:
        audit_logger.log_failed_attempt("", str(request.url), "missing_token",
                                       request.client.host if request.client else "unknown")
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    if not token_validator.is_valid_token(token):
        audit_logger.log_failed_attempt(token, str(request.url), "invalid_token",
                                       request.client.host if request.client else "unknown")
        raise HTTPException(status_code=403, detail="Invalid Bearer token")

    client_id = token_validator.validate_and_get_client_id(token)
    if not client_id:
        audit_logger.log_failed_attempt(token, str(request.url), "unknown_client",
                                       request.client.host if request.client else "unknown")
        raise HTTPException(status_code=403, detail="Unknown client")

    if not rate_limiter.is_allowed(client_id):
        audit_logger.log_rate_limit(client_id, token,
                                   request.client.host if request.client else "unknown")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    audit_logger.log_access(client_id, token, str(request.url), "success",
                           request.client.host if request.client else "unknown")

    return client_id

def verify_bearer_token_simple(auth_header: Optional[str]) -> Optional[str]:
    """
    Simple synchronous token verification (for http.server)
    Returns client_id on success, None on failure
    """
    if not auth_header:
        return None

    token = extract_bearer_token(auth_header)
    if not token or not token_validator.is_valid_token(token):
        return None

    return token_validator.validate_and_get_client_id(token)

# ============================================================================
# SECTION 7: Global Instances
# ============================================================================

token_validator = TokenValidator()
rate_limiter = RateLimiter(max_requests=1000, window=60)
audit_logger = AuditLogger()

# ============================================================================
# SECTION 8: Exports
# ============================================================================

__all__ = [
    "TokenValidator",
    "RateLimiter",
    "AuditLogger",
    "extract_bearer_token",
    "verify_bearer_token",
    "verify_bearer_token_simple",
    "token_validator",
    "rate_limiter",
    "audit_logger",
    "VALID_TOKENS",
    "HTTPException"
]
