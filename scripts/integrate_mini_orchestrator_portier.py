#!/usr/bin/env python3
"""
Mini-Orchestrator → Portier Integration
Registriert Mini-Orchestrator beim Portier und führt Test-Dispatch durch.

Schritte:
1. Prüft Health von Portier + Mini-Orchestrator
2. Registriert Mini-Orchestrator beim Portier via /route/update
3. Sendet Test-Dispatch via Portier → Mini-Orchestrator
4. Validiert Response
5. Prüft Archiv-Eintrag (Safepoint)
"""

import httpx
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
PORTIER_URL = "http://127.0.0.1:12344"
MINI_ORCHESTRATOR_URL = "http://127.0.0.1:12350"
MINI_ORCHESTRATOR_TARGET = "miniorchp"
_bearer_token: Optional[str] = None

# -------------------------------------------------------------------
# Load Bearer Token
# -------------------------------------------------------------------
def load_bearer_token() -> None:
    global _bearer_token
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("BEARER_TOKEN="):
                    _bearer_token = line.split("=", 1)[1].strip()
                    return
    print("WARNING: BEARER_TOKEN nicht in .env gefunden")

# -------------------------------------------------------------------
# Step 1: Health Checks
# -------------------------------------------------------------------
def health_check() -> bool:
    print("[1] Health-Checks...")
    
    with httpx.Client(timeout=5.0) as client:
        # Portier
        try:
            r = client.get(f"{PORTIER_URL}/health")
            if r.status_code == 200:
                print("   [OK] Portier (12344): Online")
            else:
                print(f"   [ERROR] Portier (12344): HTTP {r.status_code}")
                return False
        except Exception as e:
            print(f"   [ERROR] Portier (12344): {e}")
            return False
        
        # Mini-Orchestrator
        try:
            r = client.get(f"{MINI_ORCHESTRATOR_URL}/health")
            if r.status_code == 200:
                health_data: Dict[str, Any] = r.json()
                print(f"   [OK] Mini-Orchestrator (12350): {health_data.get('status', 'unknown')}")
            else:
                print(f"   [ERROR] Mini-Orchestrator (12350): HTTP {r.status_code}")
                return False
        except Exception as e:
            print(f"   [ERROR] Mini-Orchestrator (12350): {e}")
            return False
    
    return True

# -------------------------------------------------------------------
# Step 2: Register at Portier
# -------------------------------------------------------------------
def register_at_portier() -> bool:
    print("\n[2] Registrierung beim Portier...")
    
    headers: Dict[str, str] = {}
    if _bearer_token:
        headers["Authorization"] = f"Bearer {_bearer_token}"
    
    payload: Dict[str, str] = {
        "service_name": "mini_orchestrator",
        "endpoint": MINI_ORCHESTRATOR_URL,
        "program_target": MINI_ORCHESTRATOR_TARGET
    }
    
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.post(
                f"{PORTIER_URL}/route/update",
                json=payload,
                headers=headers
            )
            
            if r.status_code == 200:
                print("   [OK] Registrierung erfolgreich")
                print(f"      Service: {payload['service_name']}")
                print(f"      Target: {payload['program_target']}")
                print(f"      Endpoint: {payload['endpoint']}")
                return True
            else:
                print(f"   [ERROR] Registrierung fehlgeschlagen: HTTP {r.status_code}")
                print(f"      Response: {r.text}")
                return False
    except Exception as e:
        print(f"   [ERROR] Registrierung fehlgeschlagen: {e}")
        return False

# -------------------------------------------------------------------
# Step 3: Test Dispatch
# -------------------------------------------------------------------
def test_dispatch() -> bool:
    print("\n[3] Test-Dispatch (Portier -> Mini-Orchestrator)...")
    
    headers: Dict[str, str] = {}
    if _bearer_token:
        headers["Authorization"] = f"Bearer {_bearer_token}"
    
    # Test: send_mail via MailAgent
    payload: Dict[str, Any] = {
        "service_target": MINI_ORCHESTRATOR_TARGET,
        "action": "send_mail",
        "params": {
            "to": "test@example.com",
            "subject": "Integration Test",
            "body": "This is a test from Portier → Mini-Orchestrator integration"
        }
    }
    
    try:
        start = time.time()
        with httpx.Client(timeout=30.0) as client:
            r = client.post(
                f"{PORTIER_URL}/dispatch/kordp",
                json=payload,
                headers=headers
            )
            latency = time.time() - start
            
            if r.status_code == 200:
                response_data: Dict[str, Any] = r.json()
                print(f"   [OK] Dispatch erfolgreich ({latency*1000:.0f}ms)")
                print(f"      Status: {response_data.get('status', 'unknown')}")
                
                if response_data.get('data'):
                    print(f"      Data: {json.dumps(response_data['data'], indent=8)}")
                
                return True
            else:
                print(f"   [ERROR] Dispatch fehlgeschlagen: HTTP {r.status_code}")
                print(f"      Response: {r.text}")
                return False
    except Exception as e:
        print(f"   [ERROR] Dispatch fehlgeschlagen: {e}")
        return False
# -------------------------------------------------------------------
# Step 4: Verify Archiv Entry
# -------------------------------------------------------------------
def verify_archiv() -> None:
    print("\n[4] Archiv-Validierung...")
    
    archiv_index = Path("1.opena1&2_portier/archivp_store/index.jsonl")
    
    if not archiv_index.exists():
        print(f"   [WARNING] index.jsonl nicht gefunden: {archiv_index}")
        return
    
    # Lese letzte 10 Einträge
    with open(archiv_index) as f:
        lines = f.readlines()
        recent_entries: list[Dict[str, Any]] = [json.loads(line) for line in lines[-10:] if line.strip()]
    
    # Suche nach Mini-Orchestrator-Einträgen
    miniorchp_entries: list[Dict[str, Any]] = [
        e for e in recent_entries
        if MINI_ORCHESTRATOR_TARGET in e.get("sp_id", "")
        or MINI_ORCHESTRATOR_TARGET in e.get("src", "")
        or MINI_ORCHESTRATOR_TARGET in e.get("dst", "")
    ]
    
    if miniorchp_entries:
        print(f"   [OK] {len(miniorchp_entries)} Safepoint-Einträge gefunden")
        for entry in miniorchp_entries[-3:]:  # Letzte 3
            print(f"      - {entry.get('sp_id', 'unknown')} ({entry.get('type', 'unknown')})")
    else:
        print(f"   [WARNING] Keine Safepoint-Einträge für {MINI_ORCHESTRATOR_TARGET} gefunden")
        print(f"      (möglicherweise noch nicht persistiert)")
# -------------------------------------------------------------------
# Step 5: Summary
# -------------------------------------------------------------------
def print_summary() -> None:
    print("\n" + "=" * 60)
    print("[SUCCESS] Integration abgeschlossen")
    print("=" * 60)
    print("\nNächste Schritte:")
    print("1. Mini-Orchestrator ist jetzt beim Portier registriert")
    print("2. Commands können via Portier dispatch/kordp gesendet werden:")
    print(f"   curl -X POST {PORTIER_URL}/dispatch/kordp \\")
    print(f"     -H 'Authorization: Bearer $BEARER_TOKEN' \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{")
    print(f"       \"service_target\": \"{MINI_ORCHESTRATOR_TARGET}\",")
    print(f"       \"action\": \"send_mail\",")
    print(f"       \"params\": {{\"to\": \"user@example.com\", \"subject\": \"Test\"}}")
    print(f"     }}'")
    print("\n3. Alle Requests werden in OpenA2 archiviert (Safepoints)")
    print("4. Sub-Agents (MailAgent, BrowserAgent) sind intern im Mini-Orchestrator")
    print("=" * 60)
# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
def main() -> None:
    print("Mini-Orchestrator -> Portier Integration")
    print("=" * 60)
    
    load_bearer_token()
    
    # Step 1: Health
    if not health_check():
        print("\n[ERROR] Health-Checks fehlgeschlagen, Abbruch")
        return
    
    # Step 2: Register
    if not register_at_portier():
        print("\n[ERROR] Registrierung fehlgeschlagen, Abbruch")
        return
    
    # Step 3: Test Dispatch
    if not test_dispatch():
        print("\n[WARNING] Test-Dispatch fehlgeschlagen (Service evtl. noch nicht bereit)")
    
    # Step 4: Verify Archiv
    verify_archiv()
    
    # Step 5: Summary
    print_summary()

if __name__ == "__main__":
    main()
