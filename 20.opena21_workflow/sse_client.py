#!/usr/bin/env python3
"""
opena21 - Workflow Engine Agent
SSE Client Module

Port: 12364
Kürzel: workflowp

SSE Integration für Real-Time Workflow-Updates
"""

import json
import logging
from collections.abc import AsyncGenerator, Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)


# ==================== SSE Event Types ====================


@dataclass
class WorkflowSSEEvent:
    """Workflow SSE Event Struktur"""

    event_type: str
    workflow_id: str
    data: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    event_id: str | None = None

    def to_sse_format(self) -> str:
        """Konvertiert zu SSE Wire Format"""
        payload = {"workflow_id": self.workflow_id, "timestamp": self.timestamp, **self.data}
        lines = []
        if self.event_id:
            lines.append(f"id: {self.event_id}")
        lines.append(f"event: {self.event_type}")
        lines.append(f"data: {json.dumps(payload, ensure_ascii=False)}")
        lines.append("")
        return "\n".join(lines) + "\n"


# ==================== Workflow Event Publisher ====================


class WorkflowEventPublisher:
    """
    Publiziert Workflow-Events an opena20 Dashboard.

    Event-Typen:
    - workflow_started
    - workflow_completed
    - workflow_failed
    - workflow_cancelled
    - step_started
    - step_completed
    - step_failed
    """

    def __init__(self, dashboard_url: str = "http://127.0.0.1:12349", bearer_token: str | None = None):
        self.dashboard_url = dashboard_url.rstrip("/")
        self.bearer_token = bearer_token
        self._client: httpx.AsyncClient | None = None
        self._connected = False

    async def connect(self) -> None:
        """Initialisiert HTTP Client"""
        headers = {"Content-Type": "application/json"}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        self._client = httpx.AsyncClient(base_url=self.dashboard_url, headers=headers, timeout=10.0)
        self._connected = True
        logger.info(f"WorkflowEventPublisher verbunden mit {self.dashboard_url}")

    async def disconnect(self) -> None:
        """Schließt HTTP Client"""
        self._connected = False
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _publish_to_dashboard(self, event: WorkflowSSEEvent) -> bool:
        """Sendet Event an Dashboard"""
        if not self._client:
            await self.connect()

        try:
            response = await self._client.post(
                "/api/events/publish",
                json={
                    "event_type": event.event_type,
                    "source": "workflowp",
                    "data": {"workflow_id": event.workflow_id, **event.data},
                },
            )
            return response.status_code in (200, 201, 202)
        except Exception as e:
            logger.warning(f"Dashboard publish failed: {e}")
            return False

    async def workflow_started(self, workflow_id: str, workflow_name: str, inputs: dict[str, Any]) -> None:
        """Publiziert Workflow-Start Event"""
        event = WorkflowSSEEvent(
            event_type="workflow_started",
            workflow_id=workflow_id,
            data={"workflow_name": workflow_name, "inputs": inputs, "state": "running"},
        )
        await self._publish_to_dashboard(event)

    async def workflow_completed(
        self, workflow_id: str, workflow_name: str, outputs: dict[str, Any], duration_ms: int
    ) -> None:
        """Publiziert Workflow-Completion Event"""
        event = WorkflowSSEEvent(
            event_type="workflow_completed",
            workflow_id=workflow_id,
            data={"workflow_name": workflow_name, "outputs": outputs, "duration_ms": duration_ms, "state": "completed"},
        )
        await self._publish_to_dashboard(event)

    async def workflow_failed(
        self, workflow_id: str, workflow_name: str, error: str, failed_step: str | None = None
    ) -> None:
        """Publiziert Workflow-Failure Event"""
        event = WorkflowSSEEvent(
            event_type="workflow_failed",
            workflow_id=workflow_id,
            data={"workflow_name": workflow_name, "error": error, "failed_step": failed_step, "state": "failed"},
        )
        await self._publish_to_dashboard(event)

    async def workflow_cancelled(self, workflow_id: str, workflow_name: str, reason: str = "User requested") -> None:
        """Publiziert Workflow-Cancellation Event"""
        event = WorkflowSSEEvent(
            event_type="workflow_cancelled",
            workflow_id=workflow_id,
            data={"workflow_name": workflow_name, "reason": reason, "state": "cancelled"},
        )
        await self._publish_to_dashboard(event)

    async def step_started(self, workflow_id: str, step_name: str, step_index: int, total_steps: int) -> None:
        """Publiziert Step-Start Event"""
        event = WorkflowSSEEvent(
            event_type="step_started",
            workflow_id=workflow_id,
            data={
                "step_name": step_name,
                "step_index": step_index,
                "total_steps": total_steps,
                "progress": (step_index / total_steps) * 100,
            },
        )
        await self._publish_to_dashboard(event)

    async def step_completed(
        self,
        workflow_id: str,
        step_name: str,
        step_index: int,
        total_steps: int,
        output: dict[str, Any] | None = None,
        duration_ms: int = 0,
    ) -> None:
        """Publiziert Step-Completion Event"""
        event = WorkflowSSEEvent(
            event_type="step_completed",
            workflow_id=workflow_id,
            data={
                "step_name": step_name,
                "step_index": step_index,
                "total_steps": total_steps,
                "progress": ((step_index + 1) / total_steps) * 100,
                "output": output,
                "duration_ms": duration_ms,
            },
        )
        await self._publish_to_dashboard(event)

    async def step_failed(self, workflow_id: str, step_name: str, error: str, retry_count: int = 0) -> None:
        """Publiziert Step-Failure Event"""
        event = WorkflowSSEEvent(
            event_type="step_failed",
            workflow_id=workflow_id,
            data={"step_name": step_name, "error": error, "retry_count": retry_count},
        )
        await self._publish_to_dashboard(event)


# ==================== SSE Client für Agent-Subscriptions ====================


class SSEClient:
    """
    SSE Client für Subscription zu anderen Agents.

    Verwendet z.B. für:
    - Dashboard Status Updates
    - Agent Health Events
    """

    def __init__(self, base_url: str, bearer_token: str | None = None, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.bearer_token = bearer_token
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._running = False

    async def connect(self) -> None:
        """Initialisiert HTTP Client"""
        headers = {}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        self._client = httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=self.timeout)
        self._running = True

    async def disconnect(self) -> None:
        """Schließt HTTP Client"""
        self._running = False
        if self._client:
            await self._client.aclose()
            self._client = None

    async def subscribe(
        self, endpoint: str = "/sse/events", on_event: Callable[[dict[str, Any]], Awaitable[None]] | None = None
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Subscribes zu SSE Endpoint.

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

    def _parse_event(self, event_str: str) -> dict[str, Any] | None:
        """Parst SSE Event String"""
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


# ==================== Safepoint SSE Publisher ====================


class SafepointEventPublisher:
    """
    Publiziert Safepoint-Events für Archivierung.

    Sendet Events an opena2 für persistente Speicherung.
    """

    def __init__(self, opena2_url: str = "http://127.0.0.1:12345", bearer_token: str | None = None):
        self.opena2_url = opena2_url.rstrip("/")
        self.bearer_token = bearer_token
        self._client: httpx.AsyncClient | None = None

    async def connect(self) -> None:
        """Initialisiert HTTP Client"""
        headers = {"Content-Type": "application/json"}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        self._client = httpx.AsyncClient(base_url=self.opena2_url, headers=headers, timeout=10.0)

    async def disconnect(self) -> None:
        """Schließt HTTP Client"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def publish_safepoint(
        self,
        source: str,
        destination: str,
        category: str,
        payload: dict[str, Any],
        workflow_id: str | None = None,
        step_name: str | None = None,
    ) -> bool:
        """
        Publiziert Safepoint an opena2.

        Returns:
            True wenn erfolgreich
        """
        if not self._client:
            await self.connect()

        try:
            safepoint = {
                "sp_id": f"SP{int(datetime.now().timestamp() * 1000)}_{source}→{destination}_{category}",
                "timestamp": datetime.now(UTC).isoformat(),
                "source": source,
                "destination": destination,
                "kind": category,
                "payload": payload,
                "workflow_id": workflow_id,
                "step_name": step_name,
            }

            response = await self._client.post("/store/archivp", json=safepoint)
            return response.status_code in (200, 201)
        except Exception as e:
            logger.warning(f"Safepoint publish failed: {e}")
            return False


# ==================== Singleton Instances ====================

_event_publisher: WorkflowEventPublisher | None = None


def get_event_publisher(
    dashboard_url: str = "http://127.0.0.1:12349", bearer_token: str | None = None
) -> WorkflowEventPublisher:
    """Gibt globale Event Publisher Instanz zurück"""
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = WorkflowEventPublisher(dashboard_url, bearer_token)
    return _event_publisher


# ==================== Export ====================

__all__ = [
    "WorkflowSSEEvent",
    "WorkflowEventPublisher",
    "SSEClient",
    "SafepointEventPublisher",
    "get_event_publisher",
]
