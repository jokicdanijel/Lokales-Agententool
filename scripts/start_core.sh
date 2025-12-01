#!/usr/bin/env bash
################################################################################
# start_core.sh — Start OpenA1 (Coordinator) + OpenA2 (Archivator)
# Implementiert Policy-konforme Startup (VENV_PATH, Quotes für &-Ordner, Checks)
################################################################################

set -euo pipefail

# ════════════════════════════════════════════════════════════════════════════
# CONFIG (Policy-Binding)
# ════════════════════════════════════════════════════════════════════════════
ROOT="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"
PYTHON="${ROOT}/.venv/bin/python3"
OPENA2_APP="1.opena1&2_portier/opena2_app.py"
OPENA1_APP="1.opena1&2_portier/opena1_app.py"
PORT_A2=12345
PORT_A1=12344

# ════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════
echo "════════════════════════════════════════════════════════════════════════"
echo "START_CORE: OpenA1 (Coordinator) + OpenA2 (Archivator)"
echo "════════════════════════════════════════════════════════════════════════"
echo "ROOT:    $ROOT"
echo "PYTHON:  $PYTHON"
echo "OpenA2:  Port $PORT_A2 (Archivator)"
echo "OpenA1:  Port $PORT_A1 (Coordinator)"
echo

# ════════════════════════════════════════════════════════════════════════════
# PREFLIGHT
# ════════════════════════════════════════════════════════════════════════════
if [ ! -d "$ROOT" ]; then
    echo "❌ ROOT directory not found: $ROOT"
    exit 1
fi

if [ ! -f "$PYTHON" ]; then
    echo "❌ Python not found: $PYTHON"
    exit 1
fi

if [ ! -f "$ROOT/$OPENA2_APP" ]; then
    echo "❌ OpenA2 app not found: $ROOT/$OPENA2_APP"
    exit 1
fi

if [ ! -f "$ROOT/$OPENA1_APP" ]; then
    echo "❌ OpenA1 app not found: $ROOT/$OPENA1_APP"
    exit 1
fi

echo "✅ Preflight: All checks passed"
echo

# ════════════════════════════════════════════════════════════════════════════
# KILL EXISTING PROCESSES (Optional, commented out for safety)
# ════════════════════════════════════════════════════════════════════════════
# echo "Stopping existing services..."
# pkill -f "opena2_app.py" || true
# pkill -f "opena1_app.py" || true
# sleep 1

# ════════════════════════════════════════════════════════════════════════════
# START SERVICES (Archivator first, then Coordinator)
# ════════════════════════════════════════════════════════════════════════════
cd "$ROOT"

echo "1️⃣  Starting OpenA2 (Archivator, Port $PORT_A2)..."
"$PYTHON" "$OPENA2_APP" >/tmp/opena2.log 2>&1 &
PID_A2=$!
echo "   PID: $PID_A2"

sleep 2  # Give OpenA2 time to start

echo "2️⃣  Starting OpenA1 (Coordinator, Port $PORT_A1)..."
"$PYTHON" "$OPENA1_APP" >/tmp/opena1.log 2>&1 &
PID_A1=$!
echo "   PID: $PID_A1"

sleep 2  # Give both time to stabilize

# ════════════════════════════════════════════════════════════════════════════
# HEALTH CHECKS
# ════════════════════════════════════════════════════════════════════════════
echo
echo "3️⃣  Health Checks:"
echo

# OpenA2 (Archivator)
echo "  OpenA2 (Port $PORT_A2):"
if timeout 2 curl -s "http://127.0.0.1:$PORT_A2/health" 2>/dev/null | jq . 2>/dev/null; then
    echo "    ✅ OpenA2 responding"
else
    echo "    ❌ OpenA2 not responding (check /tmp/opena2.log)"
fi
echo

# OpenA1 (Coordinator)
echo "  OpenA1 (Port $PORT_A1):"
if timeout 2 curl -s "http://127.0.0.1:$PORT_A1/health" 2>/dev/null | jq . 2>/dev/null; then
    echo "    ✅ OpenA1 responding"
else
    echo "    ❌ OpenA1 not responding (check /tmp/opena1.log)"
fi
echo

# ════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════════════════
echo "════════════════════════════════════════════════════════════════════════"
echo "Startup complete. Services running in background:"
echo "  OpenA2 (PID $PID_A2): http://127.0.0.1:$PORT_A2"
echo "  OpenA1 (PID $PID_A1): http://127.0.0.1:$PORT_A1"
echo
echo "Logs:"
echo "  OpenA2: tail -f /tmp/opena2.log"
echo "  OpenA1: tail -f /tmp/opena1.log"
echo "════════════════════════════════════════════════════════════════════════"
