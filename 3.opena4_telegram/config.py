"""
Configuration loader for opena4 (Telegram Agent)
Port-Policy enforcement, Secrets management, Environment setup
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional


logger = logging.getLogger("opena4.config")


class PortierConfig:
    """Central configuration for opena4 with Port-Policy enforcement"""

    def __init__(self, env_file: Optional[Path] = None):
        """Initialize configuration from environment and .env file"""
        self.base_dir = Path(os.getenv("PORTIER_BASE_DIR", Path.cwd()))
        self.env_file = env_file or self.base_dir / ".env"
        
        # Load .env file if exists
        if self.env_file.exists():
            self._load_env_file()
        
        # Service configuration
        self.service_name = "opena4"
        self.port = self._get_port()
        self.host = os.getenv("PORTIER_HOST", "127.0.0.1")
        
        # Port-Policy enforcement (12344-12399 erlaubt, 8080 verboten)
        self.allowed_ports = list(range(12344, 12400))
        self.forbidden_ports = [8080]
        
        self._enforce_port_policy()
        
        # Telegram configuration (ENV-only secrets)
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_allowed_users = self._parse_user_ids(os.getenv("TELEGRAM_ALLOWED_USERS", ""))
        self.telegram_webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL", "")
        
        # Archivator/Coordinator URLs (Option-2-Flow)
        self.opena2_url = os.getenv("OPENA2_URL", "http://127.0.0.1:12345/command")  # opena2 = Archivator
        self.opena1_url = os.getenv("OPENA1_URL", "http://127.0.0.1:12344/invoke")   # opena1 = Koordinator
        self.kordp_url = os.getenv("KORDP_URL", "http://127.0.0.1:12346/dispatch")   # kordp = Koordinatport
        
        # Bearer Token (ENV-only)
        self.bearer_token = os.getenv("BEARER_TOKEN")
        
        # Archive directory (gemeinsames archivp aus 1.opena1&2_portier)
        archivp_root = os.getenv("ARCHIVP_ROOT", str(self.base_dir.parent / "1.opena1&2_portier" / "archivp_store"))
        self.archiv_dir = Path(archivp_root)
        self.archiv_dir.mkdir(parents=True, exist_ok=True)
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_dir = self.base_dir / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Configuration loaded: {self.service_name} @ {self.host}:{self.port}")

    def _load_env_file(self) -> None:
        """Load environment variables from .env file"""
        try:
            with open(self.env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            os.environ[key.strip()] = value.strip()
            logger.debug(f"Loaded .env from {self.env_file}")
        except Exception as e:
            logger.warning(f"Failed to load .env: {e}")

    def _get_port(self) -> int:
        """Get port from environment or default to 12348 (opena4)"""
        port_str = os.getenv("PORTIER_PORT", "12348")
        try:
            return int(port_str)
        except ValueError:
            logger.error(f"Invalid port: {port_str}, using default 12348")
            return 12348

    def _parse_ports(self, ports_str: str) -> list[int]:
        """Parse comma-separated port list"""
        if not ports_str:
            return []
        try:
            return [int(p.strip()) for p in ports_str.split(",") if p.strip()]
        except ValueError:
            logger.warning(f"Invalid port format: {ports_str}")
            return []

    def _parse_user_ids(self, user_str: str) -> list[int]:
        """Parse comma-separated user IDs"""
        if not user_str:
            return []
        try:
            return [int(u.strip()) for u in user_str.split(",") if u.strip()]
        except ValueError:
            logger.warning(f"Invalid user ID format: {user_str}")
            return []

    def _enforce_port_policy(self) -> None:
        """Enforce Port-Policy: reject if using forbidden port"""
        if self.port in self.forbidden_ports:
            logger.error(f"❌ PORT-POLICY VIOLATION: Port {self.port} ist verboten (8080 nur für UI)")
            sys.exit(1)
        
        if self.port not in self.allowed_ports:
            logger.warning(f"⚠️  Port {self.port} außerhalb erlaubtem Bereich {min(self.allowed_ports)}-{max(self.allowed_ports)}")
        
        logger.info(f"✅ Port-Policy OK: {self.port} in Bereich {min(self.allowed_ports)}-{max(self.allowed_ports)}")

    def get_logging_config(self) -> dict:
        """Return logging configuration"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s – %(message)s"
                },
                "json": {
                    "format": '{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}'
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.FileHandler",
                    "formatter": "standard",
                    "filename": str(self.log_dir / f"{self.service_name}.log"),
                    "mode": "a",
                    "encoding": "utf-8"
                }
            },
            "root": {
                "level": self.log_level,
                "handlers": ["console", "file"]
            }
        }

    def validate(self) -> bool:
        """Validate critical configuration"""
        checks = []
        
        if not self.telegram_bot_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not configured")
            checks.append(False)
        else:
            logger.info("✅ TELEGRAM_BOT_TOKEN configured")
            checks.append(True)
        
        if not self.telegram_allowed_users:
            logger.warning("⚠️  TELEGRAM_ALLOWED_USERS empty (all users allowed)")
        else:
            logger.info(f"✅ TELEGRAM_ALLOWED_USERS: {len(self.telegram_allowed_users)} users")
            checks.append(True)
        
        if not self.archiv_dir.exists():
            logger.error(f"❌ Archive directory not accessible: {self.archiv_dir}")
            checks.append(False)
        else:
            logger.info(f"✅ Archive directory: {self.archiv_dir}")
            checks.append(True)
        
        return all(checks)

    def to_dict(self) -> dict:
        """Export configuration as dictionary"""
        return {
            "service": self.service_name,
            "host": self.host,
            "port": self.port,
            "port_policy": {
                "allowed": self.allowed_ports,
                "forbidden": self.forbidden_ports
            },
            "telegram": {
                "bot_token_configured": bool(self.telegram_bot_token),
                "allowed_users_count": len(self.telegram_allowed_users),
                "webhook_url": self.telegram_webhook_url or "(none)"
            },
            "endpoints": {
                "opena1": self.opena1_url,
                "opena2": self.opena2_url,
                "kordp": self.kordp_url
            },
            "archive_dir": str(self.archiv_dir),
            "log_level": self.log_level
        }


# Singleton instance
_config: Optional[PortierConfig] = None


def get_config() -> PortierConfig:
    """Get or create global configuration instance"""
    global _config
    if _config is None:
        _config = PortierConfig()
    return _config


def reset_config() -> None:
    """Reset global configuration (for testing)"""
    global _config
    _config = None
