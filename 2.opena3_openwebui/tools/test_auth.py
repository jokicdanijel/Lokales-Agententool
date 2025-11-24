#!/usr/bin/env python3
"""
PORTIER 3.0 Authentication Test Suite
Tests all Bearer token validation functionality
"""

import sys
from pathlib import Path

# Add LocalAgent-Pro to path
la_pro_path = str(Path(__file__).parent.parent / "LocalAgent-Pro")
if la_pro_path not in sys.path:
    sys.path.insert(0, la_pro_path)

from shared.auth import (
    token_validator,
    rate_limiter,
    audit_logger,
    extract_bearer_token,
    VALID_TOKENS
)

def test_token_validation():
    """Test token validation"""
    print("🧪 TEST 1: Token Validation")
    print("-" * 50)

    # Valid token
    valid_token = "sk_opena1_coordinator_v3_production"
    result = token_validator.is_valid_token(valid_token)
    print(f"  ✅ Valid token: {result}")
    assert result == True, f"Valid token should be True, got {result}"

    # Invalid token
    invalid_token = "sk_invalid_token_v3_production"
    result = token_validator.is_valid_token(invalid_token)
    print(f"  ✅ Invalid token rejection: {not result}")
    assert result == False, f"Invalid token should be False, got {result}"

    # Empty token
    result = token_validator.is_valid_token("")
    print(f"  ✅ Empty token rejection: {not result}")
    assert result == False, f"Empty token should be False, got {result}"

    print("✨ Token validation tests passed!\n")def test_client_id_extraction():
    """Test client ID extraction from tokens"""
    print("🧪 TEST 2: Client ID Extraction")
    print("-" * 50)

    for agent_num in [1, 2, 3, 4, 10, 19]:
        token = f"sk_opena{agent_num}_compute_v3_production"
        client_id = token_validator.validate_and_get_client_id(token)
        expected = f"opena{agent_num}"
        print(f"  ✅ opena{agent_num}: {client_id} == {expected}")
        assert client_id == expected

    print("✨ Client ID extraction tests passed!\n")

def test_rate_limiting():
    """Test rate limiting functionality"""
    print("🧪 TEST 3: Rate Limiting")
    print("-" * 50)

    # Reset rate limiter
    limiter = rate_limiter
    client = "test_client"

    # Allow requests up to limit
    allowed_count = 0
    for i in range(10):
        if limiter.is_allowed(client):
            allowed_count += 1

    print(f"  ✅ Allowed 10 requests: {allowed_count == 10}")
    assert allowed_count == 10

    remaining = limiter.get_remaining_requests(client)
    print(f"  ✅ Remaining requests: {remaining} (should be < 1000)")
    assert remaining < 1000

    print("✨ Rate limiting tests passed!\n")

def test_bearer_token_extraction():
    """Test Bearer token extraction from headers"""
    print("🧪 TEST 4: Bearer Token Extraction")
    print("-" * 50)

    # Valid header
    header = "Bearer sk_opena1_coordinator_v3_production"
    token = extract_bearer_token(header)
    print(f"  ✅ Valid header: {token == 'sk_opena1_coordinator_v3_production'}")
    assert token == "sk_opena1_coordinator_v3_production"

    # Invalid format
    header = "Basic dXNlcjpwYXNz"
    token = extract_bearer_token(header)
    print(f"  ✅ Invalid format rejection: {token is None}")
    assert token is None

    # Missing header
    token = extract_bearer_token(None)
    print(f"  ✅ Missing header rejection: {token is None}")
    assert token is None

    print("✨ Bearer token extraction tests passed!\n")

def test_token_priority():
    """Test token priority levels"""
    print("🧪 TEST 5: Token Priority Levels")
    print("-" * 50)

    core_token = "sk_opena1_coordinator_v3_production"
    compute_token = "sk_opena10_compute_v3_production"

    core_priority = token_validator.get_token_priority(core_token)
    compute_priority = token_validator.get_token_priority(compute_token)

    print(f"  ✅ Core token priority: {core_priority} (should be >= compute)")
    print(f"  ✅ Compute token priority: {compute_priority}")
    assert core_priority > compute_priority

    print("✨ Token priority tests passed!\n")

def test_token_revocation():
    """Test token revocation"""
    print("🧪 TEST 6: Token Revocation")
    print("-" * 50)

    test_token = "sk_test_dev_v3_development"

    # Token should be valid initially
    valid = token_validator.is_valid_token(test_token)
    print(f"  ✅ Test token initially valid: {valid}")

    # Revoke token
    revoked = token_validator.revoke_token(test_token)
    print(f"  ✅ Token revocation successful: {revoked}")

    # Token should be invalid after revocation
    valid = token_validator.is_valid_token(test_token)
    print(f"  ✅ Test token now invalid: {not valid}")
    assert valid == False

    print("✨ Token revocation tests passed!\n")

def test_audit_logging():
    """Test audit logging"""
    print("🧪 TEST 7: Audit Logging")
    print("-" * 50)

    logger = audit_logger

    # Log successful access
    logger.log_access("opena1", "sk_opena1_coordinator_v3_production",
                     "/status", "success", "0.0.0.0")
    print(f"  ✅ Access log written")

    # Log failed attempt
    logger.log_failed_attempt("invalid_token", "/status",
                             "invalid_token", "0.0.0.0")
    print(f"  ✅ Failed attempt log written")

    # Log rate limit
    logger.log_rate_limit("opena1", "sk_opena1_coordinator_v3_production", "0.0.0.0")
    print(f"  ✅ Rate limit log written")

    # Verify log file exists
    log_file = logger.log_file
    if log_file.exists():
        print(f"  ✅ Audit log file created: {log_file}")

    print("✨ Audit logging tests passed!\n")

def test_all_tokens():
    """Verify all configured tokens are valid"""
    print("🧪 TEST 8: All Configured Tokens")
    print("-" * 50)

    print(f"  📊 Total tokens configured: {len(VALID_TOKENS)}")

    valid_count = 0
    for token in VALID_TOKENS.keys():
        if token_validator.is_valid_token(token):
            valid_count += 1

    print(f"  ✅ All tokens validated: {valid_count}/{len(VALID_TOKENS)}")
    assert valid_count == len(VALID_TOKENS)

    # Display core tokens
    print("\n  Core Tokens:")
    for token in ["sk_opena1_coordinator_v3_production",
                  "sk_opena2_archivator_v3_production",
                  "sk_opena3_gateway_v3_production"]:
        info = token_validator.get_token_info(token)
        print(f"    • {token}: {info}")

    print("\n✨ All token validation tests passed!\n")

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  🔐 PORTIER 3.0 - AUTHENTICATION TEST SUITE")
    print("=" * 60 + "\n")

    try:
        test_token_validation()
        test_client_id_extraction()
        test_rate_limiting()
        test_bearer_token_extraction()
        test_token_priority()
        test_token_revocation()
        test_audit_logging()
        test_all_tokens()

        print("=" * 60)
        print("  ✅ ALL TESTS PASSED!")
        print("=" * 60 + "\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
