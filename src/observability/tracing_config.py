"""
OpenTelemetry Tracing Configuration for ELION Hyper-Dashboard
Enables multi-agent workflow visualization and performance monitoring.
"""

import logging
import os

logger = logging.getLogger(__name__)

# Environment defaults
OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")  # gRPC
OTLP_HTTP_ENDPOINT = os.getenv("OTLP_HTTP_ENDPOINT", "http://localhost:4318")  # HTTP
ENABLE_TRACING = os.getenv("ENABLE_TRACING", "true").lower() == "true"
ENABLE_SENSITIVE_DATA = os.getenv("ENABLE_SENSITIVE_DATA", "true").lower() == "true"
TRACE_SAMPLE_RATE = float(os.getenv("TRACE_SAMPLE_RATE", "1.0"))  # 0.0 - 1.0


def setup_tracing() -> bool:
    """
    Initialize OpenTelemetry tracing for the application.

    Returns:
        bool: True if tracing initialized successfully, False otherwise
    """
    if not ENABLE_TRACING:
        logger.info("ℹ️  Tracing disabled by environment variable")
        return False

    try:
        from agent_framework.observability import setup_observability

        setup_observability(otlp_endpoint=OTLP_ENDPOINT, enable_sensitive_data=ENABLE_SENSITIVE_DATA)
        logger.info("✅ OpenTelemetry Tracing initialized")
        logger.info(f"   - OTLP gRPC: {OTLP_ENDPOINT}")
        logger.info(f"   - Sensitive data: {'enabled' if ENABLE_SENSITIVE_DATA else 'disabled'}")
        logger.info(f"   - Sample rate: {TRACE_SAMPLE_RATE}")
        return True
    except ImportError:
        logger.warning("⚠️  agent-framework not installed (pip install agent-framework)")
        return False
    except Exception as e:
        logger.error(f"❌ Tracing setup failed: {e}")
        return False


def get_tracer(name: str):
    """
    Get a tracer instance for the given module name.

    Args:
        name: Module name for tracer identification

    Returns:
        Tracer instance or None if tracing not available
    """
    try:
        from opentelemetry import trace

        return trace.get_tracer(name)
    except ImportError:
        return None


class TracingContext:
    """Context manager for manual span creation."""

    def __init__(self, name: str, attributes: dict | None = None):
        self.name = name
        self.attributes = attributes or {}
        self.span = None
        self.tracer = get_tracer(__name__)

    def __enter__(self):
        if self.tracer:
            self.span = self.tracer.start_span(self.name)
            for key, value in self.attributes.items():
                self.span.set_attribute(key, value)
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            if exc_type:
                self.span.set_attribute("error", True)
                self.span.set_attribute("error.type", exc_type.__name__)
            self.span.end()
