"""
Pydantic v2 schemas for opena4 (Telegram Agent)
Aligned with 7.1 strict validation format
"""

from typing import Optional, Any, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
import re
import uuid


class Routing(BaseModel):
    """Routing metadata for message flow"""
    model_config = ConfigDict(extra="forbid")

    resolved_path: Optional[str] = Field(None, description="Resolved file or URL path")
    notes: Optional[str] = Field(None, description="Routing notes")


class Project(BaseModel):
    """Project metadata"""
    model_config = ConfigDict(extra="forbid")

    id: Optional[str] = Field(default="telegram_relay", description="Project identifier")
    name: str = Field(..., description="Project name")


class Command71(BaseModel):
    """Telegram command in 7.1 strict format (CMD)"""
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(..., description="Unique request ID (UUID4 or timestamp-based)")
    timestamp: str = Field(..., description="ISO-8601 timestamp with Z suffix (UTC)")
    command: str = Field(..., min_length=1, description="Command type (BROWSE, ANALYZE_FILE, STATUS, etc.)")
    target_preference: Optional[str] = Field(None, description="Preferred target (opena1, opena3, etc.)")
    payload: dict[str, Any] = Field(default_factory=dict, description="Command payload")
    routing: Routing = Field(default_factory=Routing, description="Routing metadata")
    project: Project = Field(..., description="Project metadata")
    strict: Literal[True] = Field(True, description="Strict mode enforcement")

    @field_validator("request_id")
    @classmethod
    def validate_request_id(cls, v):
        """Validate request_id is UUID4 format or numeric timestamp"""
        # Allow UUID4 format or numeric string (unix timestamp)
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        if not (re.match(uuid_pattern, v.lower()) or v.replace(".", "").isdigit()):
            raise ValueError("request_id must be UUID4 or numeric timestamp")
        return v

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v):
        """Validate ISO-8601 timestamp with Z suffix"""
        if not v.endswith("Z"):
            raise ValueError("timestamp must end with 'Z' (UTC)")
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("timestamp must be valid ISO-8601 format")
        return v

    @field_validator("strict")
    @classmethod
    def validate_strict(cls, v):
        """Enforce strict=True"""
        if v is not True:
            raise ValueError("strict must be True")
        return v


class Response71(BaseModel):
    """Telegram response in 7.1 strict format (RESP)"""
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(..., description="Echoed request ID")
    timestamp: str = Field(..., description="Response timestamp (ISO-8601 Z)")
    response_type: str = Field(..., description="Response type (SUCCESS, ERROR, PARTIAL)")
    payload: dict[str, Any] = Field(default_factory=dict, description="Response data")
    routing: Routing = Field(default_factory=Routing, description="Routing metadata")
    source: str = Field(default="opena4", description="Source agent")
    strict: Literal[True] = Field(True, description="Strict mode")

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v):
        """Validate ISO-8601 timestamp"""
        if not v.endswith("Z"):
            raise ValueError("timestamp must end with 'Z'")
        return v


class Safepoint(BaseModel):
    """Safepoint format for append-only persistence"""
    model_config = ConfigDict(extra="forbid")

    timestamp: str = Field(..., description="Safepoint creation timestamp")
    src: str = Field(..., description="Source agent (opena4)")
    dst: str = Field(..., description="Destination agent (opena2, opena1, etc.)")
    kind: Literal["CMD", "RESP", "ERR"] = Field(..., description="Safepoint kind")
    payload: dict[str, Any] | Command71 | Response71 = Field(..., description="Safepoint payload")
    strict: Literal[True] = Field(True, description="Strict mode")


class ErrorSchema83(BaseModel):
    """Standard error response (schema 8.3)"""
    model_config = ConfigDict(extra="forbid")

    request_id: Optional[str] = Field(None, description="Original request ID")
    timestamp: str = Field(..., description="Error timestamp")
    source: str = Field(default="opena4", description="Error source")
    error: dict[str, Any] = Field(..., description="Error details (code, message, details)")
    strict: Literal[True] = Field(True, description="Strict mode")


class TelegramMessage(BaseModel):
    """Telegram message metadata"""
    model_config = ConfigDict(extra="forbid")

    chat_id: int = Field(..., description="Telegram chat ID")
    user_id: int = Field(..., description="Telegram user ID")
    message_id: int = Field(..., description="Telegram message ID")
    text: str = Field(..., min_length=1, description="Message text")
    timestamp: str = Field(..., description="Message timestamp")


class HealthResponse(BaseModel):
    """Health-check response"""
    model_config = ConfigDict(extra="forbid")

    service: str = Field(default="opena4", description="Service name")
    status: str = Field(default="ok", description="Status (ok, degraded, error)")
    timestamp: str = Field(..., description="Health-check timestamp")
    port_policy: dict[str, Any] = Field(..., description="Port-policy window/forbidden")
    uptime_seconds: float = Field(..., description="Uptime in seconds")
