#!/usr/bin/env python3
"""
Shared SSE Client Module

Reusable SSE and Safepoint clients for all PORTIER 3.0 agents.
This module consolidates the duplicated sse_client.py files
across all agent directories into a single, maintainable implementation.

Usage:
    from src.pkg.shared.sse_client import create_sse_client, create_safepoint_client

    # Create SSE client for specific agent
    sse_client = create_sse_client(source_agent="opena4")

    # Create safepoint client for specific agent
    safepoint_client = create_safepoint_client(source_agent="opena7")
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


@dataclass
class SSEEvent:
    """SSE Event data structure."""

    event_type: str
    data: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    event_id: str | None = None


class SSEClient:
    """SSE Client for connecting to opena20 Dashboard."""

    def __init__(self, base_url: str | None = None, bearer_token: str | None = None, timeout: float = 30.0):
        """Initialize SSEClient.

        Args:
            base_url: Base URL for opena20. Defaults to env var OPENA20_URL.
            bearer_token: Bearer token for auth. Defaults to env var BEARER_TOKEN.
            timeout: Request timeout in seconds.
        """
        self.base_url = (base_url or os.getenv("OPENA20_URL", "http://127.0.0.1:12349")).rstrip("/")
        self.bearer_token = bearer_token or os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._running = False

    async def connect(self) -> None:
        """Establish connection to SSE endpoint."""
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        self._client = httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=self.timeout)
        self._running = True

    async def disconnect(self) -> None:
        """Close the SSE connection."""
        self._running = False
        if self._client:
            await self._client.aclose()
            self._client = None

    async def subscribe(
        self, endpoint: str = "/api/events/live", on_event: Callable[[dict[str, Any]], Awaitable[None]] | None = None
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Subscribe to SSE events.

        Args:
            endpoint: SSE endpoint path
            on_event: Optional async callback for each event

        Yields:
            Dict containing event data
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
        except Exception as e:
            logger.error(f"SSE Error: {e}")
            raise

    def _parse_event(self, event_str: str) -> dict[str, Any] | None:
        """Parse SSE event string into structured data.

        Args:
            event_str: Raw SSE event string

        Returns:
            Parsed event dictionary or None
        """
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
    """Client for Safepoint archiving via opena2."""

    def __init__(self, base_url: str | None = None, bearer_token: str | None = None, source_agent: str = "unknown"):
        """Initialize SafepointClient.

        Args:
            base_url: Base URL for opena2. Defaults to env var OPENA2_URL.
            bearer_token: Bearer token for auth. Defaults to env var BEARER_TOKEN.
            source_agent: Agent identifier (e.g., "opena4", "opena7")
        """
        self.base_url = (base_url or os.getenv("OPENA2_URL", "http://127.0.0.1:12345")).rstrip("/")
        self.bearer_token = bearer_token or os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")
        self.source_agent = source_agent
        self._client: httpx.AsyncClient | None = None

    async def connect(self) -> None:
        """Establish connection to opena2."""
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        self._client = httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=10.0)

    async def disconnect(self) -> None:
        """Close the connection."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def write_safepoint(
        self, category: str, destination: str, payload: dict[str, Any], request_id: str | None = None
    ) -> str | None:
        """Write a safepoint to opena2.

        Args:
            category: Safepoint category (CMD, RESP, etc.)
            destination: Destination agent identifier
            payload: Data to store
            request_id: Optional request ID (auto-generated if not provided)

        Returns:
            Request ID on success, None on failure
        """
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


# Factory functions for easy agent-specific client creation


def create_sse_client(
    source_agent: str | None = None, base_url: str | None = None, bearer_token: str | None = None
) -> SSEClient:
    """Create an SSE client instance.

    Args:
        source_agent: Agent identifier (not used for SSE, but kept for consistency)
        base_url: Override default OPENA20_URL
        bearer_token: Override default BEARER_TOKEN

    Returns:
        Configured SSEClient instance
    """
    return SSEClient(base_url=base_url, bearer_token=bearer_token)


def create_safepoint_client(
    source_agent: str, base_url: str | None = None, bearer_token: str | None = None
) -> SafepointClient:
    """Create a safepoint client instance for a specific agent.

    Args:
        source_agent: Agent identifier (e.g., "opena4", "opena7")
        base_url: Override default OPENA2_URL
        bearer_token: Override default BEARER_TOKEN

    Returns:
        Configured SafepointClient instance
    """
    return SafepointClient(base_url=base_url, bearer_token=bearer_token, source_agent=source_agent)


# Singleton instances (backward compatibility)
_sse_client: SSEClient | None = None
_safepoint_client: SafepointClient | None = None


def get_sse_client() -> SSEClient:
    """Get or create singleton SSE client.

    Returns:
        Global SSEClient instance
    """
    global _sse_client
    if _sse_client is None:
        _sse_client = SSEClient()
    return _sse_client


def get_safepoint_client(source_agent: str = "unknown") -> SafepointClient:
    """Get or create singleton safepoint client.

    Args:
        source_agent: Agent identifier

    Returns:
        Global SafepointClient instance
    """
    global _safepoint_client
    if _safepoint_client is None:
        _safepoint_client = SafepointClient(source_agent=source_agent)
    return _safepoint_client


__all__ = [
    "SSEEvent",
    "SSEClient",
    "SafepointClient",
    "create_sse_client",
    "create_safepoint_client",
    "get_sse_client",
    "get_safepoint_client",
]
