#!/usr/bin/env python3
"""
generate_macdir.py - MAC_DIR.json Generator

Erzeugt ein strukturiertes Verzeichnisinventar (MAC_DIR.json) für das Projekt.
Enthält: Dateipfade, Typen, Größen, Zeitstempel, SHA256-Hashes.

Verwendung:
    python3 tools/generate_macdir.py [--output MAC_DIR.json] [--path /pfad/zum/projekt]
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path


def calculate_sha256(filepath: Path) -> str:
    """Berechnet SHA256-Hash einer Datei."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except OSError:
        return ""


def get_file_info(filepath: Path, base_path: Path) -> dict:
    """Sammelt Informationen über eine Datei."""
    stat = filepath.stat()
    rel_path = str(filepath.relative_to(base_path))

    info = {
        "path": rel_path,
        "type": "file",
        "size": stat.st_size,
        "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
        "permissions": oct(stat.st_mode)[-3:],
    }

    # SHA256 nur für Dateien unter 10MB
    if stat.st_size < 10 * 1024 * 1024:
        info["sha256"] = calculate_sha256(filepath)

    return info


def get_dir_info(dirpath: Path, base_path: Path, entry_count: int) -> dict:
    """Sammelt Informationen über ein Verzeichnis."""
    stat = dirpath.stat()
    rel_path = str(dirpath.relative_to(base_path))

    return {
        "path": rel_path if rel_path != "." else "/",
        "type": "dir",
        "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
        "permissions": oct(stat.st_mode)[-3:],
        "entries": entry_count,
    }


# Verzeichnisse die ignoriert werden sollen
IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".idea",
    ".vscode",
    "dist",
    "build",
    ".eggs",
    "*.egg-info",
    ".tox",
    ".nox",
    ".coverage",
    "htmlcov",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "logs",
    "*.log",
}

IGNORE_FILES = {".DS_Store", "Thumbs.db", "*.pyc", "*.pyo", "*.swp", "*.swo"}


def should_ignore(path: Path) -> bool:
    """Prüft ob Pfad ignoriert werden soll."""
    name = path.name

    # Direkte Matches
    if name in IGNORE_DIRS or name in IGNORE_FILES:
        return True

    # Pattern Matches
    for pattern in IGNORE_DIRS | IGNORE_FILES:
        if "*" in pattern:
            import fnmatch

            if fnmatch.fnmatch(name, pattern):
                return True

    return False


def scan_directory(base_path: Path, max_depth: int = 10) -> list[dict]:
    """Scannt ein Verzeichnis rekursiv."""
    entries = []

    def scan_recursive(current_path: Path, depth: int = 0):
        if depth > max_depth:
            return

        try:
            items = sorted(current_path.iterdir())
        except PermissionError:
            return

        dir_files = 0

        for item in items:
            if should_ignore(item):
                continue

            try:
                if item.is_file():
                    entries.append(get_file_info(item, base_path))
                    dir_files += 1
                elif item.is_dir():
                    subdir_count = scan_recursive(item, depth + 1)
                    entries.append(get_dir_info(item, base_path, subdir_count))
                    dir_files += 1
            except (PermissionError, OSError):
                continue

        return dir_files

    # Root-Verzeichnis scannen
    root_count = scan_recursive(base_path)

    # Root-Eintrag am Anfang hinzufügen
    entries.insert(0, get_dir_info(base_path, base_path, root_count))

    return entries


def generate_macdir(project_path: Path, output_path: Path | None = None) -> dict:
    """Generiert das MAC_DIR.json Manifest."""

    print(f"🔍 Scanne: {project_path}")

    entries = scan_directory(project_path)

    macdir = {
        "project_root": str(project_path),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "generator": "generate_macdir.py",
        "version": "1.0.0",
        "total_entries": len(entries),
        "total_files": sum(1 for e in entries if e["type"] == "file"),
        "total_dirs": sum(1 for e in entries if e["type"] == "dir"),
        "entries": entries,
    }

    # Speichern wenn Output-Pfad angegeben
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(macdir, f, indent=2, ensure_ascii=False)
        print(f"✅ Gespeichert: {output_path}")
        print(f"   📁 {macdir['total_dirs']} Verzeichnisse")
        print(f"   📄 {macdir['total_files']} Dateien")

    return macdir


def main():
    """Hauptfunktion."""
    parser = argparse.ArgumentParser(description="MAC_DIR.json Generator")
    parser.add_argument(
        "--path",
        "-p",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Projekt-Pfad (default: Eltern von tools/)",
    )
    parser.add_argument("--output", "-o", type=Path, default=None, help="Output-Datei (default: <path>/MAC_DIR.json)")
    parser.add_argument("--stdout", action="store_true", help="Ausgabe auf stdout statt Datei")

    args = parser.parse_args()

    project_path = args.path.resolve()

    if args.stdout:
        output_path = None
    else:
        output_path = args.output or (project_path / "MAC_DIR.json")

    macdir = generate_macdir(project_path, output_path)

    if args.stdout:
        print(json.dumps(macdir, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
