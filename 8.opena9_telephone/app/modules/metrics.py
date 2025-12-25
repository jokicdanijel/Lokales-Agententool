# 📊 Metrics Module - PORTIER PAS-6.0
# Performance & Health Tracking for Telephone Agent

import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class TelephonyMetrics:
    """Metrics collection and reporting for Telephone Agent"""

    def __init__(self):
        self.start_time = time.time()

        # Core counters
        self.counters = {
            "calls_made": 0,
            "calls_answered": 0,
            "calls_missed": 0,
            "calls_failed": 0,
            "voice_responses_generated": 0,
            "ivr_flows_created": 0,
            "transcriptions_completed": 0,
            "api_requests": 0,
            "api_errors": 0,
        }

        # Timing metrics
        self.timings = {
            "average_call_duration_seconds": 0,
            "total_call_duration_seconds": 0,
            "average_response_time_ms": 0,
            "last_api_response_ms": 0,
        }

        # Status tracking
        self.status = {
            "twilio_connected": False,
            "sip_gateway_active": False,
            "asterisk_connected": False,
            "openai_connected": False,
            "current_active_calls": 0,
        }

        # Rate limiting
        self.rate_limits = {
            "calls_per_minute": 0,
            "calls_per_minute_limit": int(os.getenv("CALLS_PER_MINUTE_LIMIT", "60")),
            "voice_generations_per_hour": 0,
            "voice_generations_limit": int(os.getenv("VOICE_GENS_PER_HOUR_LIMIT", "100")),
        }

        # History for trending
        self.call_history: list[dict[str, Any]] = []
        self.error_log: list[dict[str, Any]] = []

    def increment(self, metric: str, value: int = 1):
        """Increment a counter metric"""
        if metric in self.counters:
            self.counters[metric] += value
            logger.debug(f"Metric {metric} incremented to {self.counters[metric]}")

    def record_call(self, call_data: dict[str, Any]):
        """Record a call event"""
        call_record = {
            "timestamp": datetime.now().isoformat(),
            "call_id": call_data.get("call_id", "unknown"),
            "direction": call_data.get("direction", "outbound"),
            "duration_seconds": call_data.get("duration", 0),
            "status": call_data.get("status", "completed"),
        }

        self.call_history.append(call_record)

        # Keep last 1000 calls
        if len(self.call_history) > 1000:
            self.call_history = self.call_history[-1000:]

        # Update totals
        self.timings["total_call_duration_seconds"] += call_data.get("duration", 0)

        # Recalculate average
        total_calls = self.counters["calls_made"] + self.counters["calls_answered"]
        if total_calls > 0:
            self.timings["average_call_duration_seconds"] = self.timings["total_call_duration_seconds"] / total_calls

    def record_error(self, error_type: str, error_message: str, details: dict = None):
        """Record an error event"""
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": error_message,
            "details": details or {},
        }

        self.error_log.append(error_record)
        self.counters["api_errors"] += 1

        # Keep last 500 errors
        if len(self.error_log) > 500:
            self.error_log = self.error_log[-500:]

        logger.error(f"Error recorded: {error_type} - {error_message}")

    def record_api_response(self, response_time_ms: float):
        """Record API response timing"""
        self.timings["last_api_response_ms"] = response_time_ms
        self.counters["api_requests"] += 1

        # Rolling average
        current_avg = self.timings["average_response_time_ms"]
        total_requests = self.counters["api_requests"]

        self.timings["average_response_time_ms"] = (
            current_avg * (total_requests - 1) + response_time_ms
        ) / total_requests

    def update_status(self, component: str, status: bool):
        """Update component status"""
        if component in self.status:
            self.status[component] = status

    def set_active_calls(self, count: int):
        """Set current active call count"""
        self.status["current_active_calls"] = count

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
        calls_per_hour = (self.counters["calls_made"] + self.counters["calls_answered"]) / uptime_hours

        return {
            "agent": "opena9_telephone",
            "version": "6.0.0",
            "uptime": uptime,
            "counters": self.counters.copy(),
            "timings": self.timings.copy(),
            "status": self.status.copy(),
            "rates": {
                "calls_per_hour": round(calls_per_hour, 2),
                "error_rate": round(self.counters["api_errors"] / max(self.counters["api_requests"], 1) * 100, 2),
            },
            "rate_limits": self.rate_limits.copy(),
        }

    def get_detailed_metrics(self) -> dict[str, Any]:
        """Get detailed metrics including history"""
        summary = self.get_summary()

        # Add recent history
        summary["recent_calls"] = self.call_history[-20:]
        summary["recent_errors"] = self.error_log[-10:]

        # Add health indicators
        summary["health"] = {
            "overall": "healthy" if self.counters["api_errors"] < 10 else "degraded",
            "services": {
                "telephony": "up" if self.status["twilio_connected"] or self.status["sip_gateway_active"] else "down",
                "ai_engine": "up" if self.status["openai_connected"] else "down",
                "pbx": "up" if self.status["asterisk_connected"] else "unknown",
            },
        }

        return summary

    def check_rate_limits(self) -> dict[str, Any]:
        """Check current rate limit status"""
        calls_remaining = self.rate_limits["calls_per_minute_limit"] - self.rate_limits["calls_per_minute"]
        voice_remaining = self.rate_limits["voice_generations_limit"] - self.rate_limits["voice_generations_per_hour"]

        return {
            "calls": {
                "current": self.rate_limits["calls_per_minute"],
                "limit": self.rate_limits["calls_per_minute_limit"],
                "remaining": max(0, calls_remaining),
                "exceeded": calls_remaining < 0,
            },
            "voice_generations": {
                "current": self.rate_limits["voice_generations_per_hour"],
                "limit": self.rate_limits["voice_generations_limit"],
                "remaining": max(0, voice_remaining),
                "exceeded": voice_remaining < 0,
            },
        }

    def reset_rate_limits(self):
        """Reset rate limit counters (call periodically)"""
        self.rate_limits["calls_per_minute"] = 0
        self.rate_limits["voice_generations_per_hour"] = 0

    def to_prometheus_format(self) -> str:
        """Export metrics in Prometheus format"""
        lines = [
            "# HELP opena9_uptime_seconds Agent uptime in seconds",
            "# TYPE opena9_uptime_seconds gauge",
            f"opena9_uptime_seconds {self.get_uptime()['seconds']}",
            "",
            "# HELP opena9_calls_total Total number of calls",
            "# TYPE opena9_calls_total counter",
            f'opena9_calls_total{{type="made"}} {self.counters["calls_made"]}',
            f'opena9_calls_total{{type="answered"}} {self.counters["calls_answered"]}',
            f'opena9_calls_total{{type="missed"}} {self.counters["calls_missed"]}',
            f'opena9_calls_total{{type="failed"}} {self.counters["calls_failed"]}',
            "",
            "# HELP opena9_voice_responses_total Voice responses generated",
            "# TYPE opena9_voice_responses_total counter",
            f"opena9_voice_responses_total {self.counters['voice_responses_generated']}",
            "",
            "# HELP opena9_active_calls Current active calls",
            "# TYPE opena9_active_calls gauge",
            f"opena9_active_calls {self.status['current_active_calls']}",
            "",
            "# HELP opena9_api_response_ms Average API response time",
            "# TYPE opena9_api_response_ms gauge",
            f"opena9_api_response_ms {self.timings['average_response_time_ms']:.2f}",
        ]

        return "\n".join(lines)

    # Alias methods for compatibility with main.py
    def log_command(self, command: str) -> None:
        """Log command execution (alias for increment)"""
        self.increment("api_requests")
        logger.debug(f"Command logged: {command}")

    def log_success(self, command: str) -> None:
        """Log successful command"""
        logger.debug(f"Command succeeded: {command}")

    def log_error(self, command: str, error: str = "") -> None:
        """Log command error"""
        self.record_error("command_error", f"Command '{command}' failed: {error}")

    def log_ai_function(self, action: str) -> None:
        """Log AI function usage"""
        self.increment("voice_responses_generated")
        logger.debug(f"AI function logged: {action}")

    async def get_current_stats(self) -> dict[str, Any]:
        """Get current statistics (async wrapper)"""
        return self.get_summary()

    async def get_comprehensive_metrics(self) -> dict[str, Any]:
        """Get comprehensive metrics (async wrapper)"""
        return self.get_detailed_metrics()

    async def save_stats(self) -> None:
        """Save statistics to file (placeholder for persistence)"""
        logger.info("Saving metrics statistics...")
        # In production, this would persist to file/database


# Global metrics instance
_metrics: TelephonyMetrics = None


# Alias for backward compatibility
Metrics = TelephonyMetrics


def get_metrics() -> TelephonyMetrics:
    """Get or create global metrics instance"""
    global _metrics
    if _metrics is None:
        _metrics = TelephonyMetrics()
    return _metrics
