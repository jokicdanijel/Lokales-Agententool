#!/usr/bin/env python3
"""
opena4 - Telegram Gateway Agent
Konfigurationsmodul

Port: 12346
Kürzel: tgap

PORTIER 3.0 konform – Pydantic V2
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PortPolicy:
    """PORTIER 3.0 Port Policy Enforcement"""
    
    ALLOWED_RANGE = range(12344, 12400)
    FORBIDDEN_PORTS = [8080]
    
    @classmethod
    def is_valid_port(cls, port: int) -> bool:
        return port in cls.ALLOWED_RANGE and port not in cls.FORBIDDEN_PORTS
    
    @classmethod
    def get_allowed_origins(cls) -> List[str]:
        origins = ["http://127.0.0.1:8080"]
        for port in cls.ALLOWED_RANGE:
            if port not in cls.FORBIDDEN_PORTS:
                origins.append(f"http://127.0.0.1:{port}")
        return origins


class ServiceConfig(BaseSettings):
    """Hauptkonfiguration für opena4"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    service_name: str = "opena4"
    kuerzel: str = "tgap"
    host: str = "127.0.0.1"
    port: int = 12346
    version: str = "3.0"
    
    bearer_token: str = Field(
        default="",
        alias="BEARER_TOKEN"
    )
    
    base_dir: Path = Path(__file__).parent
    
    opena1_url: str = Field(default="http://127.0.0.1:12344", alias="OPENA1_URL")
    opena2_url: str = Field(default="http://127.0.0.1:12345", alias="OPENA2_URL")
    opena20_url: str = Field(default="http://127.0.0.1:12349", alias="OPENA20_URL")
    
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_allowed_users: List[int] = Field(default_factory=list, alias="TELEGRAM_ALLOWED_USER_IDS")
    archiv_dir: Path = Field(default=Path("../1.opena1&2_portier/archivp_store"), alias="ARCHIVP_ROOT")

    @field_validator("telegram_allowed_users", mode="before")
    @classmethod
    def parse_allowed_users(cls, v):
        """Parse comma-separated string or single int to list of ints"""
        if v is None or v == "":
            return []
        if isinstance(v, list):
            return [int(x) for x in v]
        if isinstance(v, int):
            return [v]
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return []

    @property
    def data_dir(self) -> Path:
        return self.base_dir / "data"
    
    @property
    def logs_dir(self) -> Path:
        return self.base_dir / "logs"
    
    def to_dict(self) -> dict:
        """Convert config to dictionary (mask secrets)"""
        return {
            "service_name": self.service_name,
            "kuerzel": self.kuerzel,
            "host": self.host,
            "port": self.port,
            "version": self.version,
            "telegram_bot_token": "***" if self.telegram_bot_token else "",
            "telegram_allowed_users": self.telegram_allowed_users,
            "opena1_url": self.opena1_url,
            "opena2_url": self.opena2_url,
            "opena20_url": self.opena20_url,
        }
    
    def get_logging_config(self) -> dict:
        """Return logging dictConfig"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {"format": self.log_format}
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": self.log_level
                }
            },
            "loggers": {
                "opena4": {
                    "handlers": ["console"],
                    "level": self.log_level,
                    "propagate": False
                }
            },
            "root": {
                "handlers": ["console"],
                "level": self.log_level
            }
        }


class AgentInfo(BaseModel):
    """Agent-Informationen"""
    
    model_config = ConfigDict(extra="forbid")
    
    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent Name")
    kuerzel: str = Field(..., description="PORTIER Kürzel")
    port: int = Field(..., description="Service Port")
    enabled: bool = Field(default=True)


_config: Optional[ServiceConfig] = None


def load_config() -> ServiceConfig:
    global _config
    if _config is None:
        _config = ServiceConfig()
        _config.data_dir.mkdir(exist_ok=True)
        _config.logs_dir.mkdir(exist_ok=True)
    return _config


# Alias for backwards compatibility
def get_config() -> ServiceConfig:
    return load_config()


__all__ = ["PortPolicy", "ServiceConfig", "AgentInfo", "load_config", "get_config"]
