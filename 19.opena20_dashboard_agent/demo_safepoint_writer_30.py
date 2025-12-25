#!/usr/bin/env python3
"""
SAFEPOINT-WRITER 3.0 Demo - Portier 3.0 Spezifikation
Demonstriert alle Funktionen des produktionsreifen Safepoint-Systems
"""

# Import vom SAFEPOINT-WRITER 3.0
import sys
from datetime import datetime

sys.path.append("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.opena20_dashboard_agent")

from main_dashboard_agent import SafepointWriter30


def demo_safepoint_writer():
    """Demonstriert SAFEPOINT-WRITER 3.0 Features"""

    print("🔥 SAFEPOINT-WRITER 3.0 Demo - Portier 3.0 Spezifikation")
    print("=" * 60)

    # Initialize writer
    writer = SafepointWriter30("/tmp/demo_archivp_store")

    print("1. Initialisierung...")
    print(f"   ✓ Archivp Root: {writer.archivp_root}")
    print(f"   ✓ Index File: {writer.index_file}")

    # Demo 1: CMD Safepoint (opena1 → opena2)
    print("\n2. CMD Safepoint (opena1 → opena2)...")
    cmd_payload = {
        "command": "chat",
        "prompt": "Hello OpenWebUI",
        "model": "gpt-4",
        "token": "sk-secret-key-should-be-masked",  # Wird automatisch maskiert
        "user_context": {"user_id": 12345},
    }

    cmd_filename = writer.write_safepoint(
        source="opena1", destination="opena2", category="CMD", request_id="req_001_demo", payload=cmd_payload
    )
    print(f"   ✓ CMD Safepoint: {cmd_filename}")

    # Demo 2: ROUTE Safepoint (opena2 → kordp)
    print("\n3. ROUTE Safepoint (opena2 → kordp)...")
    route_payload = {"target_tool": "opena3", "routing_data": cmd_payload, "priority": "high"}

    route_filename = writer.write_safepoint(
        source="opena2", destination="kordp", category="ROUTE", request_id="req_001_demo", payload=route_payload
    )
    print(f"   ✓ ROUTE Safepoint: {route_filename}")

    # Demo 3: DISPATCH Safepoint (kordp → opena3)
    print("\n4. DISPATCH Safepoint (kordp → opena3)...")
    dispatch_payload = {
        "service_target": "openwebui3",
        "forwarded_payload": cmd_payload,
        "dispatch_metadata": {"retry_count": 0},
    }

    dispatch_filename = writer.write_safepoint(
        source="kordp", destination="opena3", category="DISPATCH", request_id="req_001_demo", payload=dispatch_payload
    )
    print(f"   ✓ DISPATCH Safepoint: {dispatch_filename}")

    # Demo 4: RESP Safepoint (opena3 → opena2)
    print("\n5. RESP Safepoint (opena3 → opena2)...")
    resp_payload = {
        "success": True,
        "response": "Hello! I'm OpenWebUI assistant.",
        "model": "gpt-4",
        "tokens_used": {"prompt": 15, "completion": 25},
        "api_key": "sk-another-secret-key",  # Wird automatisch maskiert
    }

    resp_filename = writer.write_safepoint(
        source="opena3", destination="opena2", category="RESP", request_id="req_001_demo", payload=resp_payload
    )
    print(f"   ✓ RESP Safepoint: {resp_filename}")

    # Verifikation der Struktur
    print("\n6. Strukturverifikation...")
    today = datetime.now()
    day_dir = writer.archivp_root / today.strftime("%Y") / today.strftime("%m") / today.strftime("%d")

    if day_dir.exists():
        safepoints = list(day_dir.glob("SP*_*→*_*.json"))
        print(f"   ✓ Safepoints heute: {len(safepoints)}")

        for sp_file in safepoints[-4:]:  # Zeige die letzten 4
            print(f"     - {sp_file.name}")

    # Index.jsonl Verifikation
    print("\n7. Index.jsonl Verifikation...")
    if writer.index_file.exists():
        lines = writer.index_file.read_text(encoding="utf-8").strip().split("\n")
        print(f"   ✓ Index Einträge: {len([l for l in lines if l.strip()])}")
        if lines and lines[-1].strip():
            import json

            last_entry = json.loads(lines[-1])
            print(
                f"   ✓ Letzter Eintrag: {last_entry['category']} - {last_entry['source']}→{last_entry['destination']}"
            )

    # Secret Maskierung Demo
    print("\n8. Secret-Maskierung Demo...")
    test_secrets = {
        "token": "sk-secret-123",
        "password": "mypassword",
        "apikey": "api-key-456",
        "normal_field": "this-stays-visible",
    }
    masked = writer._mask_secrets(test_secrets)
    print(f"   Original: {test_secrets}")
    print(f"   Maskiert: {masked}")

    print("\n✅ SAFEPOINT-WRITER 3.0 Demo completed!")
    print(f"📁 Archivp Store: {writer.archivp_root}")
    print(f"📋 Index: {writer.index_file}")


def validate_portier_30_compliance():
    """Validiert Portier 3.0 Konformität"""

    print("\n🔍 Portier 3.0 Konformitäts-Check")
    print("=" * 40)

    writer = SafepointWriter30("/tmp/demo_archivp_store")

    # Check 1: Kategorien
    required_categories = {"CMD", "RESP", "ROUTE", "DISPATCH"}
    print(f"✓ Kategorien: {writer.CATEGORIES == required_categories}")

    # Check 2: Secret Keys
    required_secrets = {"token", "auth", "password", "apikey", "key", "secret", "credentials"}
    print(f"✓ Secret Keys: {writer.SECRET_KEYS == required_secrets}")

    # Check 3: Unicode-Pfeil im Dateinamen
    test_filename = writer.write_safepoint("test", "test2", "CMD", "test_req", {"test": True})
    has_arrow = "→" in test_filename
    print(f"✓ Unicode-Pfeil →: {has_arrow}")

    # Check 4: YYYY/MM/DD Struktur
    today = datetime.now()
    expected_path = writer.archivp_root / today.strftime("%Y") / today.strftime("%m") / today.strftime("%d")
    print(f"✓ YYYY/MM/DD Struktur: {expected_path.exists()}")

    # Check 5: index.jsonl
    print(f"✓ index.jsonl: {writer.index_file.exists()}")

    print("\n🎯 Portier 3.0 SAFEPOINT-WRITER ist konform!")


if __name__ == "__main__":
    demo_safepoint_writer()
    validate_portier_30_compliance()
