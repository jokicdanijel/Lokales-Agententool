#!/usr/bin/env python3
"""Test-Script für OpenWebUI-Agent (opena3)"""

import json
import urllib.request
import sys
import os

BASE = "http://127.0.0.1:12347"
OPENWEBUI_BASE = "http://127.0.0.1:8080"

def test_health():
    """Teste Health-Endpunkt"""
    print("\n📋 Teste /health...")
    try:
        with urllib.request.urlopen(f"{BASE}/health") as r:
            result = json.loads(r.read().decode())
            print(f"✓ Health OK: {result}")
            return result.get("status") == "ok"
    except Exception as e:
        print(f"✗ Health FEHLER: {e}")
        return False


def test_command():
    """Teste Command-Endpunkt"""
    print("\n💬 Teste POST /command...")
    try:
        payload = {
            "prompt": "Hello, how are you?",
            "context": {}
        }
        req = urllib.request.Request(
            f"{BASE}/command",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            result = json.loads(r.read().decode())
            print(f"✓ Command OK: {json.dumps(result, indent=2)}")
            return True
    except urllib.error.HTTPError as e:
        if e.code == 502:
            print(f"⚠ OpenWebUI nicht erreichbar (502). Bitte starten Sie OpenWebUI auf Port 8080")
            return False
        print(f"✗ Command FEHLER ({e.code}): {e.read().decode()}")
        return False
    except Exception as e:
        print(f"✗ Command FEHLER: {e}")
        return False


def test_openwebui_health():
    """Teste OpenWebUI Health"""
    print("\n🔍 Prüfe OpenWebUI Health...")
    try:
        with urllib.request.urlopen(f"{OPENWEBUI_BASE}/health", timeout=5) as r:
            result = json.loads(r.read().decode())
            print(f"✓ OpenWebUI OK: {result}")
            return True
    except Exception as e:
        print(f"⚠ OpenWebUI nicht erreichbar: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("OpenWebUI Agent Test")
    print("=" * 60)
    
    # Erst prüfen, ob OpenWebUI läuft
    if not test_openwebui_health():
        print("\n⚠ WARNUNG: OpenWebUI läuft nicht auf Port 8080")
        print("  → Starten Sie OpenWebUI zuerst (z.B. in 2.openwebui/)")
    
    # Tests für Agent
    health_ok = test_health()
    
    if health_ok:
        command_ok = test_command()
        if command_ok:
            print("\n✅ Alle Tests bestanden!")
            sys.exit(0)
    
    print("\n❌ Einige Tests fehlgeschlagen")
    sys.exit(1)
