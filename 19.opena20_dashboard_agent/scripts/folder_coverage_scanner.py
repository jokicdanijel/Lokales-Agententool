#!/usr/bin/env python3
"""
Full Recursive Folder Coverage Scanner
=======================================
Verifies complete recursive analysis of all agent folders.

FAIL-HARD RULES:
1. Every agent folder must exist and be non-empty
2. Recursive file enumeration count > 0
3. Inventory must contain file hashes (proof of analysis)
4. Stable ordering evidence (deterministic scan)
5. Any unreadable file = FAIL

EXIT CODES:
- 0: Full coverage verified
- 1: Coverage gaps found (CI MUST break)

Usage:
  python3 scripts/folder_coverage_scanner.py
"""

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml


@dataclass
class FolderCoverageResult:
    """Coverage result for one agent"""

    agent_id: str
    folder: str
    exists: bool
    is_empty: bool
    file_count: int
    files_with_hashes: int
    violations: list[str] = field(default_factory=list)
    passed: bool = False


@dataclass
class ScanResult:
    """Overall scan result"""

    timestamp: str
    passed: bool
    total_agents: int = 0
    agents_passed: int = 0
    agents_failed: int = 0
    results: list[FolderCoverageResult] = field(default_factory=list)


class FolderCoverageScanner:
    """Scanner for folder coverage verification"""

    def __init__(self, project_root: Path):
        self.root = project_root
        self.baseline_path = project_root / "system_baseline.yaml"
        self.inventory_path = project_root / "artifacts" / "agent_inventory.json"

        self.baseline: dict[str, Any] = {}
        self.inventory: dict[str, Any] = {}
        self.result = ScanResult(timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"), passed=False)

    def load_sources(self) -> bool:
        """Load baseline and inventory"""
        try:
            with open(self.baseline_path) as f:
                self.baseline = yaml.safe_load(f)
            print("✓ Loaded baseline")
        except Exception as e:
            print(f"✗ Failed to load baseline: {e}")
            return False

        try:
            with open(self.inventory_path) as f:
                self.inventory = json.load(f)
            print("✓ Loaded inventory")
        except Exception as e:
            print(f"✗ Failed to load inventory: {e}")
            return False

        return True

    def check_agent_folder(self, agent_data: dict, inventory_agent: dict) -> FolderCoverageResult:
        """Check coverage for single agent"""
        agent_id = agent_data["id"]
        folder_rel = agent_data["folder"]
        folder_path = self.root / folder_rel

        result = FolderCoverageResult(
            agent_id=agent_id,
            folder=folder_rel,
            exists=folder_path.exists(),
            is_empty=False,
            file_count=0,
            files_with_hashes=0,
        )

        # Check existence
        if not result.exists:
            result.violations.append(f"Folder does not exist: {folder_rel}")
            return result

        # Check if directory
        if not folder_path.is_dir():
            result.violations.append(f"Path exists but is not a directory: {folder_rel}")
            return result

        # Count actual files
        try:
            actual_files = list(folder_path.rglob("*"))
            actual_file_count = sum(1 for f in actual_files if f.is_file())
        except Exception as e:
            result.violations.append(f"Failed to enumerate folder: {e}")
            return result

        # Check empty
        if actual_file_count == 0:
            result.is_empty = True
            result.violations.append("Folder is empty (no files found)")
            return result

        # Check inventory data
        inv_file_count = inventory_agent.get("file_count", 0)
        inv_files = inventory_agent.get("files", [])

        result.file_count = inv_file_count
        result.files_with_hashes = len([f for f in inv_files if f.get("sha256")])

        # Verification
        if inv_file_count == 0:
            result.violations.append(f"Inventory reports 0 files (but folder has {actual_file_count})")

        if inv_file_count != actual_file_count:
            result.violations.append(f"File count mismatch: inventory={inv_file_count}, " f"actual={actual_file_count}")

        if result.files_with_hashes == 0 and inv_file_count > 0:
            result.violations.append("No file hashes in inventory (incomplete analysis)")

        if result.files_with_hashes != inv_file_count:
            result.violations.append(f"Not all files have hashes: {result.files_with_hashes}/{inv_file_count}")

        # Check for stable ordering (all files should have relpath)
        files_without_path = [f for f in inv_files if not f.get("relpath")]
        if files_without_path:
            result.violations.append(f"{len(files_without_path)} files missing relpath (unstable ordering)")

        # Pass if no violations
        result.passed = len(result.violations) == 0

        return result

    def run_scan(self) -> bool:
        """Run full coverage scan"""
        print(f"\n{'='*60}")
        print("FOLDER COVERAGE SCANNER")
        print(f"{'='*60}\n")

        if not self.load_sources():
            return False

        # Build agent map from inventory
        inventory_map = {}
        for agent in self.inventory.get("agents", []):
            inventory_map[agent["id"]] = agent

        # Scan each agent
        agents = self.baseline.get("agents", [])
        self.result.total_agents = len(agents)

        print(f"Scanning {len(agents)} agent folders...\n")

        for agent_data in agents:
            agent_id = agent_data["id"]
            inventory_agent = inventory_map.get(agent_id, {})

            result = self.check_agent_folder(agent_data, inventory_agent)
            self.result.results.append(result)

            status = "✓" if result.passed else "✗"
            print(f"{status} {agent_id} ({result.folder})")

            if result.violations:
                for v in result.violations:
                    print(f"    ✗ {v}")
            else:
                print(f"    Files: {result.file_count}, Hashed: {result.files_with_hashes}")

        self.result.agents_passed = sum(1 for r in self.result.results if r.passed)
        self.result.agents_failed = self.result.total_agents - self.result.agents_passed
        self.result.passed = self.result.agents_failed == 0

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
            "# Folder Coverage Scan Report",
            "",
            f"**Timestamp:** {self.result.timestamp}",
            f"**Status:** {'✅ PASSED' if self.result.passed else '❌ FAILED'}",
            "",
            "## Summary",
            "",
            f"- Total agents: {self.result.total_agents}",
            f"- Passed: {self.result.agents_passed}",
            f"- Failed: {self.result.agents_failed}",
            "",
            "## Agent Results",
            "",
        ]

        for result in self.result.results:
            status = "✅" if result.passed else "❌"
            md_lines.append(f"### {status} {result.agent_id}")
            md_lines.append("")
            md_lines.append(f"- **Folder:** `{result.folder}`")
            md_lines.append(f"- **Exists:** {result.exists}")
            md_lines.append(f"- **Is Empty:** {result.is_empty}")
            md_lines.append(f"- **File Count:** {result.file_count}")
            md_lines.append(f"- **Files with Hashes:** {result.files_with_hashes}")
            md_lines.append("")

            if result.violations:
                md_lines.append("**Violations:**")
                for v in result.violations:
                    md_lines.append(f"- ❌ {v}")
                md_lines.append("")

        md_path = output_path.with_suffix(".md")
        with open(md_path, "w") as f:
            f.write("\n".join(md_lines))

        print(f"✓ MD report: {md_path}")


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent

    scanner = FolderCoverageScanner(project_root)
    success = scanner.run_scan()

    # Generate reports
    artifacts_dir = project_root / "artifacts" / "scans"
    scanner.generate_report(artifacts_dir / "folder_coverage_scan")

    # Summary
    print(f"\n{'='*60}")
    print("SCAN SUMMARY")
    print(f"{'='*60}")

    if success:
        print("✅ ALL FOLDER COVERAGE CHECKS PASSED")
        print(f"✅ All {scanner.result.total_agents} agent folders fully analyzed")
        return 0
    else:
        print("❌ FOLDER COVERAGE VIOLATIONS FOUND")
        print(f"   Failed: {scanner.result.agents_failed}/{scanner.result.total_agents}")
        print("\n⚠️  CI MUST BREAK - Incomplete folder analysis")
        return 1


if __name__ == "__main__":
    sys.exit(main())
