"""
Memory System - Zentrales Storage Interface für alle Agents.
Unterstützt: In-Memory, File-based, optional External DB.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import asyncio
from collections import defaultdict

logger = logging.getLogger("memory_system")


@dataclass
class MemoryEntry:
    """Ein Memory-Eintrag mit Metadata"""
    agent_id: str
    key: str
    value: Any
    timestamp: str
    expires_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MemorySystem:
    """
    Zentrales Memory-System für alle Agents.
    
    Features:
    - In-Memory Storage (schnell, flüchtig)
    - File-based Persistence (optional)
    - Agent-isolierte Namespaces
    - TTL-Support
    - Query-Capabilities
    """
    
    def __init__(
        self,
        persist_to_disk: bool = False,
        storage_path: Optional[Path] = None
    ):
        self.persist_to_disk = persist_to_disk
        self.storage_path = storage_path or Path("data/agent_memory")
        
        # In-Memory Store: {agent_id: {key: MemoryEntry}}
        self._memory: Dict[str, Dict[str, MemoryEntry]] = defaultdict(dict)
        
        # Lock für Thread-Safety
        self._lock = asyncio.Lock()
        
        if self.persist_to_disk:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Memory system initialized with persistence: {self.storage_path}")
        else:
            logger.info("Memory system initialized (in-memory only)")
    
    async def store(
        self,
        agent_id: str,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Speichert einen Wert im Memory.
        
        Args:
            agent_id: Agent-ID (Namespace)
            key: Memory-Key
            value: Zu speichernder Wert
            ttl_seconds: Time-to-Live in Sekunden (optional)
            metadata: Zusätzliche Metadata (optional)
        """
        async with self._lock:
            now = datetime.now(timezone.utc)
            expires_at = None
            if ttl_seconds:
                from datetime import timedelta
                expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
            
            entry = MemoryEntry(
                agent_id=agent_id,
                key=key,
                value=value,
                timestamp=now.isoformat(),
                expires_at=expires_at,
                metadata=metadata
            )
            
            self._memory[agent_id][key] = entry
            logger.debug(f"Stored memory: {agent_id}/{key}")
            
            if self.persist_to_disk:
                await self._persist_entry(entry)
    
    async def retrieve(
        self,
        agent_id: str,
        key: str,
        default: Any = None
    ) -> Optional[Any]:
        """
        Holt einen Wert aus dem Memory.
        
        Args:
            agent_id: Agent-ID (Namespace)
            key: Memory-Key
            default: Rückgabewert wenn nicht gefunden
            
        Returns:
            Gespeicherter Wert oder default
        """
        async with self._lock:
            if agent_id not in self._memory:
                return default
            
            entry = self._memory[agent_id].get(key)
            if not entry:
                return default
            
            # TTL-Check
            if entry.expires_at:
                now = datetime.now(timezone.utc)
                expires = datetime.fromisoformat(entry.expires_at)
                if now > expires:
                    # Expired, delete
                    del self._memory[agent_id][key]
                    logger.debug(f"Memory expired: {agent_id}/{key}")
                    return default
            
            return entry.value
    
    async def delete(self, agent_id: str, key: str) -> bool:
        """
        Löscht einen Memory-Eintrag.
        
        Args:
            agent_id: Agent-ID
            key: Memory-Key
            
        Returns:
            bool: True wenn gelöscht, False wenn nicht gefunden
        """
        async with self._lock:
            if agent_id in self._memory and key in self._memory[agent_id]:
                del self._memory[agent_id][key]
                logger.debug(f"Deleted memory: {agent_id}/{key}")
                
                if self.persist_to_disk:
                    await self._delete_persisted(agent_id, key)
                
                return True
            return False
    
    async def list_keys(self, agent_id: str) -> List[str]:
        """
        Listet alle Keys eines Agents.
        
        Args:
            agent_id: Agent-ID
            
        Returns:
            Liste von Keys
        """
        async with self._lock:
            if agent_id not in self._memory:
                return []
            return list(self._memory[agent_id].keys())
    
    async def clear_agent(self, agent_id: str) -> int:
        """
        Löscht alle Memory-Einträge eines Agents.
        
        Args:
            agent_id: Agent-ID
            
        Returns:
            int: Anzahl gelöschter Einträge
        """
        async with self._lock:
            if agent_id not in self._memory:
                return 0
            
            count = len(self._memory[agent_id])
            del self._memory[agent_id]
            logger.info(f"Cleared memory for agent {agent_id}: {count} entries")
            
            if self.persist_to_disk:
                agent_file = self.storage_path / f"{agent_id}.json"
                if agent_file.exists():
                    agent_file.unlink()
            
            return count
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Statistiken über Memory-Usage.
        
        Returns:
            Dict: {"total_agents": ..., "total_entries": ..., "agents": {...}}
        """
        async with self._lock:
            stats = {
                "total_agents": len(self._memory),
                "total_entries": sum(len(entries) for entries in self._memory.values()),
                "agents": {}
            }
            
            for agent_id, entries in self._memory.items():
                stats["agents"][agent_id] = {
                    "entries": len(entries),
                    "keys": list(entries.keys())[:10]  # Nur erste 10 Keys
                }
            
            return stats
    
    # --- Persistence Helpers ---
    
    async def _persist_entry(self, entry: MemoryEntry) -> None:
        """Persistiert einen Eintrag auf Disk (JSON)"""
        agent_file = self.storage_path / f"{entry.agent_id}.json"
        
        # Load existing
        data = {}
        if agent_file.exists():
            with open(agent_file, "r") as f:
                data = json.load(f)
        
        # Update
        data[entry.key] = {
            "value": entry.value,
            "timestamp": entry.timestamp,
            "expires_at": entry.expires_at,
            "metadata": entry.metadata
        }
        
        # Save
        with open(agent_file, "w") as f:
            json.dump(data, f, indent=2)
    
    async def _delete_persisted(self, agent_id: str, key: str) -> None:
        """Löscht einen persistierten Eintrag"""
        agent_file = self.storage_path / f"{agent_id}.json"
        if not agent_file.exists():
            return
        
        with open(agent_file, "r") as f:
            data = json.load(f)
        
        if key in data:
            del data[key]
            
            with open(agent_file, "w") as f:
                json.dump(data, f, indent=2)
    
    async def load_from_disk(self) -> int:
        """
        Lädt alle Memory-Einträge von Disk in Memory.
        
        Returns:
            int: Anzahl geladener Einträge
        """
        if not self.persist_to_disk:
            return 0
        
        count = 0
        async with self._lock:
            for agent_file in self.storage_path.glob("*.json"):
                agent_id = agent_file.stem
                
                with open(agent_file, "r") as f:
                    data = json.load(f)
                
                for key, entry_data in data.items():
                    entry = MemoryEntry(
                        agent_id=agent_id,
                        key=key,
                        value=entry_data["value"],
                        timestamp=entry_data["timestamp"],
                        expires_at=entry_data.get("expires_at"),
                        metadata=entry_data.get("metadata")
                    )
                    self._memory[agent_id][key] = entry
                    count += 1
        
        logger.info(f"Loaded {count} memory entries from disk")
        return count
