#!/usr/bin/env python3
"""
opena17 - Homepage Creator Agent
Configuration Module - PORTIER 3.0 Compliant

Port: 12362
Kürzel: hpcreatep
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

# ================== BASE PATHS ==================

BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
SITES_DIR = DATA_DIR / "sites"
TEMPLATES_DIR = DATA_DIR / "templates"
OUTPUT_DIR = DATA_DIR / "output"
PREVIEW_DIR = DATA_DIR / "preview"
LOGS_DIR = BASE_DIR / "logs"
HTML_DIR = BASE_DIR / "html"

# Verzeichnisse erstellen
for directory in [DATA_DIR, SITES_DIR, TEMPLATES_DIR, OUTPUT_DIR, PREVIEW_DIR, LOGS_DIR, HTML_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


# ================== PORT POLICY ==================

class PortPolicy:
    """PORTIER 3.0 Port Policy (12344-12399)"""
    ALLOWED_RANGE = range(12344, 12400)
    FORBIDDEN_PORTS = [8080]  # Reserved for OpenWebUI UI
    
    @classmethod
    def is_valid_port(cls, port: int) -> bool:
        return port in cls.ALLOWED_RANGE and port not in cls.FORBIDDEN_PORTS


# ================== AGENT CONFIG ==================

class AgentConfig(BaseModel):
    """Agent-Konfiguration mit strict JSON Schema"""
    model_config = ConfigDict(extra="forbid")
    
    port: int = Field(default=12362, ge=12344, le=12399)
    service_name: str = Field(default="opena17")
    kuerzel: str = Field(default="hpcreatep")
    version: str = Field(default="1.0")
    bearer_token: str = Field(default="")
    
    # Portier Integration
    portier_url: str = Field(default="http://127.0.0.1:12344")
    opena2_url: str = Field(default="http://127.0.0.1:12345")
    dashboard_url: str = Field(default="http://127.0.0.1:12349")
    
    # Paths
    data_dir: Path = Field(default=DATA_DIR)
    sites_dir: Path = Field(default=SITES_DIR)
    templates_dir: Path = Field(default=TEMPLATES_DIR)
    output_dir: Path = Field(default=OUTPUT_DIR)
    logs_dir: Path = Field(default=LOGS_DIR)
    
    # Feature Flags
    enable_preview: bool = Field(default=True)
    enable_sse: bool = Field(default=True)
    enable_safepoints: bool = Field(default=True)
    
    # Limits
    max_pages_per_site: int = Field(default=50)
    max_sites: int = Field(default=100)
    max_export_size_mb: int = Field(default=50)


# ================== LOAD CONFIG FROM ENV ==================

def load_config() -> AgentConfig:
    """Lädt Konfiguration aus Environment-Variablen"""
    return AgentConfig(
        port=int(os.getenv("OPENA17_PORT", "12362")),
        service_name=os.getenv("OPENA17_SERVICE_NAME", "opena17"),
        kuerzel=os.getenv("OPENA17_KUERZEL", "hpcreatep"),
        bearer_token=os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313"),
        portier_url=os.getenv("PORTIER_URL", "http://127.0.0.1:12344"),
        opena2_url=os.getenv("OPENA2_URL", "http://127.0.0.1:12345"),
        dashboard_url=os.getenv("DASHBOARD_URL", "http://127.0.0.1:12349"),
        enable_preview=os.getenv("ENABLE_PREVIEW", "true").lower() == "true",
        enable_sse=os.getenv("ENABLE_SSE", "true").lower() == "true",
        enable_safepoints=os.getenv("ENABLE_SAFEPOINTS", "true").lower() == "true",
    )


# ================== SINGLETON CONFIG ==================

CONFIG = load_config()


# ================== TEMPLATE CONFIGS ==================

class TemplateConfig(BaseModel):
    """Website Template Konfiguration"""
    model_config = ConfigDict(extra="forbid")
    
    name: str
    description: str
    framework: str = Field(default="vanilla")  # vanilla, bootstrap, tailwind
    responsive: bool = Field(default=True)
    dark_mode: bool = Field(default=False)
    components: List[str] = Field(default_factory=list)


# Default Templates
DEFAULT_TEMPLATES = [
    TemplateConfig(
        name="default",
        description="Einfaches, sauberes Layout",
        framework="vanilla",
        components=["header", "main", "footer"]
    ),
    TemplateConfig(
        name="modern",
        description="Modernes Design mit Hero-Section",
        framework="vanilla",
        components=["header", "hero", "features", "contact", "footer"]
    ),
    TemplateConfig(
        name="portfolio",
        description="Portfolio-Template für Kreative",
        framework="vanilla",
        components=["header", "hero", "gallery", "about", "contact", "footer"]
    ),
    TemplateConfig(
        name="landing",
        description="Landing Page für Produkte/Services",
        framework="vanilla",
        components=["header", "hero", "benefits", "pricing", "cta", "footer"]
    ),
    TemplateConfig(
        name="documentation",
        description="Dokumentations-Template",
        framework="vanilla",
        components=["header", "sidebar", "content", "footer"]
    ),
]
