"""
Agent Base Class - Basisklasse für alle internen Agents im Mini-Orchestrator.
Definiert Standard-Interface für Memory, Execution, Health.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger("agent_base")


class AgentStatus(str, Enum):
    """Agent-Status für Lifecycle-Management"""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class AgentCapability(str, Enum):
    """Capabilities die ein Agent anbieten kann"""
    EMAIL = "email"
    BROWSER = "browser"
    WORKFLOW = "workflow"
    FILE_SYSTEM = "filesystem"
    API_CALL = "api_call"
    DATA_PROCESSING = "data_processing"
    MEMORY = "memory"


class AgentBase(ABC):
    """
    Basisklasse für alle Agents im Mini-Orchestrator System.
    
    Jeder Agent:
    - hat eindeutige agent_id
    - bietet Capabilities
    - kann Commands ausführen
    - hat Health-Status
    - nutzt zentrales Memory-System
    """
    
    def __init__(
        self,
        agent_id: str,
        capabilities: List[AgentCapability],
        memory_system: Optional[Any] = None
    ):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.memory = memory_system
        self.status = AgentStatus.INITIALIZING
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
        logger.info(f"Agent {agent_id} initialized with capabilities: {capabilities}")
    
    @abstractmethod
    async def execute(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt einen Command aus.
        
        Args:
            command: Command-Name (z.B. "send_email", "browse_url")
            params: Command-Parameter
            
        Returns:
            Dict mit Result: {"status": "success", "data": {...}, "error": None}
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Health-Check des Agents.
        
        Returns:
            Dict: {"status": "healthy|degraded|unhealthy", "details": {...}}
        """
        pass
    
    async def initialize(self) -> None:
        """
        Initialisierung des Agents (Verbindungen, Configs, etc.).
        Wird vom AgentManager aufgerufen.
        """
        logger.info(f"Agent {self.agent_id} initializing...")
        self.status = AgentStatus.READY
        logger.info(f"Agent {self.agent_id} ready")
    
    async def shutdown(self) -> None:
        """
        Sauberes Herunterfahren (Verbindungen schließen, Cleanup).
        Wird vom AgentManager aufgerufen.
        """
        logger.info(f"Agent {self.agent_id} shutting down...")
        self.status = AgentStatus.OFFLINE
        logger.info(f"Agent {self.agent_id} offline")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Aktueller Status + Metadata.
        
        Returns:
            Dict: {"agent_id": ..., "status": ..., "capabilities": [...], "metadata": {...}}
        """
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "capabilities": [c.value for c in self.capabilities],
            "metadata": self.metadata
        }
    
    async def store_memory(self, key: str, value: Any) -> None:
        """
        Speichert Daten im Memory-System.
        
        Args:
            key: Memory-Key
            value: Zu speichernder Wert
        """
        if self.memory:
            await self.memory.store(self.agent_id, key, value)
        else:
            logger.warning(f"Agent {self.agent_id} has no memory system attached")
    
    async def retrieve_memory(self, key: str) -> Optional[Any]:
        """
        Holt Daten aus dem Memory-System.
        
        Args:
            key: Memory-Key
            
        Returns:
            Gespeicherter Wert oder None
        """
        if self.memory:
            return await self.memory.retrieve(self.agent_id, key)
        else:
            logger.warning(f"Agent {self.agent_id} has no memory system attached")
            return None
    
    def supports_capability(self, capability: AgentCapability) -> bool:
        """
        Prüft ob Agent eine Capability unterstützt.
        
        Args:
            capability: Zu prüfende Capability
            
        Returns:
            bool: True wenn unterstützt
        """
        return capability in self.capabilities
