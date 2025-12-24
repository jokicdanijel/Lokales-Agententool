#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
BUILD = ROOT / "build" / "entitlements.json"
BASELINE = ROOT / "system_baseline.yaml"


def main():
    if not BASELINE.exists():
        print("Baseline missing", file=sys.stderr)
        sys.exit(1)
    if not BUILD.exists():
        print("Entitlements build missing", file=sys.stderr)
        sys.exit(1)
    # Load baseline and entitlements.json
    with BASELINE.open("r", encoding="utf-8") as f:
        baseline = f.read()
    with BUILD.open("r", encoding="utf-8") as f:
        ent = json.load(f)
    # Simple consistency checks: 21 agents must appear if baseline declares that
    agents = [line for line in baseline.splitlines() if line.strip().startswith("- id:")]
    if len(agents) < 21:
        print("Warning: less than 21 agents declared in baseline", file=sys.stderr)
    # Ensure that entitlements contain keys for IDs mentioned in baseline basics
    missing = []
    for a in baseline.splitlines():
        if a.strip().startswith("- id:"):
            aid = a.split(":", 1)[1].strip()
            if "agents" in ent and aid not in ent["agents"]:
                missing.append(aid)
    if missing:
        print(f"Missing entitlements for agents: {missing}")
        sys.exit(1)
    print("Entitlements validation passed")
    sys.exit(0)


if __name__ == "__main__":
    main()  #!/usr/bin/env python3
"""
ELION Hyper-Dashboard - Entitlements Validator
Validates entitlements.json for policy compliance

VALIDATIONS:
1. No agent outside baseline
2. Inclusion ordering (ultimum ⊇ premium ⊇ pro ⊇ basic)
3. Basic clickable count == 4
4. Core agents always visible, never clickable
5. System agents visible, never clickable
6. Plan limits are monotonically increasing

EXIT CODES:
- 0: All validations passed
- 1: Validation failed (CI should fail)
"""

from datetime import datetime
from pathlib import Path


class EntitlementsValidator:
    """Validates entitlements for policy compliance"""

    # Expected constraints
    REQUIRED_PLANS = ["basic", "pro", "premium", "ultimum"]
    PLAN_HIERARCHY = ["basic", "pro", "premium", "ultimum"]

    CORE_AGENTS = ["opena1", "opena2"]
    SYSTEM_AGENTS = ["opena20", "opena21"]
    BASIC_REQUIRED_CLICKABLE = ["opena3", "opena4", "opena7", "opena11"]
    BASIC_REQUIRED_COUNT = 4

    def __init__(self, project_root: Path):
        self.root = project_root
        self.entitlements_path = self.root / "build" / "entitlements.json"
        self.baseline_path = self.root / "system_baseline.yaml"
        self.output_path = self.root / "artifacts" / "entitlements_validation.json"

        self.entitlements = None
        self.baseline = None
        self.errors = []
        self.warnings = []
        self.validations = []

    def load_entitlements(self):
        """Load entitlements file"""
        print("📂 Loading entitlements...")

        if not self.entitlements_path.exists():
            self.add_error(f"Entitlements file not found: {self.entitlements_path}")
            return False

        try:
            with open(self.entitlements_path) as f:
                self.entitlements = json.load(f)
            print(f"  ✅ Loaded: {self.entitlements_path}")
            return True
        except json.JSONDecodeError as e:
            self.add_error(f"Invalid JSON: {e}")
            return False

    def load_baseline(self):
        """Load baseline (optional for extended validation)"""
        if self.baseline_path.exists():
            import yaml

            with open(self.baseline_path) as f:
                self.baseline = yaml.safe_load(f)
            print(f"  ✅ Loaded baseline: {self.baseline_path}")

    def add_error(self, message: str):
        """Add validation error"""
        self.errors.append(message)
        print(f"  ❌ ERROR: {message}")

    def add_warning(self, message: str):
        """Add validation warning"""
        self.warnings.append(message)
        print(f"  ⚠️  WARNING: {message}")

    def add_validation(self, name: str, passed: bool, message: str = ""):
        """Record validation result"""
        self.validations.append({"name": name, "passed": passed, "message": message})

        status = "✅" if passed else "❌"
        print(f"  {status} {name}: {message}")

    def validate_structure(self) -> bool:
        """Validate basic structure"""
        print("\n🔍 Validating structure...")

        if not isinstance(self.entitlements, dict):
            self.add_error("Entitlements must be a dictionary")
            return False

        # Check metadata
        if "_metadata" not in self.entitlements:
            self.add_warning("Missing _metadata section")

        # Check all required plans exist
        missing_plans = set(self.REQUIRED_PLANS) - set(self.entitlements.keys())
        if missing_plans:
            self.add_error(f"Missing plans: {', '.join(missing_plans)}")
            return False

        self.add_validation("Structure", True, f"All {len(self.REQUIRED_PLANS)} required plans present")
        return True

    def validate_basic_constraint(self) -> bool:
        """Validate Basic plan has exactly 4 clickable agents"""
        print("\n🔍 Validating Basic plan constraint...")

        basic_plan = self.entitlements.get("basic", {})
        agents = basic_plan.get("agents", {})

        # Count clickable agents (excluding core and system)
        clickable = [
            agent_id
            for agent_id, data in agents.items()
            if data.get("clickable", False) and agent_id not in self.CORE_AGENTS + self.SYSTEM_AGENTS
        ]

        count = len(clickable)

        if count != self.BASIC_REQUIRED_COUNT:
            self.add_error(f"Basic plan has {count} clickable agents, expected {self.BASIC_REQUIRED_COUNT}")
            self.add_validation("Basic constraint", False, f"Count: {count} != 4")
            return False

        # Verify they match the required list
        if set(clickable) != set(self.BASIC_REQUIRED_CLICKABLE):
            self.add_error(
                f"Basic plan clickable agents mismatch. "
                f"Expected: {self.BASIC_REQUIRED_CLICKABLE}, "
                f"Got: {clickable}"
            )
            self.add_validation("Basic agents", False, "Agent list mismatch")
            return False

        self.add_validation("Basic constraint", True, f"Exactly 4 clickable: {', '.join(sorted(clickable))}")
        return True

    def validate_inclusion_ordering(self) -> bool:
        """Validate plan inclusion (ultimum ⊇ premium ⊇ pro ⊇ basic)"""
        print("\n🔍 Validating inclusion ordering...")

        all_valid = True

        for i in range(len(self.PLAN_HIERARCHY) - 1):
            lower_plan = self.PLAN_HIERARCHY[i]
            higher_plan = self.PLAN_HIERARCHY[i + 1]

            lower_clickable = self._get_clickable_agents(lower_plan)
            higher_clickable = self._get_clickable_agents(higher_plan)

            # Check if higher plan includes all lower plan agents
            missing = lower_clickable - higher_clickable

            if missing:
                self.add_error(
                    f"Inclusion violation: {higher_plan} missing agents from {lower_plan}: "
                    f"{', '.join(sorted(missing))}"
                )
                self.add_validation(
                    f"Inclusion: {higher_plan} ⊇ {lower_plan}", False, f"Missing: {', '.join(sorted(missing))}"
                )
                all_valid = False
            else:
                additional = len(higher_clickable - lower_clickable)
                self.add_validation(
                    f"Inclusion: {higher_plan} ⊇ {lower_plan}", True, f"All included (+{additional} additional)"
                )

        return all_valid

    def _get_clickable_agents(self, plan: str) -> set[str]:
        """Get set of clickable agents for a plan"""
        plan_data = self.entitlements.get(plan, {})
        agents = plan_data.get("agents", {})

        return {agent_id for agent_id, data in agents.items() if data.get("clickable", False)}

    def validate_core_agents(self) -> bool:
        """Validate core agents are visible but not clickable"""
        print("\n🔍 Validating core agents...")

        all_valid = True

        for plan in self.REQUIRED_PLANS:
            plan_data = self.entitlements.get(plan, {})
            agents = plan_data.get("agents", {})

            for core_agent in self.CORE_AGENTS:
                if core_agent not in agents:
                    self.add_error(f"Core agent {core_agent} missing from {plan} plan")
                    all_valid = False
                    continue

                agent_data = agents[core_agent]
                visible = agent_data.get("visible", False)
                clickable = agent_data.get("clickable", False)

                if not visible:
                    self.add_error(f"Core agent {core_agent} not visible in {plan} plan")
                    all_valid = False

                if clickable:
                    self.add_error(f"Core agent {core_agent} is clickable in {plan} plan (should never be)")
                    all_valid = False

        if all_valid:
            self.add_validation(
                "Core agents", True, f"{len(self.CORE_AGENTS)} core agents: visible, not clickable in all plans"
            )
        else:
            self.add_validation("Core agents", False, "Violations found")

        return all_valid

    def validate_system_agents(self) -> bool:
        """Validate system agents are visible but not clickable"""
        print("\n🔍 Validating system agents...")

        all_valid = True

        for plan in self.REQUIRED_PLANS:
            plan_data = self.entitlements.get(plan, {})
            agents = plan_data.get("agents", {})

            for system_agent in self.SYSTEM_AGENTS:
                if system_agent not in agents:
                    # System agents might not be in all plans - that's ok
                    continue

                agent_data = agents[system_agent]
                visible = agent_data.get("visible", False)
                clickable = agent_data.get("clickable", False)

                if clickable:
                    self.add_error(f"System agent {system_agent} is clickable in {plan} plan (should never be)")
                    all_valid = False

        if all_valid:
            self.add_validation("System agents", True, f"{len(self.SYSTEM_AGENTS)} system agents: never clickable")
        else:
            self.add_validation("System agents", False, "Violations found")

        return all_valid

    def validate_baseline_coverage(self) -> bool:
        """Validate no agent outside baseline"""
        print("\n🔍 Validating baseline coverage...")

        if not self.baseline:
            self.add_warning("Baseline not available, skipping coverage check")
            return True

        baseline_agents = set(self.baseline.get("agents", {}).keys())

        all_valid = True

        for plan in self.REQUIRED_PLANS:
            plan_data = self.entitlements.get(plan, {})
            agents = plan_data.get("agents", {})

            entitlement_agents = set(agents.keys())

            # Check for agents not in baseline
            extra_agents = entitlement_agents - baseline_agents

            if extra_agents:
                self.add_error(f"Plan {plan} has agents not in baseline: {', '.join(sorted(extra_agents))}")
                all_valid = False

        if all_valid:
            total_agents = len(self.entitlements.get(self.REQUIRED_PLANS[0], {}).get("agents", {}))
            self.add_validation("Baseline coverage", True, f"All {total_agents} agents from baseline")
        else:
            self.add_validation("Baseline coverage", False, "Agents outside baseline")

        return all_valid

    def validate_limits_monotonicity(self) -> bool:
        """Validate that limits increase with plan tier"""
        print("\n🔍 Validating limits monotonicity...")

        all_valid = True

        # Check workflows_per_agent increases
        workflows = []
        for plan in self.PLAN_HIERARCHY:
            plan_data = self.entitlements.get(plan, {})
            limit = plan_data.get("limits", {}).get("workflows_per_agent", 0)
            workflows.append((plan, limit))

        for i in range(len(workflows) - 1):
            lower_plan, lower_limit = workflows[i]
            higher_plan, higher_limit = workflows[i + 1]

            # -1 means unlimited, should be greater than any number
            if higher_limit == -1:
                continue

            if lower_limit > higher_limit and lower_limit != -1:
                self.add_error(f"Workflow limit decreases: {lower_plan}={lower_limit} > {higher_plan}={higher_limit}")
                all_valid = False

        if all_valid:
            workflow_str = " → ".join([f"{p}:{l}" for p, l in workflows])
            self.add_validation("Limits monotonicity", True, f"Workflows: {workflow_str}")
        else:
            self.add_validation("Limits monotonicity", False, "Non-monotonic limits")

        return all_valid

    def generate_report(self) -> dict:
        """Generate validation report"""
        return {
            "version": "1.0.0",
            "validated_at": datetime.now().isoformat(),
            "entitlements_file": str(self.entitlements_path),
            "status": "passed" if not self.errors else "failed",
            "summary": {
                "total_validations": len(self.validations),
                "passed": sum(1 for v in self.validations if v["passed"]),
                "failed": sum(1 for v in self.validations if not v["passed"]),
                "errors": len(self.errors),
                "warnings": len(self.warnings),
            },
            "validations": self.validations,
            "errors": self.errors,
            "warnings": self.warnings,
            "plans_validated": self.REQUIRED_PLANS,
            "constraints": {
                "basic_clickable_count": self.BASIC_REQUIRED_COUNT,
                "basic_required_agents": self.BASIC_REQUIRED_CLICKABLE,
                "core_agents": self.CORE_AGENTS,
                "system_agents": self.SYSTEM_AGENTS,
                "inclusion_order": " ⊇ ".join(reversed(self.PLAN_HIERARCHY)),
            },
        }

    def save_report(self):
        """Save validation report"""
        print("\n💾 Saving validation report...")

        report = self.generate_report()

        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_path, "w") as f:
            json.dump(report, f, indent=2, sort_keys=False)

        file_size = self.output_path.stat().st_size
        print(f"  ✅ Saved: {self.output_path} ({file_size:,} bytes)")

    def run(self) -> bool:
        """Run all validations"""
        try:
            if not self.load_entitlements():
                return False

            self.load_baseline()

            # Run all validations
            validations = [
                self.validate_structure(),
                self.validate_basic_constraint(),
                self.validate_inclusion_ordering(),
                self.validate_core_agents(),
                self.validate_system_agents(),
                self.validate_baseline_coverage(),
                self.validate_limits_monotonicity(),
            ]

            self.save_report()

            # Print summary
            print("\n" + "=" * 80)
            print("📊 VALIDATION SUMMARY")
            print("=" * 80)
            print(f"✅ Passed: {sum(1 for v in self.validations if v['passed'])}/{len(self.validations)}")
            print(f"❌ Failed: {sum(1 for v in self.validations if not v['passed'])}/{len(self.validations)}")
            print(f"⚠️  Warnings: {len(self.warnings)}")

            if self.errors:
                print("\n❌ ERRORS:")
                for error in self.errors:
                    print(f"  • {error}")

            if self.warnings:
                print("\n⚠️  WARNINGS:")
                for warning in self.warnings:
                    print(f"  • {warning}")

            all_passed = all(validations) and not self.errors

            if all_passed:
                print("\n✅ All validations passed!")
            else:
                print("\n❌ Validation failed!")

            return all_passed

        except Exception as e:
            print(f"\n❌ VALIDATION ERROR: {e}")
            import traceback

            traceback.print_exc()
            return False


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent

    print("=" * 80)
    print("🔍 ELION Hyper-Dashboard - Entitlements Validator")
    print("=" * 80)
    print(f"📂 Project root: {project_root}")
    print()

    validator = EntitlementsValidator(project_root)
    success = validator.run()

    # Exit with appropriate code for CI
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
