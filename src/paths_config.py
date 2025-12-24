"""
paths_config.py – Zentrale Pfad-Konfiguration (Portable, Server-Transfer Ready)
================================================================================

Alle Pfade sind environment-basiert oder relative-basiert.
Single Source of Truth für alle Services (OpenA1–OpenA20).

Priorität:
  1. Environment-Variablen (BASE_ROOT, VENV_PATH, PORT_RANGE, FORBIDDEN_PORTS)
  2. Fallback: Automatisch ermittelt aus __file__ (repo root)
  3. Hardcoded Default: Finale Sicherheit für alle Fälle

Verwendung:
  from src.paths_config import BASE_ROOT, VENV_PATH, PORT_RANGE, FORBIDDEN_PORTS

  archive_dir = BASE_ROOT / "1.opena1&2_portier" / "archivp_store"
"""

import os
from pathlib import Path

# ════════════════════════════════════════════════════════════════════════════
# PRIMARY: Environment-based Configuration (Server-Transfer Safe)
# ════════════════════════════════════════════════════════════════════════════


def _get_base_root() -> Path:
    """
    Ermittelt BASE_ROOT mit Fallback-Kette:
    1. $BASE_ROOT (explizit gesetzt)
    2. $PORTIER_ROOT (alias)
    3. Git repo root (automatisch)
    4. Hardcoded default (finale Sicherheit)
    """
    # 1. Explicit ENV
    if base_env := os.getenv("BASE_ROOT"):
        return Path(base_env).resolve()

    if portier_env := os.getenv("PORTIER_ROOT"):
        return Path(portier_env).resolve()

    # 2. Automatisch: Finde repo root
    # __file__ = .../Gesamtprojekt/src/paths_config.py
    # → ../ = .../Gesamtprojekt/src/
    # → ../../ = .../Gesamtprojekt/ (repo root)
    current_file = Path(__file__).resolve()
    repo_root = current_file.parent.parent  # src/../ = repo root
    if (repo_root / "configs" / "agent_dirs.yaml").exists():
        return repo_root

    # 3. Hardcoded Default (für alle anderen Fälle)
    default = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt")
    return default.resolve() if default.exists() else repo_root


def _get_venv_path() -> Path:
    """
    Ermittelt VENV_PATH — POLICY-BINDING (immer 1.opena1&2_portier/venv313):
    1. $VENV_PATH (explizit, überschreibt Policy)
    2. Hardcoded Policy-Pfad: BASE_ROOT/1.opena1&2_portier/venv313 (DEFAULT)

    Diese Venv ist zentral für ALLE 20 Services. Keine Alternativen!
    """
    # Nur explizite ENV-Override erlaubt
    if venv_env := os.getenv("VENV_PATH"):
        return Path(venv_env).resolve()

    # Policy-Binding: Immer 1.opena1&2_portier/venv313
    base = _get_base_root()
    policy_venv = base / "1.opena1&2_portier" / "venv313"
    return policy_venv.resolve()


# ════════════════════════════════════════════════════════════════════════════
# CONSTANTS (Derived from ENV or hardcoded)
# ════════════════════════════════════════════════════════════════════════════

BASE_ROOT: Path = _get_base_root()
"""
Projekt-Root: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt
Enthält alle 20 OpenA-Services.
"""

VENV_PATH: Path = _get_venv_path()
"""
Python venv Pfad: BASE_ROOT/1.opena1&2_portier/venv313
Alle Services nutzen diesen Python interpreter.
"""

PYTHON_BIN: Path = VENV_PATH / "bin" / "python3"
"""Python executable: venv313/bin/python3"""

PORT_RANGE: tuple = (12344, 12399)
"""
Zulässige Port-Range: 12344–12399 (56 Ports für 20 Services)
Binding: 127.0.0.1 (Localhost only)
"""

FORBIDDEN_PORTS: set[int] = {8080}
"""
Verbotene Ports (reserviert für externe Services wie OpenWebUI)
"""

# ════════════════════════════════════════════════════════════════════════════
# SERVICE-SPECIFIC PATHS
# ════════════════════════════════════════════════════════════════════════════

PORTIER_DIR: Path = BASE_ROOT / "1.opena1&2_portier"
"""Coordinator + Archivator directory"""

ARCHIVP_STORE: Path = PORTIER_DIR / "archivp_store"
"""Archivator storage: safepoints und index.jsonl"""

ARCHIVP_INDEX: Path = ARCHIVP_STORE / "index.jsonl"
"""Index file für alle Safepoints"""

CONFIGS_DIR: Path = BASE_ROOT / "configs"
"""Konfigurationsdateien"""

SCRIPTS_DIR: Path = BASE_ROOT / "scripts"
"""Bash/Python scripts"""

LOGS_DIR: Path = BASE_ROOT / "logs"
"""Service logs"""

# ════════════════════════════════════════════════════════════════════════════
# VALIDATION
# ════════════════════════════════════════════════════════════════════════════


def validate_paths() -> bool:
    """
    Validiert alle kritischen Pfade.
    Gibt True zurück wenn OK, False wenn fehler.
    """
    checks = {
        "BASE_ROOT exists": BASE_ROOT.exists(),
        "VENV_PATH exists": VENV_PATH.exists(),
        "PORTIER_DIR exists": PORTIER_DIR.exists(),
        "CONFIGS_DIR exists": CONFIGS_DIR.exists(),
        "PORT_RANGE valid": PORT_RANGE[0] < PORT_RANGE[1],
    }

    all_ok = all(checks.values())
    if not all_ok:
        print("[WARNING] Path validation failed:")
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}")

    return all_ok


# ════════════════════════════════════════════════════════════════════════════
# DEBUG INFO
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 80)
    print("PATHS_CONFIG — Portable Path Configuration")
    print("=" * 80)
    print(f"BASE_ROOT:       {BASE_ROOT}")
    print(f"VENV_PATH:       {VENV_PATH}")
    print(f"PYTHON_BIN:      {PYTHON_BIN}")
    print(f"PORT_RANGE:      {PORT_RANGE[0]}–{PORT_RANGE[1]}")
    print(f"FORBIDDEN_PORTS: {FORBIDDEN_PORTS}")
    print(f"PORTIER_DIR:     {PORTIER_DIR}")
    print(f"ARCHIVP_STORE:   {ARCHIVP_STORE}")
    print(f"ARCHIVP_INDEX:   {ARCHIVP_INDEX}")
    print()
    print(f"Validation: {'✅ OK' if validate_paths() else '❌ FAILED'}")
    print("=" * 80)
