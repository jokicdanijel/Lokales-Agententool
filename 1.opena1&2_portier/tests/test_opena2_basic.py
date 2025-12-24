"""Basic tests for opena2 (archivp)"""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))
from opena2_app import PORT, app


def test_health_endpoint():
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200


def test_port_configured():
    assert PORT == 12345


def test_archive_store_and_health():
    with TestClient(app) as client:
        r = client.post(
            "/store/archivp",
            json={"src": "unittest", "dst": "archivp", "kind": "TEST", "body": {"test": "data"}, "strict": True},
        )
        assert r.status_code == 200
        h = client.get("/health")
        assert h.status_code == 200
        data = h.json()
        assert "entries" in data
        assert isinstance(data["entries"], int)
