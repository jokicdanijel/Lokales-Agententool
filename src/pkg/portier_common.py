#!/usr/bin/env python3
"""
Backward Compatibility Wrapper for Agent Migration

This module provides backward-compatible imports for agents during migration.
Agents can use this wrapper to gradually migrate to shared libraries without
breaking existing code.

Usage in agents (drop-in replacement):
    # Instead of: from safepoint_client import SafepointClient
    # Use: from portier_common import SafepointClient
    
    # Instead of: from sse_client import SSEClient, get_sse_client
    # Use: from portier_common import SSEClient, create_sse_client
    
    # Instead of: from security import verify_token, mask_secrets
    # Use: from portier_common import verify_token, mask_secrets
"""

# Re-export everything from shared modules for backward compatibility
from src.pkg.shared.safepoint_client import SafepointClient
from src.pkg.shared.sse_client import (
    SSEEvent,
    SSEClient,
    SafepointClient as SSESafepointClient,
    create_sse_client,
    create_safepoint_client,
    get_sse_client,
    get_safepoint_client
)
from src.pkg.shared.security import (
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
from src.pkg.shared.config_base import (
    PortPolicy,
    BaseAgentConfig,
    AgentInfo
)

__all__ = [
    # Safepoint
    "SafepointClient",
    # SSE
    "SSEEvent",
    "SSEClient",
    "SSESafepointClient",
    "create_sse_client",
    "create_safepoint_client",
    "get_sse_client",
    "get_safepoint_client",
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
    # Config
    "PortPolicy",
    "BaseAgentConfig",
    "AgentInfo"
]
