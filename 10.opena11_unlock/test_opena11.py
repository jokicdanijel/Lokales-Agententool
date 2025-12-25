#!/usr/bin/env python3
"""
Unit Tests for opena11 - Unlock Master Agent

Tests:
1. Health Check
2. Root Endpoint
3. Grant Permission
4. Revoke Permission
5. Check Permission (Allowed)
6. Check Permission (Denied)
7. Check Permission (Expired)
8. List Permissions
9. Audit Log
10. Command Endpoint
11. Wildcard Permissions
12. Strict JSON Validation
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta

import requests

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "http://127.0.0.1:12356"
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}", "Content-Type": "application/json"}

# Colors
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
RESET = "\033[0m"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def log_test(test_name: str):
    """Print test header"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}TEST: {test_name}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")


def log_success(message: str):
    """Print success message"""
    print(f"{GREEN}✓ {message}{RESET}")


def log_error(message: str):
    """Print error message"""
    print(f"{RED}✗ {message}{RESET}")


def log_info(message: str):
    """Print info message"""
    print(f"{YELLOW}ℹ {message}{RESET}")


# ============================================================================
# TEST FUNCTIONS
# ============================================================================


def test_health():
    """Test 1: Health Check"""
    log_test("Health Check")

    try:
        resp = requests.get(f"{BASE_URL}/health")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

        data = resp.json()
        assert data["status"] == "ok", "Status should be 'ok'"
        assert data["service"] == "opena11", "Service should be 'opena11'"
        assert data["kürzel"] == "unlockp", "Kürzel should be 'unlockp'"
        assert data["port"] == 12356, "Port should be 12356"

        log_success("Health check passed")
        log_info(f"Response: {json.dumps(data, indent=2)}")
        return True

    except Exception as e:
        log_error(f"Health check failed: {e}")
        return False


def test_root():
    """Test 2: Root Endpoint"""
    log_test("Root Endpoint")

    try:
        resp = requests.get(f"{BASE_URL}/")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

        data = resp.json()
        assert data["service"] == "opena11", "Service should be 'opena11'"
        assert data["kürzel"] == "unlockp", "Kürzel should be 'unlockp'"
        assert "endpoints" in data, "Should have endpoints list"

        log_success("Root endpoint passed")
        log_info(f"Endpoints: {data['endpoints']}")
        return True

    except Exception as e:
        log_error(f"Root endpoint failed: {e}")
        return False


def test_grant_permission():
    """Test 3: Grant Permission"""
    log_test("Grant Permission")

    try:
        payload = {"subject": "user123", "resource": "/files/documents", "action": "read"}

        resp = requests.post(f"{BASE_URL}/grant", headers=HEADERS, json=payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

        data = resp.json()
        assert data["status"] == "success", "Status should be 'success'"
        assert "permission" in data, "Should have permission object"
        assert data["permission"]["subject"] == "user123", "Subject mismatch"
        assert data["permission"]["resource"] == "/files/documents", "Resource mismatch"
        assert data["permission"]["action"] == "read", "Action mismatch"

        log_success("Grant permission passed")
        log_info(f"Permission ID: {data['permission']['permission_id']}")
        return True

    except Exception as e:
        log_error(f"Grant permission failed: {e}")
        return False


def test_revoke_permission():
    """Test 4: Revoke Permission"""
    log_test("Revoke Permission")

    try:
        # First grant a permission
        grant_payload = {"subject": "user456", "resource": "/files/temp", "action": "write"}
        resp = requests.post(f"{BASE_URL}/grant", headers=HEADERS, json=grant_payload)
        assert resp.status_code == 200, "Failed to grant permission for revoke test"

        # Now revoke it
        revoke_payload = {"subject": "user456", "resource": "/files/temp", "action": "write"}
        resp = requests.post(f"{BASE_URL}/revoke", headers=HEADERS, json=revoke_payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

        data = resp.json()
        assert data["status"] == "success", "Status should be 'success'"

        log_success("Revoke permission passed")
        return True

    except Exception as e:
        log_error(f"Revoke permission failed: {e}")
        return False


def test_check_permission_allowed():
    """Test 5: Check Permission (Allowed)"""
    log_test("Check Permission (Allowed)")

    try:
        # Grant permission first
        grant_payload = {"subject": "user789", "resource": "/api/endpoint", "action": "execute"}
        resp = requests.post(f"{BASE_URL}/grant", headers=HEADERS, json=grant_payload)
        assert resp.status_code == 200, "Failed to grant permission"

        # Check permission
        check_payload = {"subject": "user789", "resource": "/api/endpoint", "action": "execute"}
        resp = requests.post(f"{BASE_URL}/check", headers=HEADERS, json=check_payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

        data = resp.json()
        assert data["allowed"] is True, "Permission should be allowed"
        assert "matched_permission" in data, "Should have matched permission"

        log_success("Check permission (allowed) passed")
        log_info(f"Reason: {data['reason']}")
        return True

    except Exception as e:
        log_error(f"Check permission (allowed) failed: {e}")
        return False


def test_check_permission_denied():
    """Test 6: Check Permission (Denied)"""
    log_test("Check Permission (Denied)")

    try:
        check_payload = {"subject": "user999", "resource": "/nonexistent/resource", "action": "delete"}
        resp = requests.post(f"{BASE_URL}/check", headers=HEADERS, json=check_payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

        data = resp.json()
        assert data["allowed"] is False, "Permission should be denied"

        log_success("Check permission (denied) passed")
        log_info(f"Reason: {data['reason']}")
        return True

    except Exception as e:
        log_error(f"Check permission (denied) failed: {e}")
        return False


def test_check_permission_expired():
    """Test 7: Check Permission (Expired)"""
    log_test("Check Permission (Expired)")

    try:
        # Grant permission with past expiration
        expires_at = (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"
        grant_payload = {
            "subject": "user_expired",
            "resource": "/files/old",
            "action": "read",
            "expires_at": expires_at,
        }
        resp = requests.post(f"{BASE_URL}/grant", headers=HEADERS, json=grant_payload)
        assert resp.status_code == 200, "Failed to grant expired permission"

        # Check permission (should be denied due to expiration)
        check_payload = {"subject": "user_expired", "resource": "/files/old", "action": "read"}
        resp = requests.post(f"{BASE_URL}/check", headers=HEADERS, json=check_payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

        data = resp.json()
        assert data["allowed"] is False, "Expired permission should be denied"
        assert "expired" in data["reason"].lower(), "Reason should mention expiration"

        log_success("Check permission (expired) passed")
        log_info(f"Reason: {data['reason']}")
        return True

    except Exception as e:
        log_error(f"Check permission (expired) failed: {e}")
        return False


def test_list_permissions():
    """Test 8: List Permissions"""
    log_test("List Permissions")

    try:
        resp = requests.get(f"{BASE_URL}/list", headers=HEADERS)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

        data = resp.json()
        assert data["status"] == "success", "Status should be 'success'"
        assert "count" in data, "Should have count"
        assert "permissions" in data, "Should have permissions list"
        assert isinstance(data["permissions"], list), "Permissions should be a list"

        log_success("List permissions passed")
        log_info(f"Total permissions: {data['count']}")
        return True

    except Exception as e:
        log_error(f"List permissions failed: {e}")
        return False


def test_audit_log():
    """Test 9: Audit Log"""
    log_test("Audit Log")

    try:
        resp = requests.get(f"{BASE_URL}/audit?limit=10", headers=HEADERS)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

        data = resp.json()
        assert data["status"] == "success", "Status should be 'success'"
        assert "count" in data, "Should have count"
        assert "entries" in data, "Should have entries list"
        assert isinstance(data["entries"], list), "Entries should be a list"

        log_success("Audit log passed")
        log_info(f"Audit entries: {data['count']}")
        return True

    except Exception as e:
        log_error(f"Audit log failed: {e}")
        return False


def test_command_endpoint():
    """Test 10: Command Endpoint"""
    log_test("Command Endpoint (Option-2-Flow)")

    try:
        payload = {"command": "grant", "params": {"subject": "user_cmd", "resource": "/cmd/test", "action": "read"}}

        resp = requests.post(f"{BASE_URL}/command", headers=HEADERS, json=payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

        data = resp.json()
        assert data["status"] == "success", "Status should be 'success'"

        log_success("Command endpoint passed")
        return True

    except Exception as e:
        log_error(f"Command endpoint failed: {e}")
        return False


def test_wildcard_permissions():
    """Test 11: Wildcard Permissions"""
    log_test("Wildcard Permissions")

    try:
        # Grant wildcard permission
        grant_payload = {"subject": "user_wildcard", "resource": "/files/*", "action": "read"}
        resp = requests.post(f"{BASE_URL}/grant", headers=HEADERS, json=grant_payload)
        assert resp.status_code == 200, "Failed to grant wildcard permission"

        # Check permission on sub-resource
        check_payload = {"subject": "user_wildcard", "resource": "/files/documents/report.pdf", "action": "read"}
        resp = requests.post(f"{BASE_URL}/check", headers=HEADERS, json=check_payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

        data = resp.json()
        assert data["allowed"] is True, "Wildcard permission should match sub-resource"

        log_success("Wildcard permissions passed")
        log_info("Wildcard /files/* matched /files/documents/report.pdf")
        return True

    except Exception as e:
        log_error(f"Wildcard permissions failed: {e}")
        return False


def test_strict_json():
    """Test 12: Strict JSON Validation"""
    log_test("Strict JSON Validation (extra='forbid')")

    try:
        # Send request with extra field
        payload = {
            "subject": "user_strict",
            "resource": "/test",
            "action": "read",
            "extra_field": "this_should_fail",  # Not allowed
        }

        resp = requests.post(f"{BASE_URL}/grant", headers=HEADERS, json=payload)
        assert resp.status_code == 422, f"Expected 422 (validation error), got {resp.status_code}"

        log_success("Strict JSON validation passed (rejected extra field)")
        return True

    except Exception as e:
        log_error(f"Strict JSON validation failed: {e}")
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================


def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}opena11 (unlockp) - Test Suite{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"Base URL: {BASE_URL}")
    print(f"Bearer Token: {'SET' if BEARER_TOKEN else 'NOT SET'}")
    print(f"{BLUE}{'='*70}{RESET}\n")

    if not BEARER_TOKEN:
        log_error("BEARER_TOKEN not set in environment")
        sys.exit(1)

    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Grant Permission", test_grant_permission),
        ("Revoke Permission", test_revoke_permission),
        ("Check Permission (Allowed)", test_check_permission_allowed),
        ("Check Permission (Denied)", test_check_permission_denied),
        ("Check Permission (Expired)", test_check_permission_expired),
        ("List Permissions", test_list_permissions),
        ("Audit Log", test_audit_log),
        ("Command Endpoint", test_command_endpoint),
        ("Wildcard Permissions", test_wildcard_permissions),
        ("Strict JSON", test_strict_json),
    ]

    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
        time.sleep(0.5)  # Small delay between tests

    # Summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{status} - {name}")

    print(f"{BLUE}{'='*70}{RESET}")
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print(f"{GREEN}✓ All tests passed!{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        sys.exit(0)
    else:
        print(f"{RED}✗ {total - passed} test(s) failed{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
