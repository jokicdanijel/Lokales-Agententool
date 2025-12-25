"""
Agents Package - Mini-Orchestrator Internal Agents System

Exports:
- AgentBase: Basisklasse für alle Agents
- AgentManager: Registry + Lifecycle Management
- MemorySystem: Zentrales Storage
- AgentAPIClient: Dashboard-Kommunikation
- AgentStatus, AgentCapability: Enums
"""

from .agent_api import AgentAPIClient
from .agent_base import AgentBase, AgentCapability, AgentStatus
from .agent_manager import AgentManager
from .memory_system import MemoryEntry, MemorySystem

__all__ = [
    "AgentBase",
    "AgentStatus",
    "AgentCapability",
    "AgentManager",
    "MemorySystem",
    "MemoryEntry",
    "AgentAPIClient",
]
