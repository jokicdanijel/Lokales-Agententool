"""
Prometheus Metrics - Monitoring Integration
Stellt Metrics-Endpoints für alle Services bereit (Prometheus-kompatibel).

Features:
- Request Counter (Gesamt, Success, Failures)
- Latency Histogram
- Active Connections Gauge
- Service-spezifische Labels
- /metrics Endpoint (Prometheus Scraping)
"""

import time

from fastapi import Response
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Gauge, Histogram, generate_latest

# -------------------------------------------------------------------
# Registry (ermöglicht mehrere Instanzen)
# -------------------------------------------------------------------
registry = CollectorRegistry()

# -------------------------------------------------------------------
# Metrics Definitions
# -------------------------------------------------------------------

# Request Counter
request_counter = Counter(
    "service_requests_total",
    "Total number of requests",
    ["service", "endpoint", "status"],
    registry=registry,
)

# Latency Histogram
request_latency = Histogram(
    "service_request_duration_seconds",
    "Request latency in seconds",
    ["service", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
    registry=registry,
)

# Active Connections
active_connections = Gauge(
    "service_active_connections",
    "Number of active connections",
    ["service"],
    registry=registry,
)

# Health Status (1 = healthy, 0 = unhealthy)
health_status = Gauge(
    "service_health_status",
    "Health status of service (1=healthy, 0=unhealthy)",
    ["service"],
    registry=registry,
)

# Archiv Entries Counter
archiv_entries = Counter(
    "archiv_entries_total",
    "Total number of archiv entries created",
    ["kind"],  # CMD or RESP
    registry=registry,
)

# Agent Manager Stats
agent_count = Gauge(
    "agent_manager_agents_total",
    "Total number of registered agents",
    ["status"],  # ready, busy, error, offline
    registry=registry,
)

# Memory System Stats
memory_entries = Gauge(
    "memory_system_entries_total",
    "Total number of memory entries",
    ["agent_id"],
    registry=registry,
)


# -------------------------------------------------------------------
# Metrics Helper Class
# -------------------------------------------------------------------
class ServiceMetrics:
    """
    Helper-Klasse für Service-Metrics.
    Verwendung in FastAPI-Services via Middleware.
    """

    def __init__(self, service_name: str):
        self.service_name = service_name

    def record_request(self, endpoint: str, status: str, latency: float):
        """
        Zeichnet einen Request auf.

        Args:
            endpoint: Endpoint-Name (z.B. "/health", "/dispatch")
            status: Status (z.B. "success", "error", "timeout")
            latency: Latenz in Sekunden
        """
        request_counter.labels(service=self.service_name, endpoint=endpoint, status=status).inc()

        request_latency.labels(service=self.service_name, endpoint=endpoint).observe(latency)

    def inc_active_connections(self):
        """Erhöht Active Connections Counter"""
        active_connections.labels(service=self.service_name).inc()

    def dec_active_connections(self):
        """Verringert Active Connections Counter"""
        active_connections.labels(service=self.service_name).dec()

    def set_health(self, healthy: bool):
        """
        Setzt Health-Status.

        Args:
            healthy: True = healthy, False = unhealthy
        """
        health_status.labels(service=self.service_name).set(1 if healthy else 0)

    def record_archiv_entry(self, kind: str):
        """
        Zeichnet Archiv-Entry auf.

        Args:
            kind: "CMD" oder "RESP"
        """
        archiv_entries.labels(kind=kind).inc()

    def update_agent_stats(self, ready: int, busy: int, error: int, offline: int):
        """
        Aktualisiert Agent-Manager-Stats.

        Args:
            ready: Anzahl Agents im Status READY
            busy: Anzahl Agents im Status BUSY
            error: Anzahl Agents im Status ERROR
            offline: Anzahl Agents im Status OFFLINE
        """
        agent_count.labels(status="ready").set(ready)
        agent_count.labels(status="busy").set(busy)
        agent_count.labels(status="error").set(error)
        agent_count.labels(status="offline").set(offline)

    def update_memory_stats(self, agent_id: str, entries: int):
        """
        Aktualisiert Memory-System-Stats.

        Args:
            agent_id: Agent-ID
            entries: Anzahl Einträge
        """
        memory_entries.labels(agent_id=agent_id).set(entries)


# -------------------------------------------------------------------
# Metrics Endpoint (FastAPI Route)
# -------------------------------------------------------------------
def get_metrics_endpoint():
    """
    Generiert /metrics Endpoint für Prometheus Scraping.

    Usage in FastAPI:
        from monitoring import get_metrics_endpoint

        @app.get("/metrics")
        async def metrics():
            return get_metrics_endpoint()

    Returns:
        Response mit Prometheus-Metrics
    """
    return Response(content=generate_latest(registry), media_type=CONTENT_TYPE_LATEST)


# -------------------------------------------------------------------
# Middleware (Optional - für automatisches Tracking)
# -------------------------------------------------------------------
class MetricsMiddleware:
    """
    FastAPI Middleware für automatisches Request-Tracking.

    Usage:
        from monitoring import MetricsMiddleware

        app = FastAPI()
        app.add_middleware(MetricsMiddleware, service_name="my_service")
    """

    def __init__(self, app, service_name: str):
        self.app = app
        self.metrics = ServiceMetrics(service_name)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Track active connection
        self.metrics.inc_active_connections()

        start_time = time.time()
        status = "success"

        try:
            await self.app(scope, receive, send)
        except Exception:
            status = "error"
            raise
        finally:
            latency = time.time() - start_time
            endpoint = scope.get("path", "unknown")

            self.metrics.record_request(endpoint, status, latency)
            self.metrics.dec_active_connections()


# -------------------------------------------------------------------
# Example Integration
# -------------------------------------------------------------------
"""
# In main_dashboard.py oder agent_server.py:

from monitoring import ServiceMetrics, get_metrics_endpoint

# Metrics initialisieren
metrics = ServiceMetrics("dashboard")

# Health-Status setzen
@app.on_event("startup")
async def startup():
    metrics.set_health(True)

# Metrics-Endpoint
@app.get("/metrics")
async def metrics_endpoint():
    return get_metrics_endpoint()

# Manuelles Tracking (optional)
@app.post("/command")
async def command(request: CommandRequest):
    start = time.time()
    try:
        result = await execute_command(request)
        metrics.record_request("/command", "success", time.time() - start)
        return result
    except Exception as e:
        metrics.record_request("/command", "error", time.time() - start)
        raise
"""
