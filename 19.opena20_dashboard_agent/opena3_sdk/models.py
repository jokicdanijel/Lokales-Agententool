"""
Pydantic Models für OpenA3 SDK
Strict JSON Schema - PORTIER 3.0 kompatibel
"""

from typing import Any

from pydantic import BaseModel, Field


class CMDRequest(BaseModel):
    """Option-2-Flow CMD Envelope"""

    request_id: str = Field(..., description="Unique request identifier")
    timestamp: str = Field(..., description="ISO timestamp")
    source: str = Field(..., description="Source service name")
    command: str = Field(..., description="Command type")
    payload: dict[str, Any] = Field(..., description="Command payload")

    class Config:
        extra = "forbid"  # Strict mode


class ChatRequest(BaseModel):
    """Native Chat Request"""

    prompt: str = Field(..., min_length=1, description="Chat prompt")
    model: str = Field(default="gpt-4", description="AI model name")
    temperature: float | None = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1)

    class Config:
        extra = "forbid"


class HealthResponse(BaseModel):
    """Health Check Response"""

    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Response timestamp")
    version: str = Field(..., description="Service version")
    uptime: float | None = Field(default=None, description="Uptime in seconds")
    dependencies: dict[str, str] | None = Field(default=None)

    class Config:
        extra = "forbid"


class DispatchStatus(BaseModel):
    """Dispatch Ready Status"""

    ready: bool = Field(..., description="Dispatch ready status")
    kordp_available: bool = Field(..., description="kordp gateway status")
    last_dispatch: str | None = Field(default=None, description="Last dispatch timestamp")

    class Config:
        extra = "forbid"


class SelfTestResult(BaseModel):
    """Self Test Result"""

    overall_status: str = Field(..., description="Overall test status")
    tests: list[dict[str, Any]] = Field(..., description="Individual test results")
    timestamp: str = Field(..., description="Test execution timestamp")
    duration_ms: float = Field(..., description="Test duration in milliseconds")

    class Config:
        extra = "forbid"
