#!/usr/bin/env python3
"""
🔄 Safepoint-Client Standardisierung
===================================

Aktualisiert alle Safepoint-Clients auf die neue einheitliche
PORTIER 3.0 Spezifikation mit Remote Archivp Writer Pattern.

Ausführung: python3 update_all_safepoint_clients.py
"""

from pathlib import Path

# Neue einheitliche PORTIER 3.0 Safepoint-Client Spezifikation
SAFEPOINT_CLIENT_TEMPLATE = '''import os
import httpx
from datetime import datetime, timezone

OPENA2_URL = os.getenv("OPENA2_URL", "http://127.0.0.1:12345")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-xxx")

class SafepointClient:
    """Safepoint-Client 3.0 – Remote Archivp Writer (für alle Agenten außer opena2)."""

    SECRET_KEYS = {"token", "auth", "password", "apikey", "key", "secret", "credentials", "bearer"}
    CATEGORIES = {"CMD", "RESP", "ROUTE", "DISPATCH"}

    @staticmethod
    def _mask(obj):
        if isinstance(obj, dict):
            return {
                k: ("***" if any(s in k.lower() for s in SafepointClient.SECRET_KEYS)
                    else SafepointClient._mask(v))
                for k, v in obj.items()
            }
        if isinstance(obj, list):
            return [SafepointClient._mask(i) for i in obj]
        return obj

    @staticmethod
    async def write(category: str, source: str, destination: str, request_id: str, payload: dict):
        if category not in SafepointClient.CATEGORIES:
            raise ValueError(f"Invalid category: {category}")

        iso = datetime.now(timezone.utc).isoformat()
        ts = int(datetime.now().timestamp())

        body = {
            "timestamp": iso,
            "sp_timestamp": ts,
            "source": source,
            "destination": destination,
            "category": category,
            "request_id": request_id,
            "payload": SafepointClient._mask(payload),
            "strict": True
        }

        async with httpx.AsyncClient() as client:
            await client.post(
                f"{OPENA2_URL}/store/{category}",
                json=body,
                headers={"Authorization": f"Bearer {BEARER_TOKEN}"},
                timeout=15.0,
            )
        return body
'''


def main():
    """Aktualisiert alle Safepoint-Clients."""
    project_root = Path(".")

    # Finde alle Agent-Verzeichnisse (außer opena2)
    agent_dirs = []
    for d in project_root.glob("[0-9]*.*"):
        if d.is_dir() and d.name.startswith(
            (
                "2.",
                "3.",
                "4.",
                "5.",
                "6.",
                "7.",
                "8.",
                "9.",
                "10.",
                "11.",
                "12.",
                "13.",
                "14.",
                "15.",
                "16.",
                "17.",
                "18.",
                "19.",
                "20.",
            )
        ):
            # Überspringe opena2 (1.opena1&2_portier)
            if "opena2" not in d.name and "opena1" not in d.name:
                agent_dirs.append(d)

    print(f"🔄 Aktualisiere {len(agent_dirs)} Safepoint-Clients...")

    updated = 0
    errors = 0

    for agent_dir in sorted(agent_dirs):
        safepoint_file = agent_dir / "safepoint_client.py"

        try:
            # Backup erstellen
            if safepoint_file.exists():
                backup_file = safepoint_file.with_suffix(".py.backup")
                with open(safepoint_file, encoding="utf-8") as f:
                    backup_content = f.read()
                with open(backup_file, "w", encoding="utf-8") as f:
                    f.write(backup_content)

            # Neue einheitliche Version schreiben
            with open(safepoint_file, "w", encoding="utf-8") as f:
                f.write(SAFEPOINT_CLIENT_TEMPLATE)

            print(f"✅ {agent_dir.name}: Safepoint-Client aktualisiert")
            updated += 1

        except Exception as e:
            print(f"❌ {agent_dir.name}: Fehler - {e!s}")
            errors += 1

    print("\n🎉 Aktualisierung abgeschlossen!")
    print(f"✅ {updated} erfolgreich aktualisiert")
    print(f"❌ {errors} Fehler")

    if errors == 0:
        print("\n🚀 Alle Safepoint-Clients sind jetzt einheitlich und PORTIER 3.0 konform!")
    else:
        print(f"\n⚠️  Bitte prüfe die {errors} Fehler manuell.")

    # Validierung
    print("\n🔍 Validierung...")
    valid_count = 0

    for agent_dir in sorted(agent_dirs):
        safepoint_file = agent_dir / "safepoint_client.py"
        try:
            with open(safepoint_file, encoding="utf-8") as f:
                content = f.read()

            # Syntax-Check
            compile(content, str(safepoint_file), "exec")

            # PORTIER 3.0 Check
            if all(
                pattern in content
                for pattern in [
                    "SECRET_KEYS =",
                    "CATEGORIES =",
                    "_mask(obj)",
                    "async def write(",
                    "SafepointClient._mask(payload)",
                ]
            ):
                print(f"✅ {agent_dir.name}: Syntax & PORTIER 3.0 OK")
                valid_count += 1
            else:
                print(f"⚠️  {agent_dir.name}: Syntax OK, aber nicht vollständig PORTIER 3.0 konform")

        except Exception as e:
            print(f"❌ {agent_dir.name}: Validierungsfehler - {e!s}")

    print(f"\n📊 Validierung: {valid_count}/{len(agent_dirs)} vollständig konform")


if __name__ == "__main__":
    main()
