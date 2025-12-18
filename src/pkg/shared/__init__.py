"""SCTA Shared Utilities."""

# Re-export commonly used items for convenience
from .auth import (
    load_bearer_token_from_env,
    verify_token_httpbearer,
    verify_token_header,
    create_token_verifier,
    security,
)
from .base_models import (
    CommandRequest,
    HealthResponse,
    ServiceInfo,
    SuccessResponse,
    ErrorResponse,
    get_current_timestamp_iso,
    create_health_response,
    create_service_info,
)
from .persistence import (
    BaseDataStore,
    JSONDataStore,
    AuditLog,
)
from .config import (
    validate_port,
    get_port_from_env,
    ALLOWED_PORT_RANGE,
    FORBIDDEN_PORTS,
)

__all__ = [
    # Authentication
    "load_bearer_token_from_env",
    "verify_token_httpbearer",
    "verify_token_header",
    "create_token_verifier",
    "security",
    # Base Models
    "CommandRequest",
    "HealthResponse",
    "ServiceInfo",
    "SuccessResponse",
    "ErrorResponse",
    "get_current_timestamp_iso",
    "create_health_response",
    "create_service_info",
    # Persistence
    "BaseDataStore",
    "JSONDataStore",
    "AuditLog",
    # Configuration
    "validate_port",
    "get_port_from_env",
    "ALLOWED_PORT_RANGE",
    "FORBIDDEN_PORTS",
]

