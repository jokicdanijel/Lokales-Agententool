"""
SCTA Configuration Management
Loads environment variables with validation and secrets masking.
"""

import logging
import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    # === API Configuration ===
    api_host: str = "127.0.0.1"
    api_port: int = 3000
    api_title: str = "SCTA - Self-Contextualizing Task Agent"
    api_version: str = "0.1.0"

    # === Orchestrator Configuration ===
    orchestrator_host: str = "127.0.0.1"
    orchestrator_port: int = 5000

    # === Worker Configuration ===
    worker_planner_host: str = "127.0.0.1"
    worker_planner_port: int = 5001
    worker_executor_host: str = "127.0.0.1"
    worker_executor_port: int = 5002

    # === Database Configuration ===
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "scta_user"
    postgres_password: str = "change_me_in_production"
    postgres_db: str = "scta_db"

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # === Redis Configuration ===
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0

    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # === Qdrant Configuration (Optional) ===
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: Optional[str] = None

    @property
    def qdrant_url(self) -> str:
        """Construct Qdrant connection URL."""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"

    # === Secrets (MUST be set in production) ===
    dashboard_admin_token: str = "your_secure_token_here"
    telegram_bot_token: Optional[str] = None
    telegram_webhook_secret: Optional[str] = None
    telegram_allowed_users: str = ""

    # === Authentication ===
    jwt_secret_key: str = "your_jwt_secret_key_here"
    jwt_algorithm: str = "HS256"
    jwt_expiration_seconds: int = 86400  # 24 hours

    # === Logging & Environment ===
    environment: str = "development"  # development, staging, production
    log_level: str = "INFO"
    debug: bool = False

    # === OpenTelemetry (Optional) ===
    otel_enabled: bool = False
    otel_exporter_otlp_endpoint: str = "http://localhost:4318"
    otel_exporter_otlp_protocol: str = "http/protobuf"

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __repr__(self) -> str:
        """String representation with secrets masked."""
        config_dict = self.model_dump()

        # Mask sensitive fields
        sensitive_fields = [
            "postgres_password",
            "redis_password",
            "dashboard_admin_token",
            "telegram_bot_token",
            "telegram_webhook_secret",
            "jwt_secret_key",
            "qdrant_api_key",
        ]

        for field in sensitive_fields:
            if field in config_dict and config_dict[field]:
                config_dict[field] = "***MASKED***"

        return f"Settings({config_dict})"

    def get_masked_dict(self) -> dict:
        """Get configuration dictionary with secrets masked."""
        config_dict = self.model_dump()

        sensitive_fields = [
            "postgres_password",
            "redis_password",
            "dashboard_admin_token",
            "telegram_bot_token",
            "telegram_webhook_secret",
            "jwt_secret_key",
            "qdrant_api_key",
        ]

        for field in sensitive_fields:
            if field in config_dict and config_dict[field]:
                config_dict[field] = "***MASKED***"

        return config_dict


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()

    if settings.debug:
        logger.debug(f"Loaded configuration: {settings}")
    else:
        logger.info(f"Configuration loaded (secrets masked): {settings.get_masked_dict()}")

    return settings
