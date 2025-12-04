#!/usr/bin/env python3
"""
opena20 - Dashboard Agent
Konfigurationsmodul

Port: 12349
Kürzel: dashp

PORTIER 3.0 konform
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


# ==================== Port Policy ====================

class PortPolicy:
    """PORTIER 3.0 Port Policy Enforcement"""
    
    ALLOWED_RANGE = range(12344, 12400)
    FORBIDDEN_PORTS = [8080]  # Reserved for OpenWebUI UI
    
    @classmethod
    def is_valid_port(cls, port: int) -> bool:
        """Prüft ob Port in erlaubtem Bereich"""
        return port in cls.ALLOWED_RANGE and port not in cls.FORBIDDEN_PORTS
    
    @classmethod
    def get_allowed_origins(cls) -> List[str]:
        """Gibt erlaubte CORS Origins zurück"""
        origins = ["http://127.0.0.1:8080"]  # OpenWebUI Frontend
        for port in cls.ALLOWED_RANGE:
            if port not in cls.FORBIDDEN_PORTS:
                origins.append(f"http://127.0.0.1:{port}")
        return origins


# ==================== Service Configuration ====================

class ServiceConfig(BaseSettings):
    """Hauptkonfiguration für opena20 Dashboard Agent"""
    
    # Service Identity
    service_name: str = "opena20"
    kuerzel: str = "dashp"
    port: int = 12349
    version: str = "3.0"
    
    # Security
    bearer_token: str = Field(
        default="c899b90d-faf8-485b-afa4-078357cf5313",
        alias="BEARER_TOKEN"
    )
    
    # Paths
    base_dir: Path = Path(__file__).parent
    
    # PORTIER Integration
    opena1_url: str = Field(default="http://127.0.0.1:12344", alias="OPENA1_URL")
    opena2_url: str = Field(default="http://127.0.0.1:12345", alias="OPENA2_URL")
    kordp_url: str = Field(default="http://127.0.0.1:12346", alias="KORDP_URL")
    
    # Dashboard Settings
    sse_keepalive_interval: int = Field(default=15, alias="SSE_KEEPALIVE")
    agent_health_timeout: float = Field(default=5.0, alias="AGENT_HEALTH_TIMEOUT")
    max_sse_connections: int = Field(default=100, alias="MAX_SSE_CONNECTIONS")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def static_dir(self) -> Path:
        return self.base_dir / "static"
    
    @property
    def templates_dir(self) -> Path:
        return self.base_dir / "frontend"
    
    @property
    def data_dir(self) -> Path:
        return self.base_dir / "data"
    
    @property
    def logs_dir(self) -> Path:
        return self.base_dir / "logs"


# ==================== Agent Registry ====================

class AgentInfo(BaseModel):
    """Agent-Informationen für Registry"""
    
    id: str = Field(..., description="Agent ID (z.B. opena3)")
    name: str = Field(..., description="Human-readable Name")
    kuerzel: str = Field(..., description="PORTIER Kürzel")
    port: int = Field(..., description="Service Port")
    enabled: bool = Field(default=True, description="Agent aktiviert")
    
    class Config:
        extra = "forbid"


AGENT_REGISTRY: List[AgentInfo] = [
    AgentInfo(id="opena1",  name="Koordinator (Portier)",   kuerzel="kordp",       port=12344),
    AgentInfo(id="opena2",  name="Archivator",              kuerzel="archivp",     port=12345),
    AgentInfo(id="opena3",  name="OpenWebUI Terminal",      kuerzel="owuip",       port=12347),
    AgentInfo(id="opena4",  name="Telegram Agent",          kuerzel="telep",       port=12348),
    AgentInfo(id="opena5",  name="VS Code Agent",           kuerzel="vscop",       port=12351),
    AgentInfo(id="opena6",  name="Browser Agent",           kuerzel="browsep",     port=12352),
    AgentInfo(id="opena7",  name="Email Agent",             kuerzel="emailp",      port=12353),
    AgentInfo(id="opena8",  name="WhatsApp Agent",          kuerzel="whatsappp",   port=12354),
    AgentInfo(id="opena9",  name="Telefonie Agent",         kuerzel="telephonep",  port=12355),
    AgentInfo(id="opena10", name="Call Tracking Agent",     kuerzel="calltrackp",  port=12356),
    AgentInfo(id="opena11", name="Unlock Agent",            kuerzel="unlockp",     port=12357),
    AgentInfo(id="opena12", name="Social Media Agent",      kuerzel="smp",         port=12358),
    AgentInfo(id="opena13", name="Influencer Agent",        kuerzel="influp",      port=12359),
    AgentInfo(id="opena14", name="Calendar Agent",          kuerzel="calp",        port=12360),
    AgentInfo(id="opena15", name="HTML Creator",            kuerzel="htmlp",       port=12361),
    AgentInfo(id="opena16", name="Shop Agent",              kuerzel="shopp",       port=12362),
    AgentInfo(id="opena17", name="Homepage Creator",        kuerzel="hpcreatep",   port=12363),
    AgentInfo(id="opena18", name="CRM Agent",               kuerzel="crmp",        port=12364),
    AgentInfo(id="opena19", name="Stocks & Crypto",         kuerzel="stockcryptop",port=12365),
    AgentInfo(id="opena20", name="Dashboard Agent",         kuerzel="dashp",       port=12349),
    AgentInfo(id="opena21", name="Workflow Engine",         kuerzel="workflowp",   port=12364),
]


# ==================== SSE Configuration ====================

class SSEConfig(BaseModel):
    """SSE Bus Konfiguration"""
    
    max_connections: int = Field(default=100, description="Max. gleichzeitige SSE-Verbindungen")
    keepalive_interval: int = Field(default=15, description="Keepalive Interval in Sekunden")
    buffer_size: int = Field(default=1000, description="Event-Buffer Größe")
    event_types: List[str] = Field(
        default=["agent_status", "safepoint", "alert", "metric", "notification"],
        description="Erlaubte Event-Typen"
    )
    
    class Config:
        extra = "forbid"


# ==================== Dashboard Configuration ====================

class DashboardConfig(BaseModel):
    """Dashboard UI Konfiguration"""
    
    title: str = Field(default="ELION Dashboard 3.0", description="Dashboard Titel")
    theme: str = Field(default="dark", description="UI Theme (dark/light)")
    refresh_interval: int = Field(default=5000, description="Auto-Refresh Interval in ms")
    show_offline_agents: bool = Field(default=True, description="Offline Agents anzeigen")
    enable_notifications: bool = Field(default=True, description="Browser Notifications")
    
    class Config:
        extra = "forbid"


# ==================== Singleton Config Loader ====================

_config: Optional[ServiceConfig] = None


def load_config() -> ServiceConfig:
    """Lädt Konfiguration (Singleton Pattern)"""
    global _config
    if _config is None:
        _config = ServiceConfig()
        # Verzeichnisse erstellen
        _config.static_dir.mkdir(exist_ok=True)
        _config.templates_dir.mkdir(exist_ok=True)
        _config.data_dir.mkdir(exist_ok=True)
        _config.logs_dir.mkdir(exist_ok=True)
    return _config


def get_agent_by_id(agent_id: str) -> Optional[AgentInfo]:
    """Findet Agent nach ID"""
    for agent in AGENT_REGISTRY:
        if agent.id == agent_id:
            return agent
    return None


def get_agent_by_kuerzel(kuerzel: str) -> Optional[AgentInfo]:
    """Findet Agent nach Kürzel"""
    for agent in AGENT_REGISTRY:
        if agent.kuerzel == kuerzel:
            return agent
    return None


def get_agent_url(agent_id: str, endpoint: str = "/health") -> Optional[str]:
    """Erstellt Agent-URL für API-Calls"""
    agent = get_agent_by_id(agent_id)
    if agent:
        return f"http://127.0.0.1:{agent.port}{endpoint}"
    return None


# ==================== Export ====================

__all__ = [
    "PortPolicy",
    "ServiceConfig",
    "AgentInfo",
    "AGENT_REGISTRY",
    "SSEConfig",
    "DashboardConfig",
    "load_config",
    "get_agent_by_id",
    "get_agent_by_kuerzel",
    "get_agent_url",
]
