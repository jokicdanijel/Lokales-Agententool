"""
Pydantic Models für OpenA3 SDK
Strict JSON Schema - PORTIER 3.0 kompatibel
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List
from datetime import datetime

class CMDRequest(BaseModel):
    """Option-2-Flow CMD Envelope"""
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: str = Field(..., description="ISO timestamp")
    source: str = Field(..., description="Source service name")
    command: str = Field(..., description="Command type")
    payload: Dict[str, Any] = Field(..., description="Command payload")
    
    class Config:
        extra = "forbid"  # Strict mode

class ChatRequest(BaseModel):
    """Native Chat Request"""
    prompt: str = Field(..., min_length=1, description="Chat prompt")
    model: str = Field(default="gpt-4", description="AI model name")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    
    class Config:
        extra = "forbid"

class HealthResponse(BaseModel):
    """Health Check Response"""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Response timestamp")
    version: str = Field(..., description="Service version")
    uptime: Optional[float] = Field(default=None, description="Uptime in seconds")
    dependencies: Optional[Dict[str, str]] = Field(default=None)
    
    class Config:
        extra = "forbid"

class DispatchStatus(BaseModel):
    """Dispatch Ready Status"""
    ready: bool = Field(..., description="Dispatch ready status")
    kordp_available: bool = Field(..., description="kordp gateway status")
    last_dispatch: Optional[str] = Field(default=None, description="Last dispatch timestamp")
    
    class Config:
        extra = "forbid"

class SelfTestResult(BaseModel):
    """Self Test Result"""
    overall_status: str = Field(..., description="Overall test status")
    tests: List[Dict[str, Any]] = Field(..., description="Individual test results")
    timestamp: str = Field(..., description="Test execution timestamp")
    duration_ms: float = Field(..., description="Test duration in milliseconds")
    
    class Config:
        extra = "forbid"