#!/bin/bash
#
# GPU-Beschleunigung für Ollama auf Linux Mint einrichten
# Hardware: NVIDIA GeForce GTX 1050 (4GB VRAM, Compute Capability 6.1)
# Treiber: 535.274.02
#

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  GPU-Beschleunigung für Ollama (Linux Mint + NVIDIA GTX 1050) ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# 1. System-Informationen
info "Prüfe System-Informationen..."
echo ""
echo "OS: $(lsb_release -d | cut -f2)"
echo "Kernel: $(uname -r)"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'Nicht erkannt')"
echo "Treiber: $(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null || echo 'Nicht installiert')"
echo "VRAM: $(nvidia-smi --query-gpu=memory.total --format=csv,noheader 2>/dev/null || echo 'Unbekannt')"
echo ""

# 2. NVIDIA-Treiber prüfen
info "Prüfe NVIDIA-Treiber..."
if ! command -v nvidia-smi &> /dev/null; then
    error "NVIDIA-Treiber nicht gefunden!"
    echo ""
    echo "Installation mit:"
    echo "  sudo ubuntu-drivers devices"
    echo "  sudo ubuntu-drivers autoinstall"
    exit 1
fi
success "NVIDIA-Treiber installiert: $(nvidia-smi --query-gpu=driver_version --format=csv,noheader)"

# 3. CUDA Toolkit Status
info "Prüfe CUDA Toolkit..."
if command -v nvcc &> /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep release | sed -n 's/.*release \([0-9.]*\).*/\1/p')
    success "CUDA Toolkit gefunden: Version $CUDA_VERSION"
    CUDA_INSTALLED=true
else
    warning "CUDA Toolkit nicht installiert"
    CUDA_INSTALLED=false
fi
echo ""

# 4. CUDA Installation anbieten (falls nicht vorhanden)
if [ "$CUDA_INSTALLED" = false ]; then
    info "CUDA Toolkit wird für maximale Performance empfohlen"
    echo ""
    echo "Optionen:"
    echo "  [1] CUDA Toolkit jetzt installieren (empfohlen)"
    echo "  [2] Ohne CUDA fortfahren (Ollama nutzt CPU-Fallback)"
    echo "  [3] Abbrechen"
    echo ""
    read -p "Wähle eine Option [1-3]: " cuda_choice
    
    case $cuda_choice in
        1)
            info "Installiere CUDA Toolkit für Linux Mint..."
            echo ""
            
            # Linux Mint basiert auf Ubuntu - CUDA über Ubuntu-Repos
            info "Füge NVIDIA CUDA Repository hinzu..."
            
            # Ubuntu-Version ermitteln (Mint 21.x = Ubuntu 22.04)
            UBUNTU_VERSION=$(lsb_release -r | awk '{print $2}' | cut -d'.' -f1)
            
            if [ "$UBUNTU_VERSION" -ge 21 ]; then
                UBUNTU_CODENAME="jammy"  # Ubuntu 22.04
            else
                UBUNTU_CODENAME="focal"   # Ubuntu 20.04
            fi
            
            info "Verwende Ubuntu-Codename: $UBUNTU_CODENAME"
            
            # CUDA Keyring installieren
            wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb -O /tmp/cuda-keyring.deb
            sudo dpkg -i /tmp/cuda-keyring.deb
            sudo apt-get update
            
            # CUDA Toolkit installieren (Version 12.x für GTX 1050)
            info "Installiere CUDA Toolkit..."
            sudo apt-get install -y cuda-toolkit-12-6
            
            # Umgebungsvariablen setzen
            info "Konfiguriere Umgebungsvariablen..."
            
            if ! grep -q "/usr/local/cuda/bin" ~/.bashrc; then
                echo '' >> ~/.bashrc
                echo '# CUDA Toolkit' >> ~/.bashrc
                echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
                echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
            fi
            
            export PATH=/usr/local/cuda/bin:$PATH
            export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
            
            success "CUDA Toolkit installiert!"
            warning "Bitte Terminal neu starten oder 'source ~/.bashrc' ausführen"
            ;;
        2)
            info "Fahre ohne CUDA fort..."
            ;;
        3)
            info "Installation abgebrochen"
            exit 0
            ;;
        *)
            error "Ungültige Auswahl"
            exit 1
            ;;
    esac
fi

echo ""

# 5. Ollama Service für GPU konfigurieren
info "Konfiguriere Ollama systemd Service für GPU-Nutzung..."

OLLAMA_SERVICE="/etc/systemd/system/ollama.service"

if [ ! -f "$OLLAMA_SERVICE" ]; then
    error "Ollama Service nicht gefunden: $OLLAMA_SERVICE"
    exit 1
fi

# Backup erstellen
sudo cp "$OLLAMA_SERVICE" "${OLLAMA_SERVICE}.backup.$(date +%Y%m%d_%H%M%S)"
success "Backup erstellt: ${OLLAMA_SERVICE}.backup.*"

# Service-Datei mit GPU-Einstellungen aktualisieren
info "Aktualisiere Service-Konfiguration..."

sudo tee "$OLLAMA_SERVICE" > /dev/null <<'EOF'
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3

# GPU-Beschleunigung
Environment="CUDA_VISIBLE_DEVICES=0"
Environment="OLLAMA_NUM_GPU=1"
Environment="OLLAMA_GPU_OVERHEAD=0"
Environment="OLLAMA_MAX_LOADED_MODELS=1"

# CUDA Paths (falls installiert)
Environment="PATH=/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="LD_LIBRARY_PATH=/usr/local/cuda/lib64"

# Performance-Tuning für GTX 1050 (4GB VRAM)
Environment="OLLAMA_MAX_VRAM=3500"
Environment="OLLAMA_CONTEXT_SIZE=2048"

[Install]
WantedBy=default.target
EOF

success "Service-Konfiguration aktualisiert"

# 6. Systemd neu laden und Service neu starten
info "Lade systemd-Konfiguration neu..."
sudo systemctl daemon-reload

info "Starte Ollama Service neu..."
sudo systemctl restart ollama

sleep 3

# 7. Status prüfen
if sudo systemctl is-active --quiet ollama; then
    success "Ollama Service läuft!"
else
    error "Ollama Service konnte nicht gestartet werden!"
    echo ""
    echo "Logs anzeigen:"
    echo "  sudo journalctl -u ollama -n 50 --no-pager"
    exit 1
fi

echo ""

# 8. GPU-Nutzung testen
info "Teste GPU-Nutzung..."
echo ""

# Warte kurz bis Service bereit ist
sleep 2

# Teste Ollama-Verbindung
if curl -s http://127.0.0.1:11434/api/version > /dev/null 2>&1; then
    success "Ollama API erreichbar"
else
    error "Ollama API nicht erreichbar!"
    exit 1
fi

# Zeige GPU-Status
echo ""
info "GPU-Status während Ollama läuft:"
nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader | \
    awk -F', ' '{printf "  GPU %s: %s\n  Auslastung: %s\n  VRAM: %s / %s\n", $1, $2, $3, $4, $5}'

echo ""

# 9. Zusammenfassung
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                 GPU-BESCHLEUNIGUNG AKTIVIERT                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
success "GPU: NVIDIA GeForce GTX 1050 (4GB VRAM)"
success "Treiber: $(nvidia-smi --query-gpu=driver_version --format=csv,noheader)"

if [ "$CUDA_INSTALLED" = true ] || command -v nvcc &> /dev/null; then
    success "CUDA: $(nvcc --version 2>/dev/null | grep release | sed -n 's/.*release \([0-9.]*\).*/\1/p' || echo 'N/A')"
fi

success "Ollama Service: Aktiv mit GPU-Support"
echo ""

info "Einstellungen:"
echo "  • OLLAMA_NUM_GPU=1"
echo "  • OLLAMA_MAX_VRAM=3500 MB"
echo "  • OLLAMA_CONTEXT_SIZE=2048"
echo "  • OLLAMA_MAX_LOADED_MODELS=1"
echo ""

info "Performance testen:"
echo "  cd $(pwd)"
echo "  python3 quick_test_ollama.py"
echo ""

info "GPU-Überwachung:"
echo "  watch -n 1 nvidia-smi"
echo ""

info "Service-Logs:"
echo "  sudo journalctl -u ollama -f"
echo ""

warning "WICHTIG für GTX 1050 (4GB VRAM):"
echo "  • Verwende kleine Modelle (llama2:7b, mistral:7b, tinyllama)"
echo "  • Große Modelle (>7B) benötigen mehr VRAM!"
echo "  • Bei VRAM-Problemen: Kleineres Modell oder CPU-Fallback"
echo ""

success "Setup abgeschlossen! 🚀"
