#!/bin/bash
# OpenA3 Startup Script
# Startet alle Komponenten mit einem Befehl

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║                   🚀 OpenA3 COMPLETE SYSTEM STARTUP                       ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📍 Working Directory: $SCRIPT_DIR"
echo ""

# Check Python
echo "🐍 Prüfe Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nicht gefunden!"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1)
echo "✅ $PYTHON_VERSION"
echo ""

# Check Dateien
echo "📂 Prüfe Dateien..."
FILES=(
    "web_dashboard.py"
    "repair_integrate.py"
    "tools/voice_command_parser.py"
    "tools/voice_note_recorder.py"
    "tools/voice_call_system.py"
    "tools/voice_assistant.py"
    "tools/voice_transcriber.py"
    "tools/voice_scheduler.py"
    "src/speech_input.py"
)

MISSING=0
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        echo "✅ $file ($SIZE bytes)"
    else
        echo "❌ $file - FEHLT"
        MISSING=$((MISSING + 1))
    fi
done

if [ $MISSING -gt 0 ]; then
    echo "❌ $MISSING Dateien fehlen!"
    exit 1
fi

echo ""
echo "🌐 Starte Web Dashboard..."
echo ""
echo "   ✅ Dashboard: http://localhost:8000/"
echo "   📡 API: http://localhost:8000/api/status"
echo "   📡 API: http://localhost:8000/api/tools"
echo "   📡 API: http://localhost:8000/api/programs"
echo ""

echo "🎤 Verfügbare Voice Programme:"
echo "   python3 tools/voice_command_parser.py"
echo "   python3 tools/voice_note_recorder.py"
echo "   python3 tools/voice_call_system.py"
echo "   python3 tools/voice_assistant.py"
echo "   python3 tools/voice_transcriber.py"
echo "   python3 tools/voice_scheduler.py"
echo ""

echo "⏹️  Drücke CTRL+C zum Beenden"
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Starte Dashboard
python3 web_dashboard.py
