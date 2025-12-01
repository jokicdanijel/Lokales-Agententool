"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path

# Add src to path
SRC_PATH = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC_PATH))


@pytest.fixture
def test_config():
    """Test configuration fixture."""
    return {
        "host": "localhost",
        "port": 8001,
        "debug": True,
    }


@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory fixture."""
    return tmp_path


@pytest.fixture
def mock_api_client():
    """Mock API client fixture."""
    class MockClient:
        def get(self, url):
            return {"status": "ok", "data": []}

        def post(self, url, data):
            return {"status": "created", "id": 1}

    return MockClient()
