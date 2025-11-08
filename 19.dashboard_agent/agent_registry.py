#!/usr/bin/env python3
"""
AgentRegistry – verwaltet registrierte Agenten (ID -> Endpoint + Status).
"""

from __future__ import annotations
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

import httpx
import logging

logger = logging.getLogger("agent_registry")

class AgentRegistry:
    def __init__(self) -> None:
        # agent_id -> dict(endpoint, registered_at, last_health, meta)
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def register(self, agent_id: str, endpoint: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        async with self._lock:
            now = datetime.utcnow().isoformat() + "Z"
            self._agents[agent_id] = {
                "endpoint": endpoint.rstrip("/"),
                "registered_at": now,
                "last_health": None,
                "meta": meta or {},
            }
            logger.info(f"Agent registriert: {agent_id} -> {endpoint}")
            return {"agent": agent_id, "endpoint": endpoint, "registered_at": now, "strict": True}

    async def exists(self, agent_id: str) -> bool:
        async with self._lock:
            return agent_id in self._agents

    async def get_agent_details(self, agent_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            return self._agents.get(agent_id)

    async def get_all_status(self) -> Dict[str, Any]:
        async with self._lock:
            return {k: {"endpoint": v["endpoint"], "registered_at": v["registered_at"], "last_health": v["last_health"]} for k, v in self._agents.items()}

    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            a = self._agents.get(agent_id)
        if not a:
            return None
        # Live-Health vom Agent holen (optional)
        try:
            async with httpx.AsyncClient(timeout=3.0) as cli:
                r = await cli.get(f'{a["endpoint"]}/health')
                r.raise_for_status()
                data = r.json()
            status = {"ok": True, "data": data}
        except Exception as e:
            status = {"ok": False, "error": str(e)}
        async with self._lock:
            self._agents[agent_id]["last_health"] = status
        return status

    async def execute_command(self, agent_id: str, command: Dict[str, Any]) -> Dict[str, Any]:
        async with self._lock:
            a = self._agents.get(agent_id)
        if not a:
            raise RuntimeError(f"Agent {agent_id} nicht registriert")

        # Generischer Dispatch: POST {endpoint}/command
        payload = {"strict": True, "command": command}
        async with httpx.AsyncClient(timeout=10.0) as cli:
            r = await cli.post(f'{a["endpoint"]}/command', json=payload)
            r.raise_for_status()
            return {"strict": True, "reply": r.json()}

    async def register_if_absent(self, agent_id: str, endpoint: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Registriert einen Agenten nur, wenn er noch nicht existiert"""
        async with self._lock:
            if agent_id in self._agents:
                return {"agent": agent_id, "already_registered": True}
        return await self.register(agent_id, endpoint, meta)

    async def list_agents(self) -> Dict[str, Any]:
        """Gibt kompakte Agentenliste zurück (ohne Health-Abfrage)"""
        async with self._lock:
            return {
                k: {
                    "endpoint": v["endpoint"],
                    "registered_at": v["registered_at"]
                }
                for k, v in self._agents.items()
            }

    async def persist(self, path: str) -> None:
        """Persistiert Agenten-Registry in JSON-Datei"""
        import json
        from pathlib import Path
        async with self._lock:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(self._agents, indent=2))
            logger.info(f"Registry persistiert: {path}")

    async def load(self, path: str) -> None:
        """Lädt Agenten-Registry aus JSON-Datei"""
        import json
        from pathlib import Path
        p = Path(path)
        if not p.exists():
            logger.info(f"Registry-Datei nicht vorhanden: {path}")
            return
        async with self._lock:
            self._agents = json.loads(p.read_text())
            logger.info(f"Registry geladen: {path}")


