#!/usr/bin/env python3
"""
test_opena13.py - Integration Tests für opena13 (Influencer Agent)
===================================================================

Test Coverage:
  1. Health Check
  2. Root Endpoint
  3. Create Influencer Profile
  4. List Profiles (with filters)
  5. Create Campaign
  6. List Campaigns
  7. Match Influencers to Campaign
  8. Get Metrics
  9. Command Endpoint (Option-2-Flow)
 10. Matching Algorithm (edge cases)
 11. Strict JSON Validation

Port: 12358
Auth: Bearer Token (from .env)

Maintainer: ELION Team
Last Update: 27. November 2025
"""

import json
import requests
import time
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "http://127.0.0.1:12358"
PROJECT_ROOT = Path(__file__).parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

# Load Bearer Token
BEARER_TOKEN = None
if ENV_PATH.exists():
    with open(ENV_PATH) as f:
        for line in f:
            if line.strip().startswith("BEARER_TOKEN="):
                BEARER_TOKEN = line.split("=", 1)[1].strip()
                break

if not BEARER_TOKEN:
    print("⚠️  WARNING: BEARER_TOKEN nicht in .env gefunden!")
    BEARER_TOKEN = "dev-token-only"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

# ============================================================================
# COLOR OUTPUT
# ============================================================================

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_test(name, status, details=""):
    """Print color-coded test result"""
    color = GREEN if status == "PASS" else RED
    symbol = "✓" if status == "PASS" else "✗"
    print(f"{color}[{symbol}] Test {name}: {status}{RESET}")
    if details:
        print(f"    {BLUE}{details}{RESET}")

# ============================================================================
# TESTS
# ============================================================================

def test_health():
    """Test 1: Health Check"""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        data = r.json()
        
        assert r.status_code == 200, f"Status {r.status_code}"
        assert data["status"] == "ok", f"Status: {data['status']}"
        assert data["service"] == "opena13", f"Service: {data['service']}"
        assert data["port"] == 12358, f"Port: {data['port']}"
        assert data["kuerzel"] == "influp", f"Kürzel: {data['kuerzel']}"
        
        print_test("1 (Health)", "PASS", f"Uptime: {data['uptime_seconds']:.2f}s, Profiles: {data['total_profiles']}")
        return True
    except Exception as e:
        print_test("1 (Health)", "FAIL", str(e))
        return False


def test_root():
    """Test 2: Root Endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/", timeout=5)
        data = r.json()
        
        assert r.status_code == 200
        assert data["service"] == "opena13"
        assert data["kuerzel"] == "influp"
        assert data["port"] == "12358"
        
        print_test("2 (Root)", "PASS", f"Description: {data['description'][:50]}...")
        return True
    except Exception as e:
        print_test("2 (Root)", "FAIL", str(e))
        return False


def test_create_profile():
    """Test 3: Create Influencer Profile"""
    try:
        payload = {
            "name": "TestInfluencer_Fashion",
            "platform": "instagram",
            "followers": 150000,
            "engagement_rate": 4.5,
            "niche": "fashion",
            "contact_email": "test@example.com",
            "avg_likes": 6750,
            "avg_comments": 250
        }
        
        r = requests.post(f"{BASE_URL}/profiles/create", headers=HEADERS, json=payload, timeout=5)
        data = r.json()
        
        assert r.status_code == 200, f"Status {r.status_code}"
        assert "profile_id" in data, "Missing profile_id"
        assert data["name"] == payload["name"]
        assert data["platform"] == "instagram"
        assert data["followers"] == 150000
        assert data["niche"] == "fashion"
        
        print_test("3 (Create Profile)", "PASS", f"Profile ID: {data['profile_id'][:8]}")
        
        # Store for later tests
        global TEST_PROFILE_ID
        TEST_PROFILE_ID = data["profile_id"]
        return True
    except Exception as e:
        print_test("3 (Create Profile)", "FAIL", str(e))
        return False


def test_list_profiles():
    """Test 4: List Profiles (with filters)"""
    try:
        # Test 1: List all profiles
        r1 = requests.get(f"{BASE_URL}/profiles", headers=HEADERS, timeout=5)
        data1 = r1.json()
        
        assert r1.status_code == 200
        assert isinstance(data1, list)
        assert len(data1) > 0, "No profiles found"
        
        # Test 2: Filter by platform
        r2 = requests.get(f"{BASE_URL}/profiles?platform=instagram", headers=HEADERS, timeout=5)
        data2 = r2.json()
        
        assert r2.status_code == 200
        assert all(p["platform"] == "instagram" for p in data2)
        
        # Test 3: Filter by niche
        r3 = requests.get(f"{BASE_URL}/profiles?niche=fashion", headers=HEADERS, timeout=5)
        data3 = r3.json()
        
        assert r3.status_code == 200
        assert all(p["niche"] == "fashion" for p in data3)
        
        print_test("4 (List Profiles)", "PASS", f"Total: {len(data1)}, Instagram: {len(data2)}, Fashion: {len(data3)}")
        return True
    except Exception as e:
        print_test("4 (List Profiles)", "FAIL", str(e))
        return False


def test_create_campaign():
    """Test 5: Create Campaign"""
    try:
        payload = {
            "name": "Summer Fashion Campaign 2025",
            "budget": 50000.0,
            "target_audience": "Women 18-35, Fashion-conscious, Urban",
            "niches": ["fashion", "lifestyle"],
            "min_followers": 100000,
            "min_engagement_rate": 3.0,
            "start_date": "2025-06-01T00:00:00Z",
            "end_date": "2025-08-31T23:59:59Z"
        }
        
        r = requests.post(f"{BASE_URL}/campaigns/create", headers=HEADERS, json=payload, timeout=5)
        data = r.json()
        
        assert r.status_code == 200, f"Status {r.status_code}"
        assert "campaign_id" in data
        assert data["name"] == payload["name"]
        assert data["budget"] == 50000.0
        assert set(data["niches"]) == {"fashion", "lifestyle"}
        assert data["status"] == "draft"
        
        print_test("5 (Create Campaign)", "PASS", f"Campaign ID: {data['campaign_id'][:8]}")
        
        # Store for matching test
        global TEST_CAMPAIGN_ID
        TEST_CAMPAIGN_ID = data["campaign_id"]
        return True
    except Exception as e:
        print_test("5 (Create Campaign)", "FAIL", str(e))
        return False


def test_list_campaigns():
    """Test 6: List Campaigns"""
    try:
        r1 = requests.get(f"{BASE_URL}/campaigns", headers=HEADERS, timeout=5)
        data1 = r1.json()
        
        assert r1.status_code == 200
        assert isinstance(data1, list)
        assert len(data1) > 0
        
        # Filter by status
        r2 = requests.get(f"{BASE_URL}/campaigns?status=draft", headers=HEADERS, timeout=5)
        data2 = r2.json()
        
        assert r2.status_code == 200
        assert all(c["status"] == "draft" for c in data2)
        
        print_test("6 (List Campaigns)", "PASS", f"Total: {len(data1)}, Draft: {len(data2)}")
        return True
    except Exception as e:
        print_test("6 (List Campaigns)", "FAIL", str(e))
        return False


def test_match_influencers():
    """Test 7: Match Influencers to Campaign"""
    try:
        payload = {
            "campaign_id": TEST_CAMPAIGN_ID,
            "max_results": 5,
            "min_score": 50.0
        }
        
        r = requests.post(f"{BASE_URL}/match", headers=HEADERS, json=payload, timeout=5)
        data = r.json()
        
        assert r.status_code == 200, f"Status {r.status_code}"
        assert "matches" in data
        assert "total_candidates" in data
        assert data["campaign_id"] == TEST_CAMPAIGN_ID
        
        # Verify match structure
        if len(data["matches"]) > 0:
            match = data["matches"][0]
            assert "match_id" in match
            assert "profile" in match
            assert "score" in match
            assert "reasoning" in match
            assert 0 <= match["score"] <= 100
        
        print_test("7 (Match Influencers)", "PASS", f"Matches: {len(data['matches'])}, Candidates: {data['total_candidates']}")
        return True
    except Exception as e:
        print_test("7 (Match Influencers)", "FAIL", str(e))
        return False


def test_metrics():
    """Test 8: Get Metrics"""
    try:
        payload = {
            "platform": "instagram",
            "niche": "fashion"
        }
        
        r = requests.post(f"{BASE_URL}/metrics", headers=HEADERS, json=payload, timeout=5)
        data = r.json()
        
        assert r.status_code == 200, f"Status {r.status_code}"
        assert "total_profiles" in data
        assert "total_campaigns" in data
        assert "total_matches" in data
        assert "avg_engagement_rate" in data
        assert "total_followers" in data
        assert "platforms" in data
        assert "niches" in data
        
        print_test("8 (Metrics)", "PASS", f"Profiles: {data['total_profiles']}, Avg Engagement: {data['avg_engagement_rate']}%")
        return True
    except Exception as e:
        print_test("8 (Metrics)", "FAIL", str(e))
        return False


def test_command_endpoint():
    """Test 9: Command Endpoint (Option-2-Flow)"""
    try:
        # Test create_profile via command
        payload = {
            "action": "create_profile",
            "params": {
                "name": "TestInfluencer_Tech",
                "platform": "youtube",
                "followers": 500000,
                "engagement_rate": 6.2,
                "niche": "tech",
                "contact_email": "tech@example.com"
            }
        }
        
        r = requests.post(f"{BASE_URL}/command", headers=HEADERS, json=payload, timeout=5)
        data = r.json()
        
        assert r.status_code == 200, f"Status {r.status_code}"
        assert data["status"] == "success"
        assert data["action"] == "create_profile"
        assert "result" in data
        assert data["result"]["name"] == "TestInfluencer_Tech"
        
        print_test("9 (Command Endpoint)", "PASS", f"Action: {data['action']}, Profile created")
        return True
    except Exception as e:
        print_test("9 (Command Endpoint)", "FAIL", str(e))
        return False


def test_matching_algorithm_edge_cases():
    """Test 10: Matching Algorithm Edge Cases"""
    try:
        # Create edge case profile: Low followers, high engagement
        profile_payload = {
            "name": "MicroInfluencer_HighEngagement",
            "platform": "tiktok",
            "followers": 50000,  # Below typical threshold
            "engagement_rate": 12.5,  # Very high
            "niche": "fitness"
        }
        
        r1 = requests.post(f"{BASE_URL}/profiles/create", headers=HEADERS, json=profile_payload, timeout=5)
        assert r1.status_code == 200
        
        # Create campaign with high follower requirement
        campaign_payload = {
            "name": "Fitness Campaign - High Reach",
            "budget": 30000.0,
            "target_audience": "Fitness enthusiasts 20-40",
            "niches": ["fitness"],
            "min_followers": 200000,  # High threshold
            "min_engagement_rate": 2.0,
            "start_date": "2025-07-01T00:00:00Z"
        }
        
        r2 = requests.post(f"{BASE_URL}/campaigns/create", headers=HEADERS, json=campaign_payload, timeout=5)
        data2 = r2.json()
        campaign_id = data2["campaign_id"]
        
        # Match - should NOT match due to follower count
        match_payload = {
            "campaign_id": campaign_id,
            "max_results": 10,
            "min_score": 50.0
        }
        
        r3 = requests.post(f"{BASE_URL}/match", headers=HEADERS, json=match_payload, timeout=5)
        data3 = r3.json()
        
        # Micro influencer should not appear in results (follower threshold)
        matched_names = [m["profile"]["name"] for m in data3["matches"]]
        assert "MicroInfluencer_HighEngagement" not in matched_names, "Edge case failed: Low followers should be filtered out"
        
        print_test("10 (Matching Algorithm)", "PASS", "Edge cases handled correctly (follower threshold)")
        return True
    except Exception as e:
        print_test("10 (Matching Algorithm)", "FAIL", str(e))
        return False


def test_strict_json():
    """Test 11: Strict JSON Validation (extra="forbid")"""
    try:
        # Send request with unknown field
        payload = {
            "name": "TestProfile",
            "platform": "instagram",
            "followers": 100000,
            "engagement_rate": 3.5,
            "niche": "beauty",
            "unknown_field": "should_be_rejected"  # Extra field
        }
        
        r = requests.post(f"{BASE_URL}/profiles/create", headers=HEADERS, json=payload, timeout=5)
        
        # Pydantic should reject this (422 Unprocessable Entity)
        assert r.status_code == 422, f"Expected 422, got {r.status_code}"
        
        error = r.json()
        assert "detail" in error
        
        print_test("11 (Strict JSON)", "PASS", "Unknown fields rejected (extra='forbid')")
        return True
    except Exception as e:
        print_test("11 (Strict JSON)", "FAIL", str(e))
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}  opena13 (Influencer) - Integration Tests{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    print(f"Base URL:      {BASE_URL}")
    print(f"Bearer Token:  {BEARER_TOKEN[:20]}...")
    print()
    
    # Wait for service
    print(f"{YELLOW}Warte auf Service-Start (3 Sekunden)...{RESET}")
    time.sleep(3)
    
    # Run tests
    results = []
    
    results.append(test_health())
    results.append(test_root())
    results.append(test_create_profile())
    results.append(test_list_profiles())
    results.append(test_create_campaign())
    results.append(test_list_campaigns())
    results.append(test_match_influencers())
    results.append(test_metrics())
    results.append(test_command_endpoint())
    results.append(test_matching_algorithm_edge_cases())
    results.append(test_strict_json())
    
    # Summary
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}  Test Summary{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    print(f"Total:  {total}")
    print(f"Passed: {GREEN}{passed}{RESET}")
    print(f"Failed: {RED}{total - passed}{RESET}")
    print(f"Rate:   {GREEN if percentage == 100 else YELLOW}{percentage:.1f}%{RESET}")
    print()
    
    if percentage == 100:
        print(f"{GREEN}✅ ALL TESTS PASSED{RESET}\n")
        return 0
    else:
        print(f"{RED}❌ SOME TESTS FAILED{RESET}\n")
        return 1


if __name__ == "__main__":
    exit(main())
