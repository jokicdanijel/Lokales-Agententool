"""
SCTA Custom Exceptions
Error types used across the system.
"""


class SCTAException(Exception):
    """Base exception for SCTA system."""

    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR", details: dict | None = None):
        """
        Initialize SCTA exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
        """
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)


class ConfigurationError(SCTAException):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize configuration error."""
        super().__init__(message, "CONFIGURATION_ERROR", details)


class DatabaseError(SCTAException):
    """Raised when database operations fail."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize database error."""
        super().__init__(message, "DATABASE_ERROR", details)


class QueueError(SCTAException):
    """Raised when queue operations fail."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize queue error."""
        super().__init__(message, "QUEUE_ERROR", details)


class AuthenticationError(SCTAException):
    """Raised when authentication fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize authentication error."""
        super().__init__(message, "AUTHENTICATION_ERROR", details)


class AuthorizationError(SCTAException):
    """Raised when authorization fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize authorization error."""
        super().__init__(message, "AUTHORIZATION_ERROR", details)


class ValidationError(SCTAException):
    """Raised when validation fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize validation error."""
        super().__init__(message, "VALIDATION_ERROR", details)


class TaskNotFoundError(SCTAException):
    """Raised when task is not found."""

    def __init__(self, task_id: str, details: dict | None = None):
        """Initialize task not found error."""
        super().__init__(f"Task not found: {task_id}", "TASK_NOT_FOUND", details)


class AgentNotAvailableError(SCTAException):
    """Raised when agent is not available."""

    def __init__(self, agent_id: str, details: dict | None = None):
        """Initialize agent not available error."""
        super().__init__(f"Agent not available: {agent_id}", "AGENT_NOT_AVAILABLE", details)


class DecompositionError(SCTAException):
    """Raised when task decomposition fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize decomposition error."""
        super().__init__(message, "DECOMPOSITION_ERROR", details)


class ExecutionError(SCTAException):
    """Raised when task execution fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize execution error."""
        super().__init__(message, "EXECUTION_ERROR", details)


class TimeoutError(SCTAException):
    """Raised when operation times out."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize timeout error."""
        super().__init__(message, "TIMEOUT_ERROR", details)


class RateLimitError(SCTAException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize rate limit error."""
        super().__init__(message, "RATE_LIMIT_ERROR", details)
