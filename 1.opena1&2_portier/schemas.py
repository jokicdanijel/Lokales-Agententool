"""
opena1/schemas.py – 7.1-Validierungsschemas (Pydantic v2)
Strict validation for request routing and logging.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Any, Optional, Literal
from datetime import datetime
import re


class Routing(BaseModel):
    """Routing metadata for request."""
    resolved_path: Optional[str] = None
    notes: Optional[str] = None


class Project(BaseModel):
    """Project metadata."""
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


class Request71(BaseModel):
    """7.1 Strict validation schema for opena1 logging."""
    request_id: str = Field(..., description="UUID v4 format")
    timestamp: str = Field(..., description="ISO-8601 with Z suffix")
    command: str = Field(..., min_length=1)
    target_preference: Optional[str] = None
    payload: dict[str, Any] = Field(default_factory=dict)
    routing: Routing = Field(default_factory=Routing)
    project: Project
    strict: Literal[True]

    model_config = {"extra": "forbid"}  # Pydantic v2: reject unknown fields

    @field_validator("request_id")
    @classmethod
    def validate_request_id(cls, v: str) -> str:
        """Validate UUID4 format."""
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        if not re.match(uuid_pattern, v, re.IGNORECASE):
            raise ValueError("request_id must be valid UUID v4")
        return v

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate ISO-8601 format with Z suffix."""
        if not v.endswith("Z"):
            raise ValueError("timestamp must end with 'Z' (UTC)")
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("timestamp must be valid ISO-8601")
        return v

    @field_validator("strict")
    @classmethod
    def validate_strict(cls, v: bool) -> bool:
        """Enforce strict mode."""
        if v is not True:
            raise ValueError("strict must be True")
        return v


class ErrorSchema83(BaseModel):
    """Error response schema 8.3 (standard error format)."""
    request_id: str = Field(default="unknown")
    timestamp: str
    source: Literal["opena1"]
    error: dict[str, Any] = Field(
        default_factory=lambda: {"code": "", "message": "", "details": {}}
    )
    strict: Literal[True] = True
