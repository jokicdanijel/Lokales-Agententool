"""
kordp/schemas.py — Pydantic Schemas for kordp
Dispatch request/response structures.
LOCATION: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/kordp/schemas.py
"""

from typing import Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class DispatchRequest(BaseModel):
    """Task dispatch request schema."""
    model_config = ConfigDict(extra="forbid")
    
    agent: str = Field(..., min_length=1, description="Target tool/agent identifier")
    action: str = Field(..., min_length=1, description="Action/command to execute")
    data: Dict[str, Any] = Field(default_factory=dict, description="Request payload")
    request_id: str = Field(..., description="Request UUID")
    strict: bool = Field(default=True)


class DispatchResponse(BaseModel):
    """Task dispatch response schema."""
    model_config = ConfigDict(extra="forbid")
    
    ok: bool = Field(..., description="Success flag")
    routed_to: Dict[str, Any] = Field(..., description="Route information")
    request_id: str = Field(..., description="Request identifier")
    strict: bool = Field(default=True)


class RouteInfo(BaseModel):
    """Route registration info."""
    model_config = ConfigDict(extra="forbid")
    
    tool_id: str = Field(..., min_length=1)
    agent_id: str = Field(..., min_length=1)
    port: int = Field(..., ge=12344, le=12399)
    endpoint: str = Field(..., min_length=1)
    timeout: int = Field(default=30)
    enabled: bool = Field(default=True)


class HealthResponse(BaseModel):
    """Health check response schema."""
    model_config = ConfigDict(extra="forbid")
    
    status: str = Field(..., description="Service status (ok, degraded, down)")
    service: str = Field(..., description="Service name")
    role: str = Field(..., description="Service role")
    timestamp: str = Field(..., description="ISO-8601 Z timestamp")
    port_policy: Dict[str, Any] = Field(default_factory=dict)
    strict: bool = Field(default=True)
