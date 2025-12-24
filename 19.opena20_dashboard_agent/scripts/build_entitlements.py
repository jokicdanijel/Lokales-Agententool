#!/usr/bin/env python3
"""
ELION Hyper-Dashboard – Entitlements Builder
==============================================
Generates machine-consumable entitlement gates from system baseline + agent inventory.

OUTPUTS:
- build/entitlements.json: Plan-to-Agent entitlements mapping

POLICY:
- Core agents (opena1, opena2): Always visible, always clickable
- System agents (opena20, opena21): Always visible, may not be clickable
- Basic plan: Exactly 4 clickable agents (opena3, opena4, opena7, opena11)
- Higher plans include all lower plan entitlements
- Basic plan: logs read-only, workflow limit 4/agent
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


class EntitlementsBuilder:
    """Compiles entitlements from baseline and inventory."""

    # Plan hierarchy (lower plans included in higher)
    PLAN_HIERARCHY = ["basic", "pro", "premium", "ultimum"]

    # Core agents: always visible and clickable
    CORE_AGENTS = ["opena1", "opena2"]

    # System agents: visible but not necessarily clickable
    SYSTEM_AGENTS = ["opena20", "opena21"]

    # Basic plan specific clickable agents
    BASIC_CLICKABLE = ["opena3", "opena4", "opena7", "opena11"]

    def __init__(self, baseline_path: str, inventory_path: str):
        self.baseline_path = Path(baseline_path)
        self.inventory_path = Path(inventory_path)
        self.baseline = None
        self.inventory = None

    def load_inputs(self) -> bool:
        """Load baseline and inventory files."""
        try:
            # Load system baseline
            with open(self.baseline_path) as f:
                self.baseline = yaml.safe_load(f)
            print(f"✓ Loaded baseline from {self.baseline_path}")

            # Load agent inventory
            with open(self.inventory_path) as f:
                self.inventory = json.load(f)
            print(f"✓ Loaded inventory from {self.inventory_path}")

            return True
        except Exception as e:
            print(f"✗ Error loading inputs: {e}", file=sys.stderr)
            return False

    def extract_plan_agents(self) -> dict[str, list[str]]:
        """Extract agent IDs for each plan from baseline."""
        plan_agents = {}

        plans = self.baseline.get("plans", {})
        for plan_id in self.PLAN_HIERARCHY:
            if plan_id in plans:
                agents = plans[plan_id].get("agents", [])
                plan_agents[plan_id] = agents
            else:
                plan_agents[plan_id] = []

        return plan_agents

    def get_all_agents(self) -> list[str]:
        """Get all agent IDs from inventory."""
        agents = []
        for agent_data in self.inventory.get("agents", []):
            agent_id = agent_data.get("id")
            if agent_id:
                agents.append(agent_id)
        return agents

    def build_plan_entitlements(self, plan_id: str, plan_agents: dict[str, list[str]]) -> dict[str, dict]:
        """Build entitlements for a specific plan."""
        entitlements = {}

        # Get cumulative agents (all agents from this plan and lower plans)
        cumulative_agents = set()
        for lower_plan in self.PLAN_HIERARCHY:
            cumulative_agents.update(plan_agents.get(lower_plan, []))
            if lower_plan == plan_id:
                break

        # Get all discovered agents
        all_agents = self.get_all_agents()

        for agent_id in all_agents:
            # Core agents: always visible and clickable
            if agent_id in self.CORE_AGENTS:
                entitlements[agent_id] = {
                    "visible": True,
                    "clickable": True,
                    "reason": "core_agent",
                    "limits": {},
                    "gates": [],
                }

            # System agents: visible, not clickable by default
            elif agent_id in self.SYSTEM_AGENTS:
                entitlements[agent_id] = {
                    "visible": True,
                    "clickable": False,
                    "reason": "system_agent",
                    "limits": {},
                    "gates": ["system_only"],
                }

            # Plan-specific agents
            elif agent_id in cumulative_agents:
                # Basic plan specific rules
                if plan_id == "basic":
                    clickable = agent_id in self.BASIC_CLICKABLE
                    limits = {"logs_access": "read_only", "workflow_limit": 4}
                    gates = [] if clickable else ["requires_upgrade"]
                else:
                    clickable = True
                    limits = {"logs_access": "full", "workflow_limit": -1}  # unlimited
                    gates = []

                entitlements[agent_id] = {
                    "visible": True,
                    "clickable": clickable,
                    "reason": f"included_in_{plan_id}",
                    "limits": limits,
                    "gates": gates,
                }

            # Not in this plan
            else:
                entitlements[agent_id] = {
                    "visible": True,
                    "clickable": False,
                    "reason": "not_in_plan",
                    "limits": {},
                    "gates": ["requires_upgrade"],
                }

        return entitlements

    def build(self) -> dict[str, Any]:
        """Build complete entitlements structure."""
        plan_agents = self.extract_plan_agents()

        entitlements = {
            "version": "1.0",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "source": {"baseline": str(self.baseline_path), "inventory": str(self.inventory_path)},
            "plans": {},
        }

        # Build entitlements for each plan
        for plan_id in self.PLAN_HIERARCHY:
            print(f"Building entitlements for plan: {plan_id}")
            entitlements["plans"][plan_id] = {
                "name": self.baseline["plans"][plan_id]["name"],
                "description": self.baseline["plans"][plan_id]["description"],
                "agents": self.build_plan_entitlements(plan_id, plan_agents),
            }

        # Add metadata
        entitlements["metadata"] = {
            "total_agents": len(self.get_all_agents()),
            "core_agents": self.CORE_AGENTS,
            "system_agents": self.SYSTEM_AGENTS,
            "basic_clickable": self.BASIC_CLICKABLE,
            "plan_hierarchy": self.PLAN_HIERARCHY,
        }

        return entitlements

    def save(self, entitlements: dict[str, Any], output_path: str) -> bool:
        """Save entitlements to JSON file."""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w") as f:
                json.dump(entitlements, f, indent=2)

            print(f"✓ Entitlements saved to {output_file}")

            # Print summary
            print("\n" + "=" * 60)
            print("ENTITLEMENTS SUMMARY")
            print("=" * 60)
            for plan_id, plan_data in entitlements["plans"].items():
                clickable_count = sum(1 for agent_data in plan_data["agents"].values() if agent_data["clickable"])
                print(f"{plan_id.upper()}: {clickable_count} clickable agents")
            print("=" * 60)

            return True
        except Exception as e:
            print(f"✗ Error saving entitlements: {e}", file=sys.stderr)
            return False


def main():
    """Main entry point."""
    # Get project root (parent of scripts/)
    project_root = Path(__file__).parent.parent

    baseline_path = project_root / "system_baseline.yaml"
    inventory_path = project_root / "artifacts" / "agent_inventory.json"
    output_path = project_root / "build" / "entitlements.json"

    print("=" * 60)
    print("ELION Entitlements Builder")
    print("=" * 60)
    print(f"Baseline:  {baseline_path}")
    print(f"Inventory: {inventory_path}")
    print(f"Output:    {output_path}")
    print("=" * 60 + "\n")

    # Build entitlements
    builder = EntitlementsBuilder(baseline_path=str(baseline_path), inventory_path=str(inventory_path))

    if not builder.load_inputs():
        sys.exit(1)

    entitlements = builder.build()

    if not builder.save(entitlements, str(output_path)):
        sys.exit(1)

    print("\n✓ Entitlements build complete!")
    sys.exit(0)


if __name__ == "__main__":
    main()
