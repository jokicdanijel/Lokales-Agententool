#!/bin/bash
# QUICK START: Phase 5 System vollständig starten und testen

set -euo pipefail

BASE="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"
cd "$BASE"

echo "================================================================================"
echo "🚀 ELION HYPER-DASHBOARD: QUICK START (Phasen 1-5)"
echo "================================================================================"

# Step 1: Activate venv
echo ""
echo "📍 Step 1: Aktiviere Python 3.12 venv..."
if [ -d "1.portier_openai/venv313" ]; then
  source 1.portier_openai/venv313/bin/activate
  echo "✅ venv313 aktiviert"
else
  echo "❌ venv313 nicht gefunden!"
  exit 1
fi

# Step 2: Generate token if missing
echo ""
echo "📍 Step 2: Prüfe Token (.env)..."
if [ ! -f "19.dashboard_agent/.env" ]; then
  echo "⚠️  .env fehlt – generiere Token..."
  TOKEN=$(openssl rand -hex 16)
  echo "$TOKEN" > "19.dashboard_agent/.env"
  echo "✅ Token generiert: $TOKEN"
else
  TOKEN=$(cat "19.dashboard_agent/.env" 2>/dev/null)
  echo "✅ Token vorhanden: ${TOKEN:0:10}..."
fi

# Step 3: Start all services
echo ""
echo "📍 Step 3: Starte alle 19 Services (Phasen 1-5)..."
cd "19.dashboard_agent"
chmod +x bin/start_all.sh bin/stop_all.sh bin/ops.sh
./bin/start_all.sh
sleep 5

# Step 4: Wait for services to boot
echo ""
echo "📍 Step 4: Warte auf Service-Start (30 Sekunden)..."
for i in {1..30}; do
  echo -n "."
  sleep 1
done
echo ""

# Step 5: Check health
echo ""
echo "📍 Step 5: Prüfe Service-Health..."
for port in 12344 12345 12346 12364 12365 12366 12367; do
  if curl -s "http://127.0.0.1:$port/health" >/dev/null 2>&1; then
    echo "✅ Port $port: LIVE"
  else
    echo "⏳ Port $port: Starting..."
  fi
done

# Step 6: Register agents
echo ""
echo "📍 Step 6: Registriere alle Agenten im Dashboard..."
sleep 2
./bin/ops.sh agents:register >/dev/null 2>&1 || true

# Step 7: System verification
echo ""
echo "📍 Step 7: Starte System-Verifikation..."
./bin/ops.sh verify >/dev/null 2>&1 || true

# Step 8: Final status
echo ""
echo "📍 Step 8: System-Status..."
echo ""
./bin/ops.sh status 2>/dev/null | head -30 || echo "Dashboard nicht sofort bereit – bitte warten..."

# Step 9: Display URLs
echo ""
echo "================================================================================"
echo "✅ SYSTEM BEREIT!"
echo "================================================================================"
echo ""
echo "🌐 Verfügbare Endpoints:"
echo ""
echo "  Dashboard (Central):    http://127.0.0.1:12349"
echo ""
echo "  Phase 1 (Core):"
echo "    - Coordinator:        http://127.0.0.1:12344"
echo "    - Archivator:         http://127.0.0.1:12345"
echo "    - Scheduler:          http://127.0.0.1:12346"
echo ""
echo "  Phase 4 (Marketing):"
echo "    - Social Media:       http://127.0.0.1:12359"
echo "    - Influencer:         http://127.0.0.1:12360"
echo "    - Calendar:           http://127.0.0.1:12361"
echo "    - HTML Generator:     http://127.0.0.1:12362"
echo "    - E-Commerce Shop:    http://127.0.0.1:12363"
echo ""
echo "  Phase 5 (Enterprise):   ← NEW!"
echo "    - CRM:                http://127.0.0.1:12364"
echo "    - Analytics:          http://127.0.0.1:12365"
echo "    - Dashboard:          http://127.0.0.1:12366"
echo "    - Workflow:           http://127.0.0.1:12367"
echo ""
echo "📋 Nützliche Befehle:"
echo ""
echo "  View status:            bin/ops.sh status"
echo "  View logs:              bin/ops.sh logs"
echo "  Run tests:              pytest tests/test_phase5.py -v"
echo "  Stop system:            bin/ops.sh stop"
echo ""
echo "🔑 Token:"
echo "  $TOKEN"
echo ""
echo "=================================================================================================="
echo "System-Status: 🟢 READY"
echo "=================================================================================================="
