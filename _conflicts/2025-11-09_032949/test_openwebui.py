#!/usr/bin/env python3
"""
scripts/test_openwebui.py – Test für OpenWebUI Agent (opena3)

Testet:
- GET /health
- POST /command mit Beispiel-Prompt
- Token-Authentifizierung aus .env
"""

import json
import os
import sys
from pathlib import Path

import requests

# ============================================================================
# KONFIGURATION
# ============================================================================
AGENT_URL = "http://127.0.0.1:12347"
AGENT_HEALTH_ENDPOINT = f"{AGENT_URL}/health"
AGENT_COMMAND_ENDPOINT = f"{AGENT_URL}/command"
ENV_PATH = Path(__file__).parent.parent / ".env"
TIMEOUT = 10

# Farben für Terminal-Output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def _print(msg: str, color: str = RESET):
    """Print mit Farbe"""
    print(f"{color}{msg}{RESET}")


def read_token() -> str:
    """Lese Token aus .env"""
    if not ENV_PATH.exists():
        _print(f"❌ .env nicht gefunden: {ENV_PATH}", RED)
        sys.exit(1)

    with open(ENV_PATH, "r") as f:
        for line in f:
            if line.startswith("DASHBOARD_ADMIN_TOKEN="):
                return line.split("=", 1)[1].strip()

    _print("❌ DASHBOARD_ADMIN_TOKEN nicht in .env gefunden", RED)
    sys.exit(1)


def test_health(token: str):
    """Teste GET /health"""
    _print("\n[TEST 1] GET /health", BLUE)
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(AGENT_HEALTH_ENDPOINT, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        _print(f"✅ Status: {resp.status_code}", GREEN)
        _print(f"   Service: {data.get('service')}", BLUE)
        _print(f"   Status: {data.get('status')}", BLUE)
        _print(f"   Timestamp: {data.get('ts')}", BLUE)
        return True
    except requests.ConnectionError as e:
        _print(f"❌ Verbindungsfehler: {e}", RED)
        return False
    except requests.Timeout:
        _print(f"❌ Timeout nach {TIMEOUT}s", RED)
        return False
    except Exception as e:
        _print(f"❌ Fehler: {e}", RED)
        return False


def test_command(token: str):
    """Teste POST /command mit Beispiel-Prompt"""
    _print("\n[TEST 2] POST /command", BLUE)

    payload = {
        "prompt": "Hello, how are you?",
        "context": {},
        "model": None
    }

    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        resp = requests.post(
            AGENT_COMMAND_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()
        _print(f"✅ Status: {resp.status_code}", GREEN)
        _print(f"   Prompt: {payload['prompt']}", BLUE)
        _print(f"   Response-Text: {data.get('text', 'N/A')[:100]}...", BLUE)
        _print(f"   Timestamp: {data.get('ts')}", BLUE)
        return True
    except requests.ConnectionError as e:
        _print(f"❌ Verbindungsfehler: {e}", RED)
        _print("   Hinweis: Ist der Agent gestartet? (bin/start_opena3.sh)", YELLOW)
        return False
    except requests.Timeout:
        _print(f"❌ Timeout nach {TIMEOUT}s", RED)
        _print("   Hinweis: OpenWebUI antwortet nicht? Prüfe http://127.0.0.1:8080", YELLOW)
        return False
    except requests.HTTPError as e:
        _print(f"❌ HTTP-Fehler {e.response.status_code}", RED)
        _print(f"   Response: {e.response.text}", RED)
        return False
    except Exception as e:
        _print(f"❌ Fehler: {e}", RED)
        return False


def main():
    """Hauptfunktion"""
    _print("=" * 80, BLUE)
    _print("OpenWebUI Agent Test Suite", BLUE)
    _print("=" * 80, BLUE)

    # Token lesen
    _print("\n[SETUP] Token aus .env lesen...", BLUE)
    token = read_token()
    _print(f"✅ Token gefunden: {token[:20]}...", GREEN)

    # Tests durchführen
    health_ok = test_health(token)
    command_ok = test_command(token)

    # Zusammenfassung
    _print("\n" + "=" * 80, BLUE)
    if health_ok and command_ok:
        _print("✅ ALLE TESTS ERFOLGREICH", GREEN)
        _print("=" * 80, BLUE)
        return 0
    else:
        _print("❌ EINIGE TESTS FEHLGESCHLAGEN", RED)
        _print("=" * 80, BLUE)
        if not health_ok:
            _print("\nTroubleshooting für Health-Check:", YELLOW)
            _print("- Ist der Agent gestartet? (bin/start_opena3.sh)", YELLOW)
            _print("- Port 12347 erreichbar? (netstat -ln | grep 12347)", YELLOW)
        if not command_ok:
            _print("\nTroubleshooting für Command-Test:", YELLOW)
            _print("- Läuft OpenWebUI? (docker-compose up -d in 2.openwebui/)", YELLOW)
            _print("- Health-Check erfolgreich? (curl http://127.0.0.1:8080/health)", YELLOW)
            _print("- Token gültig? (cat .env | grep DASHBOARD_ADMIN_TOKEN)", YELLOW)
        return 1


if __name__ == "__main__":
    sys.exit(main())
