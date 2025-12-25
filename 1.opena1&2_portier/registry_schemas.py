"""
Registry Schemas – Pydantic v2 models for Tool Registry validation
Part of Schritt 2 (Tool-Registry & Mapping)
"""

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ToolCategoryEnum(str, Enum):
    """Tool categories"""

    BROWSE = "browse"
    ANALYZE = "analyze"
    EDIT = "edit"
    MONITOR = "monitor"
    NOTIFY = "notify"
    EXECUTE = "execute"
    QUERY = "query"
    STORE = "store"


class ToolSchema(BaseModel):
    """Schema for tool definition"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(..., min_length=1, max_length=50, description="Unique tool ID")
    name: str = Field(..., min_length=1, max_length=100, description="Human-readable name")
    category: ToolCategoryEnum = Field(..., description="Tool category")
    description: str = Field(..., min_length=1, max_length=500, description="Tool description")
    agent_id: str = Field(..., min_length=1, max_length=50, description="Agent that handles this tool")
    port: int = Field(..., ge=12344, le=12399, description="Agent port")
    endpoint: str = Field(..., pattern="^/.*", description="API endpoint path")
    timeout_seconds: int = Field(default=30, ge=1, le=300, description="Timeout in seconds")
    requires_auth: bool = Field(default=True, description="Requires authentication")
    params: dict[str, str] = Field(default_factory=dict, description="Expected parameters")
    response_type: str = Field(default="json", description="Response type")
    deprecated: bool = Field(default=False, description="Deprecated flag")
    version: str = Field(default="1.0", description="Tool version")

    @field_validator("id", "agent_id")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        """Validate identifier format"""
        if not v.replace("_", "").isalnum():
            raise ValueError("Must be alphanumeric with underscores")
        return v


class AgentSchema(BaseModel):
    """Schema for agent definition"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(..., min_length=1, max_length=50, description="Unique agent ID")
    name: str = Field(..., min_length=1, max_length=100, description="Human-readable name")
    port: int = Field(..., ge=12344, le=12399, description="Agent port (or 8080 for opena3)")
    host: str = Field(default="127.0.0.1", description="Bind host")
    description: str = Field(default="", max_length=500, description="Agent description")
    enabled: bool = Field(default=True, description="Is agent enabled")
    role: str = Field(default="", max_length=100, description="Agent role")
    tools: list[str] = Field(default_factory=list, description="Tool IDs this agent handles")
    dependencies: list[str] = Field(default_factory=list, description="Dependent agent IDs")
    health_endpoint: str = Field(default="/health", description="Health check endpoint")
    max_concurrent: int = Field(default=100, ge=1, le=10000, description="Max concurrent requests")
    retry_count: int = Field(default=3, ge=0, le=10, description="Retry count on failure")
    retry_delay_ms: int = Field(default=100, ge=0, le=10000, description="Delay between retries")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port is in allowed range"""
        if v != 8080 and not (12344 <= v <= 12399):
            raise ValueError("Port must be in [12344-12399] or 8080")
        return v

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate agent ID format"""
        if not v.replace("_", "").isalnum():
            raise ValueError("Must be alphanumeric with underscores")
        return v


class RegistrySchema(BaseModel):
    """Schema for complete registry"""

    model_config = ConfigDict(extra="forbid")

    agents: dict[str, AgentSchema] = Field(..., description="Agents by ID")
    tools: dict[str, ToolSchema] = Field(..., description="Tools by ID")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


# ──────────────────────────────────────────────────────────────────────────────
# Tool Request/Response Models
# ──────────────────────────────────────────────────────────────────────────────


class ToolRequestParams71(BaseModel):
    """7.1-Compatible tool request parameters"""

    model_config = ConfigDict(extra="forbid")

    strict: Literal[True] = Field(..., description="Must be True for strict validation")
    request_id: str = Field(..., min_length=1, description="Unique request ID")
    timestamp: str = Field(..., description="ISO-8601 Z timestamp")
    tool_id: str = Field(..., min_length=1, description="Tool to execute")
    params: dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    source_agent: str = Field(default="dashboard", description="Source agent ID")

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate ISO-8601 Z format"""
        if not v.endswith("Z"):
            raise ValueError("Timestamp must end with 'Z' (ISO-8601)")
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Invalid ISO-8601 timestamp")
        return v


class ToolResponseItem(BaseModel):
    """Single tool response item"""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="Status: ok, error, timeout")
    data: dict[str, Any] = Field(default_factory=dict, description="Response data")
    error: str | None = Field(default=None, description="Error message if any")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class ToolResponse71(BaseModel):
    """7.1-Compatible tool response"""

    model_config = ConfigDict(extra="forbid")

    ok: bool = Field(..., description="Success flag")
    request_id: str = Field(..., description="Echo request ID")
    tool_id: str = Field(..., description="Tool that was executed")
    target_agent: str = Field(..., description="Target agent")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    result: dict[str, Any] = Field(default_factory=dict, description="Tool result")
    cmd_safepoint: str | None = Field(default=None, description="Command safepoint path")
    resp_safepoint: str | None = Field(default=None, description="Response safepoint path")


class ErrorDetail(BaseModel):
    """Error detail structure"""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(..., min_length=1, description="Error code")
    message: str = Field(..., description="Error message")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional details")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class ErrorResponse83(BaseModel):
    """Error response in schema 8.3 format"""

    model_config = ConfigDict(extra="forbid")

    ok: Literal[False] = Field(default=False)
    request_id: str | None = Field(default=None, description="Request ID if available")
    error: ErrorDetail = Field(..., description="Error information")


class DispatchRequest(BaseModel):
    """Request to dispatch a tool"""

    model_config = ConfigDict(extra="forbid")

    tool_id: str = Field(..., min_length=1, description="Tool to execute")
    params: dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    source_agent: str = Field(default="dashboard", description="Source agent")
    request_id: str | None = Field(default=None, description="Request ID (auto-generated if not provided)")


class AgentHealthResponse(BaseModel):
    """Agent health check response"""

    model_config = ConfigDict(extra="forbid")

    ok: bool = Field(..., description="Health status")
    agent_id: str = Field(..., description="Agent ID")
    port: int = Field(..., description="Agent port")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    uptime_seconds: float | None = Field(default=None, description="Uptime in seconds")
    status: str = Field(default="ok", description="Detailed status")


class RegistryStatusResponse(BaseModel):
    """Registry status overview"""

    model_config = ConfigDict(extra="forbid")

    ok: bool = Field(default=True)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    total_agents: int = Field(..., ge=0)
    enabled_agents: int = Field(..., ge=0)
    total_tools: int = Field(..., ge=0)
    active_tools: int = Field(..., ge=0)
    agents_by_role: dict[str, int] = Field(default_factory=dict)
    tools_by_category: dict[str, int] = Field(default_factory=dict)


class ToolListResponse(BaseModel):
    """List of available tools"""

    model_config = ConfigDict(extra="forbid")

    ok: bool = Field(default=True)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    agent_id: str | None = Field(default=None, description="If filtered by agent")
    count: int = Field(..., ge=0)
    tools: list[dict[str, Any]] = Field(default_factory=list)
