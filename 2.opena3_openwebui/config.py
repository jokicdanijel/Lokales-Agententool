#!/usr/bin/env python3
"""
opena3 - OpenWebUI Terminal
Konfigurationsmodul

Port: 12347
Kürzel: owuip

PORTIER 3.0 konform

Version: 2.0 (erweitert mit Multi-Model, Rate-Limiting, Logging-Config)
"""

import logging
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# ══════════════════════════════════════════════════════════════════════════════
# PORT POLICY
# ══════════════════════════════════════════════════════════════════════════════


class PortPolicy:
    """PORTIER 3.0 Port Policy Enforcement"""

    ALLOWED_RANGE = range(12344, 12400)
    FORBIDDEN_PORTS = [8080]

    @classmethod
    def is_valid_port(cls, port: int) -> bool:
        return port in cls.ALLOWED_RANGE and port not in cls.FORBIDDEN_PORTS

    @classmethod
    def get_allowed_origins(cls) -> list[str]:
        origins = ["http://127.0.0.1:8080"]
        for port in cls.ALLOWED_RANGE:
            if port not in cls.FORBIDDEN_PORTS:
                origins.append(f"http://127.0.0.1:{port}")
        return origins


# ══════════════════════════════════════════════════════════════════════════════
# MODEL CONFIGURATION (Multi-Model-Support)
# ══════════════════════════════════════════════════════════════════════════════


class ModelInfo(BaseModel):
    """Einzelnes Modell in der Konfiguration"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Interne Modell-ID (für Backend)")
    name: str = Field(..., description="Anzeigename")
    type: str = Field(default="llm", description="Typ: llm, embedding, etc.")
    tags: list[str] = Field(default_factory=list, description="Tags für Filterung")
    default: bool = Field(default=False, description="Ist dies das Default-Modell?")
    backend: str = Field(default="openwebui", description="Backend: openwebui, ollama, localagent")


class ModelRegistry:
    """
    Zentrale Modell-Registry mit Alias-Mapping.
    Ermöglicht dynamische Modell-Konfiguration ohne Hardcoding.
    """

    # Default-Modelle (können via ENV/Config überschrieben werden)
    DEFAULT_MODELS: dict[str, ModelInfo] = {
        "llama3.1": ModelInfo(
            id="llama3.1:8b",
            name="LLaMA 3.1 (8B)",
            type="llm",
            tags=["chat", "general"],
            default=True,
            backend="ollama",
        ),
        "gpt-4": ModelInfo(
            id="gpt-4-turbo",
            name="GPT-4 Turbo",
            type="llm",
            tags=["chat", "advanced"],
            default=False,
            backend="openwebui",
        ),
        "codellama": ModelInfo(
            id="codellama:13b",
            name="Code LLaMA (13B)",
            type="llm",
            tags=["code", "programming"],
            default=False,
            backend="ollama",
        ),
    }

    def __init__(self, custom_models: dict[str, dict[str, Any]] | None = None):
        """Initialisiert Registry mit optionalen Custom-Modellen"""
        self._models: dict[str, ModelInfo] = dict(self.DEFAULT_MODELS)

        # Custom-Modelle hinzufügen/überschreiben
        if custom_models:
            for alias, model_dict in custom_models.items():
                self._models[alias] = ModelInfo(**model_dict)

    def get_model(self, alias: str) -> ModelInfo | None:
        """Gibt Modell für Alias zurück oder None"""
        return self._models.get(alias)

    def resolve_model_id(self, alias: str) -> str:
        """Resolves Alias → interne Modell-ID. Raises ValueError bei unbekanntem Alias."""
        model = self.get_model(alias)
        if model is None:
            available = ", ".join(self._models.keys())
            raise ValueError(f"Unbekanntes Modell-Alias: '{alias}'. Verfügbar: {available}")
        return model.id

    def get_default_model(self) -> ModelInfo | None:
        """Gibt das Default-Modell zurück"""
        for model in self._models.values():
            if model.default:
                return model
        return next(iter(self._models.values()), None)

    def list_models(self) -> list[dict[str, Any]]:
        """Gibt Liste aller Modelle zurück"""
        return [
            {
                "alias": alias,
                "id": model.id,
                "name": model.name,
                "type": model.type,
                "tags": model.tags,
                "default": model.default,
                "backend": model.backend,
            }
            for alias, model in self._models.items()
        ]

    def add_model(self, alias: str, model: ModelInfo) -> None:
        """Fügt neues Modell hinzu"""
        self._models[alias] = model

    @property
    def available_aliases(self) -> list[str]:
        """Gibt alle verfügbaren Aliase zurück"""
        return list(self._models.keys())


# ══════════════════════════════════════════════════════════════════════════════
# RATE LIMITING CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════


class RateLimitConfig(BaseModel):
    """Rate-Limit-Konfiguration pro Endpoint/Client"""

    model_config = ConfigDict(extra="forbid")

    # Globale Limits
    global_requests_per_minute: int = Field(default=60, ge=1, description="Globale Requests/Minute")
    global_requests_per_hour: int = Field(default=1000, ge=1, description="Globale Requests/Stunde")

    # Pro-Client Limits
    client_requests_per_minute: int = Field(default=30, ge=1, description="Requests/Minute pro Client")
    client_burst_size: int = Field(default=10, ge=1, description="Burst-Size (schnelle Aufeinanderfolge)")

    # Endpoint-spezifische Limits
    chat_requests_per_minute: int = Field(default=20, ge=1, description="Chat-Requests/Minute")
    stream_requests_per_minute: int = Field(default=10, ge=1, description="Stream-Requests/Minute")

    # Retry-After Zeit in Sekunden
    retry_after_seconds: int = Field(default=60, ge=1, description="Retry-After Header Wert")

    # Rate-Limit aktivieren/deaktivieren
    enabled: bool = Field(default=True, description="Rate-Limiting aktiviert")


# ══════════════════════════════════════════════════════════════════════════════
# RETRY CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════


class RetryConfig(BaseModel):
    """Konfiguration für Retry mit Exponential Backoff"""

    model_config = ConfigDict(extra="forbid")

    max_retries: int = Field(default=3, ge=0, le=10, description="Maximale Retry-Versuche")
    base_delay: float = Field(default=0.5, ge=0.1, le=10.0, description="Basis-Delay in Sekunden")
    max_delay: float = Field(default=30.0, ge=1.0, le=120.0, description="Max Delay in Sekunden")
    exponential_base: float = Field(default=2.0, ge=1.5, le=4.0, description="Exponential-Faktor")

    # Retryable Status-Codes
    retryable_status_codes: list[int] = Field(
        default=[502, 503, 504], description="HTTP-Status-Codes, bei denen Retry durchgeführt wird"
    )

    # Retry bei Connection-Errors
    retry_on_connection_error: bool = Field(default=True, description="Retry bei Connection-Errors")
    retry_on_timeout: bool = Field(default=True, description="Retry bei Timeouts")

    def get_delay(self, attempt: int) -> float:
        """Berechnet Delay für gegebenen Retry-Versuch (0-basiert)"""
        delay = self.base_delay * (self.exponential_base**attempt)
        return min(delay, self.max_delay)


# ══════════════════════════════════════════════════════════════════════════════
# LOGGING CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════


class LoggingConfig(BaseModel):
    """Erweiterte Logging-Konfiguration"""

    model_config = ConfigDict(extra="forbid")

    level: str = Field(default="INFO", description="Log-Level: DEBUG, INFO, WARNING, ERROR")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log-Format-String")

    # JSON-Logging
    json_logging: bool = Field(default=False, description="Strukturiertes JSON-Logging aktivieren")

    # Rotation
    max_file_size_mb: int = Field(default=10, ge=1, le=100, description="Max Logfile-Größe in MB")
    backup_count: int = Field(default=5, ge=1, le=20, description="Anzahl Backup-Dateien")

    # Ausgabe-Ziele
    log_to_console: bool = Field(default=True, description="Logging zur Console")
    log_to_file: bool = Field(default=True, description="Logging in Datei")
    log_file_name: str = Field(default="opena3.log", description="Logfile-Name")

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        valid = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid:
            raise ValueError(f"Ungültiger Log-Level: {v}. Erlaubt: {valid}")
        return v.upper()

    def get_numeric_level(self) -> int:
        """Gibt numerischen Log-Level zurück"""
        return getattr(logging, self.level, logging.INFO)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN SERVICE CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════


class ServiceConfig(BaseSettings):
    """Hauptkonfiguration für opena3 (erweitert)"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Basic Info
    service_name: str = "opena3"
    kuerzel: str = "owuip"
    port: int = 12347
    version: str = "3.1"

    # Auth
    bearer_token: str = Field(default="c899b90d-faf8-485b-afa4-078357cf5313", alias="BEARER_TOKEN")

    # Pfade
    base_dir: Path = Path(__file__).parent

    # Externe Services
    opena1_url: str = Field(default="http://127.0.0.1:12344", alias="OPENA1_URL")
    opena2_url: str = Field(default="http://127.0.0.1:12345", alias="OPENA2_URL")
    opena20_url: str = Field(default="http://127.0.0.1:12349", alias="OPENA20_URL")
    openwebui_url: str = Field(default="http://127.0.0.1:3000", alias="OPENWEBUI_URL")
    adapter_url: str = Field(default="http://127.0.0.1:12350", alias="OPENWEBUI_ADAPTER_URL")
    localagent_url: str = Field(default="http://127.0.0.1:8001", alias="LOCALAGENT_URL")

    # Timeouts
    timeout: int = Field(default=30, alias="OPENA3_TIMEOUT")
    stream_timeout: int = Field(default=120, alias="OPENA3_STREAM_TIMEOUT")

    # Logging (legacy, wird durch LoggingConfig ersetzt)
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @property
    def data_dir(self) -> Path:
        return self.base_dir / "data"

    @property
    def logs_dir(self) -> Path:
        return self.base_dir / "logs"


class AgentInfo(BaseModel):
    """Agent-Informationen"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent Name")
    kuerzel: str = Field(..., description="PORTIER Kürzel")
    port: int = Field(..., description="Service Port")
    enabled: bool = Field(default=True)


# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CONFIG INSTANCES
# ══════════════════════════════════════════════════════════════════════════════

_config: ServiceConfig | None = None
_model_registry: ModelRegistry | None = None
_rate_limit_config: RateLimitConfig | None = None
_retry_config: RetryConfig | None = None
_logging_config: LoggingConfig | None = None


def load_config() -> ServiceConfig:
    """Lädt/cached ServiceConfig"""
    global _config
    if _config is None:
        _config = ServiceConfig()
        _config.data_dir.mkdir(exist_ok=True)
        _config.logs_dir.mkdir(exist_ok=True)
    return _config


def get_model_registry() -> ModelRegistry:
    """Lädt/cached ModelRegistry"""
    global _model_registry
    if _model_registry is None:
        # Custom-Modelle aus ENV laden (optional)
        custom_json = os.getenv("OPENA3_CUSTOM_MODELS")
        custom_models = None
        if custom_json:
            import json

            try:
                custom_models = json.loads(custom_json)
            except json.JSONDecodeError:
                pass
        _model_registry = ModelRegistry(custom_models)
    return _model_registry


def get_rate_limit_config() -> RateLimitConfig:
    """Lädt/cached RateLimitConfig"""
    global _rate_limit_config
    if _rate_limit_config is None:
        _rate_limit_config = RateLimitConfig(
            enabled=os.getenv("OPENA3_RATE_LIMIT_ENABLED", "true").lower() == "true",
            global_requests_per_minute=int(os.getenv("OPENA3_GLOBAL_RPM", "60")),
            client_requests_per_minute=int(os.getenv("OPENA3_CLIENT_RPM", "30")),
            chat_requests_per_minute=int(os.getenv("OPENA3_CHAT_RPM", "20")),
            stream_requests_per_minute=int(os.getenv("OPENA3_STREAM_RPM", "10")),
        )
    return _rate_limit_config


def get_retry_config() -> RetryConfig:
    """Lädt/cached RetryConfig"""
    global _retry_config
    if _retry_config is None:
        _retry_config = RetryConfig(
            max_retries=int(os.getenv("OPENA3_MAX_RETRIES", "3")),
            base_delay=float(os.getenv("OPENA3_RETRY_BASE_DELAY", "0.5")),
        )
    return _retry_config


def get_logging_config() -> LoggingConfig:
    """Lädt/cached LoggingConfig"""
    global _logging_config
    if _logging_config is None:
        _logging_config = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            json_logging=os.getenv("OPENA3_JSON_LOGGING", "false").lower() == "true",
            max_file_size_mb=int(os.getenv("OPENA3_LOG_MAX_SIZE_MB", "10")),
            backup_count=int(os.getenv("OPENA3_LOG_BACKUP_COUNT", "5")),
        )
    return _logging_config


__all__ = [
    # Core
    "PortPolicy",
    "ServiceConfig",
    "AgentInfo",
    "load_config",
    # Multi-Model
    "ModelInfo",
    "ModelRegistry",
    "get_model_registry",
    # Rate-Limiting
    "RateLimitConfig",
    "get_rate_limit_config",
    # Retry
    "RetryConfig",
    "get_retry_config",
    # Logging
    "LoggingConfig",
    "get_logging_config",
]
