#!/usr/bin/env python3
"""
opena20 - Dashboard Agent
SSE Client & Bus Module

Port: 12349
Kürzel: dashp

Server-Sent Events für Real-Time Updates
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Set, AsyncGenerator, Callable, Awaitable
from dataclasses import dataclass, field

import httpx


logger = logging.getLogger(__name__)


# ==================== SSE Event Types ====================

@dataclass
class SSEEvent:
    """Server-Sent Event Struktur"""
    event_type: str
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_id: Optional[str] = None
    
    def to_sse_format(self) -> str:
        """Konvertiert zu SSE Wire Format"""
        lines = []
        if self.event_id:
            lines.append(f"id: {self.event_id}")
        lines.append(f"event: {self.event_type}")
        lines.append(f"data: {json.dumps(self.data, ensure_ascii=False)}")
        lines.append("")  # Leere Zeile als Event-Ende
        return "\n".join(lines) + "\n"


# ==================== SSE Connection Tracker ====================

@dataclass
class SSEConnection:
    """SSE Connection Info"""
    connection_id: str
    client_ip: str
    connected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    events_sent: int = 0
    last_event_at: Optional[str] = None


# ==================== SSE Bus (Server-Side) ====================

class SSEBus:
    """
    Server-Sent Events Bus für Real-Time Updates.
    
    Features:
    - Multiple Connections
    - Event Broadcasting
    - Connection Tracking
    - Keepalive
    - Event History Buffer
    """
    
    def __init__(
        self,
        max_connections: int = 100,
        keepalive_interval: int = 15,
        buffer_size: int = 1000
    ):
        self.max_connections = max_connections
        self.keepalive_interval = keepalive_interval
        self.buffer_size = buffer_size
        
        self._connections: Dict[str, SSEConnection] = {}
        self._queues: Dict[str, asyncio.Queue] = {}
        self._event_buffer: list = []
        self._running = False
        self._keepalive_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Startet den SSE Bus"""
        if self._running:
            return
        
        self._running = True
        self._keepalive_task = asyncio.create_task(self._keepalive_loop())
        logger.info("SSE Bus gestartet")
    
    async def stop(self) -> None:
        """Stoppt den SSE Bus"""
        self._running = False
        
        if self._keepalive_task:
            self._keepalive_task.cancel()
            try:
                await self._keepalive_task
            except asyncio.CancelledError:
                pass
        
        # Alle Queues leeren
        for queue in self._queues.values():
            while not queue.empty():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
        
        self._connections.clear()
        self._queues.clear()
        logger.info("SSE Bus gestoppt")
    
    def connect(self, client_ip: str) -> str:
        """
        Registriert neue SSE Connection.
        
        Returns:
            Connection ID
            
        Raises:
            ConnectionError: Wenn max_connections erreicht
        """
        if len(self._connections) >= self.max_connections:
            raise ConnectionError(f"Max SSE connections ({self.max_connections}) reached")
        
        connection_id = str(uuid.uuid4())[:8]
        
        self._connections[connection_id] = SSEConnection(
            connection_id=connection_id,
            client_ip=client_ip
        )
        self._queues[connection_id] = asyncio.Queue(maxsize=100)
        
        logger.info(f"SSE Connection {connection_id} von {client_ip}")
        return connection_id
    
    def disconnect(self, connection_id: str) -> None:
        """Entfernt SSE Connection"""
        if connection_id in self._connections:
            del self._connections[connection_id]
        if connection_id in self._queues:
            del self._queues[connection_id]
        logger.info(f"SSE Connection {connection_id} getrennt")
    
    async def publish(
        self,
        event_type: str,
        data: Dict[str, Any],
        event_id: Optional[str] = None
    ) -> int:
        """
        Veröffentlicht Event an alle Connections.
        
        Returns:
            Anzahl erreichter Connections
        """
        event = SSEEvent(
            event_type=event_type,
            data=data,
            event_id=event_id or str(uuid.uuid4())[:8]
        )
        
        # In Buffer speichern
        self._event_buffer.append(event)
        if len(self._event_buffer) > self.buffer_size:
            self._event_buffer = self._event_buffer[-self.buffer_size:]
        
        # An alle Queues senden
        sent_count = 0
        for conn_id, queue in list(self._queues.items()):
            try:
                queue.put_nowait(event)
                if conn_id in self._connections:
                    self._connections[conn_id].events_sent += 1
                    self._connections[conn_id].last_event_at = event.timestamp
                sent_count += 1
            except asyncio.QueueFull:
                logger.warning(f"Queue full für Connection {conn_id}")
        
        return sent_count
    
    async def subscribe(self, connection_id: str) -> AsyncGenerator[str, None]:
        """
        Async Generator für SSE Stream.
        
        Yields:
            SSE-formatierte Event Strings
        """
        if connection_id not in self._queues:
            return
        
        queue = self._queues[connection_id]
        
        try:
            while self._running and connection_id in self._connections:
                try:
                    event = await asyncio.wait_for(
                        queue.get(),
                        timeout=self.keepalive_interval + 5
                    )
                    yield event.to_sse_format()
                except asyncio.TimeoutError:
                    # Connection timeout - cleanup
                    break
        finally:
            self.disconnect(connection_id)
    
    async def _keepalive_loop(self) -> None:
        """Sendet regelmäßig Keepalive Events"""
        while self._running:
            try:
                await asyncio.sleep(self.keepalive_interval)
                await self.publish(
                    event_type="heartbeat",
                    data={
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "connections": len(self._connections)
                    }
                )
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Keepalive error: {e}")
    
    def get_connection_count(self) -> int:
        """Gibt Anzahl aktiver Connections zurück"""
        return len(self._connections)
    
    def get_connections(self) -> list:
        """Gibt Liste aller Connections zurück"""
        return [
            {
                "connection_id": conn.connection_id,
                "client_ip": conn.client_ip,
                "connected_at": conn.connected_at,
                "events_sent": conn.events_sent
            }
            for conn in self._connections.values()
        ]
    
    def get_recent_events(self, count: int = 10) -> list:
        """Gibt letzte Events aus Buffer zurück"""
        return [
            {
                "event_type": e.event_type,
                "timestamp": e.timestamp,
                "data": e.data
            }
            for e in self._event_buffer[-count:]
        ]


# ==================== SSE Client (für Dashboard → andere Agents) ====================

class SSEClient:
    """
    SSE Client für Verbindung zu anderen Agents.
    
    Verwendet für Dashboard → Agent SSE Subscriptions.
    """
    
    def __init__(
        self,
        base_url: str,
        bearer_token: Optional[str] = None,
        timeout: float = 30.0
    ):
        self.base_url = base_url.rstrip("/")
        self.bearer_token = bearer_token
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._running = False
    
    async def connect(self) -> None:
        """Initialisiert HTTP Client"""
        headers = {}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout
        )
        self._running = True
    
    async def disconnect(self) -> None:
        """Schließt HTTP Client"""
        self._running = False
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def subscribe(
        self,
        endpoint: str = "/sse/events",
        on_event: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Subscribes zu SSE Endpoint.
        
        Args:
            endpoint: SSE Endpoint Pfad
            on_event: Optionaler Callback für Events
            
        Yields:
            Parsed Event Dictionaries
        """
        if not self._client:
            await self.connect()
        
        try:
            async with self._client.stream("GET", endpoint) as response:
                response.raise_for_status()
                
                buffer = ""
                async for chunk in response.aiter_text():
                    buffer += chunk
                    
                    while "\n\n" in buffer:
                        event_str, buffer = buffer.split("\n\n", 1)
                        event = self._parse_event(event_str)
                        
                        if event:
                            if on_event:
                                await on_event(event)
                            yield event
                    
                    if not self._running:
                        break
                        
        except httpx.HTTPStatusError as e:
            logger.error(f"SSE HTTP Error: {e}")
            raise
        except Exception as e:
            logger.error(f"SSE Error: {e}")
            raise
    
    def _parse_event(self, event_str: str) -> Optional[Dict[str, Any]]:
        """Parst SSE Event String"""
        event_data: Dict[str, Any] = {}
        
        for line in event_str.strip().split("\n"):
            if line.startswith("event:"):
                event_data["event_type"] = line[6:].strip()
            elif line.startswith("data:"):
                try:
                    event_data["data"] = json.loads(line[5:].strip())
                except json.JSONDecodeError:
                    event_data["data"] = line[5:].strip()
            elif line.startswith("id:"):
                event_data["event_id"] = line[3:].strip()
        
        return event_data if event_data else None


# ==================== Dashboard Event Publisher ====================

class DashboardEventPublisher:
    """
    Spezialisierter Event Publisher für Dashboard.
    
    Veröffentlicht Events zu:
    - opena20 SSE Bus (lokal)
    - Optionally: opena2 für Archivierung
    """
    
    def __init__(self, sse_bus: SSEBus, opena2_url: Optional[str] = None):
        self.sse_bus = sse_bus
        self.opena2_url = opena2_url
        self._client: Optional[httpx.AsyncClient] = None
    
    async def start(self) -> None:
        """Startet Publisher"""
        if self.opena2_url:
            self._client = httpx.AsyncClient(
                base_url=self.opena2_url,
                timeout=10.0
            )
    
    async def stop(self) -> None:
        """Stoppt Publisher"""
        if self._client:
            await self._client.aclose()
    
    async def publish_agent_status(
        self,
        agent_id: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publiziert Agent Status Event"""
        await self.sse_bus.publish(
            event_type="agent_status",
            data={
                "agent_id": agent_id,
                "status": status,
                "details": details or {},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    async def publish_alert(
        self,
        severity: str,
        source: str,
        title: str,
        message: str
    ) -> None:
        """Publiziert Alert Event"""
        await self.sse_bus.publish(
            event_type="alert",
            data={
                "severity": severity,
                "source": source,
                "title": title,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    async def publish_metric(
        self,
        name: str,
        value: float,
        unit: str,
        source: str,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Publiziert Metrik Event"""
        await self.sse_bus.publish(
            event_type="metric",
            data={
                "name": name,
                "value": value,
                "unit": unit,
                "source": source,
                "tags": tags or {},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    async def publish_notification(
        self,
        title: str,
        message: str,
        category: str = "info"
    ) -> None:
        """Publiziert Notification Event"""
        await self.sse_bus.publish(
            event_type="notification",
            data={
                "title": title,
                "message": message,
                "category": category,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


# ==================== Singleton Instances ====================

# Global SSE Bus Instance
_sse_bus: Optional[SSEBus] = None


def get_sse_bus() -> SSEBus:
    """Gibt globale SSE Bus Instanz zurück"""
    global _sse_bus
    if _sse_bus is None:
        _sse_bus = SSEBus()
    return _sse_bus


# ==================== Export ====================

__all__ = [
    "SSEEvent",
    "SSEConnection",
    "SSEBus",
    "SSEClient",
    "DashboardEventPublisher",
    "get_sse_bus",
]
