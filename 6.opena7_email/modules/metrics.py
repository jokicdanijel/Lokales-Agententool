#!/usr/bin/env python3
"""
📊 Email Metrics Module - PORTIER PAS-6.0
Tracks email processing statistics and performance
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class EmailMetrics:
    """Email agent performance and usage metrics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.stats = {
            "emails_received": 0,
            "emails_sent": 0,
            "ai_replies_generated": 0,
            "classifications_made": 0,
            "auto_responses_sent": 0,
            "errors": 0,
            "api_calls": 0
        }
        
        # Load persistent stats if available
        self.stats_file = Path("data/email_metrics.json")
        self.load_stats()
        
        logger.info("📊 EmailMetrics initialized")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        uptime = time.time() - self.start_time
        
        return {
            "agent": "opena7_email",
            "version": "6.0.0",
            "uptime_seconds": round(uptime, 2),
            "uptime_formatted": self._format_uptime(uptime),
            "statistics": self.stats.copy(),
            "performance": self._calculate_performance(),
            "status": "healthy" if self.stats["errors"] < 10 else "degraded",
            "timestamp": datetime.now().isoformat()
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human readable format"""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def _calculate_performance(self) -> Dict[str, float]:
        """Calculate performance metrics"""
        uptime_hours = (time.time() - self.start_time) / 3600
        
        if uptime_hours == 0:
            return {"emails_per_hour": 0.0, "ai_replies_per_hour": 0.0, "error_rate": 0.0}
        
        emails_per_hour = (self.stats["emails_received"] + self.stats["emails_sent"]) / uptime_hours
        ai_replies_per_hour = self.stats["ai_replies_generated"] / uptime_hours
        
        total_operations = sum(self.stats.values())
        error_rate = (self.stats["errors"] / total_operations * 100) if total_operations > 0 else 0.0
        
        return {
            "emails_per_hour": round(emails_per_hour, 2),
            "ai_replies_per_hour": round(ai_replies_per_hour, 2),
            "error_rate_percent": round(error_rate, 2)
        }
    
    def increment_stat(self, stat_name: str, amount: int = 1):
        """Increment a statistic counter"""
        if stat_name in self.stats:
            self.stats[stat_name] += amount
            self.save_stats()
        else:
            logger.warning(f"⚠️ Unknown stat: {stat_name}")
    
    def record_email_received(self):
        """Record an email received"""
        self.increment_stat("emails_received")
    
    def record_email_sent(self):
        """Record an email sent"""
        self.increment_stat("emails_sent")
    
    def record_ai_reply(self):
        """Record an AI reply generated"""
        self.increment_stat("ai_replies_generated")
    
    def record_classification(self):
        """Record an email classification"""
        self.increment_stat("classifications_made")
    
    def record_auto_response(self):
        """Record an auto response sent"""
        self.increment_stat("auto_responses_sent")
    
    def record_error(self):
        """Record an error"""
        self.increment_stat("errors")
    
    def record_api_call(self):
        """Record an API call"""
        self.increment_stat("api_calls")
    
    def load_stats(self):
        """Load stats from persistent storage"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    saved_stats = json.load(f)
                    self.stats.update(saved_stats)
                logger.info("📊 Metrics loaded from disk")
        except Exception as e:
            logger.warning(f"⚠️ Could not load metrics: {e}")
    
    def save_stats(self):
        """Save stats to persistent storage"""
        try:
            self.stats_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.warning(f"⚠️ Could not save metrics: {e}")
    
    def reset_stats(self):
        """Reset all statistics"""
        self.stats = {key: 0 for key in self.stats.keys()}
        self.start_time = time.time()
        self.save_stats()
        logger.info("📊 Metrics reset")
    
    def get_daily_summary(self) -> Dict[str, Any]:
        """Get daily activity summary"""
        # Mock implementation - would track daily stats in real system
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "emails_processed": self.stats["emails_received"] + self.stats["emails_sent"],
            "ai_interactions": self.stats["ai_replies_generated"],
            "success_rate": self._calculate_success_rate(),
            "peak_hour": self._get_peak_hour(),
            "summary": "Email agent operating normally"
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate percentage"""
        total_operations = sum(self.stats.values())
        if total_operations == 0:
            return 100.0
        
        successful_operations = total_operations - self.stats["errors"]
        return round((successful_operations / total_operations) * 100, 2)
    
    def _get_peak_hour(self) -> str:
        """Get peak activity hour (mock)"""
        # In real implementation, would track hourly activity
        return datetime.now().strftime("%H:00")