# 🔐 Metrics Module - PORTIER PAS-6.0
# Performance & Health Tracking for Unlock Master Agent

import logging
import time
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class UnlockMetrics:
    """Metrics collection and reporting for Unlock Master Agent"""

    def __init__(self):
        self.start_time = time.time()

        # Core counters
        self.counters = {
            "commands_received": 0,
            "permissions_granted": 0,
            "permissions_revoked": 0,
            "permission_checks": 0,
            "permission_denials": 0,
            "ai_analyses": 0,
            "command_errors": 0,
            "api_requests": 0,
        }

        # Timing metrics
        self.timings = {"average_check_time_ms": 0, "average_grant_time_ms": 0, "last_command_time_ms": 0}

        # Status tracking
        self.status = {
            "store_healthy": True,
            "audit_healthy": True,
            "ai_engine_connected": False,
            "cache_hit_rate": 0.0,
        }

        # Rate tracking
        self.rate_windows = {"checks_per_minute": [], "grants_per_minute": []}

        logger.info("✅ Unlock Metrics initialized")

    def increment(self, metric: str, value: int = 1):
        """Increment a counter metric"""
        if metric in self.counters:
            self.counters[metric] += value
            logger.debug(f"Metric {metric}: {self.counters[metric]}")

    def record_timing(self, operation: str, duration_ms: float):
        """Record operation timing"""
        timing_key = f"average_{operation}_time_ms"
        if timing_key in self.timings:
            current = self.timings[timing_key]
            # Rolling average
            self.timings[timing_key] = (current + duration_ms) / 2
        self.timings["last_command_time_ms"] = duration_ms

    def update_status(self, component: str, status: bool):
        """Update component status"""
        if component in self.status:
            self.status[component] = status

    def get_uptime(self) -> dict[str, Any]:
        """Get agent uptime information"""
        uptime_seconds = time.time() - self.start_time

        return {
            "seconds": int(uptime_seconds),
            "formatted": str(timedelta(seconds=int(uptime_seconds))),
            "started_at": datetime.fromtimestamp(self.start_time).isoformat(),
        }

    def get_summary(self) -> dict[str, Any]:
        """Get metrics summary"""
        uptime = self.get_uptime()

        # Calculate rates
        uptime_hours = max(uptime["seconds"] / 3600, 0.001)
        checks_per_hour = self.counters["permission_checks"] / uptime_hours
        grants_per_hour = self.counters["permissions_granted"] / uptime_hours

        # Calculate denial rate
        total_checks = self.counters["permission_checks"]
        denial_rate = self.counters["permission_denials"] / total_checks * 100 if total_checks > 0 else 0

        return {
            "agent": "opena11_unlock",
            "version": "6.0.0",
            "uptime": uptime,
            "counters": self.counters.copy(),
            "timings": self.timings.copy(),
            "status": self.status.copy(),
            "rates": {
                "checks_per_hour": round(checks_per_hour, 2),
                "grants_per_hour": round(grants_per_hour, 2),
                "denial_rate_percent": round(denial_rate, 2),
                "error_rate_percent": round(
                    self.counters["command_errors"] / max(self.counters["commands_received"], 1) * 100, 2
                ),
            },
        }

    def to_prometheus_format(self) -> str:
        """Export metrics in Prometheus format"""
        lines = [
            "# HELP opena11_uptime_seconds Agent uptime in seconds",
            "# TYPE opena11_uptime_seconds gauge",
            f"opena11_uptime_seconds {self.get_uptime()['seconds']}",
            "",
            "# HELP opena11_permissions_total Total permission operations",
            "# TYPE opena11_permissions_total counter",
            f'opena11_permissions_total{{type="granted"}} {self.counters["permissions_granted"]}',
            f'opena11_permissions_total{{type="revoked"}} {self.counters["permissions_revoked"]}',
            f'opena11_permissions_total{{type="checks"}} {self.counters["permission_checks"]}',
            f'opena11_permissions_total{{type="denials"}} {self.counters["permission_denials"]}',
            "",
            "# HELP opena11_commands_total Total commands received",
            "# TYPE opena11_commands_total counter",
            f"opena11_commands_total {self.counters['commands_received']}",
            "",
            "# HELP opena11_errors_total Total errors",
            "# TYPE opena11_errors_total counter",
            f"opena11_errors_total {self.counters['command_errors']}",
            "",
            "# HELP opena11_ai_analyses_total AI analyses performed",
            "# TYPE opena11_ai_analyses_total counter",
            f"opena11_ai_analyses_total {self.counters['ai_analyses']}",
            "",
            "# HELP opena11_check_duration_ms Average permission check duration",
            "# TYPE opena11_check_duration_ms gauge",
            f"opena11_check_duration_ms {self.timings['average_check_time_ms']:.2f}",
        ]

        return "\n".join(lines)


# Global metrics instance
_metrics: UnlockMetrics = None


def get_metrics() -> UnlockMetrics:
    """Get or create global metrics instance"""
    global _metrics
    if _metrics is None:
        _metrics = UnlockMetrics()
    return _metrics
