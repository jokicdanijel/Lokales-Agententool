# 📦 Installation Guide - LocalAgent-Pro

Detaillierte Installationsanleitung für LocalAgent-Pro.

---

## 📋 Voraussetzungen

### Minimale Anforderungen

- **Python:** 3.10 oder höher
- **RAM:** 4 GB (8 GB empfohlen)
- **Speicher:** 10 GB freier Festplattenspeicher
- **OS:** Linux, macOS, Windows (WSL2)

### Optionale Anforderungen

- **Docker:** 20.10+ (für Docker-Installation)
- **Docker Compose:** 2.0+
- **Ollama:** Neueste Version (für lokale LLM-Modelle)

---

## 🚀 Installationsmethoden

### Methode 1: Docker (empfohlen)

**Vorteile:**

- ✅ Schnellste Installation
- ✅ Alle Dependencies enthalten
- ✅ Isolierte Umgebung
- ✅ Production-ready

```bash
# 1. Repository klonen
git clone https://github.com/jokicdanijel/Lokales-Agententool.git
cd Lokales-Agententool/LocalAgent-Pro

# 2. Docker-Compose starten
docker-compose up -d

# 3. Status überprüfen
docker-compose ps

# 4. Logs anzeigen
docker-compose logs -f localagent-pro
```

**Services:**

- LocalAgent-Pro: `http://localhost:8001`
- OpenWebUI: `http://localhost:3000`
- Ollama: `http://localhost:11434`

---

### Methode 2: Manuelle Installation (Linux/macOS)

```bash
# 1. Repository klonen
git clone https://github.com/jokicdanijel/Lokales-Agententool.git
cd Lokales-Agententool/LocalAgent-Pro

# 2. Python Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# 3. Dependencies installieren
pip install --upgrade pip
pip install -r requirements.txt

# 4. Ollama installieren (optional)
# Linux:
curl -fsSL https://ollama.ai/install.sh | sh

# macOS:
brew install ollama

# 5. Ollama-Modell herunterladen
ollama pull llama3.1:8b-instruct-q4_K_M

# 6. Server starten
python src/openwebui_agent_server.py
```

---

### Methode 3: Manuelle Installation (Windows)

```powershell
# 1. Repository klonen
git clone https://github.com/jokicdanijel/Lokales-Agententool.git
cd Lokales-Agententool\LocalAgent-Pro

# 2. Virtual Environment erstellen
python -m venv venv
venv\Scripts\activate

# 3. Dependencies installieren
pip install --upgrade pip
pip install -r requirements.txt

# 4. Ollama installieren
# Download von: https://ollama.ai/download

# 5. Ollama-Modell herunterladen
ollama pull llama3.1:8b-instruct-q4_K_M

# 6. Server starten
python src\openwebui_agent_server.py
```

---

## ⚙️ Konfiguration

### 1. Umgebungsvariablen

Erstelle eine `.env` Datei im Hauptverzeichnis:

```bash
# Server-Konfiguration
PORT=8001
HOST=127.0.0.1

# Ollama-Konfiguration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b-instruct-q4_K_M

# Sandbox-Konfiguration
SANDBOX_DIR=${HOME}/localagent_sandbox

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/localagent.log

# Prometheus (optional)
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
```

### 2. Konfigurationsdatei

Die Hauptkonfiguration befindet sich in `config/config.yaml`:

```yaml
server:
  host: 127.0.0.1
  port: 8001
  debug: false

ollama:
  base_url: http://localhost:11434
  model: llama3.1:8b-instruct-q4_K_M
  timeout: 60

sandbox:
  enabled: true
  base_dir: ~/localagent_sandbox
  max_file_size: 10485760  # 10 MB

security:
  shell_whitelist:
    - ls
    - cat
    - grep
    - echo
    - pwd
    - date
  domain_whitelist:
    - example.com
    - api.github.com
```

---

## 🧪 Installation verifizieren

### Health Check

```bash
# Server-Status prüfen
curl http://localhost:8001/health

# Erwartete Antwort:
# {"status": "healthy", "version": "1.0.0"}
```

### Modell-Verfügbarkeit

```bash
# Verfügbare Modelle abrufen
curl http://localhost:8001/v1/models

# Erwartete Antwort:
# {"models": ["llama3.1:8b-instruct-q4_K_M"]}
```

### Test-Anfrage

```bash
# Chat-Completion testen
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hallo LocalAgent-Pro!"}]
  }'
```

---

## 🔧 Systemd-Service (Linux)

### Installation

```bash
# Installations-Skript ausführen
sudo ./install_systemd_service.sh
```

### Service-Verwaltung

```bash
# Service starten
sudo systemctl start localagent-pro

# Service stoppen
sudo systemctl stop localagent-pro

# Service neu starten
sudo systemctl restart localagent-pro

# Auto-Start aktivieren
sudo systemctl enable localagent-pro

# Status anzeigen
sudo systemctl status localagent-pro

# Logs anzeigen
sudo journalctl -u localagent-pro -f
```

---

## 🐛 Troubleshooting

### Problem: Port bereits belegt

```bash
# Port-Nutzung prüfen
lsof -i :8001

# Prozess beenden
kill -9 <PID>
```

### Problem: Ollama nicht verfügbar

```bash
# Ollama-Status prüfen
ollama list

# Ollama neu starten
# Linux/macOS:
sudo systemctl restart ollama

# Windows:
# Ollama-Anwendung neu starten
```

### Problem: Python-Dependencies fehlen

```bash
# Virtual Environment neu erstellen
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Problem: Sandbox-Berechtigungen

```bash
# Sandbox-Verzeichnis erstellen
mkdir -p ~/localagent_sandbox

# Berechtigungen setzen
chmod 755 ~/localagent_sandbox
```

---

## 📊 Performance-Optimierung

### Ollama GPU-Beschleunigung

```bash
# NVIDIA GPU
docker-compose -f docker-compose.gpu.yml up -d

# AMD GPU
# Siehe GPU_SETUP.md
```

### Prometheus-Monitoring

```bash
# Prometheus aktivieren
docker-compose -f docker-compose.monitoring.yml up -d

# Grafana-Dashboard: http://localhost:3001
# Username: admin
# Password: admin
```

---

## 🔄 Updates

### Docker-Installation

```bash
# Images aktualisieren
docker-compose pull

# Neu starten
docker-compose up -d
```

### Manuelle Installation

```bash
# Code aktualisieren
git pull origin main

# Dependencies aktualisieren
pip install --upgrade -r requirements.txt

# Server neu starten
sudo systemctl restart localagent-pro
```

---

## 📚 Nächste Schritte

1. **Quick Start:** [QUICK_START.md](QUICK_START.md)
2. **API-Dokumentation:** [docs/API.md](docs/API.md)
3. **Sicherheit:** [SECURITY.md](SECURITY.md)
4. **Testing:** [tests/README.md](tests/README.md)

---

**Bei Fragen oder Problemen:** [GitHub Issues](https://github.com/jokicdanijel/Lokales-Agententool/issues)
