# 📱 Metrics Module - PORTIER PAS-6.0
# Performance & Analytics Tracking for Social Media Agent

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class SocialMetrics:
    """Metrics collection and reporting for Social Media Agent"""
    
    def __init__(self):
        self.start_time = time.time()
        
        # Core counters
        self.counters = {
            "posts_created": 0,
            "posts_scheduled": 0,
            "posts_executed": 0,
            "posts_failed": 0,
            "ai_generations": 0,
            "media_uploads": 0,
            "api_requests": 0,
            "errors": 0
        }
        
        # Platform-specific counters
        self.platform_posts = {
            "linkedin": 0,
            "x": 0,
            "facebook": 0,
            "instagram": 0
        }
        
        self.timings = {
            "average_post_time_ms": 0,
            "last_post_time_ms": 0,
            "average_generation_time_ms": 0
        }
        
        # Activity history
        self.post_history: List[Dict[str, Any]] = []
        self.error_log: List[Dict[str, Any]] = []
    
    def increment(self, metric: str, value: int = 1):
        """Increment a counter"""
        if metric in self.counters:
            self.counters[metric] += value
            logger.debug(f"Metric {metric}: {self.counters[metric]}")
    
    def increment_platform(self, platform: str, status: str):
        """Increment platform-specific counter"""
        if platform in self.platform_counters:
            if status == "success":
                self.platform_counters[platform]["sent"] += 1
            else:
                self.platform_counters[platform]["failed"] += 1
    
    def record_post(self, post_data: Dict[str, Any]):
        """Record a post event"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "platforms": post_data.get("platforms", []),
            "text_preview": post_data.get("text", "")[:50],
            "success": post_data.get("success", False)
        }
        
        self.post_history.append(record)
        
        # Keep last 500 posts
        if len(self.post_history) > 500:
            self.post_history = self.post_history[-500:]
    
    def record_error(self, error_type: str, message: str, details: Dict = None):
        """Record an error"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": message,
            "details": details or {}
        }
        
        self.error_log.append(record)
        self.counters["api_errors"] += 1
        
        # Keep last 200 errors
        if len(self.error_log) > 200:
            self.error_log = self.error_log[-200:]
        
        logger.error(f"Error: {error_type} - {message}")
    
    def record_timing(self, metric: str, duration_ms: float):
        """Record timing metric"""
        if metric in self.timings:
            self.timings[f"last_{metric}"] = duration_ms
            
            # Rolling average
            current = self.timings.get(f"average_{metric}", 0)
            count = self.counters["api_requests"]
            if count > 0:
                self.timings[f"average_{metric}"] = (current * (count - 1) + duration_ms) / count
    
    def get_uptime(self) -> Dict[str, Any]:
        """Get uptime info"""
        uptime_seconds = time.time() - self.start_time
        
        return {
            "seconds": int(uptime_seconds),
            "formatted": str(timedelta(seconds=int(uptime_seconds))),
            "started_at": datetime.fromtimestamp(self.start_time).isoformat()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        uptime = self.get_uptime()
        uptime_hours = max(uptime["seconds"] / 3600, 0.001)
        
        return {
            "agent": "opena12_social_media",
            "version": "6.0.0",
            "uptime": uptime,
            "counters": self.counters.copy(),
            "rates": {
                "posts_per_hour": round(self.counters["posts_sent"] / uptime_hours, 2),
                "error_rate": round(
                    self.counters["api_errors"] / max(self.counters["api_requests"], 1) * 100, 2
                )
            }
        }
    
    def get_detailed(self) -> Dict[str, Any]:
        """Get detailed metrics"""
        summary = self.get_summary()
        
        summary["platforms"] = self.platform_counters.copy()
        summary["timings"] = self.timings.copy()
        summary["recent_posts"] = self.post_history[-10:]
        summary["recent_errors"] = self.error_log[-5:]
        
        # Health assessment
        error_rate = self.counters["api_errors"] / max(self.counters["api_requests"], 1)
        summary["health"] = {
            "overall": "healthy" if error_rate < 0.1 else "degraded" if error_rate < 0.3 else "critical",
            "error_rate_percent": round(error_rate * 100, 2)
        }
        
        return summary
    
    def to_prometheus_format(self) -> str:
        """Export Prometheus format"""
        lines = [
            "# HELP opena12_uptime_seconds Agent uptime",
            "# TYPE opena12_uptime_seconds gauge",
            f"opena12_uptime_seconds {self.get_uptime()['seconds']}",
            "",
            "# HELP opena12_posts_total Total posts",
            "# TYPE opena12_posts_total counter",
            f'opena12_posts_total{{status="sent"}} {self.counters["posts_sent"]}',
            f'opena12_posts_total{{status="scheduled"}} {self.counters["posts_scheduled"]}',
            f'opena12_posts_total{{status="failed"}} {self.counters["posts_failed"]}',
            "",
            "# HELP opena12_platform_posts Posts per platform",
            "# TYPE opena12_platform_posts counter"
        ]
        
        for platform, stats in self.platform_counters.items():
            lines.append(f'opena12_platform_posts{{platform="{platform}",status="sent"}} {stats["sent"]}')
            lines.append(f'opena12_platform_posts{{platform="{platform}",status="failed"}} {stats["failed"]}')
        
        lines.extend([
            "",
            "# HELP opena12_ai_generations AI content generations",
            "# TYPE opena12_ai_generations counter",
            f"opena12_ai_generations {self.counters['ai_generations']}"
        ])
        
        return "\n".join(lines)


# Global metrics instance
_metrics: SocialMetrics = None

def get_metrics() -> SocialMetrics:
    """Get or create global metrics instance"""
    global _metrics
    if _metrics is None:
        _metrics = SocialMetrics()
    return _metrics
