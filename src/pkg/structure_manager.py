#!/usr/bin/env python3
"""
Structure Manager - Portier Project Structure Validator & Normalizer
Orchestriert Kategorisierung, Konflikt-Isolation, Berichtsgenerierung
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

# Configuration
INCLUDE_GLOBS = [
    "src/**/*.py",
    "configs/**/*.{json,yaml,yml}",
    "assets/**/*.{css,js,html}",
    "assets/img/**/*.{png,jpg,svg}",
    "scripts/**/*.sh",
    "docs/**/*.md",
]

EXCLUDE_GLOBS = [
    "**/.venv/**",
    "**/.git/**",
    "**/node_modules/**",
    "**/*.lock",
    "**/backups/**",
    "**/_conflicts/**",
    "**/__pycache__/**",
    "**/*.pyc",
]

CONFLICT_KEYWORDS = {
    "demo",
    "demonstration",
    "simulation",
    "simulator",
    "phantom",
    "phantoms",
    "mock",
    "mocks",
    "example",
    "examples",
    "fixture",
    "fixtures",
    "test_",
    "tests_",
}

MAX_DEPTH = 6
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


class StructureManager:
    def __init__(self, root: Path = Path("."), dry_run: bool = True):
        self.root = root
        self.dry_run = dry_run
        self.rename_map: dict[str, str] = {}
        self.conflicts: list[dict] = []
        self.violations: list[dict] = []
        self.files_checked = 0
        self.files_moved = 0
        self.files_conflicted = 0

    def validate_depth(self, path: Path) -> bool:
        """Überprüfe Dateipfad-Tiefe"""
        depth = len(path.relative_to(self.root).parts)
        if depth > MAX_DEPTH:
            self.violations.append(
                {
                    "type": "depth_exceeded",
                    "path": str(path),
                    "depth": depth,
                    "max": MAX_DEPTH,
                }
            )
            return False
        return True

    def has_conflict_keyword(self, name: str) -> bool:
        """Überprüfe auf Konflikt-Keywords"""
        name_lower = name.lower()
        return any(kw in name_lower for kw in CONFLICT_KEYWORDS)

    def categorize_file(self, path: Path) -> tuple[Path, bool]:
        """Kategorisiere Datei, gebe Zielpath und Konflikt-Flag zurück"""
        name = path.name
        suffix = path.suffix.lower()

        is_conflict = self.has_conflict_keyword(name)

        if is_conflict:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            conflict_dir = self.root / "_conflicts" / timestamp
            return conflict_dir / name, True

        # Normale Kategorisierung
        if suffix in [".py"]:
            if "test" in name.lower():
                return self.root / "src" / "tests" / name, False
            else:
                return self.root / "src" / "pkg" / name, False

        if suffix in [".md"]:
            return self.root / "docs" / name, False

        if suffix in [".json", ".yaml", ".yml"]:
            return self.root / "configs" / name, False

        if suffix in [".sh"]:
            return self.root / "scripts" / name, False

        if suffix in [".css", ".js", ".html", ".jinja", ".jinja2"]:
            return self.root / "assets" / name, False

        if suffix in [".png", ".jpg", ".jpeg", ".svg", ".gif"]:
            return self.root / "assets" / "img" / name, False

        # Default: bleibe im aktuellen Verzeichnis
        return path, False

    def scan_project(self) -> None:
        """Scanne Projekt auf Strukturverletzungen"""
        print(f"[Scan] Scanning project at {self.root}...")

        for fpath in self.root.rglob("*"):
            if fpath.is_file() and not any(part.startswith(".") for part in fpath.parts):
                self.files_checked += 1

                # Tiefe prüfen
                if not self.validate_depth(fpath):
                    continue

                # Kategorisierung
                target_path, is_conflict = self.categorize_file(fpath)

                if target_path != fpath:
                    self.rename_map[str(fpath.relative_to(self.root))] = str(target_path.relative_to(self.root))
                    self.files_moved += 1

                    if is_conflict:
                        self.conflicts.append(
                            {
                                "original": str(fpath.relative_to(self.root)),
                                "target": str(target_path.relative_to(self.root)),
                                "size": fpath.stat().st_size,
                                "reason": "conflict_keyword",
                            }
                        )
                        self.files_conflicted += 1

        print(
            f"[Scan] Scanned {self.files_checked} files, {self.files_moved} changes needed, {self.files_conflicted} conflicts"
        )

    def apply_changes(self) -> None:
        """Wende Änderungen an (nur wenn nicht dry_run)"""
        if self.dry_run:
            print("[DryRun] Changes NOT applied (dry-run mode)")
            return

        print("[Apply] Applying structure changes...")

        for src, dst in self.rename_map.items():
            src_path = self.root / src
            dst_path = self.root / dst

            if src_path.exists():
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                src_path.rename(dst_path)
                print(f"  ✓ {src} → {dst}")
                self.files_moved += 1

        print(f"[Apply] {len(self.rename_map)} files reorganized")

    def generate_reports(self) -> None:
        """Erzeuge Reports"""
        print("[Reports] Generating...")

        # 1. rename_map.csv
        with open(self.root / "rename_map.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["source", "destination"])
            for src, dst in self.rename_map.items():
                writer.writerow([src, dst])
        print(f"  ✓ rename_map.csv ({len(self.rename_map)} entries)")

        # 2. path_index.json
        files_index = {
            "generated_at": datetime.now().isoformat(),
            "total_files": self.files_checked,
            "files": [{"path": k, "category": "categorized"} for k in self.rename_map.keys()],
        }
        with open(self.root / "path_index.json", "w") as f:
            json.dump(files_index, f, indent=2)
        print("  ✓ path_index.json")

        # 3. violations_report.md
        with open(self.root / "violations_report.md", "w") as f:
            f.write("# Project Structure Violations Report\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")

            if not self.violations and not self.conflicts:
                f.write("✅ **No violations found.**\n")
            else:
                if self.violations:
                    f.write("## Violations\n\n")
                    for v in self.violations:
                        f.write(f"- `{v.get('path', 'unknown')}` - {v.get('type', 'unknown')}\n")

                if self.conflicts:
                    f.write(f"\n## Conflicts ({len(self.conflicts)})\n\n")
                    for c in self.conflicts[:10]:  # Top 10
                        size_kb = c.get("size", 0) / 1024
                        f.write(f"- `{c['original']}` → `{c['target']}` ({size_kb:.1f} KB)\n")

        print("  ✓ violations_report.md")

        # 4. structure_checkpoint.json
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "files_checked": self.files_checked,
            "files_moved": self.files_moved,
            "conflicts": self.files_conflicted,
            "violations_count": len(self.violations),
            "status": "ready_for_apply" if self.dry_run else "applied",
        }
        with open(self.root / "structure_checkpoint.json", "w") as f:
            json.dump(checkpoint, f, indent=2)
        print("  ✓ structure_checkpoint.json")


def main():
    parser = argparse.ArgumentParser(description="Portier Structure Manager")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry-run)")
    parser.add_argument("--symlinks", action="store_true", help="Create symlinks for moved files")
    parser.add_argument("--root", default=".", help="Project root directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    manager = StructureManager(root, dry_run=not args.apply)

    print(f"\n{'='*70}")
    print(f"Portier Structure Manager - {'APPLY' if args.apply else 'DRY-RUN'}")
    print(f"{'='*70}\n")

    manager.scan_project()
    manager.generate_reports()

    print(f"\n{'='*70}")
    print("Summary:")
    print(f"  Files checked: {manager.files_checked}")
    print(f"  Changes needed: {manager.files_moved}")
    print(f"  Conflicts: {manager.files_conflicted}")
    print(f"  Violations: {len(manager.violations)}")
    print(f"{'='*70}\n")

    if args.apply and manager.files_moved > 0:
        manager.apply_changes()

    return 0


if __name__ == "__main__":
    sys.exit(main())
