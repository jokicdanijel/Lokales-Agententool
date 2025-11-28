#!/usr/bin/env python3
"""
opena21 - Workflow Engine Configuration
Zentrale Konfiguration für Workflow-Engine
"""

import os
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from dotenv import load_dotenv

load_dotenv()


class WorkflowEngineConfig(BaseModel):
    """Konfiguration für Workflow-Engine"""
    model_config = ConfigDict(extra="forbid")
    
    # Service-Identifikation
    service_name: str = Field("opena21", description="Service-Name")
    program_target: str = Field("workflowp", description="kordp-Kürzel")
    port: int = Field(12364, description="Service-Port")
    version: str = Field("2.0", description="Service-Version")
    
    # Authentifizierung
    bearer_token: Optional[str] = Field(None, description="Bearer Token für Auth")
    
    # Workflow-Execution
    default_timeout: int = Field(300, description="Standard-Timeout in Sekunden")
    max_retry_count: int = Field(3, description="Maximale Anzahl Retries pro Step")
    step_timeout: int = Field(30, description="Standard Step-Timeout")
    
    # Storage (Produktiv: DB/Redis)
    storage_backend: str = Field("memory", description="Storage Backend (memory/redis/postgres)")
    redis_url: Optional[str] = Field(None, description="Redis Connection URL")
    db_url: Optional[str] = Field(None, description="Database Connection URL")
    
    # Logging
    log_level: str = Field("INFO", description="Log-Level")
    log_file: str = Field("logs/opena21.nohup.log", description="Log-Datei")
    
    # Portier-Integration
    portier_url: str = Field("http://127.0.0.1:12344", description="Portier (opena1) URL")
    opena2_url: str = Field("http://127.0.0.1:12345", description="OpenA2 (Archivator) URL")
    kordp_url: str = Field("http://127.0.0.1:12346", description="kordp (Gateway) URL")
    
    # Port-Policy
    allowed_ports_start: int = Field(12344, description="Erlaubter Port-Bereich Start")
    allowed_ports_end: int = Field(12399, description="Erlaubter Port-Bereich Ende")
    forbidden_ports: list[int] = Field([8080], description="Verbotene Ports")


def load_config() -> WorkflowEngineConfig:
    """Lädt Konfiguration aus Environment-Variablen"""
    return WorkflowEngineConfig(
        service_name=os.getenv("SERVICE_NAME", "opena21"),
        program_target=os.getenv("PROGRAM_TARGET", "workflowp"),
        port=int(os.getenv("OPENA21_PORT", "12364")),
        version=os.getenv("VERSION", "2.0"),
        bearer_token=os.getenv("BEARER_TOKEN"),
        default_timeout=int(os.getenv("WORKFLOW_DEFAULT_TIMEOUT", "300")),
        max_retry_count=int(os.getenv("WORKFLOW_MAX_RETRIES", "3")),
        step_timeout=int(os.getenv("WORKFLOW_STEP_TIMEOUT", "30")),
        storage_backend=os.getenv("STORAGE_BACKEND", "memory"),
        redis_url=os.getenv("REDIS_URL"),
        db_url=os.getenv("DATABASE_URL"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_file=os.getenv("LOG_FILE", "logs/opena21.nohup.log"),
        portier_url=os.getenv("PORTIER_URL", "http://127.0.0.1:12344"),
        opena2_url=os.getenv("OPENA2_URL", "http://127.0.0.1:12345"),
        kordp_url=os.getenv("KORDP_URL", "http://127.0.0.1:12346")
    )


# Globale Config-Instanz
config = load_config()
