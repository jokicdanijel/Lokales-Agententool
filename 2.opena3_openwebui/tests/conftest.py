#!/usr/bin/env python3
"""
Pytest Fixtures für opena3 Tests
"""
import sys
import os
from pathlib import Path

import pytest

# Projekt-Root zum Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ENV für Tests setzen
os.environ.setdefault("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")
os.environ.setdefault("LOG_LEVEL", "WARNING")  # Weniger Noise in Tests
os.environ.setdefault("OPENA3_RATE_LIMIT_ENABLED", "true")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Richtet Test-Environment ein"""
    # Logs-Verzeichnis erstellen
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Data-Verzeichnis erstellen
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    
    yield
    
    # Cleanup (optional)
    pass


@pytest.fixture
def temp_archive_dir(tmp_path):
    """Temporäres Archiv-Verzeichnis für Safepoint-Tests"""
    archive = tmp_path / "archivp_store"
    archive.mkdir()
    return archive
