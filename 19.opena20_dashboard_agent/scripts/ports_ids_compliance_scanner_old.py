#!/usr/bin/env python3
"""
Ports & Agent IDs Compliance Scanner
=====================================
Enforces absolute compliance with port and agent ID policies.

FAIL-HARD RULES (1000% ENFORCEMENT):
1. Exactly opena1..opena21 exist (no more, no less)
2. Ports are unique and EXACTLY match baseline
3. Forbidden ports (8080, 3000) NEVER appear anywhere
4. Any agent reference outside opena1-opena21 = FAIL
5. Port conflicts = FAIL
6. Port mismatches = FAIL

EXIT CODES:
- 0: Full compliance
- 1: Violations found (CI MUST break)

Usage:
  python3 scripts/ports_ids_compliance_scanner.py
"""

import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

# ============================================================================
# CONFIGURATION
# ============================================================================

REQUIRED_AGENTS = [f"opena{i}" for i in range(1, 22)]  # opena1..opena21
AGENT_ID_PATTERN = re.compile(r"\b(opena\d{1,2})\b", re.IGNORECASE)
PORT_PATTERN = re.compile(r"\b(\d{2,5})\b")


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class ComplianceViolation:
    """A compliance violation"""

    severity: str  # 'critical', 'error', 'warning'
    category: str
    message: str
    location: str = ""


@dataclass
class ScanResult:
    """Overall scan result"""

    timestamp: str
    passed: bool
    violations: list[ComplianceViolation] = field(default_factory=list)

    # Checks performed
    agents_found: list[str] = field(default_factory=list)
    agents_missing: list[str] = field(default_factory=list)
    agents_extra: list[str] = field(default_factory=list)

    port_assignments: dict[str, int] = field(default_factory=dict)
    port_conflicts: list[dict[str, Any]] = field(default_factory=list)
    port_mismatches: list[dict[str, Any]] = field(default_factory=list)
    forbidden_port_usages: list[dict[str, Any]] = field(default_factory=list)

    invalid_agent_references: list[dict[str, Any]] = field(default_factory=list)


# ============================================================================
# SCANNER
# ============================================================================


class PortsIDsComplianceScanner:
    """Scanner for ports and agent IDs compliance"""

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
            print(f"✓ Loaded baseline: {self.baseline_path}")
        except Exception as e:
            self.add_violation("critical", "loading", f"Failed to load baseline: {e}")
            return False

        try:
            with open(self.inventory_path) as f:
                self.inventory = json.load(f)
            print(f"✓ Loaded inventory: {self.inventory_path}")
        except Exception as e:
            self.add_violation("critical", "loading", f"Failed to load inventory: {e}")
            return False

        return True

    def add_violation(self, severity: str, category: str, message: str, location: str = ""):
        """Add a violation to results"""
        self.result.violations.append(
            ComplianceViolation(severity=severity, category=category, message=message, location=location)
        )

    def check_agent_completeness(self):
        """Check that exactly opena1-opena21 exist"""
        print("\n[1/6] Checking agent completeness...")

        # From baseline
        baseline_agents = set()
        for agent in self.baseline.get("agents", []):
            agent_id = agent.get("id", "")
            baseline_agents.add(agent_id)

        # From inventory
        inventory_agents = set()
        for agent in self.inventory.get("agents", []):
            agent_id = agent.get("id", "")
            inventory_agents.add(agent_id)

        required_set = set(REQUIRED_AGENTS)

        # Check baseline
        baseline_missing = required_set - baseline_agents
        baseline_extra = baseline_agents - required_set

        if baseline_missing:
            for agent_id in sorted(baseline_missing):
                self.add_violation(
                    "critical",
                    "agent_missing",
                    f"Required agent missing from baseline: {agent_id}",
                    "system_baseline.yaml",
                )
                self.result.agents_missing.append(agent_id)

        if baseline_extra:
            for agent_id in sorted(baseline_extra):
                self.add_violation(
                    "critical",
                    "agent_extra",
                    f"Unexpected agent in baseline: {agent_id} (only opena1-21 allowed)",
                    "system_baseline.yaml",
                )
                self.result.agents_extra.append(agent_id)

        # Check inventory
        inventory_missing = required_set - inventory_agents
        inventory_extra = inventory_agents - required_set

        if inventory_missing:
            for agent_id in sorted(inventory_missing):
                self.add_violation(
                    "error",
                    "agent_missing",
                    f"Required agent missing from inventory: {agent_id}",
                    "artifacts/agent_inventory.json",
                )

        if inventory_extra:
            for agent_id in sorted(inventory_extra):
                self.add_violation(
                    "error",
                    "agent_extra",
                    f"Unexpected agent in inventory: {agent_id}",
                    "artifacts/agent_inventory.json",
                )

        self.result.agents_found = sorted(baseline_agents & required_set)

        if not baseline_missing and not baseline_extra:
            print("  ✓ All 21 required agents present in baseline")
        else:
            print("  ✗ Agent completeness check failed")

    def check_port_assignments(self):
        """Check port uniqueness and baseline matching"""
        print("\n[2/6] Checking port assignments...")

        # Build port map from baseline
        baseline_ports: dict[str, int] = {}
        for agent in self.baseline.get("agents", []):
            agent_id = agent.get("id")
            port = agent.get("port")
            if agent_id and port:
                baseline_ports[agent_id] = port

        self.result.port_assignments = baseline_ports

        # Check for duplicates
        port_to_agents: dict[int, list[str]] = {}
        for agent_id, port in baseline_ports.items():
            port_to_agents.setdefault(port, []).append(agent_id)

        for port, agents in port_to_agents.items():
            if len(agents) > 1:
                self.add_violation(
                    "critical",
                    "port_conflict",
                    f"Port {port} assigned to multiple agents: {', '.join(agents)}",
                    "system_baseline.yaml",
                )
                self.result.port_conflicts.append({"port": port, "agents": agents})

        # Check inventory matches baseline
        for agent in self.inventory.get("agents", []):
            agent_id = agent.get("id")
            if agent_id not in baseline_ports:
                continue

            baseline_port = baseline_ports[agent_id]
            detected_ports = agent.get("ports_detected", [])

            if detected_ports:
                # All detected ports must match baseline
                non_matching = [p for p in detected_ports if p != baseline_port]
                if non_matching:
                    self.add_violation(
                        "critical",
                        "port_mismatch",
                        f"{agent_id}: Port mismatch! Baseline={baseline_port}, " f"Detected={detected_ports}",
                        f"Agent folder: {agent.get('folder')}",
                    )
                    self.result.port_mismatches.append(
                        {"agent_id": agent_id, "baseline_port": baseline_port, "detected_ports": detected_ports}
                    )

        if not self.result.port_conflicts and not self.result.port_mismatches:
            print("  ✓ All port assignments are unique and match baseline")
        else:
            print("  ✗ Port assignment check failed")

    def check_forbidden_ports(self):
        """Check that forbidden ports never appear"""
        print("\n[3/6] Checking forbidden ports...")

        port_policy = self.baseline.get("port_policy", {})
        forbidden = set(port_policy.get("forbidden_ports", []))

        if not forbidden:
            print("  ⚠️  No forbidden ports defined in baseline")
            return

        # Check baseline itself
        for agent in self.baseline.get("agents", []):
            port = agent.get("port")
            if port in forbidden:
                self.add_violation(
                    "critical",
                    "forbidden_port",
                    f"{agent.get('id')}: Uses forbidden port {port}",
                    "system_baseline.yaml",
                )

        # Check inventory
        for agent in self.inventory.get("agents", []):
            agent_id = agent.get("id")
            detected_ports = agent.get("ports_detected", [])

            for port in detected_ports:
                if port in forbidden:
                    self.add_violation(
                        "critical",
                        "forbidden_port",
                        f"{agent_id}: Forbidden port {port} found in agent files",
                        f"Agent folder: {agent.get('folder')}",
                    )
                    self.result.forbidden_port_usages.append(
                        {"agent_id": agent_id, "port": port, "folder": agent.get("folder")}
                    )

        if not self.result.forbidden_port_usages:
            print("  ✓ No forbidden ports detected")
        else:
            print("  ✗ Forbidden port check failed")

    def check_agent_references(self):
        """Check that all agent references are valid (opena1-21 only)"""
        print("\n[4/6] Checking agent references...")

        valid_agents = set(REQUIRED_AGENTS)

        for agent in self.inventory.get("agents", []):
            agent_id = agent.get("id")
            agent_refs = agent.get("agent_references", [])

            for ref in agent_refs:
                ref_lower = ref.lower()
                if ref_lower not in valid_agents:
                    self.add_violation(
                        "error",
                        "invalid_agent_ref",
                        f"{agent_id}: Invalid agent reference '{ref}' " f"(only opena1-opena21 allowed)",
                        f"Agent folder: {agent.get('folder')}",
                    )
                    self.result.invalid_agent_references.append(
                        {"source_agent": agent_id, "invalid_reference": ref, "folder": agent.get("folder")}
                    )

        if not self.result.invalid_agent_references:
            print("  ✓ All agent references are valid")
        else:
            print("  ✗ Invalid agent references found")

    def check_port_range_policy(self):
        """Check that all ports are within allowed range"""
        print("\n[5/6] Checking port range policy...")

        port_policy = self.baseline.get("port_policy", {})
        allowed_range = port_policy.get("allowed_range", [1, 65535])
        min_port, max_port = allowed_range

        violations_found = False

        for agent in self.baseline.get("agents", []):
            agent_id = agent.get("id")
            port = agent.get("port")

            if port and not (min_port <= port <= max_port):
                self.add_violation(
                    "critical",
                    "port_out_of_range",
                    f"{agent_id}: Port {port} outside allowed range " f"[{min_port}, {max_port}]",
                    "system_baseline.yaml",
                )
                violations_found = True

        if not violations_found:
            print(f"  ✓ All ports within allowed range [{min_port}, {max_port}]")
        else:
            print("  ✗ Port range policy check failed")

    def verify_inventory_errors(self):
        """Check if inventory itself reported any errors"""
        print("\n[6/6] Checking inventory errors...")

        inventory_errors = self.inventory.get("errors", [])

        if inventory_errors:
            for error in inventory_errors:
                self.add_violation(
                    "error", "inventory_error", f"Inventory reported: {error}", "artifacts/agent_inventory.json"
                )
            print(f"  ✗ Inventory contains {len(inventory_errors)} error(s)")
        else:
            print("  ✓ Inventory has no errors")

    def run_all_checks(self) -> bool:
        """Run all compliance checks"""
        print(f"\n{'='*60}")
        print("PORTS & IDs COMPLIANCE SCANNER")
        print(f"{'='*60}")

        if not self.load_sources():
            return False

        self.check_agent_completeness()
        self.check_port_assignments()
        self.check_forbidden_ports()
        self.check_agent_references()
        self.check_port_range_policy()
        self.verify_inventory_errors()

        # Determine pass/fail
        critical_violations = [v for v in self.result.violations if v.severity == "critical"]
        error_violations = [v for v in self.result.violations if v.severity == "error"]

        self.result.passed = len(critical_violations) == 0 and len(error_violations) == 0

        return self.result.passed

    def generate_report(self, output_path: Path):
        """Generate JSON and MD reports"""
        # Convert to dict
        result_dict = asdict(self.result)

        # JSON report
        json_path = output_path.with_suffix(".json")
        json_path.parent.mkdir(parents=True, exist_ok=True)

        with open(json_path, "w") as f:
            json.dump(result_dict, f, indent=2)

        print(f"\n✓ JSON report: {json_path}")

        # MD report
        md_lines = [
            "# Ports & Agent IDs Compliance Scan Report",
            "",
            f"**Timestamp:** {self.result.timestamp}",
            f"**Status:** {'✅ PASSED' if self.result.passed else '❌ FAILED'}",
            "",
            "## Summary",
            "",
            f"- Agents found: {len(self.result.agents_found)}/21",
            f"- Agents missing: {len(self.result.agents_missing)}",
            f"- Agents extra: {len(self.result.agents_extra)}",
            f"- Port conflicts: {len(self.result.port_conflicts)}",
            f"- Port mismatches: {len(self.result.port_mismatches)}",
            f"- Forbidden port usages: {len(self.result.forbidden_port_usages)}",
            f"- Invalid agent references: {len(self.result.invalid_agent_references)}",
            "",
            f"## Violations ({len(self.result.violations)})",
            "",
        ]

        # Group by severity
        critical = [v for v in self.result.violations if v.severity == "critical"]
        errors = [v for v in self.result.violations if v.severity == "error"]
        warnings = [v for v in self.result.violations if v.severity == "warning"]

        if critical:
            md_lines.append("### 🔴 CRITICAL")
            md_lines.append("")
            for v in critical:
                md_lines.append(f"- **{v.category}**: {v.message}")
                if v.location:
                    md_lines.append(f"  - Location: `{v.location}`")
            md_lines.append("")

        if errors:
            md_lines.append("### ⚠️ ERRORS")
            md_lines.append("")
            for v in errors:
                md_lines.append(f"- **{v.category}**: {v.message}")
                if v.location:
                    md_lines.append(f"  - Location: `{v.location}`")
            md_lines.append("")

        if warnings:
            md_lines.append("### ℹ️ WARNINGS")
            md_lines.append("")
            for v in warnings:
                md_lines.append(f"- **{v.category}**: {v.message}")
                if v.location:
                    md_lines.append(f"  - Location: `{v.location}`")
            md_lines.append("")

        if not self.result.violations:
            md_lines.append("✅ No violations found.")
            md_lines.append("")

        md_path = output_path.with_suffix(".md")
        with open(md_path, "w") as f:
            f.write("\n".join(md_lines))

        print(f"✓ MD report: {md_path}")


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent

    scanner = PortsIDsComplianceScanner(project_root)
    success = scanner.run_all_checks()

    # Generate reports
    artifacts_dir = project_root / "artifacts" / "scans"
    scanner.generate_report(artifacts_dir / "ports_ids_scan")

    # Print summary
    print(f"\n{'='*60}")
    print("SCAN SUMMARY")
    print(f"{'='*60}")

    critical = [v for v in scanner.result.violations if v.severity == "critical"]
    errors = [v for v in scanner.result.violations if v.severity == "error"]

    if success:
        print("✅ ALL COMPLIANCE CHECKS PASSED")
        print("✅ Ports and Agent IDs are 1000% compliant")
        return 0
    else:
        print("❌ COMPLIANCE VIOLATIONS FOUND")
        print(f"   - Critical: {len(critical)}")
        print(f"   - Errors: {len(errors)}")
        print("\n⚠️  CI MUST BREAK - Fix violations before deployment")
        return 1


if __name__ == "__main__":
    sys.exit(main())
