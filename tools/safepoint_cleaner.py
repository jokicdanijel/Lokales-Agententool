#!/usr/bin/env python3
"""
PORTIER 3.0 Safepoint Cleaner Tool
Reinigt und organisiert Safepoint-Archive

Features:
- Alte Safepoints archivieren
- Defekte JSON-Dateien reparieren
- index.jsonl neu aufbauen
- Statistiken und Reports
- Batch-Operationen
"""

import argparse
import json
import logging
import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


class SafepointCleaner:
    """PORTIER 3.0 Safepoint Maintenance & Cleanup Tool"""

    def __init__(self, archivp_root: str = "/tmp/archivp_store"):
        self.archivp_root = Path(archivp_root)
        self.index_file = self.archivp_root / "index.jsonl"
        self.backup_dir = self.archivp_root / "_backups"

        # Logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("safepoint_cleaner")

        # Stats
        self.stats = {
            "files_processed": 0,
            "files_archived": 0,
            "files_repaired": 0,
            "files_deleted": 0,
            "index_entries_rebuilt": 0,
            "errors": [],
        }

    def clean_old_safepoints(self, days_old: int = 30) -> dict[str, int]:
        """Archiviert Safepoints älter als X Tage"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        archived_count = 0

        self.logger.info(f"Archiving safepoints older than {days_old} days ({cutoff_date.strftime('%Y-%m-%d')})")

        # Erstelle Backup-Verzeichnis
        self.backup_dir.mkdir(exist_ok=True)
        archive_target = self.backup_dir / f"archived_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        archive_target.mkdir(exist_ok=True)

        # Durchlaufe alle YYYY-Ordner
        for year_dir in self.archivp_root.glob("????"):
            if not year_dir.is_dir() or year_dir.name.startswith("_"):
                continue

            # Durchlaufe MM-Ordner
            for month_dir in year_dir.glob("??"):
                if not month_dir.is_dir():
                    continue

                # Durchlaufe DD-Ordner
                for day_dir in month_dir.glob("??"):
                    if not day_dir.is_dir():
                        continue

                    # Prüfe Datum
                    try:
                        dir_date = datetime.strptime(f"{year_dir.name}-{month_dir.name}-{day_dir.name}", "%Y-%m-%d")
                        if dir_date < cutoff_date:
                            # Archiviere kompletten Tag
                            shutil.move(
                                str(day_dir), str(archive_target / f"{year_dir.name}_{month_dir.name}_{day_dir.name}")
                            )
                            archived_count += 1
                            self.logger.info(f"Archived {year_dir.name}/{month_dir.name}/{day_dir.name}")
                    except ValueError:
                        self.logger.warning(f"Invalid date directory: {day_dir}")

        self.stats["files_archived"] = archived_count
        return {"archived_directories": archived_count, "archive_location": str(archive_target)}

    def repair_corrupted_json(self) -> dict[str, int]:
        """Repariert defekte JSON-Dateien"""
        repaired_count = 0
        error_count = 0

        self.logger.info("Scanning for corrupted JSON files...")

        # Durchlaufe alle .json Dateien
        for json_file in self.archivp_root.rglob("*.json"):
            if json_file.parent.name.startswith("_"):  # Skip backup dirs
                continue

            try:
                # Versuche JSON zu lesen
                content = json_file.read_text(encoding="utf-8")
                json.loads(content)  # Validierung
                self.stats["files_processed"] += 1

            except json.JSONDecodeError as e:
                self.logger.warning(f"Corrupted JSON: {json_file} - {e}")

                # Backup erstellen
                backup_file = self.backup_dir / "corrupted" / json_file.name
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(json_file, backup_file)

                # Versuche zu reparieren
                if self._repair_json_file(json_file):
                    repaired_count += 1
                    self.logger.info(f"Repaired: {json_file}")
                else:
                    error_count += 1
                    self.stats["errors"].append(f"Could not repair: {json_file}")

        self.stats["files_repaired"] = repaired_count
        return {"repaired": repaired_count, "errors": error_count}

    def _repair_json_file(self, json_file: Path) -> bool:
        """Versucht eine defekte JSON-Datei zu reparieren"""
        try:
            content = json_file.read_text(encoding="utf-8")

            # Häufige JSON-Reparaturen
            # 1. Trailing comma entfernen
            content = content.replace(",}", "}").replace(",]", "]")

            # 2. Fehlende Anführungszeichen bei Schlüsseln
            import re

            content = re.sub(r"(\w+):", r'"\1":', content)

            # 3. Escape-Zeichen korrigieren
            content = content.replace("\\", "\\\\").replace('"\\"', '\\"')

            # Test ob repariert
            json.loads(content)

            # Schreibe reparierte Datei
            json_file.write_text(content, encoding="utf-8")
            return True

        except Exception:
            return False

    def rebuild_index(self) -> dict[str, int]:
        """Baut index.jsonl aus vorhandenen Safepoint-Dateien neu auf"""
        self.logger.info("Rebuilding index.jsonl from existing safepoints...")

        # Backup des alten Index
        if self.index_file.exists():
            backup_index = self.backup_dir / f"index_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
            backup_index.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.index_file, backup_index)

        # Neuen Index aufbauen
        new_entries = []

        # Durchlaufe alle Safepoint-Dateien
        for json_file in self.archivp_root.rglob("SP*.json"):
            if json_file.parent.name.startswith("_"):  # Skip backups
                continue

            try:
                # Safepoint laden
                content = json.loads(json_file.read_text(encoding="utf-8"))

                # Index-Eintrag erstellen
                index_entry = {
                    "file": json_file.name,
                    "ts": content.get("timestamp", ""),
                    "category": content.get("category", ""),
                    "source": content.get("source", ""),
                    "destination": content.get("destination", ""),
                    "request_id": content.get("request_id", ""),
                }

                new_entries.append(index_entry)

            except Exception as e:
                self.logger.warning(f"Could not process {json_file}: {e}")
                self.stats["errors"].append(f"Index rebuild error: {json_file} - {e}")

        # Index-Datei schreiben
        with open(self.index_file, "w", encoding="utf-8") as f:
            for entry in sorted(new_entries, key=lambda x: x["ts"]):
                f.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")

        self.stats["index_entries_rebuilt"] = len(new_entries)
        self.logger.info(f"Rebuilt index with {len(new_entries)} entries")

        return {"entries": len(new_entries), "backup_location": str(backup_index) if self.index_file.exists() else None}

    def validate_safepoints(self) -> dict[str, Any]:
        """Validiert alle Safepoints auf PORTIER 3.0 Konformität"""
        validation_results = {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "validation_errors": [],
            "categories": {"CMD": 0, "RESP": 0, "ROUTE": 0, "DISPATCH": 0},
            "agents": {},
        }

        self.logger.info("Validating PORTIER 3.0 compliance...")

        for json_file in self.archivp_root.rglob("SP*.json"):
            if json_file.parent.name.startswith("_"):
                continue

            validation_results["total_files"] += 1

            try:
                content = json.loads(json_file.read_text(encoding="utf-8"))

                # PORTIER 3.0 Schema validieren
                required_fields = ["timestamp", "source", "destination", "category", "request_id", "payload"]
                missing_fields = [field for field in required_fields if field not in content]

                if missing_fields:
                    validation_results["invalid_files"] += 1
                    validation_results["validation_errors"].append(
                        {"file": str(json_file), "error": f"Missing fields: {missing_fields}"}
                    )
                    continue

                # Kategorie validieren
                category = content.get("category", "")
                if category not in ["CMD", "RESP", "ROUTE", "DISPATCH"]:
                    validation_results["invalid_files"] += 1
                    validation_results["validation_errors"].append(
                        {"file": str(json_file), "error": f"Invalid category: {category}"}
                    )
                    continue

                # Unicode-Pfeil im Dateinamen prüfen
                if "→" not in json_file.name:
                    validation_results["invalid_files"] += 1
                    validation_results["validation_errors"].append(
                        {"file": str(json_file), "error": "Missing Unicode arrow in filename"}
                    )
                    continue

                # Statistiken aktualisieren
                validation_results["valid_files"] += 1
                validation_results["categories"][category] += 1

                source = content.get("source", "unknown")
                validation_results["agents"][source] = validation_results["agents"].get(source, 0) + 1

            except Exception as e:
                validation_results["invalid_files"] += 1
                validation_results["validation_errors"].append({"file": str(json_file), "error": f"JSON error: {e}"})

        return validation_results

    def generate_report(self) -> str:
        """Generiert ausführlichen Maintenance-Report"""
        report_lines = [
            "🔥 PORTIER 3.0 Safepoint Maintenance Report",
            "=" * 50,
            f"Generated: {datetime.now(UTC).isoformat()}",
            f"Archivp Root: {self.archivp_root}",
            "",
            "📊 Processing Statistics:",
            f"  • Files Processed: {self.stats['files_processed']}",
            f"  • Files Archived: {self.stats['files_archived']}",
            f"  • Files Repaired: {self.stats['files_repaired']}",
            f"  • Index Entries Rebuilt: {self.stats['index_entries_rebuilt']}",
            "",
        ]

        # Disk Usage
        try:
            total_size = sum(f.stat().st_size for f in self.archivp_root.rglob("*") if f.is_file())
            report_lines.extend(
                [
                    "💾 Storage Usage:",
                    f"  • Total Size: {total_size / (1024*1024):.1f} MB",
                    f"  • Safepoint Files: {len(list(self.archivp_root.rglob('SP*.json')))}",
                    f"  • Index Size: {self.index_file.stat().st_size if self.index_file.exists() else 0} bytes",
                    "",
                ]
            )
        except Exception:
            pass

        # Errors
        if self.stats["errors"]:
            report_lines.extend(
                [
                    "❌ Errors:",
                    *[f"  • {error}" for error in self.stats["errors"][:10]],
                    (
                        ""
                        if len(self.stats["errors"]) <= 10
                        else f"  • ... and {len(self.stats['errors']) - 10} more errors"
                    ),
                    "",
                ]
            )

        report_lines.extend(
            [
                "✅ Maintenance completed successfully!",
                f"🔧 Backup location: {self.backup_dir}",
            ]
        )

        return "\n".join(report_lines)


def main():
    """CLI für Safepoint Cleaner"""
    parser = argparse.ArgumentParser(description="PORTIER 3.0 Safepoint Maintenance Tool")
    parser.add_argument("--archivp-root", default="/tmp/archivp_store", help="Archivp root directory")
    parser.add_argument("--clean-days", type=int, default=30, help="Archive safepoints older than N days")
    parser.add_argument("--repair-json", action="store_true", help="Repair corrupted JSON files")
    parser.add_argument("--rebuild-index", action="store_true", help="Rebuild index.jsonl")
    parser.add_argument("--validate", action="store_true", help="Validate PORTIER 3.0 compliance")
    parser.add_argument("--all", action="store_true", help="Run all maintenance tasks")

    args = parser.parse_args()

    # Cleaner erstellen
    cleaner = SafepointCleaner(args.archivp_root)

    print("🔥 PORTIER 3.0 Safepoint Cleaner")
    print("=" * 40)

    # Tasks ausführen
    if args.all or args.clean_days:
        print("🗂️ Cleaning old safepoints...")
        result = cleaner.clean_old_safepoints(args.clean_days)
        print(f"✓ Archived {result['archived_directories']} directories")

    if args.all or args.repair_json:
        print("🔧 Repairing corrupted JSON...")
        result = cleaner.repair_corrupted_json()
        print(f"✓ Repaired {result['repaired']} files, {result['errors']} errors")

    if args.all or args.rebuild_index:
        print("📝 Rebuilding index...")
        result = cleaner.rebuild_index()
        print(f"✓ Rebuilt index with {result['entries']} entries")

    if args.all or args.validate:
        print("✅ Validating compliance...")
        result = cleaner.validate_safepoints()
        print(f"✓ {result['valid_files']}/{result['total_files']} files valid")
        if result["validation_errors"]:
            print(f"⚠️ {len(result['validation_errors'])} validation errors found")

    # Report generieren
    print("\n" + cleaner.generate_report())


if __name__ == "__main__":
    main()
