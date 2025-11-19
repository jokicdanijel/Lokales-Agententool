# OpenWebUI Custom Prompts - Quick Reference

## 🚀 Schnellstart

### 1. Backend prüfen
```bash
curl -s http://127.0.0.1:8001/health | jq '.'
```

### 2. OpenWebUI öffnen
```
http://localhost:3000
```

### 3. API in OpenWebUI konfigurieren
```
Settings → Connections → OpenAI API
Base URL: http://127.0.0.1:8001/v1
API Key: (leer lassen)
```

---

## 📋 Verfügbare Prompts

### `/openwebui_connection` - Verbindungstest

**Zweck:** Grundlegende Verbindung testen

**Felder:**
- API Base URL: `http://127.0.0.1:8001/v1`
- OpenWebUI Port: `3000`
- Modell: `tinyllama` / `localagent-pro` / `llama3.1`
- Health Endpoint: `/health`
- Beschreibung: (optional)

**Ausgabe:**
```
✅ API Health-Check (0.12s)
✅ Modell-Verfügbarkeit (tinyllama)
✅ OpenWebUI-Verbindung (Port 3000)
📊 Zusammenfassung: Alle Tests bestanden
```

---

### `/openwebui_models_test` - Modelltest

**Zweck:** Modell-Performance und Verfügbarkeit testen

**Felder:**
- API Base URL: `http://127.0.0.1:8001/v1`
- Modell: `tinyllama` / `localagent-pro` / `llama3.1`
- Test-Typ:
  - `smoke-test` - Schneller Funktionstest
  - `health-check` - Nur Verfügbarkeit
  - `performance` - Detaillierte Performance-Messung
  - `end-to-end` - Vollständiger Workflow
- Beschreibung: (optional)

**Ausgabe (Performance-Test):**
```
✅ Modell verfügbar: tinyllama
🚀 Performance-Messung:
   - Response-Zeit: 5.2s
   - Tokens/Sekunde: 9.6 t/s
   - GPU-Auslastung: 93%
   - VRAM: 1.2 GB / 4.0 GB
📊 Benchmark: ✅ Optimal (erwartete 6-10 t/s)
```

---

### `/openwebui_e2e_test` - End-to-End-Test

**Zweck:** Vollständige Integration testen (Backend, Ollama, OpenWebUI, Tools)

**Felder:**
- API Base URL: `http://127.0.0.1:8001/v1`
- OpenWebUI URL: `http://localhost:3000`
- Modell: `tinyllama` / `localagent-pro` / `llama3.1`
- Sample Prompt: `Erstelle Datei test.txt mit Hallo Welt`
- Erwartetes Ergebnis: `Datei erstellt, Bestätigungsnachricht`

**Ausgabe:**
```
Phase 1: ✅ Infrastruktur (Backend, Ollama, OpenWebUI)
Phase 2: ✅ API-Endpoints (/health, /models, /chat/completions)
Phase 3: ✅ OpenWebUI-Integration
Phase 4: ✅ Funktionstest (Tool ausgeführt)
Phase 5: ✅ Tool-Verifikation (Datei existiert)

📊 Performance: 0.35s (Tool-Execution)
🎯 Empfehlung: ✅ Tool-System funktioniert perfekt
```

---

## 🧪 Test-Szenarien

### Szenario 1: Erstmaliges Setup testen

```bash
# 1. Backend starten
./start_server.sh

# 2. In OpenWebUI:
/openwebui_connection
  → Alle Systeme prüfen

# 3. Modell testen
/openwebui_models_test (smoke-test, tinyllama)
  → Grundfunktion verifizieren

# 4. Vollständiger Test
/openwebui_e2e_test
  Sample Prompt: Hallo, wie geht es dir?
  → Integration bestätigen
```

**Erwartung:** Alle 3 Tests ✅

---

### Szenario 2: Performance nach GPU-Setup

```bash
# 1. Baseline messen (vor GPU-Setup)
/openwebui_models_test (performance, tinyllama)
  → Notiere: Tokens/Sekunde

# 2. GPU-Beschleunigung aktivieren
cd /path/to/LocalAgent-Pro
./setup_gpu_acceleration.sh

# 3. System neu starten
sudo systemctl restart ollama
./start_server.sh

# 4. Performance erneut messen
/openwebui_models_test (performance, tinyllama)
  → Erwarte: ~3-4x schneller
```

**Erwartung:**
- Vorher: 2-3 t/s (CPU)
- Nachher: 6-10 t/s (GPU)
- Speedup: ~3-4x

---

### Szenario 3: Tool-System testen

```bash
# 1. Datei erstellen
/openwebui_e2e_test
  Sample Prompt: Erstelle Datei hello.txt mit "Hello World"
  Erwartetes Ergebnis: Datei erstellt in Sandbox

# 2. Datei lesen
/openwebui_e2e_test
  Sample Prompt: Lies Datei hello.txt
  Erwartetes Ergebnis: Inhalt angezeigt

# 3. Verzeichnis listen
/openwebui_e2e_test
  Sample Prompt: Liste alle Dateien auf
  Erwartetes Ergebnis: hello.txt in Liste

# 4. Verifikation
ls -lh ~/localagent_sandbox/
  → hello.txt sollte existieren
```

**Erwartung:** Alle Tool-Operationen ✅

---

### Szenario 4: Streaming-Test

```bash
/openwebui_e2e_test
  Sample Prompt: Erkläre Künstliche Intelligenz in 5 Sätzen
  Erwartetes Ergebnis: Streaming-Response, word-by-word
```

**Erwartung:**
- Streaming aktiv (SSE)
- 40-60 Chunks
- Word-by-word Anzeige in OpenWebUI

---

## 🛠️ Troubleshooting

### Problem: Backend nicht erreichbar

**Symptom:**
```
❌ connection_check: Connection refused
```

**Lösung:**
```bash
# Server-Status prüfen
ps aux | grep openwebui_agent_server

# Logs checken
tail -f logs/localagent_pro_api.log

# Server starten
./start_server.sh
```

---

### Problem: Modell nicht gefunden

**Symptom:**
```
❌ models_test: Model 'tinyllama' not available
```

**Lösung:**
```bash
# Verfügbare Modelle
ollama list

# Modell herunterladen
ollama pull tinyllama

# Verifizieren
curl -s http://127.0.0.1:8001/v1/models | jq '.data[].id'
```

---

### Problem: Langsame Performance

**Symptom:**
```
⚠️ performance: 2.3 t/s (erwartet: 6-10 t/s)
```

**Lösung:**
```bash
# GPU-Status prüfen
nvidia-smi

# Ollama GPU-Nutzung
journalctl -u ollama -f | grep "GPU"

# Falls keine GPU-Nutzung:
./setup_gpu_acceleration.sh
sudo systemctl restart ollama
```

---

### Problem: Tools werden nicht ausgeführt

**Symptom:**
```
❌ e2e_test: Tool execution failed
```

**Lösung:**
```bash
# 1. Sandbox-Modus prüfen
cat config/config.yaml | grep sandbox

# 2. Sandbox erstellen
mkdir -p ~/localagent_sandbox

# 3. Logs prüfen
tail -f logs/localagent_pro_tools.log

# 4. Direkt testen
curl -X POST http://127.0.0.1:8001/test \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Erstelle Datei test.txt mit Test"}'
```

---

### Problem: OpenWebUI zeigt Fehler

**Symptom:**
```
OpenWebUI: "Failed to connect to API"
```

**Lösung:**
1. **API Base URL prüfen:**
   - Muss enden mit `/v1`
   - Korrekt: `http://127.0.0.1:8001/v1`
   - Falsch: `http://127.0.0.1:8001`

2. **Connection-Test:**
   ```bash
   curl -s http://127.0.0.1:8001/v1/models
   ```

3. **Logs checken:**
   ```bash
   tail -f logs/localagent_pro_api.log
   ```

---

## 📊 Performance-Benchmarks

### TinyLlama (GPU - GTX 1050)
```
Tokens/Sekunde: 6-10 t/s
Response-Zeit (50 tokens): ~5-8s
GPU-Auslastung: 85-95%
VRAM: 1-2 GB / 4 GB
```

### TinyLlama (CPU)
```
Tokens/Sekunde: 2-3 t/s
Response-Zeit (50 tokens): ~20-25s
CPU-Auslastung: 100%
```

### Llama3.1 (GPU - GTX 1050)
```
Tokens/Sekunde: 3-5 t/s
Response-Zeit (50 tokens): ~10-15s
GPU-Auslastung: 90-100%
VRAM: 3-4 GB / 4 GB (nahe Limit)
```

---

## 💡 Best Practices

### 1. Regelmäßige Health-Checks
```bash
# Täglich ausführen:
/openwebui_connection

# Bei Änderungen:
/openwebui_e2e_test
```

### 2. Performance-Monitoring
```bash
# Wöchentlich:
/openwebui_models_test (performance)

# Vergleiche mit Baseline
# Erwartung: Stabile Performance
```

### 3. Log-Analyse
```bash
# Logs regelmäßig prüfen
tail -100 logs/localagent_pro_api.log
tail -100 logs/localagent_pro_tools.log

# Fehler suchen
grep "ERROR" logs/*.log
```

### 4. Sandbox-Cleanup
```bash
# Sandbox regelmäßig leeren
ls -lh ~/localagent_sandbox/
rm ~/localagent_sandbox/test*.txt
```

---

## 🔗 Weiterführende Links

- **Installation:** `INSTALLATION.md`
- **GPU-Setup:** `GPU_SETUP.md`
- **Prompts-Details:** `openwebui_prompts/README.md`
- **Server-Code:** `src/openwebui_agent_server.py`

---

## 📝 Notizen

### Häufig verwendete Commands

```bash
# Backend starten
./start_server.sh

# Backend stoppen
ps aux | grep openwebui_agent_server | grep -v grep | awk '{print $2}' | xargs -r kill

# Logs tail (alle)
tail -f logs/*.log

# Health-Check
curl -s http://127.0.0.1:8001/health | jq '.'

# Modelle listen
curl -s http://127.0.0.1:8001/v1/models | jq '.data[].id'

# GPU-Status
nvidia-smi

# Ollama-Status
systemctl status ollama
```

---

**Version:** 1.0  
**Letzte Aktualisierung:** November 2025  
**Kompatibel mit:** LocalAgent-Pro 1.0, OpenWebUI 0.1.x
