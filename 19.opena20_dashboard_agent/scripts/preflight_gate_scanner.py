#!/usr/bin/env python3
"""
Preflight Gate Scanner
=======================
Verifies exact step ordering and blocking behavior.

FAIL-HARD RULES:
1. All 8 scanners must be called in preflight
2. EXACT ORDER enforced (no parallel, no reordering)
3. Each scanner MUST block on failure (exit 1)
4. No steps skipped
5. CI config must call preflight.sh

EXPECTED PREFLIGHT ORDER:
1. ports_ids_compliance_scanner.py
2. folder_coverage_scanner.py
3. secrets_vault_scanner.py
4. html_contract_scanner.py
5. public_website_scanner.py
6. entitlements_consistency_scanner.py
7. api_binding_scanner.py
8. preflight_gate_scanner.py (self-check)

EXIT CODES:
- 0: Preflight properly configured
- 1: Gate violations found (CI MUST break)

Usage:
  python3 scripts/preflight_gate_scanner.py
"""

import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

# tracing
from scripts.tracing import init_tracing  # init tracing for scripts

# ============================================================================
# EXPECTED CONFIGURATION
# ============================================================================

EXPECTED_SCANNERS = [
    "ports_ids_compliance_scanner.py",
    "folder_coverage_scanner.py",
    "secrets_vault_scanner.py",
    "html_contract_scanner.py",
    "public_website_scanner.py",
    "entitlements_consistency_scanner.py",
    "api_binding_scanner.py",
    "preflight_gate_scanner.py",
]


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class GateViolation:
    """A preflight gate violation"""

    category: str
    violation: str
    severity: str = "critical"
    context: str | None = None


@dataclass
class ScanResult:
    """Overall scan result"""

    timestamp: str
    passed: bool
    violations: list[GateViolation] = field(default_factory=list)
    scanner_files_found: list[str] = field(default_factory=list)
    preflight_script_found: bool = False
    ci_config_found: bool = False


# ============================================================================
# SCANNER
# ============================================================================


class PreflightGateScanner:
    """Scanner for preflight gate ordering and blocking"""

    def __init__(self, project_root: Path):
        self.root = project_root
        self.scripts_dir = project_root / "scripts"
        self.preflight_path = project_root / "scripts" / "preflight.sh"
        self.ci_paths = [
            project_root / ".github" / "workflows",
            project_root / ".gitlab-ci.yml",
            project_root / "Jenkinsfile",
        ]

        self.result = ScanResult(timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"), passed=False)

    def check_scanner_files_exist(self):
        """Verify all scanner files exist"""
        print("Checking scanner files...")

        for scanner in EXPECTED_SCANNERS:
            scanner_path = self.scripts_dir / scanner

            if scanner_path.exists():
                self.result.scanner_files_found.append(scanner)
                print(f"  ✓ {scanner}")
            else:
                self.result.violations.append(
                    GateViolation(
                        category="missing_scanner", violation=f"Scanner file missing: {scanner}", severity="critical"
                    )
                )
                print(f"  ✗ {scanner} - MISSING")

    def check_preflight_script(self):
        """Verify preflight.sh exists and has correct structure"""
        print("\nChecking preflight script...")

        if not self.preflight_path.exists():
            self.result.violations.append(
                GateViolation(
                    category="missing_preflight", violation="preflight.sh not found in scripts/", severity="critical"
                )
            )
            print("  ✗ preflight.sh - MISSING")
            return

        self.result.preflight_script_found = True
        print("  ✓ preflight.sh exists")

        # Parse preflight.sh
        try:
            with open(self.preflight_path) as f:
                content = f.read()
        except Exception as e:
            self.result.violations.append(
                GateViolation(
                    category="preflight_unreadable", violation=f"Cannot read preflight.sh: {e}", severity="critical"
                )
            )
            return

        # Extract python3 "$SCRIPT_DIR/..." calls
        pattern = r'python3\s+["\']?\$SCRIPT_DIR/(\w+\.py)["\']?'
        calls = re.findall(pattern, content)

        print(f"\n  Found {len(calls)} scanner calls in preflight.sh")

        # Check all scanners are called
        for scanner in EXPECTED_SCANNERS:
            if scanner not in calls:
                self.result.violations.append(
                    GateViolation(
                        category="scanner_not_called",
                        violation=f"Scanner not called in preflight: {scanner}",
                        severity="critical",
                    )
                )
                print(f"    ✗ {scanner} - NOT CALLED")

        # Check ordering
        called_scanners = [s for s in calls if s in EXPECTED_SCANNERS]

        for i, expected in enumerate(EXPECTED_SCANNERS):
            if i < len(called_scanners):
                actual = called_scanners[i]
                if actual != expected:
                    self.result.violations.append(
                        GateViolation(
                            category="wrong_order",
                            violation=f"Scanner order wrong at position {i+1}",
                            severity="error",
                            context=f"Expected: {expected}, Got: {actual}",
                        )
                    )
                    print(f"    ✗ Position {i+1}: expected {expected}, got {actual}")

        # Check for blocking (|| exit 1)
        blocking_pattern = r'python3\s+["\']?\$SCRIPT_DIR/\w+\.py["\']?\s*\|\|\s*exit\s+1'
        blocking_calls = re.findall(blocking_pattern, content)

        if len(blocking_calls) < len(EXPECTED_SCANNERS):
            self.result.violations.append(
                GateViolation(
                    category="missing_blocking",
                    violation="Not all scanners have blocking behavior (|| exit 1)",
                    severity="critical",
                    context=f"Expected {len(EXPECTED_SCANNERS)}, got {len(blocking_calls)}",
                )
            )
            print(f"    ✗ Blocking: {len(blocking_calls)}/{len(EXPECTED_SCANNERS)}")
        else:
            print(f"    ✓ Blocking: {len(blocking_calls)}/{len(EXPECTED_SCANNERS)}")

    def check_ci_config(self):
        """Verify CI config calls preflight.sh"""
        print("\nChecking CI configuration...")

        found_ci = False

        # Check GitHub Actions
        gh_workflows = self.root / ".github" / "workflows"
        if gh_workflows.exists():
            for workflow_file in gh_workflows.glob("*.yml"):
                try:
                    with open(workflow_file) as f:
                        content = f.read()

                    if "preflight.sh" in content or "preflight" in content:
                        found_ci = True
                        print(f"  ✓ GitHub Actions calls preflight: {workflow_file.name}")
                        break
                except Exception:
                    pass

        # Check GitLab CI
        gitlab_ci = self.root / ".gitlab-ci.yml"
        if gitlab_ci.exists():
            try:
                with open(gitlab_ci) as f:
                    content = f.read()

                if "preflight.sh" in content or "preflight" in content:
                    found_ci = True
                    print("  ✓ GitLab CI calls preflight")
            except Exception:
                pass

        self.result.ci_config_found = found_ci

        if not found_ci:
            self.result.violations.append(
                GateViolation(
                    category="ci_no_preflight", violation="CI config doesn't call preflight.sh", severity="critical"
                )
            )
            print("  ✗ No CI config calls preflight.sh")

    def run_scan(self) -> bool:
        """Run full gate scan"""
        print(f"\n{'='*60}")
        print("PREFLIGHT GATE SCANNER")
        print(f"{'='*60}\n")

        print(f"Expected scanners: {len(EXPECTED_SCANNERS)}\n")

        # Check scanner files
        self.check_scanner_files_exist()

        # Check preflight script
        self.check_preflight_script()

        # Check CI config
        self.check_ci_config()

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
            "# Preflight Gate Scan Report",
            "",
            f"**Timestamp:** {self.result.timestamp}",
            f"**Status:** {'✅ PASSED' if self.result.passed else '❌ FAILED'}",
            "",
            "## Summary",
            "",
            f"- Scanner files found: {len(self.result.scanner_files_found)}/{len(EXPECTED_SCANNERS)}",
            f"- Preflight script exists: {self.result.preflight_script_found}",
            f"- CI config found: {self.result.ci_config_found}",
            f"- Total violations: {len(self.result.violations)}",
            "",
        ]

        if self.result.violations:
            # Group by category
            by_category = {}
            for v in self.result.violations:
                if v.category not in by_category:
                    by_category[v.category] = []
                by_category[v.category].append(v)

            md_lines.extend(["## Violations", ""])

            for category, violations in by_category.items():
                md_lines.append(f"### {category.replace('_', ' ').title()}")
                md_lines.append("")

                for v in violations:
                    severity_icon = {"critical": "🔴", "error": "⚠️", "warning": "i"}
                    icon = severity_icon.get(v.severity, "•")
                    md_lines.append(f"- {icon} {v.violation}")
                    if v.context:
                        md_lines.append(f"  - *{v.context}*")

                md_lines.append("")

        if self.result.passed:
            md_lines.extend(
                [
                    "## ✅ All Gate Checks Passed",
                    "",
                    "- All 8 scanner files exist",
                    "- Preflight script properly configured",
                    "- Correct scanner ordering enforced",
                    "- Blocking behavior verified (|| exit 1)",
                    "- CI config calls preflight.sh",
                ]
            )

        md_path = output_path.with_suffix(".md")
        with open(md_path, "w") as f:
            f.write("\n".join(md_lines))

        print(f"✓ MD report: {md_path}")


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent

    scanner = PreflightGateScanner(project_root)
    success = scanner.run_scan()

    # Generate reports
    artifacts_dir = project_root / "artifacts" / "scans"
    scanner.generate_report(artifacts_dir / "preflight_gate_scan")

    # Summary
    print(f"\n{'='*60}")
    print("SCAN SUMMARY")
    print(f"{'='*60}")

    if success:
        print("✅ PREFLIGHT GATE CONFIGURATION VERIFIED")
        print("✅ All scanners properly ordered and blocking")
        print("✅ CI integration confirmed")
        return 0
    else:
        print("❌ PREFLIGHT GATE VIOLATIONS DETECTED")
        print(f"   Total violations: {len(scanner.result.violations)}")
        print("\n⚠️  CI MUST BREAK - Preflight gate misconfigured")
        return 1


if __name__ == "__main__":
    # initialize tracing for this script
    init_tracing("preflight_gate_scanner")
    sys.exit(main())
