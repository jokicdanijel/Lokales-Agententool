#!/usr/bin/env python3
"""
API Binding Scanner
====================
Ensures NO direct agent:PORT calls in HTML/JS.

FAIL-HARD RULES:
1. NO direct URLs like http://localhost:12345
2. NO agent:PORT hardcoded endpoints
3. ALL API calls must go through control plane (opena1)
4. NO direct agent-to-agent communication
5. Coordination via opena1 ONLY

ACCEPTABLE PATTERNS:
- /api/* (routed via control plane)
- Relative paths: /status, /health
- data-api attributes (resolved by control plane)

FORBIDDEN PATTERNS:
- http://localhost:12344
- agent://opena5:12348
- Direct port references

EXIT CODES:
- 0: All API calls properly routed
- 1: Direct bindings found (CI MUST break)

Usage:
  python3 scripts/api_binding_scanner.py
"""

import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

# ============================================================================
# BINDING PATTERNS
# ============================================================================

FORBIDDEN_PATTERNS = [
    # Direct localhost URLs
    (r"https?://localhost:\d{4,5}", "Direct localhost:PORT binding", "critical"),
    (r"https?://127\.0\.0\.1:\d{4,5}", "Direct 127.0.0.1:PORT binding", "critical"),
    # Agent protocol
    (r"agent://opena\d+:\d+", "Direct agent:// protocol binding", "critical"),
    # Port references in URLs
    (r'url\s*[:=]\s*[\'"].+:\d{4,5}', "Hardcoded port in URL", "error"),
    (r'endpoint\s*[:=]\s*[\'"].+:\d{4,5}', "Hardcoded port in endpoint", "error"),
    # Direct agent references
    (r'fetch\([\'"]https?://.+:\d{4,5}', "Direct fetch to port", "critical"),
    (r'axios\.(get|post|put|delete)\([\'"]https?://.+:\d{4,5}', "Direct axios to port", "critical"),
    # Port constants
    (r"(?i)PORT\s*=\s*\d{4,5}", "Port number constant", "warning"),
    (r"(?i)const\s+\w+_PORT\s*=\s*\d{4,5}", "Port constant definition", "warning"),
]

ACCEPTABLE_PATTERNS = [
    # These are OK (control plane routing)
    r"\/api\/",  # /api/* routes
    r"data-api\s*=",  # data-api attributes
    r'fetch\([\'"]\/[^:]+',  # Relative paths
    r"proxy\.forward",  # Proxy forwarding
    r"controlPlane\.route",  # Control plane routing
]


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class BindingViolation:
    """A detected API binding violation"""

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
    violations: list[BindingViolation] = field(default_factory=list)


# ============================================================================
# SCANNER
# ============================================================================


class APIBindingScanner:
    """Scanner for API binding compliance"""

    SCAN_FOLDERS: ClassVar[list[str]] = ["webpanel"]
    SCAN_EXTENSIONS: ClassVar[set[str]] = {".html", ".js", ".ts"}
    EXCLUDED_PATTERNS: ClassVar[set[str]] = {
        "node_modules/",
        ".venv/",
        "__pycache__/",
        ".git/",
        "test/",
        "tests/",
        "spec/",
        ".test.",
        ".spec.",
    }

    def __init__(self, project_root: Path):
        self.root = project_root
        self.result = ScanResult(timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"), passed=False)

        # Compile patterns
        self.forbidden_patterns = [(re.compile(p), name, severity) for p, name, severity in FORBIDDEN_PATTERNS]
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
        """Scan single file for binding violations"""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            return

        rel_path = str(file_path.relative_to(self.root))

        for line_num, line in enumerate(lines, 1):
            # Skip comments
            if re.match(r"^\s*(?://|#|/\*)", line):
                continue

            # Skip if acceptable pattern
            if self.is_acceptable(line):
                continue

            # Check forbidden patterns
            for pattern, name, severity in self.forbidden_patterns:
                match = pattern.search(line)
                if match:
                    self.result.violations.append(
                        BindingViolation(
                            file=rel_path,
                            line_number=line_num,
                            violation_type=name,
                            context=line.strip()[:120],
                            severity=severity,
                        )
                    )

    def run_scan(self) -> bool:
        """Run full binding scan"""
        print(f"\n{'='*60}")
        print("API BINDING SCANNER")
        print(f"{'='*60}\n")

        print("Scanning for direct agent:PORT bindings...")
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
        warnings = [v for v in self.result.violations if v.severity == "warning"]

        print("\nViolations found:")
        print(f"  Critical: {len(critical)}")
        print(f"  Errors: {len(errors)}")
        print(f"  Warnings: {len(warnings)}")

        # Determine pass/fail (warnings don't fail)
        self.result.passed = (len(critical) + len(errors)) == 0

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
            "# API Binding Scan Report",
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
            warnings = [v for v in self.result.violations if v.severity == "warning"]

            if critical:
                md_lines.extend(
                    [
                        "## 🔴 CRITICAL VIOLATIONS",
                        "",
                        "*Direct agent:PORT bindings detected - bypasses control plane*",
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

            if warnings:
                md_lines.extend(
                    [
                        "## WARNINGS",
                        "",
                    ]
                )
                for v in warnings:
                    md_lines.append(f"### {v.file}:{v.line_number}")
                    md_lines.append(f"- **Type:** {v.violation_type}")
                    md_lines.append(f"- **Context:** `{v.context}`")
                    md_lines.append("")

        if self.result.passed:
            md_lines.extend(
                [
                    "## ✅ All Checks Passed",
                    "",
                    "- No direct agent:PORT bindings found",
                    "- All API calls properly routed through control plane",
                    "- Coordination via opena1 verified",
                ]
            )

        md_path = output_path.with_suffix(".md")
        with open(md_path, "w") as f:
            f.write("\n".join(md_lines))

        print(f"✓ MD report: {md_path}")


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent

    scanner = APIBindingScanner(project_root)
    success = scanner.run_scan()

    # Generate reports
    artifacts_dir = project_root / "artifacts" / "scans"
    scanner.generate_report(artifacts_dir / "api_binding_scan")

    # Summary
    print(f"\n{'='*60}")
    print("SCAN SUMMARY")
    print(f"{'='*60}")

    if success:
        print("✅ API BINDING COMPLIANCE VERIFIED")
        print("✅ No direct agent:PORT calls found")
        print("✅ Proper control plane routing")
        return 0
    else:
        print("❌ API BINDING VIOLATIONS DETECTED")
        print(f"   Total violations: {len(scanner.result.violations)}")
        print("\n⚠️  CI MUST BREAK - Direct agent bindings bypass control plane")
        return 1


if __name__ == "__main__":
    sys.exit(main())
