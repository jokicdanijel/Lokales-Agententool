#!/usr/bin/env python3
"""
opena10 Test Suite (Call Tracking Agent)
=========================================

Tests:
1. Health-Check (GET /health)
2. Root-Endpoint (GET /)
3. Command-Endpoint (POST /command)
4. Campaign Creation (POST /campaigns/create)
5. Campaign List (GET /campaigns/list)
6. Tracking Number Creation (POST /tracking_numbers/create)
7. Tracking Number List (GET /tracking_numbers/list)
8. Event Ingestion (POST /events/ingest)
9. Stats Summary (GET /stats/summary)
10. Stats by Campaign (GET /stats/by_campaign)
11. Strict JSON Validation (extra="forbid")

Expected: 11/11 tests pass
"""

import os
import sys
import requests
from datetime import datetime, timezone

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────

BASE_URL = "http://127.0.0.1:12355"
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

if not BEARER_TOKEN:
    print("⚠️  WARNING: BEARER_TOKEN nicht gesetzt")
    print("   Setze mit: export BEARER_TOKEN=$(grep BEARER_TOKEN ../.env | cut -d= -f2)")

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# ──────────────────────────────────────────────────────────────────────────────
# TESTS
# ──────────────────────────────────────────────────────────────────────────────

def test_health():
    """Test: Health-Check"""
    print(f"\n{BLUE}TEST: Health-Check{RESET}")
    resp = requests.get(f"{BASE_URL}/health")
    data = resp.json()
    print(f"   Health: {data}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert data["status"] == "ok", f"Expected status=ok, got {data.get('status')}"
    assert data["agent"] == "opena10", f"Expected agent=opena10, got {data.get('agent')}"
    assert data["kuerzel"] == "calltrackp", f"Expected kuerzel=calltrackp, got {data.get('kuerzel')}"
    print(f"{GREEN}✅ Health OK{RESET}")


def test_root():
    """Test: Root-Endpoint"""
    print(f"\n{BLUE}TEST: Root-Endpoint{RESET}")
    resp = requests.get(f"{BASE_URL}/")
    data = resp.json()
    print(f"   Root: {data}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert data["kuerzel"] == "calltrackp", f"Expected kuerzel=calltrackp"
    assert "capabilities" in data, "Expected capabilities field"
    assert "events/ingest" in data["capabilities"], "Expected events/ingest capability"
    print(f"{GREEN}✅ Root OK{RESET}")


def test_command():
    """Test: Command-Endpoint"""
    print(f"\n{BLUE}TEST: Command-Endpoint{RESET}")
    payload = {
        "command": "test_command",
        "params": {"test": "value"}
    }
    resp = requests.post(f"{BASE_URL}/command", json=payload, headers=HEADERS)
    data = resp.json()
    print(f"   Command: {data}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert data["status"] == "executed", f"Expected status=executed"
    print(f"{GREEN}✅ Command OK{RESET}")


def test_campaign_create():
    """Test: Campaign Creation"""
    print(f"\n{BLUE}TEST: Campaign Creation{RESET}")
    payload = {
        "campaign_id": f"test_campaign_{int(datetime.now().timestamp())}",
        "name": "Test Campaign",
        "description": "Automated test campaign"
    }
    resp = requests.post(f"{BASE_URL}/campaigns/create", json=payload, headers=HEADERS)
    data = resp.json()
    print(f"   Campaign Created: {data}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert data["status"] == "success", f"Expected status=success"
    assert "campaign" in data, "Expected campaign field"
    print(f"{GREEN}✅ Campaign Create OK{RESET}")
    return data["campaign"]["campaign_id"]


def test_campaign_list():
    """Test: Campaign List"""
    print(f"\n{BLUE}TEST: Campaign List{RESET}")
    resp = requests.get(f"{BASE_URL}/campaigns/list", headers=HEADERS)
    data = resp.json()
    print(f"   Campaigns: {len(data.get('campaigns', []))} campaigns found")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert "campaigns" in data, "Expected campaigns field"
    print(f"{GREEN}✅ Campaign List OK{RESET}")


def test_tracking_number_create(campaign_id):
    """Test: Tracking Number Creation"""
    print(f"\n{BLUE}TEST: Tracking Number Creation{RESET}")
    payload = {
        "number": f"+491234{int(datetime.now().timestamp()) % 1000000}",
        "campaign_id": campaign_id,
        "description": "Test tracking number"
    }
    resp = requests.post(f"{BASE_URL}/tracking_numbers/create", json=payload, headers=HEADERS)
    data = resp.json()
    print(f"   Tracking Number Created: {data}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert data["status"] == "success", f"Expected status=success"
    print(f"{GREEN}✅ Tracking Number Create OK{RESET}")
    return data["tracking_number"]["number"]


def test_tracking_number_list():
    """Test: Tracking Number List"""
    print(f"\n{BLUE}TEST: Tracking Number List{RESET}")
    resp = requests.get(f"{BASE_URL}/tracking_numbers/list", headers=HEADERS)
    data = resp.json()
    print(f"   Tracking Numbers: {len(data.get('tracking_numbers', []))} numbers found")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert "tracking_numbers" in data, "Expected tracking_numbers field"
    print(f"{GREEN}✅ Tracking Number List OK{RESET}")


def test_event_ingest(tracking_number):
    """Test: Event Ingestion"""
    print(f"\n{BLUE}TEST: Event Ingestion{RESET}")
    payload = {
        "call_id": f"test_call_{int(datetime.now().timestamp())}",
        "tracking_number": tracking_number,
        "caller_number": "+491234567890",
        "duration_seconds": 120,
        "status": "completed",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": {"test": "value"}
    }
    resp = requests.post(f"{BASE_URL}/events/ingest", json=payload, headers=HEADERS)
    data = resp.json()
    print(f"   Event Ingested: {data}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert data["status"] == "success", f"Expected status=success"
    assert "event_id" in data, "Expected event_id field"
    print(f"{GREEN}✅ Event Ingest OK{RESET}")


def test_stats_summary():
    """Test: Stats Summary"""
    print(f"\n{BLUE}TEST: Stats Summary{RESET}")
    resp = requests.get(f"{BASE_URL}/stats/summary", headers=HEADERS)
    data = resp.json()
    print(f"   Stats: {data}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert "total_calls" in data, "Expected total_calls field"
    assert "avg_duration_seconds" in data, "Expected avg_duration_seconds field"
    print(f"{GREEN}✅ Stats Summary OK{RESET}")


def test_stats_by_campaign(campaign_id):
    """Test: Stats by Campaign"""
    print(f"\n{BLUE}TEST: Stats by Campaign{RESET}")
    resp = requests.get(f"{BASE_URL}/stats/by_campaign?campaign_id={campaign_id}", headers=HEADERS)
    data = resp.json()
    print(f"   Campaign Stats: {data}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert "campaigns" in data, "Expected campaigns field"
    print(f"{GREEN}✅ Stats by Campaign OK{RESET}")


def test_strict_json():
    """Test: Strict JSON Validation (extra='forbid')"""
    print(f"\n{BLUE}TEST: Strict JSON Validation{RESET}")
    payload = {
        "command": "test",
        "params": {},
        "extra_field": "should_fail"  # Not allowed
    }
    resp = requests.post(f"{BASE_URL}/command", json=payload, headers=HEADERS)
    print(f"   Strict JSON: Extra fields korrekt rejected ({resp.status_code})")
    assert resp.status_code == 422, f"Expected 422 (validation error), got {resp.status_code}"
    print(f"{GREEN}✅ Strict JSON OK{RESET}")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  opena10 Test Suite")
    print("=" * 60)

    results = {
        "Health": False,
        "Root": False,
        "Command": False,
        "Campaign Create": False,
        "Campaign List": False,
        "Tracking Number Create": False,
        "Tracking Number List": False,
        "Event Ingest": False,
        "Stats Summary": False,
        "Stats by Campaign": False,
        "Strict JSON": False
    }

    campaign_id = None
    tracking_number = None

    # Test 1: Health
    try:
        test_health()
        results["Health"] = True
    except Exception as e:
        print(f"{RED}❌ Health FAILED: {e}{RESET}")

    # Test 2: Root
    try:
        test_root()
        results["Root"] = True
    except Exception as e:
        print(f"{RED}❌ Root FAILED: {e}{RESET}")

    # Test 3: Command
    try:
        test_command()
        results["Command"] = True
    except Exception as e:
        print(f"{RED}❌ Command FAILED: {e}{RESET}")

    # Test 4: Campaign Create
    try:
        campaign_id = test_campaign_create()
        results["Campaign Create"] = True
    except Exception as e:
        print(f"{RED}❌ Campaign Create FAILED: {e}{RESET}")

    # Test 5: Campaign List
    try:
        test_campaign_list()
        results["Campaign List"] = True
    except Exception as e:
        print(f"{RED}❌ Campaign List FAILED: {e}{RESET}")

    # Test 6: Tracking Number Create (needs campaign_id)
    if campaign_id:
        try:
            tracking_number = test_tracking_number_create(campaign_id)
            results["Tracking Number Create"] = True
        except Exception as e:
            print(f"{RED}❌ Tracking Number Create FAILED: {e}{RESET}")

    # Test 7: Tracking Number List
    try:
        test_tracking_number_list()
        results["Tracking Number List"] = True
    except Exception as e:
        print(f"{RED}❌ Tracking Number List FAILED: {e}{RESET}")

    # Test 8: Event Ingest (needs tracking_number)
    if tracking_number:
        try:
            test_event_ingest(tracking_number)
            results["Event Ingest"] = True
        except Exception as e:
            print(f"{RED}❌ Event Ingest FAILED: {e}{RESET}")

    # Test 9: Stats Summary
    try:
        test_stats_summary()
        results["Stats Summary"] = True
    except Exception as e:
        print(f"{RED}❌ Stats Summary FAILED: {e}{RESET}")

    # Test 10: Stats by Campaign (needs campaign_id)
    if campaign_id:
        try:
            test_stats_by_campaign(campaign_id)
            results["Stats by Campaign"] = True
        except Exception as e:
            print(f"{RED}❌ Stats by Campaign FAILED: {e}{RESET}")

    # Test 11: Strict JSON
    try:
        test_strict_json()
        results["Strict JSON"] = True
    except Exception as e:
        print(f"{RED}❌ Strict JSON FAILED: {e}{RESET}")

    # ──────────────────────────────────────────────────────────────────────────
    # SUMMARY
    # ──────────────────────────────────────────────────────────────────────────

    print("\n" + "=" * 60)
    print("ERGEBNISSE")
    print("=" * 60)

    for test_name, passed in results.items():
        status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
        print(f"{test_name:30s} {status}")

    passed_count = sum(results.values())
    total_count = len(results)

    print(f"\nTests bestanden: {passed_count}/{total_count}")

    if passed_count == total_count:
        print(f"{GREEN}✅ Alle Tests erfolgreich!{RESET}")
        sys.exit(0)
    else:
        print(f"{RED}❌ {total_count - passed_count} Test(s) fehlgeschlagen{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
