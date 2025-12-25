#!/usr/bin/env python3
"""
opena21 - Workflow Engine Agent
Pydantic Models

Port: 12364
Kürzel: workflowp

PORTIER 3.0 Strict JSON Schemas für Workflows
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ==================== Enums ====================


class WorkflowState(str, Enum):
    """Workflow-Zustände"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    WAITING = "waiting"


class StepState(str, Enum):
    """Step-Zustände"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class ActionType(str, Enum):
    """Erlaubte Action-Typen"""

    CALL_AGENT = "call_agent"
    TRANSFORM_DATA = "transform_data"
    CONDITION = "condition"
    WAIT = "wait"
    PARALLEL = "parallel"
    SEQUENCE = "sequence"
    RETRY = "retry"
    TIMEOUT = "timeout"


class OnFailureAction(str, Enum):
    """Verhalten bei Fehler"""

    STOP = "stop"
    CONTINUE = "continue"
    RETRY = "retry"
    SKIP = "skip"


class SafepointCategory(str, Enum):
    """Safepoint Kategorien nach PORTIER 3.0"""

    CMD = "CMD"
    RESP = "RESP"
    ROUTE = "ROUTE"
    DISPATCH = "DISPATCH"


# ==================== Step Models ====================


class StepDefinition(BaseModel):
    """Definition eines Workflow-Steps"""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=100, description="Step-Name")
    action: ActionType = Field(..., description="Aktion")
    agent: str | None = Field(None, description="Ziel-Agent (für call_agent)")
    params: dict[str, Any] = Field(default_factory=dict, description="Parameter")
    timeout: int = Field(30, ge=5, le=300, description="Timeout in Sekunden")
    retry_count: int = Field(0, ge=0, le=5, description="Retry-Versuche")
    retry_delay: int = Field(1, ge=1, le=60, description="Retry-Delay in Sekunden")
    condition: str | None = Field(None, description="Ausführungsbedingung")
    on_failure: OnFailureAction = Field(OnFailureAction.STOP, description="Fehlerverhalten")
    depends_on: list[str] | None = Field(None, description="Abhängigkeiten")
    description: str | None = Field(None, max_length=500, description="Beschreibung")


class StepResult(BaseModel):
    """Ergebnis eines ausgeführten Steps"""

    model_config = ConfigDict(extra="forbid")

    step_name: str = Field(..., description="Step-Name")
    state: StepState = Field(..., description="Zustand")
    started_at: str = Field(..., description="Startzeit")
    completed_at: str | None = Field(None, description="Endzeit")
    duration_ms: int = Field(0, description="Dauer in ms")
    output: dict[str, Any] | None = Field(None, description="Output-Daten")
    error: str | None = Field(None, description="Fehlermeldung")
    retry_count: int = Field(0, description="Durchgeführte Retries")


# ==================== Workflow Models ====================


class WorkflowDefinition(BaseModel):
    """Vollständige Workflow-Definition"""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=100, description="Workflow-Name")
    description: str | None = Field(None, max_length=1000, description="Beschreibung")
    version: str = Field("1.0", description="Version")
    steps: list[StepDefinition] = Field(..., min_length=1, description="Steps")
    timeout: int = Field(300, ge=30, le=3600, description="Gesamttimeout")
    tags: list[str] = Field(default_factory=list, description="Tags")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata")


class WorkflowStatus(BaseModel):
    """Status eines Workflows"""

    model_config = ConfigDict(extra="forbid")

    workflow_id: str = Field(..., description="Workflow-ID")
    workflow_name: str = Field(..., description="Workflow-Name")
    state: WorkflowState = Field(..., description="Zustand")
    current_step: str | None = Field(None, description="Aktueller Step")
    started_at: str = Field(..., description="Startzeit")
    completed_at: str | None = Field(None, description="Endzeit")
    duration_ms: int = Field(0, description="Dauer in ms")
    progress: float = Field(0.0, ge=0.0, le=100.0, description="Fortschritt %")
    steps_completed: int = Field(0, description="Abgeschlossene Steps")
    steps_total: int = Field(0, description="Gesamtzahl Steps")
    outputs: dict[str, Any] = Field(default_factory=dict, description="Workflow-Outputs")
    error: str | None = Field(None, description="Fehlermeldung")
    step_results: list[StepResult] = Field(default_factory=list, description="Step-Ergebnisse")


class WorkflowSummary(BaseModel):
    """Kurze Workflow-Zusammenfassung"""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Workflow-Name")
    description: str | None = Field(None, description="Beschreibung")
    steps_count: int = Field(..., description="Anzahl Steps")
    timeout: int = Field(..., description="Timeout")
    tags: list[str] = Field(default_factory=list, description="Tags")


# ==================== API Request/Response Models ====================


class ExecuteRequest(BaseModel):
    """Request zum Starten eines Workflows"""

    model_config = ConfigDict(extra="forbid")

    workflow_name: str = Field(..., description="Workflow-Name")
    inputs: dict[str, Any] = Field(default_factory=dict, description="Input-Parameter")
    mode: str = Field("sync", pattern="^(sync|async)$", description="Ausführungsmodus")
    priority: int = Field(5, ge=1, le=10, description="Priorität (1-10)")


class ExecuteResponse(BaseModel):
    """Response nach Workflow-Start"""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="Status (success/error)")
    workflow_id: str = Field(..., description="Workflow-ID")
    message: str = Field(..., description="Nachricht")
    execution: WorkflowStatus | None = Field(None, description="Execution-Details")


class InvokeRequest(BaseModel):
    """PORTIER 3.0 Option-2-Flow Invoke Request"""

    model_config = ConfigDict(extra="forbid")

    action: str = Field(..., description="Aktion")
    params: dict[str, Any] = Field(default_factory=dict, description="Parameter")


class InvokeResponse(BaseModel):
    """Invoke Response"""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="Status")
    action: str = Field(..., description="Aktion")
    result: dict[str, Any] | None = Field(None, description="Ergebnis")
    error: str | None = Field(None, description="Fehlermeldung")


# ==================== Safepoint Models ====================


class SafepointRequest(BaseModel):
    """Safepoint für Option-2-Flow Archivierung"""

    model_config = ConfigDict(extra="forbid")

    sp_id: str = Field(..., description="Safepoint-ID")
    timestamp: str = Field(..., description="ISO 8601 Timestamp")
    source: str = Field(..., description="Quell-Agent")
    destination: str = Field(..., description="Ziel-Agent")
    kind: SafepointCategory = Field(..., description="Art (CMD/RESP)")
    payload: dict[str, Any] = Field(..., description="Nutzdaten")
    workflow_id: str | None = Field(None, description="Workflow-ID")
    step_name: str | None = Field(None, description="Step-Name")


# ==================== Health & Monitoring ====================


class HealthResponse(BaseModel):
    """Health-Check Response"""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="Status (ok/error)")
    service: str = Field(..., description="Service-Name")
    port: int = Field(..., description="Port")
    program_target: str = Field(..., description="PORTIER Kürzel")
    uptime_seconds: float = Field(..., description="Uptime")
    version: str = Field(..., description="Version")

    # Workflow-spezifisch
    workflows_count: int = Field(0, description="Definierte Workflows")
    executions_running: int = Field(0, description="Laufende Executions")
    executions_completed: int = Field(0, description="Abgeschlossene Executions")
    executions_failed: int = Field(0, description="Fehlgeschlagene Executions")

    # Connectivity
    portier_connected: bool = Field(False, description="Portier-Verbindung")
    opena2_connected: bool = Field(False, description="OpenA2-Verbindung")

    strict: bool = Field(True, description="Strict JSON Mode")


class WorkflowStatistics(BaseModel):
    """Workflow-Engine Statistiken"""

    model_config = ConfigDict(extra="forbid")

    total_executions: int = Field(0, description="Gesamtanzahl Executions")
    successful_executions: int = Field(0, description="Erfolgreiche Executions")
    failed_executions: int = Field(0, description="Fehlgeschlagene Executions")
    cancelled_executions: int = Field(0, description="Abgebrochene Executions")
    total_steps_executed: int = Field(0, description="Gesamtanzahl Steps")
    average_duration_ms: float = Field(0.0, description="Durchschnittliche Dauer")
    last_execution: str | None = Field(None, description="Letzte Execution")


class WorkflowListResponse(BaseModel):
    """Liste aller Workflows"""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="Status")
    count: int = Field(..., description="Anzahl")
    workflows: list[WorkflowSummary] = Field(..., description="Workflow-Summaries")


class ExecutionListResponse(BaseModel):
    """Liste aller Executions"""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="Status")
    count: int = Field(..., description="Anzahl")
    statistics: WorkflowStatistics = Field(..., description="Statistiken")
    executions: list[WorkflowStatus] = Field(..., description="Executions")


# ==================== Error Models ====================


class WorkflowError(BaseModel):
    """Workflow-Fehler"""

    model_config = ConfigDict(extra="forbid")

    error_code: str = Field(..., description="Fehlercode")
    message: str = Field(..., description="Fehlermeldung")
    workflow_id: str | None = Field(None, description="Workflow-ID")
    step_name: str | None = Field(None, description="Step-Name")
    details: dict[str, Any] = Field(default_factory=dict, description="Details")
    timestamp: str = Field(..., description="Timestamp")


# ==================== Export ====================

__all__ = [
    # Enums
    "WorkflowState",
    "StepState",
    "ActionType",
    "OnFailureAction",
    "SafepointCategory",
    # Step Models
    "StepDefinition",
    "StepResult",
    # Workflow Models
    "WorkflowDefinition",
    "WorkflowStatus",
    "WorkflowSummary",
    # API Models
    "ExecuteRequest",
    "ExecuteResponse",
    "InvokeRequest",
    "InvokeResponse",
    # Safepoint
    "SafepointRequest",
    # Health & Monitoring
    "HealthResponse",
    "WorkflowStatistics",
    "WorkflowListResponse",
    "ExecutionListResponse",
    # Errors
    "WorkflowError",
]
