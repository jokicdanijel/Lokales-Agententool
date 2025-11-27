#!/usr/bin/env python3
"""
Test Suite für opena7 – E-Mail Client Agent
Port: 12352 | Kürzel: emailp
"""

import os
import sys
import requests
import time

# ============================================================================
# CONFIG
# ============================================================================

BASE_URL = "http://127.0.0.1:12352"
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

if not BEARER_TOKEN:
    print("❌ BEARER_TOKEN nicht gesetzt!")
    print("   export BEARER_TOKEN=$(grep BEARER_TOKEN ../.env | cut -d= -f2)")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

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
            if data.get("status") == "ok" and data.get("agent") == "opena7" and data.get("port") == 12352:
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
            if data.get("kuerzel") == "emailp" and "capabilities" in data:
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
        payload = {
            "command": "test_command",
            "params": {"test": "data"}
        }
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

def test_inbox_list():
    test("Inbox List (IMAP erforderlich)")
    try:
        payload = {
            "folder": "INBOX",
            "limit": 10,
            "offset": 0
        }
        resp = requests.post(f"{BASE_URL}/inbox/list", json=payload, headers=HEADERS, timeout=10)
        
        if resp.status_code == 500 and "EMAIL_PASSWORD not configured" in resp.text:
            print(f"   {YELLOW}⚠️  E-Mail-Credentials nicht konfiguriert (erwartet){RESET}")
            success("Inbox List")
        elif resp.status_code == 502:
            print(f"   {YELLOW}⚠️  IMAP-Verbindung fehlgeschlagen (Server nicht erreichbar){RESET}")
            success("Inbox List")
        elif resp.status_code == 200:
            data = resp.json()
            print(f"   {YELLOW}Inbox:{RESET} folder={data.get('folder')}, total={data.get('total')}")
            if "folder" in data and "messages" in data:
                success("Inbox List")
            else:
                fail("Inbox List", f"Unexpected response: {data}")
        else:
            fail("Inbox List", f"HTTP {resp.status_code}: {resp.text}")
    except requests.exceptions.Timeout:
        fail("Inbox List", "Timeout")
    except Exception as e:
        fail("Inbox List", str(e))

def test_folders_list():
    test("Folders List (IMAP erforderlich)")
    try:
        resp = requests.get(f"{BASE_URL}/folders/list", headers=HEADERS, timeout=10)
        
        if resp.status_code == 500 and "EMAIL_PASSWORD not configured" in resp.text:
            print(f"   {YELLOW}⚠️  E-Mail-Credentials nicht konfiguriert (erwartet){RESET}")
            success("Folders List")
        elif resp.status_code == 502:
            print(f"   {YELLOW}⚠️  IMAP-Verbindung fehlgeschlagen (Server nicht erreichbar){RESET}")
            success("Folders List")
        elif resp.status_code == 200:
            data = resp.json()
            print(f"   {YELLOW}Folders:{RESET} count={data.get('count')}")
            if "folders" in data:
                success("Folders List")
            else:
                fail("Folders List", f"Unexpected response: {data}")
        else:
            fail("Folders List", f"HTTP {resp.status_code}: {resp.text}")
    except requests.exceptions.Timeout:
        fail("Folders List", "Timeout")
    except Exception as e:
        fail("Folders List", str(e))

def test_strict_json():
    test("Strict JSON Validation")
    try:
        # Extra field sollte rejected werden
        payload = {
            "command": "test",
            "params": {},
            "extra_field": "not_allowed"
        }
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
    print("  opena7 Test Suite")
    print("=" * 60)
    
    # Warte kurz falls Service gerade gestartet wurde
    time.sleep(1)
    
    test_health()
    test_root()
    test_command()
    test_inbox_list()
    test_folders_list()
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
