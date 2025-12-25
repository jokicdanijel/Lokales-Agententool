#!/usr/bin/env python3
"""
Wrapper script for structure_manager.py
Forwards all calls to src/pkg/structure_manager.py
"""

import sys
from pathlib import Path

# Add src/pkg to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src" / "pkg"))

# Import and run the actual structure_manager
from structure_manager import main

if __name__ == "__main__":
    sys.exit(main())
