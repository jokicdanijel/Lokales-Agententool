#!/usr/bin/env python3
"""
API Tests for LocalAgent-Pro
Tests for Flask endpoints and OpenWebUI compatibility
"""

import time

import pytest
import requests

# Test configuration
BASE_URL = "http://localhost:8001"
TIMEOUT = 5


class TestHealthCheck:
    """Test health check endpoint"""

    def test_health_endpoint_exists(self):
        """Test that health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        assert response.status_code == 200

    def test_health_response_format(self):
        """Test health check response format"""
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        data = response.json()

        assert "status" in data
        assert "version" in data
        assert "sandbox" in data
        assert "timestamp" in data

        assert data["status"] == "healthy"

    def test_health_response_json(self):
        """Test health check returns valid JSON"""
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        assert response.headers["Content-Type"] == "application/json"


class TestModelsEndpoint:
    """Test models listing endpoint"""

    def test_models_endpoint_exists(self):
        """Test that models endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/v1/models", timeout=TIMEOUT)
        assert response.status_code == 200

    def test_models_response_format(self):
        """Test models response format (OpenAI-compatible)"""
        response = requests.get(f"{BASE_URL}/v1/models", timeout=TIMEOUT)
        data = response.json()

        assert "object" in data
        assert "data" in data
        assert data["object"] == "list"
        assert isinstance(data["data"], list)

    def test_models_data_structure(self):
        """Test model data structure"""
        response = requests.get(f"{BASE_URL}/v1/models", timeout=TIMEOUT)
        data = response.json()

        if len(data["data"]) > 0:
            model = data["data"][0]
            assert "id" in model
            assert "object" in model
            assert "created" in model
            assert "owned_by" in model


class TestChatCompletions:
    """Test chat completions endpoint"""

    def test_chat_completions_endpoint_exists(self):
        """Test chat completions endpoint"""
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Hello"}]},
            timeout=TIMEOUT,
        )
        assert response.status_code == 200

    def test_chat_completions_response_format(self):
        """Test OpenAI-compatible response format"""
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Hello"}]},
            timeout=TIMEOUT,
        )
        data = response.json()

        assert "id" in data
        assert "object" in data
        assert "created" in data
        assert "model" in data
        assert "choices" in data

        assert data["object"] == "chat.completion"
        assert isinstance(data["choices"], list)

    def test_chat_completions_choices_structure(self):
        """Test choices array structure"""
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Hello"}]},
            timeout=TIMEOUT,
        )
        data = response.json()

        assert len(data["choices"]) > 0
        choice = data["choices"][0]

        assert "index" in choice
        assert "message" in choice
        assert "finish_reason" in choice

        assert "role" in choice["message"]
        assert "content" in choice["message"]

    def test_chat_completions_empty_message(self):
        """Test with empty message array"""
        response = requests.post(f"{BASE_URL}/v1/chat/completions", json={"messages": []}, timeout=TIMEOUT)
        # Should still return 200 or handle gracefully
        assert response.status_code in [200, 400]

    def test_chat_completions_missing_messages(self):
        """Test with missing messages field"""
        response = requests.post(f"{BASE_URL}/v1/chat/completions", json={}, timeout=TIMEOUT)
        # Should handle missing messages field
        assert response.status_code in [200, 400]


class TestToolCalling:
    """Test tool calling functionality"""

    def test_write_file_tool(self):
        """Test write_file tool detection"""
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Erstelle test.txt\nHello World!"}]},
            timeout=TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        assert "success" in content.lower() or "tool executed" in content.lower()

    def test_read_file_tool(self):
        """Test read_file tool detection"""
        # First create a file
        requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Erstelle read_test.txt\nTest content"}]},
            timeout=TIMEOUT,
        )

        # Then read it
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Lies read_test.txt"}]},
            timeout=TIMEOUT,
        )
        assert response.status_code == 200

    def test_delete_file_tool(self):
        """Test delete_file tool detection"""
        # First create a file
        requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Erstelle delete_test.txt\nTo be deleted"}]},
            timeout=TIMEOUT,
        )

        # Then delete it
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Lösche delete_test.txt"}]},
            timeout=TIMEOUT,
        )
        assert response.status_code == 200


class TestRequestDeduplication:
    """Test request deduplication"""

    def test_duplicate_request_detection(self):
        """Test that duplicate requests are detected"""
        request_data = {"messages": [{"role": "user", "content": "Unique message for dedup test"}]}

        # First request
        response1 = requests.post(f"{BASE_URL}/v1/chat/completions", json=request_data, timeout=TIMEOUT)
        assert response1.status_code == 200

        # Duplicate request (immediate)
        response2 = requests.post(f"{BASE_URL}/v1/chat/completions", json=request_data, timeout=TIMEOUT)

        # Should either succeed or return 429
        assert response2.status_code in [200, 429]


class TestMetricsEndpoint:
    """Test Prometheus metrics endpoint"""

    def test_metrics_endpoint_exists(self):
        """Test metrics endpoint accessibility"""
        response = requests.get(f"{BASE_URL}/metrics", timeout=TIMEOUT)
        assert response.status_code == 200

    def test_metrics_format(self):
        """Test metrics are in Prometheus format"""
        response = requests.get(f"{BASE_URL}/metrics", timeout=TIMEOUT)
        content = response.text

        # Should contain HELP and TYPE comments
        assert "# HELP" in content
        assert "# TYPE" in content

    def test_metrics_contains_expected_data(self):
        """Test that expected metrics are present"""
        response = requests.get(f"{BASE_URL}/metrics", timeout=TIMEOUT)
        content = response.text

        assert "http_requests_total" in content
        assert "sandbox_files" in content


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_json(self):
        """Test with invalid JSON"""
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT,
        )
        assert response.status_code in [400, 500]

    def test_invalid_content_type(self):
        """Test with invalid content type"""
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions", data="some data", headers={"Content-Type": "text/plain"}, timeout=TIMEOUT
        )
        assert response.status_code in [400, 415, 500]

    def test_nonexistent_endpoint(self):
        """Test accessing non-existent endpoint"""
        response = requests.get(f"{BASE_URL}/v1/nonexistent", timeout=TIMEOUT)
        assert response.status_code == 404


class TestCORS:
    """Test CORS headers"""

    def test_cors_headers_present(self):
        """Test that CORS headers are set"""
        response = requests.options(f"{BASE_URL}/v1/chat/completions", timeout=TIMEOUT)
        # Should have CORS headers or handle OPTIONS
        assert response.status_code in [200, 204]


class TestIntegrationWorkflow:
    """Integration tests for complete workflows"""

    def test_complete_file_workflow(self):
        """Test complete file lifecycle: create -> read -> delete"""
        filename = f"workflow_test_{int(time.time())}.txt"
        content = "Integration test content"

        # Create file
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json={"messages": [{"role": "user", "content": f"Erstelle {filename}\n{content}"}]},
            timeout=TIMEOUT,
        )
        assert response.status_code == 200

        # Read file
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json={"messages": [{"role": "user", "content": f"Lies {filename}"}]},
            timeout=TIMEOUT,
        )
        assert response.status_code == 200

        # Delete file
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json={"messages": [{"role": "user", "content": f"Lösche {filename}"}]},
            timeout=TIMEOUT,
        )
        assert response.status_code == 200


@pytest.fixture(scope="session", autouse=True)
def check_server_running():
    """Check if server is running before tests"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            pytest.skip("Server not running or not healthy")
    except requests.exceptions.RequestException:
        pytest.skip(f"Server not accessible at {BASE_URL}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
