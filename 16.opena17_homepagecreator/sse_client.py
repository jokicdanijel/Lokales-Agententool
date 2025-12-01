#!/usr/bin/env python3
"""
opena17 - Homepage Creator Agent
SSE Client Module - PORTIER 3.0 Compliant

Server-Sent Events Client für Dashboard Integration
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Callable, Awaitable

import aiohttp

# Logging
logger = logging.getLogger("opena17.sse_client")


class SSEClient:
    """SSE-Client für Dashboard-Integration (opena20)"""
    
    def __init__(
        self,
        dashboard_url: str = "http://127.0.0.1:12349",
        bearer_token: Optional[str] = None,
        agent_id: str = "opena17",
        kuerzel: str = "hpcreatep"
    ):
        self.dashboard_url = dashboard_url.rstrip("/")
        self.bearer_token = bearer_token or os.getenv("BEARER_TOKEN", "")
        self.agent_id = agent_id
        self.kuerzel = kuerzel
        self._session: Optional[aiohttp.ClientSession] = None
        self._connected = False
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Lazy Session-Initialisierung"""
        if self._session is None or self._session.closed:
            headers = {}
            if self.bearer_token:
                headers["Authorization"] = f"Bearer {self.bearer_token}"
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session
    
    async def close(self) -> None:
        """Schließt Session"""
        if self._session and not self._session.closed:
            await self._session.close()
        self._connected = False
    
    async def publish_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        category: str = "agent"
    ) -> bool:
        """
        Publiziert Event an Dashboard SSE-Bus.
        
        Args:
            event_type: Event-Typ (z.B. "site_generated", "export_complete")
            data: Event-Daten
            category: Event-Kategorie
        
        Returns:
            True wenn erfolgreich, False sonst
        """
        try:
            session = await self._get_session()
            
            payload = {
                "event_type": event_type,
                "category": category,
                "agent": self.agent_id,
                "kuerzel": self.kuerzel,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": data
            }
            
            url = f"{self.dashboard_url}/api/events/publish"
            
            async with session.post(url, json=payload, timeout=5) as response:
                if response.status == 200:
                    logger.info(f"SSE Event published: {event_type}")
                    return True
                else:
                    logger.warning(f"SSE Event publish failed: HTTP {response.status}")
                    return False
        
        except asyncio.TimeoutError:
            logger.warning("SSE Event publish timeout")
            return False
        except aiohttp.ClientError as e:
            logger.warning(f"SSE Event publish error: {e}")
            return False
        except Exception as e:
            logger.error(f"SSE Event publish unexpected error: {e}")
            return False
    
    async def publish_site_generated(
        self,
        site_id: str,
        site_name: str,
        pages_count: int,
        generator: str
    ) -> bool:
        """Publiziert Site-Generated Event"""
        return await self.publish_event(
            event_type="site_generated",
            data={
                "site_id": site_id,
                "site_name": site_name,
                "pages_count": pages_count,
                "generator": generator
            },
            category="homepage_creator"
        )
    
    async def publish_site_exported(
        self,
        site_id: str,
        format: str,
        file_size_bytes: int
    ) -> bool:
        """Publiziert Site-Exported Event"""
        return await self.publish_event(
            event_type="site_exported",
            data={
                "site_id": site_id,
                "format": format,
                "file_size_bytes": file_size_bytes
            },
            category="homepage_creator"
        )
    
    async def publish_site_deployed(
        self,
        site_id: str,
        target: str,
        deployment_url: Optional[str]
    ) -> bool:
        """Publiziert Site-Deployed Event"""
        return await self.publish_event(
            event_type="site_deployed",
            data={
                "site_id": site_id,
                "target": target,
                "deployment_url": deployment_url
            },
            category="homepage_creator"
        )
    
    async def publish_health_status(
        self,
        status: str,
        uptime_seconds: float,
        total_sites: int
    ) -> bool:
        """Publiziert Health-Status Event"""
        return await self.publish_event(
            event_type="health_status",
            data={
                "status": status,
                "uptime_seconds": uptime_seconds,
                "total_sites": total_sites
            },
            category="health"
        )
    
    async def publish_error(
        self,
        error_code: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Publiziert Error Event"""
        return await self.publish_event(
            event_type="error",
            data={
                "code": error_code,
                "message": error_message,
                "details": details or {}
            },
            category="error"
        )


class SSEEventEmitter:
    """Event-Emitter für lokale SSE-Streams"""
    
    def __init__(self):
        self._subscribers: Dict[str, list] = {}
        self._lock = asyncio.Lock()
    
    async def subscribe(self, channel: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Registriert Subscriber für Channel"""
        async with self._lock:
            if channel not in self._subscribers:
                self._subscribers[channel] = []
            self._subscribers[channel].append(callback)
    
    async def unsubscribe(self, channel: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Entfernt Subscriber von Channel"""
        async with self._lock:
            if channel in self._subscribers and callback in self._subscribers[channel]:
                self._subscribers[channel].remove(callback)
    
    async def emit(self, channel: str, data: Dict[str, Any]):
        """Emittiert Event an alle Subscriber"""
        async with self._lock:
            subscribers = self._subscribers.get(channel, []).copy()
        
        for callback in subscribers:
            try:
                await callback(data)
            except Exception as e:
                logger.error(f"SSE emit error: {e}")


# Singleton Instanzen
sse_client = SSEClient()
event_emitter = SSEEventEmitter()
