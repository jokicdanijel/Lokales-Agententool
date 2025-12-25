"""
opena6 Configuration Module
Browser Agent für deterministische Web-Automation
"""

import os

from pydantic_settings import BaseSettings


class OpenaConfig(BaseSettings):
    """Configuration for opena6 Browser Agent"""

    # Service Identity
    SERVICE_NAME: str = "opena6"
    SERVICE_COMPONENT: str = "browser"
    PORT: int = int(os.getenv("OPENA6_PORT", "12349"))

    # Archivator (opena2) Integration
    OPENA2_URL: str = os.getenv("OPENA2_URL", "http://127.0.0.1:12345")
    ARCHIV_PATH: str = os.getenv("ARCHIV_PATH", "archivp")

    # Coordinator (opena1) Integration
    OPENA1_URL: str = os.getenv("OPENA1_URL", "http://127.0.0.1:12344")

    # Playwright Configuration
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() in ("true", "1")
    BROWSER_TYPE: str = os.getenv("BROWSER_TYPE", "chromium")  # chromium, firefox, webkit
    PLAYWRIGHT_TIMEOUT_MS: int = int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", "10000"))
    VIEWPORT_WIDTH: int = int(os.getenv("VIEWPORT_WIDTH", "1280"))
    VIEWPORT_HEIGHT: int = int(os.getenv("VIEWPORT_HEIGHT", "800"))

    # Rate Limiting (per domain, requests per second)
    DEFAULT_RPS_LIMIT: float = float(os.getenv("DEFAULT_RPS_LIMIT", "1.0"))

    # Artifact Management
    MAX_ARTIFACT_SIZE_MB: int = int(os.getenv("MAX_ARTIFACT_SIZE_MB", "50"))
    ATTACH_HTML_DEFAULT: bool = os.getenv("ATTACH_HTML", "true").lower() in ("true", "1")
    ATTACH_HAR_DEFAULT: bool = os.getenv("ATTACH_HAR", "false").lower() in ("true", "1")
    ATTACH_PDF_DEFAULT: bool = os.getenv("ATTACH_PDF", "false").lower() in ("true", "1")
    ATTACH_SCREENSHOT_DEFAULT: bool = os.getenv("ATTACH_SCREENSHOT", "true").lower() in ("true", "1")

    # Security & Compliance
    OBEY_ROBOTS_DEFAULT: bool = os.getenv("OBEY_ROBOTS", "true").lower() in ("true", "1")
    ALLOWED_DOMAINS: list = os.getenv("ALLOWED_DOMAINS", "localhost,127.0.0.1,example.org").split(",")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs/opena6")

    # Metrics
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() in ("true", "1")
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "12349"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = OpenaConfig()
