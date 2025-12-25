"""
Lightweight OpenTelemetry bootstrap helper for Portier services.

Designed to be safe to import when OpenTelemetry packages are not installed and
to be idempotent (multiple calls won't re-initialize).

Usage:
    from pkg.observability import init_tracing
    init_tracing(app, service_name="opena20")

Configuration via environment variables (all optional):
  - OTEL_ENABLED / ENABLE_TRACING: 'true' to enable
  - OTEL_EXPORTER_OTLP_ENDPOINT: OTLP HTTP endpoint (default http://localhost:4318/v1/traces)

This module intentionally catches ImportError so it is safe when deps are not present.
"""

from __future__ import annotations

import logging
import os

_logger = logging.getLogger(__name__)
_initialized = False


def _env_flag(name: str) -> bool:
    v = os.environ.get(name)
    if v is None:
        return False
    return str(v).lower() in ("1", "true", "yes", "on")


def init_tracing(
    app: object | None = None,
    service_name: str | None = None,
    *,
    enabled: bool | None = None,
    endpoint: str | None = None,
) -> bool:
    """Initialize OpenTelemetry tracing optionally and idempotently.

    Returns True if tracing was successfully initialized, False otherwise.
    """
    global _initialized
    if _initialized:
        _logger.debug("Tracing already initialized")
        return True

    # Determine whether tracing should be enabled
    if enabled is None:
        enabled = (
            _env_flag("OTEL_ENABLED")
            or _env_flag("ENABLE_TRACING")
            or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT") is not None
        )

    if not enabled:
        _logger.info("OpenTelemetry tracing is disabled (env) — skipping setup")
        return False

    endpoint = endpoint or os.environ.get(
        "OTEL_EXPORTER_OTLP_ENDPOINT", os.environ.get("OTEL_ENDPOINT", "http://localhost:4318/v1/traces")
    )

    try:
        # Lazy import of opentelemetry packages so code is safe when deps are absent
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.logging import LoggingInstrumentor
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError as exc:  # pragma: no cover - environment dependent
        _logger.warning("OpenTelemetry packages not installed; tracing skipped: %s", exc)
        return False

    try:
        service_name = service_name or os.environ.get(
            "OTEL_SERVICE_NAME", os.environ.get("SERVICE_NAME", "portier-service")
        )

        resource = Resource.create(attributes={"service.name": service_name})
        provider = TracerProvider(resource=resource)

        exporter = OTLPSpanExporter(endpoint=endpoint)
        span_processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(span_processor)

        trace.set_tracer_provider(provider)

        # Instrument HTTP clients and FastAPI app (if provided)
        try:
            RequestsInstrumentor().instrument()
        except Exception as e:  # pragma: no cover - defensive
            _logger.warning("Failed to instrument requests: %s", e)

        try:
            LoggingInstrumentor().instrument(set_logging_format=True)
        except Exception as e:  # pragma: no cover - defensive
            _logger.debug("Logging instrumentation not applied: %s", e)

        if app is not None:
            try:
                FastAPIInstrumentor().instrument_app(app)
            except Exception as e:  # pragma: no cover - defensive
                _logger.warning("FastAPI instrumentation failed: %s", e)

        _initialized = True
        _logger.info("OpenTelemetry tracing initialized (endpoint=%s, service=%s)", endpoint, service_name)
        return True

    except Exception as exc:  # pragma: no cover - defensive
        _logger.exception("Failed to initialize OpenTelemetry: %s", exc)
        return False


__all__ = ["init_tracing"]
