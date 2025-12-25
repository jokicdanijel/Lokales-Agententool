#!/usr/bin/env python3
"""
🧹 PORTIER 3.0 Cleaner & Inspector
=================================

Zentrales Tool für:
- Safepoint-Client Validierung
- Code-Qualitätsprüfung
- System-Wartung
- Archiv-Bereinigung
- Performance-Inspektion
- Konformitätschecks

Version: 3.0
Datum: 29. November 2025
Autor: ELION Team
"""

import argparse
import json
import logging
import shutil
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("cleaner_inspector")


@dataclass
class InspectionResult:
    """Ergebnis einer Inspektion."""

    component: str
    status: str  # OK, WARNING, ERROR
    message: str
    details: dict[str, Any] | None = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(UTC).isoformat()


@dataclass
class CleanupResult:
    """Ergebnis einer Bereinigung."""

    operation: str
    files_removed: int
    bytes_freed: int
    errors: list[str]
    duration: float


class SafepointClientInspector:
    """Inspektor für Safepoint-Clients."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.agent_dirs = [
            d
            for d in project_root.glob("[0-9]*.*")
            if d.is_dir()
            and d.name.startswith(
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
            )
        ]

    def inspect_all_clients(self) -> list[InspectionResult]:
        """Inspiziert alle Safepoint-Clients."""
        results = []

        for agent_dir in self.agent_dirs:
            safepoint_file = agent_dir / "safepoint_client.py"

            if not safepoint_file.exists():
                results.append(
                    InspectionResult(
                        component=agent_dir.name,
                        status="ERROR",
                        message="Safepoint-Client fehlt",
                        details={"expected_path": str(safepoint_file)},
                    )
                )
                continue

            # Syntax-Check
            syntax_result = self._check_syntax(safepoint_file)
            if syntax_result.status != "OK":
                results.append(syntax_result)
                continue

            # PORTIER 3.0 Compliance Check
            compliance_result = self._check_portier30_compliance(safepoint_file)
            results.append(compliance_result)

            # Performance Check
            perf_result = self._check_performance_patterns(safepoint_file)
            results.append(perf_result)

        return results

    def _check_syntax(self, file_path: Path) -> InspectionResult:
        """Prüft Python-Syntax."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            compile(content, str(file_path), "exec")

            return InspectionResult(component=file_path.parent.name, status="OK", message="Syntax korrekt")
        except SyntaxError as e:
            return InspectionResult(
                component=file_path.parent.name,
                status="ERROR",
                message=f"Syntax-Fehler: {e.msg}",
                details={"line": e.lineno, "offset": e.offset, "text": e.text},
            )
        except Exception as e:
            return InspectionResult(
                component=file_path.parent.name, status="ERROR", message=f"Unerwarteter Fehler: {e!s}"
            )

    def _check_portier30_compliance(self, file_path: Path) -> InspectionResult:
        """Prüft PORTIER 3.0 Konformität."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            compliance_checks = {
                "imports_correct": all(
                    imp in content for imp in ["import os", "import httpx", "from datetime import datetime, timezone"]
                ),
                "safepoint_class": "class SafepointClient:" in content,
                "async_write": "async def write(" in content,
                "mask_function": "def mask(obj):" in content,
                "secret_masking": all(
                    secret in content for secret in ["token", "auth", "password", "apikey", "secret", "key"]
                ),
                "http_post": "client.post(" in content,
                "bearer_auth": '"Authorization"' in content and "Bearer" in content,
                "timeout": "timeout=15.0" in content,
                "env_vars": "os.getenv" in content,
                "type_hints": ": str" in content and ": dict" in content,
            }

            passed = sum(compliance_checks.values())
            total = len(compliance_checks)

            if passed == total:
                status = "OK"
                message = "Vollständig PORTIER 3.0 konform"
            elif passed >= total * 0.8:
                status = "WARNING"
                message = f"Größtenteils konform ({passed}/{total})"
            else:
                status = "ERROR"
                message = f"Nicht konform ({passed}/{total})"

            return InspectionResult(
                component=file_path.parent.name, status=status, message=message, details=compliance_checks
            )

        except Exception as e:
            return InspectionResult(
                component=file_path.parent.name, status="ERROR", message=f"Compliance-Check fehlgeschlagen: {e!s}"
            )

    def _check_performance_patterns(self, file_path: Path) -> InspectionResult:
        """Prüft Performance-Patterns."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            perf_issues = []

            # Async/Await Pattern
            if "def write(" in content and "async def write(" not in content:
                perf_issues.append("write() sollte async sein")

            # Context Manager für HTTP Client
            if "httpx.AsyncClient()" in content and "async with" not in content:
                perf_issues.append("AsyncClient sollte mit 'async with' verwendet werden")

            # Timeout gesetzt
            if "client.post(" in content and "timeout=" not in content:
                perf_issues.append("HTTP Timeout fehlt")

            # JSON Serialization
            if "json.dumps" in content:
                perf_issues.append("Manuelle JSON-Serialization - httpx macht das automatisch")

            if not perf_issues:
                status = "OK"
                message = "Performance-Patterns korrekt"
            else:
                status = "WARNING"
                message = f"{len(perf_issues)} Performance-Verbesserungen möglich"

            return InspectionResult(
                component=file_path.parent.name, status=status, message=message, details={"issues": perf_issues}
            )

        except Exception as e:
            return InspectionResult(
                component=file_path.parent.name, status="ERROR", message=f"Performance-Check fehlgeschlagen: {e!s}"
            )


class SystemCleaner:
    """System-Bereiniger."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def clean_python_cache(self) -> CleanupResult:
        """Bereinigt Python-Cache-Dateien."""
        start_time = time.time()
        files_removed = 0
        bytes_freed = 0
        errors = []

        try:
            # __pycache__ Ordner
            for pycache_dir in self.project_root.rglob("__pycache__"):
                try:
                    size = sum(f.stat().st_size for f in pycache_dir.rglob("*") if f.is_file())
                    shutil.rmtree(pycache_dir)
                    bytes_freed += size
                    files_removed += 1
                except Exception as e:
                    errors.append(f"Fehler beim Löschen {pycache_dir}: {e!s}")

            # .pyc Dateien
            for pyc_file in self.project_root.rglob("*.pyc"):
                try:
                    size = pyc_file.stat().st_size
                    pyc_file.unlink()
                    bytes_freed += size
                    files_removed += 1
                except Exception as e:
                    errors.append(f"Fehler beim Löschen {pyc_file}: {e!s}")

        except Exception as e:
            errors.append(f"Allgemeiner Fehler: {e!s}")

        duration = time.time() - start_time

        return CleanupResult(
            operation="Python Cache Cleanup",
            files_removed=files_removed,
            bytes_freed=bytes_freed,
            errors=errors,
            duration=duration,
        )

    def clean_log_files(self, max_age_days: int = 7) -> CleanupResult:
        """Bereinigt alte Log-Dateien."""
        start_time = time.time()
        files_removed = 0
        bytes_freed = 0
        errors = []

        try:
            cutoff_time = time.time() - (max_age_days * 24 * 3600)

            # .log Dateien
            for log_file in self.project_root.rglob("*.log"):
                try:
                    if log_file.stat().st_mtime < cutoff_time:
                        size = log_file.stat().st_size
                        log_file.unlink()
                        bytes_freed += size
                        files_removed += 1
                except Exception as e:
                    errors.append(f"Fehler beim Löschen {log_file}: {e!s}")

            # .nohup.log Dateien
            for nohup_file in self.project_root.rglob("*.nohup.log"):
                try:
                    if nohup_file.stat().st_mtime < cutoff_time:
                        size = nohup_file.stat().st_size
                        nohup_file.unlink()
                        bytes_freed += size
                        files_removed += 1
                except Exception as e:
                    errors.append(f"Fehler beim Löschen {nohup_file}: {e!s}")

        except Exception as e:
            errors.append(f"Allgemeiner Fehler: {e!s}")

        duration = time.time() - start_time

        return CleanupResult(
            operation=f"Log Cleanup (>{max_age_days} Tage)",
            files_removed=files_removed,
            bytes_freed=bytes_freed,
            errors=errors,
            duration=duration,
        )

    def clean_temp_files(self) -> CleanupResult:
        """Bereinigt temporäre Dateien."""
        start_time = time.time()
        files_removed = 0
        bytes_freed = 0
        errors = []

        temp_patterns = ["*.tmp", "*.temp", "*~", ".DS_Store", "Thumbs.db", "*.swp", "*.swo"]

        try:
            for pattern in temp_patterns:
                for temp_file in self.project_root.rglob(pattern):
                    try:
                        size = temp_file.stat().st_size
                        temp_file.unlink()
                        bytes_freed += size
                        files_removed += 1
                    except Exception as e:
                        errors.append(f"Fehler beim Löschen {temp_file}: {e!s}")

        except Exception as e:
            errors.append(f"Allgemeiner Fehler: {e!s}")

        duration = time.time() - start_time

        return CleanupResult(
            operation="Temp Files Cleanup",
            files_removed=files_removed,
            bytes_freed=bytes_freed,
            errors=errors,
            duration=duration,
        )


class ArchiveInspector:
    """Archiv-Inspektor für Safepoints."""

    def __init__(self, archivp_root: Path):
        self.archivp_root = archivp_root

    def inspect_archive_structure(self) -> InspectionResult:
        """Inspiziert Archiv-Struktur."""
        if not self.archivp_root.exists():
            return InspectionResult(
                component="archivp",
                status="WARNING",
                message="Archiv-Ordner existiert nicht",
                details={"path": str(self.archivp_root)},
            )

        # Prüfe YYYY/MM/DD Struktur
        year_dirs = [d for d in self.archivp_root.iterdir() if d.is_dir() and d.name.isdigit() and len(d.name) == 4]

        structure_info = {
            "year_dirs": len(year_dirs),
            "total_safepoints": 0,
            "index_exists": (self.archivp_root / "index.jsonl").exists(),
            "latest_year": max([d.name for d in year_dirs]) if year_dirs else None,
        }

        # Zähle Safepoints
        for sp_file in self.archivp_root.rglob("SP*.json"):
            structure_info["total_safepoints"] += 1

        if structure_info["total_safepoints"] > 0:
            status = "OK"
            message = f"Archiv OK - {structure_info['total_safepoints']} Safepoints"
        else:
            status = "WARNING"
            message = "Archiv leer"

        return InspectionResult(component="archivp", status=status, message=message, details=structure_info)

    def inspect_safepoint_integrity(self) -> list[InspectionResult]:
        """Prüft Integrität einzelner Safepoints."""
        results = []
        corrupt_count = 0
        valid_count = 0

        for sp_file in self.archivp_root.rglob("SP*.json"):
            try:
                with open(sp_file, encoding="utf-8") as f:
                    data = json.load(f)

                # PORTIER 3.0 Schema-Validierung
                required_fields = [
                    "timestamp",
                    "sp_timestamp",
                    "source",
                    "destination",
                    "category",
                    "request_id",
                    "payload",
                    "strict",
                ]

                missing_fields = [field for field in required_fields if field not in data]

                if missing_fields:
                    results.append(
                        InspectionResult(
                            component=sp_file.name,
                            status="ERROR",
                            message=f"Fehlende Felder: {', '.join(missing_fields)}",
                            details={"path": str(sp_file)},
                        )
                    )
                    corrupt_count += 1
                else:
                    valid_count += 1

            except json.JSONDecodeError:
                results.append(
                    InspectionResult(
                        component=sp_file.name,
                        status="ERROR",
                        message="Ungültiges JSON",
                        details={"path": str(sp_file)},
                    )
                )
                corrupt_count += 1
            except Exception as e:
                results.append(
                    InspectionResult(
                        component=sp_file.name,
                        status="ERROR",
                        message=f"Lesefehler: {e!s}",
                        details={"path": str(sp_file)},
                    )
                )
                corrupt_count += 1

        # Summary
        if corrupt_count == 0:
            summary_status = "OK"
            summary_message = f"Alle {valid_count} Safepoints sind valide"
        else:
            summary_status = "WARNING" if corrupt_count < valid_count * 0.1 else "ERROR"
            summary_message = f"{corrupt_count} korrupte, {valid_count} valide Safepoints"

        results.insert(
            0,
            InspectionResult(
                component="safepoint_integrity",
                status=summary_status,
                message=summary_message,
                details={"valid": valid_count, "corrupt": corrupt_count},
            ),
        )

        return results


class PortierCleanerInspector:
    """Hauptklasse für Cleaner & Inspector."""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.safepoint_inspector = SafepointClientInspector(self.project_root)
        self.system_cleaner = SystemCleaner(self.project_root)
        self.archive_inspector = ArchiveInspector(self.project_root / "archivp")

    def run_full_inspection(self) -> dict[str, list[InspectionResult]]:
        """Führt vollständige System-Inspektion durch."""
        logger.info("Starte vollständige System-Inspektion...")

        results = {
            "safepoint_clients": self.safepoint_inspector.inspect_all_clients(),
            "archive_structure": [self.archive_inspector.inspect_archive_structure()],
            "archive_integrity": self.archive_inspector.inspect_safepoint_integrity(),
        }

        logger.info("System-Inspektion abgeschlossen")
        return results

    def run_full_cleanup(self, max_log_age_days: int = 7) -> dict[str, CleanupResult]:
        """Führt vollständige System-Bereinigung durch."""
        logger.info("Starte vollständige System-Bereinigung...")

        results = {
            "python_cache": self.system_cleaner.clean_python_cache(),
            "log_files": self.system_cleaner.clean_log_files(max_log_age_days),
            "temp_files": self.system_cleaner.clean_temp_files(),
        }

        logger.info("System-Bereinigung abgeschlossen")
        return results

    def generate_report(
        self, inspection_results: dict[str, list[InspectionResult]], cleanup_results: dict[str, CleanupResult] = None
    ) -> str:
        """Generiert einen detaillierten Report."""
        report_lines = []
        report_lines.append("🧹 PORTIER 3.0 Cleaner & Inspector Report")
        report_lines.append("=" * 50)
        report_lines.append(f"Timestamp: {datetime.now(UTC).isoformat()}")
        report_lines.append(f"Project Root: {self.project_root}")
        report_lines.append("")

        # Inspection Results
        report_lines.append("📋 INSPEKTION")
        report_lines.append("-" * 20)

        for category, results in inspection_results.items():
            report_lines.append(f"\n{category.upper().replace('_', ' ')}:")

            status_counts = {"OK": 0, "WARNING": 0, "ERROR": 0}

            for result in results:
                status_counts[result.status] = status_counts.get(result.status, 0) + 1

                status_icon = "✅" if result.status == "OK" else "⚠️" if result.status == "WARNING" else "❌"
                report_lines.append(f"  {status_icon} {result.component}: {result.message}")

                if result.details and result.status != "OK":
                    for key, value in result.details.items():
                        report_lines.append(f"    └─ {key}: {value}")

            report_lines.append(
                f"  Summary: {status_counts['OK']} OK, {status_counts['WARNING']} Warnings, {status_counts['ERROR']} Errors"
            )

        # Cleanup Results
        if cleanup_results:
            report_lines.append("\n🧽 BEREINIGUNG")
            report_lines.append("-" * 20)

            total_files = sum(r.files_removed for r in cleanup_results.values())
            total_bytes = sum(r.bytes_freed for r in cleanup_results.values())
            total_duration = sum(r.duration for r in cleanup_results.values())

            for operation, result in cleanup_results.items():
                report_lines.append(f"\n{operation.upper().replace('_', ' ')}:")
                report_lines.append(f"  📁 Dateien entfernt: {result.files_removed}")
                report_lines.append(f"  💾 Speicher freigegeben: {self._format_bytes(result.bytes_freed)}")
                report_lines.append(f"  ⏱️ Duration: {result.duration:.2f}s")

                if result.errors:
                    report_lines.append(f"  ⚠️ Fehler ({len(result.errors)}):")
                    for error in result.errors[:5]:  # Max 5 Fehler anzeigen
                        report_lines.append(f"    └─ {error}")
                    if len(result.errors) > 5:
                        report_lines.append(f"    └─ ... und {len(result.errors) - 5} weitere")

            report_lines.append(
                f"\nGESAMT: {total_files} Dateien, {self._format_bytes(total_bytes)} freigegeben in {total_duration:.2f}s"
            )

        return "\n".join(report_lines)

    def _format_bytes(self, bytes_count: int) -> str:
        """Formatiert Byte-Anzahl lesbar."""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} TB"


def main():
    """Hauptfunktion für CLI."""
    parser = argparse.ArgumentParser(description="PORTIER 3.0 Cleaner & Inspector")

    parser.add_argument("--inspect", action="store_true", help="Führt Inspektion durch")
    parser.add_argument("--clean", action="store_true", help="Führt Bereinigung durch")
    parser.add_argument("--full", action="store_true", help="Führt Inspektion + Bereinigung durch")
    parser.add_argument("--project-root", help="Projekt-Root-Pfad", default=None)
    parser.add_argument("--max-log-age", type=int, default=7, help="Max Alter für Log-Dateien (Tage)")
    parser.add_argument("--output", help="Output-Datei für Report", default=None)
    parser.add_argument("--quiet", action="store_true", help="Weniger Output")

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    # Default: Full Operation
    if not (args.inspect or args.clean):
        args.full = True

    try:
        inspector = PortierCleanerInspector(args.project_root)

        inspection_results = None
        cleanup_results = None

        if args.inspect or args.full:
            inspection_results = inspector.run_full_inspection()

        if args.clean or args.full:
            cleanup_results = inspector.run_full_cleanup(args.max_log_age)

        # Report generieren
        report = inspector.generate_report(inspection_results or {}, cleanup_results)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"Report gespeichert: {args.output}")
        else:
            print(report)

        # Exit Code basierend auf Ergebnissen
        if inspection_results:
            error_count = sum(sum(1 for r in results if r.status == "ERROR") for results in inspection_results.values())
            if error_count > 0:
                sys.exit(1)

    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {e!s}")
        sys.exit(1)


if __name__ == "__main__":
    main()
