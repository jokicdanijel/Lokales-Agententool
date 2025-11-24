"""
Agents Package - Mini-Orchestrator Internal Agents System

Exports:
- AgentBase: Basisklasse für alle Agents
- AgentManager: Registry + Lifecycle Management
- MemorySystem: Zentrales Storage
- AgentAPIClient: Dashboard-Kommunikation
- AgentStatus, AgentCapability: Enums
"""

from .agent_base import AgentBase, AgentStatus, AgentCapability
from .agent_manager import AgentManager
from .memory_system import MemorySystem, MemoryEntry
from .agent_api import AgentAPIClient

__all__ = [
    "AgentBase",
    "AgentStatus",
    "AgentCapability",
    "AgentManager",
    "MemorySystem",
    "MemoryEntry",
    "AgentAPIClient",
]
