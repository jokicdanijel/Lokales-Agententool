"""
SCTA Shared Pydantic Schemas
Centralized request/response validation models.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TaskStatus(str, Enum):
    """Task status enumeration."""

    PENDING = "pending"
    ROUTING = "routing"
    DECOMPOSED = "decomposed"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskCreate(BaseModel):
    """Request model for task creation."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        """Pydantic config: strict validation."""

        extra = "forbid"
        str_strip_whitespace = True


class TaskResponse(BaseModel):
    """Response model for task information."""

    id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class TaskListResponse(BaseModel):
    """Response model for task list."""

    total: int
    items: List[TaskResponse]
    page: int
    page_size: int


class SubtaskCreate(BaseModel):
    """Request model for subtask creation."""

    task_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    order: int = Field(..., ge=0)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        """Pydantic config."""

        extra = "forbid"


class SubtaskResponse(BaseModel):
    """Response model for subtask information."""

    id: UUID
    task_id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    order: int
    created_at: datetime
    updated_at: datetime
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., pattern="^(healthy|degraded|unhealthy)$")
    timestamp: datetime
    version: str
    dependencies: Dict[str, str]

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate health status value."""
        valid_statuses = {"healthy", "degraded", "unhealthy"}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v


class AgentResponse(BaseModel):
    """Response model for agent status."""

    agent_id: str
    name: str
    status: str
    port: int
    uptime_seconds: float
    tasks_processed: int


class AgentListResponse(BaseModel):
    """Response model for agent list."""

    agents: List[AgentResponse]
    total: int


class ErrorResponse(BaseModel):
    """Response model for error responses."""

    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        """Pydantic config."""

        extra = "forbid"


class PaginationParams(BaseModel):
    """Request model for pagination parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    class Config:
        """Pydantic config."""

        extra = "forbid"
