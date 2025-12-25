"""
Dispatcher Client - Communication with opena1/opena2
Handles Safepoint integration and command routing through Portier
"""

import logging
from datetime import datetime
from typing import Any

import requests

logger = logging.getLogger("dispatcher_client")


class DispatcherClient:
    """Client for communicating with opena1 (Dispatcher) and opena2 (Archivator)"""

    def __init__(
        self,
        agent_name: str = "5.opena6_browser",
        bearer_token: str = None,
        dispatcher_url: str = "http://0.0.0.0:12345",
        archivator_url: str = "http://0.0.0.0:12346",
    ):
        """Initialize dispatcher client"""
        self.agent_name = agent_name
        self.bearer_token = bearer_token
        self.dispatcher_url = dispatcher_url
        self.archivator_url = archivator_url

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}" if bearer_token else None,
        }

        logger.info(f"✅ DispatcherClient initialized for {agent_name}")

    def register_agent(self) -> bool:
        """Register agent with dispatcher"""
        try:
            payload = {
                "agent_name": self.agent_name,
                "agent_type": "browser_automation",
                "port": 12350,
                "status": "ready",
                "timestamp": datetime.utcnow().isoformat(),
            }

            response = requests.post(f"{self.dispatcher_url}/register", json=payload, headers=self.headers, timeout=5)

            if response.status_code == 200:
                logger.info("✅ Agent registered with dispatcher")
                return True
            else:
                logger.warning(f"⚠️  Registration failed: {response.status_code}")
                return False

        except Exception as e:
            logger.warning(f"⚠️  Could not register with dispatcher: {e}")
            return False

    def fetch_command(self) -> dict[str, Any] | None:
        """Fetch pending command from archivator"""
        try:
            response = requests.get(f"{self.archivator_url}/pending", headers=self.headers, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data.get("command"):
                    logger.info("📥 Command fetched from archivator")
                    return data.get("command")

            return None

        except Exception as e:
            logger.debug(f"Could not fetch command: {e}")
            return None

    def report_result(self, result: dict[str, Any]) -> bool:
        """Report execution result to archivator"""
        try:
            payload = {
                "agent": self.agent_name,
                "safepoint_type": "RESP",
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
            }

            response = requests.post(f"{self.archivator_url}/safepoint", json=payload, headers=self.headers, timeout=5)

            if response.status_code in [200, 201]:
                logger.info("✅ Result reported to archivator")
                return True
            else:
                logger.warning(f"⚠️  Result reporting failed: {response.status_code}")
                return False

        except Exception as e:
            logger.warning(f"⚠️  Could not report result: {e}")
            return False

    def get_agent_status(self) -> dict[str, Any]:
        """Get agent status from dispatcher"""
        try:
            response = requests.get(f"{self.dispatcher_url}/status/{self.agent_name}", headers=self.headers, timeout=5)

            if response.status_code == 200:
                return response.json()

            return {}

        except Exception as e:
            logger.debug(f"Could not fetch agent status: {e}")
            return {}


class SafepointManager:
    """Manages Safepoint creation and storage"""

    def __init__(self, agent_name: str = "5.opena6_browser"):
        """Initialize safepoint manager"""
        self.agent_name = agent_name
        self.safepoints = {}
        logger.info("✅ SafepointManager initialized")

    def create_cmd_safepoint(self, command: dict[str, Any]) -> str:
        """Create CMD safepoint"""
        safepoint_id = f"sp_{len(self.safepoints):06d}"

        safepoint = {
            "id": safepoint_id,
            "type": "CMD",
            "agent": self.agent_name,
            "command": command,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",
        }

        self.safepoints[safepoint_id] = safepoint
        logger.info(f"📍 CMD Safepoint created: {safepoint_id}")

        return safepoint_id

    def create_resp_safepoint(self, command_id: str, result: dict[str, Any]) -> str:
        """Create RESP safepoint"""
        safepoint_id = f"sp_{len(self.safepoints):06d}"

        safepoint = {
            "id": safepoint_id,
            "type": "RESP",
            "agent": self.agent_name,
            "command_id": command_id,
            "result": result,
            "created_at": datetime.utcnow().isoformat(),
            "status": "complete",
        }

        self.safepoints[safepoint_id] = safepoint
        logger.info(f"📍 RESP Safepoint created: {safepoint_id}")

        return safepoint_id

    def get_safepoint(self, safepoint_id: str) -> dict[str, Any] | None:
        """Get safepoint details"""
        return self.safepoints.get(safepoint_id)

    def list_safepoints(self) -> list:
        """List all safepoints"""
        return list(self.safepoints.values())
