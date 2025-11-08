"""Basis-Tests für Agent"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app, AGENT_ID, PORT

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["port"] == PORT

def test_status(client):
    response = client.get("/status")
    assert response.status_code == 200

def test_invoke(client):
    response = client.post("/invoke", json={"test": True})
    assert response.status_code == 200
