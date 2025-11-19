# OpenWebUI – End-to-End-Verbindungstest

**Befehl:** `/openwebui_e2e_test`  
**Zugriff:** `public`

## Eingabeaufforderung

Führe einen vollständigen End-to-End-Test durch, der API-Verbindung, OpenWebUI-Integration, Modell-Inferenz und Tool-Ausführung umfasst.

## Eingabefelder

```
{{api_base_url | url:placeholder="z.B. http://127.0.0.1:8001/v1":required}}
{{openwebui_url | url:placeholder="z.B. http://localhost:3000":required}}
{{model | select:options=["tinyllama","localagent-pro","llama2:latest","llama3.1"]:default="tinyllama":required}}
{{sample_prompt | textarea:placeholder="Beispiel-Prompt zum Testen":default="Erstelle Datei test.txt mit Hallo Welt":required}}
{{expected_result | textarea:placeholder="Was soll das System liefern?":required}}
```

## Prompt-Template

```
🚀 **End-to-End-Test: OpenWebUI ↔ LocalAgent-Pro**

Teste die vollständige Integration von OpenWebUI mit LocalAgent-Pro API.

---

## 🎯 Test-Konfiguration

- **API Base URL:** {{api_base_url}}
- **OpenWebUI URL:** {{openwebui_url}}
- **Modell:** {{model}}
- **Test-Prompt:** {{sample_prompt}}
- **Erwartetes Ergebnis:** {{expected_result}}

---

## 📋 Test-Sequenz

### Phase 1: Infrastruktur-Check ✅
1. **Backend-Server:**
   - Prüfe: {{api_base_url}}/health
   - Erwarte: Status 200, JSON Response
   - Validiere: `status: "ok"`, `model: "{{model}}"`

2. **Ollama-Service:**
   - Prüfe: systemctl status ollama
   - Erwarte: active (running)
   - Validiere: GPU-Layers geladen

3. **OpenWebUI-Frontend:**
   - Prüfe: {{openwebui_url}}
   - Erwarte: UI erreichbar
   - Validiere: Login-Page oder Dashboard

---

### Phase 2: API-Endpoints ✅
1. **Models-Endpoint:**
   ```bash
   curl -s {{api_base_url}}/models
   ```
   - Erwarte: Liste mit "{{model}}"
   - Validiere: OpenAI-kompatibles Format

2. **Chat-Completions-Endpoint:**
   ```bash
   curl -X POST {{api_base_url}}/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "{{model}}",
       "messages": [{"role": "user", "content": "test"}]
     }'
   ```
   - Erwarte: Status 200
   - Validiere: `choices[0].message.content` vorhanden

---

### Phase 3: OpenWebUI-Integration ✅
1. **API-Konfiguration in OpenWebUI:**
   - Settings → Connections → OpenAI API
   - Base URL: {{api_base_url}}
   - API Key: (optional, kann leer bleiben)
   - Speichern & Testen

2. **Modell-Auswahl:**
   - Wähle "{{model}}" aus Dropdown
   - Validiere: Modell erscheint in Liste

---

### Phase 4: Funktionstest ✅
**Test-Prompt:** {{sample_prompt}}

1. **Sende Prompt über OpenWebUI:**
   - Eingabe in Chat: "{{sample_prompt}}"
   - Klicke "Send"

2. **Erwartetes Verhalten:**
   {{expected_result}}

3. **Validierung:**
   - Response innerhalb 5s
   - Keine Fehlermeldungen
   - Ergebnis entspricht Erwartung

---

### Phase 5: Tool-Execution (falls zutreffend) ✅
**Wenn Prompt Tools nutzt (z.B. Datei erstellen):**

1. **Tool-Detection:**
   - Backend erkennt: "Erstelle Datei"
   - Tool ausgewählt: `write_file()`

2. **Tool-Ausführung:**
   - Datei erstellt in Sandbox
   - Erfolgsmeldung zurück

3. **Verifikation:**
   ```bash
   # Falls Sandbox-Modus:
   ls -lh ~/localagent_sandbox/test.txt
   
   # Falls Live-Modus:
   ls -lh test.txt
   ```

---

## 📊 Test-Report

Erstelle nach allen Tests folgenden Report:

```markdown
# End-to-End Test-Report
**Datum:** <Timestamp>
**Modell:** {{model}}

## ✅ Erfolgreich
- [x] Backend-Server erreichbar
- [x] Ollama-Service aktiv
- [x] OpenWebUI-Frontend läuft
- [x] API-Endpoints funktionieren
- [x] Modell verfügbar
- [x] Chat-Integration funktioniert
- [x] Test-Prompt erfolgreich
- [x] Tools ausgeführt (falls zutreffend)

## ⚠️ Warnungen
<Falls vorhanden, sonst "Keine">

## ❌ Fehler
<Falls vorhanden, sonst "Keine">

## 📈 Performance-Metriken
- Response-Zeit: <X>s
- Tokens/Sekunde: <X> t/s
- GPU-Auslastung: <X>%
- VRAM-Nutzung: <X> MB / 4096 MB

## 🎯 Empfehlung
<Basierend auf Test-Ergebnissen>
```
```

---

## Beispiel-Verwendung

### Test 1: Einfacher Chat-Test

```
/openwebui_e2e_test
API Base URL: http://127.0.0.1:8001/v1
OpenWebUI URL: http://localhost:3000
Modell: tinyllama
Sample Prompt: Hallo, wie geht es dir?
Erwartetes Ergebnis: Freundliche Begrüßung, Angebot zur Hilfe
```

**Output:**
```
🚀 End-to-End Test-Report

Phase 1: ✅ Infrastruktur
- Backend: ✅ Läuft (http://127.0.0.1:8001)
- Ollama: ✅ Active (23/23 GPU Layers)
- OpenWebUI: ✅ Erreichbar (Port 3000)

Phase 2: ✅ API-Endpoints
- /health: 200 OK
- /models: 2 Modelle verfügbar
- /chat/completions: Funktioniert

Phase 3: ✅ OpenWebUI-Integration
- API konfiguriert
- Modell "tinyllama" ausgewählt

Phase 4: ✅ Funktionstest
- Prompt: "Hallo, wie geht es dir?"
- Response: "Hallo! Mir geht es gut, danke. Wie kann ich dir heute helfen?"
- Zeit: 1.2s
- Status: ✅ Erfolgreich

📊 Performance:
- Response-Zeit: 1.2s
- Tokens/Sekunde: 9.2 t/s
- GPU-Auslastung: 87%

🎯 Empfehlung: ✅ System voll funktionsfähig
```

---

### Test 2: Tool-Integration

```
/openwebui_e2e_test
API Base URL: http://127.0.0.1:8001/v1
OpenWebUI URL: http://localhost:3000
Modell: localagent-pro
Sample Prompt: Erstelle Datei hello.txt mit "Hello World"
Erwartetes Ergebnis: Datei erstellt, Bestätigung mit Pfad
```

**Output:**
```
🚀 End-to-End Test-Report (Tool-Test)

Phase 1-3: ✅ Alle Checks bestanden

Phase 4: ✅ Tool-Ausführung
- Prompt erkannt: "Erstelle Datei"
- Tool selected: write_file()
- Parameters:
  * path: hello.txt
  * content: "Hello World"

Phase 5: ✅ Tool-Verifikation
- Datei erstellt: ~/localagent_sandbox/hello.txt
- Größe: 11 bytes
- Inhalt: ✅ Korrekt

Backend-Response:
```
🤖 LocalAgent-Pro hat deine Anfrage bearbeitet:

✏️ Datei schreiben:
✅ Datei erstellt (Sandbox: /home/user/localagent_sandbox/hello.txt)
📝 11 Zeichen geschrieben
```

📊 Performance:
- Response-Zeit: 0.3s (Tool-Execution)
- Tool-Latenz: 0.05s
- Gesamt: 0.35s

🎯 Empfehlung: ✅ Tool-System funktioniert perfekt
```

---

### Test 3: Streaming-Test

```
/openwebui_e2e_test
API Base URL: http://127.0.0.1:8001/v1
OpenWebUI URL: http://localhost:3000
Modell: tinyllama
Sample Prompt: Erkläre Künstliche Intelligenz in 3 Sätzen
Erwartetes Ergebnis: Streaming-Response, word-by-word
```

**Output:**
```
🚀 End-to-End Test-Report (Streaming)

Phase 1-3: ✅ Alle Checks bestanden

Phase 4: ✅ Streaming-Test
- Request mit "stream": true
- Chunks empfangen: 42
- Format: Server-Sent Events (SSE)
- Anzeige: ✅ Word-by-word in OpenWebUI

Response (vollständig):
"Künstliche Intelligenz (KI) bezeichnet Systeme, die menschenähnliche 
kognitive Fähigkeiten simulieren. Sie lernen aus Daten, erkennen Muster 
und treffen Entscheidungen. Anwendungen reichen von Chatbots bis zu 
autonomen Fahrzeugen."

📊 Streaming-Metriken:
- Erste Chunk-Latenz: 0.8s
- Durchschnitt pro Chunk: 0.05s
- Gesamt-Zeit: 3.2s
- Chunks: 42

🎯 Empfehlung: ✅ Streaming funktioniert optimal
```

---

## 🛠️ Troubleshooting

### Backend nicht erreichbar
```bash
# Server-Status prüfen
ps aux | grep openwebui_agent_server

# Logs checken
tail -f logs/localagent_pro_api.log

# Server starten
./start_server.sh
```

### OpenWebUI zeigt "Connection failed"
```bash
# OpenWebUI-Container prüfen (falls Docker)
docker ps | grep open-webui

# API Base URL prüfen
curl -s http://127.0.0.1:8001/v1/models

# In OpenWebUI: Settings → Connections
# Base URL: http://127.0.0.1:8001/v1 (mit /v1!)
```

### Modell antwortet nicht
```bash
# Ollama-Status
systemctl status ollama

# Modell laden
ollama pull tinyllama

# GPU-Beschleunigung prüfen
nvidia-smi
```

### Tools werden nicht ausgeführt
```bash
# Sandbox-Modus prüfen
cat config/config.yaml | grep sandbox

# Logs für Tool-Execution
tail -f logs/localagent_pro_tools.log

# Test direkt über API
curl -X POST http://127.0.0.1:8001/test \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Erstelle Datei test.txt mit Test"}'
```

---

## 📚 Weiterführende Dokumentation

- `INSTALLATION.md` - Vollständige Setup-Anleitung
- `GPU_SETUP.md` - GPU-Beschleunigung konfigurieren
- `logs/` - Alle Log-Dateien für Debugging
- `config/config.yaml` - Konfigurationsoptionen
