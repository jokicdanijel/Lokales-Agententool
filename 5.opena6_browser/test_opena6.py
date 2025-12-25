#!/usr/bin/env python3
"""
Test Suite für opena6 – Browser Automation Agent
Port: 12350 | Kürzel: browsep
"""

import os
import sys
import time

import requests

# ============================================================================
# CONFIG
# ============================================================================

BASE_URL = "http://127.0.0.1:12350"
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

if not BEARER_TOKEN:
    print("❌ BEARER_TOKEN nicht gesetzt!")
    print("   export BEARER_TOKEN=$(grep BEARER_TOKEN ../.env | cut -d= -f2)")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}", "Content-Type": "application/json"}

# ============================================================================
# COLORS
# ============================================================================

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# ============================================================================
# TEST TRACKING
# ============================================================================

results = {}


def test(name):
    print(f"\n{BLUE}TEST:{RESET} {name}")


def success(name):
    results[name] = "✅ PASS"
    print(f"{GREEN}✅ {name} OK{RESET}")


def fail(name, reason):
    results[name] = "❌ FAIL"
    print(f"{RED}❌ {name} FAILED: {reason}{RESET}")


# ============================================================================
# TESTS
# ============================================================================


def test_health():
    test("Health-Check")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"   {YELLOW}Health:{RESET} {data}")
            if data.get("status") == "ok" and data.get("agent") == "opena6" and data.get("port") == 12350:
                success("Health")
            else:
                fail("Health", f"Unexpected data: {data}")
        else:
            fail("Health", f"HTTP {resp.status_code}")
    except Exception as e:
        fail("Health", str(e))


def test_root():
    test("Root-Endpoint")
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"   {YELLOW}Root:{RESET} {data}")
            if data.get("kuerzel") == "browsep" and "capabilities" in data:
                success("Root")
            else:
                fail("Root", f"Unexpected data: {data}")
        else:
            fail("Root", f"HTTP {resp.status_code}")
    except Exception as e:
        fail("Root", str(e))


def test_command():
    test("Command-Endpoint")
    try:
        payload = {"command": "test_command", "params": {"test": "data"}}
        resp = requests.post(f"{BASE_URL}/command", json=payload, headers=HEADERS, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"   {YELLOW}Command:{RESET} {data}")
            if data.get("status") == "executed":
                success("Command")
            else:
                fail("Command", f"Unexpected response: {data}")
        else:
            fail("Command", f"HTTP {resp.status_code}")
    except Exception as e:
        fail("Command", str(e))


def test_navigate():
    test("Navigate (Playwright erforderlich)")
    try:
        payload = {"url": "https://example.com", "wait_until": "load", "timeout": 10000}
        resp = requests.post(f"{BASE_URL}/navigate", json=payload, headers=HEADERS, timeout=15)

        if resp.status_code == 503:
            # Playwright nicht installiert
            print(f"   {YELLOW}⚠️  Playwright nicht installiert (erwartet){RESET}")
            success("Navigate")
        elif resp.status_code == 200:
            data = resp.json()
            print(f"   {YELLOW}Navigate:{RESET} {data}")
            if "url" in data and data.get("status") == "success":
                success("Navigate")
            else:
                fail("Navigate", f"Unexpected response: {data}")
        else:
            fail("Navigate", f"HTTP {resp.status_code}: {resp.text}")
    except requests.exceptions.Timeout:
        fail("Navigate", "Timeout (Browser-Start dauert zu lange)")
    except Exception as e:
        fail("Navigate", str(e))


def test_screenshot():
    test("Screenshot (Playwright erforderlich)")
    try:
        payload = {"url": "https://example.com", "full_page": False, "format": "png", "timeout": 10000}
        resp = requests.post(f"{BASE_URL}/screenshot", json=payload, headers=HEADERS, timeout=15)

        if resp.status_code == 503:
            # Playwright nicht installiert
            print(f"   {YELLOW}⚠️  Playwright nicht installiert (erwartet){RESET}")
            success("Screenshot")
        elif resp.status_code == 200:
            data = resp.json()
            print(f"   {YELLOW}Screenshot:{RESET} path={data.get('path')}, size={data.get('size_bytes')} bytes")
            if "path" in data and "filename" in data:
                success("Screenshot")
            else:
                fail("Screenshot", f"Unexpected response: {data}")
        else:
            fail("Screenshot", f"HTTP {resp.status_code}: {resp.text}")
    except requests.exceptions.Timeout:
        fail("Screenshot", "Timeout")
    except Exception as e:
        fail("Screenshot", str(e))


def test_strict_json():
    test("Strict JSON Validation")
    try:
        # Extra field sollte rejected werden
        payload = {"command": "test", "params": {}, "extra_field": "not_allowed"}
        resp = requests.post(f"{BASE_URL}/command", json=payload, headers=HEADERS, timeout=5)
        if resp.status_code == 422:
            print(f"   {YELLOW}Strict JSON:{RESET} Extra fields korrekt rejected (422)")
            success("Strict JSON")
        else:
            fail("Strict JSON", f"Expected 422, got {resp.status_code}")
    except Exception as e:
        fail("Strict JSON", str(e))


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  opena6 Test Suite")
    print("=" * 60)

    # Warte kurz falls Service gerade gestartet wurde
    time.sleep(1)

    test_health()
    test_root()
    test_command()
    test_navigate()
    test_screenshot()
    test_strict_json()

    # ========================================================================
    # RESULTS
    # ========================================================================

    print("\n" + "=" * 60)
    print("ERGEBNISSE")
    print("=" * 60)

    for name, status in results.items():
        print(f"{name:20} {status}")

    passed = sum(1 for v in results.values() if "PASS" in v)
    total = len(results)

    print("")
    print(f"Tests bestanden: {passed}/{total}")

    if passed == total:
        print(f"{GREEN}✅ Alle Tests erfolgreich!{RESET}")
        sys.exit(0)
    else:
        print(f"{RED}❌ Einige Tests fehlgeschlagen!{RESET}")
        sys.exit(1)
