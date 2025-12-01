#!/usr/bin/env python3
"""
Tests für opena4 Health-Endpoint
FastAPI TestClient + Pydantic V2
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """FastAPI TestClient Fixture"""
    from main_telegram_agent import app
    return TestClient(app)


class TestHealthEndpoint:
    """Tests für /health Endpoint"""

    def test_health_returns_200(self, client):
        """Test: /health gibt HTTP 200 zurück"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_contains_agent_name(self, client):
        """Test: /health enthält agent='opena4'"""
        response = client.get("/health")
        data = response.json()
        
        assert "agent" in data
        assert data["agent"] == "opena4"

    def test_health_contains_port(self, client):
        """Test: /health enthält port"""
        response = client.get("/health")
        data = response.json()
        
        assert "port" in data
        assert isinstance(data["port"], int)

    def test_health_contains_status_ok(self, client):
        """Test: /health status ist 'ok'"""
        response = client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "ok"

    def test_health_contains_telegram_info(self, client):
        """Test: /health enthält Telegram-Status"""
        response = client.get("/health")
        data = response.json()
        
        # Prüfe dass Telegram-Info vorhanden ist
        assert "telegram_available" in data or "telegram_users_configured" in data


class TestRootEndpoint:
    """Tests für / Root-Endpoint"""

    def test_root_returns_200(self, client):
        """Test: / gibt HTTP 200 zurück"""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_contains_kuerzel(self, client):
        """Test: / enthält kuerzel='tgap' oder 'telep'"""
        response = client.get("/")
        data = response.json()
        
        assert "kuerzel" in data
        assert data["kuerzel"] in ["tgap", "telep"]  # Beide akzeptabel

    def test_root_contains_description(self, client):
        """Test: / enthält description"""
        response = client.get("/")
        data = response.json()
        
        assert "description" in data
        assert len(data["description"]) > 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
