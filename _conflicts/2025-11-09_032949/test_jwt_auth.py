"""
JWT Authentication Tests

Unit tests for JWT token generation, verification, and validation.
Tests for RS256 signing, token claims, expiration, and error handling.
"""

import json
import time
import pytest
from datetime import datetime, timedelta, timezone
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jwt_auth import (
    create_token,
    verify_token,
    refresh_token,
    TokenClaims,
    TokenValidationResult,
    JWTConfig,
    RSAKeyManager
)


class TestTokenGeneration:
    """Token generation tests"""
    
    def test_create_token(self):
        """Test basic token creation"""
        token = create_token(agent_id="opena1", scope="invoke")
        assert isinstance(token, str)
        assert len(token) > 0
        print(f"✅ Token created: {token[:50]}...")
    
    def test_create_token_with_permissions(self):
        """Test token creation with permissions"""
        token = create_token(
            agent_id="opena2",
            scope="admin",
            permissions=["read", "write", "delete"]
        )
        assert isinstance(token, str)
        result = verify_token(token)
        assert result.valid
        assert result.claims.permissions == ["read", "write", "delete"]
        print("✅ Token with permissions created and verified")
    
    def test_create_multiple_tokens(self):
        """Test creating tokens for multiple agents"""
        agents = ["opena1", "opena2", "kordp", "opena4"]
        tokens = {}
        
        for agent_id in agents:
            token = create_token(agent_id=agent_id, scope="invoke")
            tokens[agent_id] = token
            assert isinstance(token, str)
        
        assert len(tokens) == len(agents)
        print(f"✅ {len(tokens)} tokens created successfully")


class TestTokenVerification:
    """Token verification tests"""
    
    def test_verify_valid_token(self):
        """Test verification of valid token"""
        token = create_token(agent_id="opena1", scope="invoke")
        result = verify_token(token)
        
        assert result.valid
        assert result.claims is not None
        assert result.claims.agent_id == "opena1"
        assert result.claims.scope == "invoke"
        print("✅ Valid token verified successfully")
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token"""
        result = verify_token("invalid.token.here")
        assert not result.valid
        assert result.error is not None
        print(f"✅ Invalid token rejected: {result.error_type}")
    
    def test_verify_token_claims(self):
        """Test that token contains correct claims"""
        token = create_token(
            agent_id="opena2",
            scope="admin",
            permissions=["read", "write"]
        )
        result = verify_token(token)
        
        assert result.valid
        claims = result.claims
        assert claims.agent_id == "opena2"
        assert claims.scope == "admin"
        assert claims.permissions == ["read", "write"]
        assert claims.iss == JWTConfig.ISSUER
        assert claims.aud == JWTConfig.AUDIENCE
        print("✅ Token claims verified")
    
    def test_verify_expired_token(self):
        """Test verification of expired token"""
        token = create_token(agent_id="opena1", expires_in_hours=-1)
        result = verify_token(token)
        
        assert not result.valid
        assert result.error_type == "EXPIRED"
        print(f"✅ Expired token detected: {result.error_type}")


class TestTokenRefresh:
    """Token refresh tests"""
    
    def test_refresh_token_not_needed(self):
        """Test that fresh token doesn't get refreshed"""
        token = create_token(agent_id="opena1", expires_in_hours=24)
        new_token = refresh_token(token, agent_id="opena1")
        
        # Fresh token should not be refreshed
        assert new_token is None
        print("✅ Fresh token not refreshed (correct behavior)")
    
    def test_refresh_token_invalid(self):
        """Test refresh with invalid token"""
        new_token = refresh_token("invalid.token", agent_id="opena1")
        assert new_token is None
        print("✅ Invalid token refresh rejected")


class TestKeyManagement:
    """RSA Key management tests"""
    
    def test_generate_keypair(self):
        """Test RSA keypair generation"""
        private_key, public_key = RSAKeyManager.generate_keypair()
        
        assert isinstance(private_key, str)
        assert isinstance(public_key, str)
        assert "BEGIN PRIVATE KEY" in private_key
        assert "BEGIN PUBLIC KEY" in public_key
        print("✅ RSA keypair generated successfully")
    
    def test_load_keys(self):
        """Test loading keys"""
        private_key = RSAKeyManager.load_private_key()
        public_key = RSAKeyManager.load_public_key()
        
        assert isinstance(private_key, str)
        assert isinstance(public_key, str)
        assert len(private_key) > 0
        assert len(public_key) > 0
        print("✅ Keys loaded successfully")


class TestTokenPayloads:
    """Test various token payloads and claims"""
    
    def test_token_payload_structure(self):
        """Test that token payload has correct structure"""
        import jwt as pyjwt
        
        token = create_token(agent_id="opena1", scope="invoke")
        
        # Decode without verification to check payload structure
        payload = pyjwt.decode(token, options={"verify_signature": False})
        
        # Check required JWT claims
        assert "iss" in payload
        assert "sub" in payload
        assert "aud" in payload
        assert "iat" in payload
        assert "exp" in payload
        assert "nbf" in payload
        assert "jti" in payload
        
        # Check custom claims
        assert "agent_id" in payload
        assert "scope" in payload
        assert "permissions" in payload
        
        print("✅ Token payload structure verified")
    
    def test_different_scopes(self):
        """Test tokens with different scopes"""
        scopes = ["read", "write", "admin", "invoke", "delete"]
        
        for scope in scopes:
            token = create_token(agent_id="opena1", scope=scope)
            result = verify_token(token)
            
            assert result.valid
            assert result.claims.scope == scope
        
        print(f"✅ All {len(scopes)} scope variants created and verified")


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_token_with_empty_permissions(self):
        """Test token with empty permissions"""
        token = create_token(agent_id="opena1", permissions=[])
        result = verify_token(token)
        
        assert result.valid
        assert result.claims.permissions == []
        print("✅ Empty permissions handled correctly")
    
    def test_token_with_long_agent_id(self):
        """Test token with long agent ID"""
        long_id = "agent_" + "x" * 100
        token = create_token(agent_id=long_id)
        result = verify_token(token)
        
        assert result.valid
        assert result.claims.agent_id == long_id
        print("✅ Long agent ID handled correctly")
    
    def test_tampered_token(self):
        """Test that tampered token is rejected"""
        token = create_token(agent_id="opena1")
        
        # Tamper with token
        tampered = token[:-10] + "0000000000"
        result = verify_token(tampered)
        
        assert not result.valid
        print("✅ Tampered token rejected")


class TestTimestamps:
    """Test timestamp handling in tokens"""
    
    def test_token_timestamps(self):
        """Test that token has correct timestamps"""
        import jwt as pyjwt
        
        token = create_token(agent_id="opena1")
        payload = pyjwt.decode(token, options={"verify_signature": False})
        
        # Verify timestamps are reasonable
        iat = payload["iat"]
        exp = payload["exp"]
        nbf = payload["nbf"]
        
        now = int(datetime.now(timezone.utc).timestamp())
        
        # iat should be close to now
        assert abs(now - iat) < 5
        
        # nbf should equal iat
        assert nbf == iat
        
        # exp should be after iat
        assert exp > iat
        
        # Expiration should be roughly 24 hours later
        exp_hours = (exp - iat) / 3600
        assert 23 < exp_hours < 25
        
        print("✅ Timestamps verified")


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple features"""
    
    def test_full_workflow(self):
        """Test complete token workflow"""
        # 1. Create token
        token = create_token(agent_id="opena1", scope="invoke", permissions=["read"])
        print("  1. ✅ Token created")
        
        # 2. Verify token
        result = verify_token(token)
        assert result.valid
        print("  2. ✅ Token verified")
        
        # 3. Check claims
        assert result.claims.agent_id == "opena1"
        assert result.claims.scope == "invoke"
        print("  3. ✅ Claims validated")
        
        # 4. Simulate token usage (get claims)
        claims_dict = {
            "agent_id": result.claims.agent_id,
            "scope": result.claims.scope,
            "permissions": result.claims.permissions
        }
        assert claims_dict["agent_id"] == "opena1"
        print("  4. ✅ Token used successfully")
    
    def test_multi_agent_tokens(self):
        """Test tokens for multiple agents"""
        agents = [
            ("opena1", "invoke", ["read", "write"]),
            ("opena2", "admin", ["read", "write", "delete"]),
            ("kordp", "read", ["read"]),
        ]
        
        tokens = {}
        for agent_id, scope, perms in agents:
            token = create_token(agent_id=agent_id, scope=scope, permissions=perms)
            result = verify_token(token)
            
            assert result.valid
            assert result.claims.agent_id == agent_id
            tokens[agent_id] = token
        
        assert len(tokens) == len(agents)
        print(f"✅ {len(tokens)} multi-agent tokens created and verified")


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Performance and stress tests"""
    
    def test_token_creation_performance(self):
        """Test token creation speed"""
        import time
        
        start = time.time()
        for i in range(10):
            create_token(agent_id=f"opena{i}", scope="invoke")
        elapsed = time.time() - start
        
        avg_time_ms = (elapsed / 10) * 1000
        print(f"✅ 10 tokens created in {elapsed:.3f}s (avg {avg_time_ms:.1f}ms/token)")
        
        assert elapsed < 5, "Token creation too slow"
    
    def test_token_verification_performance(self):
        """Test token verification speed"""
        import time
        
        tokens = [create_token(agent_id="opena1") for _ in range(5)]
        
        start = time.time()
        for token in tokens:
            verify_token(token)
        elapsed = time.time() - start
        
        avg_time_ms = (elapsed / len(tokens)) * 1000
        print(f"✅ {len(tokens)} tokens verified in {elapsed:.3f}s (avg {avg_time_ms:.1f}ms/token)")
        
        assert elapsed < 2, "Token verification too slow"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🔐 JWT Authentication Tests")
    print("=" * 70 + "\n")
    
    # Run with pytest if available
    pytest.main([__file__, "-v", "-s"])
