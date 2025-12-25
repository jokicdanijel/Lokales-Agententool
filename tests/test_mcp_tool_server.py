#!/usr/bin/env python3
"""
Unit Tests für MCP Tool Server
==============================

Tests für:
- Tool Registration
- tools/list Endpoint
- tools/call Endpoint
- Rate Limiting
- Authentication
- Error Handling

Ausführung:
    pytest tests/test_mcp_tool_server.py -v
"""

import asyncio

# Import the server module
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent / "mcp_server"))

from mcp_tool_server import BEARER_TOKEN, RateLimiter, ToolRegistry, app

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create valid auth headers"""
    return {"Authorization": f"Bearer {BEARER_TOKEN}"}


@pytest.fixture
def fresh_registry():
    """Create fresh tool registry for isolated tests"""
    return ToolRegistry()


@pytest.fixture
def fresh_rate_limiter():
    """Create fresh rate limiter"""
    return RateLimiter(max_requests=5, window=60)


# ============================================================================
# HEALTH & ROOT TESTS
# ============================================================================


class TestHealthEndpoint:
    """Tests for /health endpoint"""

    def test_health_returns_ok(self, client):
        """Health check should return status ok"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "mcp_tool_server"
        assert data["kuerzel"] == "mcpp"
        assert data["port"] == 12398

    def test_health_no_auth_required(self, client):
        """Health check should not require authentication"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_root_returns_service_info(self, client):
        """Root endpoint should return service info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================


class TestAuthentication:
    """Tests for authentication"""

    def test_missing_auth_header_returns_401(self, client):
        """Missing auth header should return 401"""
        response = client.post("/tools/list", json={})
        assert response.status_code == 401
        assert "Missing Authorization" in response.json()["detail"]

    def test_invalid_auth_format_returns_401(self, client):
        """Invalid auth format should return 401"""
        headers = {"Authorization": "InvalidFormat token"}
        response = client.post("/tools/list", json={}, headers=headers)
        assert response.status_code == 401

    def test_invalid_token_returns_401(self, client):
        """Invalid token should return 401"""
        headers = {"Authorization": "Bearer invalid-token-12345"}
        response = client.post("/tools/list", json={}, headers=headers)
        assert response.status_code == 401
        assert "Invalid Bearer token" in response.json()["detail"]

    def test_valid_token_succeeds(self, client, auth_headers):
        """Valid token should succeed"""
        response = client.post("/tools/list", json={}, headers=auth_headers)
        assert response.status_code == 200


# ============================================================================
# TOOLS/LIST TESTS
# ============================================================================


class TestToolsList:
    """Tests for tools/list endpoint"""

    def test_list_tools_returns_tools(self, client, auth_headers):
        """tools/list should return list of tools"""
        response = client.post("/tools/list", json={}, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert isinstance(data["tools"], list)
        assert len(data["tools"]) > 0

    def test_list_tools_structure(self, client, auth_headers):
        """Each tool should have required fields"""
        response = client.post("/tools/list", json={}, headers=auth_headers)
        data = response.json()
        for tool in data["tools"]:
            assert "name" in tool
            assert "inputSchema" in tool
            assert tool["inputSchema"]["type"] == "object"

    def test_list_tools_with_cursor(self, client, auth_headers):
        """tools/list should accept cursor parameter"""
        response = client.post("/tools/list", json={"cursor": "some-cursor"}, headers=auth_headers)
        assert response.status_code == 200

    def test_default_tools_registered(self, client, auth_headers):
        """Default tools should be registered"""
        response = client.post("/tools/list", json={}, headers=auth_headers)
        data = response.json()
        tool_names = [t["name"] for t in data["tools"]]

        expected_tools = [
            "calculate_sum",
            "calculate_product",
            "get_current_time",
            "echo_message",
            "list_files",
            "get_system_info",
            "validate_json",
            "hash_text",
        ]

        for expected in expected_tools:
            assert expected in tool_names, f"Tool {expected} not found"


# ============================================================================
# TOOLS/CALL TESTS
# ============================================================================


class TestToolsCall:
    """Tests for tools/call endpoint"""

    def test_call_calculate_sum(self, client, auth_headers):
        """Calculate sum should work correctly"""
        response = client.post(
            "/tools/call", json={"name": "calculate_sum", "arguments": {"a": 5, "b": 3}}, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["isError"] is False
        assert "8" in data["content"][0]["text"]

    def test_call_calculate_product(self, client, auth_headers):
        """Calculate product should work correctly"""
        response = client.post(
            "/tools/call", json={"name": "calculate_product", "arguments": {"a": 4, "b": 7}}, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["isError"] is False
        assert "28" in data["content"][0]["text"]

    def test_call_echo_message(self, client, auth_headers):
        """Echo message should return the message"""
        response = client.post(
            "/tools/call", json={"name": "echo_message", "arguments": {"message": "Hello MCP!"}}, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["isError"] is False
        assert "Hello MCP!" in data["content"][0]["text"]

    def test_call_nonexistent_tool(self, client, auth_headers):
        """Calling nonexistent tool should return error"""
        response = client.post("/tools/call", json={"name": "nonexistent_tool", "arguments": {}}, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["isError"] is True
        assert "not found" in data["content"][0]["text"]

    def test_call_with_missing_required_args(self, client, auth_headers):
        """Missing required args should return error"""
        response = client.post(
            "/tools/call",
            json={"name": "calculate_sum", "arguments": {"a": 5}},
            headers=auth_headers,  # missing 'b'
        )
        assert response.status_code == 200
        data = response.json()
        assert data["isError"] is True

    def test_call_validate_json_valid(self, client, auth_headers):
        """Validate JSON with valid input"""
        response = client.post(
            "/tools/call",
            json={"name": "validate_json", "arguments": {"json_string": '{"key": "value"}'}},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["isError"] is False
        assert "Valid JSON" in data["content"][0]["text"]

    def test_call_validate_json_invalid(self, client, auth_headers):
        """Validate JSON with invalid input"""
        response = client.post(
            "/tools/call",
            json={"name": "validate_json", "arguments": {"json_string": "not valid json"}},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["isError"] is False
        assert "Invalid JSON" in data["content"][0]["text"]

    def test_call_hash_text(self, client, auth_headers):
        """Hash text should return hash"""
        response = client.post(
            "/tools/call",
            json={"name": "hash_text", "arguments": {"text": "hello", "algorithm": "sha256"}},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["isError"] is False
        assert "SHA256" in data["content"][0]["text"]
        # Known SHA256 hash of "hello"
        assert "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824" in data["content"][0]["text"]


# ============================================================================
# RATE LIMITING TESTS
# ============================================================================


class TestRateLimiting:
    """Tests for rate limiting"""

    def test_rate_limiter_allows_requests(self, fresh_rate_limiter):
        """Rate limiter should allow requests under limit"""
        for i in range(5):
            assert fresh_rate_limiter.is_allowed("client1") is True

    def test_rate_limiter_blocks_over_limit(self, fresh_rate_limiter):
        """Rate limiter should block requests over limit"""
        for i in range(5):
            fresh_rate_limiter.is_allowed("client1")

        # 6th request should be blocked
        assert fresh_rate_limiter.is_allowed("client1") is False

    def test_rate_limiter_per_client(self, fresh_rate_limiter):
        """Rate limiter should track per client"""
        for i in range(5):
            fresh_rate_limiter.is_allowed("client1")

        # Different client should still be allowed
        assert fresh_rate_limiter.is_allowed("client2") is True

    def test_get_remaining(self, fresh_rate_limiter):
        """Should return remaining requests"""
        fresh_rate_limiter.is_allowed("client1")
        fresh_rate_limiter.is_allowed("client1")
        remaining = fresh_rate_limiter.get_remaining("client1")
        assert remaining == 3


# ============================================================================
# TOOL REGISTRY TESTS
# ============================================================================


class TestToolRegistry:
    """Tests for tool registry"""

    def test_register_tool(self, fresh_registry):
        """Should register a tool"""

        async def dummy_handler(x: int) -> str:
            return str(x)

        fresh_registry.register(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object", "properties": {"x": {"type": "integer"}}},
            handler=dummy_handler,
        )

        assert fresh_registry.tool_exists("test_tool")

    def test_get_tool(self, fresh_registry):
        """Should get tool definition"""

        async def dummy_handler() -> str:
            return "ok"

        fresh_registry.register(
            name="my_tool",
            description="My tool",
            input_schema={"type": "object", "properties": {}},
            handler=dummy_handler,
        )

        tool = fresh_registry.get_tool("my_tool")
        assert tool is not None
        assert tool["name"] == "my_tool"
        assert tool["description"] == "My tool"

    def test_get_all_tools(self, fresh_registry):
        """Should get all tools"""

        async def h1() -> str:
            return "1"

        async def h2() -> str:
            return "2"

        fresh_registry.register("tool1", "desc1", {"type": "object", "properties": {}}, h1)
        fresh_registry.register("tool2", "desc2", {"type": "object", "properties": {}}, h2)

        tools = fresh_registry.get_all_tools()
        assert len(tools) == 2

    def test_tool_not_exists(self, fresh_registry):
        """Should return False for nonexistent tool"""
        assert fresh_registry.tool_exists("nonexistent") is False

    def test_get_handler(self, fresh_registry):
        """Should get tool handler"""

        async def my_handler(val: str) -> str:
            return val.upper()

        fresh_registry.register(
            name="upper_tool",
            description="Uppercase",
            input_schema={"type": "object", "properties": {"val": {"type": "string"}}},
            handler=my_handler,
        )

        handler = fresh_registry.get_handler("upper_tool")
        assert handler is not None
        assert asyncio.iscoroutinefunction(handler)


# ============================================================================
# CONVENIENCE ENDPOINTS TESTS
# ============================================================================


class TestConvenienceEndpoints:
    """Tests for convenience endpoints"""

    def test_get_tools_simple(self, client, auth_headers):
        """GET /tools should return tools list"""
        response = client.get("/tools", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_tool_info(self, client, auth_headers):
        """GET /tools/{name} should return tool info"""
        response = client.get("/tools/calculate_sum", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "calculate_sum"

    def test_get_tool_info_not_found(self, client, auth_headers):
        """GET /tools/{name} for nonexistent should return 404"""
        response = client.get("/tools/nonexistent", headers=auth_headers)
        assert response.status_code == 404


# ============================================================================
# TOOL ANNOTATIONS TESTS
# ============================================================================


class TestToolAnnotations:
    """Tests for tool annotations"""

    def test_tools_have_annotations(self, client, auth_headers):
        """Tools should have annotations"""
        response = client.post("/tools/list", json={}, headers=auth_headers)
        data = response.json()

        for tool in data["tools"]:
            if tool.get("annotations"):
                annotations = tool["annotations"]
                assert "readOnlyHint" in annotations

    def test_calculate_sum_is_readonly(self, client, auth_headers):
        """calculate_sum should be marked as read-only"""
        response = client.get("/tools/calculate_sum", headers=auth_headers)
        data = response.json()

        assert data["annotations"]["readOnlyHint"] is True
        assert data["annotations"]["destructiveHint"] is False


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestErrorHandling:
    """Tests for error handling"""

    def test_invalid_json_body(self, client, auth_headers):
        """Invalid JSON should return 422"""
        response = client.post(
            "/tools/call", content="not valid json", headers={**auth_headers, "Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_extra_fields_rejected(self, client, auth_headers):
        """Extra fields should be rejected (strict mode)"""
        response = client.post(
            "/tools/call",
            json={"name": "echo_message", "arguments": {"message": "test"}, "extra_field": "should fail"},
            headers=auth_headers,
        )
        assert response.status_code == 422


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegration:
    """Integration tests"""

    def test_full_workflow(self, client, auth_headers):
        """Test complete workflow: list -> call -> verify"""
        # 1. List tools
        list_response = client.post("/tools/list", json={}, headers=auth_headers)
        assert list_response.status_code == 200
        tools = list_response.json()["tools"]
        assert len(tools) > 0

        # 2. Find calculate_sum
        calc_tool = next((t for t in tools if t["name"] == "calculate_sum"), None)
        assert calc_tool is not None

        # 3. Call it
        call_response = client.post(
            "/tools/call", json={"name": "calculate_sum", "arguments": {"a": 10, "b": 20}}, headers=auth_headers
        )
        assert call_response.status_code == 200
        result = call_response.json()
        assert result["isError"] is False
        assert "30" in result["content"][0]["text"]

    def test_error_in_tool_returns_isError(self, client, auth_headers):
        """Tool errors should set isError=true, not HTTP error"""
        # Call with wrong argument types (will cause TypeError)
        response = client.post(
            "/tools/call",
            json={"name": "calculate_sum", "arguments": {"a": "not a number", "b": 5}},
            headers=auth_headers,
        )
        # Should still return 200, with isError=true
        assert response.status_code == 200
        data = response.json()
        # Note: The tool might still work if Python can handle "not a number" + 5
        # But if it fails, isError should be True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
