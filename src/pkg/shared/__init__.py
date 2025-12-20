"""SCTA Shared Utilities."""

# Configuration and base classes
from .config_base import PortPolicy, BaseAgentConfig, AgentInfo

# Security components
from .security import (
    BEARER_TOKEN,
    DEV_MODE,
    SECRET_KEYS,
    mask_secrets,
    security,
    verify_token,
    optional_verify_token,
    RateLimiter,
    default_limiter,
    api_limiter,
    PortPolicyEnforcer
)

# Safepoint client
from .safepoint_client import SafepointClient

# SSE client
from .sse_client import (
    SSEEvent,
    SSEClient,
    SafepointClient as SSESafepointClient,  # Note: duplicate of above, kept for backward compat
    create_sse_client,
    create_safepoint_client,
    get_sse_client,
    get_safepoint_client
)

__all__ = [
    # Config
    "PortPolicy",
    "BaseAgentConfig", 
    "AgentInfo",
    # Security
    "BEARER_TOKEN",
    "DEV_MODE",
    "SECRET_KEYS",
    "mask_secrets",
    "security",
    "verify_token",
    "optional_verify_token",
    "RateLimiter",
    "default_limiter",
    "api_limiter",
    "PortPolicyEnforcer",
    # Safepoint
    "SafepointClient",
    # SSE
    "SSEEvent",
    "SSEClient",
    "create_sse_client",
    "create_safepoint_client",
    "get_sse_client",
    "get_safepoint_client"
]
