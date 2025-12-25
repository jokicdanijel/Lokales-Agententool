"""SCTA Shared Utilities."""

# Configuration and base classes
from .config_base import AgentInfo, BaseAgentConfig, PortPolicy

# Safepoint client
from .safepoint_client import SafepointClient

# Security components
from .security import (
    BEARER_TOKEN,
    DEV_MODE,
    SECRET_KEYS,
    PortPolicyEnforcer,
    RateLimiter,
    api_limiter,
    default_limiter,
    mask_secrets,
    optional_verify_token,
    security,
    verify_token,
)

# SSE client
from .sse_client import SafepointClient as SSESafepointClient  # Note: duplicate of above, kept for backward compat
from .sse_client import (
    SSEClient,
    SSEEvent,
    create_safepoint_client,
    create_sse_client,
    get_safepoint_client,
    get_sse_client,
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
    "get_safepoint_client",
]
