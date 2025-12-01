"""
opena8 Configuration Module
WhatsApp Chatbot für automatisierte Messaging-Integration
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class OpenaConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_nested_delimiter="__"
    )
    
    """Configuration for opena8 WhatsApp Agent"""

    # Service Identity
    SERVICE_NAME: str = "opena8"
    SERVICE_COMPONENT: str = "whatsapp"
    PORT: int = int(os.getenv("OPENA8_PORT", "12351"))
    
    # Archivator (opena2) Integration
    OPENA2_URL: str = os.getenv("OPENA2_URL", "http://127.0.0.1:12345")
    ARCHIV_PATH: str = os.getenv("ARCHIV_PATH", "archivp")
    
    # Coordinator (opena1) Integration
    OPENA1_URL: str = os.getenv("OPENA1_URL", "http://127.0.0.1:12344")
    
    # Meta WhatsApp Configuration
    META_API_VERSION: str = os.getenv("META_API_VERSION", "v20.0")
    META_PHONE_NUMBER_ID: str = os.getenv("META_PHONE_NUMBER_ID", "123456789012345")
    META_BUSINESS_ACCOUNT_ID: str = os.getenv("META_BUSINESS_ACCOUNT_ID", "123456789012345")
    META_ACCESS_TOKEN: str = os.getenv("META_ACCESS_TOKEN", "EAAxxxxxxxxxx...")
    META_WEBHOOK_VERIFY_TOKEN: str = os.getenv("META_WEBHOOK_VERIFY_TOKEN", "webhook_secret_32chars_min_12345")
    
    # Meta Webhook Settings
    WEBHOOK_PATH: str = os.getenv("WEBHOOK_PATH", "/webhook")
    WEBHOOK_TIMEOUT: int = int(os.getenv("WEBHOOK_TIMEOUT", "30"))
    
    # Message Processing
    MESSAGE_MAX_LENGTH: int = int(os.getenv("MESSAGE_MAX_LENGTH", "4096"))
    MEDIA_MAX_SIZE_MB: int = int(os.getenv("MEDIA_MAX_SIZE_MB", "100"))
    MEDIA_TYPES: List[str] = [
        "image", "document", "audio", "video"
    ]
    
    # Message Classification & Sentiment
    ENABLE_CLASSIFICATION: bool = os.getenv("ENABLE_CLASSIFICATION", "true").lower() in ("true", "1")
    ENABLE_SENTIMENT: bool = os.getenv("ENABLE_SENTIMENT", "true").lower() in ("true", "1")
    
    # Security & Filtering
    WHATSAPP_ALLOWLIST: List[str] = [
        s.strip() 
        for s in os.getenv("WHATSAPP_ALLOWLIST", "").split(",")
        if s.strip()
    ]
    WHATSAPP_BLOCKLIST: List[str] = [
        s.strip() 
        for s in os.getenv("WHATSAPP_BLOCKLIST", "").split(",")
        if s.strip()
    ]
    
    # Auto-Reply Settings
    AUTOREPLY_ENABLED: bool = os.getenv("AUTOREPLY_ENABLED", "false").lower() in ("true", "1")
    AUTOREPLY_TEMPLATE: str = os.getenv("AUTOREPLY_TEMPLATE", "templates/wa_reply.md")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs/opena8")
    
    # Metrics
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() in ("true", "1")
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "12351"))


config = OpenaConfig()
