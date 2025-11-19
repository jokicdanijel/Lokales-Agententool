"""Pytest configuration and fixtures for LocalAgent-Pro tests."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

# Test fixtures
@pytest.fixture
def temp_sandbox():
    """Create temporary sandbox directory for testing."""
    temp_dir = tempfile.mkdtemp(prefix="test_sandbox_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_ollama_response():
    """Mock Ollama API response."""
    return {
        "model": "llama3.1:8b-instruct-q4_K_M",
        "message": {
            "role": "assistant",
            "content": "write_file('/home/user/test.txt', 'Hello World')"
        },
        "done": True
    }

@pytest.fixture
def sample_chat_request():
    """Sample chat completion request."""
    return {
        "model": "localagent-pro",
        "messages": [
            {"role": "user", "content": "Erstelle Datei test.txt mit Inhalt Hello"}
        ],
        "stream": False
    }

@pytest.fixture
def app_client():
    """Flask test client."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from openwebui_agent_server import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
