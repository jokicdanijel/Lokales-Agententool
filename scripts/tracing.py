"""Tracing bootstrap for repository scripts.

Provides a simple `init_tracing(service_name: str)` helper that:
- configures an OpenTelemetry TracerProvider
- tries to export via OTLP (endpoint from OTEL_EXPORTER_OTLP_ENDPOINT or default http://localhost:4318)
- falls back to ConsoleSpanExporter if OTLP exporter is unavailable
- instruments `requests` automatically

Usage:
    from scripts.tracing import init_tracing
    init_tracing("my-service")
"""

from __future__ import annotations

import logging
import os

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
except Exception:  # pragma: no cover - best-effort import
    trace = None


LOG = logging.getLogger(__name__)


def init_tracing(service_name: str) -> None:
    """Initialise tracing for a script.

    The function is resilient when OpenTelemetry packages are not installed (no-op).
    It prefers OTLP exporter and falls back to console exporter.
    """
    if trace is None:
        LOG.debug("OpenTelemetry packages not available; tracing disabled")
        return

    # Avoid double initialization
    if isinstance(trace.get_tracer_provider(), TracerProvider):
        LOG.debug("TracerProvider already configured")
        return

    # Resource metadata
    resource = Resource.create({"service.name": service_name})

    provider = TracerProvider(resource=resource)

    # Try to read OTLP endpoint from env, otherwise default to localhost (AI Toolkit default)
    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

    try:
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
        LOG.info("Tracing initialized with OTLP endpoint %s", otlp_endpoint)
    except Exception as exc:  # pragma: no cover - runtime fallback
        LOG.warning("Failed to initialize OTLP exporter (%s), falling back to console exporter", exc)
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)

    # Instrument requests for simple http spans (used by preflight)
    try:
        RequestsInstrumentor().instrument()
        LOG.info("Requests instrumentation enabled")
    except Exception:
        LOG.debug("Requests instrumentation not available or already initialized")
