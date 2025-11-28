#!/usr/bin/env python3
"""
Tests für opena21 - Workflow Engine
Port: 12364
"""

import pytest
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
