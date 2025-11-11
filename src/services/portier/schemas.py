"""
portier/schemas.py — Shared Pydantic Models
Defines request/response structures for Coordinator Gateway (kordp).
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ServiceInfo(BaseModel):
    """Service registration info."""
    model_config = ConfigDict(extra="forbid")
    
    agent: str = Field(..., min_length=1, description="Service identifier")
    agent_id: str = Field(..., min_length=1, description="Unique agent ID")
    port: int = Field(..., ge=12344, le=12399, description="Service port (Policy: 12344-12399)")
    program: str = Field(..., min_length=1, description="Program name (e.g., kordp, telep, openweb)")
    archivator_port: int = Field(default=12345, description="Archivator port (default: 12345)")
    mapping_ts: str = Field(..., description="Timestamp of route registration")
    mapping: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DispatchRequest(BaseModel):
    """Task dispatch request."""
    model_config = ConfigDict(extra="forbid")
    
    agent: str = Field(..., min_length=1, description="Target service identifier")
    action: str = Field(..., min_length=1, description="Action/command to execute")
    data: Dict[str, Any] = Field(default_factory=dict, description="Request payload")
    request_id: str = Field(default_factory=lambda: f"req-{int(datetime.utcnow().timestamp()*1000)}")
    strict: bool = Field(default=True, description="Strict validation flag")


class DispatchResponse(BaseModel):
    """Task dispatch response."""
    ok: bool = Field(..., description="Success flag")
    routed_to: Dict[str, Any] = Field(..., description="Route information")
    request_id: str = Field(..., description="Request identifier")
    strict: bool = Field(default=True)


class LogEntry(BaseModel):
    """Log entry model."""
    model_config = ConfigDict(extra="forbid")
    
    source: str = Field(..., min_length=1, description="Log source")
    event: str = Field(..., min_length=1, description="Event type")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    strict: bool = Field(default=True)
    ts: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status (ok, degraded, down)")
    service: str = Field(..., description="Service name")
    program_target: str = Field(..., description="Program target (kordp, telep, etc.)")
    role: str = Field(..., description="Service role (coordinator, gateway, etc.)")
    host: str = Field(..., description="Hostname")
    port: int = Field(..., description="Service port")
    routes_count: int = Field(default=0, description="Number of registered routes")
    openai_key_present: bool = Field(default=False, description="OpenAI API key available")
    openai_fp: str = Field(default="", description="OpenAI API key fingerprint")
    openai_base_url: str = Field(default="https://api.openai.com/v1")
    strict: bool = Field(default=True)
