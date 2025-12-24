#!/usr/bin/env python3
"""
ELION Hyper-Dashboard - Entitlements Builder
Generates machine-readable plan entitlements from baseline + inventory

INPUTS:
- system_baseline.yaml (agent definitions, plan structure)
- artifacts/agent_inventory.json (discovery output)

OUTPUT:
- build/entitlements.json (plan_id → agent_id → {visible, clickable, limits, gates})

RULES:
- Plans: basic, pro, premium, ultimum
- Higher plan includes all lower plan entitlements (inclusion)
- Core agents (opena1, opena2) always visible, never gated
- System agents (opena20, opena21) visible but not clickable
- Basic: EXACTLY 4 clickable agents (opena3, opena4, opena7, opena11)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar

import yaml


class EntitlementsBuilder:
    """Builds plan entitlements from baseline and inventory"""

    # HARD-CODED CONSTRAINTS (as per requirements)
    CORE_AGENTS: ClassVar[list[str]] = ["opena1", "opena2"]  # Always visible, never gated
    SYSTEM_AGENTS: ClassVar[list[str]] = ["opena20", "opena21"]  # Visible but not clickable

    # Plan hierarchy (lower → higher)
    PLAN_HIERARCHY: ClassVar[list[str]] = ["basic", "pro", "premium", "ultimum"]

    # Basic plan MUST have exactly these 4 clickable agents
    BASIC_CLICKABLE: ClassVar[list[str]] = ["opena3", "opena4", "opena7", "opena11"]

    # Default limits per plan
    DEFAULT_LIMITS: ClassVar[dict[str, dict[str, Any]]] = {
        "basic": {
            "workflows_per_agent": 4,
            "logs_access": "read-only",
            "max_concurrent_tasks": 2,
            "api_calls_per_day": 1000,
        },
        "pro": {
            "workflows_per_agent": 10,
            "logs_access": "read-write",
            "max_concurrent_tasks": 5,
            "api_calls_per_day": 5000,
        },
        "premium": {
            "workflows_per_agent": 25,
            "logs_access": "read-write",
            "max_concurrent_tasks": 10,
            "api_calls_per_day": 20000,
        },
        "ultimum": {
            "workflows_per_agent": -1,  # unlimited
            "logs_access": "full",
            "max_concurrent_tasks": -1,  # unlimited
            "api_calls_per_day": -1,  # unlimited
        },
    }

    def __init__(self, project_root: Path):
        self.root = project_root
        self.baseline_path = self.root / "system_baseline.yaml"
        self.inventory_path = self.root / "artifacts" / "agent_inventory.json"
        self.output_path = self.root / "build" / "entitlements.json"

        self.baseline = None
        self.inventory = None
        self.entitlements = {}

    def load_sources(self):
        """Load baseline and inventory"""
        print("📂 Loading sources...")

        # Load baseline
        if self.baseline_path.exists():
            with open(self.baseline_path) as f:
                self.baseline = yaml.safe_load(f)
            print(f"  ✅ Loaded baseline: {self.baseline_path}")
        else:
            print(f"  ⚠️  Baseline not found: {self.baseline_path}")
            print("  📝 Creating default baseline...")
            self.baseline = self._create_default_baseline()
            self._save_baseline()

        # Load inventory
        if self.inventory_path.exists():
            with open(self.inventory_path) as f:
                self.inventory = json.load(f)
            print(f"  ✅ Loaded inventory: {self.inventory_path}")
        else:
            print(f"  ⚠️  Inventory not found: {self.inventory_path}")
            print("  📝 Creating minimal inventory from baseline...")
            self.inventory = self._create_minimal_inventory()

    def _create_default_baseline(self) -> dict:
        """Create default baseline structure"""
        return {
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "agents": {
                f"opena{i}": {
                    "id": f"opena{i}",
                    "name": f"Agent {i}",
                    "port": 12343 + i,
                    "role": "service",
                    "visibility": "public" if i not in [20, 21] else "system",
                }
                for i in range(1, 22)
            },
            "plans": {
                "basic": {
                    "name": "Basic Plan",
                    "description": "Communication essentials",
                    "agents": self.BASIC_CLICKABLE,
                },
                "pro": {
                    "name": "Pro Plan",
                    "description": "Business tools + CRM",
                    "agents": ["opena3", "opena4", "opena7", "opena8", "opena11", "opena12", "opena14", "opena18"],
                },
                "premium": {
                    "name": "Premium Plan",
                    "description": "Automation + E-Commerce",
                    "agents": [
                        "opena3",
                        "opena4",
                        "opena6",
                        "opena7",
                        "opena8",
                        "opena9",
                        "opena11",
                        "opena12",
                        "opena14",
                        "opena15",
                        "opena16",
                        "opena18",
                    ],
                },
                "ultimum": {
                    "name": "Ultimum Plan",
                    "description": "Enterprise features + Finance",
                    "agents": [
                        "opena3",
                        "opena4",
                        "opena5",
                        "opena6",
                        "opena7",
                        "opena8",
                        "opena9",
                        "opena10",
                        "opena11",
                        "opena12",
                        "opena13",
                        "opena14",
                        "opena15",
                        "opena16",
                        "opena17",
                        "opena18",
                        "opena19",
                    ],
                },
            },
        }

    def _save_baseline(self):
        """Save default baseline"""
        self.baseline_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.baseline_path, "w") as f:
            yaml.dump(self.baseline, f, default_flow_style=False, sort_keys=False)
        print(f"  ✅ Created baseline: {self.baseline_path}")

    def _create_minimal_inventory(self) -> dict:
        """Create minimal inventory from baseline"""
        agents = {}
        for agent_id, agent_data in self.baseline.get("agents", {}).items():
            agents[agent_id] = {
                "name": agent_data.get("name", agent_id),
                "port": agent_data.get("port", 0),
                "role": agent_data.get("role", "service"),
                "visibility": agent_data.get("visibility", "public"),
                "description": agent_data.get("description", ""),
                "has_main": False,
                "all_endpoints": [],
            }

        return {
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "baseline_hash": "minimal",
            "agent_count": len(agents),
            "agents": agents,
        }

    def build(self):
        """Build entitlements for all plans"""
        print("\n🏗️  Building entitlements...")

        all_agent_ids = set(self.inventory.get("agents", {}).keys())
        print(f"  📊 Total agents: {len(all_agent_ids)}")

        # Build entitlements for each plan
        for plan in sorted(self.PLAN_HIERARCHY):
            print(f"\n  🔐 Building plan: {plan.upper()}")
            self.entitlements[plan] = self._build_plan_entitlements(plan, all_agent_ids)

        # Add metadata
        self.entitlements["_metadata"] = {
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "baseline_hash": self.inventory.get("baseline_hash", "unknown"),
            "total_agents": len(all_agent_ids),
            "plans": self.PLAN_HIERARCHY,
            "rules": {
                "core_agents": self.CORE_AGENTS,
                "system_agents": self.SYSTEM_AGENTS,
                "basic_clickable": self.BASIC_CLICKABLE,
                "inclusion_order": "ultimum ⊇ premium ⊇ pro ⊇ basic",
            },
        }

        print(f"\n  ✅ Built entitlements for {len(self.PLAN_HIERARCHY)} plans")

    def _build_plan_entitlements(self, plan: str, all_agent_ids: set[str]) -> dict:
        """Build entitlements for a specific plan"""

        # Get clickable agents for this plan
        clickable_agents = self._get_clickable_agents_for_plan(plan)

        # Get plan-specific limits
        limits = self.DEFAULT_LIMITS.get(plan, {})

        plan_data = {
            "name": self.baseline.get("plans", {}).get(plan, {}).get("name", plan.title()),
            "description": self.baseline.get("plans", {}).get(plan, {}).get("description", ""),
            "limits": limits,
            "agents": {},
        }

        # Build agent-specific entitlements
        for agent_id in sorted(all_agent_ids):
            agent_entitlements = self._build_agent_entitlements(agent_id, plan, clickable_agents)
            plan_data["agents"][agent_id] = agent_entitlements

        # Count clickable agents (excluding core and system)
        clickable_count = sum(
            1
            for agent_id, data in plan_data["agents"].items()
            if data["clickable"] and agent_id not in self.CORE_AGENTS + self.SYSTEM_AGENTS
        )

        plan_data["clickable_count"] = clickable_count
        print(f"    📊 {clickable_count} clickable agents (excluding core/system)")

        return plan_data

    def _get_clickable_agents_for_plan(self, plan: str) -> set[str]:
        """Get clickable agents for a plan (with inclusion)"""

        clickable = set()

        # Add agents for this plan and all lower plans (inclusion)
        plan_index = self.PLAN_HIERARCHY.index(plan)
        for lower_plan in self.PLAN_HIERARCHY[: plan_index + 1]:
            plan_agents = self.baseline.get("plans", {}).get(lower_plan, {}).get("agents", [])
            clickable.update(plan_agents)

        # Core agents are NEVER clickable (always visible but locked)
        clickable -= set(self.CORE_AGENTS)

        # System agents are NEVER clickable
        clickable -= set(self.SYSTEM_AGENTS)

        return clickable

    def _build_agent_entitlements(self, agent_id: str, plan: str, clickable_agents: set[str]) -> dict:
        """Build entitlements for a specific agent in a plan"""

        agent_data = self.inventory.get("agents", {}).get(agent_id, {})
        visibility = agent_data.get("visibility", "public")

        # Core agents: always visible, never clickable
        if agent_id in self.CORE_AGENTS:
            visible = True
            clickable = False
            gate_reason = "Core infrastructure - always visible, not directly accessible"

        # System agents: visible but not clickable
        elif agent_id in self.SYSTEM_AGENTS:
            visible = True
            clickable = False
            gate_reason = "System agent - monitoring/orchestration only"

        # System visibility agents: never visible
        elif visibility == "system":
            visible = False
            clickable = False
            gate_reason = "System-internal agent"

        # Regular agents: check plan entitlements
        else:
            visible = True  # All agents visible (per requirements)
            clickable = agent_id in clickable_agents
            gate_reason = None if clickable else f"Not available in {plan} plan"

        entitlements = {
            "visible": visible,
            "clickable": clickable,
            "gates": {"plan_required": plan if clickable else self._get_required_plan(agent_id), "reason": gate_reason},
            "limits": {},
        }

        # Add plan-specific limits if clickable
        if clickable:
            plan_limits = self.DEFAULT_LIMITS.get(plan, {})
            entitlements["limits"] = {
                "workflows": plan_limits.get("workflows_per_agent", 0),
                "logs_access": plan_limits.get("logs_access", "none"),
                "max_concurrent_tasks": plan_limits.get("max_concurrent_tasks", 0),
            }

        return entitlements

    def _get_required_plan(self, agent_id: str) -> str:
        """Get the minimum plan required for an agent"""
        for plan in self.PLAN_HIERARCHY:
            plan_agents = self.baseline.get("plans", {}).get(plan, {}).get("agents", [])
            if agent_id in plan_agents:
                return plan
        return "ultimum"  # Default to highest plan

    def save(self):
        """Save entitlements to file"""
        print("\n💾 Saving entitlements...")

        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_path, "w") as f:
            json.dump(self.entitlements, f, indent=2, sort_keys=False)

        file_size = self.output_path.stat().st_size
        print(f"  ✅ Saved: {self.output_path} ({file_size:,} bytes)")

    def verify_basic_constraint(self) -> bool:
        """Verify that Basic plan has EXACTLY 4 clickable agents"""
        print("\n🔍 Verifying Basic plan constraint...")

        basic_plan = self.entitlements.get("basic", {})
        clickable_count = basic_plan.get("clickable_count", 0)

        if clickable_count == 4:
            print("  ✅ Basic plan has exactly 4 clickable agents")

            # List them
            clickable = [
                agent_id
                for agent_id, data in basic_plan.get("agents", {}).items()
                if data["clickable"] and agent_id not in self.CORE_AGENTS + self.SYSTEM_AGENTS
            ]
            print(f"  📋 Clickable: {', '.join(sorted(clickable))}")

            # Verify they match the required list
            if set(clickable) == set(self.BASIC_CLICKABLE):
                print(f"  ✅ Matches required list: {', '.join(self.BASIC_CLICKABLE)}")
                return True
            else:
                print(f"  ❌ MISMATCH! Expected: {', '.join(self.BASIC_CLICKABLE)}")
                return False
        else:
            print(f"  ❌ FAILED! Basic plan has {clickable_count} clickable agents (expected 4)")
            return False

    def run(self) -> bool:
        """Run the full build process"""
        try:
            self.load_sources()
            self.build()
            self.save()

            # Verify constraints
            if not self.verify_basic_constraint():
                print("\n❌ CONSTRAINT VIOLATION: Basic plan must have exactly 4 clickable agents")
                return False

            print("\n✅ Entitlements build complete!")
            return True

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback

            traceback.print_exc()
            return False


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent

    print("=" * 80)
    print("🔐 ELION Hyper-Dashboard - Entitlements Builder")
    print("=" * 80)
    print(f"📂 Project root: {project_root}")
    print()

    builder = EntitlementsBuilder(project_root)
    success = builder.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
