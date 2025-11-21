"""
opena7 Configuration Module
Mail Agent für automatisierte E-Mail-Kommunikation
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List


class OpenaConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_nested_delimiter="__"
    )
    """Configuration for opena7 Mail Agent"""

    # Service Identity
    SERVICE_NAME: str = "opena7"
    SERVICE_COMPONENT: str = "mail"
    PORT: int = int(os.getenv("OPENA7_PORT", "12350"))
    
    # Archivator (opena2) Integration
    OPENA2_URL: str = os.getenv("OPENA2_URL", "http://127.0.0.1:12345")
    ARCHIV_PATH: str = os.getenv("ARCHIV_PATH", "archivp")
    
    # Coordinator (opena1) Integration
    OPENA1_URL: str = os.getenv("OPENA1_URL", "http://127.0.0.1:12344")
    
    # Mail Server Configuration (IMAP)
    MAIL_IMAP_HOST: str = os.getenv("MAIL_IMAP_HOST", "imap.provider.at")
    MAIL_IMAP_PORT: int = int(os.getenv("MAIL_IMAP_PORT", "993"))
    MAIL_IMAP_SSL: bool = os.getenv("MAIL_IMAP_SSL", "true").lower() in ("true", "1")
    
    # Mail Server Configuration (SMTP)
    MAIL_SMTP_HOST: str = os.getenv("MAIL_SMTP_HOST", "smtp.provider.at")
    MAIL_SMTP_PORT: int = int(os.getenv("MAIL_SMTP_PORT", "587"))
    MAIL_SMTP_TLS: bool = os.getenv("MAIL_SMTP_TLS", "true").lower() in ("true", "1")
    
    # Mail Credentials (from secret store, not .env!)
    MAIL_USER: str = os.getenv("MAIL_USER", "bot@example.org")
    MAIL_PASS_ENVKEY: str = os.getenv("MAIL_PASS_ENVKEY", "ENV:MAIL_PASS_TOKEN")
    
    # Mail Processing
    MAIL_CHECK_INTERVAL: str = os.getenv("MAIL_CHECK_INTERVAL", "PT5M")  # ISO-8601
    MAIL_ATTACHMENT_LIMIT_MB: int = int(os.getenv("MAIL_ATTACHMENT_LIMIT_MB", "25"))
    MAIL_BODY_PREVIEW_CHARS: int = int(os.getenv("MAIL_BODY_PREVIEW_CHARS", "500"))
    
    # Security & Filtering
    MAIL_ALLOWLIST: List[str] = [
        s.strip() 
        for s in os.getenv("MAIL_ALLOWLIST", "localhost,127.0.0.1,@example.org").split(",")
    ]
    MAIL_BLOCKLIST: List[str] = [
        s.strip() 
        for s in os.getenv("MAIL_BLOCKLIST", "").split(",")
        if s.strip()
    ]
    
    # Classification & Sentiment
    ENABLE_SENTIMENT: bool = os.getenv("ENABLE_SENTIMENT", "true").lower() in ("true", "1")
    ENABLE_LANGUAGE_DETECTION: bool = os.getenv("ENABLE_LANGUAGE_DETECTION", "true").lower() in ("true", "1")
    
    # Auto-Reply Configuration
    AUTOREPLY_ENABLED: bool = os.getenv("AUTOREPLY_ENABLED", "false").lower() in ("true", "1")
    AUTOREPLY_TEMPLATE: str = os.getenv("AUTOREPLY_TEMPLATE", "templates/auto_reply.md")
    
    # Attachment Handling
    SCAN_ATTACHMENTS: bool = os.getenv("SCAN_ATTACHMENTS", "true").lower() in ("true", "1")
    DANGEROUS_EXTENSIONS: List[str] = [
        ".exe", ".dll", ".zip", ".rar", ".bat", ".cmd", ".scr", ".vbs", ".js"
    ]
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs/opena7")
    
    # Metrics
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() in ("true", "1")
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "12350"))


config = OpenaConfig()
