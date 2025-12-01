#!/usr/bin/env python3
"""
opena3 Test Suite
Testet Health, Command, Invoke-Endpoints
"""

import requests
import json
import time
import os
import sys
from pathlib import Path

# Farben
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

BASE_URL = "http://127.0.0.1:12347"
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

def print_test(name: str):
    print(f"\n{YELLOW}{'=' * 60}{NC}")
    print(f"{YELLOW}TEST: {name}{NC}")
    print(f"{YELLOW}{'=' * 60}{NC}")

def print_success(msg: str):
    print(f"{GREEN}✅ {msg}{NC}")

def print_error(msg: str):
    print(f"{RED}❌ {msg}{NC}")

def test_health():
    """Test Health-Endpoint"""
    print_test("Health-Check")
    
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if resp.status_code == 200:
            data = resp.json()
            print_success(f"Health OK: {json.dumps(data, indent=2)}")
            assert data["agent"] == "opena3"
            assert data["port"] == 12347
            assert data["status"] == "ok"
            return True
        else:
            print_error(f"Health fehlgeschlagen: {resp.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Health-Fehler: {e}")
        return False

def test_root():
    """Test Root-Endpoint"""
    print_test("Root-Endpoint")
    
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        
        if resp.status_code == 200:
            data = resp.json()
            print_success(f"Root OK: {json.dumps(data, indent=2)}")
            assert data["agent"] == "opena3"
            assert data["kuerzel"] == "owuip"
            return True
        else:
            print_error(f"Root fehlgeschlagen: {resp.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Root-Fehler: {e}")
        return False

def test_command():
    """Test Command-Endpoint"""
    print_test("Command-Endpoint")
    
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"} if BEARER_TOKEN else {}
    
    payload = {
        "command": "test_command",
        "context": {"test": "data"},
        "timeout": 10
    }
    
    try:
        resp = requests.post(
            f"{BASE_URL}/command",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print_success(f"Command OK: {json.dumps(data, indent=2)}")
            assert data["status"] == "executed"
            assert data["command"] == "test_command"
            return True
        elif resp.status_code == 401:
            print_error("Auth fehlgeschlagen (BEARER_TOKEN falsch oder fehlend)")
            return False
        else:
            print_error(f"Command fehlgeschlagen: {resp.status_code} - {resp.text}")
            return False
            
    except Exception as e:
        print_error(f"Command-Fehler: {e}")
        return False

def test_invalid_json():
    """Test Strict JSON (extra fields sollten rejected werden)"""
    print_test("Strict JSON Validation")
    
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"} if BEARER_TOKEN else {}
    
    # Payload mit extra field (sollte rejected werden)
    payload = {
        "command": "test",
        "extra_field": "should_be_rejected"
    }
    
    try:
        resp = requests.post(
            f"{BASE_URL}/command",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if resp.status_code == 422:
            print_success("Strict JSON OK: Extra fields wurden rejected")
            return True
        else:
            print_error(f"Strict JSON fehlgeschlagen: {resp.status_code} (erwartet 422)")
            return False
            
    except Exception as e:
        print_error(f"Strict JSON-Fehler: {e}")
        return False

def test_safepoints():
    """Prüfe ob Safepoints erstellt wurden"""
    print_test("Safepoint-Erstellung")
    
    archive_dir = Path("../1.opena1&2_portier/archivp_store")
    index_file = archive_dir / "index.jsonl"
    
    if not index_file.exists():
        print_error(f"Index-File nicht gefunden: {index_file}")
        return False
    
    # Lies letzte 5 Einträge
    with index_file.open("r") as f:
        lines = f.readlines()
        recent = lines[-5:] if len(lines) >= 5 else lines
    
    print_success(f"Letzte {len(recent)} Safepoints:")
    for line in recent:
        entry = json.loads(line)
        print(f"  - {entry['sp_id']} | {entry['src']}→{entry['dst']} | {entry['type']}")
    
    # Prüfe ob opena3-Safepoints vorhanden
    opena3_sps = [json.loads(line) for line in recent if "opena3" in line]
    
    if opena3_sps:
        print_success(f"✅ {len(opena3_sps)} opena3-Safepoints gefunden")
        return True
    else:
        print_error("Keine opena3-Safepoints gefunden")
        return False

def main():
    """Führe alle Tests aus"""
    print(f"{GREEN}{'=' * 60}{NC}")
    print(f"{GREEN}  opena3 Test Suite{NC}")
    print(f"{GREEN}{'=' * 60}{NC}")
    
    if not BEARER_TOKEN:
        print(f"{YELLOW}⚠️  BEARER_TOKEN nicht gesetzt, Auth-Tests werden übersprungen{NC}")
    
    results = []
    
    # Tests ausführen
    results.append(("Health-Check", test_health()))
    time.sleep(0.5)
    
    results.append(("Root-Endpoint", test_root()))
    time.sleep(0.5)
    
    if BEARER_TOKEN:
        results.append(("Command-Endpoint", test_command()))
        time.sleep(0.5)
        
        results.append(("Strict JSON", test_invalid_json()))
        time.sleep(0.5)
        
        results.append(("Safepoints", test_safepoints()))
    
    # Zusammenfassung
    print(f"\n{GREEN}{'=' * 60}{NC}")
    print(f"{GREEN}  TEST-ZUSAMMENFASSUNG{NC}")
    print(f"{GREEN}{'=' * 60}{NC}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}✅ PASS{NC}" if result else f"{RED}❌ FAIL{NC}"
        print(f"{status} | {name}")
    
    print(f"\n{GREEN if passed == total else YELLOW}Ergebnis: {passed}/{total} Tests bestanden{NC}")
    
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
