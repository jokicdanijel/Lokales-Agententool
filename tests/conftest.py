import sys
from pathlib import Path

# Projekt-Root (eine Ebene über /tests)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Nur einmal einfügen (keine Duplikate)
root_str = str(PROJECT_ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)
