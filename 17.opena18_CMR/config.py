#!/usr/bin/env python3
"""
opena18 - CRM Agent
Configuration Module - PORTIER 3.0 Compliant

Port: 12363
Kürzel: crmp
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

# ================== BASE PATHS ==================

BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
CONTACTS_DIR = DATA_DIR / "contacts"
LOGS_DIR = BASE_DIR / "logs"
HTML_DIR = BASE_DIR / "html"
CONFIG_DIR = BASE_DIR / "config"

# Verzeichnisse erstellen
for directory in [DATA_DIR, CONTACTS_DIR, LOGS_DIR, HTML_DIR, CONFIG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


# ================== PORT POLICY ==================

class PortPolicy:
    """PORTIER 3.0 Port Policy (12344-12399)"""
    ALLOWED_RANGE = range(12344, 12400)
    FORBIDDEN_PORTS = [8080]
    
    @classmethod
    def is_valid_port(cls, port: int) -> bool:
        return port in cls.ALLOWED_RANGE and port not in cls.FORBIDDEN_PORTS


# ================== AGENT CONFIG ==================

class AgentConfig(BaseModel):
    """Agent-Konfiguration mit strict JSON Schema"""
    model_config = ConfigDict(extra="forbid")
    
    port: int = Field(default=12363, ge=12344, le=12399)
    service_name: str = Field(default="opena18")
    kuerzel: str = Field(default="crmp")
    version: str = Field(default="1.0")
    bearer_token: str = Field(default="")
    
    # Portier Integration
    portier_url: str = Field(default="http://127.0.0.1:12344")
    opena2_url: str = Field(default="http://127.0.0.1:12345")
    dashboard_url: str = Field(default="http://127.0.0.1:12349")
    
    # Paths
    data_dir: Path = Field(default=DATA_DIR)
    logs_dir: Path = Field(default=LOGS_DIR)
    
    # Feature Flags
    enable_gdpr_compliance: bool = Field(default=True)
    enable_audit_log: bool = Field(default=True)
    enable_sse: bool = Field(default=True)
    enable_safepoints: bool = Field(default=True)
    
    # Limits
    max_contacts: int = Field(default=10000)
    max_organizations: int = Field(default=1000)
    max_deals: int = Field(default=5000)
    max_activities: int = Field(default=50000)
    
    # Data Retention
    activity_retention_days: int = Field(default=365)
    audit_log_retention_days: int = Field(default=730)


# ================== LOAD CONFIG FROM ENV ==================

def load_config() -> AgentConfig:
    """Lädt Konfiguration aus Environment-Variablen"""
    return AgentConfig(
        port=int(os.getenv("OPENA18_PORT", "12363")),
        service_name=os.getenv("OPENA18_SERVICE_NAME", "opena18"),
        kuerzel=os.getenv("OPENA18_KUERZEL", "crmp"),
        bearer_token=os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313"),
        portier_url=os.getenv("PORTIER_URL", "http://127.0.0.1:12344"),
        opena2_url=os.getenv("OPENA2_URL", "http://127.0.0.1:12345"),
        dashboard_url=os.getenv("DASHBOARD_URL", "http://127.0.0.1:12349"),
        enable_gdpr_compliance=os.getenv("ENABLE_GDPR", "true").lower() == "true",
        enable_audit_log=os.getenv("ENABLE_AUDIT_LOG", "true").lower() == "true",
        enable_sse=os.getenv("ENABLE_SSE", "true").lower() == "true",
        enable_safepoints=os.getenv("ENABLE_SAFEPOINTS", "true").lower() == "true",
    )


# ================== SINGLETON CONFIG ==================

CONFIG = load_config()


# ================== GDPR CONFIG ==================

class GDPRConfig(BaseModel):
    """GDPR Compliance Konfiguration"""
    model_config = ConfigDict(extra="forbid")
    
    data_export_enabled: bool = Field(default=True)
    data_deletion_enabled: bool = Field(default=True)
    consent_tracking: bool = Field(default=True)
    anonymization_enabled: bool = Field(default=True)
    audit_trail_enabled: bool = Field(default=True)
    retention_policy_days: int = Field(default=365 * 3)  # 3 Jahre


GDPR_CONFIG = GDPRConfig()
