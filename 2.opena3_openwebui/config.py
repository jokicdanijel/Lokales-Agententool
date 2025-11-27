"""
opena3 Configuration Module
ENV-only Configuration (niemals hardcoded)
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class OpenWebUIConfig(BaseModel):
    """OpenWebUI-spezifische Konfiguration"""
    url: str = Field(default="http://127.0.0.1:8080", description="OpenWebUI Base-URL")
    adapter_url: str = Field(default="http://127.0.0.1:12350", description="OpenWebUI Adapter URL")
    timeout: int = Field(default=30, description="Request-Timeout in Sekunden")
    max_retries: int = Field(default=3, description="Maximale Retry-Anzahl")


class Opena3Config(BaseModel):
    """Hauptkonfiguration für opena3"""
    port: int = Field(default=12347, description="Agent-Port")
    host: str = Field(default="127.0.0.1", description="Bind-Host")
    bearer_token: Optional[str] = Field(default=None, description="Bearer Token (ENV-only)")
    log_level: str = Field(default="INFO", description="Log-Level")
    
    # Paths
    base_root: Path = Field(default_factory=lambda: Path.cwd().parent, description="Projekt-Root")
    archive_dir: Optional[Path] = Field(default=None, description="Safepoint-Archiv")
    
    # OpenWebUI
    openwebui: OpenWebUIConfig = Field(default_factory=OpenWebUIConfig)
    
    def __init__(self, **kwargs):
        # Lade ENV-Variablen
        env_overrides = {
            "port": int(os.getenv("OPENA3_PORT", "12347")),
            "host": os.getenv("OPENA3_HOST", "127.0.0.1"),
            "bearer_token": os.getenv("BEARER_TOKEN"),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "base_root": Path(os.getenv("BASE_ROOT", Path.cwd().parent)),
        }
        
        # Merge mit kwargs
        merged = {**env_overrides, **kwargs}
        super().__init__(**merged)
        
        # Setze archive_dir falls nicht gegeben
        if self.archive_dir is None:
            self.archive_dir = self.base_root / "1.opena1&2_portier" / "archivp_store"
    
    class Config:
        extra = "forbid"


# Singleton-Instanz
_config: Optional[Opena3Config] = None


def get_config() -> Opena3Config:
    """Gibt Singleton-Config-Instanz zurück"""
    global _config
    if _config is None:
        _config = Opena3Config()
    return _config
