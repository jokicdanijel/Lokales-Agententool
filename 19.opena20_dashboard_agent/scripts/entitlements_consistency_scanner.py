#!/usr/bin/env python3
"""
Entitlements Consistency Scanner
==================================
Verifies HTML doesn't hardcode entitlement logic.

FAIL-HARD RULES:
1. NO hardcoded plan logic in HTML (no if plan=="basic")
2. NO inline agent enable/disable (use entitlements.json)
3. Basic plan: Exactly 4 clickable agents (via entitlements, not HTML)
4. Plan hierarchy preserved (HTML reads JSON, doesn't compute)
5. NO agent unlocking logic in JavaScript/HTML

EXIT CODES:
- 0: Entitlements properly externalized
- 1: Hardcoded logic found (CI MUST break)

Usage:
  python3 scripts/entitlements_consistency_scanner.py
"""

import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

# ============================================================================
# VIOLATION PATTERNS
# ============================================================================

HARDCODE_PATTERNS = [
    # Plan string literals
    (r'(?i)if.*plan\s*===?\s*["\'](?:basic|pro|premium|ultimum)["\']', "Hardcoded plan check", "critical"),
    (r'(?i)plan\s*===?\s*["\'](?:basic|pro|premium|ultimum)["\']', "Plan string comparison", "critical"),
    # Agent enable/disable logic
    (r"(?i)(?:enable|disable|unlock|activate).*opena\d+", "Agent enable/disable logic", "critical"),
    (r"(?i)opena\d+.*(?:enabled|disabled|locked|unlocked)", "Agent state logic", "critical"),
    # Clickable array definitions
    (r"(?i)clickable\s*=\s*\[.*opena.*\]", "Hardcoded clickable array", "critical"),
    (r"(?i)allowed_agents\s*=\s*\[", "Hardcoded allowed agents", "critical"),
    # Plan hierarchy in code
    (r"(?i)if.*basic.*opena[347]", "Basic plan logic in code", "critical"),
    (r"(?i)switch.*plan.*case.*basic", "Switch-case plan logic", "error"),
    # Inline checks
    (r'(?i)user\.plan\s*[!=]==?\s*["\']', "User plan inline check", "error"),
]

ACCEPTABLE_PATTERNS = [
    # These are OK (reading from API/JSON)
    r"fetch.*entitlements\.json",
    r"entitlements\[plan\]",
    r"entitlements\.get\(",
    r"data-plan=",  # HTML attribute
]


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class EntitlementsViolation:
    """A detected entitlements hardcoding violation"""

    file: str
    line_number: int
    violation_type: str
    context: str
    severity: str = "critical"


@dataclass
class ScanResult:
    """Overall scan result"""

    timestamp: str
    passed: bool
    files_scanned: int = 0
    violations: list[EntitlementsViolation] = field(default_factory=list)


# ============================================================================
# SCANNER
# ============================================================================


class EntitlementsConsistencyScanner:
    """Scanner for entitlements consistency"""

    SCAN_FOLDERS: ClassVar[list[str]] = ["webpanel"]
    SCAN_EXTENSIONS: ClassVar[set[str]] = {".html", ".js", ".ts"}
    EXCLUDED_PATTERNS: ClassVar[set[str]] = {
        "node_modules/",
        ".venv/",
        "__pycache__/",
        ".git/",
        "entitlements-demo.html",  # Demo file is allowed
    }

    def __init__(self, project_root: Path):
        self.root = project_root
        self.entitlements_path = project_root / "build" / "entitlements.json"
        self.result = ScanResult(timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"), passed=False)

        # Compile patterns
        self.hardcode_patterns = [(re.compile(p), name, severity) for p, name, severity in HARDCODE_PATTERNS]
        self.acceptable_patterns = [re.compile(p) for p in ACCEPTABLE_PATTERNS]

    def should_scan_file(self, file_path: Path) -> bool:
        """Determine if file should be scanned"""
        # Check extension
        if file_path.suffix not in self.SCAN_EXTENSIONS:
            return False

        # Check excluded patterns
        path_str = str(file_path)
        for pattern in self.EXCLUDED_PATTERNS:
            if pattern in path_str:
                return False

        # Only scan specific folders
        for folder in self.SCAN_FOLDERS:
            if folder in path_str:
                return True

        return False

    def is_acceptable(self, line: str) -> bool:
        """Check if line matches acceptable patterns"""
        for pattern in self.acceptable_patterns:
            if pattern.search(line):
                return True
        return False

    def scan_file(self, file_path: Path):
        """Scan single file for hardcoded logic"""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            return

        rel_path = str(file_path.relative_to(self.root))

        for line_num, line in enumerate(lines, 1):
            # Skip if acceptable pattern
            if self.is_acceptable(line):
                continue

            # Check hardcode patterns
            for pattern, name, severity in self.hardcode_patterns:
                if pattern.search(line):
                    self.result.violations.append(
                        EntitlementsViolation(
                            file=rel_path,
                            line_number=line_num,
                            violation_type=name,
                            context=line.strip()[:120],
                            severity=severity,
                        )
                    )

    def check_entitlements_file(self) -> bool:
        """Verify entitlements.json exists and is valid"""
        if not self.entitlements_path.exists():
            print(f"✗ Entitlements file missing: {self.entitlements_path}")
            return False

        try:
            with open(self.entitlements_path) as f:
                data = json.load(f)

            # Check structure
            if "plans" not in data:
                print("✗ Entitlements missing 'plans' key")
                return False

            # Check basic plan
            basic = data["plans"].get("basic", {})
            clickable = basic.get("clickable_agents", [])

            if len(clickable) != 4:
                print(f"✗ Basic plan should have exactly 4 clickable agents, got {len(clickable)}")
                return False

            expected = {"opena3", "opena4", "opena7", "opena11"}
            actual = set(clickable)

            if actual != expected:
                print("✗ Basic clickable agents mismatch")
                print(f"   Expected: {expected}")
                print(f"   Actual: {actual}")
                return False

            print("✓ Entitlements file valid")
            print(f"  Basic plan: {len(clickable)} clickable agents")
            return True

        except Exception as e:
            print(f"✗ Failed to load entitlements: {e}")
            return False

    def run_scan(self) -> bool:
        """Run full consistency scan"""
        print(f"\n{'='*60}")
        print("ENTITLEMENTS CONSISTENCY SCANNER")
        print(f"{'='*60}\n")

        # Check entitlements file first
        if not self.check_entitlements_file():
            return False

        print("\nScanning for hardcoded logic...")
        print(f"Folders: {', '.join(self.SCAN_FOLDERS)}")
        print(f"Extensions: {', '.join(self.SCAN_EXTENSIONS)}\n")

        # Find all scannable files
        all_files = []
        for folder in self.SCAN_FOLDERS:
            folder_path = self.root / folder
            if folder_path.exists():
                for ext in self.SCAN_EXTENSIONS:
                    all_files.extend(folder_path.rglob(f"*{ext}"))

        scannable = [f for f in all_files if self.should_scan_file(f)]
        self.result.files_scanned = len(scannable)

        print(f"Files to scan: {len(scannable)}")

        # Scan each file
        for file_path in scannable:
            self.scan_file(file_path)

        print(f"\n✓ Scanned {self.result.files_scanned} files")

        # Group violations by severity
        critical = [v for v in self.result.violations if v.severity == "critical"]
        errors = [v for v in self.result.violations if v.severity == "error"]

        print("\nViolations found:")
        print(f"  Critical: {len(critical)}")
        print(f"  Errors: {len(errors)}")

        # Determine pass/fail
        self.result.passed = len(self.result.violations) == 0

        return self.result.passed

    def generate_report(self, output_path: Path):
        """Generate JSON and MD reports"""
        result_dict = asdict(self.result)

        # JSON
        json_path = output_path.with_suffix(".json")
        json_path.parent.mkdir(parents=True, exist_ok=True)

        with open(json_path, "w") as f:
            json.dump(result_dict, f, indent=2)

        print(f"\n✓ JSON report: {json_path}")

        # MD
        md_lines = [
            "# Entitlements Consistency Scan Report",
            "",
            f"**Timestamp:** {self.result.timestamp}",
            f"**Status:** {'✅ PASSED' if self.result.passed else '❌ FAILED'}",
            "",
            "## Summary",
            "",
            f"- Files scanned: {self.result.files_scanned}",
            f"- Total violations: {len(self.result.violations)}",
            "",
        ]

        if self.result.violations:
            # Group by severity
            critical = [v for v in self.result.violations if v.severity == "critical"]
            errors = [v for v in self.result.violations if v.severity == "error"]

            if critical:
                md_lines.extend(
                    [
                        "## 🔴 CRITICAL VIOLATIONS",
                        "",
                    ]
                )
                for v in critical:
                    md_lines.append(f"### {v.file}:{v.line_number}")
                    md_lines.append(f"- **Type:** {v.violation_type}")
                    md_lines.append(f"- **Context:** `{v.context}`")
                    md_lines.append("")

            if errors:
                md_lines.extend(
                    [
                        "## ⚠️ ERRORS",
                        "",
                    ]
                )
                for v in errors:
                    md_lines.append(f"### {v.file}:{v.line_number}")
                    md_lines.append(f"- **Type:** {v.violation_type}")
                    md_lines.append(f"- **Context:** `{v.context}`")
                    md_lines.append("")

        if self.result.passed:
            md_lines.extend(
                [
                    "## ✅ All Checks Passed",
                    "",
                    "- No hardcoded entitlement logic found",
                    "- HTML/JS properly reads entitlements.json",
                    "- Basic plan correctly configured (4 clickable agents)",
                ]
            )

        md_path = output_path.with_suffix(".md")
        with open(md_path, "w") as f:
            f.write("\n".join(md_lines))

        print(f"✓ MD report: {md_path}")


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent

    scanner = EntitlementsConsistencyScanner(project_root)
    success = scanner.run_scan()

    # Generate reports
    artifacts_dir = project_root / "artifacts" / "scans"
    scanner.generate_report(artifacts_dir / "entitlements_consistency_scan")

    # Summary
    print(f"\n{'='*60}")
    print("SCAN SUMMARY")
    print(f"{'='*60}")

    if success:
        print("✅ ENTITLEMENTS CONSISTENCY VERIFIED")
        print("✅ No hardcoded logic found")
        print("✅ Proper externalization via entitlements.json")
        return 0
    else:
        print("❌ CONSISTENCY VIOLATIONS DETECTED")
        print(f"   Total violations: {len(scanner.result.violations)}")
        print("\n⚠️  CI MUST BREAK - Hardcoded entitlement logic found")
        return 1


if __name__ == "__main__":
    sys.exit(main())
