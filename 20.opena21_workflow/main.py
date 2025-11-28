#!/usr/bin/env python3
"""
opena21 - Workflow Engine Agent
Port: 12364
Kürzel: workflowp
Version: 2.0
Status: Production

Workflow-Orchestrierung für PORTIER 3.0 Multi-Agent-System.
Ermöglicht Definition, Ausführung und Monitoring von Multi-Step-Workflows.
"""

import os
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, ConfigDict
import uvicorn
from dotenv import load_dotenv

# Environment laden
load_dotenv()

# Konfiguration
PORT = int(os.getenv("OPENA21_PORT", "12364"))
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
SERVICE_NAME = "opena21"
PROGRAM_TARGET = "workflowp"
VERSION = "2.0"

# FastAPI App
app = FastAPI(
    title=f"{SERVICE_NAME} - Workflow Engine",
    description="Multi-Agent Workflow Orchestration für PORTIER 3.0",
    version=VERSION
)

# Security
security = HTTPBearer()
start_time = time.time()


# ==================== Schemas ====================

class WorkflowState(str, Enum):
    """Workflow-Zustandstypen"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepDefinition(BaseModel):
    """Definition eines Workflow-Steps"""
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., description="Name des Steps")
    action: str = Field(..., description="Aktion (z.B. 'call_agent', 'transform_data')")
    agent: Optional[str] = Field(None, description="Ziel-Agent (z.B. 'opena3', 'opena4')")
    params: Dict[str, Any] = Field(default_factory=dict, description="Step-Parameter")
    timeout: int = Field(30, description="Timeout in Sekunden")
    retry_count: int = Field(0, description="Anzahl Retry-Versuche")


class WorkflowDefinition(BaseModel):
    """Vollständige Workflow-Definition"""
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., description="Workflow-Name")
    description: Optional[str] = Field(None, description="Workflow-Beschreibung")
    steps: List[StepDefinition] = Field(..., description="Liste der Steps")
    timeout: int = Field(300, description="Gesamtzeit Timeout in Sekunden")


class ExecuteRequest(BaseModel):
    """Request zum Starten eines Workflows"""
    model_config = ConfigDict(extra="forbid")
    
    workflow_name: str = Field(..., description="Name des auszuführenden Workflows")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input-Parameter")
    mode: str = Field("sync", description="Ausführungsmodus (sync/async)")


class WorkflowStatus(BaseModel):
    """Status eines laufenden/abgeschlossenen Workflows"""
    model_config = ConfigDict(extra="forbid")
    
    workflow_id: str = Field(..., description="Eindeutige Workflow-ID")
    workflow_name: str = Field(..., description="Workflow-Name")
    state: WorkflowState = Field(..., description="Aktueller Zustand")
    current_step: Optional[str] = Field(None, description="Aktueller Step (wenn running)")
    started_at: str = Field(..., description="Start-Zeitstempel (ISO 8601)")
    completed_at: Optional[str] = Field(None, description="Completion-Zeitstempel")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Workflow-Outputs")
    error: Optional[str] = Field(None, description="Fehlermeldung (wenn failed)")


class InvokeRequest(BaseModel):
    """Generic Invoke Request für Option-2-Flow Kompatibilität"""
    model_config = ConfigDict(extra="forbid")
    
    action: str = Field(..., description="Aktion (z.B. 'execute_workflow', 'get_status')")
    params: Dict[str, Any] = Field(default_factory=dict, description="Action-Parameter")


class HealthResponse(BaseModel):
    """Health-Check Response"""
    model_config = ConfigDict(extra="forbid")
    
    status: str = Field(..., description="Status (ok/error)")
    service: str = Field(..., description="Service-Name")
    port: int = Field(..., description="Port-Nummer")
    program_target: str = Field(..., description="Programm-Ziel (kordp-Kürzel)")
    uptime_seconds: float = Field(..., description="Uptime in Sekunden")
    version: str = Field(..., description="Version")
    workflows_count: int = Field(0, description="Anzahl definierter Workflows")


# ==================== In-Memory Storage (Produktiv: DB/Redis) ====================

workflows_registry: Dict[str, WorkflowDefinition] = {}
executions_registry: Dict[str, WorkflowStatus] = {}


# ==================== Security ====================

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verifiziert Bearer Token"""
    if not BEARER_TOKEN:
        # DEV-Mode ohne Token
        return "dev-mode"
    
    if credentials.credentials != BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token"
        )
    return credentials.credentials


# ==================== Workflow Engine (Simplified) ====================

def execute_workflow_sync(workflow: WorkflowDefinition, inputs: Dict[str, Any]) -> WorkflowStatus:
    """
    Führt Workflow synchron aus (Simplified Version).
    Produktiv: Celery/Redis für asynchrone Ausführung.
    """
    workflow_id = f"wf_{int(time.time() * 1000)}"
    started_at = datetime.utcnow().isoformat() + "Z"
    
    status_obj = WorkflowStatus(
        workflow_id=workflow_id,
        workflow_name=workflow.name,
        state=WorkflowState.RUNNING,
        started_at=started_at,
        outputs={}
    )
    
    executions_registry[workflow_id] = status_obj
    
    try:
        # Steps ausführen
        step_outputs = {}
        for step in workflow.steps:
            status_obj.current_step = step.name
            
            # Simplified: Step-Ausführung simulieren
            # Produktiv: HTTP-Call an Ziel-Agent via kordp
            step_result = {
                "step_name": step.name,
                "action": step.action,
                "agent": step.agent,
                "success": True,
                "output": f"Step {step.name} executed successfully"
            }
            
            step_outputs[step.name] = step_result
            time.sleep(0.1)  # Simuliere Verarbeitungszeit
        
        # Workflow erfolgreich
        status_obj.state = WorkflowState.COMPLETED
        status_obj.completed_at = datetime.utcnow().isoformat() + "Z"
        status_obj.outputs = step_outputs
        status_obj.current_step = None
        
    except Exception as e:
        # Workflow fehlgeschlagen
        status_obj.state = WorkflowState.FAILED
        status_obj.completed_at = datetime.utcnow().isoformat() + "Z"
        status_obj.error = str(e)
        status_obj.current_step = None
    
    executions_registry[workflow_id] = status_obj
    return status_obj


# ==================== API Endpoints ====================

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health-Check Endpoint (öffentlich)"""
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        port=PORT,
        program_target=PROGRAM_TARGET,
        uptime_seconds=time.time() - start_time,
        version=VERSION,
        workflows_count=len(workflows_registry)
    )


@app.post("/invoke", tags=["Option-2-Flow"])
async def invoke(
    request: InvokeRequest,
    token: str = Depends(verify_token)
):
    """
    Generic Invoke Endpoint für Option-2-Flow Kompatibilität.
    Dispatcht Actions an interne Handler.
    """
    if request.action == "execute_workflow":
        # Workflow ausführen
        workflow_name = request.params.get("workflow_name")
        inputs = request.params.get("inputs", {})
        
        if not workflow_name or workflow_name not in workflows_registry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow '{workflow_name}' nicht gefunden"
            )
        
        workflow = workflows_registry[workflow_name]
        status_obj = execute_workflow_sync(workflow, inputs)
        
        return {
            "status": "success",
            "action": request.action,
            "result": status_obj.model_dump()
        }
    
    elif request.action == "get_status":
        # Status abfragen
        workflow_id = request.params.get("workflow_id")
        
        if not workflow_id or workflow_id not in executions_registry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow-ID '{workflow_id}' nicht gefunden"
            )
        
        status_obj = executions_registry[workflow_id]
        
        return {
            "status": "success",
            "action": request.action,
            "result": status_obj.model_dump()
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unbekannte Action: {request.action}"
        )


@app.post("/workflows/create", tags=["Workflows"])
async def create_workflow(
    workflow: WorkflowDefinition,
    token: str = Depends(verify_token)
):
    """Erstellt eine neue Workflow-Definition"""
    if workflow.name in workflows_registry:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Workflow '{workflow.name}' existiert bereits"
        )
    
    workflows_registry[workflow.name] = workflow
    
    return {
        "status": "success",
        "message": f"Workflow '{workflow.name}' erstellt",
        "workflow": workflow.model_dump()
    }


@app.get("/workflows/list", tags=["Workflows"])
async def list_workflows(token: str = Depends(verify_token)) -> Dict[str, Any]:
    """Listet alle definierten Workflows 


@app.post("/workflows/execute", tags=["Workflows"])
async def execute_workflow_endpoint(
    request: ExecuteRequest,
    token: str = Depends(verify_token)
):
    """Führt einen Workflow aus"""
    if request.workflow_name not in workflows_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow '{request.workflow_name}' nicht gefunden"
        )
    
    workflow = workflows_registry[request.workflow_name]
    
    if request.mode == "sync":
        status_obj = execute_workflow_sync(workflow, request.inputs)
        return {
            "status": "success",
            "execution": status_obj.model_dump()
        }
    else:
        # Async-Mode (Produktiv: Celery-Task)
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Async-Mode noch nicht implementiert"
        )


@app.get("/workflows/status/{workflow_id}", tags=["Workflows"])
async def get_workflow_status(
    workflow_id: str,
    token: str = Depends(verify_token)
):
    """Fragt Status eines Workflows ab"""
    if workflow_id not in executions_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow-ID '{workflow_id}' nicht gefunden"
        )
    
    status_obj = executions_registry[workflow_id]
    return {
        "status": "success",
        "execution": status_obj.model_dump()
    }


@app.get("/workflows/executions", tags=["Workflows"])
async def list_executions(token: str = Depends(verify_token)):
    """Listet alle Workflow-Ausführungen auf"""
    return {
        "status": "success",
        "count": len(executions_registry),
        "executions": [exec_obj.model_dump() for exec_obj in executions_registry.values()]
    }


# ==================== Startup/Shutdown ====================

@app.on_event("startup")
async def startup_event():
    """Initialisierung beim Start"""
    print(f"🚀 {SERVICE_NAME} startet auf Port {PORT}")
    print(f"📊 Program Target: {PROGRAM_TARGET}")
    print(f"🔐 Bearer Token: {'✅ Aktiviert' if BEARER_TOKEN else '⚠️  Nicht gesetzt (DEV-Mode)'}")
    
    # Demo-Workflow erstellen
    demo_workflow = WorkflowDefinition(
        name="demo_multi_agent",
        description="Demo: OpenWebUI → Browser → Email Chain",
        steps=[
            StepDefinition(
                name="query_openwebui",
                action="call_agent",
                agent="opena3",
                params={"query": "Aktuelle Nachrichten abrufen"}
            ),
            StepDefinition(
                name="analyze_browser",
                action="call_agent",
                agent="opena6",
                params={"url": "https://news.example.com"}
            ),
            StepDefinition(
                name="send_email",
                action="call_agent",
                agent="opena7",
                params={"to": "admin@example.com", "subject": "Nachrichten-Report"}
            )
        ],
        timeout=120
    )
    
    workflows_registry["demo_multi_agent"] = demo_workflow
    print(f"✅ Demo-Workflow 'demo_multi_agent' registriert (3 Steps)")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup beim Shutdown"""
    print(f"🛑 {SERVICE_NAME} wird gestoppt")


# ==================== Main ====================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
