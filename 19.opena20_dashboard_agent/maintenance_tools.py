#!/usr/bin/env python3
"""
Maintenance Tools für opena20 Dashboard Agent
PORTIER 3.0 Enterprise Maintenance & Operations Suite

Features:
- Database Maintenance & Optimization
- Log Rotation & Cleanup
- Performance Analysis
- Health Reports
- Configuration Validation
- System Diagnostics
"""

import argparse
import gzip
import json
import logging
import shutil
import sqlite3
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path


class MaintenanceTools:
    """Maintenance tools for opena20 system"""

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or Path(__file__).parent
        self.logs_dir = self.base_dir / "logs"
        self.data_dir = self.base_dir / "data"
        self.backups_dir = self.base_dir / "backups"

        # Setup logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
        self.logger = logging.getLogger("maintenance")

        # Ensure directories exist
        for directory in [self.logs_dir, self.data_dir, self.backups_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def rotate_logs(self, max_size_mb: int = 100, max_files: int = 10) -> dict:
        """Rotate log files"""
        self.logger.info("Starting log rotation...")
        rotated_files = []
        errors = []

        try:
            for log_file in self.logs_dir.glob("*.log"):
                try:
                    # Check file size
                    size_mb = log_file.stat().st_size / (1024 * 1024)

                    if size_mb > max_size_mb:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        rotated_name = f"{log_file.stem}_{timestamp}.log.gz"
                        rotated_path = self.logs_dir / rotated_name

                        # Compress and rotate
                        with open(log_file, "rb") as f_in:
                            with gzip.open(rotated_path, "wb") as f_out:
                                shutil.copyfileobj(f_in, f_out)

                        # Clear original file
                        log_file.write_text("")

                        rotated_files.append(str(rotated_path))
                        self.logger.info(f"Rotated log: {log_file.name} -> {rotated_name}")

                except Exception as e:
                    error_msg = f"Failed to rotate {log_file.name}: {e}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)

            # Cleanup old rotated logs
            rotated_logs = list(self.logs_dir.glob("*.log.gz"))
            if len(rotated_logs) > max_files:
                # Sort by modification time and remove oldest
                rotated_logs.sort(key=lambda x: x.stat().st_mtime)
                for old_log in rotated_logs[:-max_files]:
                    old_log.unlink()
                    self.logger.info(f"Removed old rotated log: {old_log.name}")

            return {
                "status": "success",
                "rotated_files": rotated_files,
                "errors": errors,
                "total_rotated": len(rotated_files),
            }

        except Exception as e:
            error_msg = f"Log rotation failed: {e}"
            self.logger.error(error_msg)
            return {"status": "error", "message": error_msg}

    def vacuum_databases(self) -> dict:
        """Vacuum and optimize SQLite databases"""
        self.logger.info("Starting database maintenance...")
        results = []

        try:
            for db_file in self.data_dir.glob("*.db"):
                try:
                    # Get database size before
                    size_before = db_file.stat().st_size

                    # Connect and vacuum
                    with sqlite3.connect(db_file) as conn:
                        conn.execute("PRAGMA optimize")
                        conn.execute("VACUUM")
                        conn.execute("ANALYZE")
                        conn.commit()

                    # Get database size after
                    size_after = db_file.stat().st_size
                    savings = size_before - size_after

                    results.append(
                        {
                            "database": db_file.name,
                            "size_before_mb": round(size_before / (1024 * 1024), 2),
                            "size_after_mb": round(size_after / (1024 * 1024), 2),
                            "savings_mb": round(savings / (1024 * 1024), 2),
                            "status": "success",
                        }
                    )

                    self.logger.info(f"Optimized {db_file.name}: {savings} bytes saved")

                except Exception as e:
                    error_msg = f"Failed to optimize {db_file.name}: {e}"
                    results.append({"database": db_file.name, "status": "error", "error": error_msg})
                    self.logger.error(error_msg)

            return {
                "status": "success",
                "databases": results,
                "total_savings_mb": round(sum(r.get("savings_mb", 0) for r in results), 2),
            }

        except Exception as e:
            error_msg = f"Database maintenance failed: {e}"
            self.logger.error(error_msg)
            return {"status": "error", "message": error_msg}

    def analyze_performance(self, days: int = 7) -> dict:
        """Analyze system performance over specified period"""
        self.logger.info(f"Analyzing performance for last {days} days...")

        try:
            # Analyze monitoring database if it exists
            monitoring_db = self.data_dir / "monitoring.db"
            if not monitoring_db.exists():
                return {"status": "error", "message": "Monitoring database not found"}

            cutoff_date = datetime.now(UTC) - timedelta(days=days)
            cutoff_timestamp = cutoff_date.isoformat()

            with sqlite3.connect(monitoring_db) as conn:
                # Agent performance
                cursor = conn.execute(
                    """
                    SELECT agent_id,
                           AVG(response_time) as avg_response_time,
                           MAX(response_time) as max_response_time,
                           COUNT(*) as total_checks,
                           SUM(CASE WHEN status = 'healthy' THEN 1 ELSE 0 END) as healthy_checks
                    FROM agent_metrics
                    WHERE timestamp > ?
                    GROUP BY agent_id
                """,
                    (cutoff_timestamp,),
                )

                agent_performance = {}
                for row in cursor.fetchall():
                    agent_id, avg_rt, max_rt, total, healthy = row
                    uptime_percent = (healthy / total * 100) if total > 0 else 0

                    agent_performance[agent_id] = {
                        "avg_response_time": round(avg_rt, 3),
                        "max_response_time": round(max_rt, 3),
                        "uptime_percent": round(uptime_percent, 2),
                        "total_checks": total,
                        "healthy_checks": healthy,
                    }

                # System performance
                cursor = conn.execute(
                    """
                    SELECT AVG(cpu_percent) as avg_cpu,
                           MAX(cpu_percent) as max_cpu,
                           AVG(memory_percent) as avg_memory,
                           MAX(memory_percent) as max_memory,
                           AVG(disk_usage_percent) as avg_disk,
                           MAX(disk_usage_percent) as max_disk
                    FROM system_metrics
                    WHERE timestamp > ?
                """,
                    (cutoff_timestamp,),
                )

                system_row = cursor.fetchone()
                system_performance = {}
                if system_row:
                    system_performance = {
                        "cpu": {"average": round(system_row[0] or 0, 2), "peak": round(system_row[1] or 0, 2)},
                        "memory": {"average": round(system_row[2] or 0, 2), "peak": round(system_row[3] or 0, 2)},
                        "disk": {"average": round(system_row[4] or 0, 2), "peak": round(system_row[5] or 0, 2)},
                    }

                # Alert statistics
                cursor = conn.execute(
                    """
                    SELECT alert_type, severity, COUNT(*) as count
                    FROM alerts
                    WHERE timestamp > ?
                    GROUP BY alert_type, severity
                """,
                    (cutoff_timestamp,),
                )

                alert_stats = {}
                for row in cursor.fetchall():
                    alert_type, severity, count = row
                    if alert_type not in alert_stats:
                        alert_stats[alert_type] = {}
                    alert_stats[alert_type][severity] = count

            return {
                "status": "success",
                "period_days": days,
                "agent_performance": agent_performance,
                "system_performance": system_performance,
                "alert_statistics": alert_stats,
                "analysis_timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            error_msg = f"Performance analysis failed: {e}"
            self.logger.error(error_msg)
            return {"status": "error", "message": error_msg}

    def generate_health_report(self) -> dict:
        """Generate comprehensive health report"""
        self.logger.info("Generating health report...")

        try:
            report = {
                "timestamp": datetime.now(UTC).isoformat(),
                "system_info": {},
                "disk_usage": {},
                "process_info": {},
                "network_connectivity": {},
                "database_health": {},
                "log_analysis": {},
                "recommendations": [],
            }

            # System information
            try:
                import psutil

                report["system_info"] = {
                    "cpu_count": psutil.cpu_count(),
                    "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                    "disk_total_gb": round(psutil.disk_usage("/").total / (1024**3), 2),
                    "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                    "python_version": sys.version,
                }
            except ImportError:
                self.logger.warning("psutil not available for system info")

            # Disk usage analysis
            for directory in [self.logs_dir, self.data_dir, self.backups_dir]:
                if directory.exists():
                    total_size = sum(f.stat().st_size for f in directory.rglob("*") if f.is_file())
                    file_count = len(list(directory.rglob("*")))

                    report["disk_usage"][directory.name] = {
                        "size_mb": round(total_size / (1024 * 1024), 2),
                        "file_count": file_count,
                    }

            # Database health
            for db_file in self.data_dir.glob("*.db"):
                try:
                    with sqlite3.connect(db_file) as conn:
                        cursor = conn.execute("PRAGMA integrity_check")
                        integrity = cursor.fetchone()[0]

                        cursor = conn.execute("PRAGMA page_count")
                        page_count = cursor.fetchone()[0]

                        cursor = conn.execute("PRAGMA page_size")
                        page_size = cursor.fetchone()[0]

                        report["database_health"][db_file.name] = {
                            "integrity": integrity,
                            "size_mb": round((page_count * page_size) / (1024 * 1024), 2),
                            "pages": page_count,
                        }

                except Exception as e:
                    report["database_health"][db_file.name] = {"error": str(e)}

            # Log analysis
            for log_file in self.logs_dir.glob("*.log"):
                try:
                    with open(log_file) as f:
                        lines = f.readlines()

                    error_count = sum(1 for line in lines if "ERROR" in line)
                    warning_count = sum(1 for line in lines if "WARNING" in line)

                    report["log_analysis"][log_file.name] = {
                        "total_lines": len(lines),
                        "error_count": error_count,
                        "warning_count": warning_count,
                        "size_mb": round(log_file.stat().st_size / (1024 * 1024), 2),
                    }

                except Exception as e:
                    report["log_analysis"][log_file.name] = {"error": str(e)}

            # Generate recommendations
            recommendations = []

            # Check disk usage
            for dir_name, info in report["disk_usage"].items():
                if info["size_mb"] > 1000:  # 1GB
                    recommendations.append(
                        f"Consider cleaning up {dir_name} directory (currently {info['size_mb']} MB)"
                    )

            # Check log errors
            for log_name, info in report["log_analysis"].items():
                if isinstance(info, dict) and info.get("error_count", 0) > 100:
                    recommendations.append(f"High error count in {log_name}: {info['error_count']} errors")
                if isinstance(info, dict) and info.get("size_mb", 0) > 100:
                    recommendations.append(f"Large log file {log_name}: {info['size_mb']} MB - consider rotation")

            # Check database health
            for db_name, info in report["database_health"].items():
                if isinstance(info, dict) and info.get("integrity") != "ok":
                    recommendations.append(f"Database integrity issue in {db_name}")
                if isinstance(info, dict) and info.get("size_mb", 0) > 500:
                    recommendations.append(
                        f"Large database {db_name}: {info['size_mb']} MB - consider archiving old data"
                    )

            report["recommendations"] = recommendations

            return {"status": "success", "report": report}

        except Exception as e:
            error_msg = f"Health report generation failed: {e}"
            self.logger.error(error_msg)
            return {"status": "error", "message": error_msg}

    def validate_configuration(self) -> dict:
        """Validate system configuration files"""
        self.logger.info("Validating configuration...")

        validation_results = {"status": "success", "files": {}, "errors": [], "warnings": []}

        # Configuration files to check
        config_files = {
            "monitoring_config.json": {"required": True, "schema": "monitoring"},
            "auto_update_config.json": {"required": False, "schema": "auto_update"},
            ".env": {"required": True, "schema": "env"},
            "agent_registry.json": {"required": False, "schema": "registry"},
        }

        for config_file, info in config_files.items():
            file_path = self.base_dir / config_file
            result = {
                "exists": file_path.exists(),
                "readable": False,
                "valid_json": False,
                "schema_valid": False,
                "issues": [],
            }

            try:
                if file_path.exists():
                    result["readable"] = True

                    if config_file.endswith(".json"):
                        # Validate JSON syntax
                        with open(file_path) as f:
                            data = json.load(f)
                        result["valid_json"] = True

                        # Basic schema validation
                        if info["schema"] == "monitoring":
                            required_keys = ["check_interval", "agents", "alerts"]
                            missing_keys = [key for key in required_keys if key not in data]
                            if missing_keys:
                                result["issues"].append(f"Missing required keys: {missing_keys}")
                            else:
                                result["schema_valid"] = True

                        elif info["schema"] == "auto_update":
                            required_keys = ["git_repo", "branch", "check_interval_hours"]
                            missing_keys = [key for key in required_keys if key not in data]
                            if missing_keys:
                                result["issues"].append(f"Missing required keys: {missing_keys}")
                            else:
                                result["schema_valid"] = True

                    elif config_file == ".env":
                        # Validate .env file
                        with open(file_path) as f:
                            content = f.read()

                        required_vars = ["BEARER_TOKEN", "OPENAI_API_KEY"]
                        missing_vars = []

                        for var in required_vars:
                            if f"{var}=" not in content:
                                missing_vars.append(var)

                        if missing_vars:
                            result["issues"].append(f"Missing environment variables: {missing_vars}")
                        else:
                            result["schema_valid"] = True

                else:
                    if info["required"]:
                        result["issues"].append("Required file is missing")
                        validation_results["errors"].append(f"Missing required file: {config_file}")

            except json.JSONDecodeError as e:
                result["issues"].append(f"Invalid JSON syntax: {e}")
                validation_results["errors"].append(f"JSON error in {config_file}: {e}")
            except Exception as e:
                result["issues"].append(f"Validation error: {e}")
                validation_results["errors"].append(f"Error validating {config_file}: {e}")

            validation_results["files"][config_file] = result

        # Set overall status
        if validation_results["errors"]:
            validation_results["status"] = "error"
        elif any(result["issues"] for result in validation_results["files"].values()):
            validation_results["status"] = "warning"

        return validation_results

    def cleanup_temp_files(self) -> dict:
        """Clean up temporary files and caches"""
        self.logger.info("Cleaning up temporary files...")

        try:
            cleaned_files = []
            total_size = 0

            # Python cache files
            for cache_dir in self.base_dir.rglob("__pycache__"):
                if cache_dir.is_dir():
                    size = sum(f.stat().st_size for f in cache_dir.rglob("*") if f.is_file())
                    shutil.rmtree(cache_dir)
                    cleaned_files.append(str(cache_dir))
                    total_size += size

            # Temporary files
            temp_patterns = ["*.tmp", "*.temp", "*.bak", "*.swp", "*~"]
            for pattern in temp_patterns:
                for temp_file in self.base_dir.rglob(pattern):
                    if temp_file.is_file():
                        size = temp_file.stat().st_size
                        temp_file.unlink()
                        cleaned_files.append(str(temp_file))
                        total_size += size

            return {
                "status": "success",
                "cleaned_files": cleaned_files,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": len(cleaned_files),
            }

        except Exception as e:
            error_msg = f"Temp file cleanup failed: {e}"
            self.logger.error(error_msg)
            return {"status": "error", "message": error_msg}

    def backup_configuration(self) -> dict:
        """Create backup of all configuration files"""
        self.logger.info("Creating configuration backup...")

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"config_backup_{timestamp}"
            backup_path = self.backups_dir / backup_name
            backup_path.mkdir(exist_ok=True)

            backed_up_files = []

            # Configuration files to backup
            config_patterns = ["*.json", "*.conf", "*.cfg", ".env", "*.yml", "*.yaml"]

            for pattern in config_patterns:
                for config_file in self.base_dir.glob(pattern):
                    if config_file.is_file():
                        dest_file = backup_path / config_file.name
                        shutil.copy2(config_file, dest_file)
                        backed_up_files.append(config_file.name)

            # Create backup manifest
            manifest = {
                "timestamp": datetime.now(UTC).isoformat(),
                "backup_name": backup_name,
                "files": backed_up_files,
                "total_files": len(backed_up_files),
            }

            with open(backup_path / "manifest.json", "w") as f:
                json.dump(manifest, f, indent=2)

            return {
                "status": "success",
                "backup_path": str(backup_path),
                "backup_name": backup_name,
                "files_backed_up": backed_up_files,
                "total_files": len(backed_up_files),
            }

        except Exception as e:
            error_msg = f"Configuration backup failed: {e}"
            self.logger.error(error_msg)
            return {"status": "error", "message": error_msg}


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="opena20 Maintenance Tools")
    parser.add_argument("--base-dir", help="Base directory path")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Log rotation command
    rotate_parser = subparsers.add_parser("rotate-logs", help="Rotate log files")
    rotate_parser.add_argument("--max-size", type=int, default=100, help="Maximum log size in MB")
    rotate_parser.add_argument("--max-files", type=int, default=10, help="Maximum rotated files to keep")

    # Database maintenance command
    subparsers.add_parser("vacuum-db", help="Vacuum and optimize databases")

    # Performance analysis command
    perf_parser = subparsers.add_parser("analyze-performance", help="Analyze system performance")
    perf_parser.add_argument("--days", type=int, default=7, help="Days to analyze")

    # Health report command
    subparsers.add_parser("health-report", help="Generate health report")

    # Configuration validation command
    subparsers.add_parser("validate-config", help="Validate configuration files")

    # Cleanup command
    subparsers.add_parser("cleanup", help="Clean up temporary files")

    # Backup command
    subparsers.add_parser("backup-config", help="Backup configuration files")

    # Full maintenance command
    subparsers.add_parser("full-maintenance", help="Run full maintenance routine")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize maintenance tools
    base_dir = Path(args.base_dir) if args.base_dir else None
    maintenance = MaintenanceTools(base_dir)

    # Execute command
    result = None

    if args.command == "rotate-logs":
        result = maintenance.rotate_logs(args.max_size, args.max_files)
    elif args.command == "vacuum-db":
        result = maintenance.vacuum_databases()
    elif args.command == "analyze-performance":
        result = maintenance.analyze_performance(args.days)
    elif args.command == "health-report":
        result = maintenance.generate_health_report()
    elif args.command == "validate-config":
        result = maintenance.validate_configuration()
    elif args.command == "cleanup":
        result = maintenance.cleanup_temp_files()
    elif args.command == "backup-config":
        result = maintenance.backup_configuration()
    elif args.command == "full-maintenance":
        # Run full maintenance routine
        results = {}
        results["log_rotation"] = maintenance.rotate_logs()
        results["database_vacuum"] = maintenance.vacuum_databases()
        results["temp_cleanup"] = maintenance.cleanup_temp_files()
        results["config_backup"] = maintenance.backup_configuration()
        results["config_validation"] = maintenance.validate_configuration()
        results["health_report"] = maintenance.generate_health_report()

        result = {
            "status": "success",
            "maintenance_results": results,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    # Output result
    if result:
        print(json.dumps(result, indent=2))

        # Exit with appropriate code
        if result.get("status") == "error":
            sys.exit(1)
        elif result.get("status") == "warning":
            sys.exit(2)
        else:
            sys.exit(0)
    else:
        print("No result generated")
        sys.exit(1)


if __name__ == "__main__":
    main()
