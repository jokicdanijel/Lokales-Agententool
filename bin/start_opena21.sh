#!/bin/bash
# ELION Hyper-Dashboard – opena21 (Workflow Orchestrator)
# Port: 12368

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
LOG_DIR="$PROJECT_ROOT/logs"

# Ensure directories
mkdir -p "$LOG_DIR"
mkdir -p "$PROJECT_ROOT/data/workflows"

# Activate venv
if [[ -d "$VENV_DIR" ]]; then
    source "$VENV_DIR/bin/activate"
else
    echo "❌ Virtual environment not found: $VENV_DIR"
    exit 1
fi

# Check dependencies
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "❌ Missing dependencies. Installing..."
    pip install -q fastapi uvicorn httpx
fi

echo "🚀 Starting opena21 (Workflow Orchestrator) on port 12368"
echo "🔄 Features: Registry, Execution, Triggers, Cross-Agent"
echo "📂 Database: $PROJECT_ROOT/data/workflows/"

cd "$PROJECT_ROOT/20.opena21_workflow" 2>/dev/null || {
    echo "⚠️ opena21 folder not found, attempting alternate location"
    cd "$PROJECT_ROOT/src/agents/opena21_workflow" 2>/dev/null || {
        echo "❌ Could not find opena21_workflow folder"
        exit 1
    }
}

python3 main.py 2>&1 | tee "$LOG_DIR/opena21.log"
