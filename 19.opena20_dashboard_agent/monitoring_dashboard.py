#!/usr/bin/env python3
"""
Monitoring Dashboard für opena20 Agent
PORTIER 3.0 Enterprise Monitoring & Alerting System

Features:
- Real-time Metrics Collection
- Prometheus Integration
- Health Status Aggregation
- Performance Monitoring
- Alert Management
- System Resource Tracking
"""

import asyncio
import json
import logging
import os
import sqlite3
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import aiohttp
import psutil
from prometheus_client import Counter, Gauge, Histogram, start_http_server


@dataclass
class AgentMetrics:
    """Agent metrics data structure"""

    agent_id: str
    port: int
    status: str
    response_time: float
    last_check: str
    error_count: int
    success_count: int
    cpu_usage: float
    memory_usage: float
    uptime: float


@dataclass
class SystemMetrics:
    """System metrics data structure"""

    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: dict[str, int]
    process_count: int
    load_average: list[float]


class PrometheusMetrics:
    """Prometheus metrics collector"""

    def __init__(self):
        # Counters
        self.http_requests_total = Counter(
            "opena20_http_requests_total", "Total HTTP requests", ["agent", "method", "status_code"]
        )

        self.agent_errors_total = Counter("opena20_agent_errors_total", "Total agent errors", ["agent", "error_type"])

        # Gauges
        self.agent_status = Gauge("opena20_agent_status", "Agent status (1=healthy, 0=unhealthy)", ["agent"])

        self.agent_response_time = Gauge(
            "opena20_agent_response_time_seconds", "Agent response time in seconds", ["agent"]
        )

        self.system_cpu_percent = Gauge("opena20_system_cpu_percent", "System CPU usage percentage")

        self.system_memory_percent = Gauge("opena20_system_memory_percent", "System memory usage percentage")

        self.system_disk_percent = Gauge("opena20_system_disk_percent", "System disk usage percentage")

        # Histograms
        self.agent_response_time_histogram = Histogram(
            "opena20_agent_response_time_histogram", "Agent response time histogram", ["agent"]
        )


class MonitoringDashboard:
    """Main monitoring dashboard class"""

    def __init__(self, config_path: str | None = None):
        self.base_dir = Path(__file__).parent
        self.config_path = config_path or self.base_dir / "monitoring_config.json"
        self.db_path = self.base_dir / "data" / "monitoring.db"

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[logging.FileHandler(self.base_dir / "logs" / "monitoring.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger("monitoring")

        # Load configuration
        self.config = self.load_config()

        # Initialize metrics
        self.metrics = PrometheusMetrics()

        # Agent configuration
        self.agents = self.config.get("agents", [])

        # Create database
        self.init_database()

        # Start Prometheus server
        if self.config.get("prometheus", {}).get("enabled", True):
            prometheus_port = self.config.get("prometheus", {}).get("port", 9090)
            try:
                start_http_server(prometheus_port)
                self.logger.info(f"Prometheus metrics server started on port {prometheus_port}")
            except Exception as e:
                self.logger.error(f"Failed to start Prometheus server: {e}")

    def load_config(self) -> dict:
        """Load monitoring configuration"""
        default_config = {
            "check_interval": 30,
            "prometheus": {"enabled": True, "port": 9090},
            "agents": [
                {"id": "opena1", "name": "Koordinator", "port": 12344, "endpoint": "/health"},
                {"id": "opena2", "name": "Archivator", "port": 12345, "endpoint": "/health"},
                {"id": "opena3", "name": "OpenWebUI", "port": 12347, "endpoint": "/health"},
                {"id": "opena20", "name": "Dashboard", "port": 12349, "endpoint": "/health"},
            ],
            "alerts": {
                "enabled": True,
                "webhook_url": None,
                "thresholds": {
                    "response_time": 5.0,
                    "cpu_usage": 80.0,
                    "memory_usage": 85.0,
                    "disk_usage": 90.0,
                    "error_rate": 10.0,
                },
            },
            "retention": {"metrics_days": 30, "logs_days": 7},
        }

        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
        else:
            # Create default config
            with open(self.config_path, "w") as f:
                json.dump(default_config, f, indent=2)
            self.logger.info("Created default monitoring configuration")

        return default_config

    def init_database(self):
        """Initialize SQLite database for metrics storage"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS agent_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        agent_id TEXT NOT NULL,
                        status TEXT NOT NULL,
                        response_time REAL NOT NULL,
                        error_count INTEGER DEFAULT 0,
                        success_count INTEGER DEFAULT 0,
                        cpu_usage REAL DEFAULT 0,
                        memory_usage REAL DEFAULT 0
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        cpu_percent REAL NOT NULL,
                        memory_percent REAL NOT NULL,
                        disk_usage_percent REAL NOT NULL,
                        process_count INTEGER NOT NULL,
                        load_average TEXT NOT NULL
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        alert_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        message TEXT NOT NULL,
                        resolved BOOLEAN DEFAULT FALSE
                    )
                """
                )

                # Create indexes
                conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_metrics_timestamp ON agent_metrics(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)")

                conn.commit()

        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")

    async def check_agent_health(self, agent: dict) -> AgentMetrics:
        """Check health of a single agent"""
        agent_id = agent["id"]
        port = agent["port"]
        endpoint = agent.get("endpoint", "/health")
        url = f"http://127.0.0.1:{port}{endpoint}"

        start_time = time.time()

        try:
            timeout = aiohttp.ClientTimeout(total=5.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    response_time = time.time() - start_time

                    if response.status == 200:
                        data = await response.json()
                        status = "healthy" if data.get("status") == "ok" else "degraded"

                        # Update Prometheus metrics
                        self.metrics.agent_status.labels(agent=agent_id).set(1)
                        self.metrics.agent_response_time.labels(agent=agent_id).set(response_time)
                        self.metrics.agent_response_time_histogram.labels(agent=agent_id).observe(response_time)

                        return AgentMetrics(
                            agent_id=agent_id,
                            port=port,
                            status=status,
                            response_time=response_time,
                            last_check=datetime.now(UTC).isoformat(),
                            error_count=0,
                            success_count=1,
                            cpu_usage=0.0,  # Would need process-specific monitoring
                            memory_usage=0.0,
                            uptime=0.0,
                        )
                    else:
                        raise Exception(f"HTTP {response.status}")

        except Exception as e:
            response_time = time.time() - start_time
            self.logger.warning(f"Agent {agent_id} health check failed: {e}")

            # Update Prometheus metrics
            self.metrics.agent_status.labels(agent=agent_id).set(0)
            self.metrics.agent_errors_total.labels(agent=agent_id, error_type="health_check").inc()

            return AgentMetrics(
                agent_id=agent_id,
                port=port,
                status="unhealthy",
                response_time=response_time,
                last_check=datetime.now(UTC).isoformat(),
                error_count=1,
                success_count=0,
                cpu_usage=0.0,
                memory_usage=0.0,
                uptime=0.0,
            )

    def collect_system_metrics(self) -> SystemMetrics:
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100

            # Network I/O
            network_io = psutil.net_io_counters()._asdict()

            # Process count
            process_count = len(psutil.pids())

            # Load average (Linux/Unix only)
            try:
                load_average = list(os.getloadavg())
            except:
                load_average = [0.0, 0.0, 0.0]

            # Update Prometheus metrics
            self.metrics.system_cpu_percent.set(cpu_percent)
            self.metrics.system_memory_percent.set(memory_percent)
            self.metrics.system_disk_percent.set(disk_percent)

            return SystemMetrics(
                timestamp=datetime.now(UTC).isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage_percent=disk_percent,
                network_io=network_io,
                process_count=process_count,
                load_average=load_average,
            )

        except Exception as e:
            self.logger.error(f"System metrics collection failed: {e}")
            return SystemMetrics(
                timestamp=datetime.now(UTC).isoformat(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                network_io={},
                process_count=0,
                load_average=[0.0, 0.0, 0.0],
            )

    def store_metrics(self, agent_metrics: list[AgentMetrics], system_metrics: SystemMetrics):
        """Store metrics in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Store agent metrics
                for metrics in agent_metrics:
                    conn.execute(
                        """
                        INSERT INTO agent_metrics
                        (timestamp, agent_id, status, response_time, error_count, success_count, cpu_usage, memory_usage)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            metrics.last_check,
                            metrics.agent_id,
                            metrics.status,
                            metrics.response_time,
                            metrics.error_count,
                            metrics.success_count,
                            metrics.cpu_usage,
                            metrics.memory_usage,
                        ),
                    )

                # Store system metrics
                conn.execute(
                    """
                    INSERT INTO system_metrics
                    (timestamp, cpu_percent, memory_percent, disk_usage_percent, process_count, load_average)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        system_metrics.timestamp,
                        system_metrics.cpu_percent,
                        system_metrics.memory_percent,
                        system_metrics.disk_usage_percent,
                        system_metrics.process_count,
                        json.dumps(system_metrics.load_average),
                    ),
                )

                conn.commit()

        except Exception as e:
            self.logger.error(f"Metrics storage failed: {e}")

    def check_alerts(self, agent_metrics: list[AgentMetrics], system_metrics: SystemMetrics):
        """Check for alert conditions"""
        if not self.config.get("alerts", {}).get("enabled", True):
            return

        thresholds = self.config.get("alerts", {}).get("thresholds", {})
        alerts = []

        # Check agent response times
        for metrics in agent_metrics:
            if metrics.response_time > thresholds.get("response_time", 5.0):
                alerts.append(
                    {
                        "type": "agent_slow_response",
                        "severity": "warning",
                        "message": f"Agent {metrics.agent_id} response time {metrics.response_time:.2f}s exceeds threshold",
                    }
                )

            if metrics.status == "unhealthy":
                alerts.append(
                    {
                        "type": "agent_unhealthy",
                        "severity": "critical",
                        "message": f"Agent {metrics.agent_id} is unhealthy",
                    }
                )

        # Check system metrics
        if system_metrics.cpu_percent > thresholds.get("cpu_usage", 80.0):
            alerts.append(
                {
                    "type": "high_cpu_usage",
                    "severity": "warning",
                    "message": f"High CPU usage: {system_metrics.cpu_percent:.1f}%",
                }
            )

        if system_metrics.memory_percent > thresholds.get("memory_usage", 85.0):
            alerts.append(
                {
                    "type": "high_memory_usage",
                    "severity": "warning",
                    "message": f"High memory usage: {system_metrics.memory_percent:.1f}%",
                }
            )

        if system_metrics.disk_usage_percent > thresholds.get("disk_usage", 90.0):
            alerts.append(
                {
                    "type": "high_disk_usage",
                    "severity": "critical",
                    "message": f"High disk usage: {system_metrics.disk_usage_percent:.1f}%",
                }
            )

        # Process alerts
        for alert in alerts:
            self.process_alert(alert)

    def process_alert(self, alert: dict):
        """Process and store alert"""
        try:
            timestamp = datetime.now(UTC).isoformat()

            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO alerts (timestamp, alert_type, severity, message)
                    VALUES (?, ?, ?, ?)
                """,
                    (timestamp, alert["type"], alert["severity"], alert["message"]),
                )
                conn.commit()

            self.logger.warning(f"ALERT [{alert['severity'].upper()}]: {alert['message']}")

            # Send webhook notification
            webhook_url = self.config.get("alerts", {}).get("webhook_url")
            if webhook_url:
                asyncio.create_task(self.send_webhook_alert(webhook_url, alert))

        except Exception as e:
            self.logger.error(f"Alert processing failed: {e}")

    async def send_webhook_alert(self, webhook_url: str, alert: dict):
        """Send alert via webhook"""
        try:
            payload = {
                "timestamp": datetime.now(UTC).isoformat(),
                "alert": alert,
                "service": "opena20-monitoring",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        self.logger.info("Alert webhook sent successfully")
                    else:
                        self.logger.error(f"Alert webhook failed: HTTP {response.status}")

        except Exception as e:
            self.logger.error(f"Webhook alert failed: {e}")

    def cleanup_old_data(self):
        """Cleanup old metrics and logs based on retention policy"""
        try:
            retention = self.config.get("retention", {})
            metrics_days = retention.get("metrics_days", 30)

            cutoff_date = datetime.now(UTC) - timedelta(days=metrics_days)
            cutoff_timestamp = cutoff_date.isoformat()

            with sqlite3.connect(self.db_path) as conn:
                # Cleanup old agent metrics
                conn.execute("DELETE FROM agent_metrics WHERE timestamp < ?", (cutoff_timestamp,))

                # Cleanup old system metrics
                conn.execute("DELETE FROM system_metrics WHERE timestamp < ?", (cutoff_timestamp,))

                # Cleanup resolved alerts
                alert_cutoff = datetime.now(UTC) - timedelta(days=7)
                conn.execute("DELETE FROM alerts WHERE timestamp < ? AND resolved = TRUE", (alert_cutoff.isoformat(),))

                conn.commit()

            self.logger.info(f"Cleaned up metrics older than {metrics_days} days")

        except Exception as e:
            self.logger.error(f"Data cleanup failed: {e}")

    def get_dashboard_data(self) -> dict:
        """Get current dashboard data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get latest agent metrics
                agent_data = {}
                for agent in self.agents:
                    cursor = conn.execute(
                        """
                        SELECT * FROM agent_metrics
                        WHERE agent_id = ?
                        ORDER BY timestamp DESC LIMIT 1
                    """,
                        (agent["id"],),
                    )

                    row = cursor.fetchone()
                    if row:
                        agent_data[agent["id"]] = {"status": row[3], "response_time": row[4], "last_check": row[2]}
                    else:
                        agent_data[agent["id"]] = {"status": "unknown", "response_time": 0.0, "last_check": "never"}

                # Get latest system metrics
                cursor = conn.execute("SELECT * FROM system_metrics ORDER BY timestamp DESC LIMIT 1")
                system_row = cursor.fetchone()

                system_data = {}
                if system_row:
                    system_data = {
                        "cpu_percent": system_row[2],
                        "memory_percent": system_row[3],
                        "disk_usage_percent": system_row[4],
                        "process_count": system_row[5],
                        "load_average": json.loads(system_row[6]),
                        "timestamp": system_row[1],
                    }

                # Get recent alerts
                cursor = conn.execute(
                    """
                    SELECT * FROM alerts
                    WHERE resolved = FALSE
                    ORDER BY timestamp DESC LIMIT 10
                """
                )

                alerts = []
                for row in cursor.fetchall():
                    alerts.append(
                        {"id": row[0], "timestamp": row[1], "type": row[2], "severity": row[3], "message": row[4]}
                    )

                return {
                    "agents": agent_data,
                    "system": system_data,
                    "alerts": alerts,
                    "timestamp": datetime.now(UTC).isoformat(),
                }

        except Exception as e:
            self.logger.error(f"Dashboard data retrieval failed: {e}")
            return {"error": str(e)}

    async def monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info("Starting monitoring loop...")

        while True:
            try:
                # Check all agents
                agent_tasks = [self.check_agent_health(agent) for agent in self.agents]
                agent_metrics = await asyncio.gather(*agent_tasks, return_exceptions=True)

                # Filter out exceptions
                valid_metrics = [m for m in agent_metrics if isinstance(m, AgentMetrics)]

                # Collect system metrics
                system_metrics = self.collect_system_metrics()

                # Store metrics
                self.store_metrics(valid_metrics, system_metrics)

                # Check alerts
                self.check_alerts(valid_metrics, system_metrics)

                # Cleanup old data (every hour)
                if time.time() % 3600 < self.config.get("check_interval", 30):
                    self.cleanup_old_data()

                # Log summary
                healthy_agents = sum(1 for m in valid_metrics if m.status == "healthy")
                total_agents = len(self.agents)

                self.logger.info(f"Monitoring cycle complete: {healthy_agents}/{total_agents} agents healthy")

                # Wait for next cycle
                await asyncio.sleep(self.config.get("check_interval", 30))

            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(10)

    def run(self):
        """Run monitoring dashboard"""
        try:
            asyncio.run(self.monitoring_loop())
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Monitoring failed: {e}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="opena20 Monitoring Dashboard")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--dashboard", action="store_true", help="Show current dashboard data")

    args = parser.parse_args()

    monitor = MonitoringDashboard(args.config)

    if args.dashboard:
        data = monitor.get_dashboard_data()
        print(json.dumps(data, indent=2))
    else:
        monitor.run()


if __name__ == "__main__":
    main()
