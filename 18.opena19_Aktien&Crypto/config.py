#!/usr/bin/env python3
"""
opena19 - Stocks & Crypto Agent
Configuration Module - PORTIER 3.0 Compliant

Port: 12365
Kürzel: stockcryptop
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

# ================== BASE PATHS ==================

BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
HTML_DIR = BASE_DIR / "html"
CONFIG_DIR = BASE_DIR / "config"

# Verzeichnisse erstellen
for directory in [DATA_DIR, LOGS_DIR, HTML_DIR, CONFIG_DIR]:
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
    
    port: int = Field(default=12365, ge=12344, le=12399)
    service_name: str = Field(default="opena19")
    kuerzel: str = Field(default="stockcryptop")
    version: str = Field(default="1.0")
    bearer_token: str = Field(default="")
    
    # Portier Integration
    portier_url: str = Field(default="http://127.0.0.1:12344")
    opena2_url: str = Field(default="http://127.0.0.1:12345")
    dashboard_url: str = Field(default="http://127.0.0.1:12349")
    
    # Paths
    data_dir: Path = Field(default=DATA_DIR)
    logs_dir: Path = Field(default=LOGS_DIR)
    
    # API Keys (from ENV only)
    alpha_vantage_key: str = Field(default="")
    coingecko_api_key: str = Field(default="")
    
    # Feature Flags
    enable_caching: bool = Field(default=True)
    enable_alerts: bool = Field(default=True)
    enable_sse: bool = Field(default=True)
    enable_safepoints: bool = Field(default=True)
    
    # Cache Settings
    cache_ttl_seconds: int = Field(default=300)  # 5 Minuten
    
    # Limits
    max_portfolio_positions: int = Field(default=100)
    max_alerts: int = Field(default=50)
    max_price_symbols: int = Field(default=20)


# ================== LOAD CONFIG FROM ENV ==================

def load_config() -> AgentConfig:
    """Lädt Konfiguration aus Environment-Variablen"""
    return AgentConfig(
        port=int(os.getenv("OPENA19_PORT", "12365")),
        service_name=os.getenv("OPENA19_SERVICE_NAME", "opena19"),
        kuerzel=os.getenv("OPENA19_KUERZEL", "stockcryptop"),
        bearer_token=os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313"),
        portier_url=os.getenv("PORTIER_URL", "http://127.0.0.1:12344"),
        opena2_url=os.getenv("OPENA2_URL", "http://127.0.0.1:12345"),
        dashboard_url=os.getenv("DASHBOARD_URL", "http://127.0.0.1:12349"),
        alpha_vantage_key=os.getenv("ALPHA_VANTAGE_KEY", "demo"),
        coingecko_api_key=os.getenv("COINGECKO_API_KEY", ""),
        enable_caching=os.getenv("ENABLE_CACHING", "true").lower() == "true",
        enable_alerts=os.getenv("ENABLE_ALERTS", "true").lower() == "true",
        cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "300")),
    )


# ================== SINGLETON CONFIG ==================

CONFIG = load_config()


# ================== MARKET CONFIG ==================

class MarketConfig(BaseModel):
    """Market-Konfiguration"""
    model_config = ConfigDict(extra="forbid")
    
    # Supported Stock Exchanges
    stock_exchanges: List[str] = Field(default=["NYSE", "NASDAQ", "XETRA"])
    
    # Supported Cryptocurrencies
    supported_cryptos: List[str] = Field(default=[
        "bitcoin", "ethereum", "tether", "binancecoin", "solana",
        "cardano", "ripple", "polkadot", "dogecoin", "avalanche"
    ])
    
    # Default Currency
    default_currency: str = Field(default="USD")
    
    # Trading Hours (UTC)
    stock_market_open: str = Field(default="13:30")  # NYSE
    stock_market_close: str = Field(default="20:00")


MARKET_CONFIG = MarketConfig()
