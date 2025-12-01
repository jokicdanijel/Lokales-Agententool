"""
Agent API Client - HTTP-Client für Kommunikation mit Dashboard (opena19).
Ermöglicht: Registration, Status-Updates, SSE-Events, Command-Forwarding.
"""

import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import asyncio

logger = logging.getLogger("agent_api")


class AgentAPIClient:
    """
    HTTP-Client für Kommunikation zwischen Mini-Orchestrator und Dashboard.
    
    Features:
    - Agent-Registration beim Dashboard
    - Status-Updates
    - Command-Forwarding
    - SSE-Event-Publishing
    """
    
    def __init__(
        self,
        dashboard_url: str = "http://127.0.0.1:12349",
        agent_id: str = "opena_mini_orchestrator",
        bearer_token: Optional[str] = None,
        timeout: int = 30
    ):
        self.dashboard_url = dashboard_url.rstrip("/")
        self.agent_id = agent_id
        self.bearer_token = bearer_token
        self.timeout = timeout
        
        # HTTP Client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers=self._get_headers()
        )
        
        logger.info(f"AgentAPIClient initialized: {self.dashboard_url} (agent_id: {self.agent_id})")
    
    def _get_headers(self) -> Dict[str, str]:
        """Generiert Headers inkl. Bearer-Token"""
        headers = {"Content-Type": "application/json"}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        return headers
    
    async def register_agent(
        self,
        port: int,
        capabilities: list,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Registriert den Mini-Orchestrator beim Dashboard.
        
        Args:
            port: Port auf dem der Mini-Orchestrator läuft
            capabilities: Liste von Capabilities (z.B. ["email", "browser", "workflow"])
            metadata: Zusätzliche Metadata
            
        Returns:
            Dict: Response vom Dashboard
        """
        endpoint = f"{self.dashboard_url}/api/agent/register"
        
        payload = {
            "agent_id": self.agent_id,
            "endpoint": f"http://127.0.0.1:{port}",
            "capabilities": capabilities,
            "status": "online",
            "metadata": metadata or {}
        }
        
        try:
            response = await self.client.post(endpoint, json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Agent registered successfully: {self.agent_id}")
            return data
        
        except httpx.HTTPError as e:
            logger.error(f"Registration failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def update_status(
        self,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Aktualisiert den Status beim Dashboard.
        
        Args:
            status: Status-String ("online", "busy", "error", "offline")
            metadata: Zusätzliche Metadata
            
        Returns:
            Dict: Response vom Dashboard
        """
        endpoint = f"{self.dashboard_url}/api/agent/{self.agent_id}/status"
        
        payload = {
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }
        
        try:
            response = await self.client.post(endpoint, json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Status updated: {status}")
            return data
        
        except httpx.HTTPError as e:
            logger.error(f"Status update failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def publish_sse_event(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Published ein SSE-Event ans Dashboard (für UI-Updates).
        
        Args:
            event_type: Event-Typ (z.B. "command_executed", "agent_status_changed")
            data: Event-Daten
            
        Returns:
            Dict: Response vom Dashboard
        """
        endpoint = f"{self.dashboard_url}/api/sse/publish"
        
        payload = {
            "event_type": event_type,
            "data": data,
            "source": self.agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            response = await self.client.post(endpoint, json=payload)
            response.raise_for_status()
            
            data_response = response.json()
            logger.debug(f"SSE event published: {event_type}")
            return data_response
        
        except httpx.HTTPError as e:
            logger.error(f"SSE publish failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def forward_command(
        self,
        target_agent: str,
        command: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Forwarded einen Command an einen anderen Agent via Dashboard.
        
        Args:
            target_agent: Ziel-Agent-ID
            command: Command-Name
            params: Command-Parameter
            
        Returns:
            Dict: Response vom Ziel-Agent
        """
        endpoint = f"{self.dashboard_url}/api/command"
        
        payload = {
            "agent_id": target_agent,
            "command": command,
            "params": params,
            "source": self.agent_id
        }
        
        try:
            response = await self.client.post(endpoint, json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Command forwarded to {target_agent}: {command}")
            return data
        
        except httpx.HTTPError as e:
            logger.error(f"Command forward failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """
        Holt den Status eines anderen Agents vom Dashboard.
        
        Args:
            agent_id: Agent-ID
            
        Returns:
            Dict: Agent-Status
        """
        endpoint = f"{self.dashboard_url}/api/agent/{agent_id}/status"
        
        try:
            response = await self.client.get(endpoint)
            response.raise_for_status()
            
            data = response.json()
            return data
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to get agent status: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_all_agents(self) -> Dict[str, Any]:
        """
        Holt Liste aller registrierten Agents vom Dashboard.
        
        Returns:
            Dict: {"agents": [...]}
        """
        endpoint = f"{self.dashboard_url}/api/status/all"
        
        try:
            response = await self.client.get(endpoint)
            response.raise_for_status()
            
            data = response.json()
            return data
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to get all agents: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def close(self) -> None:
        """Schließt den HTTP-Client sauber."""
        await self.client.aclose()
        logger.info("AgentAPIClient closed")
    
    async def heartbeat_loop(self, interval_seconds: int = 30) -> None:
        """
        Sendet regelmäßig Heartbeats an Dashboard (Background-Task).
        
        Args:
            interval_seconds: Heartbeat-Interval
        """
        logger.info(f"Starting heartbeat loop (interval: {interval_seconds}s)")
        
        while True:
            try:
                await self.update_status("online", metadata={"heartbeat": True})
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                logger.info("Heartbeat loop cancelled")
                break
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
                await asyncio.sleep(interval_seconds)
