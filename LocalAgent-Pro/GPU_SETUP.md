# 🚀 GPU-Beschleunigung für Ollama (Linux Mint + NVIDIA)

Anleitung zur Aktivierung der GPU-Beschleunigung für Ollama auf **Linux Mint** mit **NVIDIA GeForce GTX 1050**.

---

## 📋 Systemvoraussetzungen

- **OS**: Linux Mint 21.x oder höher
- **GPU**: NVIDIA GeForce GTX 1050 (4GB VRAM, Compute Capability 6.1)
- **Treiber**: NVIDIA 535.x oder höher
- **Ollama**: Version 0.12.x oder höher

---

## ⚡ Schnellstart

### 1. Automatisches Setup

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Lokales\ Agententool/LocalAgent-Pro
./setup_gpu_acceleration.sh
```

Das Skript führt automatisch aus:
- ✅ System-Check (GPU, Treiber, CUDA)
- ✅ CUDA Toolkit Installation (optional)
- ✅ Ollama Service-Konfiguration für GPU
- ✅ Service-Neustart
- ✅ GPU-Test

### 2. Manuelle Konfiguration

Falls du die Konfiguration manuell durchführen möchtest:

#### Ollama Service bearbeiten

```bash
sudo nano /etc/systemd/system/ollama.service
```

Füge diese GPU-Einstellungen hinzu:

```ini
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

# CUDA Paths
Environment="PATH=/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="LD_LIBRARY_PATH=/usr/local/cuda/lib64"

# Performance-Tuning für GTX 1050 (4GB VRAM)
Environment="OLLAMA_MAX_VRAM=3500"
Environment="OLLAMA_CONTEXT_SIZE=2048"
```

#### Service neu laden

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
sudo systemctl status ollama
```

---

## 🔧 CUDA Toolkit Installation (Linux Mint)

### Ubuntu-Version ermitteln

Linux Mint basiert auf Ubuntu. Ermittle die Ubuntu-Version:

```bash
lsb_release -a
# Mint 21.x → Ubuntu 22.04 (jammy)
# Mint 20.x → Ubuntu 20.04 (focal)
```

### CUDA Repository hinzufügen

```bash
# Für Ubuntu 22.04 (Mint 21.x)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
```

### CUDA Toolkit installieren

```bash
# CUDA 12.6 (kompatibel mit GTX 1050)
sudo apt-get install -y cuda-toolkit-12-6
```

### Umgebungsvariablen setzen

```bash
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

### Installation prüfen

```bash
nvcc --version
nvidia-smi
```

---

## 📊 GPU-Nutzung überwachen

### Live-Monitoring

```bash
# GPU-Auslastung in Echtzeit
watch -n 1 nvidia-smi

# Kompakte Ansicht
watch -n 1 'nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader'
```

### Ollama-Logs

```bash
# Live-Logs
sudo journalctl -u ollama -f

# Letzte 100 Zeilen
sudo journalctl -u ollama -n 100 --no-pager
```

### GPU während Inference

```bash
# Terminal 1: Test starten
python3 quick_test_ollama.py

# Terminal 2: GPU beobachten
watch -n 0.5 nvidia-smi
```

---

## 🎯 Performance-Optimierung (GTX 1050)

### Empfohlene Modelle (4GB VRAM)

| Modell | VRAM | Performance |
|--------|------|-------------|
| `tinyllama` | ~637 MB | ⚡⚡⚡ Sehr schnell |
| `phi3:mini` | ~2.3 GB | ⚡⚡ Schnell |
| `llama2:7b` | ~3.8 GB | ⚡ Mittel |
| `mistral:7b` | ~4.1 GB | ⚡ Mittel (knapp) |
| `llama3:8b` | ~4.7 GB | ❌ Zu groß |

### Modelle installieren

```bash
# Schnellstes Modell für Tests
ollama pull tinyllama

# Gute Balance (Qualität/Speed)
ollama pull phi3:mini

# Maximale Größe für GTX 1050
ollama pull llama2:7b
```

### Environment-Variablen

```bash
# Für GTX 1050 (4GB VRAM) optimiert:
OLLAMA_MAX_VRAM=3500          # Max. 3.5 GB nutzen
OLLAMA_CONTEXT_SIZE=2048      # Context-Länge begrenzen
OLLAMA_MAX_LOADED_MODELS=1    # Nur 1 Modell gleichzeitig
OLLAMA_NUM_GPU=1              # Anzahl GPUs
OLLAMA_GPU_OVERHEAD=0         # Kein zusätzlicher Overhead
```

---

## 🧪 GPU-Beschleunigung testen

### Python-Test

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Lokales\ Agententool/LocalAgent-Pro
source venv/bin/activate
python3 quick_test_ollama.py
```

**Erwartete Performance-Verbesserung:**
- **CPU-Modus**: ~2-3 tokens/s
- **GPU-Modus**: ~15-30 tokens/s (5-10x schneller!)

### Curl-Test

```bash
# Generate-Request
time curl -X POST http://127.0.0.1:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tinyllama",
    "prompt": "Zähle von 1 bis 5.",
    "stream": false
  }'
```

### Vergleich CPU vs GPU

```bash
# 1. GPU-Modus (normal)
time python3 -c "
from src.ollama_integration import create_ollama_client
client = create_ollama_client()
client.generate('Test', model='tinyllama')
"

# 2. CPU-Modus erzwingen
CUDA_VISIBLE_DEVICES=-1 time python3 -c "..."
```

---

## 🐛 Troubleshooting

### Problem: "CUDA not found"

**Ursache**: CUDA Toolkit nicht installiert

**Lösung**:
```bash
# Installation prüfen
which nvcc
ls -l /usr/local/cuda

# Neu installieren
./setup_gpu_acceleration.sh
```

### Problem: "Out of memory"

**Ursache**: Modell zu groß für 4GB VRAM

**Lösung**:
```bash
# Kleineres Modell verwenden
ollama pull tinyllama
ollama pull phi3:mini

# VRAM-Limit anpassen
sudo systemctl edit ollama
# Füge hinzu: Environment="OLLAMA_MAX_VRAM=3000"
sudo systemctl restart ollama
```

### Problem: GPU wird nicht genutzt

**Prüfung**:
```bash
# 1. GPU sichtbar?
nvidia-smi

# 2. CUDA funktioniert?
nvcc --version

# 3. Ollama-Service nutzt GPU?
sudo systemctl status ollama
sudo journalctl -u ollama | grep -i gpu

# 4. Environment-Variablen gesetzt?
systemctl cat ollama | grep CUDA
```

**Lösung**:
```bash
# Service-Konfiguration prüfen
sudo systemctl cat ollama

# Sollte enthalten:
# Environment="CUDA_VISIBLE_DEVICES=0"
# Environment="OLLAMA_NUM_GPU=1"

# Neu laden
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### Problem: Inference immer noch langsam

**Check**:
```bash
# GPU-Auslastung während Inference
nvidia-smi dmon -s u -c 10

# Sollte zeigen:
# GPU-Util: 80-100%
# Memory: 2000-3500 MB
```

**Wenn GPU-Util niedrig (<20%)**:
- Modell läuft im CPU-Modus
- CUDA nicht korrekt konfiguriert
- VRAM zu wenig → CPU-Fallback

### Problem: Service startet nicht

**Logs anzeigen**:
```bash
sudo journalctl -u ollama -n 100 --no-pager
```

**Häufige Fehler**:
```bash
# Permission denied
sudo chown -R ollama:ollama /usr/share/ollama

# CUDA path falsch
# Prüfe: /usr/local/cuda/bin existiert?
ls -l /usr/local/cuda/bin/nvcc
```

---

## 📈 Performance-Benchmarks

### GTX 1050 (4GB VRAM) Erwartete Werte

| Modell | CPU | GPU | Speedup |
|--------|-----|-----|---------|
| tinyllama | 3 t/s | 25-30 t/s | **8-10x** |
| phi3:mini | 2 t/s | 18-22 t/s | **9-11x** |
| llama2:7b | 2 t/s | 12-15 t/s | **6-8x** |
| mistral:7b | 1.5 t/s | 10-12 t/s | **6-8x** |

### Benchmark durchführen

```bash
# Test-Skript
cat > benchmark_gpu.py << 'EOF'
import time
from src.ollama_integration import create_ollama_client

models = ['tinyllama', 'phi3:mini', 'llama2:7b']
prompt = "Erkläre Python in einem Satz."

client = create_ollama_client()

for model in models:
    print(f"\n🧪 Test: {model}")
    start = time.time()
    response = client.generate(prompt, model=model)
    duration = time.time() - start
    
    if response:
        tokens = len(response.split())
        print(f"✅ {tokens} tokens in {duration:.1f}s ({tokens/duration:.1f} t/s)")
EOF

python3 benchmark_gpu.py
```

---

## 🔍 Service-Konfiguration prüfen

```bash
# Aktuelle Konfiguration anzeigen
systemctl cat ollama

# Environment-Variablen extrahieren
systemctl show ollama -p Environment

# Status
systemctl status ollama

# Backup der Konfiguration
sudo cp /etc/systemd/system/ollama.service ~/ollama.service.backup
```

---

## 📚 Weiterführende Links

- [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)
- [Ollama GPU Dokumentation](https://github.com/ollama/ollama/blob/main/docs/gpu.md)
- [GTX 1050 Specs](https://www.nvidia.com/de-de/geforce/graphics-cards/geforce-gtx-1050/)
- [Ollama Environment Variables](https://github.com/ollama/ollama/blob/main/docs/faq.md#how-do-i-configure-ollama-server)

---

## ✅ Checkliste nach Setup

- [ ] NVIDIA-Treiber installiert (`nvidia-smi` funktioniert)
- [ ] CUDA Toolkit installiert (`nvcc --version` zeigt Version)
- [ ] Ollama Service konfiguriert (Environment-Variablen gesetzt)
- [ ] Service neu gestartet (`systemctl restart ollama`)
- [ ] GPU wird genutzt (nvidia-smi zeigt Ollama-Prozess)
- [ ] Performance-Test durchgeführt (>10 tokens/s mit tinyllama)
- [ ] Logs zeigen keine Fehler (`journalctl -u ollama`)

---

**Erstellt**: 16. November 2025  
**Hardware**: NVIDIA GeForce GTX 1050 (4GB VRAM)  
**OS**: Linux Mint 21.x  
**Ollama**: 0.12.11
