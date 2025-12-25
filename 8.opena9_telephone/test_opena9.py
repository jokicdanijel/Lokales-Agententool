#!/usr/bin/env python3
"""
Test Suite für opena9 – Telefonie Agent (Twilio)
Port: 12354 | Kürzel: telphonep
"""

import os
import sys
import time

import requests

# ============================================================================
# CONFIG
# ============================================================================

BASE_URL = "http://127.0.0.1:12354"
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
            if data.get("status") == "ok" and data.get("agent") == "opena9" and data.get("port") == 12354:
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
            if data.get("kuerzel") == "telphonep" and "capabilities" in data:
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


def test_call_start():
    test("Call Start (Twilio erforderlich)")
    try:
        payload = {"to": "+491234567890", "timeout": 30}
        resp = requests.post(f"{BASE_URL}/call/start", json=payload, headers=HEADERS, timeout=10)

        if resp.status_code == 500 and ("TWILIO_ACCOUNT_SID" in resp.text or "TWILIO_AUTH_TOKEN" in resp.text):
            print(f"   {YELLOW}⚠️  Twilio-Credentials nicht konfiguriert (erwartet){RESET}")
            success("Call Start")
        elif resp.status_code == 400:
            print(f"   {YELLOW}⚠️  Ungültige Nummer (erwartet ohne echte API){RESET}")
            success("Call Start")
        elif resp.status_code == 502:
            print(f"   {YELLOW}⚠️  Twilio API nicht erreichbar (Server-Fehler){RESET}")
            success("Call Start")
        elif resp.status_code == 200:
            data = resp.json()
            print(f"   {YELLOW}Call Start:{RESET} status={data.get('status')}, call_id={data.get('call_id')}")
            if "call_id" in data:
                success("Call Start")
            else:
                fail("Call Start", f"Unexpected response: {data}")
        else:
            fail("Call Start", f"HTTP {resp.status_code}: {resp.text}")
    except requests.exceptions.Timeout:
        fail("Call Start", "Timeout")
    except Exception as e:
        fail("Call Start", str(e))


def test_call_hangup():
    test("Call Hangup (Dummy Call ID)")
    try:
        payload = {"call_id": "CA00000000000000000000000000000000"}
        resp = requests.post(f"{BASE_URL}/call/hangup", json=payload, headers=HEADERS, timeout=10)

        if resp.status_code == 500 and "Twilio credentials" in resp.text:
            print(f"   {YELLOW}⚠️  Twilio-Credentials nicht konfiguriert (erwartet){RESET}")
            success("Call Hangup")
        elif resp.status_code == 404:
            print(f"   {YELLOW}⚠️  Call nicht gefunden (erwartet mit Dummy-ID){RESET}")
            success("Call Hangup")
        elif resp.status_code == 502:
            print(f"   {YELLOW}⚠️  Twilio API nicht erreichbar (Server-Fehler){RESET}")
            success("Call Hangup")
        elif resp.status_code == 200:
            data = resp.json()
            print(f"   {YELLOW}Call Hangup:{RESET} status={data.get('status')}")
            success("Call Hangup")
        else:
            fail("Call Hangup", f"HTTP {resp.status_code}: {resp.text}")
    except requests.exceptions.Timeout:
        fail("Call Hangup", "Timeout")
    except Exception as e:
        fail("Call Hangup", str(e))


def test_call_status():
    test("Call Status (Dummy Call ID)")
    try:
        call_id = "CA00000000000000000000000000000000"
        resp = requests.get(f"{BASE_URL}/call/status/{call_id}", headers=HEADERS, timeout=10)

        if resp.status_code == 500 and "Twilio credentials" in resp.text:
            print(f"   {YELLOW}⚠️  Twilio-Credentials nicht konfiguriert (erwartet){RESET}")
            success("Call Status")
        elif resp.status_code == 404:
            print(f"   {YELLOW}⚠️  Call nicht gefunden (erwartet mit Dummy-ID){RESET}")
            success("Call Status")
        elif resp.status_code == 502:
            print(f"   {YELLOW}⚠️  Twilio API nicht erreichbar (Server-Fehler){RESET}")
            success("Call Status")
        elif resp.status_code == 200:
            data = resp.json()
            print(f"   {YELLOW}Call Status:{RESET} status={data.get('status')}")
            success("Call Status")
        else:
            fail("Call Status", f"HTTP {resp.status_code}: {resp.text}")
    except requests.exceptions.Timeout:
        fail("Call Status", "Timeout")
    except Exception as e:
        fail("Call Status", str(e))


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
    print("  opena9 Test Suite")
    print("=" * 60)

    # Warte kurz falls Service gerade gestartet wurde
    time.sleep(1)

    test_health()
    test_root()
    test_command()
    test_call_start()
    test_call_hangup()
    test_call_status()
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
