#!/usr/bin/env python3
"""
scripts/seed_openwebui.py

Seed-Script: Sendet Beispiel-Prompts an OpenWebUI-Agent und speichert Antworten 
als Safepoints in der Archivator (opena2).

Verwendung:
    python3 scripts/seed_openwebui.py
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import requests

# ==============================================================================
# KONFIGURATION
# ==============================================================================
DASHBOARD_URL = "http://127.0.0.1:12349"
AGENT_URL = "http://127.0.0.1:12347"
OPENA2_URL = "http://127.0.0.1:12345"  # Archivator

ENV_PATH = Path(".env")
TIMEOUT = 30

# Test-Prompts
TEST_PROMPTS = [
    "What is ELION Hyper-Dashboard?",
    "Explain what Python agents are",
    "How does OpenWebUI integrate with FastAPI?",
    "What are the benefits of distributed systems?",
    "Describe microservices architecture",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def read_token() -> str:
    """Lese Token aus .env"""
    if not ENV_PATH.exists():
        logger.error(f".env nicht gefunden: {ENV_PATH}")
        sys.exit(1)

    with open(ENV_PATH, "r") as f:
        for line in f:
            if line.startswith("DASHBOARD_ADMIN_TOKEN="):
                return line.split("=", 1)[1].strip()

    logger.error("DASHBOARD_ADMIN_TOKEN nicht in .env")
    sys.exit(1)


def send_prompt(token: str, prompt: str) -> dict:
    """Sendet Prompt an OpenWebUI-Agent"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "context": {
            "source": "seed_openwebui.py",
            "timestamp": datetime.utcnow().isoformat()
        }
    }

    try:
        logger.info(f"Sende Prompt: '{prompt[:50]}...'")
        resp = requests.post(
            f"{DASHBOARD_URL}/api/openwebui/chat",
            json=payload,
            headers=headers,
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"Antwort erhalten: {data.get('text', 'N/A')[:50]}...")
        return data
    except requests.Timeout:
        logger.error(f"Timeout bei Prompt: {prompt}")
        return {"error": "Timeout"}
    except requests.HTTPError as e:
        logger.error(f"HTTP-Fehler {e.response.status_code}: {e.response.text}")
        return {"error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        logger.error(f"Fehler: {e}")
        return {"error": str(e)}


def save_safepoint(token: str, prompt: str, response: dict) -> bool:
    """Speichert Response als Safepoint in opena2 (Archivator)"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Safepoint-Payload
    safepoint = {
        "src": "openwebui_seed",
        "dst": "opena2",
        "kind": "RESPONSE",
        "payload": {
            "prompt": prompt,
            "response": response.get("text") or response.get("response"),
            "model": response.get("model"),
            "ts": response.get("ts") or datetime.utcnow().isoformat()
        }
    }

    try:
        logger.info(f"Speichere Safepoint für Prompt: '{prompt[:30]}...'")
        resp = requests.post(
            f"{OPENA2_URL}/store/archivp",
            json=safepoint,
            headers=headers,
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        logger.info(f"✅ Safepoint gespeichert")
        return True
    except Exception as e:
        logger.warning(f"⚠️  Safepoint-Speicherung fehlgeschlagen: {e}")
        return False


def main():
    """Hauptfunktion"""
    logger.info("=" * 80)
    logger.info("OpenWebUI Seed Script")
    logger.info("=" * 80)

    # Token laden
    logger.info("Lese Token aus .env...")
    token = read_token()
    logger.info(f"Token geladen: {token[:20]}...")

    # Sende Prompts
    logger.info(f"\nSende {len(TEST_PROMPTS)} Test-Prompts...")

    successful = 0
    for i, prompt in enumerate(TEST_PROMPTS, 1):
        logger.info(f"\n[{i}/{len(TEST_PROMPTS)}] Verarbeite Prompt...")

        # Sende Prompt
        response = send_prompt(token, prompt)

        if "error" in response:
            logger.warning(f"Fehler bei Prompt {i}: {response['error']}")
            continue

        # Speichere als Safepoint
        if save_safepoint(token, prompt, response):
            successful += 1

    # Zusammenfassung
    logger.info("\n" + "=" * 80)
    logger.info(f"✅ Abgeschlossen: {successful}/{len(TEST_PROMPTS)} erfolgreich")
    logger.info("=" * 80)

    return 0 if successful > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
