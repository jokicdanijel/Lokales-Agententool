"""
schemas.py — Complete Pydantic Schemas for opena1
Strict validation for request routing and logging.
LOCATION: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/schemas.py
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class RoutingData(BaseModel):
    """Routing metadata for request."""
    model_config = ConfigDict(extra="forbid")
    
    resolved_path: Optional[str] = None
    target: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)


class ProjectData(BaseModel):
    """Project metadata."""
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., min_length=1)
    id: str = Field(..., min_length=1)


class Request71(BaseModel):
    """7.1 Strict validation schema for opena1 logging."""
    model_config = ConfigDict(extra="forbid")
    
    request_id: str = Field(..., description="UUID v4 format")
    timestamp: str = Field(..., description="ISO-8601 with Z suffix")
    command: str = Field(..., min_length=1)
    payload: Dict[str, Any] = Field(default_factory=dict)
    routing: RoutingData = Field(default_factory=RoutingData)
    project: ProjectData
    strict: bool = Field(default=True)


class ErrorSchema83(BaseModel):
    """Error response schema 8.3 (standard error format)."""
    model_config = ConfigDict(extra="forbid")
    
    request_id: str = Field(default="unknown")
    timestamp: str
    source: str = Field(default="opena1")
    error: Dict[str, Any] = Field(
        default_factory=lambda: {"code": "", "message": "", "details": {}}
    )
    strict: bool = Field(default=True)


class Decision72(BaseModel):
    """Decision response schema 7.2 (opena1 decision output)."""
    model_config = ConfigDict(extra="forbid")
    
    request_id: str = Field(..., description="Request UUID")
    timestamp: str = Field(..., description="ISO-8601 Z timestamp")
    source: str = Field(default="opena1")
    decision: Dict[str, Any] = Field(
        ...,
        description="Decision details (selected_tool, reason, resolved_path)"
    )
    archivator_forward: Dict[str, Any] = Field(
        default_factory=dict,
        description="Archivator forwarding status (endpoint, status)"
    )
    status: str = Field(..., description="Decision status (FORWARDED, ERROR, etc.)")
    strict: bool = Field(default=True)
