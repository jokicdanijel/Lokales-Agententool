#!/usr/bin/env python3
"""
opena3 Test Configuration
"""
import sys
from pathlib import Path

# Projekt-Root zum Path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
