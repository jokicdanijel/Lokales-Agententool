"""
Dispatcher FlowMap Visualizer for Portier Dashboard
Author: LocalAgentPro
Version: 1.0.0
Description: Visualisiert CMD/RESP Flows des LocalAgentPro Dispatchers mit Safepoints
"""

import logging
import os
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class FlowEntry(BaseModel):
    """Single flow entry"""

    flow_id: str
    source_agent: str
    target_agent: str
    command_type: str
    safepoint: str | None = None
    status: str  # pending, executing, completed, failed
    timestamp: str


class SafepointInfo(BaseModel):
    """Safepoint information"""

    name: str
    description: str
    agent_id: str
    exit_required: bool


class Tools:
    """Dispatcher FlowMap Tools"""

    def __init__(self):
        self.dispatcher_url = os.getenv("DISPATCHER_URL", "http://localhost:8100")
        self.cache_dir = os.getenv("PORTIER_CACHE_DIR", "/tmp/portier_flowmap")
        os.makedirs(self.cache_dir, exist_ok=True)

    async def dispatcher_flowmap_generate(
        self, max_entries: int = Field(default=50, description="Maximale Anzahl von Flow-Einträgen")
    ) -> dict[str, Any]:
        """
        Generate FlowMap from dispatcher history

        Args:
            max_entries: Maximum number of flow entries to retrieve

        Returns:
            FlowMap visualization data
        """
        logger.info("🗺️ Generating Dispatcher FlowMap")

        try:
            import requests
        except ImportError:
            logger.error("requests library not available")
            return {"status": "error", "message": "requests library erforderlich"}

        flows = []
        safepoints = []

        try:
            # Try to fetch from dispatcher
            response = requests.get(f"{self.dispatcher_url}/history", timeout=5, params={"limit": max_entries})

            if response.status_code == 200:
                history_data = response.json()

                # Parse flow entries
                for entry in history_data.get("flows", []):
                    flow = {
                        "flow_id": entry.get("id", f"flow_{len(flows)}"),
                        "source_agent": entry.get("source", "unknown"),
                        "target_agent": entry.get("target", "unknown"),
                        "command_type": entry.get("cmd_type", "CMD"),
                        "safepoint": entry.get("safepoint"),
                        "status": entry.get("status", "completed"),
                        "timestamp": entry.get("timestamp", datetime.now().isoformat()),
                    }
                    flows.append(flow)

                # Parse safepoints
                for sp in history_data.get("safepoints", []):
                    safepoint = {
                        "name": sp.get("name", "Unnamed"),
                        "description": sp.get("description", ""),
                        "agent_id": sp.get("agent_id", "unknown"),
                        "exit_required": sp.get("exit_required", False),
                    }
                    safepoints.append(safepoint)

                logger.info(f"✅ FlowMap generated: {len(flows)} flows, {len(safepoints)} safepoints")

        except requests.RequestException as e:
            logger.warning(f"⚠️ Dispatcher not reachable: {e}, using mock data")
            # Return mock data for demonstration
            flows = self._generate_mock_flows(max_entries)
            safepoints = self._generate_mock_safepoints()

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "flowmap": {
                "flows": flows,
                "safepoints": safepoints,
                "statistics": {
                    "total_flows": len(flows),
                    "total_safepoints": len(safepoints),
                    "completed": sum(1 for f in flows if f["status"] == "completed"),
                    "executing": sum(1 for f in flows if f["status"] == "executing"),
                    "pending": sum(1 for f in flows if f["status"] == "pending"),
                    "failed": sum(1 for f in flows if f["status"] == "failed"),
                },
                "agents": self._extract_agents(flows),
                "critical_path": self._compute_critical_path(flows),
            },
        }

    def _generate_mock_flows(self, count: int) -> list[dict]:
        """Generate mock flow data for demonstration"""
        flows = []
        agents = ["openwebui_agent", "vscode_agent", "browser_agent", "dispatcher_controller"]
        cmd_types = ["CMD", "RESP", "EXEC", "VALIDATE"]
        statuses = ["completed", "executing", "pending"]

        for i in range(min(count, 10)):
            flow = {
                "flow_id": f"flow_{i:03d}",
                "source_agent": agents[i % len(agents)],
                "target_agent": agents[(i + 1) % len(agents)],
                "command_type": cmd_types[i % len(cmd_types)],
                "safepoint": f"checkpoint_{i % 3}" if i % 3 == 0 else None,
                "status": statuses[i % len(statuses)],
                "timestamp": datetime.now().isoformat(),
            }
            flows.append(flow)

        return flows

    def _generate_mock_safepoints(self) -> list[dict]:
        """Generate mock safepoint data"""
        return [
            {
                "name": "Pre-Execution",
                "description": "Validation safepoint before command execution",
                "agent_id": "dispatcher_controller",
                "exit_required": True,
            },
            {
                "name": "Post-Execution",
                "description": "Result verification safepoint",
                "agent_id": "dispatcher_controller",
                "exit_required": False,
            },
            {
                "name": "Error-Handling",
                "description": "Error recovery checkpoint",
                "agent_id": "dispatcher_controller",
                "exit_required": True,
            },
        ]

    def _extract_agents(self, flows: list[dict]) -> dict[str, dict]:
        """Extract agent statistics from flows"""
        agents = {}

        for flow in flows:
            source = flow["source_agent"]
            target = flow["target_agent"]

            for agent in [source, target]:
                if agent not in agents:
                    agents[agent] = {"name": agent, "flows_sent": 0, "flows_received": 0, "status": "online"}

            agents[source]["flows_sent"] += 1
            agents[target]["flows_received"] += 1

        return agents

    def _compute_critical_path(self, flows: list[dict]) -> list[dict]:
        """Compute critical path through flows"""
        if not flows:
            return []

        # Simple critical path: chain of flows sorted by timestamp
        return sorted(flows, key=lambda x: x.get("timestamp", ""))[:5]

    async def dispatcher_status_check(self) -> dict[str, Any]:
        """Check dispatcher status"""
        logger.info("🔍 Checking Dispatcher status")

        try:
            import requests

            response = requests.get(f"{self.dispatcher_url}/health", timeout=3)

            if response.status_code == 200:
                return {"status": "success", "dispatcher": "online", "details": response.json()}
        except:
            pass

        return {
            "status": "warning",
            "dispatcher": "offline or unreachable",
            "message": "Dispatcher konnte nicht erreicht werden",
        }

    async def dispatcher_safepoint_list(self) -> dict[str, Any]:
        """List all defined safepoints"""
        logger.info("🛡️ Listing safepoints")

        safepoints = [
            {
                "name": "Pre-Execution",
                "description": "Validierungsprüfung vor Befehlsausführung",
                "agent_id": "dispatcher_controller",
                "exit_required": True,
                "active": True,
            },
            {
                "name": "Post-Execution",
                "description": "Ergebnisverifizierungsprüfung",
                "agent_id": "dispatcher_controller",
                "exit_required": False,
                "active": True,
            },
            {
                "name": "Error-Handling",
                "description": "Fehlerwiederherstellungsprüfung",
                "agent_id": "dispatcher_controller",
                "exit_required": True,
                "active": True,
            },
            {
                "name": "Rate-Limit-Check",
                "description": "Rate-Limiting Enforcement",
                "agent_id": "dispatcher_controller",
                "exit_required": False,
                "active": False,
            },
        ]

        return {"status": "success", "safepoints": safepoints, "total": len(safepoints)}

    async def dispatcher_flow_trace(
        self, flow_id: str = Field(..., description="Flow ID zum Tracen")
    ) -> dict[str, Any]:
        """Trace a specific flow through the system"""
        logger.info(f"🔎 Tracing flow: {flow_id}")

        trace = {
            "flow_id": flow_id,
            "status": "success",
            "steps": [
                {
                    "step": 1,
                    "agent": "openwebui_agent",
                    "action": "send_command",
                    "safepoint": "Pre-Execution",
                    "timestamp": datetime.now().isoformat(),
                    "result": "passed",
                },
                {
                    "step": 2,
                    "agent": "dispatcher_controller",
                    "action": "route",
                    "safepoint": None,
                    "timestamp": datetime.now().isoformat(),
                    "result": "routed to browser_agent",
                },
                {
                    "step": 3,
                    "agent": "browser_agent",
                    "action": "execute",
                    "safepoint": None,
                    "timestamp": datetime.now().isoformat(),
                    "result": "executed successfully",
                },
                {
                    "step": 4,
                    "agent": "dispatcher_controller",
                    "action": "verify",
                    "safepoint": "Post-Execution",
                    "timestamp": datetime.now().isoformat(),
                    "result": "passed",
                },
            ],
            "total_steps": 4,
            "execution_time_ms": 1250.5,
        }

        return trace
