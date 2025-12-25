# ⚡ Quick Start - LocalAgent-Pro

Schnelleinstieg in 5 Minuten!

---

## 🎯 Ziel

Nach diesem Guide hast du:

- ✅ LocalAgent-Pro installiert und gestartet
- ✅ Erste API-Anfrage erfolgreich gesendet
- ✅ Grundlegende Funktionen getestet

---

## 🚀 Schritt 1: Installation (1 Minute)

### Option A: Docker (empfohlen)

```bash
git clone https://github.com/jokicdanijel/Lokales-Agententool.git
cd Lokales-Agententool/LocalAgent-Pro
docker-compose up -d
```

### Option B: Manuell

```bash
git clone https://github.com/jokicdanijel/Lokales-Agententool.git
cd Lokales-Agententool/LocalAgent-Pro
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/openwebui_agent_server.py
```

---

## ✅ Schritt 2: Verifizierung (30 Sekunden)

### Health Check

```bash
curl http://localhost:8001/health
```

**Erwartete Antwort:**

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## 💬 Schritt 3: Erste Chat-Anfrage (1 Minute)

### Einfache Nachricht

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hallo! Was kannst du tun?"}
    ]
  }'
```

**Erwartete Antwort:**

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Ich bin LocalAgent-Pro! Ich kann Dateien verwalten, Shell-Befehle ausführen und Web-Requests senden."
      }
    }
  ]
}
```

---

## 🧪 Schritt 4: Tools testen (2 Minuten)

### 1. Datei erstellen

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Erstelle eine Datei hello.txt mit dem Inhalt: Hello World!"}
    ]
  }'
```

### 2. Datei lesen

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Lies die Datei hello.txt"}
    ]
  }'
```

### 3. Shell-Befehl ausführen

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Führe den Befehl aus: ls -la"}
    ]
  }'
```

### 4. Web-Request

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hole den Inhalt von https://api.github.com"}
    ]
  }'
```

---

## 🌐 Schritt 5: OpenWebUI verwenden (optional)

Wenn du OpenWebUI nutzen möchtest:

1. **Browser öffnen:** http://localhost:3000
2. **Account erstellen:** Ersten Nutzer registrieren
3. **Model auswählen:** `llama3.1:8b-instruct-q4_K_M`
4. **Chat starten:** Nachricht eingeben und testen

---

## 🎓 Was nun?

### Wichtige Endpoints

| Endpoint                    | Beschreibung        |
| --------------------------- | ------------------- |
| `GET /health`               | Server-Status       |
| `GET /v1/models`            | Verfügbare Modelle  |
| `POST /v1/chat/completions` | Chat-Anfrage        |
| `GET /metrics`              | Prometheus-Metriken |

### Beispiel-Workflows

#### Workflow 1: Datei-Analyse

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Erstelle eine Datei config.yaml mit: port: 8080\nhost: 0.0.0.0"},
      {"role": "user", "content": "Lies config.yaml und erkläre die Konfiguration"}
    ]
  }'
```

#### Workflow 2: System-Info

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Zeige mir das aktuelle Datum und Verzeichnis"}
    ]
  }'
```

---

## 📚 Weitere Ressourcen

- **Vollständige API-Docs:** [docs/API.md](docs/API.md)
- **Detaillierte Installation:** [INSTALLATION.md](INSTALLATION.md)
- **Sicherheit:** [SECURITY.md](SECURITY.md)
- **GitHub Copilot Integration:** [COPILOT_SYSTEM_PROMPT.md](COPILOT_SYSTEM_PROMPT.md)

---

## 🐛 Probleme?

### Server startet nicht

```bash
# Logs überprüfen
docker-compose logs -f localagent-pro

# Port-Konflikte prüfen
lsof -i :8001
```

### Ollama nicht verfügbar

```bash
# Ollama-Status prüfen
ollama list

# Modell herunterladen
ollama pull llama3.1:8b-instruct-q4_K_M
```

### API-Fehler

```bash
# Verbose Logging aktivieren
export LOG_LEVEL=DEBUG
python src/openwebui_agent_server.py
```

---

**🎉 Glückwunsch! Du bist bereit, LocalAgent-Pro zu nutzen!**

**Nächster Schritt:** Erkunde die vollständige [API-Dokumentation](docs/API.md)
