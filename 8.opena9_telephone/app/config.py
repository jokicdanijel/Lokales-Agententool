"""
opena9 Configuration Module
Telephone/VoIP Agent für SIP-Integration
"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenaConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False, env_nested_delimiter="__"
    )

    """Configuration for opena9 Telephone Agent"""

    # Service Identity
    SERVICE_NAME: str = "opena9"
    SERVICE_COMPONENT: str = "telephone"
    PORT: int = int(os.getenv("OPENA9_PORT", "12352"))

    # Archivator (opena2) Integration
    OPENA2_URL: str = os.getenv("OPENA2_URL", "http://127.0.0.1:12345")
    ARCHIV_PATH: str = os.getenv("ARCHIV_PATH", "archivp")

    # Coordinator (opena1) Integration
    OPENA1_URL: str = os.getenv("OPENA1_URL", "http://127.0.0.1:12344")

    # SIP/VoIP Configuration
    SIP_SERVER: str = os.getenv("SIP_SERVER", "sip.provider.com")
    SIP_PORT: int = int(os.getenv("SIP_PORT", "5060"))
    SIP_USERNAME: str = os.getenv("SIP_USERNAME", "your_sip_username")
    SIP_PASSWORD: str = os.getenv("SIP_PASSWORD", "your_sip_password")
    SIP_DOMAIN: str = os.getenv("SIP_DOMAIN", "provider.com")

    # Voice/Audio Settings
    AUDIO_CODEC: str = os.getenv("AUDIO_CODEC", "G711")  # G711, G729, G722
    AUDIO_SAMPLE_RATE: int = int(os.getenv("AUDIO_SAMPLE_RATE", "8000"))
    DTMF_METHOD: str = os.getenv("DTMF_METHOD", "RFC2833")  # RFC2833, SIP_INFO, INBAND

    # Call Configuration
    DEFAULT_CALLER_ID: str = os.getenv("DEFAULT_CALLER_ID", "+49123456789")
    MAX_CALL_DURATION: int = int(os.getenv("MAX_CALL_DURATION", "1800"))  # 30 Minuten
    MAX_CONCURRENT_CALLS: int = int(os.getenv("MAX_CONCURRENT_CALLS", "10"))

    # Auto-Answer Settings
    AUTO_ANSWER_ENABLED: bool = os.getenv("AUTO_ANSWER_ENABLED", "false").lower() in ("true", "1")
    AUTO_ANSWER_DELAY: int = int(os.getenv("AUTO_ANSWER_DELAY", "3"))  # Sekunden

    # Call Routing
    CALL_FORWARDING_ENABLED: bool = os.getenv("CALL_FORWARDING_ENABLED", "false").lower() in ("true", "1")
    FORWARD_TO_NUMBER: str | None = os.getenv("FORWARD_TO_NUMBER")
    BUSINESS_HOURS_START: str = os.getenv("BUSINESS_HOURS_START", "08:00")
    BUSINESS_HOURS_END: str = os.getenv("BUSINESS_HOURS_END", "18:00")

    # Security & Filtering
    ALLOWED_NUMBERS: list[str] = [s.strip() for s in os.getenv("ALLOWED_NUMBERS", "").split(",") if s.strip()]
    BLOCKED_NUMBERS: list[str] = [s.strip() for s in os.getenv("BLOCKED_NUMBERS", "").split(",") if s.strip()]

    # Recording Settings
    CALL_RECORDING_ENABLED: bool = os.getenv("CALL_RECORDING_ENABLED", "false").lower() in ("true", "1")
    RECORDING_FORMAT: str = os.getenv("RECORDING_FORMAT", "WAV")  # WAV, MP3, OGG
    RECORDING_QUALITY: str = os.getenv("RECORDING_QUALITY", "medium")  # low, medium, high
    RECORDING_STORAGE_PATH: str = os.getenv("RECORDING_STORAGE_PATH", "data/recordings")

    # Voicemail Settings
    VOICEMAIL_ENABLED: bool = os.getenv("VOICEMAIL_ENABLED", "true").lower() in ("true", "1")
    VOICEMAIL_MAX_DURATION: int = int(os.getenv("VOICEMAIL_MAX_DURATION", "180"))  # 3 Minuten
    VOICEMAIL_GREETING_FILE: str = os.getenv("VOICEMAIL_GREETING_FILE", "data/greetings/default.wav")

    # Provider-specific Settings
    PROVIDER_NAME: str = os.getenv("PROVIDER_NAME", "generic")  # twilio, asterisk, freeswitch
    PROVIDER_API_KEY: str | None = os.getenv("PROVIDER_API_KEY")
    PROVIDER_WEBHOOK_SECRET: str | None = os.getenv("PROVIDER_WEBHOOK_SECRET")

    # RTP/Media Settings
    RTP_PORT_RANGE_START: int = int(os.getenv("RTP_PORT_RANGE_START", "10000"))
    RTP_PORT_RANGE_END: int = int(os.getenv("RTP_PORT_RANGE_END", "20000"))
    RTP_TIMEOUT: int = int(os.getenv("RTP_TIMEOUT", "30"))  # Sekunden

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs/opena9")
    LOG_CALLS: bool = os.getenv("LOG_CALLS", "true").lower() in ("true", "1")

    # Monitoring & Metrics
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() in ("true", "1")
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "12352"))
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))  # Sekunden


config = OpenaConfig()
