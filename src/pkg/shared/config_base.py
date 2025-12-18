#!/usr/bin/env python3
"""
Shared Configuration Base Module

Reusable base configuration classes for all PORTIER 3.0 agents.
This module provides common configuration patterns to reduce duplication.

Usage:
    from src.pkg.shared.config_base import PortPolicy, BaseAgentConfig
    
    class MyAgentConfig(BaseAgentConfig):
        service_name: str = "opena4"
        kuerzel: str = "tgap"
        port: int = 12346
        
        # Add agent-specific fields
        telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
"""

from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class PortPolicy:
    """PORTIER 3.0 Port Policy Enforcement.
    
    Defines allowed port ranges and forbidden ports for the system.
    """
    
    ALLOWED_RANGE = range(12344, 12400)
    FORBIDDEN_PORTS = [8080]
    
    @classmethod
    def is_valid_port(cls, port: int) -> bool:
        """Check if a port is valid according to policy.
        
        Args:
            port: Port number to validate
            
        Returns:
            True if port is in allowed range and not forbidden
        """
        return port in cls.ALLOWED_RANGE and port not in cls.FORBIDDEN_PORTS
    
    @classmethod
    def get_allowed_origins(cls) -> List[str]:
        """Get list of allowed CORS origins based on port policy.
        
        Returns:
            List of allowed origin URLs
        """
        origins = ["http://127.0.0.1:8080"]
        for port in cls.ALLOWED_RANGE:
            if port not in cls.FORBIDDEN_PORTS:
                origins.append(f"http://127.0.0.1:{port}")
        return origins


class BaseAgentConfig(BaseSettings):
    """Base configuration for PORTIER 3.0 agents.
    
    Provides common configuration fields and methods that all agents share.
    Inherit from this class to create agent-specific configurations.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Service identification
    service_name: str = Field(..., description="Service name (e.g., opena4)")
    kuerzel: str = Field(..., description="PORTIER abbreviation (e.g., tgap)")
    host: str = Field(default="127.0.0.1", description="Service host")
    port: int = Field(..., description="Service port")
    version: str = Field(default="3.0", description="PORTIER version")
    
    # Authentication
    bearer_token: str = Field(
        default="",
        alias="BEARER_TOKEN",
        description="Bearer token for authentication"
    )
    
    # Base directory
    base_dir: Path = Field(
        default_factory=lambda: Path.cwd(),
        description="Base directory for the service"
    )
    
    # Service URLs
    opena1_url: str = Field(
        default="http://127.0.0.1:12344",
        alias="OPENA1_URL",
        description="opena1 coordinator URL"
    )
    opena2_url: str = Field(
        default="http://127.0.0.1:12345",
        alias="OPENA2_URL",
        description="opena2 archivator URL"
    )
    opena20_url: str = Field(
        default="http://127.0.0.1:12349",
        alias="OPENA20_URL",
        description="opena20 dashboard URL"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
        description="Logging level"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    
    @property
    def data_dir(self) -> Path:
        """Get data directory path.
        
        Returns:
            Path to data directory
        """
        return self.base_dir / "data"
    
    @property
    def logs_dir(self) -> Path:
        """Get logs directory path.
        
        Returns:
            Path to logs directory
        """
        return self.base_dir / "logs"
    
    def ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        self.data_dir.mkdir(exist_ok=True, parents=True)
        self.logs_dir.mkdir(exist_ok=True, parents=True)
    
    def get_logging_config(self) -> dict:
        """Get logging configuration dictionary.
        
        Returns:
            Dict compatible with logging.config.dictConfig
        """
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
                self.service_name: {
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
    
    def to_dict(self, mask_secrets: bool = True) -> dict:
        """Convert config to dictionary.
        
        Args:
            mask_secrets: Whether to mask sensitive fields
            
        Returns:
            Configuration dictionary
        """
        config_dict = {
            "service_name": self.service_name,
            "kuerzel": self.kuerzel,
            "host": self.host,
            "port": self.port,
            "version": self.version,
            "opena1_url": self.opena1_url,
            "opena2_url": self.opena2_url,
            "opena20_url": self.opena20_url,
            "log_level": self.log_level,
        }
        
        if mask_secrets:
            config_dict["bearer_token"] = "***" if self.bearer_token else ""
        else:
            config_dict["bearer_token"] = self.bearer_token
            
        return config_dict


class AgentInfo(BaseModel):
    """Agent information model.
    
    Used for agent registry and identification.
    """
    
    model_config = ConfigDict(extra="forbid")
    
    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent Name")
    kuerzel: str = Field(..., description="PORTIER Kürzel")
    port: int = Field(..., description="Service Port")
    enabled: bool = Field(default=True, description="Agent enabled status")


__all__ = [
    "PortPolicy",
    "BaseAgentConfig",
    "AgentInfo"
]
