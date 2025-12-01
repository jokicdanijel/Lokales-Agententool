#!/usr/bin/env python3
"""
Tests für opena21 - Workflow Engine
Port: 12364
"""

#!/usr/bin/env python3
"""
opena21 Workflow Engine Tests
Unit Tests für Multi-Agent Workflow Orchestrierung
"""

import pytest
import asyncio
import httpx
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch

# Import der zu testenden Module
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import (
    WorkflowDefinition, StepDefinition, ExecuteRequest, WorkflowState,
    execute_step, execute_workflow_async, call_agent_via_kordp,
    check_portier_connection, send_safepoint
)


class TestWorkflowEngine:
    """Test Suite für Workflow Engine"""
    
    def test_workflow_definition_validation(self):
        """Test Workflow-Definition Validierung"""
        # Gültiger Workflow
        workflow = WorkflowDefinition(
            name="test_workflow",
            description="Test Workflow",
            steps=[
                StepDefinition(
                    name="step1",
                    action="call_agent",
                    agent="opena3",
                    params={"test": "value"},
                    timeout=30
                )
            ],
            timeout=120
        )
        
        assert workflow.name == "test_workflow"
        assert len(workflow.steps) == 1
        assert workflow.steps[0].name == "step1"
    
    def test_step_definition_validation(self):
        """Test Step-Definition Validierung"""
        step = StepDefinition(
            name="test_step",
            action="call_agent",
            agent="opena6",
            params={"url": "https://example.com"},
            timeout=45,
            retry_count=2
        )
        
        assert step.name == "test_step"
        assert step.action == "call_agent"
        assert step.agent == "opena6"
        assert step.timeout == 45
        assert step.retry_count == 2
    
    def test_execute_request_validation(self):
        """Test Execute-Request Validierung"""
        request = ExecuteRequest(
            workflow_name="demo_workflow",
            inputs={"param1": "value1"},
            mode="sync"
        )
        
        assert request.workflow_name == "demo_workflow"
        assert request.inputs == {"param1": "value1"}
        assert request.mode == "sync"


class TestPortierIntegration:
    """Test Suite für PORTIER 3.0 Integration"""
    
    @pytest.mark.asyncio
    async def test_check_portier_connection(self):
        """Test Portier-Verbindung Check"""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Erfolgreiche Verbindung
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = await check_portier_connection()
            assert result is True
            
            # Fehlgeschlagene Verbindung
            mock_get.side_effect = Exception("Connection failed")
            result = await check_portier_connection()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_call_agent_via_kordp(self):
        """Test Agent-Aufruf via kordp Gateway"""
        with patch('httpx.AsyncClient.post') as mock_post:
            # Erfolgreicher Aufruf
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success", "data": {"result": "test"}}
            mock_post.return_value = mock_response
            
            result = await call_agent_via_kordp("opena3", "invoke", {"test": "param"})
            
            assert result["success"] is True
            assert "data" in result
            
            # Fehlgeschlagener Aufruf
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_post.return_value = mock_response
            
            result = await call_agent_via_kordp("opena3", "invoke", {"test": "param"})
            
            assert result["success"] is False
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_send_safepoint(self):
        """Test Safepoint-Archivierung"""
        from main import SafepointRequest
        
        safepoint = SafepointRequest(
            sp_id="SP123_workflowp→test_CMD",
            timestamp=datetime.now(timezone.utc).isoformat(),
            source="workflowp",
            destination="test",
            kind="CMD",
            payload={"test": "data"}
        )
        
        with patch('httpx.AsyncClient.post') as mock_post:
            # Erfolgreiche Archivierung
            mock_response = Mock()
            mock_response.status_code = 201
            mock_post.return_value = mock_response
            
            result = await send_safepoint(safepoint)
            assert result is True
            
            # Fehlgeschlagene Archivierung
            mock_post.side_effect = Exception("Archive failed")
            result = await send_safepoint(safepoint)
            assert result is False


class TestWorkflowExecution:
    """Test Suite für Workflow-Ausführung"""
    
    @pytest.mark.asyncio
    async def test_execute_step_call_agent(self):
        """Test Step-Ausführung mit Agent-Aufruf"""
        step = StepDefinition(
            name="test_step",
            action="call_agent",
            agent="opena3",
            params={"query": "test query"}
        )
        
        workflow_id = "test_workflow_123"
        context = {}
        
        with patch('main.call_agent_via_kordp') as mock_call_agent, \
             patch('main.send_safepoint') as mock_safepoint:
            
            # Mock erfolgreichen Agent-Call
            mock_call_agent.return_value = {"success": True, "data": {"response": "test response"}}
            mock_safepoint.return_value = True
            
            result = await execute_step(step, workflow_id, context)
            
            assert result["success"] is True
            assert mock_call_agent.called
            assert mock_safepoint.call_count >= 2  # CMD + RESP Safepoint
    
    @pytest.mark.asyncio
    async def test_execute_step_transform_data(self):
        """Test Step-Ausführung mit Data-Transformation"""
        step = StepDefinition(
            name="transform_step",
            action="transform_data",
            params={"input": "raw_data", "format": "json"}
        )
        
        workflow_id = "test_workflow_123"
        context = {}
        
        with patch('main.send_safepoint') as mock_safepoint:
            mock_safepoint.return_value = True
            
            result = await execute_step(step, workflow_id, context)
            
            assert result["success"] is True
            assert "data" in result
            assert result["data"]["transformed"] == step.params
    
    @pytest.mark.asyncio 
    async def test_execute_workflow_success(self):
        """Test erfolgreiche Workflow-Ausführung"""
        workflow = WorkflowDefinition(
            name="test_workflow",
            description="Test Workflow",
            steps=[
                StepDefinition(
                    name="step1",
                    action="transform_data",
                    params={"data": "test1"}
                ),
                StepDefinition(
                    name="step2", 
                    action="transform_data",
                    params={"data": "test2"}
                )
            ],
            timeout=60
        )
        
        inputs = {"initial": "data"}
        
        with patch('main.send_safepoint') as mock_safepoint:
            mock_safepoint.return_value = True
            
            result = await execute_workflow_async(workflow, inputs)
            
            assert result.state == WorkflowState.COMPLETED
            assert result.workflow_name == "test_workflow"
            assert len(result.outputs) == 2
            assert result.completed_at is not None
    
    @pytest.mark.asyncio
    async def test_execute_workflow_failure(self):
        """Test Workflow-Ausführung mit Fehler"""
        workflow = WorkflowDefinition(
            name="failing_workflow",
            steps=[
                StepDefinition(
                    name="failing_step",
                    action="call_agent",
                    agent="nonexistent_agent",
                    params={}
                )
            ],
            timeout=30
        )
        
        inputs = {}
        
        with patch('main.send_safepoint') as mock_safepoint, \
             patch('main.call_agent_via_kordp') as mock_call_agent:
            
            mock_safepoint.return_value = True
            mock_call_agent.side_effect = Exception("Agent not found")
            
            result = await execute_workflow_async(workflow, inputs)
            
            assert result.state == WorkflowState.FAILED
            assert result.error is not None


class TestValidation:
    """Test Suite für Input-Validierung"""
    
    def test_invalid_workflow_name(self):
        """Test ungültige Workflow-Namen"""
        with pytest.raises(Exception):
            WorkflowDefinition(
                name="",  # Leerer Name
                steps=[]
            )
    
    def test_step_timeout_limits(self):
        """Test Step-Timeout Grenzen"""
        # Gültiger Timeout
        step = StepDefinition(
            name="test",
            action="test",
            timeout=30
        )
        assert step.timeout == 30
        
        # Ungültige Timeouts werden durch Pydantic validiert
        with pytest.raises(ValueError):
            StepDefinition(
                name="test",
                action="test", 
                timeout=1  # Zu niedrig (< 5)
            )
        
        with pytest.raises(ValueError):
            StepDefinition(
                name="test",
                action="test",
                timeout=500  # Zu hoch (> 300)
            )
    
    def test_retry_count_limits(self):
        """Test Retry-Count Grenzen"""
        # Gültiger Retry-Count
        step = StepDefinition(
            name="test",
            action="test",
            retry_count=3
        )
        assert step.retry_count == 3
        
        # Ungültige Retry-Counts
        with pytest.raises(ValueError):
            StepDefinition(
                name="test",
                action="test",
                retry_count=-1  # Negativ
            )
        
        with pytest.raises(ValueError):
            StepDefinition(
                name="test", 
                action="test",
                retry_count=10  # Zu hoch (> 5)
            )


class TestHealthCheck:
    """Test Suite für Health-Check"""
    
    @pytest.mark.asyncio
    async def test_health_response_structure(self):
        """Test Health-Response Struktur"""
        from main import HealthResponse
        
        with patch('main.check_portier_connection') as mock_portier, \
             patch('main.check_opena2_connection') as mock_opena2:
            
            mock_portier.return_value = True
            mock_opena2.return_value = True
            
            health = HealthResponse(
                status="ok",
                service="opena21",
                port=12364,
                program_target="workflowp",
                uptime_seconds=123.45,
                version="2.0",
                workflows_count=3,
                executions_count=1,
                portier_connected=True,
                opena2_connected=True
            )
            
            assert health.status == "ok"
            assert health.service == "opena21"
            assert health.port == 12364
            assert health.program_target == "workflowp"
            assert health.portier_connected is True
            assert health.opena2_connected is True


if __name__ == "__main__":
    # Tests ausführen
    pytest.main([__file__, "-v", "--tb=short"])
import httpx
from unittest.mock import Mock, patch
import time
import os
import sys

# Path-Setup für Imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test-Konfiguration
BASE_URL = "http://127.0.0.1:12364"
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "test-token-12345")


# ==================== Health-Check Tests ====================

@pytest.mark.asyncio
async def test_health_check():
    """Test /health Endpoint (öffentlich)"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health", timeout=5.0)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert data["service"] == "opena21"
        assert data["port"] == 12364
        assert data["program_target"] == "workflowp"
        assert "uptime_seconds" in data
        assert "version" in data
        assert data["version"] == "2.0"


# ==================== Workflow Creation Tests ====================

@pytest.mark.asyncio
async def test_create_workflow():
    """Test /workflows/create Endpoint"""
    workflow_def = {
        "name": "test_workflow_001",
        "description": "Test Workflow",
        "steps": [
            {
                "name": "step1",
                "action": "call_agent",
                "agent": "opena3",
                "params": {"query": "test"}
            }
        ],
        "timeout": 60
    }
    
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/workflows/create",
            json=workflow_def,
            headers=headers,
            timeout=5.0
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "workflow" in data
        assert data["workflow"]["name"] == "test_workflow_001"


@pytest.mark.asyncio
async def test_create_workflow_duplicate():
    """Test Duplikat-Workflow wird abgelehnt"""
    workflow_def = {
        "name": "demo_multi_agent",  # Bereits beim Startup erstellt
        "description": "Duplicate Test",
        "steps": [],
        "timeout": 60
    }
    
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/workflows/create",
            json=workflow_def,
            headers=headers,
            timeout=5.0
        )
        
        assert response.status_code == 409  # Conflict
        data = response.json()
        assert "existiert bereits" in data["detail"]


# ==================== Workflow Listing Tests ====================

@pytest.mark.asyncio
async def test_list_workflows():
    """Test /workflows/list Endpoint"""
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/workflows/list",
            headers=headers,
            timeout=5.0
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "count" in data
        assert "workflows" in data
        assert data["count"] >= 1  # Mindestens demo_multi_agent


# ==================== Workflow Execution Tests ====================

@pytest.mark.asyncio
async def test_execute_workflow_sync():
    """Test synchrone Workflow-Ausführung"""
    execute_request = {
        "workflow_name": "demo_multi_agent",
        "inputs": {"test_param": "test_value"},
        "mode": "sync"
    }
    
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/workflows/execute",
            json=execute_request,
            headers=headers,
            timeout=10.0
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "execution" in data
        
        execution = data["execution"]
        assert execution["workflow_name"] == "demo_multi_agent"
        assert execution["state"] in ["completed", "failed"]
        assert "workflow_id" in execution


@pytest.mark.asyncio
async def test_execute_workflow_not_found():
    """Test Ausführung nicht-existierenden Workflows"""
    execute_request = {
        "workflow_name": "non_existent_workflow",
        "inputs": {},
        "mode": "sync"
    }
    
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/workflows/execute",
            json=execute_request,
            headers=headers,
            timeout=5.0
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "nicht gefunden" in data["detail"]


# ==================== Workflow Status Tests ====================

@pytest.mark.asyncio
async def test_workflow_status():
    """Test /workflows/status/{id} Endpoint"""
    # Erst Workflow ausführen
    execute_request = {
        "workflow_name": "demo_multi_agent",
        "inputs": {},
        "mode": "sync"
    }
    
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        # Workflow ausführen
        exec_response = await client.post(
            f"{BASE_URL}/workflows/execute",
            json=execute_request,
            headers=headers,
            timeout=10.0
        )
        
        assert exec_response.status_code == 200
        exec_data = exec_response.json()
        workflow_id = exec_data["execution"]["workflow_id"]
        
        # Status abfragen
        status_response = await client.get(
            f"{BASE_URL}/workflows/status/{workflow_id}",
            headers=headers,
            timeout=5.0
        )
        
        assert status_response.status_code == 200
        status_data = status_response.json()
        
        assert status_data["status"] == "success"
        assert status_data["execution"]["workflow_id"] == workflow_id


# ==================== Invoke Endpoint Tests (Option-2-Flow) ====================

@pytest.mark.asyncio
async def test_invoke_execute_workflow():
    """Test /invoke mit execute_workflow Action"""
    invoke_request = {
        "action": "execute_workflow",
        "params": {
            "workflow_name": "demo_multi_agent",
            "inputs": {}
        }
    }
    
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/invoke",
            json=invoke_request,
            headers=headers,
            timeout=10.0
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["action"] == "execute_workflow"
        assert "result" in data


@pytest.mark.asyncio
async def test_invoke_get_status():
    """Test /invoke mit get_status Action"""
    # Erst Workflow ausführen
    exec_request = {
        "action": "execute_workflow",
        "params": {
            "workflow_name": "demo_multi_agent",
            "inputs": {}
        }
    }
    
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        # Workflow ausführen
        exec_response = await client.post(
            f"{BASE_URL}/invoke",
            json=exec_request,
            headers=headers,
            timeout=10.0
        )
        
        workflow_id = exec_response.json()["result"]["workflow_id"]
        
        # Status via invoke abfragen
        status_request = {
            "action": "get_status",
            "params": {
                "workflow_id": workflow_id
            }
        }
        
        status_response = await client.post(
            f"{BASE_URL}/invoke",
            json=status_request,
            headers=headers,
            timeout=5.0
        )
        
        assert status_response.status_code == 200
        data = status_response.json()
        
        assert data["status"] == "success"
        assert data["action"] == "get_status"
        assert data["result"]["workflow_id"] == workflow_id


# ==================== Security Tests ====================

@pytest.mark.asyncio
async def test_auth_required():
    """Test Bearer Token wird geprüft"""
    async with httpx.AsyncClient() as client:
        # Ohne Token
        response = await client.get(
            f"{BASE_URL}/workflows/list",
            timeout=5.0
        )
        
        assert response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_auth_invalid_token():
    """Test invalider Token wird abgelehnt"""
    headers = {"Authorization": "Bearer invalid-token-xyz"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/workflows/list",
            headers=headers,
            timeout=5.0
        )
        
        # Wenn BEARER_TOKEN gesetzt ist, 401, sonst 200 (DEV-Mode)
        if os.getenv("BEARER_TOKEN"):
            assert response.status_code == 401


# ==================== Schema Validation Tests ====================

@pytest.mark.asyncio
async def test_strict_json_validation():
    """Test Pydantic extra='forbid' Validierung"""
    workflow_def = {
        "name": "test_strict",
        "steps": [],
        "timeout": 60,
        "invalid_field": "should_fail"  # Extra field
    }
    
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/workflows/create",
            json=workflow_def,
            headers=headers,
            timeout=5.0
        )
        
        assert response.status_code == 422  # Unprocessable Entity
        data = response.json()
        assert "detail" in data


# ==================== Integration Tests ====================

@pytest.mark.asyncio
async def test_full_workflow_lifecycle():
    """Test kompletter Lifecycle: Create → Execute → Status → List"""
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        # 1. Workflow erstellen
        workflow_def = {
            "name": f"lifecycle_test_{int(time.time())}",
            "description": "Lifecycle Test Workflow",
            "steps": [
                {
                    "name": "step1",
                    "action": "call_agent",
                    "agent": "opena3",
                    "params": {}
                }
            ],
            "timeout": 60
        }
        
        create_response = await client.post(
            f"{BASE_URL}/workflows/create",
            json=workflow_def,
            headers=headers,
            timeout=5.0
        )
        assert create_response.status_code == 200
        
        # 2. Workflow ausführen
        execute_request = {
            "workflow_name": workflow_def["name"],
            "inputs": {},
            "mode": "sync"
        }
        
        exec_response = await client.post(
            f"{BASE_URL}/workflows/execute",
            json=execute_request,
            headers=headers,
            timeout=10.0
        )
        assert exec_response.status_code == 200
        workflow_id = exec_response.json()["execution"]["workflow_id"]
        
        # 3. Status abfragen
        status_response = await client.get(
            f"{BASE_URL}/workflows/status/{workflow_id}",
            headers=headers,
            timeout=5.0
        )
        assert status_response.status_code == 200
        
        # 4. In Liste prüfen
        list_response = await client.get(
            f"{BASE_URL}/workflows/list",
            headers=headers,
            timeout=5.0
        )
        assert list_response.status_code == 200
        workflows = list_response.json()["workflows"]
        assert any(wf["name"] == workflow_def["name"] for wf in workflows)


# ==================== Pytest Main ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
