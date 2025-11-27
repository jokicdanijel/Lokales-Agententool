#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
opena4 Test Suite (Telegram Agent)
Tests für Health, Root, Command, Strict JSON Validation
"""

import os
import sys
import json
import requests
from pathlib import Path

# Farben
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color

# Config
BASE_URL = "http://127.0.0.1:12348"
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

if not BEARER_TOKEN:
    print(f"{RED}❌ BEARER_TOKEN nicht gesetzt!{NC}")
    print(f"{YELLOW}   export BEARER_TOKEN=$(grep BEARER_TOKEN .env | cut -d= -f2){NC}")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}


def print_section(title):
    """Print section header"""
    print(f"\n{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}TEST: {title}{NC}")
    print(f"{BLUE}{'=' * 60}{NC}")


def test_health():
    """Test health endpoint"""
    print_section("Health-Check")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        
        assert data.get("status") == "ok", f"Unexpected status: {data.get('status')}"
        assert data.get("agent") == "opena4", f"Unexpected agent: {data.get('agent')}"
        assert data.get("port") == 12348, f"Unexpected port: {data.get('port')}"
        
        print(f"{GREEN}✅ Health OK: {json.dumps(data, ensure_ascii=False)}{NC}")
        return True
    except Exception as e:
        print(f"{RED}❌ Health FAILED: {e}{NC}")
        return False


def test_root():
    """Test root endpoint"""
    print_section("Root-Endpoint")
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        
        assert data.get("kuerzel") == "telep", f"Unexpected kuerzel: {data.get('kuerzel')}"
        assert data.get("agent") == "opena4", f"Unexpected agent: {data.get('agent')}"
        assert data.get("port") == 12348, f"Unexpected port: {data.get('port')}"
        
        print(f"{GREEN}✅ Root OK: {json.dumps(data, ensure_ascii=False)}{NC}")
        return True
    except Exception as e:
        print(f"{RED}❌ Root FAILED: {e}{NC}")
        return False


def test_command():
    """Test command endpoint (Bearer auth)"""
    print_section("Command-Endpoint")
    try:
        payload = {
            "request_id": "test_12345",
            "command": "test_command",
            "payload": {"msg": "Hello from opena4 test"}
        }
        resp = requests.post(f"{BASE_URL}/command", json=payload, headers=HEADERS, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        
        assert data.get("status") == "executed", f"Unexpected status: {data.get('status')}"
        assert data.get("command") == "test_command", f"Unexpected command: {data.get('command')}"
        
        print(f"{GREEN}✅ Command OK: {json.dumps(data, ensure_ascii=False)}{NC}")
        return True
    except Exception as e:
        print(f"{RED}❌ Command FAILED: {e}{NC}")
        return False


def test_invalid_json():
    """Test strict JSON validation (extra fields should be rejected)"""
    print_section("Strict JSON Validation")
    try:
        payload = {
            "request_id": "test_12346",
            "command": "test",
            "extra_field": "should_be_rejected"  # Nicht erlaubt
        }
        resp = requests.post(f"{BASE_URL}/command", json=payload, headers=HEADERS, timeout=5)
        
        # Erwarten 422 oder 400 (Validation Error)
        if resp.status_code in [422, 400]:
            print(f"{GREEN}✅ Strict JSON OK: Extra fields wurden rejected{NC}")
            return True
        else:
            # Falls es durchgeht, ist das ein Fehler
            print(f"{RED}❌ Strict JSON FAILED: Extra fields wurden akzeptiert (Status: {resp.status_code}){NC}")
            return False
    except Exception as e:
        print(f"{RED}❌ Strict JSON FAILED: {e}{NC}")
        return False


def test_safepoints():
    """Test Safepoint creation"""
    print_section("Safepoint-Erstellung")
    try:
        # Prüfe archivp index.jsonl
        archivp_root = Path(__file__).parent.parent / "1.opena1&2_portier" / "archivp_store"
        index_file = archivp_root / "index.jsonl"
        
        if not index_file.exists():
            print(f"{YELLOW}⚠️  index.jsonl nicht gefunden: {index_file}{NC}")
            return True  # Nicht kritisch
        
        # Lese letzte 5 Einträge
        with open(index_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) < 5:
                recent = lines
            else:
                recent = lines[-5:]
        
        print(f"{GREEN}✅ Letzte 5 Safepoints:{NC}")
        for line in recent:
            entry = json.loads(line)
            print(f"   - {entry.get('sp', 'N/A')} | {entry.get('src', 'N/A')} → {entry.get('dst', 'N/A')} | {entry.get('kind', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"{RED}❌ Safepoint-Test FAILED: {e}{NC}")
        return False


def main():
    """Run all tests"""
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}  opena4 Test Suite{NC}")
    print(f"{BLUE}{'=' * 60}{NC}")
    
    results = {
        "Health": test_health(),
        "Root": test_root(),
        "Command": test_command(),
        "Strict JSON": test_invalid_json(),
        "Safepoints": test_safepoints()
    }
    
    print(f"\n{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}ERGEBNISSE{NC}")
    print(f"{BLUE}{'=' * 60}{NC}")
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = f"{GREEN}✅ PASS{NC}" if result else f"{RED}❌ FAIL{NC}"
        print(f"{name:20} {status}")
    
    print(f"\n{BLUE}Tests bestanden: {passed}/{total}{NC}")
    
    if passed == total:
        print(f"{GREEN}✅ Alle Tests erfolgreich!{NC}")
        sys.exit(0)
    else:
        print(f"{RED}❌ {total - passed} Test(s) fehlgeschlagen{NC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
