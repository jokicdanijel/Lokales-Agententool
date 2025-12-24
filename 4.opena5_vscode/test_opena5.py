#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
opena5 Test Suite (VS Code Agent)
Tests für Health, Root, Command, File-Operations, Search
"""

import json
import os
import sys
from pathlib import Path

import requests

# Farben
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"

BASE_URL = "http://127.0.0.1:12350"
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

if not BEARER_TOKEN:
    print(f"{RED}❌ BEARER_TOKEN nicht gesetzt!{NC}")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}", "Content-Type": "application/json"}


def print_section(title):
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

        assert data.get("status") == "ok"
        assert data.get("agent") == "opena5"
        assert data.get("port") == 12350

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

        assert data.get("kuerzel") == "vscop"
        assert data.get("agent") == "opena5"
        assert data.get("port") == 12350

        print(f"{GREEN}✅ Root OK: {json.dumps(data, ensure_ascii=False)}{NC}")
        return True
    except Exception as e:
        print(f"{RED}❌ Root FAILED: {e}{NC}")
        return False


def test_command():
    """Test command endpoint"""
    print_section("Command-Endpoint")
    try:
        payload = {"request_id": "test_cmd_001", "command": "test_command", "payload": {"test": "data"}}
        resp = requests.post(f"{BASE_URL}/command", json=payload, headers=HEADERS, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        assert data.get("status") == "executed"
        assert data.get("command") == "test_command"

        print(f"{GREEN}✅ Command OK: {json.dumps(data, ensure_ascii=False)}{NC}")
        return True
    except Exception as e:
        print(f"{RED}❌ Command FAILED: {e}{NC}")
        return False


def test_workspace_list():
    """Test workspace list"""
    print_section("Workspace-List")
    try:
        resp = requests.get(f"{BASE_URL}/workspace/list", headers=HEADERS, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        assert data.get("status") == "success"
        assert "items" in data

        print(f"{GREEN}✅ Workspace List OK: {data.get('count', 0)} items{NC}")
        return True
    except Exception as e:
        print(f"{RED}❌ Workspace List FAILED: {e}{NC}")
        return False


def test_strict_json():
    """Test strict JSON validation"""
    print_section("Strict JSON Validation")
    try:
        payload = {
            "request_id": "test_002",
            "command": "test",
            "payload": {},
            "extra_field": "should_reject",  # Nicht erlaubt
        }
        resp = requests.post(f"{BASE_URL}/command", json=payload, headers=HEADERS, timeout=5)

        if resp.status_code in [422, 400]:
            print(f"{GREEN}✅ Strict JSON OK: Extra fields rejected{NC}")
            return True
        else:
            print(f"{RED}❌ Strict JSON FAILED: Extra fields akzeptiert (Status: {resp.status_code}){NC}")
            return False
    except Exception as e:
        print(f"{RED}❌ Strict JSON FAILED: {e}{NC}")
        return False


def main():
    """Run all tests"""
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}  opena5 Test Suite{NC}")
    print(f"{BLUE}{'=' * 60}{NC}")

    results = {
        "Health": test_health(),
        "Root": test_root(),
        "Command": test_command(),
        "Workspace List": test_workspace_list(),
        "Strict JSON": test_strict_json(),
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
