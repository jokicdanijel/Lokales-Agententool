#!/bin/bash
#
# LocalAgent-Pro - Komplettes Setup-Skript
# Installiert und konfiguriert das gesamte System
#

set -e

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funktionen
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

header() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  $1${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Banner
clear
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║               🤖  LOCALAGENT-PRO SETUP  🤖                                   ║"
echo "║                                                                              ║"
echo "║  KI-gestützter Agent mit Ollama, GPU-Beschleunigung & OpenWebUI             ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Projekt-Verzeichnis
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

info "Projekt-Verzeichnis: $SCRIPT_DIR"
echo ""

# =====================================
# 1. SYSTEM-ANFORDERUNGEN PRÜFEN
# =====================================

header "1. SYSTEM-ANFORDERUNGEN PRÜFEN"

info "Prüfe Python-Version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    success "Python gefunden: $PYTHON_VERSION"
else
    error "Python 3 nicht gefunden!"
    echo "Installation: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

info "Prüfe NVIDIA GPU..."
if command -v nvidia-smi &> /dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo "Nicht erkannt")
    GPU_DRIVER=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null || echo "Unbekannt")
    success "GPU gefunden: $GPU_NAME (Treiber: $GPU_DRIVER)"
    HAS_GPU=true
else
    warning "Keine NVIDIA GPU gefunden (CPU-Modus wird verwendet)"
    HAS_GPU=false
fi

info "Prüfe Ollama..."
if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama --version 2>&1 | grep -oP 'version is \K[0-9.]+' || echo "unbekannt")
    success "Ollama gefunden: Version $OLLAMA_VERSION"
    HAS_OLLAMA=true
else
    warning "Ollama nicht installiert"
    HAS_OLLAMA=false
fi

echo ""

# =====================================
# 2. OLLAMA INSTALLATION (falls nötig)
# =====================================

if [ "$HAS_OLLAMA" = false ]; then
    header "2. OLLAMA INSTALLIEREN"
    
    info "Möchtest du Ollama jetzt installieren? (j/n)"
    read -p "> " install_ollama
    
    if [[ "$install_ollama" =~ ^[Jj]$ ]]; then
        info "Installiere Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
        success "Ollama installiert!"
        
        # Systemd-Service einrichten
        if [ "$HAS_GPU" = true ]; then
            info "Richte GPU-Beschleunigung ein..."
            sudo systemctl enable ollama
            sudo systemctl start ollama
            success "Ollama-Service mit GPU-Support gestartet"
        fi
    else
        warning "Ollama wird später benötigt. Installation übersprungen."
    fi
    echo ""
fi

# =====================================
# 3. PYTHON VIRTUAL ENVIRONMENT
# =====================================

header "3. PYTHON-UMGEBUNG EINRICHTEN"

if [ ! -d "venv" ]; then
    info "Erstelle Virtual Environment..."
    python3 -m venv venv
    success "Virtual Environment erstellt"
else
    success "Virtual Environment existiert bereits"
fi

info "Aktiviere Virtual Environment..."
source venv/bin/activate

info "Installiere Python-Abhängigkeiten..."
pip install --upgrade pip -q
pip install -r requirements.txt -q 2>&1 | grep -v "Requirement already satisfied" || true
success "Abhängigkeiten installiert"

echo ""

# =====================================
# 4. OLLAMA MODELL HERUNTERLADEN
# =====================================

header "4. OLLAMA-MODELL HERUNTERLADEN"

if [ "$HAS_OLLAMA" = true ] || command -v ollama &> /dev/null; then
    info "Prüfe verfügbare Modelle..."
    
    if ollama list 2>/dev/null | grep -q "tinyllama"; then
        success "tinyllama bereits installiert"
    else
        info "Möchtest du tinyllama herunterladen? (empfohlen für GPU, 637 MB) (j/n)"
        read -p "> " download_model
        
        if [[ "$download_model" =~ ^[Jj]$ ]]; then
            info "Lade tinyllama herunter (637 MB)..."
            ollama pull tinyllama
            success "tinyllama heruntergeladen"
        fi
    fi
    
    info "Verfügbare Modelle:"
    ollama list 2>/dev/null | tail -n +2 | awk '{printf "   📦 %s (%s)\n", $1, $2}'
fi

echo ""

# =====================================
# 5. GPU-BESCHLEUNIGUNG (optional)
# =====================================

if [ "$HAS_GPU" = true ]; then
    header "5. GPU-BESCHLEUNIGUNG KONFIGURIEREN"
    
    info "Möchtest du GPU-Beschleunigung einrichten? (j/n)"
    read -p "> " setup_gpu
    
    if [[ "$setup_gpu" =~ ^[Jj]$ ]]; then
        if [ -f "setup_gpu_acceleration.sh" ]; then
            info "Führe GPU-Setup aus..."
            bash setup_gpu_acceleration.sh
            success "GPU-Beschleunigung konfiguriert"
        else
            warning "setup_gpu_acceleration.sh nicht gefunden"
        fi
    else
        info "GPU-Setup übersprungen"
    fi
    echo ""
fi

# =====================================
# 6. KONFIGURATION
# =====================================

header "6. KONFIGURATION PRÜFEN"

if [ ! -f "config/config.yaml" ]; then
    warning "config/config.yaml nicht gefunden!"
    info "Erstelle Standard-Konfiguration..."
    
    mkdir -p config
    cat > config/config.yaml << 'EOF'
# LocalAgent-Pro Konfiguration

llm:
  model: "tinyllama"
  api_base: "http://127.0.0.1:11434"

sandbox: true
sandbox_path: "~/localagent_sandbox"

allowed_domains:
  - "example.com"
  - "github.com"
  - "ubuntu.com"
  - "archlinux.org"

open_webui_port: 3000
EOF
    success "Konfiguration erstellt: config/config.yaml"
else
    success "Konfiguration gefunden: config/config.yaml"
fi

# Sandbox-Verzeichnis erstellen
SANDBOX_PATH=$(grep sandbox_path config/config.yaml | cut -d':' -f2 | tr -d ' "' | sed "s|~|$HOME|")
if [ ! -d "$SANDBOX_PATH" ]; then
    info "Erstelle Sandbox-Verzeichnis: $SANDBOX_PATH"
    mkdir -p "$SANDBOX_PATH"
    success "Sandbox erstellt"
fi

echo ""

# =====================================
# 7. LOGS VORBEREITEN
# =====================================

header "7. LOG-VERZEICHNIS EINRICHTEN"

if [ ! -d "logs" ]; then
    info "Erstelle Log-Verzeichnis..."
    mkdir -p logs
    success "Log-Verzeichnis erstellt"
else
    success "Log-Verzeichnis existiert"
fi

echo ""

# =====================================
# 8. TESTS DURCHFÜHREN
# =====================================

header "8. SYSTEM-TESTS DURCHFÜHREN"

info "Teste Ollama-Verbindung..."
if curl -s http://127.0.0.1:11434/api/version > /dev/null 2>&1; then
    success "Ollama erreichbar"
    
    info "Teste Ollama-Integration..."
    if python3 quick_test_ollama.py 2>&1 | grep -q "ALLE TESTS ERFOLGREICH"; then
        success "Ollama-Integration funktioniert"
    else
        warning "Ollama-Tests teilweise fehlgeschlagen (siehe Ausgabe oben)"
    fi
else
    warning "Ollama nicht erreichbar (Server möglicherweise nicht gestartet)"
    info "Starte mit: sudo systemctl start ollama"
fi

echo ""

# =====================================
# 9. ZUSAMMENFASSUNG
# =====================================

header "INSTALLATION ABGESCHLOSSEN"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                 ✅ SETUP ERFOLGREICH                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

success "System-Status:"
echo ""

if [ "$HAS_GPU" = true ]; then
    echo "   🖥️  GPU: $GPU_NAME (Treiber: $GPU_DRIVER)"
else
    echo "   ⚠️  GPU: Keine NVIDIA GPU (CPU-Modus)"
fi

if [ "$HAS_OLLAMA" = true ] || command -v ollama &> /dev/null; then
    echo "   🤖 Ollama: Version $OLLAMA_VERSION"
    OLLAMA_STATUS=$(systemctl is-active ollama 2>/dev/null || echo "nicht als Service")
    echo "   📡 Ollama-Service: $OLLAMA_STATUS"
else
    echo "   ⚠️  Ollama: Nicht installiert"
fi

echo "   🐍 Python: $PYTHON_VERSION (venv aktiv)"
echo "   📁 Projekt: $SCRIPT_DIR"
echo "   📂 Sandbox: $SANDBOX_PATH"
echo ""

success "Verfügbare Skripte:"
echo ""
echo "   ./start_server.sh              - Backend-Server starten"
echo "   ./quick_test_ollama.py         - Ollama-Integration testen"
echo "   ./benchmark_cpu_vs_gpu.py      - GPU-Performance messen"
echo "   ./test_api_endpoints.py        - API-Endpoints testen"
echo "   ./tail_logs.sh                 - Live-Logs anzeigen"
echo "   ./analyze_logs.sh              - Log-Analyse"
echo "   ./cleanup_logs.sh              - Logs aufräumen"
echo ""

success "Server starten:"
echo ""
echo "   cd $SCRIPT_DIR"
echo "   source venv/bin/activate"
echo "   python3 src/openwebui_agent_server.py"
echo ""
echo "   Oder mit Start-Skript:"
echo "   ./start_server.sh"
echo ""

success "OpenWebUI konfigurieren:"
echo ""
echo "   1. OpenWebUI öffnen: http://localhost:3000"
echo "   2. Settings → Connections → OpenAI API"
echo "   3. API Base URL: http://127.0.0.1:8001/v1"
echo "   4. Modell wählen: tinyllama oder localagent-pro"
echo ""

success "Dokumentation:"
echo ""
echo "   cat GPU_SETUP.md              - GPU-Beschleunigung"
echo "   cat OLLAMA_SETUP.md           - Ollama-Integration"
echo "   cat LOGGING_GUIDE.md          - Logging-System"
echo "   cat LOGGING_IMPLEMENTATION.md - Tech-Details"
echo ""

info "Nächste Schritte:"
echo ""
echo "   1. Server starten: ./start_server.sh"
echo "   2. Tests durchführen: python3 test_api_endpoints.py"
echo "   3. OpenWebUI verbinden (siehe oben)"
echo ""

success "Setup abgeschlossen! 🚀"
echo ""
