"""
JWT Authentication Module for ELION OpenWebUI Integration

Provides secure JWT token generation, validation, and management
for inter-agent communication and OpenWebUI integration.

SECURITY-CRITICAL:
  - RS256 (RSA) signing - asymmetric encryption
  - Private keys loaded from secure sources ONLY:
    * Environment variables (JWT_PRIVATE_KEY / JWT_PUBLIC_KEY)
    * PEM files on disk (JWT_PRIVATE_KEY_PATH / JWT_PUBLIC_KEY_PATH)
    * NEVER hardcoded in source code
  - Standard JWT claims: iss, sub, aud, iat, exp, nbf
  - Additional claims: agent_id, scope, permissions
  
Features:
  - RS256 (RSA) signing with secure key management
  - Configurable token expiration (default: 24 hours)
  - Agent-specific claims (agent_id, scope, permissions)
  - Token refresh/rotation mechanism
  - Signature verification with error handling
  - Pydantic-based token models with validation

Usage:
  >>> from jwt_auth import create_token, verify_token
  >>> token = create_token(agent_id="opena1", scope="invoke")
  >>> payload = verify_token(token)
  >>> print(payload.get("agent_id"))  # "opena1"

Key Loading Priority:
  1. Environment variables (JWT_PRIVATE_KEY / JWT_PUBLIC_KEY)
  2. File paths from env (JWT_PRIVATE_KEY_PATH / JWT_PUBLIC_KEY_PATH)
  3. Default paths (./secrets/jwt_private.pem, ./secrets/jwt_public.pem)
  4. Raise error if no keys found

Deployment:
  - Production: Use GitHub Secrets or Vault
  - Development: Use .env file (gitignored)
  - Testing: Use test keys in CI/CD only
"""

import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import jwt
from pydantic import BaseModel, Field, validator


# ============================================================================
# Configuration
# ============================================================================

class JWTConfig:
    """JWT Configuration Constants"""
    
    # Algorithm (RS256 = RSA Signature with SHA-256)
    ALGORITHM = "RS256"
    
    # Default token expiration: 24 hours
    TOKEN_EXPIRATION_HOURS = 24
    
    # Refresh threshold: token can be refreshed if < 1 hour left
    REFRESH_THRESHOLD_HOURS = 1
    
    # Issuer (who creates the token)
    ISSUER = "elion-dashboard"
    
    # Audience (intended recipients)
    AUDIENCE = "elion-agents"
    
    # Key storage locations
    PRIVATE_KEY_ENV = "JWT_PRIVATE_KEY"
    PUBLIC_KEY_ENV = "JWT_PUBLIC_KEY"
    
    # Key file paths (fallback if not in .env)
    PRIVATE_KEY_FILE = "secrets/jwt_private.pem"
    PUBLIC_KEY_FILE = "secrets/jwt_public.pem"


# ============================================================================
# Pydantic Models (Data Validation)
# ============================================================================

class TokenClaims(BaseModel):
    """JWT Token Claims (Payload)"""
    
    # Standard JWT claims
    iss: str = Field(default=JWTConfig.ISSUER, description="Issuer")
    sub: str = Field(..., description="Subject (agent_id)")
    aud: str = Field(default=JWTConfig.AUDIENCE, description="Audience")
    iat: int = Field(..., description="Issued at (Unix timestamp)")
    exp: int = Field(..., description="Expiration (Unix timestamp)")
    nbf: int = Field(..., description="Not before (Unix timestamp)")
    jti: str = Field(..., description="JWT ID (unique identifier)")
    
    # Custom claims
    agent_id: str = Field(..., description="Agent ID (opena1, opena2, etc.)")
    scope: str = Field(default="default", description="Token scope (invoke, read, admin)")
    permissions: List[str] = Field(
        default_factory=list,
        description="Additional permissions"
    )
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "iss": "elion-dashboard",
                "sub": "opena1",
                "aud": "elion-agents",
                "iat": 1699512345,
                "exp": 1699598745,
                "nbf": 1699512345,
                "jti": "abc123def456",
                "agent_id": "opena1",
                "scope": "invoke",
                "permissions": ["read", "write"]
            }
        }


class TokenResponse(BaseModel):
    """Token Response Model"""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Expires in seconds")
    scope: str = Field(..., description="Token scope")
    agent_id: str = Field(..., description="Agent ID")


class TokenRefreshRequest(BaseModel):
    """Token Refresh Request"""
    
    token: str = Field(..., description="Current token to refresh")
    agent_id: str = Field(..., description="Agent ID")


class TokenValidationResult(BaseModel):
    """Token Validation Result"""
    
    valid: bool = Field(..., description="Is token valid?")
    claims: Optional[TokenClaims] = Field(None, description="Token claims if valid")
    error: Optional[str] = Field(None, description="Error message if invalid")
    error_type: Optional[str] = Field(None, description="Error type")


# ============================================================================
# Secure Key Management
# ============================================================================

class SecureKeyManager:
    """
    Manages RSA key loading from secure sources.
    
    Priority order:
    1. Environment variables (JWT_PRIVATE_KEY / JWT_PUBLIC_KEY)
    2. File paths from environment (JWT_PRIVATE_KEY_PATH / JWT_PUBLIC_KEY_PATH)
    3. Default file paths (./secrets/jwt_*.pem)
    4. Raise error if not found
    
    NEVER uses hardcoded keys or generates keys at runtime in production.
    """
    
    # Default paths (should be gitignored)
    DEFAULT_PRIVATE_KEY_FILE = "secrets/jwt_private.pem"
    DEFAULT_PUBLIC_KEY_FILE = "secrets/jwt_public.pem"
    
    # Environment variable names
    ENV_PRIVATE_KEY = "JWT_PRIVATE_KEY"
    ENV_PUBLIC_KEY = "JWT_PUBLIC_KEY"
    ENV_PRIVATE_KEY_PATH = "JWT_PRIVATE_KEY_PATH"
    ENV_PUBLIC_KEY_PATH = "JWT_PUBLIC_KEY_PATH"
    
    @staticmethod
    def load_private_key() -> str:
        """
        Load private key from secure source.
        
        Returns:
            str: Private key PEM content
            
        Raises:
            RuntimeError: If key cannot be loaded
        """
        # 1. Try environment variable (highest priority)
        if os.getenv(SecureKeyManager.ENV_PRIVATE_KEY):
            key = os.getenv(SecureKeyManager.ENV_PRIVATE_KEY)
            if key and len(key) > 100:  # Basic sanity check
                return key
        
        # 2. Try file path from environment
        file_path = os.getenv(SecureKeyManager.ENV_PRIVATE_KEY_PATH)
        if file_path and Path(file_path).exists():
            try:
                return Path(file_path).read_text()
            except Exception as e:
                raise RuntimeError(f"Failed to read private key from {file_path}: {e}")
        
        # 3. Try default path
        if Path(SecureKeyManager.DEFAULT_PRIVATE_KEY_FILE).exists():
            try:
                return Path(SecureKeyManager.DEFAULT_PRIVATE_KEY_FILE).read_text()
            except Exception as e:
                raise RuntimeError(f"Failed to read default private key: {e}")
        
        # 4. Not found - raise error
        raise RuntimeError(
            f"No private RSA key found. Set one of:\n"
            f"  - {SecureKeyManager.ENV_PRIVATE_KEY} (environment variable with key content)\n"
            f"  - {SecureKeyManager.ENV_PRIVATE_KEY_PATH} (environment variable with file path)\n"
            f"  - {SecureKeyManager.DEFAULT_PRIVATE_KEY_FILE} (default file path)"
        )
    
    @staticmethod
    def load_public_key() -> str:
        """
        Load public key from secure source.
        
        Returns:
            str: Public key PEM content
            
        Raises:
            RuntimeError: If key cannot be loaded
        """
        # 1. Try environment variable
        if os.getenv(SecureKeyManager.ENV_PUBLIC_KEY):
            key = os.getenv(SecureKeyManager.ENV_PUBLIC_KEY)
            if key and len(key) > 50:  # Basic sanity check
                return key
        
        # 2. Try file path from environment
        file_path = os.getenv(SecureKeyManager.ENV_PUBLIC_KEY_PATH)
        if file_path and Path(file_path).exists():
            try:
                return Path(file_path).read_text()
            except Exception as e:
                raise RuntimeError(f"Failed to read public key from {file_path}: {e}")
        
        # 3. Try default path
        if Path(SecureKeyManager.DEFAULT_PUBLIC_KEY_FILE).exists():
            try:
                return Path(SecureKeyManager.DEFAULT_PUBLIC_KEY_FILE).read_text()
            except Exception as e:
                raise RuntimeError(f"Failed to read default public key: {e}")
        
        # 4. Not found - raise error
        raise RuntimeError(
            f"No public RSA key found. Set one of:\n"
            f"  - {SecureKeyManager.ENV_PUBLIC_KEY} (environment variable with key content)\n"
            f"  - {SecureKeyManager.ENV_PUBLIC_KEY_PATH} (environment variable with file path)\n"
            f"  - {SecureKeyManager.DEFAULT_PUBLIC_KEY_FILE} (default file path)"
        )
    
    @staticmethod
    def verify_keys_available() -> Tuple[bool, str]:
        """
        Verify both keys are available without loading them.
        
        Returns:
            Tuple[bool, str]: (keys_available, error_message)
        """
        try:
            SecureKeyManager.load_private_key()
            SecureKeyManager.load_public_key()
            return True, "Both keys available"
        except RuntimeError as e:
            return False, str(e)


# ============================================================================
# Token Generation & Validation
# ============================================================================

def create_token(
    agent_id: str,
    scope: str = "default",
    permissions: Optional[List[str]] = None,
    expires_in_hours: int = JWTConfig.TOKEN_EXPIRATION_HOURS
) -> str:
    """
    Create a signed JWT token for an agent.
    
    Args:
        agent_id: Agent identifier (e.g., "opena1")
        scope: Token scope ("invoke", "read", "admin", etc.)
        permissions: List of additional permissions
        expires_in_hours: Token expiration in hours
    
    Returns:
        str: Signed JWT token
    
    Raises:
        ValueError: If private key cannot be loaded
    """
    try:
        private_key = RSAKeyManager.load_private_key()
    except Exception as e:
        raise ValueError(f"Failed to load private key: {str(e)}")
    
    # Create timestamps
    now = datetime.now(timezone.utc)
    iat_timestamp = int(now.timestamp())
    exp_timestamp = int((now + timedelta(hours=expires_in_hours)).timestamp())
    
    # Create claims
    claims = TokenClaims(
        iss=JWTConfig.ISSUER,
        sub=agent_id,
        aud=JWTConfig.AUDIENCE,
        iat=iat_timestamp,
        exp=exp_timestamp,
        nbf=iat_timestamp,
        jti=secrets.token_hex(16),  # Unique token ID
        agent_id=agent_id,
        scope=scope,
        permissions=permissions or []
    )
    
    # Encode token
    token = jwt.encode(
        claims.dict(),
        private_key,
        algorithm=JWTConfig.ALGORITHM
    )
    
    return token


def verify_token(token: str) -> TokenValidationResult:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        TokenValidationResult: Validation result with claims or error
    """
    try:
        public_key = RSAKeyManager.load_public_key()
    except Exception as e:
        return TokenValidationResult(
            valid=False,
            error=str(e),
            error_type="KEY_LOAD_ERROR"
        )
    
    try:
        # Decode and verify
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[JWTConfig.ALGORITHM],
            audience=JWTConfig.AUDIENCE,
            issuer=JWTConfig.ISSUER
        )
        
        # Convert to TokenClaims model
        claims = TokenClaims(**payload)
        
        return TokenValidationResult(
            valid=True,
            claims=claims
        )
    
    except jwt.ExpiredSignatureError:
        return TokenValidationResult(
            valid=False,
            error="Token has expired",
            error_type="EXPIRED"
        )
    
    except jwt.InvalidSignatureError:
        return TokenValidationResult(
            valid=False,
            error="Token signature is invalid",
            error_type="INVALID_SIGNATURE"
        )
    
    except jwt.InvalidAudienceError:
        return TokenValidationResult(
            valid=False,
            error="Token audience is invalid",
            error_type="INVALID_AUDIENCE"
        )
    
    except jwt.InvalidIssuerError:
        return TokenValidationResult(
            valid=False,
            error="Token issuer is invalid",
            error_type="INVALID_ISSUER"
        )
    
    except jwt.DecodeError as e:
        return TokenValidationResult(
            valid=False,
            error=f"Token decode error: {str(e)}",
            error_type="DECODE_ERROR"
        )
    
    except Exception as e:
        return TokenValidationResult(
            valid=False,
            error=str(e),
            error_type="UNKNOWN_ERROR"
        )


def refresh_token(token: str, agent_id: str) -> Optional[str]:
    """
    Refresh a token if it's close to expiration.
    
    Args:
        token: Current token
        agent_id: Agent ID
    
    Returns:
        Optional[str]: New token if refreshed, None if not needed/invalid
    """
    result = verify_token(token)
    
    if not result.valid:
        return None
    
    claims = result.claims
    
    # Check if token can be refreshed
    now = int(datetime.now(timezone.utc).timestamp())
    time_until_expiry = claims.exp - now
    refresh_threshold_seconds = JWTConfig.REFRESH_THRESHOLD_HOURS * 3600
    
    if time_until_expiry > refresh_threshold_seconds:
        # Token still has enough time, don't refresh
        return None
    
    # Create new token with same scope and permissions
    return create_token(
        agent_id=agent_id,
        scope=claims.scope,
        permissions=claims.permissions
    )


# ============================================================================
# FastAPI Integration Helpers
# ============================================================================

async def verify_token_from_header(authorization_header: str) -> TokenValidationResult:
    """
    Verify token from Authorization header (Bearer scheme).
    
    Args:
        authorization_header: "Bearer <token>"
    
    Returns:
        TokenValidationResult: Validation result
    """
    if not authorization_header:
        return TokenValidationResult(
            valid=False,
            error="Missing Authorization header",
            error_type="MISSING_HEADER"
        )
    
    parts = authorization_header.split()
    
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return TokenValidationResult(
            valid=False,
            error="Invalid Authorization header format. Expected 'Bearer <token>'",
            error_type="INVALID_FORMAT"
        )
    
    token = parts[1]
    return verify_token(token)


# ============================================================================
# Testing & Demo
# ============================================================================

async def demo():
    """Demo JWT token creation, verification, and refresh."""
    print("\n" + "=" * 70)
    print("🔐 JWT Authentication System - Demo")
    print("=" * 70)
    
    # 1. Create token
    print("\n1️⃣  Creating token for opena1...")
    token = create_token(
        agent_id="opena1",
        scope="invoke",
        permissions=["read", "write"]
    )
    print(f"   Token: {token[:50]}...")
    print(f"   Length: {len(token)} chars")
    
    # 2. Verify token
    print("\n2️⃣  Verifying token...")
    result = verify_token(token)
    if result.valid:
        print(f"   ✅ Valid token")
        print(f"   Agent: {result.claims.agent_id}")
        print(f"   Scope: {result.claims.scope}")
        print(f"   Permissions: {result.claims.permissions}")
        print(f"   Expires: {datetime.fromtimestamp(result.claims.exp)}")
    else:
        print(f"   ❌ Invalid: {result.error}")
    
    # 3. Verify from header
    print("\n3️⃣  Verifying from Authorization header...")
    header_result = await verify_token_from_header(f"Bearer {token}")
    print(f"   Valid: {header_result.valid}")
    
    # 4. Create multiple tokens
    print("\n4️⃣  Creating tokens for multiple agents...")
    agents = ["opena1", "opena2", "kordp", "opena4"]
    tokens = {}
    for agent_id in agents:
        tokens[agent_id] = create_token(agent_id=agent_id, scope="invoke")
        print(f"   ✅ {agent_id}: {tokens[agent_id][:40]}...")
    
    # 5. Verify each token
    print("\n5️⃣  Verifying all tokens...")
    for agent_id, token in tokens.items():
        result = verify_token(token)
        status = "✅" if result.valid else "❌"
        print(f"   {status} {agent_id}")
    
    # 6. Test expired token
    print("\n6️⃣  Testing expired token simulation...")
    expired_token = create_token(agent_id="opena1", expires_in_hours=-1)
    expired_result = verify_token(expired_token)
    print(f"   Error: {expired_result.error_type}")
    
    print("\n" + "=" * 70)
    print("✅ Demo complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())
