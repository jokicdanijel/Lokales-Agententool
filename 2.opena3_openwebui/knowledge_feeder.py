#!/usr/bin/env python3
"""
ELION Knowledgebase Auto-Feeder
- Automatisches Füttern der Knowledgebase mit indexierten Inhalten
- Intelligente Kategorisierung und Deduplikation
- Safepoint-Integration für alle Operationen
"""

import json
import logging
import os
import sys
import time
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

AUTO_INDEX_DIR = OPENA3_DIR / "auto_indexed"
METADATA_FILE = AUTO_INDEX_DIR / "index_metadata.jsonl"
KB_INDEX_FILE = KNOWLEDGEBASE_DIR / "kb_index.jsonl"

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("elion.kb_feeder")

# ──────────────────────────────────────────────────────────────────────────────
# Safepoint Utilities
# ──────────────────────────────────────────────────────────────────────────────


def write_safepoint(src: str, dst: str, kind: str, body: dict[str, Any]) -> Path:
    """Schreibt Safepoint für KB-Feeding-Operationen."""
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
# Knowledgebase Index Management
# ──────────────────────────────────────────────────────────────────────────────


def load_kb_index() -> dict[str, Any]:
    """Lädt bestehenden Knowledgebase-Index."""
    if not KB_INDEX_FILE.exists():
        return {}

    kb_index = {}
    with KB_INDEX_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line.strip())
            kb_index[entry["file_hash"]] = entry
    return kb_index


def save_kb_entry(entry: dict[str, Any]):
    """Speichert KB-Index-Eintrag."""
    KB_INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with KB_INDEX_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def categorize_file(filepath: Path) -> str:
    """Bestimmt Kategorie basierend auf Dateiname und Pfad."""
    name_lower = filepath.name.lower()

    # Bridge/Integration Files
    if "bridge" in name_lower or "relay" in name_lower:
        return "integration"

    # OpenWebUI spezifisch
    if "openwebui" in name_lower or "open-webui" in name_lower:
        return "openwebui"

    # Configuration
    if name_lower in ["config.json", "settings.json", ".env"]:
        return "config"

    # Database
    if "db" in name_lower or "database" in name_lower:
        return "database"

    # Documentation
    if filepath.suffix in [".md", ".txt", ".rst"]:
        return "documentation"

    # Code
    if filepath.suffix in [".py", ".js", ".ts"]:
        return "code"

    # Data
    if filepath.suffix in [".json", ".yaml", ".yml", ".csv"]:
        return "data"

    return "misc"


def extract_metadata(filepath: Path) -> dict[str, Any]:
    """Extrahiert erweiterte Metadata aus Datei."""
    metadata = {"category": categorize_file(filepath), "tags": []}

    # Extrahiere Tags aus Dateiname
    name = filepath.stem.lower()

    tag_keywords = {
        "api": ["api", "endpoint", "rest"],
        "auth": ["auth", "token", "bearer", "login"],
        "chat": ["chat", "message", "conversation"],
        "github": ["github", "webhook", "git"],
        "telegram": ["telegram", "bot", "tg"],
        "docker": ["docker", "container", "compose"],
        "database": ["db", "database", "sql", "sqlite"],
        "config": ["config", "settings", "env"],
    }

    for tag, keywords in tag_keywords.items():
        if any(kw in name for kw in keywords):
            metadata["tags"].append(tag)

    return metadata


# ──────────────────────────────────────────────────────────────────────────────
# Auto-Feeding Workflow
# ──────────────────────────────────────────────────────────────────────────────


def auto_feed_knowledgebase():
    """Hauptfunktion für automatisches Knowledgebase-Feeding."""
    logger.info("=" * 80)
    logger.info("ELION Knowledgebase Auto-Feeder gestartet")
    logger.info("=" * 80)

    # Lade Indizes
    kb_index = load_kb_index()
    logger.info(f"Bestehende KB-Einträge: {len(kb_index)}")

    # Statistiken
    stats = {"total_scanned": 0, "new_entries": 0, "duplicates_skipped": 0, "categories": {}}

    # Safepoint: Start
    write_safepoint(
        "kb_feeder",
        "knowledgebase",
        "FEED_START",
        {"timestamp": datetime.utcnow().isoformat() + "Z", "kb_dir": str(KNOWLEDGEBASE_DIR)},
    )

    # ─────────────────────────────────────────────────────────────────────────
    # Scanne Knowledgebase-Verzeichnis
    # ─────────────────────────────────────────────────────────────────────────

    logger.info("\nScanne Knowledgebase-Verzeichnis...")

    for root, dirs, files in os.walk(KNOWLEDGEBASE_DIR):
        for filename in files:
            filepath = Path(root) / filename

            # Überspringe Index-Dateien und temporäre Dateien
            if filename.startswith(".") or filename.endswith((".jsonl", ".tmp")):
                continue

            stats["total_scanned"] += 1

            try:
                # Berechne Hash
                import hashlib

                sha256 = hashlib.sha256()
                with filepath.open("rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        sha256.update(chunk)
                file_hash = sha256.hexdigest()

                # Prüfe auf Duplikate
                if file_hash in kb_index:
                    stats["duplicates_skipped"] += 1
                    logger.debug(f"  ⊙ Bereits in KB: {filename}")
                    continue

                # Extrahiere Metadata
                metadata = extract_metadata(filepath)
                category = metadata["category"]

                # Update Kategorie-Statistik
                stats["categories"][category] = stats["categories"].get(category, 0) + 1

                # Erstelle KB-Eintrag
                kb_entry = {
                    "file_path": str(filepath),
                    "file_name": filename,
                    "file_hash": file_hash,
                    "file_size": filepath.stat().st_size,
                    "category": category,
                    "tags": metadata["tags"],
                    "added_at": datetime.utcnow().isoformat() + "Z",
                    "relative_path": str(filepath.relative_to(KNOWLEDGEBASE_DIR)),
                }

                # Speichere in KB-Index
                save_kb_entry(kb_entry)
                stats["new_entries"] += 1

                logger.info(f"  + Neu in KB: {filename} [{category}]")

            except Exception as e:
                logger.error(f"  ✗ Fehler bei {filename}: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # Generiere Bericht
    # ─────────────────────────────────────────────────────────────────────────

    report = {
        "feeder_version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "statistics": stats,
        "kb_index_file": str(KB_INDEX_FILE),
        "kb_entries_total": len(kb_index) + stats["new_entries"],
    }

    report_file = KNOWLEDGEBASE_DIR / f"feed_report_{int(time.time())}.json"
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # Safepoint: Completion
    write_safepoint("kb_feeder", "knowledgebase", "FEED_COMPLETE", report)

    # ─────────────────────────────────────────────────────────────────────────
    # Ausgabe
    # ─────────────────────────────────────────────────────────────────────────

    logger.info("\n" + "=" * 80)
    logger.info("ELION Knowledgebase Auto-Feeder abgeschlossen")
    logger.info("=" * 80)
    logger.info(f"Gescannte Dateien:    {stats['total_scanned']}")
    logger.info(f"Neue KB-Einträge:     {stats['new_entries']}")
    logger.info(f"Duplikate übersprungen:{stats['duplicates_skipped']}")
    logger.info(f"Gesamt KB-Einträge:   {len(kb_index) + stats['new_entries']}")
    logger.info("\nKategorien:")
    for category, count in sorted(stats["categories"].items()):
        logger.info(f"  {category:20s}: {count}")
    logger.info("=" * 80)
    logger.info(f"KB-Index: {KB_INDEX_FILE}")
    logger.info(f"Bericht:  {report_file}")
    logger.info("=" * 80)


# ──────────────────────────────────────────────────────────────────────────────
# CLI Interface
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ELION Knowledgebase Auto-Feeder")
    parser.add_argument("--verbose", action="store_true", help="Verbose Logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        auto_feed_knowledgebase()
    except KeyboardInterrupt:
        logger.warning("\nFeeding durch Benutzer abgebrochen")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Fehler bei Auto-Feeding: {e}")
        sys.exit(1)
