# 🤖 LocalAgent-Pro - Vollständige Installation

Ein KI-gestützter Agent mit Ollama-Integration, GPU-Beschleunigung und OpenWebUI-Kompatibilität.

## 🚀 Schnellstart (Ein Befehl)

```bash
./setup_localagent_pro.sh
```

Dieses Skript:
- ✅ Prüft System-Anforderungen (Python, GPU, Ollama)
- ✅ Erstellt Python Virtual Environment
- ✅ Installiert alle Abhängigkeiten
- ✅ Lädt Ollama-Modell herunter (tinyllama)
- ✅ Konfiguriert GPU-Beschleunigung (optional)
- ✅ Erstellt Konfiguration und Logs
- ✅ Führt System-Tests durch

---

## 📋 Voraussetzungen

### Minimum:
- **OS**: Linux (Ubuntu 20.04+, Linux Mint 21+)
- **Python**: 3.8+
- **RAM**: 8 GB
- **Speicher**: 5 GB frei

### Empfohlen:
- **GPU**: NVIDIA (GTX 1050 oder besser, 4+ GB VRAM)
- **CUDA**: 12.0+
- **RAM**: 16 GB
- **Speicher**: 10 GB frei

---

## 🛠️ Manuelle Installation

### 1. Ollama installieren

```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable ollama
sudo systemctl start ollama
```

### 2. Modell herunterladen

```bash
# Schnelles Modell für GPU (empfohlen)
ollama pull tinyllama

# Oder größeres Modell
ollama pull llama2
```

### 3. Python-Umgebung einrichten

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. GPU-Beschleunigung (optional)

```bash
./setup_gpu_acceleration.sh
```

### 5. Konfiguration anpassen

Bearbeite `config/config.yaml`:

```yaml
llm:
  model: "tinyllama"
  api_base: "http://127.0.0.1:11434"

sandbox: true
sandbox_path: "~/localagent_sandbox"

allowed_domains:
  - "example.com"
  - "github.com"
```

---

## 🎯 Server starten

### Option 1: Start-Skript (empfohlen)

```bash
./start_server.sh
```

### Option 2: Manuell

```bash
source venv/bin/activate
python3 src/openwebui_agent_server.py
```

### Option 3: Hintergrund (daemonisiert)

```bash
nohup python3 src/openwebui_agent_server.py > server.log 2>&1 &
```

---

## 🧪 Tests durchführen

### Ollama-Integration testen

```bash
python3 quick_test_ollama.py
```

### GPU-Performance messen

```bash
python3 benchmark_cpu_vs_gpu.py
```

### API-Endpoints testen

```bash
python3 test_api_endpoints.py
```

### Manuelle API-Tests

```bash
# Health-Check
curl -s http://127.0.0.1:8001/health | jq '.'

# Modelle
curl -s http://127.0.0.1:8001/v1/models | jq '.'

# Chat (non-streaming)
curl -X POST http://127.0.0.1:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hallo!"}]}' | jq '.'

# Chat (streaming)
curl -N -X POST http://127.0.0.1:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Zähle von 1 bis 5"}],"stream":true}'
```

---

## 🌐 OpenWebUI-Integration

### 1. OpenWebUI öffnen

```
http://localhost:3000
```

### 2. API konfigurieren

- Gehe zu: **Settings** → **Connections** → **OpenAI API**
- **API Base URL**: `http://127.0.0.1:8001/v1`
- **API Key**: (leer lassen oder beliebig)
- **Modell wählen**: `tinyllama` oder `localagent-pro`

### 3. Testen

Schreibe eine Nachricht im Chat und beobachte:
- ✅ Streaming-Antworten
- ✅ Tool-Aufrufe (Dateien, Shell, Web)
- ✅ GPU-beschleunigte Inferenz

---

## 📊 Monitoring & Logs

### Live-Logs anzeigen

```bash
./tail_logs.sh
```

### Log-Analyse

```bash
./analyze_logs.sh
```

### Logs aufräumen

```bash
./cleanup_logs.sh
```

### GPU-Überwachung

```bash
# Echtzeit
watch -n 1 nvidia-smi

# Ollama-Logs
sudo journalctl -u ollama -f
```

---

## 📁 Projekt-Struktur

```
LocalAgent-Pro/
├── src/
│   ├── openwebui_agent_server.py  # Haupt-Backend-Server
│   ├── ollama_integration.py      # Ollama-Client
│   └── logging_config.py          # Logging-System
├── config/
│   └── config.yaml                # Konfiguration
├── logs/
│   ├── localagent-pro.log         # Haupt-Log
│   ├── api_requests.log           # API-Requests
│   ├── tool_executions.log        # Tool-Aufrufe
│   └── ollama_integration.log     # Ollama-Calls
├── setup_localagent_pro.sh        # Vollständiges Setup
├── start_server.sh                # Server starten
├── setup_gpu_acceleration.sh      # GPU-Setup
├── quick_test_ollama.py           # Ollama-Test
├── benchmark_cpu_vs_gpu.py        # Performance-Test
├── test_api_endpoints.py          # API-Tests
├── requirements.txt               # Python-Abhängigkeiten
└── *.md                           # Dokumentation
```

---

## 🛠️ Verfügbare Tools

Der Agent unterstützt folgende Tools:

### 1. **Datei lesen**
```
"Lies Datei test.txt"
"Zeige config.yaml"
```

### 2. **Datei schreiben**
```
"Erstelle Datei hello.txt mit Hallo Welt"
"Schreibe test.py mit print('Hello')"
```

### 3. **Verzeichnis auflisten**
```
"Liste alle Dateien auf"
"Zeige Dateien im Ordner /tmp"
```

### 4. **Shell-Kommando**
```
"Führe Kommando 'ls -la' aus"
"Execute 'pwd'"
```

### 5. **Web-Request**
```
"Hole github.com"
"Lade Webseite example.com"
```

---

## 🚀 Performance-Optimierung

### GPU-Beschleunigung aktivieren

```bash
./setup_gpu_acceleration.sh
```

**Erwartete Verbesserung:**
- CPU-Modus: ~2-3 tokens/s
- GPU-Modus: ~20-30 tokens/s (mit tinyllama)
- **Speedup: 9-10x schneller!**

### Modell-Auswahl (GPU GTX 1050, 4GB VRAM)

| Modell | VRAM | Speed | Qualität |
|--------|------|-------|----------|
| `tinyllama` | 637 MB | ⚡⚡⚡ | ⭐⭐ |
| `phi3:mini` | 2.3 GB | ⚡⚡ | ⭐⭐⭐ |
| `llama2:7b` | 3.8 GB | ⚡ | ⭐⭐⭐⭐ |

### Konfiguration anpassen

In `config/config.yaml`:

```yaml
llm:
  model: "tinyllama"  # Schnellstes Modell
  temperature: 0.7    # Kreativität (0.0-1.0)
  max_tokens: 500     # Max. Response-Länge
```

---

## 🐛 Troubleshooting

### Problem: "Ollama nicht erreichbar"

```bash
# Service prüfen
systemctl status ollama

# Service starten
sudo systemctl start ollama

# Manuell starten
ollama serve
```

### Problem: "Port 8001 bereits belegt"

```bash
# Prozess finden
lsof -i:8001

# Prozess beenden
ps aux | grep openwebui_agent_server | awk '{print $2}' | xargs kill
```

### Problem: "GPU wird nicht genutzt"

```bash
# GPU-Status prüfen
nvidia-smi

# CUDA-Version prüfen
nvcc --version

# Ollama-Logs prüfen
sudo journalctl -u ollama -n 50
```

### Problem: "Import-Fehler"

```bash
# Virtual Environment aktivieren
source venv/bin/activate

# Abhängigkeiten neu installieren
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Dokumentation

- **GPU_SETUP.md** - GPU-Beschleunigung einrichten
- **OLLAMA_SETUP.md** - Ollama-Integration
- **LOGGING_GUIDE.md** - Logging-System
- **LOGGING_IMPLEMENTATION.md** - Tech-Details

---

## 🔗 Nützliche Links

- [Ollama](https://ollama.com/)
- [OpenWebUI](https://github.com/open-webui/open-webui)
- [NVIDIA CUDA](https://developer.nvidia.com/cuda-toolkit)

---

## 📝 Lizenz

MIT License - Siehe LICENSE-Datei

---

## 🤝 Support

Bei Problemen:
1. Prüfe die Logs: `./tail_logs.sh`
2. Führe Tests aus: `python3 test_api_endpoints.py`
3. Lies die Dokumentation: `cat GPU_SETUP.md`

---

**Erstellt**: 16. November 2025  
**Version**: 1.0.0  
**Hardware getestet**: NVIDIA GeForce GTX 1050 (4GB VRAM)  
**OS getestet**: Linux Mint 22.2
