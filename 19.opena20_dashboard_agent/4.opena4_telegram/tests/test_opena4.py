"""
Tests for opena4 (Telegram Agent)
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import AGENT_ID, PORT, app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["agent"] == AGENT_ID
    assert data["port"] == PORT


def test_correct_port():
    """Test that agent uses correct canonical port"""
    assert PORT == 12346, f"Port mismatch: {PORT} != 12346"


def test_capabilities_endpoint():
    """Test capabilities endpoint (used by opena20)"""
    response = client.get("/capabilities")
    assert response.status_code == 200

    data = response.json()
    assert data["agent_id"] == "opena4"
    assert data["port"] == 12346
    assert data["plan"] == "basic"

    # Check endpoints
    assert "POST /send" in data["endpoints"]
    assert "GET /chats" in data["endpoints"]
    assert "GET /messages/{chat_id}" in data["endpoints"]

    # Check features
    assert data["features"]["send_messages"] == True
    assert data["features"]["receive_messages"] == True
    assert data["features"]["delete_messages"] == False  # Pro+ only


@pytest.mark.asyncio
async def test_send_message_no_bot():
    """Test send message when bot is not initialized"""
    response = client.post("/send", json={"chat_id": 123456789, "text": "Test message"})

    # Should fail gracefully if bot not initialized
    assert response.status_code in [503, 200]


def test_delete_message_requires_pro():
    """Test that message deletion requires Pro plan"""
    response = client.delete("/messages/1")

    assert response.status_code == 403
    assert "Pro plan" in response.json()["detail"]


def test_get_stats_endpoint():
    """Test stats endpoint"""
    # Note: Will fail if database not available, that's ok for unit test
    response = client.get("/stats")
    assert response.status_code in [200, 503]


def test_send_message_validation():
    """Test send message input validation"""
    # Missing required fields
    response = client.post("/send", json={})
    assert response.status_code == 422

    # Invalid chat_id type
    response = client.post("/send", json={"chat_id": "not_a_number", "text": "Test"})
    assert response.status_code == 422


def test_get_chats_pagination():
    """Test chats endpoint with pagination"""
    response = client.get("/chats?limit=10&offset=0")
    assert response.status_code in [200, 503]  # 503 if DB not available


def test_get_messages_pagination():
    """Test messages endpoint with pagination"""
    response = client.get("/messages/123456789?limit=100&offset=0")
    assert response.status_code in [200, 503]  # 503 if DB not available


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
