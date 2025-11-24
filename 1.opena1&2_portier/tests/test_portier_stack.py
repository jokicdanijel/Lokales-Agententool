"""
Test Suite — Portier 2.0 Stack (opena1 + opena2 + kordp)
End-to-End tests for Option-2-Flow validation.
LOCATION: /home/danijel-jd/.../1.opena1&2_portier/tests/test_portier_stack.py
"""

import pytest
import httpx
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


# Test Configuration
BASE_URL_OPENA1 = "http://127.0.0.1:12344"
BASE_URL_OPENA2 = "http://127.0.0.1:12345"
BASE_URL_KORDP = "http://127.0.0.1:12346"
TIMEOUT = 10


def utc():
    """Generate UTC timestamp with Z suffix."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def generate_request_id():
    """Generate UUID4 request ID."""
    return str(uuid.uuid4())


# ============================================================================
# HEALTH CHECKS
# ============================================================================

@pytest.mark.asyncio
async def test_opena2_health():
    """Test opena2 (Archivator) health endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL_OPENA2}/health", timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "opena2"
        assert data["role"] == "archivp"
        assert data["port"] == 12345
        assert data["strict"] is True
        print("✅ opena2 health check passed")


@pytest.mark.asyncio
async def test_opena1_health():
    """Test opena1 (Coordinator) health endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL_OPENA1}/health", timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "opena1"
        assert "port_policy" in data
        assert data["port_policy"]["forbidden"] == [8080]
        print("✅ opena1 health check passed")


@pytest.mark.asyncio
async def test_kordp_health():
    """Test kordp (Gateway) health endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL_KORDP}/health", timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "kordp"
        assert data["role"] == "gateway"
        print("✅ kordp health check passed")


# ============================================================================
# SCHEMA VALIDATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_opena1_request71_validation():
    """Test opena1 Request71 schema validation."""
    request_id = generate_request_id()
    
    valid_request = {
        "request_id": request_id,
        "timestamp": utc(),
        "command": "analyze project files",
        "payload": {"path": "/home/user/project"},
        "routing": {"resolved_path": None},
        "project": {"id": "test-project", "name": "Test Project"},
        "strict": True
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL_OPENA1}/log/opena1",
            json=valid_request,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["request_id"] == request_id
        assert data["source"] == "opena1"
        assert "decision" in data
        assert data["strict"] is True
        print(f"✅ Request71 validation passed (request_id: {request_id})")


@pytest.mark.asyncio
async def test_opena1_invalid_request71():
    """Test opena1 rejects invalid Request71."""
    invalid_request = {
        "request_id": "invalid-uuid",  # Invalid UUID
        "timestamp": "not-iso-8601",   # Invalid timestamp
        "command": "test"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL_OPENA1}/log/opena1",
            json=invalid_request,
            timeout=TIMEOUT
        )
        assert response.status_code == 400
        print("✅ Invalid Request71 rejected correctly")


# ============================================================================
# DECISION72 RESPONSE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_opena1_decision72_file_command():
    """Test Decision72 for file command."""
    request_id = generate_request_id()
    
    request = {
        "request_id": request_id,
        "timestamp": utc(),
        "command": "list files in directory",
        "payload": {},
        "routing": {"resolved_path": None},
        "project": {"id": "test", "name": "Test"},
        "strict": True
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL_OPENA1}/log/opena1",
            json=request,
            timeout=TIMEOUT
        )
        data = response.json()
        
        assert data["decision"]["selected_tool"] == "tool_file_manager"
        assert "file" in data["decision"]["reason"].lower()
        assert data["archivator_forward"]["status"] == "sent"
        print("✅ Decision72 file command routing correct")


@pytest.mark.asyncio
async def test_opena1_decision72_search_command():
    """Test Decision72 for search command."""
    request_id = generate_request_id()
    
    request = {
        "request_id": request_id,
        "timestamp": utc(),
        "command": "search for text in files",
        "payload": {},
        "routing": {"resolved_path": None},
        "project": {"id": "test", "name": "Test"},
        "strict": True
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL_OPENA1}/log/opena1",
            json=request,
            timeout=TIMEOUT
        )
        data = response.json()
        
        assert data["decision"]["selected_tool"] == "tool_file_searcher"
        assert "search" in data["decision"]["reason"].lower()
        print("✅ Decision72 search command routing correct")


@pytest.mark.asyncio
async def test_opena1_decision72_analyze_command():
    """Test Decision72 for analyze command."""
    request_id = generate_request_id()
    
    request = {
        "request_id": request_id,
        "timestamp": utc(),
        "command": "analyze code complexity",
        "payload": {},
        "routing": {"resolved_path": None},
        "project": {"id": "test", "name": "Test"},
        "strict": True
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL_OPENA1}/log/opena1",
            json=request,
            timeout=TIMEOUT
        )
        data = response.json()
        
        assert data["decision"]["selected_tool"] == "tool_text_analyzer"
        assert "analyze" in data["decision"]["reason"].lower()
        print("✅ Decision72 analyze command routing correct")


# ============================================================================
# SAFEPOINT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_opena2_cmd_safepoint():
    """Test opena2 CMD safepoint creation."""
    request_id = generate_request_id()
    
    cmd_payload = {
        "request_id": request_id,
        "timestamp": utc(),
        "source": "opena1",
        "cmd": {
            "command": "test command",
            "tool": "tool_test",
            "reason": "test reason",
            "payload": {"test": "data"}
        },
        "strict": True
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL_OPENA2}/finalize/opena2",
            json=cmd_payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["ok"] is True
        assert data["request_id"] == request_id
        assert "stored" in data
        print(f"✅ CMD safepoint created: {data['stored']}")


@pytest.mark.asyncio
async def test_opena2_resp_safepoint():
    """Test opena2 RESP safepoint creation."""
    request_id = generate_request_id()
    
    resp_payload = {
        "request_id": request_id,
        "timestamp": utc(),
        "source": "tool_test",
        "result": {"status": "success", "data": {"test": "result"}},
        "strict": True
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL_OPENA2}/store/resp",
            json=resp_payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["ok"] is True
        assert data["request_id"] == request_id
        print(f"✅ RESP safepoint created: {data['stored']}")


# ============================================================================
# KORDP GATEWAY TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_kordp_routes_list():
    """Test kordp route listing."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL_KORDP}/dispatch/routes", timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert data["ok"] is True
        assert "routes" in data
        assert data["count"] > 0
        
        # Check default tools are registered
        routes = data["routes"]
        tool_ids = [r["tool_id"] for r in routes]
        assert "tool_file_manager" in tool_ids
        assert "tool_file_searcher" in tool_ids
        assert "tool_text_analyzer" in tool_ids
        print(f"✅ kordp routes available: {data['count']}")


@pytest.mark.asyncio
async def test_kordp_route_detail():
    """Test kordp route detail retrieval."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL_KORDP}/dispatch/routes/tool_file_manager",
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["ok"] is True
        assert data["tool"] == "tool_file_manager"
        assert "route" in data
        assert data["route"]["enabled"] is True
        print("✅ kordp route detail retrieval works")


# ============================================================================
# END-TO-END OPTION-2-FLOW TEST
# ============================================================================

@pytest.mark.asyncio
async def test_complete_option2_flow():
    """
    Complete End-to-End test of Option-2-Flow:
    OpenAI → opena1 → opena2 → kordp → Tool
    """
    request_id = generate_request_id()
    
    # Step 1: Send Request71 to opena1
    request = {
        "request_id": request_id,
        "timestamp": utc(),
        "command": "analyze project structure",
        "payload": {"project_path": "/home/user/test"},
        "routing": {"resolved_path": None},
        "project": {"id": "e2e-test", "name": "E2E Test Project"},
        "strict": True
    }
    
    async with httpx.AsyncClient() as client:
        # Step 1: opena1 receives Request71
        print(f"\n🟦 Step 1: Sending Request71 to opena1 (request_id: {request_id})")
        response = await client.post(
            f"{BASE_URL_OPENA1}/log/opena1",
            json=request,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        decision = response.json()
        
        # Validate Decision72
        assert decision["request_id"] == request_id
        assert decision["source"] == "opena1"
        assert decision["decision"]["selected_tool"] == "tool_text_analyzer"
        assert decision["archivator_forward"]["status"] == "sent"
        assert decision["status"] == "FORWARDED"
        print(f"✅ Step 1: Decision72 received (tool: {decision['decision']['selected_tool']})")
        
        # Step 2: Verify CMD safepoint in opena2
        print("🟦 Step 2: Verifying CMD safepoint in opena2")
        # (Safepoint is created automatically by opena1 → opena2 forwarding)
        health_response = await client.get(f"{BASE_URL_OPENA2}/health", timeout=TIMEOUT)
        health_data = health_response.json()
        assert health_data["entries"] > 0
        print(f"✅ Step 2: Safepoints exist (count: {health_data['entries']})")
        
        # Step 3: Verify kordp can route the tool
        print("🟦 Step 3: Verifying kordp tool routing")
        route_response = await client.get(
            f"{BASE_URL_KORDP}/dispatch/routes/tool_text_analyzer",
            timeout=TIMEOUT
        )
        assert route_response.status_code == 200
        route_data = route_response.json()
        assert route_data["route"]["enabled"] is True
        print(f"✅ Step 3: Tool route confirmed (url: {route_data['route']['url']})")
        
        print("\n🎯 END-TO-END OPTION-2-FLOW TEST PASSED!")
        print(f"   Request ID: {request_id}")
        print(f"   Tool Selected: {decision['decision']['selected_tool']}")
        print(f"   Flow: OpenAI → opena1 → opena2 → kordp → Tool ✅")


# ============================================================================
# PORT POLICY TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_port_policy_enforcement():
    """Test that port 8080 is forbidden in policy."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL_OPENA1}/health", timeout=TIMEOUT)
        data = response.json()
        
        assert 8080 in data["port_policy"]["forbidden"]
        assert data["port_policy"]["window"] == [12344, 12349]
        print("✅ Port policy enforced (8080 forbidden)")


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
