"""Basic tests for opena1 (Koordinator)"""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))
from opena1_app import PORT, app


def test_health_endpoint():
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200


def test_port_configured():
    assert PORT == 12344


def test_routes_update_and_health():
    with TestClient(app) as client:
        r = client.post(
            "/route/update",
            json={
                "agent": "test-agent",
                "agent_id": "test-agent-1",
                "port": 12350,
                "program": "test",
                "archivator_port": 12345,
                "mapping_ts": "ts",
                "mapping": {},
            },
        )
        assert r.status_code == 200
        h = client.get("/health")
        assert h.status_code == 200
        data = h.json()
        assert "routes_count" in data
        assert isinstance(data["routes_count"], int)
