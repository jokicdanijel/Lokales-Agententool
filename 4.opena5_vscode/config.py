#!/usr/bin/env python3
"""
opena5 - VS Code Agent
Konfigurationsmodul

Port: 12365
Kürzel: vscop

PORTIER 3.0 konform
"""

from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class PortPolicy:
    """PORTIER 3.0 Port Policy Enforcement"""

    ALLOWED_RANGE = range(12344, 12400)
    FORBIDDEN_PORTS = [8080]

    @classmethod
    def is_valid_port(cls, port: int) -> bool:
        return port in cls.ALLOWED_RANGE and port not in cls.FORBIDDEN_PORTS

    @classmethod
    def get_allowed_origins(cls) -> list[str]:
        origins = ["http://127.0.0.1:8080"]
        for port in cls.ALLOWED_RANGE:
            if port not in cls.FORBIDDEN_PORTS:
                origins.append(f"http://127.0.0.1:{port}")
        return origins


class ServiceConfig(BaseSettings):
    """Hauptkonfiguration für opena5"""

    service_name: str = "opena5"
    kuerzel: str = "vscop"
    port: int = 12365
    version: str = "3.0"

    bearer_token: str = Field(default="c899b90d-faf8-485b-afa4-078357cf5313", alias="BEARER_TOKEN")

    base_dir: Path = Path(__file__).parent

    opena1_url: str = Field(default="http://127.0.0.1:12344", alias="OPENA1_URL")
    opena2_url: str = Field(default="http://127.0.0.1:12345", alias="OPENA2_URL")
    opena20_url: str = Field(default="http://127.0.0.1:12349", alias="OPENA20_URL")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def data_dir(self) -> Path:
        return self.base_dir / "data"

    @property
    def logs_dir(self) -> Path:
        return self.base_dir / "logs"


class AgentInfo(BaseModel):
    """Agent-Informationen"""

    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent Name")
    kuerzel: str = Field(..., description="PORTIER Kürzel")
    port: int = Field(..., description="Service Port")
    enabled: bool = Field(default=True)

    class Config:
        extra = "forbid"


_config: ServiceConfig | None = None


def load_config() -> ServiceConfig:
    global _config
    if _config is None:
        _config = ServiceConfig()
        _config.data_dir.mkdir(exist_ok=True)
        _config.logs_dir.mkdir(exist_ok=True)
    return _config


__all__ = ["PortPolicy", "ServiceConfig", "AgentInfo", "load_config"]
