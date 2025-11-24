"""
Agent Manager - Registry + Lifecycle Management aller internen Agents.
Zentrale Komponente des Mini-Orchestrators.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import asyncio

from .agent_base import AgentBase, AgentStatus, AgentCapability
from .memory_system import MemorySystem

logger = logging.getLogger("agent_manager")


class AgentManager:
    """
    Zentraler Manager für alle Agents im Mini-Orchestrator System.
    
    Verantwortlich für:
    - Agent-Registration
    - Lifecycle (initialize, shutdown)
    - Command-Routing an passende Agents
    - Health-Monitoring
    - Capability-Discovery
    """
    
    def __init__(self, memory_system: Optional[MemorySystem] = None):
        self.agents: Dict[str, AgentBase] = {}
        self.memory_system = memory_system or MemorySystem(persist_to_disk=True)
        self._lock = asyncio.Lock()
        logger.info("AgentManager initialized")
    
    async def register_agent(self, agent: AgentBase) -> None:
        """
        Registriert einen Agent und initialisiert ihn.
        
        Args:
            agent: AgentBase-Instanz
        """
        async with self._lock:
            if agent.agent_id in self.agents:
                logger.warning(f"Agent {agent.agent_id} already registered, skipping")
                return
            
            # Memory-System anhängen
            agent.memory = self.memory_system
            
            # Agent initialisieren
            await agent.initialize()
            
            # Registrieren
            self.agents[agent.agent_id] = agent
            logger.info(f"Agent registered: {agent.agent_id} (capabilities: {agent.capabilities})")
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Deregistriert einen Agent und fährt ihn herunter.
        
        Args:
            agent_id: Agent-ID
            
        Returns:
            bool: True wenn erfolgreich
        """
        async with self._lock:
            if agent_id not in self.agents:
                logger.warning(f"Agent {agent_id} not found")
                return False
            
            agent = self.agents[agent_id]
            await agent.shutdown()
            del self.agents[agent_id]
            logger.info(f"Agent unregistered: {agent_id}")
            return True
    
    async def execute_command(
        self,
        command: str,
        params: Dict[str, Any],
        agent_id: Optional[str] = None,
        capability: Optional[AgentCapability] = None
    ) -> Dict[str, Any]:
        """
        Führt einen Command aus (entweder an spezifischen Agent oder an ersten passenden).
        
        Args:
            command: Command-Name (z.B. "send_email")
            params: Command-Parameter
            agent_id: Explizite Agent-ID (optional)
            capability: Gewünschte Capability (optional, für Auto-Routing)
            
        Returns:
            Dict: {"status": "success|error", "data": {...}, "agent_id": ...}
        """
        # Option 1: Expliziter Agent
        if agent_id:
            if agent_id not in self.agents:
                return {
                    "status": "error",
                    "error": f"Agent {agent_id} not found",
                    "data": None
                }
            
            agent = self.agents[agent_id]
            try:
                result = await agent.execute(command, params)
                result["agent_id"] = agent_id
                return result
            except Exception as e:
                logger.error(f"Command execution failed on {agent_id}: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "data": None,
                    "agent_id": agent_id
                }
        
        # Option 2: Auto-Routing via Capability
        if capability:
            candidates = [
                a for a in self.agents.values()
                if a.supports_capability(capability) and a.status == AgentStatus.READY
            ]
            
            if not candidates:
                return {
                    "status": "error",
                    "error": f"No agent found with capability {capability.value}",
                    "data": None
                }
            
            # Ersten verfügbaren nutzen
            agent = candidates[0]
            try:
                result = await agent.execute(command, params)
                result["agent_id"] = agent.agent_id
                return result
            except Exception as e:
                logger.error(f"Command execution failed on {agent.agent_id}: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "data": None,
                    "agent_id": agent.agent_id
                }
        
        # Keine Routing-Info
        return {
            "status": "error",
            "error": "Must provide either agent_id or capability for routing",
            "data": None
        }
    
    async def get_all_status(self) -> List[Dict[str, Any]]:
        """
        Holt Status aller Agents.
        
        Returns:
            Liste von Agent-Status-Dicts
        """
        async with self._lock:
            return [agent.get_status() for agent in self.agents.values()]
    
    async def health_check_all(self) -> Dict[str, Any]:
        """
        Führt Health-Check für alle Agents durch.
        
        Returns:
            Dict: {"overall": "healthy|degraded|unhealthy", "agents": {...}}
        """
        results = {}
        unhealthy_count = 0
        degraded_count = 0
        
        for agent_id, agent in self.agents.items():
            try:
                health = await agent.health_check()
                results[agent_id] = health
                
                status = health.get("status", "unknown")
                if status == "unhealthy":
                    unhealthy_count += 1
                elif status == "degraded":
                    degraded_count += 1
            except Exception as e:
                logger.error(f"Health check failed for {agent_id}: {e}")
                results[agent_id] = {"status": "unhealthy", "error": str(e)}
                unhealthy_count += 1
        
        # Overall-Status bestimmen
        if unhealthy_count > 0:
            overall = "unhealthy"
        elif degraded_count > 0:
            overall = "degraded"
        else:
            overall = "healthy"
        
        return {
            "overall": overall,
            "agents": results,
            "summary": {
                "total": len(self.agents),
                "healthy": len(self.agents) - unhealthy_count - degraded_count,
                "degraded": degraded_count,
                "unhealthy": unhealthy_count
            }
        }
    
    async def find_agents_by_capability(self, capability: AgentCapability) -> List[str]:
        """
        Findet alle Agents mit einer bestimmten Capability.
        
        Args:
            capability: Gesuchte Capability
            
        Returns:
            Liste von Agent-IDs
        """
        return [
            agent_id for agent_id, agent in self.agents.items()
            if agent.supports_capability(capability)
        ]
    
    async def shutdown_all(self) -> None:
        """
        Fährt alle Agents sauber herunter.
        """
        logger.info("Shutting down all agents...")
        async with self._lock:
            for agent_id, agent in list(self.agents.items()):
                try:
                    await agent.shutdown()
                    logger.info(f"Agent {agent_id} shut down")
                except Exception as e:
                    logger.error(f"Error shutting down {agent_id}: {e}")
            
            self.agents.clear()
        logger.info("All agents shut down")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Statistiken über den AgentManager.
        
        Returns:
            Dict: {"total_agents": ..., "by_status": {...}, "by_capability": {...}}
        """
        by_status: Dict[str, int] = {}
        by_capability: Dict[str, int] = {}
        
        for agent in self.agents.values():
            # Status
            status_key = agent.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1
            
            # Capabilities
            for cap in agent.capabilities:
                cap_key = cap.value
                by_capability[cap_key] = by_capability.get(cap_key, 0) + 1
        
        return {
            "total_agents": len(self.agents),
            "by_status": by_status,
            "by_capability": by_capability,
            "agent_ids": list(self.agents.keys())
        }
