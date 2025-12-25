#!/usr/bin/env python3
"""
ELION Auto-Indexer für OpenWebUI Integration
- Auto-extrahiert und indexiert hochgeladene Projektdateien
- Kein Eingriff in bestehende Ordnerstrukturen
- Automatisches Knowledgebase-Feeding
- Safepoint-Integration für alle Operationen
"""

import hashlib
import json
import logging
import os
import shutil
import sys
import tarfile
import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

BASE_ROOT = Path(os.getenv("BASE_ROOT", "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"))
OPENA3_DIR = BASE_ROOT / "2.opena3_openwebui"
KNOWLEDGEBASE_DIR = BASE_ROOT / "1.opena1&2_portier" / "knowledgebase"
ARCHIVE_DIR = BASE_ROOT / "1.opena1&2_portier" / "archivp_store"
INDEX_FILE = ARCHIVE_DIR / "index.jsonl"

# Auto-Index Konfiguration
AUTO_INDEX_DIR = OPENA3_DIR / "auto_indexed"
EXTRACTION_DIR = AUTO_INDEX_DIR / "extracted"
METADATA_FILE = AUTO_INDEX_DIR / "index_metadata.jsonl"

# Zu indexierende Dateien
TARGET_FILES = [
    OPENA3_DIR / "openwebui_data_backup.tar",
    OPENA3_DIR / "main_openwebui_bridge.py",
    OPENA3_DIR / "main_openwebui_bridge_v2.py",
]

# Zusätzliche Archive (erweiterte Integration)
ADDITIONAL_ARCHIVES = [
    KNOWLEDGEBASE_DIR / "opena1" / "LocalAgent-Pro.zip",
    KNOWLEDGEBASE_DIR / "opena1" / "opena5_dashboard_skeleton.zip",
    BASE_ROOT / "localagent datein" / "LocalAgent-Pro.zip",
    BASE_ROOT / "localagent datein" / "vscode-icons-12.15.0.zip",
    BASE_ROOT / "localagent datein" / ".git.zip",
    BASE_ROOT / "localagent datein" / ".vscode.zip",
]

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("elion.auto_indexer")

# ──────────────────────────────────────────────────────────────────────────────
# Safepoint Utilities
# ──────────────────────────────────────────────────────────────────────────────


def write_safepoint(src: str, dst: str, kind: str, body: dict[str, Any]) -> Path:
    """Schreibt Safepoint für Indexierungs-Operationen."""
    today = datetime.utcnow().strftime("%Y/%m/%d")
    target_dir = ARCHIVE_DIR / today
    target_dir.mkdir(parents=True, exist_ok=True)

    ts = int(time.time())
    name = f"SP{ts}_{src}→{dst}_{kind}.json"
    fpath = target_dir / name

    payload = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "src": src,
        "dst": dst,
        "kind": kind,
        "body": body,
        "strict": True,
    }

    fpath.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Append to index
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with INDEX_FILE.open("a", encoding="utf-8") as idx:
        idx.write(
            json.dumps({"sp": name, "ts": payload["ts"], "src": src, "dst": dst, "kind": kind, "path": str(fpath)})
            + "\n"
        )

    logger.debug(f"Safepoint: {name}")
    return fpath


# ──────────────────────────────────────────────────────────────────────────────
# Hash & Metadata Utilities
# ──────────────────────────────────────────────────────────────────────────────


def compute_file_hash(filepath: Path) -> str:
    """Berechnet SHA256-Hash einer Datei."""
    sha256 = hashlib.sha256()
    with filepath.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_metadata() -> dict[str, Any]:
    """Lädt bestehende Metadata."""
    if not METADATA_FILE.exists():
        return {}

    metadata = {}
    with METADATA_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line.strip())
            metadata[entry["file_path"]] = entry
    return metadata


def save_metadata_entry(entry: dict[str, Any]):
    """Speichert einzelnen Metadata-Eintrag."""
    METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with METADATA_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ──────────────────────────────────────────────────────────────────────────────
# Extraction & Indexing
# ──────────────────────────────────────────────────────────────────────────────


def extract_tar_archive(tar_path: Path, dest_dir: Path) -> list[Path]:
    """Extrahiert TAR-Archiv und gibt Liste der extrahierten Dateien zurück."""
    logger.info(f"Extrahiere TAR-Archiv: {tar_path.name}")

    dest_dir.mkdir(parents=True, exist_ok=True)
    extracted_files = []

    try:
        with tarfile.open(tar_path, "r") as tar:
            members = tar.getmembers()
            logger.info(f"  {len(members)} Dateien gefunden")

            tar.extractall(path=dest_dir)

            for member in members:
                if member.isfile():
                    extracted_path = dest_dir / member.name
                    if extracted_path.exists():
                        extracted_files.append(extracted_path)

        logger.info(f"  ✓ {len(extracted_files)} Dateien extrahiert")
        return extracted_files

    except Exception as e:
        logger.error(f"Fehler beim Extrahieren: {e}")
        return []


def extract_zip_archive(zip_path: Path, dest_dir: Path) -> list[Path]:
    """Extrahiert ZIP-Archiv und gibt Liste der extrahierten Dateien zurück."""
    logger.info(f"Extrahiere ZIP-Archiv: {zip_path.name}")

    dest_dir.mkdir(parents=True, exist_ok=True)
    extracted_files = []

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            members = zf.namelist()
            logger.info(f"  {len(members)} Einträge gefunden")

            zf.extractall(path=dest_dir)

            for member in members:
                extracted_path = dest_dir / member
                if extracted_path.exists() and extracted_path.is_file():
                    extracted_files.append(extracted_path)

        logger.info(f"  ✓ {len(extracted_files)} Dateien extrahiert")
        return extracted_files

    except Exception as e:
        logger.error(f"Fehler beim Extrahieren von ZIP: {e}")
        return []


def index_file(filepath: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    """Indexiert einzelne Datei und gibt Metadata zurück."""
    file_hash = compute_file_hash(filepath)
    file_stat = filepath.stat()

    entry = {
        "file_path": str(filepath),
        "file_name": filepath.name,
        "file_size": file_stat.st_size,
        "file_hash": file_hash,
        "indexed_at": datetime.utcnow().isoformat() + "Z",
        "file_type": filepath.suffix,
        "relative_path": (
            str(filepath.relative_to(AUTO_INDEX_DIR)) if filepath.is_relative_to(AUTO_INDEX_DIR) else str(filepath)
        ),
    }

    # Prüfe ob bereits indexiert
    if str(filepath) in metadata:
        existing = metadata[str(filepath)]
        if existing.get("file_hash") == file_hash:
            logger.debug(f"  ⊙ Bereits indexiert: {filepath.name}")
            return existing
        else:
            logger.info(f"  ↻ Datei geändert: {filepath.name}")
    else:
        logger.info(f"  + Neu indexiert: {filepath.name}")

    save_metadata_entry(entry)
    return entry


def copy_to_knowledgebase(source_path: Path, kb_category: str = "opena3") -> Path:
    """Kopiert Datei in Knowledgebase ohne bestehende Struktur zu stören."""
    kb_target_dir = KNOWLEDGEBASE_DIR / "opena1" / kb_category
    kb_target_dir.mkdir(parents=True, exist_ok=True)

    # Generiere eindeutigen Dateinamen falls nötig
    target_path = kb_target_dir / source_path.name
    counter = 1
    while target_path.exists():
        stem = source_path.stem
        suffix = source_path.suffix
        target_path = kb_target_dir / f"{stem}_{counter}{suffix}"
        counter += 1

    shutil.copy2(source_path, target_path)
    logger.info(f"  ✓ Kopiert nach Knowledgebase: {kb_category}/{target_path.name}")
    return target_path


# ──────────────────────────────────────────────────────────────────────────────
# Main Auto-Indexing Workflow
# ──────────────────────────────────────────────────────────────────────────────


def auto_index_all():
    """Hauptfunktion für Auto-Indexierung aller Projektdateien."""
    logger.info("=" * 80)
    logger.info("ELION Auto-Indexer gestartet")
    logger.info("=" * 80)

    # Lade bestehende Metadata
    metadata = load_metadata()
    logger.info(f"Bestehende Index-Einträge: {len(metadata)}")

    # Zähler
    stats = {
        "total_files": 0,
        "new_files": 0,
        "updated_files": 0,
        "skipped_files": 0,
        "extracted_archives": 0,
        "kb_entries": 0,
    }

    # Safepoint: Start
    write_safepoint(
        "elion_indexer",
        "opena3",
        "INDEX_START",
        {"timestamp": datetime.utcnow().isoformat() + "Z", "target_files": [str(f) for f in TARGET_FILES]},
    )

    # ─────────────────────────────────────────────────────────────────────────
    # 1. Python-Dateien direkt indexieren
    # ─────────────────────────────────────────────────────────────────────────

    logger.info("\n[1/3] Indexiere Python Bridge-Dateien...")

    for py_file in TARGET_FILES:
        if not py_file.exists() or py_file.suffix != ".py":
            continue

        stats["total_files"] += 1
        entry = index_file(py_file, metadata)

        if str(py_file) not in metadata:
            stats["new_files"] += 1
        elif entry.get("file_hash") != metadata.get(str(py_file), {}).get("file_hash"):
            stats["updated_files"] += 1
        else:
            stats["skipped_files"] += 1

        # Kopiere in Knowledgebase
        kb_path = copy_to_knowledgebase(py_file, "openwebui_bridge")
        stats["kb_entries"] += 1

    # ─────────────────────────────────────────────────────────────────────────
    # 2. TAR-Archive extrahieren und indexieren
    # ─────────────────────────────────────────────────────────────────────────

    logger.info("\n[2/4] Extrahiere und indexiere TAR-Archive...")

    for tar_file in TARGET_FILES:
        if not tar_file.exists() or not tar_file.name.endswith(".tar"):
            continue

        tar_hash = compute_file_hash(tar_file)
        extract_dir = EXTRACTION_DIR / f"{tar_file.stem}_{tar_hash[:8]}"

        # Prüfe ob bereits extrahiert
        if extract_dir.exists():
            logger.info(f"  ⊙ Bereits extrahiert: {tar_file.name}")
        else:
            extracted_files = extract_tar_archive(tar_file, extract_dir)
            stats["extracted_archives"] += 1

            # Indexiere extrahierte Dateien
            logger.info(f"  Indexiere {len(extracted_files)} extrahierte Dateien...")
            for extracted_file in extracted_files:
                stats["total_files"] += 1
                entry = index_file(extracted_file, metadata)

                if str(extracted_file) not in metadata:
                    stats["new_files"] += 1

                # Selektive Knowledgebase-Integration (nur relevante Dateien)
                if extracted_file.suffix in [".json", ".md", ".txt", ".py", ".js", ".yml", ".yaml"]:
                    if extracted_file.stat().st_size < 1024 * 1024:  # < 1MB
                        kb_path = copy_to_knowledgebase(extracted_file, "openwebui_data")
                        stats["kb_entries"] += 1

    # ─────────────────────────────────────────────────────────────────────────
    # 3. ZIP-Archive extrahieren und indexieren (erweiterte Integration)
    # ─────────────────────────────────────────────────────────────────────────

    logger.info("\n[3/4] Extrahiere und indexiere ZIP-Archive...")

    for zip_file in ADDITIONAL_ARCHIVES:
        if not zip_file.exists():
            logger.debug(f"  ⊘ Nicht gefunden: {zip_file.name}")
            continue

        zip_hash = compute_file_hash(zip_file)
        extract_dir = EXTRACTION_DIR / f"{zip_file.stem}_{zip_hash[:8]}"

        # Prüfe ob bereits extrahiert
        if extract_dir.exists():
            logger.info(f"  ⊙ Bereits extrahiert: {zip_file.name}")
            continue

        extracted_files = extract_zip_archive(zip_file, extract_dir)
        if extracted_files:
            stats["extracted_archives"] += 1

            # Indexiere extrahierte Dateien (mit Limit für große Archive)
            max_files = min(len(extracted_files), 500)  # Max 500 Dateien pro Archiv
            logger.info(f"  Indexiere {max_files} von {len(extracted_files)} extrahierten Dateien...")

            for extracted_file in extracted_files[:max_files]:
                stats["total_files"] += 1
                entry = index_file(extracted_file, metadata)

                if str(extracted_file) not in metadata:
                    stats["new_files"] += 1

                # Selektive Knowledgebase-Integration
                if extracted_file.suffix in [".py", ".js", ".ts", ".json", ".md", ".txt", ".yml", ".yaml"]:
                    if extracted_file.stat().st_size < 512 * 1024:  # < 512KB
                        # Bestimme Kategorie basierend auf Quellarchiv
                        if "LocalAgent" in zip_file.name:
                            category = "localagent_pro"
                        elif "vscode-icons" in zip_file.name:
                            category = "vscode_extensions"
                        elif "dashboard" in zip_file.name:
                            category = "dashboard_skeleton"
                        else:
                            category = "misc_archives"

                        kb_path = copy_to_knowledgebase(extracted_file, category)
                        stats["kb_entries"] += 1

    # ─────────────────────────────────────────────────────────────────────────
    # 4. Generiere Index-Bericht
    # ─────────────────────────────────────────────────────────────────────────

    logger.info("\n[4/4] Generiere Index-Bericht...")

    report = {
        "indexer_version": "1.1.0",  # Version erhöht wegen ZIP-Support
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "statistics": stats,
        "auto_index_dir": str(AUTO_INDEX_DIR),
        "extraction_dir": str(EXTRACTION_DIR),
        "knowledgebase_dir": str(KNOWLEDGEBASE_DIR),
        "metadata_file": str(METADATA_FILE),
        "additional_archives_count": len([f for f in ADDITIONAL_ARCHIVES if f.exists()]),
    }

    report_file = AUTO_INDEX_DIR / f"index_report_{int(time.time())}.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # Safepoint: Completion
    write_safepoint("elion_indexer", "opena3", "INDEX_COMPLETE", report)

    # ─────────────────────────────────────────────────────────────────────────
    # Ausgabe
    # ─────────────────────────────────────────────────────────────────────────

    logger.info("\n" + "=" * 80)
    logger.info("ELION Auto-Indexer abgeschlossen")
    logger.info("=" * 80)
    logger.info(f"Gesamte Dateien:      {stats['total_files']}")
    logger.info(f"Neue Dateien:         {stats['new_files']}")
    logger.info(f"Aktualisierte Dateien:{stats['updated_files']}")
    logger.info(f"Übersprungene Dateien:{stats['skipped_files']}")
    logger.info(f"Extrahierte Archive:  {stats['extracted_archives']}")
    logger.info(f"Knowledgebase-Einträge:{stats['kb_entries']}")
    logger.info("=" * 80)
    logger.info(f"Index-Bericht: {report_file}")
    logger.info(f"Metadata-Datei: {METADATA_FILE}")
    logger.info("=" * 80)


# ──────────────────────────────────────────────────────────────────────────────
# CLI Interface
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ELION Auto-Indexer für OpenWebUI Integration")
    parser.add_argument("--dry-run", action="store_true", help="Simuliere Indexierung ohne Änderungen")
    parser.add_argument("--verbose", action="store_true", help="Verbose Logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.dry_run:
        logger.warning("DRY RUN MODE - Keine Änderungen werden vorgenommen")
        sys.exit(0)

    try:
        auto_index_all()
    except KeyboardInterrupt:
        logger.warning("\nIndexierung durch Benutzer abgebrochen")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Fehler bei Auto-Indexierung: {e}")
        sys.exit(1)
