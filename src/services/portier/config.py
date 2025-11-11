"""
portier/config.py — Configuration for Coordinator Gateway (kordp)
Centralizes settings for the portier service.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class PortierConfig(BaseSettings):
    """Portier service configuration."""
    
    # Service Identity
    service_name: str = "portier"
    program_target: str = "kordp"
    port: int = 12344
    host: str = "127.0.0.1"
    
    # Archivator Integration
    archivator_host: str = "127.0.0.1"
    archivator_port: int = 12345
    archivator_timeout: float = 5.0
    
    # OpenAI (optional)
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_org: Optional[str] = os.getenv("OPENAI_ORG")
    
    # Logging
    log_level: str = "info"
    log_file: Optional[Path] = None
    
    # Policy
    port_policy_min: int = 12344
    port_policy_max: int = 12399
    
    # Feature Flags
    strict_mode: bool = True
    enable_redaction: bool = True
    
    class Config:
        """Pydantic settings config."""
        env_file = ".env"
        env_prefix = "PORTIER_"
        case_sensitive = False
    
    @property
    def archivator_url(self) -> str:
        """Build archivator base URL."""
        return f"http://{self.archivator_host}:{self.archivator_port}"
    
    @property
    def archivator_store_endpoint(self) -> str:
        """Archivator store endpoint."""
        return f"{self.archivator_url}/store/archivp"


# Global config instance
config = PortierConfig()


def get_config() -> PortierConfig:
    """Get global configuration instance."""
    return config
