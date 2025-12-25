#!/usr/bin/env python3
"""
opena11 - SSE Client Module

Port: 12357
Kürzel: unlockp

SSE Client für opena20 Dashboard Events
Safepoint Client für opena2 Archivierung
"""

import json
import logging
import os
import time
import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)

OPENA20_URL = os.getenv("OPENA20_URL", "http://127.0.0.1:12349")
OPENA2_URL = os.getenv("OPENA2_URL", "http://127.0.0.1:12345")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")


@dataclass
class SSEEvent:
    event_type: str
    data: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    event_id: str | None = None


class SSEClient:
    """SSE Client für Verbindung zu opena20 Dashboard"""

    def __init__(self, base_url: str = OPENA20_URL, bearer_token: str = BEARER_TOKEN, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.bearer_token = bearer_token
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._running = False

    async def connect(self) -> None:
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        self._client = httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=self.timeout)
        self._running = True

    async def disconnect(self) -> None:
        self._running = False
        if self._client:
            await self._client.aclose()
            self._client = None

    async def subscribe(
        self, endpoint: str = "/api/events/live", on_event: Callable[[dict[str, Any]], Awaitable[None]] | None = None
    ) -> AsyncGenerator[dict[str, Any], None]:
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
        except Exception as e:
            logger.error(f"SSE Error: {e}")
            raise

    def _parse_event(self, event_str: str) -> dict[str, Any] | None:
        event_data: dict[str, Any] = {}
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


class SafepointClient:
    """Client für Safepoint-Archivierung via opena2"""

    def __init__(self, base_url: str = OPENA2_URL, bearer_token: str = BEARER_TOKEN, source_agent: str = "opena11"):
        self.base_url = base_url.rstrip("/")
        self.bearer_token = bearer_token
        self.source_agent = source_agent
        self._client: httpx.AsyncClient | None = None

    async def connect(self) -> None:
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        self._client = httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=10.0)

    async def disconnect(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def write_safepoint(
        self, category: str, destination: str, payload: dict[str, Any], request_id: str | None = None
    ) -> str | None:
        if not self._client:
            await self.connect()

        safepoint = {
            "sp_timestamp": int(time.time() * 1000),
            "timestamp": datetime.now(UTC).isoformat(),
            "source": self.source_agent,
            "destination": destination,
            "category": category,
            "request_id": request_id or str(uuid.uuid4())[:8],
            "payload": payload,
            "strict": True,
        }

        try:
            response = await self._client.post("/api/safepoint", json=safepoint)
            response.raise_for_status()
            return safepoint["request_id"]
        except Exception as e:
            logger.error(f"Safepoint write failed: {e}")
            return None


_sse_client: SSEClient | None = None
_safepoint_client: SafepointClient | None = None


def get_sse_client() -> SSEClient:
    global _sse_client
    if _sse_client is None:
        _sse_client = SSEClient()
    return _sse_client


def get_safepoint_client() -> SafepointClient:
    global _safepoint_client
    if _safepoint_client is None:
        _safepoint_client = SafepointClient()
    return _safepoint_client


__all__ = ["SSEEvent", "SSEClient", "SafepointClient", "get_sse_client", "get_safepoint_client"]
