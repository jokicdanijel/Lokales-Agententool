#!/usr/bin/env python3
"""
opena20 - Dashboard Agent
Pydantic Models

Port: 12349
Kürzel: dashp

PORTIER 3.0 Strict JSON Schemas
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ==================== Enums ====================


class AgentStatus(str, Enum):
    """Agent Status Codes"""

    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPING = "stopping"


class EventType(str, Enum):
    """SSE Event Types"""

    AGENT_STATUS = "agent_status"
    SAFEPOINT = "safepoint"
    ALERT = "alert"
    METRIC = "metric"
    NOTIFICATION = "notification"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


class AlertSeverity(str, Enum):
    """Alert Severity Levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SafepointCategory(str, Enum):
    """Safepoint Kategorien nach PORTIER 3.0"""

    CMD = "CMD"
    RESP = "RESP"
    ROUTE = "ROUTE"
    DISPATCH = "DISPATCH"


# ==================== Health & Status Models ====================


class HealthResponse(BaseModel):
    """Health Check Response - PORTIER 3.0 Standard"""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="Status (ok/error)")
    service: str = Field(..., description="Service-Name")
    kuerzel: str = Field(..., description="PORTIER Kürzel")
    port: int = Field(..., description="Port-Nummer")
    uptime_seconds: float = Field(..., description="Uptime in Sekunden")
    version: str = Field(..., description="Version")

    # Dashboard-spezifisch
    agents_total: int = Field(0, description="Gesamtzahl registrierter Agents")
    agents_online: int = Field(0, description="Anzahl online Agents")
    agents_offline: int = Field(0, description="Anzahl offline Agents")
    sse_connections: int = Field(0, description="Aktive SSE-Verbindungen")

    # Connectivity
    opena1_connected: bool = Field(False, description="Verbindung zu opena1")
    opena2_connected: bool = Field(False, description="Verbindung zu opena2")

    strict: bool = Field(True, description="Strict JSON Mode")


class AgentHealthResponse(BaseModel):
    """Einzelner Agent Health Status"""

    model_config = ConfigDict(extra="forbid")

    agent_id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent Name")
    kuerzel: str = Field(..., description="PORTIER Kürzel")
    port: int = Field(..., description="Port")
    status: AgentStatus = Field(..., description="Status")
    response_time_ms: float | None = Field(None, description="Antwortzeit in ms")
    last_check: str = Field(..., description="Letzter Check (ISO 8601)")
    error: str | None = Field(None, description="Fehlermeldung")
    version: str | None = Field(None, description="Agent-Version")


class AllAgentsStatusResponse(BaseModel):
    """Status aller Agents"""

    model_config = ConfigDict(extra="forbid")

    timestamp: str = Field(..., description="Abfrage-Zeitpunkt (ISO 8601)")
    total: int = Field(..., description="Gesamtzahl Agents")
    online: int = Field(..., description="Online Agents")
    offline: int = Field(..., description="Offline Agents")
    degraded: int = Field(0, description="Degraded Agents")
    agents: list[AgentHealthResponse] = Field(..., description="Agent-Details")


# ==================== SSE Models ====================


class SSEEvent(BaseModel):
    """Server-Sent Event Struktur"""

    model_config = ConfigDict(extra="forbid")

    event_type: EventType = Field(..., description="Event-Typ")
    timestamp: str = Field(..., description="Timestamp (ISO 8601)")
    source: str = Field(..., description="Quell-Agent")
    data: dict[str, Any] = Field(..., description="Event-Daten")
    event_id: str | None = Field(None, description="Optionale Event-ID")


class SSEConnectionInfo(BaseModel):
    """SSE Connection Info"""

    model_config = ConfigDict(extra="forbid")

    connection_id: str = Field(..., description="Connection ID")
    client_ip: str = Field(..., description="Client IP")
    connected_at: str = Field(..., description="Verbindungszeitpunkt")
    events_sent: int = Field(0, description="Gesendete Events")


# ==================== Safepoint Models ====================


class SafepointRecord(BaseModel):
    """Safepoint Record nach PORTIER 3.0"""

    model_config = ConfigDict(extra="forbid")

    sp_timestamp: int = Field(..., description="Unix Timestamp")
    timestamp: str = Field(..., description="ISO 8601 Timestamp")
    source: str = Field(..., description="Quell-Agent")
    destination: str = Field(..., description="Ziel-Agent")
    category: SafepointCategory = Field(..., description="Kategorie")
    request_id: str = Field(..., description="Request ID")
    payload: dict[str, Any] = Field(..., description="Payload (maskiert)")
    strict: bool = Field(True, description="Strict Mode Flag")


class SafepointIndexEntry(BaseModel):
    """Safepoint Index Eintrag"""

    model_config = ConfigDict(extra="forbid")

    file: str = Field(..., description="Relativer Dateipfad")
    ts: str = Field(..., description="Timestamp")
    category: SafepointCategory = Field(..., description="Kategorie")
    source: str = Field(..., description="Quelle")
    destination: str = Field(..., description="Ziel")
    request_id: str = Field(..., description="Request ID")


# ==================== Dashboard API Models ====================


class CommandRequest(BaseModel):
    """Generic Command Request"""

    model_config = ConfigDict(extra="forbid")

    action: str = Field(..., description="Aktion")
    target: str | None = Field(None, description="Ziel-Agent")
    params: dict[str, Any] = Field(default_factory=dict, description="Parameter")


class CommandResponse(BaseModel):
    """Generic Command Response"""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="Status (success/error)")
    action: str = Field(..., description="Ausgeführte Aktion")
    result: dict[str, Any] | None = Field(None, description="Ergebnis")
    error: str | None = Field(None, description="Fehlermeldung")
    timestamp: str = Field(..., description="Timestamp")


class InvokeRequest(BaseModel):
    """PORTIER 3.0 Option-2-Flow Invoke Request"""

    model_config = ConfigDict(extra="forbid")

    action: str = Field(..., description="Aktion (z.B. 'get_status', 'dispatch')")
    params: dict[str, Any] = Field(default_factory=dict, description="Parameter")


class DispatchRequest(BaseModel):
    """Agent Dispatch Request"""

    model_config = ConfigDict(extra="forbid")

    target_agent: str = Field(..., description="Ziel-Agent ID")
    action: str = Field(..., description="Aktion")
    payload: dict[str, Any] = Field(default_factory=dict, description="Payload")
    timeout: int = Field(30, ge=5, le=300, description="Timeout in Sekunden")


class DispatchResponse(BaseModel):
    """Agent Dispatch Response"""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="Status")
    target_agent: str = Field(..., description="Ziel-Agent")
    response: dict[str, Any] | None = Field(None, description="Agent-Response")
    response_time_ms: float = Field(..., description="Antwortzeit")
    safepoint_id: str | None = Field(None, description="Safepoint ID")


# ==================== Alert Models ====================


class Alert(BaseModel):
    """System Alert"""

    model_config = ConfigDict(extra="forbid")

    alert_id: str = Field(..., description="Alert ID")
    severity: AlertSeverity = Field(..., description="Schweregrad")
    source: str = Field(..., description="Quelle")
    title: str = Field(..., description="Titel")
    message: str = Field(..., description="Nachricht")
    timestamp: str = Field(..., description="Timestamp")
    acknowledged: bool = Field(False, description="Bestätigt")
    resolved: bool = Field(False, description="Aufgelöst")


class AlertCreateRequest(BaseModel):
    """Alert erstellen"""

    model_config = ConfigDict(extra="forbid")

    severity: AlertSeverity = Field(..., description="Schweregrad")
    source: str = Field(..., description="Quelle")
    title: str = Field(..., min_length=1, max_length=200, description="Titel")
    message: str = Field(..., min_length=1, max_length=2000, description="Nachricht")


# ==================== Metric Models ====================


class Metric(BaseModel):
    """System Metric"""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Metrik-Name")
    value: float = Field(..., description="Wert")
    unit: str = Field(..., description="Einheit")
    timestamp: str = Field(..., description="Timestamp")
    source: str = Field(..., description="Quelle")
    tags: dict[str, str] = Field(default_factory=dict, description="Tags")


class MetricSeries(BaseModel):
    """Metriken-Zeitreihe"""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Metrik-Name")
    source: str = Field(..., description="Quelle")
    data_points: list[dict[str, Any]] = Field(..., description="Datenpunkte")
    interval: str = Field(..., description="Aggregations-Interval")


# ==================== Dashboard Configuration Models ====================


class DashboardSettings(BaseModel):
    """Dashboard Einstellungen"""

    model_config = ConfigDict(extra="forbid")

    theme: str = Field("dark", description="Theme (dark/light)")
    refresh_interval: int = Field(5000, description="Refresh Interval in ms")
    show_offline_agents: bool = Field(True, description="Offline Agents anzeigen")
    enable_notifications: bool = Field(True, description="Browser Notifications")
    enable_sounds: bool = Field(False, description="Sound Alerts")
    default_view: str = Field("grid", description="Default View (grid/list)")


class DashboardWidget(BaseModel):
    """Dashboard Widget Konfiguration"""

    model_config = ConfigDict(extra="forbid")

    widget_id: str = Field(..., description="Widget ID")
    widget_type: str = Field(..., description="Widget-Typ")
    title: str = Field(..., description="Widget-Titel")
    position: dict[str, int] = Field(..., description="Position (x, y, w, h)")
    config: dict[str, Any] = Field(default_factory=dict, description="Widget-Config")
    enabled: bool = Field(True, description="Widget aktiv")


# ==================== API Response Wrappers ====================


class APIResponse(BaseModel):
    """Generic API Response Wrapper"""

    model_config = ConfigDict(extra="forbid")

    success: bool = Field(..., description="Erfolg")
    data: Any | None = Field(None, description="Daten")
    error: str | None = Field(None, description="Fehlermeldung")
    timestamp: str = Field(..., description="Response Timestamp")


class PaginatedResponse(BaseModel):
    """Paginierte Response"""

    model_config = ConfigDict(extra="forbid")

    items: list[Any] = Field(..., description="Ergebnisse")
    total: int = Field(..., description="Gesamtzahl")
    page: int = Field(..., description="Aktuelle Seite")
    page_size: int = Field(..., description="Seitengröße")
    pages: int = Field(..., description="Anzahl Seiten")


# ==================== Export ====================

__all__ = [
    # Enums
    "AgentStatus",
    "EventType",
    "AlertSeverity",
    "SafepointCategory",
    # Health & Status
    "HealthResponse",
    "AgentHealthResponse",
    "AllAgentsStatusResponse",
    # SSE
    "SSEEvent",
    "SSEConnectionInfo",
    # Safepoint
    "SafepointRecord",
    "SafepointIndexEntry",
    # API
    "CommandRequest",
    "CommandResponse",
    "InvokeRequest",
    "DispatchRequest",
    "DispatchResponse",
    # Alerts
    "Alert",
    "AlertCreateRequest",
    # Metrics
    "Metric",
    "MetricSeries",
    # Dashboard
    "DashboardSettings",
    "DashboardWidget",
    # Wrappers
    "APIResponse",
    "PaginatedResponse",
]
