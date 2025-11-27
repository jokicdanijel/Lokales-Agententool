#!/usr/bin/env python3
"""
Unit Tests for opena12 - Social Media Automation Agent

Tests:
1. Health Check
2. Root Endpoint
3. Post to Single Platform
4. Post to Multiple Platforms
5. Schedule Post
6. Get Post Status
7. Delete Post
8. List Platforms
9. Character Limit Validation
10. Command Endpoint
11. Strict JSON Validation
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta

import requests

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "http://127.0.0.1:12357"
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

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
        assert data["service"] == "opena12", "Service should be 'opena12'"
        assert data["kürzel"] == "smp", "Kürzel should be 'smp'"
        assert data["port"] == 12357, "Port should be 12357"
        assert "platforms" in data, "Should have platforms list"
        
        log_success("Health check passed")
        log_info(f"Platforms: {data['platforms']}")
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
        assert data["service"] == "opena12", "Service should be 'opena12'"
        assert data["kürzel"] == "smp", "Kürzel should be 'smp'"
        assert "endpoints" in data, "Should have endpoints list"
        assert "platforms" in data, "Should have platforms list"
        
        log_success("Root endpoint passed")
        log_info(f"Endpoints: {data['endpoints']}")
        return True
    
    except Exception as e:
        log_error(f"Root endpoint failed: {e}")
        return False


def test_post_single_platform():
    """Test 3: Post to Single Platform"""
    log_test("Post to Single Platform")
    
    try:
        payload = {
            "platforms": ["linkedin"],
            "text": "Test post from opena12 - Social Media Automation Agent",
            "hashtags": ["testing", "automation"]
        }
        
        resp = requests.post(f"{BASE_URL}/post", headers=HEADERS, json=payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert data["status"] == "success", "Status should be 'success'"
        assert "post_id" in data, "Should have post_id"
        assert "published_urls" in data, "Should have published_urls"
        assert "linkedin" in data["published_urls"], "Should have LinkedIn URL"
        
        log_success("Post to single platform passed")
        log_info(f"Post ID: {data['post_id']}")
        log_info(f"LinkedIn URL: {data['published_urls']['linkedin']}")
        return True
    
    except Exception as e:
        log_error(f"Post to single platform failed: {e}")
        return False


def test_post_multiple_platforms():
    """Test 4: Post to Multiple Platforms"""
    log_test("Post to Multiple Platforms")
    
    try:
        payload = {
            "platforms": ["linkedin", "x", "facebook"],
            "text": "Multi-platform test post 🚀",
            "hashtags": ["multiplatform", "socialmedia"]
        }
        
        resp = requests.post(f"{BASE_URL}/post", headers=HEADERS, json=payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert data["status"] == "success", "Status should be 'success'"
        assert len(data["published_urls"]) == 3, "Should have 3 platform URLs"
        
        log_success("Post to multiple platforms passed")
        log_info(f"Published to: {list(data['published_urls'].keys())}")
        return True
    
    except Exception as e:
        log_error(f"Post to multiple platforms failed: {e}")
        return False


def test_schedule_post():
    """Test 5: Schedule Post"""
    log_test("Schedule Post")
    
    try:
        # Schedule for 1 hour from now
        scheduled_time = (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"
        
        payload = {
            "platforms": ["linkedin"],
            "text": "Scheduled post test",
            "hashtags": ["scheduled"],
            "scheduled_at": scheduled_time
        }
        
        resp = requests.post(f"{BASE_URL}/schedule", headers=HEADERS, json=payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert data["status"] == "success", "Status should be 'success'"
        assert "post_id" in data, "Should have post_id"
        assert data["scheduled_at"] == scheduled_time, "Scheduled time should match"
        
        log_success("Schedule post passed")
        log_info(f"Post ID: {data['post_id']}")
        log_info(f"Scheduled for: {scheduled_time}")
        return True
    
    except Exception as e:
        log_error(f"Schedule post failed: {e}")
        return False


def test_get_status():
    """Test 6: Get Post Status"""
    log_test("Get Post Status")
    
    try:
        # First create a post
        payload = {
            "platforms": ["x"],
            "text": "Status check test post"
        }
        
        resp = requests.post(f"{BASE_URL}/post", headers=HEADERS, json=payload)
        assert resp.status_code == 200, "Failed to create post for status test"
        
        post_id = resp.json()["post_id"]
        
        # Now check status
        resp = requests.get(f"{BASE_URL}/status/{post_id}", headers=HEADERS)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert data["post_id"] == post_id, "Post ID should match"
        assert data["status"] in ["published", "pending"], "Status should be valid"
        
        log_success("Get post status passed")
        log_info(f"Status: {data['status']}")
        return True
    
    except Exception as e:
        log_error(f"Get post status failed: {e}")
        return False


def test_delete_post():
    """Test 7: Delete Post"""
    log_test("Delete Post")
    
    try:
        # First create a post
        payload = {
            "platforms": ["facebook"],
            "text": "Post to be deleted"
        }
        
        resp = requests.post(f"{BASE_URL}/post", headers=HEADERS, json=payload)
        assert resp.status_code == 200, "Failed to create post for deletion test"
        
        post_id = resp.json()["post_id"]
        
        # Now delete it
        delete_payload = {
            "post_id": post_id,
            "platform": "facebook"
        }
        
        resp = requests.delete(f"{BASE_URL}/delete", headers=HEADERS, json=delete_payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert data["status"] == "success", "Status should be 'success'"
        
        log_success("Delete post passed")
        return True
    
    except Exception as e:
        log_error(f"Delete post failed: {e}")
        return False


def test_list_platforms():
    """Test 8: List Platforms"""
    log_test("List Platforms")
    
    try:
        resp = requests.get(f"{BASE_URL}/platforms/list", headers=HEADERS)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert data["status"] == "success", "Status should be 'success'"
        assert "platforms" in data, "Should have platforms list"
        assert isinstance(data["platforms"], list), "Platforms should be a list"
        assert len(data["platforms"]) > 0, "Should have at least one platform"
        
        log_success("List platforms passed")
        log_info(f"Platforms: {[p['name'] for p in data['platforms']]}")
        return True
    
    except Exception as e:
        log_error(f"List platforms failed: {e}")
        return False


def test_character_limit():
    """Test 9: Character Limit Validation"""
    log_test("Character Limit Validation (X/Twitter 280)")
    
    try:
        # Create text longer than Twitter's 280 character limit
        long_text = "A" * 300
        
        payload = {
            "platforms": ["x"],
            "text": long_text
        }
        
        resp = requests.post(f"{BASE_URL}/post", headers=HEADERS, json=payload)
        
        # Should either fail or truncate
        # In our mock implementation, it should fail
        data = resp.json()
        
        if resp.status_code == 200:
            # Check if there's an error for the platform
            assert data.get("errors"), "Should have platform-specific error"
            assert "x" in data.get("errors", {}), "Should have error for X platform"
            log_success("Character limit validation passed (error reported)")
        else:
            log_success("Character limit validation passed (request rejected)")
        
        return True
    
    except Exception as e:
        log_error(f"Character limit validation failed: {e}")
        return False


def test_command_endpoint():
    """Test 10: Command Endpoint (Option-2-Flow)"""
    log_test("Command Endpoint")
    
    try:
        payload = {
            "command": "post",
            "params": {
                "platforms": ["linkedin"],
                "text": "Command endpoint test"
            }
        }
        
        resp = requests.post(f"{BASE_URL}/command", headers=HEADERS, json=payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert data["status"] == "success", "Status should be 'success'"
        
        log_success("Command endpoint passed")
        return True
    
    except Exception as e:
        log_error(f"Command endpoint failed: {e}")
        return False


def test_strict_json():
    """Test 11: Strict JSON Validation"""
    log_test("Strict JSON Validation (extra='forbid')")
    
    try:
        # Send request with extra field
        payload = {
            "platforms": ["linkedin"],
            "text": "Test post",
            "extra_field": "this_should_fail"  # Not allowed
        }
        
        resp = requests.post(f"{BASE_URL}/post", headers=HEADERS, json=payload)
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
    print(f"{BLUE}opena12 (smp) - Test Suite{RESET}")
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
        ("Post to Single Platform", test_post_single_platform),
        ("Post to Multiple Platforms", test_post_multiple_platforms),
        ("Schedule Post", test_schedule_post),
        ("Get Post Status", test_get_status),
        ("Delete Post", test_delete_post),
        ("List Platforms", test_list_platforms),
        ("Character Limit Validation", test_character_limit),
        ("Command Endpoint", test_command_endpoint),
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
