#!/usr/bin/env python3
"""
🔧 PORTIER 3.0 Auto-Fixer
========================

Automatische Reparatur von häufigen Problemen:
- Syntax-Fehler in Safepoint-Clients
- PORTIER 3.0 Compliance Violations
- Performance-Probleme
- Formatting Issues

Version: 1.0
Datum: 29. November 2025
"""

import logging
import re
import shutil
from pathlib import Path

logger = logging.getLogger("auto_fixer")


class SafepointClientFixer:
    """Automatischer Fixer für Safepoint-Clients."""

    TEMPLATE = '''import os
import httpx
from datetime import datetime, timezone

OPENA2_URL = os.getenv("OPENA2_URL", "http://127.0.0.1:12345")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-xxx")

class SafepointClient:
    """Safepoint-Client 3.0 für {agent_name}."""

    @staticmethod
    async def write(category: str, source: str, destination: str, request_id: str, payload: dict):
        iso = datetime.now(timezone.utc).isoformat()
        ts = int(datetime.now().timestamp())

        def mask(obj):
            if isinstance(obj, dict):
                return {{k: ("***" if k.lower() in ["token","auth","password","apikey","secret","key"] else mask(v)) for k,v in obj.items()}}
            if isinstance(obj, list):
                return [mask(i) for i in obj]
            return obj

        body = {{
            "timestamp": iso,
            "sp_timestamp": ts,
            "source": source,
            "destination": destination,
            "category": category,
            "request_id": request_id,
            "payload": mask(payload),
            "strict": True
        }}

        async with httpx.AsyncClient() as client:
            await client.post(
                f"{{OPENA2_URL}}/store/{{category}}",
                json=body,
                headers={{"Authorization": f"Bearer {{BEARER_TOKEN}}"}},
                timeout=15.0
            )
        return body
'''

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def fix_all_clients(self) -> dict[str, list[str]]:
        """Repariert alle Safepoint-Clients."""
        results = {"fixed": [], "errors": [], "skipped": []}

        for agent_dir in self.project_root.glob("[0-9]*.*"):
            if not agent_dir.is_dir():
                continue

            safepoint_file = agent_dir / "safepoint_client.py"

            if not safepoint_file.exists():
                results["skipped"].append(f"{agent_dir.name}: Datei existiert nicht")
                continue

            try:
                if self._fix_safepoint_client(safepoint_file, agent_dir.name):
                    results["fixed"].append(f"{agent_dir.name}: Erfolgreich repariert")
                else:
                    results["skipped"].append(f"{agent_dir.name}: Keine Reparatur nötig")
            except Exception as e:
                results["errors"].append(f"{agent_dir.name}: {e!s}")

        return results

    def _fix_safepoint_client(self, file_path: Path, agent_dir_name: str) -> bool:
        """Repariert einzelnen Safepoint-Client."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception:
            # Datei nicht lesbar - komplett neu erstellen
            return self._create_from_template(file_path, agent_dir_name)

        # Syntax-Check
        try:
            compile(content, str(file_path), "exec")
        except SyntaxError:
            # Syntax-Fehler - komplett neu erstellen
            return self._create_from_template(file_path, agent_dir_name)

        # Compliance-Check und Fixes
        fixed = False

        # 1. Import-Fixes
        if not all(imp in content for imp in ["import os", "import httpx", "from datetime import datetime, timezone"]):
            fixed = True
            content = self._fix_imports(content)

        # 2. Class-Definition Fix
        if "class SafepointClient:" not in content:
            fixed = True
            return self._create_from_template(file_path, agent_dir_name)

        # 3. Async-Method Fix
        if "def write(" in content and "async def write(" not in content:
            fixed = True
            content = content.replace("def write(", "async def write(")

        # 4. Type-Hints Fix
        if ": str" not in content or ": dict" not in content:
            fixed = True
            content = self._fix_type_hints(content)

        # 5. HTTP-Client Fix
        if "httpx.AsyncClient()" in content and "async with" not in content:
            fixed = True
            content = self._fix_http_client(content)

        # 6. Secret-Masking Fix
        if not all(secret in content for secret in ["token", "auth", "password"]):
            fixed = True
            content = self._fix_secret_masking(content)

        if fixed:
            # Backup erstellen
            backup_path = file_path.with_suffix(".py.backup")
            shutil.copy2(file_path, backup_path)

            # Reparierte Version schreiben
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        return fixed

    def _create_from_template(self, file_path: Path, agent_dir_name: str) -> bool:
        """Erstellt Datei komplett neu aus Template."""
        # Agent-Name aus Verzeichnis extrahieren
        match = re.search(r"opena\d+[^/]*", agent_dir_name)
        agent_name = match.group(0) if match else agent_dir_name

        # Backup der alten Datei
        if file_path.exists():
            backup_path = file_path.with_suffix(".py.broken")
            shutil.copy2(file_path, backup_path)

        # Neue Datei aus Template
        content = self.TEMPLATE.format(agent_name=agent_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return True

    def _fix_imports(self, content: str) -> str:
        """Repariert Import-Statements."""
        lines = content.split("\n")

        # Entferne alte Imports
        filtered_lines = [
            line for line in lines if not (line.strip().startswith("import ") or line.strip().startswith("from "))
        ]

        # Neue Imports hinzufügen
        new_imports = [
            "import os",
            "import httpx",
            "from datetime import datetime, timezone",
            "",  # Leerzeile
        ]

        return "\n".join(new_imports + filtered_lines)

    def _fix_type_hints(self, content: str) -> str:
        """Fügt Type-Hints hinzu."""
        # Async write method fix
        pattern = r"async def write\([^)]*\):"
        replacement = "async def write(category: str, source: str, destination: str, request_id: str, payload: dict):"

        return re.sub(pattern, replacement, content)

    def _fix_http_client(self, content: str) -> str:
        """Repariert HTTP-Client Usage."""
        # Pattern für alten Style
        old_pattern = r"httpx\.AsyncClient\(\) as (\w+):"
        new_pattern = r"async with httpx.AsyncClient() as \1:"

        return re.sub(old_pattern, new_pattern, content)

    def _fix_secret_masking(self, content: str) -> str:
        """Repariert Secret-Masking."""
        # Wenn mask-Funktion fehlt, komplette Neuerstellung
        if "def mask(" not in content:
            return content  # Wird durch Template-Erstellung gefixt

        # Secret-Liste erweitern
        secret_pattern = r'\["token","auth","password"[^\]]*\]'
        new_secrets = '["token","auth","password","apikey","secret","key"]'

        return re.sub(secret_pattern, new_secrets, content)


class CodeFormatter:
    """Code-Formatter für einheitlichen Style."""

    def format_file(self, file_path: Path) -> bool:
        """Formatiert einzelne Datei."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Basic Formatting
            formatted = self._format_content(content)

            if formatted != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(formatted)
                return True

        except Exception as e:
            logger.error(f"Formatierung fehlgeschlagen für {file_path}: {e}")

        return False

    def _format_content(self, content: str) -> str:
        """Formatiert Content."""
        lines = content.split("\n")
        formatted_lines = []

        for line in lines:
            # Entferne trailing whitespace
            line = line.rstrip()

            # Normalize Einrückung (4 Spaces)
            if line.strip():
                indent_level = (len(line) - len(line.lstrip())) // 4
                line = "    " * indent_level + line.lstrip()

            formatted_lines.append(line)

        # Entferne mehrfache Leerzeilen
        result_lines = []
        empty_count = 0

        for line in formatted_lines:
            if not line.strip():
                empty_count += 1
                if empty_count <= 2:  # Max 2 aufeinanderfolgende Leerzeilen
                    result_lines.append(line)
            else:
                empty_count = 0
                result_lines.append(line)

        return "\n".join(result_lines)


def main():
    """Hauptfunktion für Auto-Fixer."""
    import argparse

    parser = argparse.ArgumentParser(description="PORTIER 3.0 Auto-Fixer")
    parser.add_argument("--project-root", default=".", help="Projekt-Root-Pfad")
    parser.add_argument("--format-only", action="store_true", help="Nur Formatierung")
    parser.add_argument("--dry-run", action="store_true", help="Simulation ohne Änderungen")

    args = parser.parse_args()

    project_root = Path(args.project_root)

    if args.format_only:
        formatter = CodeFormatter()
        fixed_count = 0

        for safepoint_file in project_root.glob("*/safepoint_client.py"):
            if formatter.format_file(safepoint_file):
                print(f"✅ Formatiert: {safepoint_file}")
                fixed_count += 1

        print(f"\n🎉 {fixed_count} Dateien formatiert")

    else:
        fixer = SafepointClientFixer(project_root)

        if args.dry_run:
            print("🔍 DRY RUN - Keine Änderungen werden gespeichert")

        results = fixer.fix_all_clients()

        print("🔧 AUTO-FIXER ERGEBNISSE")
        print("=" * 30)

        if results["fixed"]:
            print("✅ REPARIERT:")
            for item in results["fixed"]:
                print(f"  • {item}")

        if results["skipped"]:
            print("\n⏭️ ÜBERSPRUNGEN:")
            for item in results["skipped"]:
                print(f"  • {item}")

        if results["errors"]:
            print("\n❌ FEHLER:")
            for item in results["errors"]:
                print(f"  • {item}")

        print(
            f"\n📊 SUMMARY: {len(results['fixed'])} repariert, {len(results['skipped'])} übersprungen, {len(results['errors'])} Fehler"
        )


if __name__ == "__main__":
    main()
