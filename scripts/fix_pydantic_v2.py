#!/usr/bin/env python3
"""
Pydantic v2 Migration Fix für PORTIER Agents
Behebt Pydantic v1 -> v2 Breaking Changes in opena3,4,5,7,9
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent

# Agents mit Pydantic-Problemen
PROBLEM_AGENTS = ["opena3", "opena4", "opena5", "opena7", "opena9"]

# Pydantic v2 Migrations-Patterns
MIGRATIONS = [
    # pydantic_settings Import Fix
    (
        r"from pydantic import BaseSettings",
        "from pydantic_settings import BaseSettings"
    ),
    # Config class -> model_config
    (
        r"class Config:\s*env_file\s*=\s*['\"]\.env['\"]",
        "model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')"
    ),
    # Field validators (@validator -> @field_validator)
    (
        r"@validator\((['\"])([^'\"]+)\1\)",
        r"@field_validator('\2')"
    ),
    # parse_obj -> model_validate
    (
        r"\.parse_obj\(",
        ".model_validate("
    ),
    # dict() -> model_dump()
    (
        r"\.dict\(\)",
        ".model_dump()"
    ),
    # HTTPException syntax fix
    (
        r"raise HTTPException\(\s*from\s+e",
        "raise HTTPException("
    ),
]


def find_agent_main_file(agent_id: str) -> Path | None:
    """Findet main*.py Datei des Agents"""
    agent_dirs = list(PROJECT_ROOT.glob(f"*{agent_id}*"))
    if not agent_dirs:
        return None

    agent_dir = agent_dirs[0]
    main_files = list(agent_dir.glob("main*.py"))
    return main_files[0] if main_files else None


def apply_migrations(file_path: Path) -> Tuple[bool, List[str]]:
    """Wendet Pydantic v2 Migrations an"""
    content = file_path.read_text(encoding="utf-8")
    original = content
    changes = []

    for pattern, replacement in MIGRATIONS:
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        if new_content != content:
            changes.append(f"  ✓ {pattern[:50]}... → {replacement[:50]}...")
            content = new_content

    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return True, changes
    return False, []


def install_pydantic_settings(agent_dir: Path) -> bool:
    """Installiert pydantic-settings im Agent venv"""
    venv_pip = agent_dir / "venv" / "bin" / "pip"
    if not venv_pip.exists():
        return False

    try:
        subprocess.run(
            [str(venv_pip), "install", "pydantic-settings>=2.0.0"],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def validate_syntax(file_path: Path) -> bool:
    """Prüft Python-Syntax"""
    try:
        subprocess.run(
            ["python3", "-m", "py_compile", str(file_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Syntax-Fehler: {e.stderr[:100]}")
        return False


def main():
    """Hauptprozess"""
    print("🔧 Pydantic v2 Migration für PORTIER Agents")
    print("=" * 60)

    fixed = 0
    failed = 0

    for agent_id in PROBLEM_AGENTS:
        print(f"\n🔹 [{agent_id}]")

        main_file = find_agent_main_file(agent_id)
        if not main_file:
            print(f"   ⚠️  main.py nicht gefunden")
            failed += 1
            continue

        print(f"   📄 {main_file.name}")

        # Backup erstellen
        backup = main_file.with_suffix(".py.bak")
        backup.write_text(main_file.read_text(), encoding="utf-8")
        print(f"   💾 Backup: {backup.name}")

        # Migrationen anwenden
        modified, changes = apply_migrations(main_file)
        if modified:
            print(f"   ✏️  {len(changes)} Änderungen:")
            for change in changes:
                print(change)
        else:
            print("   ℹ️  Keine Änderungen nötig")

        # Syntax prüfen
        if validate_syntax(main_file):
            print("   ✅ Syntax OK")
        else:
            print("   ❌ Syntax-Fehler nach Migration")
            main_file.write_text(backup.read_text(), encoding="utf-8")
            print("   ↩️  Backup wiederhergestellt")
            failed += 1
            continue

        # pydantic-settings installieren
        agent_dir = main_file.parent
        if install_pydantic_settings(agent_dir):
            print("   📦 pydantic-settings installiert")
        else:
            print("   ⚠️  pydantic-settings Installation übersprungen (kein venv)")

        fixed += 1

    print("\n" + "=" * 60)
    print(f"📊 Ergebnis: {fixed} gefixt, {failed} fehlgeschlagen")

    if fixed > 0:
        print("\n🔄 Starte Agents neu:")
        print("   bash bin/ops.sh restart opena3 opena4 opena5 opena7 opena9")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
