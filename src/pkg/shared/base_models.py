"""
Shared Base Models
Common Pydantic models used across all agents.

Updated to use Pydantic V2 ConfigDict style for consistency with opena6 browser agent.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class CommandRequest(BaseModel):
    """
    Generic command request for Option-2-Flow compatibility.
    
    Used by all agents to handle command-based requests.
    """
    model_config = ConfigDict(extra="forbid")
    
    command: str = Field(..., min_length=1, max_length=200, description="Command to execute")
    params: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")


class HealthResponse(BaseModel):
    """
    Standard health check response for all agents.
    
    Provides consistent health check format across the system.
    """
    model_config = ConfigDict(extra="allow")  # Allow agents to add custom fields
    
    status: str = Field(..., description="Health status: 'ok', 'degraded', 'unhealthy'")
    service: str = Field(..., description="Service name (e.g., 'opena11')")
    kuerzel: str = Field(..., description="Service abbreviation (e.g., 'unlockp')")
    port: int = Field(..., description="Service port number")
    uptime_seconds: float = Field(..., description="Uptime in seconds since service start")
    timestamp: str = Field(..., description="ISO 8601 timestamp of health check")
    
    # Optional additional fields that agents can include
    extra_info: Optional[Dict[str, Any]] = Field(None, description="Additional service-specific info")


class ServiceInfo(BaseModel):
    """
    Service information response for root endpoint.
    """
    model_config = ConfigDict(extra="forbid")
    
    service: str = Field(..., description="Service name")
    kuerzel: str = Field(..., description="Service abbreviation")
    description: str = Field(..., description="Service description")
    port: int = Field(..., description="Service port")
    version: str = Field(..., description="Service version")
    endpoints: list = Field(default_factory=list, description="Available endpoints")


class SuccessResponse(BaseModel):
    """
    Generic success response.
    """
    model_config = ConfigDict(extra="forbid")
    
    status: str = Field(default="success", description="Response status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")


class ErrorResponse(BaseModel):
    """
    Generic error response.
    """
    model_config = ConfigDict(extra="forbid")
    
    status: str = Field(default="error", description="Response status")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


def get_current_timestamp_iso() -> str:
    """
    Get current timestamp in ISO 8601 format with Z suffix.
    
    Returns:
        ISO 8601 timestamp string (e.g., "2025-12-18T01:51:20.000Z")
    """
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def create_health_response(
    service: str,
    kuerzel: str,
    port: int,
    start_time: float,
    **extra_info
) -> HealthResponse:
    """
    Factory function to create a standard health response.
    
    Args:
        service: Service name (e.g., "opena11")
        kuerzel: Service abbreviation (e.g., "unlockp")
        port: Service port number
        start_time: Service start time (from time.time())
        **extra_info: Additional service-specific information
        
    Returns:
        HealthResponse instance
        
    Example:
        >>> import time
        >>> START_TIME = time.time()
        >>> response = create_health_response(
        ...     service="opena11",
        ...     kuerzel="unlockp",
        ...     port=12356,
        ...     start_time=START_TIME,
        ...     permissions_count=42
        ... )
    """
    import time
    uptime = time.time() - start_time
    
    return HealthResponse(
        status="ok",
        service=service,
        kuerzel=kuerzel,
        port=port,
        uptime_seconds=round(uptime, 2),
        timestamp=get_current_timestamp_iso(),
        extra_info=extra_info if extra_info else None
    )


def create_service_info(
    service: str,
    kuerzel: str,
    description: str,
    port: int,
    version: str,
    endpoints: list
) -> ServiceInfo:
    """
    Factory function to create service info for root endpoint.
    
    Args:
        service: Service name
        kuerzel: Service abbreviation
        description: Service description
        port: Service port
        version: Service version
        endpoints: List of available endpoint paths
        
    Returns:
        ServiceInfo instance
    """
    return ServiceInfo(
        service=service,
        kuerzel=kuerzel,
        description=description,
        port=port,
        version=version,
        endpoints=endpoints
    )
