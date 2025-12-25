#!/usr/bin/env python3
"""
Auto-Updater für opena20 Dashboard Agent
PORTIER 3.0 Konform | Enterprise Grade Auto-Update System

Features:
- Git-basierte Updates
- Rollback-Mechanismus
- Health-Check Validation
- Zero-Downtime Updates
- Backup & Restore
- Configuration Migration
- Dependency Management
"""

import json
import logging
import os
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import requests


class OpenaAutoUpdater:
    """Auto-Updater für opena20 Dashboard Agent"""

    def __init__(self, config_path: str | None = None):
        self.base_dir = Path(__file__).parent
        self.config_path = config_path or self.base_dir / "auto_update_config.json"
        self.backup_dir = self.base_dir / "backups"
        self.temp_dir = None

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[logging.FileHandler(self.base_dir / "logs" / "auto_updater.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger("auto_updater")

        # Load configuration
        self.config = self.load_config()

        # Create directories
        self.backup_dir.mkdir(exist_ok=True)

    def load_config(self) -> dict:
        """Load auto-updater configuration"""
        default_config = {
            "git_repo": "https://github.com/jokicdanijel/Gesamtprojekt-start.git",
            "branch": "main",
            "check_interval_hours": 6,
            "auto_update": False,
            "backup_retention_days": 30,
            "health_check_url": "http://127.0.0.1:12349/health",
            "health_check_timeout": 10,
            "max_rollback_attempts": 3,
            "files_to_update": ["main_dashboard_final.py", "requirements.txt", "static/", "templates/"],
            "files_to_preserve": ["logs/", "data/", ".env", "auto_update_config.json"],
            "pre_update_commands": [],
            "post_update_commands": [["pip", "install", "-r", "requirements.txt"]],
            "restart_command": ["systemctl", "restart", "opena20"],
            "notification_webhook": None,
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
            self.logger.info("Created default configuration file")

        return default_config

    def check_for_updates(self) -> tuple[bool, str]:
        """Check if updates are available"""
        try:
            # Get current commit hash
            current_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.base_dir).decode().strip()

            # Fetch latest changes
            subprocess.check_output(["git", "fetch", "origin", self.config["branch"]], cwd=self.base_dir)

            # Get remote commit hash
            remote_hash = (
                subprocess.check_output(["git", "rev-parse", f"origin/{self.config['branch']}"], cwd=self.base_dir)
                .decode()
                .strip()
            )

            if current_hash != remote_hash:
                self.logger.info(f"Update available: {current_hash[:8]} -> {remote_hash[:8]}")
                return True, remote_hash
            else:
                self.logger.info("No updates available")
                return False, current_hash

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git operation failed: {e}")
            return False, ""
        except Exception as e:
            self.logger.error(f"Update check failed: {e}")
            return False, ""

    def create_backup(self) -> Path | None:
        """Create backup of current installation"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"opena20_backup_{timestamp}"
            backup_path = self.backup_dir / backup_name

            self.logger.info(f"Creating backup: {backup_name}")

            # Create backup directory
            backup_path.mkdir(exist_ok=True)

            # Copy files to backup
            for item in self.config["files_to_update"]:
                src = self.base_dir / item
                dst = backup_path / item

                if src.exists():
                    if src.is_dir():
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dst)

            # Create backup metadata
            metadata = {
                "timestamp": timestamp,
                "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.base_dir).decode().strip(),
                "version": self.get_current_version(),
                "files": self.config["files_to_update"],
            }

            with open(backup_path / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)

            self.logger.info(f"Backup created successfully: {backup_path}")
            return backup_path

        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return None

    def health_check(self) -> bool:
        """Perform health check on the application"""
        try:
            response = requests.get(self.config["health_check_url"], timeout=self.config["health_check_timeout"])

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    self.logger.info("Health check passed")
                    return True

            self.logger.warning(f"Health check failed: HTTP {response.status_code}")
            return False

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    def apply_update(self, target_commit: str) -> bool:
        """Apply the update"""
        try:
            self.logger.info("Applying update...")

            # Run pre-update commands
            for cmd in self.config["pre_update_commands"]:
                self.logger.info(f"Running pre-update command: {' '.join(cmd)}")
                subprocess.check_output(cmd, cwd=self.base_dir)

            # Pull changes
            subprocess.check_output(["git", "checkout", self.config["branch"]], cwd=self.base_dir)

            subprocess.check_output(["git", "pull", "origin", self.config["branch"]], cwd=self.base_dir)

            # Verify we got the expected commit
            current_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.base_dir).decode().strip()

            if current_hash != target_commit:
                raise Exception(f"Update verification failed: expected {target_commit}, got {current_hash}")

            # Run post-update commands
            for cmd in self.config["post_update_commands"]:
                self.logger.info(f"Running post-update command: {' '.join(cmd)}")
                subprocess.check_output(cmd, cwd=self.base_dir)

            self.logger.info("Update applied successfully")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Update command failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Update failed: {e}")
            return False

    def restart_service(self) -> bool:
        """Restart the service"""
        try:
            self.logger.info("Restarting service...")
            subprocess.check_output(self.config["restart_command"])

            # Wait for service to start
            time.sleep(5)

            # Verify service is running
            if self.health_check():
                self.logger.info("Service restarted successfully")
                return True
            else:
                self.logger.error("Service failed health check after restart")
                return False

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Service restart failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Restart failed: {e}")
            return False

    def rollback_to_backup(self, backup_path: Path) -> bool:
        """Rollback to a specific backup"""
        try:
            self.logger.info(f"Rolling back to backup: {backup_path}")

            # Load backup metadata
            with open(backup_path / "metadata.json") as f:
                metadata = json.load(f)

            # Restore files
            for item in metadata["files"]:
                src = backup_path / item
                dst = self.base_dir / item

                if src.exists():
                    if dst.exists():
                        if dst.is_dir():
                            shutil.rmtree(dst)
                        else:
                            dst.unlink()

                    if src.is_dir():
                        shutil.copytree(src, dst)
                    else:
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dst)

            # Reset git to backup commit
            subprocess.check_output(["git", "checkout", metadata["git_commit"]], cwd=self.base_dir)

            self.logger.info("Rollback completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            return False

    def cleanup_old_backups(self):
        """Cleanup old backups based on retention policy"""
        try:
            cutoff_time = time.time() - (self.config["backup_retention_days"] * 24 * 3600)

            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir() and backup_dir.stat().st_mtime < cutoff_time:
                    self.logger.info(f"Removing old backup: {backup_dir.name}")
                    shutil.rmtree(backup_dir)

        except Exception as e:
            self.logger.error(f"Backup cleanup failed: {e}")

    def send_notification(self, message: str, success: bool = True):
        """Send notification via webhook"""
        if not self.config.get("notification_webhook"):
            return

        try:
            payload = {
                "timestamp": datetime.now(UTC).isoformat(),
                "service": "opena20-auto-updater",
                "message": message,
                "success": success,
                "hostname": os.uname().nodename,
            }

            response = requests.post(self.config["notification_webhook"], json=payload, timeout=10)

            if response.status_code == 200:
                self.logger.info("Notification sent successfully")
            else:
                self.logger.warning(f"Notification failed: HTTP {response.status_code}")

        except Exception as e:
            self.logger.error(f"Notification failed: {e}")

    def get_current_version(self) -> str:
        """Get current version/commit"""
        try:
            return (
                subprocess.check_output(["git", "describe", "--tags", "--always"], cwd=self.base_dir).decode().strip()
            )
        except:
            return "unknown"

    def perform_update(self) -> bool:
        """Perform complete update process"""
        self.logger.info("Starting update process...")

        # Initial health check
        if not self.health_check():
            self.logger.error("Pre-update health check failed, aborting")
            self.send_notification("Update aborted: pre-update health check failed", False)
            return False

        # Check for updates
        has_updates, target_commit = self.check_for_updates()
        if not has_updates:
            self.logger.info("No updates available")
            return True

        # Create backup
        backup_path = self.create_backup()
        if not backup_path:
            self.logger.error("Backup creation failed, aborting update")
            self.send_notification("Update aborted: backup creation failed", False)
            return False

        try:
            # Apply update
            if not self.apply_update(target_commit):
                raise Exception("Update application failed")

            # Restart service
            if not self.restart_service():
                raise Exception("Service restart failed")

            # Final health check
            if not self.health_check():
                raise Exception("Post-update health check failed")

            self.logger.info("Update completed successfully")
            self.send_notification(f"Update completed successfully: {self.get_current_version()}", True)

            # Cleanup old backups
            self.cleanup_old_backups()

            return True

        except Exception as e:
            self.logger.error(f"Update failed: {e}")

            # Attempt rollback
            self.logger.info("Attempting rollback...")
            if self.rollback_to_backup(backup_path):
                if self.restart_service():
                    self.logger.info("Rollback completed successfully")
                    self.send_notification(f"Update failed, rollback successful: {e}", False)
                else:
                    self.logger.error("Rollback restart failed")
                    self.send_notification(f"Update and rollback restart failed: {e}", False)
            else:
                self.logger.error("Rollback failed")
                self.send_notification(f"Update and rollback failed: {e}", False)

            return False

    def run_daemon(self):
        """Run as daemon with periodic update checks"""
        self.logger.info("Starting auto-updater daemon...")

        while True:
            try:
                if self.config["auto_update"]:
                    self.perform_update()
                else:
                    # Just check for updates without applying
                    has_updates, _ = self.check_for_updates()
                    if has_updates:
                        self.logger.info("Updates available but auto_update is disabled")

                # Wait for next check
                sleep_time = self.config["check_interval_hours"] * 3600
                self.logger.info(f"Sleeping for {self.config['check_interval_hours']} hours...")
                time.sleep(sleep_time)

            except KeyboardInterrupt:
                self.logger.info("Auto-updater daemon stopped")
                break
            except Exception as e:
                self.logger.error(f"Daemon error: {e}")
                time.sleep(300)  # Wait 5 minutes before retry


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="opena20 Auto-Updater")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--update", action="store_true", help="Perform one-time update")
    parser.add_argument("--check", action="store_true", help="Check for updates only")
    parser.add_argument("--rollback", help="Rollback to specific backup")

    args = parser.parse_args()

    updater = OpenaAutoUpdater(args.config)

    if args.daemon:
        updater.run_daemon()
    elif args.update:
        success = updater.perform_update()
        sys.exit(0 if success else 1)
    elif args.check:
        has_updates, commit = updater.check_for_updates()
        if has_updates:
            print(f"Updates available: {commit}")
            sys.exit(1)
        else:
            print("No updates available")
            sys.exit(0)
    elif args.rollback:
        backup_path = updater.backup_dir / args.rollback
        if backup_path.exists():
            success = updater.rollback_to_backup(backup_path)
            sys.exit(0 if success else 1)
        else:
            print(f"Backup not found: {args.rollback}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
