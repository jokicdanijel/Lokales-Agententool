#!/usr/bin/env python3
"""
opena7 - Pydantic Models

Port: 12353
Kürzel: emailp

PORTIER 3.0 Strict JSON Schemas
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class AgentStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class SafepointCategory(str, Enum):
    CMD = "CMD"
    RESP = "RESP"
    ROUTE = "ROUTE"
    DISPATCH = "DISPATCH"


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    status: str = Field(..., description="Status (ok/error)")
    service: str = Field(..., description="Service-Name")
    kuerzel: str = Field(..., description="PORTIER Kürzel")
    port: int = Field(..., description="Port-Nummer")
    uptime_seconds: float = Field(..., description="Uptime in Sekunden")
    version: str = Field(..., description="Version")
    strict: bool = Field(True, description="Strict JSON Mode")


class CommandRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    action: str = Field(..., description="Aktion")
    target: Optional[str] = Field(None, description="Ziel-Agent")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameter")


class CommandResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    status: str = Field(..., description="Status (success/error)")
    action: str = Field(..., description="Ausgeführte Aktion")
    result: Optional[Dict[str, Any]] = Field(None, description="Ergebnis")
    error: Optional[str] = Field(None, description="Fehlermeldung")
    timestamp: str = Field(..., description="Timestamp")


class InvokeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    action: str = Field(..., description="Aktion")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameter")


class SafepointRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    sp_timestamp: int = Field(..., description="Unix Timestamp")
    timestamp: str = Field(..., description="ISO 8601 Timestamp")
    source: str = Field(..., description="Quell-Agent")
    destination: str = Field(..., description="Ziel-Agent")
    category: SafepointCategory = Field(..., description="Kategorie")
    request_id: str = Field(..., description="Request ID")
    payload: Dict[str, Any] = Field(..., description="Payload")
    strict: bool = Field(True, description="Strict Mode")


class APIResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    success: bool = Field(..., description="Erfolg")
    data: Optional[Any] = Field(None, description="Daten")
    error: Optional[str] = Field(None, description="Fehlermeldung")
    timestamp: str = Field(..., description="Response Timestamp")


__all__ = [
    "AgentStatus", "SafepointCategory", "HealthResponse",
    "CommandRequest", "CommandResponse", "InvokeRequest",
    "SafepointRecord", "APIResponse"
]
