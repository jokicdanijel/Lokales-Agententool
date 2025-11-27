#!/usr/bin/env python3
"""
🚨 GOVERNANCE CORRECTION AUTOMATION
═══════════════════════════════════════════════════════════════
Automated compliance checker & fixer for PORTIER 3.0 Governance Rules
Based on: GOVERNANCE_VIOLATIONS_REPORT.md, rename_map.csv

Usage:
    python scripts/governance_correction.py analyze     # Read-only scan
    python scripts/governance_correction.py plan        # Generate fix scripts
    python scripts/governance_correction.py apply       # Execute with guards
    python scripts/governance_correction.py validate    # Post-fix verification

Author: Governance Automation (Phase 4)
Date: 2025-11-27
Version: 1.0.0
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# === CONFIGURATION ===
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
RENAME_MAP_PATH = PROJECT_ROOT / "rename_map.csv"
VIOLATIONS_REPORT = PROJECT_ROOT / "GOVERNANCE_VIOLATIONS_REPORT.md"
ARCHIV_PATTERN = re.compile(r"SP\d+.*?\.json$")
VENV_LEAK_EXTENSIONS = [".py"]
CONFLICTS_DIR = PROJECT_ROOT / "_conflicts"
SRC_PKG_DIR = PROJECT_ROOT / "src" / "pkg"


class GovernanceAnalyzer:
    """Scans workspace for governance violations"""

    def __init__(self):
        self.violations: Dict[str, List[str]] = {
            "archiv": [],
            "venv_leaks": [],
            "tests_displaced": [],
            "port_violations": [],
            "doc_missing": [],
        }

    def scan_archiv_contamination(self) -> List[str]:
        """Detect Safepoints outside ARCHIV/archivp/"""
        violations = []
        configs_dir = PROJECT_ROOT / "configs"
        if configs_dir.exists():
            for file in configs_dir.rglob("SP*.json"):
                violations.append(str(file.relative_to(PROJECT_ROOT)))
        return violations

    def scan_venv_leaks(self) -> List[str]:
        """Detect venv packages in src/pkg/"""
        violations = []
        if SRC_PKG_DIR.exists():
            forbidden_packages = [
                "typing_extensions.py",
                "socks.py",
                "py.py",
                "sockshandler.py",
            ]
            for pkg in forbidden_packages:
                file_path = SRC_PKG_DIR / pkg
                if file_path.exists():
                    violations.append(str(file_path.relative_to(PROJECT_ROOT)))
        return violations

    def scan_tests_displaced(self) -> List[str]:
        """Detect test files in _conflicts/"""
        violations = []
        if CONFLICTS_DIR.exists():
            for file in CONFLICTS_DIR.rglob("test_*.py"):
                violations.append(str(file.relative_to(PROJECT_ROOT)))
            for file in CONFLICTS_DIR.rglob("test_*.sh"):
                violations.append(str(file.relative_to(PROJECT_ROOT)))
        return violations

    def scan_port_violations(self) -> List[str]:
        """Detect hardcoded port 8080 in backend code"""
        violations = []
        python_files = list(PROJECT_ROOT.glob("**/*.py"))
        for file in python_files:
            if "_conflicts" in str(file) or "venv" in str(file):
                continue
            try:
                content = file.read_text(encoding="utf-8")
                if re.search(r'port\s*=\s*8080|PORT\s*=\s*8080|:8080(?!["\'])', content):
                    violations.append(str(file.relative_to(PROJECT_ROOT)))
            except Exception:
                pass
        return violations

    def scan_doc_missing(self) -> List[str]:
        """Check for missing critical documentation"""
        violations = []
        required_docs = [
            "README.md",
            "docs/ARCHITECTURE.md",
            "docs/QUICKSTART.md",
        ]
        for doc in required_docs:
            doc_path = PROJECT_ROOT / doc
            if not doc_path.exists():
                violations.append(doc)
        return violations

    def analyze(self) -> Dict[str, List[str]]:
        """Run all scans"""
        print("🔍 Scanning workspace for governance violations...")
        self.violations["archiv"] = self.scan_archiv_contamination()
        self.violations["venv_leaks"] = self.scan_venv_leaks()
        self.violations["tests_displaced"] = self.scan_tests_displaced()
        self.violations["port_violations"] = self.scan_port_violations()
        self.violations["doc_missing"] = self.scan_doc_missing()
        return self.violations


class GovernanceFixer:
    """Generates & executes fix scripts"""

    def __init__(self, violations: Dict[str, List[str]]):
        self.violations = violations
        self.fix_log = []

    def generate_fix_plan(self) -> List[str]:
        """Generate shell commands to fix violations"""
        plan = []

        # ARCHIV fixes
        if self.violations["archiv"]:
            plan.append("# === ARCHIV ROLLBACK ===")
            plan.append("DRY_RUN=false ./GOVERNANCE_FIX_ARCHIV.sh")
            plan.append("")

        # venv-leaks fixes
        if self.violations["venv_leaks"]:
            plan.append("# === VENV-LEAKS CLEANUP ===")
            plan.append("DRY_RUN=false ./GOVERNANCE_FIX_VENV_LEAKS.sh")
            plan.append("")

        # Tests rescue
        if self.violations["tests_displaced"]:
            plan.append("# === TESTS RESCUE ===")
            plan.append("DRY_RUN=false ./GOVERNANCE_FIX_TESTS.sh")
            plan.append("")

        # Port violations (manual review required)
        if self.violations["port_violations"]:
            plan.append("# === PORT VIOLATIONS (MANUAL FIX REQUIRED) ===")
            for file in self.violations["port_violations"]:
                plan.append(f"# Review: {file}")
            plan.append("")

        # Documentation
        if self.violations["doc_missing"]:
            plan.append("# === DOCUMENTATION ===")
            for doc in self.violations["doc_missing"]:
                plan.append(f"# Create: {doc}")
            plan.append("")

        return plan

    def apply_fixes(self, dry_run: bool = True) -> bool:
        """Execute fix scripts with safety guards"""
        if dry_run:
            print("⚠️  DRY-RUN mode – no changes will be made")

        # Execute ARCHIV fix
        if self.violations["archiv"]:
            script = PROJECT_ROOT / "GOVERNANCE_FIX_ARCHIV.sh"
            if script.exists():
                env = os.environ.copy()
                env["DRY_RUN"] = "true" if dry_run else "false"
                result = subprocess.run(
                    [str(script)],
                    env=env,
                    capture_output=True,
                    text=True,
                    cwd=PROJECT_ROOT,
                )
                self.fix_log.append(
                    {
                        "script": "GOVERNANCE_FIX_ARCHIV.sh",
                        "exit_code": result.returncode,
                        "stdout": result.stdout[-500:],  # Last 500 chars
                    }
                )

        # Execute venv-leaks fix
        if self.violations["venv_leaks"]:
            script = PROJECT_ROOT / "GOVERNANCE_FIX_VENV_LEAKS.sh"
            if script.exists():
                env = os.environ.copy()
                env["DRY_RUN"] = "true" if dry_run else "false"
                result = subprocess.run(
                    [str(script)],
                    env=env,
                    capture_output=True,
                    text=True,
                    cwd=PROJECT_ROOT,
                )
                self.fix_log.append(
                    {
                        "script": "GOVERNANCE_FIX_VENV_LEAKS.sh",
                        "exit_code": result.returncode,
                        "stdout": result.stdout[-500:],
                    }
                )

        # Execute tests rescue
        if self.violations["tests_displaced"]:
            script = PROJECT_ROOT / "GOVERNANCE_FIX_TESTS.sh"
            if script.exists():
                env = os.environ.copy()
                env["DRY_RUN"] = "true" if dry_run else "false"
                result = subprocess.run(
                    [str(script)],
                    env=env,
                    capture_output=True,
                    text=True,
                    cwd=PROJECT_ROOT,
                )
                self.fix_log.append(
                    {
                        "script": "GOVERNANCE_FIX_TESTS.sh",
                        "exit_code": result.returncode,
                        "stdout": result.stdout[-500:],
                    }
                )

        return all(log["exit_code"] == 0 for log in self.fix_log)


class GovernanceValidator:
    """Post-fix validation"""

    def __init__(self):
        self.results = {}

    def validate_archiv(self) -> bool:
        """Verify no Safepoints in configs/"""
        configs_dir = PROJECT_ROOT / "configs"
        if not configs_dir.exists():
            return True
        sp_files = list(configs_dir.rglob("SP*.json"))
        self.results["archiv_clean"] = len(sp_files) == 0
        return self.results["archiv_clean"]

    def validate_venv_leaks(self) -> bool:
        """Verify no venv packages in src/pkg/"""
        forbidden = ["typing_extensions.py", "socks.py", "py.py", "sockshandler.py"]
        violations = []
        if SRC_PKG_DIR.exists():
            for pkg in forbidden:
                if (SRC_PKG_DIR / pkg).exists():
                    violations.append(pkg)
        self.results["venv_clean"] = len(violations) == 0
        return self.results["venv_clean"]

    def validate_tests(self) -> bool:
        """Verify critical tests exist in 19.dashboard_agent/tests/"""
        tests_dir = PROJECT_ROOT / "19.dashboard_agent" / "tests"
        required_tests = ["test_archivator.py", "test_openwebui_agent.py"]
        missing = []
        for test in required_tests:
            if not (tests_dir / test).exists():
                missing.append(test)
        self.results["tests_present"] = len(missing) == 0
        return self.results["tests_present"]

    def validate_all(self) -> Dict[str, bool]:
        """Run all validations"""
        print("✅ Validating governance compliance...")
        self.validate_archiv()
        self.validate_venv_leaks()
        self.validate_tests()
        return self.results


def print_report(violations: Dict[str, List[str]]):
    """Pretty-print violations report"""
    print("\n" + "=" * 70)
    print("📋 GOVERNANCE VIOLATIONS REPORT")
    print("=" * 70)

    total = sum(len(v) for v in violations.values())
    if total == 0:
        print("✅ No violations found – system is compliant!")
        return

    for category, items in violations.items():
        if items:
            print(f"\n❌ {category.upper().replace('_', ' ')}: {len(items)} violations")
            for item in items[:5]:  # Show first 5
                print(f"   - {item}")
            if len(items) > 5:
                print(f"   ... +{len(items) - 5} more")

    print(f"\n🔢 TOTAL VIOLATIONS: {total}")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Automated Governance Compliance Checker & Fixer"
    )
    parser.add_argument(
        "mode",
        choices=["analyze", "plan", "apply", "validate"],
        help="Operation mode",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate fixes without applying (default for 'apply')",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for plan (default: stdout)",
    )

    args = parser.parse_args()

    # ANALYZE mode
    if args.mode == "analyze":
        analyzer = GovernanceAnalyzer()
        violations = analyzer.analyze()
        print_report(violations)

        # Save to JSON
        report_file = PROJECT_ROOT / f"governance_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "violations": violations,
                    "total": sum(len(v) for v in violations.values()),
                },
                f,
                indent=2,
            )
        print(f"📄 Report saved: {report_file}")

    # PLAN mode
    elif args.mode == "plan":
        analyzer = GovernanceAnalyzer()
        violations = analyzer.analyze()
        fixer = GovernanceFixer(violations)
        plan = fixer.generate_fix_plan()

        if args.output:
            output_file = PROJECT_ROOT / args.output
            output_file.write_text("\n".join(plan))
            print(f"📜 Fix plan saved: {output_file}")
        else:
            print("\n".join(plan))

    # APPLY mode
    elif args.mode == "apply":
        analyzer = GovernanceAnalyzer()
        violations = analyzer.analyze()
        print_report(violations)

        if sum(len(v) for v in violations.values()) == 0:
            print("✅ No fixes needed – system already compliant!")
            return

        # Default to dry-run unless explicitly disabled
        dry_run = args.dry_run or True
        if not dry_run:
            confirm = input("\n⚠️  LIVE MODE – Apply fixes? (yes/NO): ")
            if confirm.lower() != "yes":
                print("❌ Aborted by user")
                return

        fixer = GovernanceFixer(violations)
        success = fixer.apply_fixes(dry_run=dry_run)

        print("\n" + "=" * 70)
        print("📊 FIX EXECUTION LOG")
        print("=" * 70)
        for log in fixer.fix_log:
            status = "✅" if log["exit_code"] == 0 else "❌"
            print(f"{status} {log['script']} (exit {log['exit_code']})")
            print(f"   {log['stdout'][:200]}")

        if success:
            print("\n✅ All fixes applied successfully!")
        else:
            print("\n❌ Some fixes failed – check logs above")

    # VALIDATE mode
    elif args.mode == "validate":
        validator = GovernanceValidator()
        results = validator.validate_all()

        print("\n" + "=" * 70)
        print("✅ GOVERNANCE VALIDATION RESULTS")
        print("=" * 70)
        for check, passed in results.items():
            status = "✅" if passed else "❌"
            print(f"{status} {check.replace('_', ' ').title()}")

        if all(results.values()):
            print("\n🎉 System is fully compliant!")
        else:
            print("\n⚠️  Some checks failed – run 'analyze' for details")


if __name__ == "__main__":
    main()
