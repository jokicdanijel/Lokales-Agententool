#!/usr/bin/env python3
"""
ELION Hyper-Dashboard - Entitlements Validator
===============================================
Validates entitlements.json for policy compliance and consistency.

VALIDATION RULES:
1. No agent outside baseline
2. Plan inclusion ordering: ultimum ⊇ premium ⊇ pro ⊇ basic
3. Basic plan has exactly 4 clickable agents
4. Core agents always clickable
5. System agents always visible

EXIT CODES:
- 0: All validations passed
- 1: Validation failed (CI must break)
"""

import json
import sys
from pathlib import Path
from typing import ClassVar

import yaml


class EntitlementsValidator:
    """Validates entitlement rules and policies."""

    PLAN_HIERARCHY: ClassVar[list[str]] = ["basic", "pro", "premium", "ultimum"]
    CORE_AGENTS: ClassVar[list[str]] = ["opena1", "opena2"]
    SYSTEM_AGENTS: ClassVar[list[str]] = ["opena20", "opena21"]
    BASIC_CLICKABLE_COUNT: ClassVar[int] = 4

    def __init__(self, baseline_path: str, entitlements_path: str):
        self.baseline_path = Path(baseline_path)
        self.entitlements_path = Path(entitlements_path)
        self.baseline = None
        self.entitlements = None
        self.errors = []
        self.warnings = []

    def load_files(self) -> bool:
        """Load baseline and entitlements files."""
        try:
            # Load baseline
            with open(self.baseline_path) as f:
                self.baseline = yaml.safe_load(f)
            print(f"✓ Loaded baseline from {self.baseline_path}")

            # Load entitlements
            with open(self.entitlements_path) as f:
                self.entitlements = json.load(f)
            print(f"✓ Loaded entitlements from {self.entitlements_path}")

            return True
        except Exception as e:
            self.errors.append(f"Failed to load files: {e}")
            return False

    def get_baseline_agents(self) -> set:
        """Get all valid agent IDs from baseline."""
        agents = set()
        for agent in self.baseline.get("agents", []):
            agents.add(agent["id"])
        return agents

    def validate_agent_existence(self) -> bool:
        """Ensure no agent in entitlements is outside baseline."""
        print("\n[1/6] Validating agent existence...")

        baseline_agents = self.get_baseline_agents()
        valid = True

        for plan_id, plan_data in self.entitlements["plans"].items():
            for agent_id in plan_data["agents"].keys():
                if agent_id not in baseline_agents:
                    self.errors.append(f"Agent '{agent_id}' in plan '{plan_id}' " f"not found in baseline")
                    valid = False

        if valid:
            print("  ✓ All agents exist in baseline")
        return valid

    def validate_plan_inclusion_ordering(self) -> bool:
        """Ensure higher plans include all lower plan clickable agents."""
        print("\n[2/6] Validating plan inclusion ordering...")

        valid = True

        # Build set of clickable agents per plan
        plan_clickable = {}
        for plan_id in self.PLAN_HIERARCHY:
            clickable = set()
            plan_data = self.entitlements["plans"][plan_id]
            for agent_id, agent_data in plan_data["agents"].items():
                if agent_data["clickable"]:
                    clickable.add(agent_id)
            plan_clickable[plan_id] = clickable

        # Validate inclusion: higher ⊇ lower
        for i in range(len(self.PLAN_HIERARCHY) - 1):
            lower_plan = self.PLAN_HIERARCHY[i]
            higher_plan = self.PLAN_HIERARCHY[i + 1]

            lower_clickable = plan_clickable[lower_plan]
            higher_clickable = plan_clickable[higher_plan]

            missing = lower_clickable - higher_clickable
            if missing:
                self.errors.append(
                    f"Plan '{higher_plan}' does not include all clickable "
                    f"agents from '{lower_plan}': missing {missing}"
                )
                valid = False

        if valid:
            print("  ✓ Plan inclusion ordering correct")
        return valid

    def validate_basic_clickable_count(self) -> bool:
        """Ensure Basic plan has exactly 4 clickable agents."""
        print("\n[3/6] Validating Basic plan clickable count...")

        basic_plan = self.entitlements["plans"]["basic"]
        clickable_agents = [
            agent_id for agent_id, agent_data in basic_plan["agents"].items() if agent_data["clickable"]
        ]

        # Count excludes core agents for this check
        non_core_clickable = [agent_id for agent_id in clickable_agents if agent_id not in self.CORE_AGENTS]

        expected = self.BASIC_CLICKABLE_COUNT
        actual = len(non_core_clickable)

        if actual != expected:
            self.errors.append(
                f"Basic plan must have exactly {expected} clickable "
                f"non-core agents, found {actual}: {non_core_clickable}"
            )
            return False

        print(f"  ✓ Basic plan has {expected} clickable non-core agents")
        return True

    def validate_core_agents(self) -> bool:
        """Ensure core agents are always visible and clickable."""
        print("\n[4/6] Validating core agents...")

        valid = True

        for plan_id, plan_data in self.entitlements["plans"].items():
            for agent_id in self.CORE_AGENTS:
                if agent_id not in plan_data["agents"]:
                    self.errors.append(f"Core agent '{agent_id}' missing in plan '{plan_id}'")
                    valid = False
                    continue

                agent_data = plan_data["agents"][agent_id]
                if not agent_data["visible"]:
                    self.errors.append(f"Core agent '{agent_id}' not visible in plan '{plan_id}'")
                    valid = False

                if not agent_data["clickable"]:
                    self.errors.append(f"Core agent '{agent_id}' not clickable in plan '{plan_id}'")
                    valid = False

        if valid:
            print("  ✓ Core agents correctly configured")
        return valid

    def validate_system_agents(self) -> bool:
        """Ensure system agents are always visible."""
        print("\n[5/6] Validating system agents...")

        valid = True

        for plan_id, plan_data in self.entitlements["plans"].items():
            for agent_id in self.SYSTEM_AGENTS:
                if agent_id not in plan_data["agents"]:
                    self.warnings.append(f"System agent '{agent_id}' missing in plan '{plan_id}'")
                    continue

                agent_data = plan_data["agents"][agent_id]
                if not agent_data["visible"]:
                    self.errors.append(f"System agent '{agent_id}' not visible in plan '{plan_id}'")
                    valid = False

        if valid:
            print("  ✓ System agents correctly configured")
        return valid

    def validate_basic_limits(self) -> bool:
        """Validate Basic plan specific limits."""
        print("\n[6/6] Validating Basic plan limits...")

        valid = True
        basic_plan = self.entitlements["plans"]["basic"]

        for agent_id, agent_data in basic_plan["agents"].items():
            # Skip core and system agents
            if agent_id in self.CORE_AGENTS or agent_id in self.SYSTEM_AGENTS:
                continue

            # Only check clickable non-core agents
            if agent_data["clickable"]:
                limits = agent_data.get("limits", {})

                # Check logs access
                if limits.get("logs_access") != "read_only":
                    self.errors.append(f"Basic plan agent '{agent_id}' must have " f"logs_access='read_only'")
                    valid = False

                # Check workflow limit
                if limits.get("workflow_limit") != 4:
                    self.errors.append(f"Basic plan agent '{agent_id}' must have " f"workflow_limit=4")
                    valid = False

        if valid:
            print("  ✓ Basic plan limits correctly configured")
        return valid

    def run_all_validations(self) -> bool:
        """Run all validation checks."""
        print("\n" + "=" * 60)
        print("ENTITLEMENTS VALIDATION")
        print("=" * 60)

        validations = [
            self.validate_agent_existence(),
            self.validate_plan_inclusion_ordering(),
            self.validate_basic_clickable_count(),
            self.validate_core_agents(),
            self.validate_system_agents(),
            self.validate_basic_limits(),
        ]

        return all(validations)

    def save_validation_report(self, output_path: str) -> None:
        """Save validation report to JSON."""
        report = {
            "timestamp": self.entitlements.get("generated_at", "unknown"),
            "baseline": str(self.baseline_path),
            "entitlements": str(self.entitlements_path),
            "status": "passed" if not self.errors else "failed",
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {"total_errors": len(self.errors), "total_warnings": len(self.warnings)},
        }

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Validation report saved to {output_file}")

    def print_summary(self) -> None:
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)

        if self.errors:
            print(f"✗ {len(self.errors)} ERROR(S) FOUND:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")

        if self.warnings:
            print(f"\n⚠ {len(self.warnings)} WARNING(S):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        if not self.errors and not self.warnings:
            print("✓ ALL VALIDATIONS PASSED")

        print("=" * 60)


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent

    baseline_path = project_root / "system_baseline.yaml"
    entitlements_path = project_root / "build" / "entitlements.json"
    report_path = project_root / "artifacts" / "entitlements_validation.json"

    print("=" * 60)
    print("ELION Entitlements Validator")
    print("=" * 60)
    print(f"Baseline:     {baseline_path}")
    print(f"Entitlements: {entitlements_path}")
    print(f"Report:       {report_path}")
    print("=" * 60)

    # Validate
    validator = EntitlementsValidator(baseline_path=str(baseline_path), entitlements_path=str(entitlements_path))

    if not validator.load_files():
        print("\n✗ Failed to load files", file=sys.stderr)
        sys.exit(1)

    success = validator.run_all_validations()
    validator.save_validation_report(str(report_path))
    validator.print_summary()

    if not success:
        print("\n✗ Validation FAILED - CI must break!", file=sys.stderr)
        sys.exit(1)

    print("\n✓ Validation PASSED!")
    sys.exit(0)


if __name__ == "__main__":
    main()
