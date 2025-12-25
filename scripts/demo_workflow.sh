#!/usr/bin/env bash
# ==============================================================================
# demo_workflow.sh - Demonstration of ELION setup workflow
#
# This script demonstrates the workflow mentioned in the problem statement:
# 1. Set OPENAI_API_KEY if not present
# 2. Start services with bin/ops.sh start
# 3. Register agents with python3 scripts/register_agents.py
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "========================================================================"
echo "ELION Hyper-Dashboard Setup Workflow Demonstration"
echo "========================================================================"
echo ""

# Step 1: Check/Set OPENAI_API_KEY
echo "📝 Step 1: Checking OPENAI_API_KEY in .env"
echo "------------------------------------------------------------------------"

if [[ ! -f .env ]]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [[ -f .env.example ]]; then
        cp .env.example .env
        echo "✅ Created .env from .env.example"
        echo "⚠️  Please edit .env and add your OPENAI_API_KEY"
        echo "   Example: echo 'OPENAI_API_KEY=sk-...' >> .env"
    else
        echo "❌ .env.example not found. Cannot create .env"
        exit 1
    fi
else
    if grep -q "^OPENAI_API_KEY=" .env; then
        echo "✅ OPENAI_API_KEY already present in .env"
        # Show masked version
        KEY_VALUE=$(grep "^OPENAI_API_KEY=" .env | cut -d= -f2)
        KEY_LENGTH=${#KEY_VALUE}
        echo "   Key length: $KEY_LENGTH characters"
        echo "   Preview: ***...*** (hidden for security)"
    else
        echo "⚠️  OPENAI_API_KEY not found in .env"
        echo "   To add it, run:"
        echo "   echo 'OPENAI_API_KEY=your_key_here' >> .env"
        echo ""
        echo "   For this demo, we'll skip this step."
    fi
fi

echo ""
echo "📋 Step 2: Starting services with bin/ops.sh start"
echo "------------------------------------------------------------------------"
echo "ℹ️  In production, this would start all ELION services:"
echo "   - Dashboard (Port 12349)"
echo "   - Portier/Coordinator (Port 12344)"
echo "   - Archivator (Port 12345)"
echo "   - And other agent services..."
echo ""
echo "   For this demo, we'll show the help instead:"
echo ""
./bin/ops.sh help

echo ""
echo "📝 Step 3: Registering agents with scripts/register_agents.py"
echo "------------------------------------------------------------------------"
echo "ℹ️  In production, this would register agents with the dashboard."
echo "   The script would:"
echo "   - Read DASHBOARD_ADMIN_TOKEN from .env"
echo "   - POST to http://127.0.0.1:12349/api/agent/register"
echo "   - Register opena1 (Port 12344) and opena2 (Port 12345)"
echo ""
echo "   Script structure:"
python3 -c "
import os
script_path = 'scripts/register_agents.py'
if os.path.exists(script_path):
    with open(script_path, 'r') as f:
        lines = f.readlines()

    print(f'   Total lines: {len(lines)}')
    print(f'   Contains token() function: {\"def token():\" in \"\".join(lines)}')
    print(f'   Contains post() function: {\"def post(\" in \"\".join(lines)}')
    print(f'   Registers opena1: {\"opena1\" in \"\".join(lines)}')
    print(f'   Registers opena2: {\"opena2\" in \"\".join(lines)}')
else:
    print('   ❌ Script not found')
"

echo ""
echo "========================================================================"
echo "✅ Workflow Demonstration Complete!"
echo "========================================================================"
echo ""
echo "To actually run the workflow (when services are running):"
echo ""
echo "  1. Ensure OPENAI_API_KEY is set:"
echo "     echo 'OPENAI_API_KEY=your_key_here' >> .env"
echo ""
echo "  2. Start services:"
echo "     bin/ops.sh start"
echo ""
echo "  3. Register agents:"
echo "     python3 scripts/register_agents.py"
echo "     # OR use the shortcut:"
echo "     bin/ops.sh agents:register"
echo ""
echo "  4. Verify status:"
echo "     bin/ops.sh status"
echo ""
echo "========================================================================"
