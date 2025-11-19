# OpenWebUI Custom Prompts für LocalAgent-Pro

Diese Sammlung enthält Custom Prompts für OpenWebUI, um die Integration mit LocalAgent-Pro zu testen und zu nutzen.

## 📋 Verfügbare Prompts

### 1. `/openwebui_connection` - Verbindungsprüfung
**Datei:** `connection_check.md`

Testet die grundlegende Verbindung zwischen OpenWebUI und LocalAgent-Pro API.

**Was wird getestet:**
- ✅ API Health-Check
- ✅ Modell-Verfügbarkeit
- ✅ OpenWebUI-Erreichbarkeit
- ✅ Response-Zeiten

**Verwendung:**
```
/openwebui_connection
API Base URL: http://127.0.0.1:8001/v1
OpenWebUI Port: 3000
Modell: tinyllama
```

---

### 2. `/openwebui_models_test` - Modell-Verfügbarkeitstest
**Datei:** `models_test.md`

Testet einzelne Modelle auf Verfügbarkeit und Performance.

**Was wird getestet:**
- ✅ Modell-Listing
- ✅ Smoke-Tests
- ✅ Performance-Benchmarks
- ✅ GPU-Beschleunigung

**Test-Typen:**
- **smoke-test**: Schneller Funktionstest
- **health-check**: Nur Verfügbarkeit prüfen
- **performance**: Detaillierte Performance-Messung
- **end-to-end**: Vollständiger Workflow-Test

**Verwendung:**
```
/openwebui_models_test
API Base URL: http://127.0.0.1:8001/v1
Modell: tinyllama
Test-Typ: performance
```

---

### 3. `/openwebui_e2e_test` - End-to-End-Test
**Datei:** `e2e_test.md`

Vollständiger Integration-Test über alle Komponenten.

**Was wird getestet:**
- ✅ Infrastruktur (Backend, Ollama, OpenWebUI)
- ✅ API-Endpoints
- ✅ OpenWebUI-Integration
- ✅ Modell-Inferenz
- ✅ Tool-Ausführung
- ✅ Streaming-Support

**Verwendung:**
```
/openwebui_e2e_test
API Base URL: http://127.0.0.1:8001/v1
OpenWebUI URL: http://localhost:3000
Modell: localagent-pro
Sample Prompt: Erstelle Datei test.txt mit Hallo Welt
Erwartetes Ergebnis: Datei erstellt, Bestätigungsnachricht
```

---

## 🚀 Installation in OpenWebUI

### Schritt 1: OpenWebUI öffnen
```bash
# Falls noch nicht gestartet:
docker run -d -p 3000:8080 -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:main
```

Öffne: http://localhost:3000

### Schritt 2: Workspace öffnen
1. Klicke auf **Workspace** (linke Sidebar)
2. Wähle **Functions** → **Custom Prompts**

### Schritt 3: Prompts hinzufügen

#### Variante A: Manuell kopieren
1. Klicke **"New Prompt"**
2. Öffne eine der `.md`-Dateien (z.B. `connection_check.md`)
3. Kopiere den Inhalt unter "Prompt-Template"
4. Füge ihn in OpenWebUI ein
5. Konfiguriere:
   - **Command:** `/openwebui_connection`
   - **Access:** `public`
   - **Felder:** Wie in der Datei beschrieben
6. Klicke **Save**

#### Variante B: Import (falls OpenWebUI Import unterstützt)
1. Workspace → Functions → Import
2. Wähle `.md`-Datei
3. Bestätige Import

---

## 📊 Beispiel-Workflows

### Workflow 1: Erstmaliges Setup testen
```
1. /openwebui_connection
   → Prüfe, ob alles läuft

2. /openwebui_models_test (smoke-test)
   → Schneller Funktionstest

3. /openwebui_e2e_test
   → Vollständiger Integration-Test
```

### Workflow 2: Performance-Optimierung
```
1. /openwebui_models_test (performance, tinyllama)
   → Baseline-Performance messen

2. GPU-Beschleunigung aktivieren:
   cd /path/to/LocalAgent-Pro
   ./setup_gpu_acceleration.sh

3. /openwebui_models_test (performance, tinyllama)
   → Vergleiche Ergebnisse (erwarte ~3-4x Speedup)
```

### Workflow 3: Tool-System testen
```
1. /openwebui_e2e_test
   Prompt: "Erstelle Datei hello.txt mit Hello World"
   → Datei-Erstellung testen

2. /openwebui_e2e_test
   Prompt: "Liste alle Dateien auf"
   → Verzeichnis-Listing testen

3. /openwebui_e2e_test
   Prompt: "Lies Datei hello.txt"
   → Datei-Lesen testen
```

---

## 🎯 Erwartete Ergebnisse

### Bei funktionierendem System:
```
✅ connection_check:
   - Alle Endpoints erreichbar
   - Response-Zeit < 1s
   - Modelle verfügbar

✅ models_test (smoke):
   - Modell antwortet
   - Format korrekt
   - Performance: 6-10 t/s (tinyllama, GPU)

✅ e2e_test:
   - Tools funktionieren
   - Streaming aktiv
   - Keine Fehler
```

### Bei Problemen:
```
❌ connection_check → "Connection refused"
   → Lösung: ./start_server.sh

❌ models_test → "Model not found"
   → Lösung: ollama pull tinyllama

❌ e2e_test → "Tool execution failed"
   → Lösung: config/config.yaml prüfen (sandbox: true?)
```

---

## 🛠️ Konfiguration anpassen

### Standard-Modell ändern
Editiere in den `.md`-Dateien:
```
{{model | select:options=["tinyllama","llama3.1","mistral"]:default="llama3.1"}}
```

### API Base URL anpassen
Falls LocalAgent-Pro auf anderem Port läuft:
```
{{api_base_url | url:placeholder="z.B. http://127.0.0.1:9000/v1":required}}
```

### Neue Test-Typen hinzufügen
In `models_test.md`:
```
{{test_type | select:options=["smoke-test","custom-test"]:default="custom-test"}}

**Bei "custom-test":**
- Beschreibe hier, was passieren soll
- Erwartete Ergebnisse
- Validierungsschritte
```

---

## 📚 Weitere Ressourcen

### LocalAgent-Pro Dokumentation
- `INSTALLATION.md` - Setup-Anleitung
- `GPU_SETUP.md` - GPU-Beschleunigung
- `README.md` - Projekt-Übersicht

### OpenWebUI Dokumentation
- https://docs.openwebui.com
- https://github.com/open-webui/open-webui

### Logs für Debugging
```bash
# API-Logs
tail -f logs/localagent_pro_api.log

# Tool-Logs
tail -f logs/localagent_pro_tools.log

# Ollama-Logs
tail -f logs/localagent_pro_ollama.log

# Alle Logs
tail -f logs/*.log
```

---

## 🔧 Troubleshooting

### Prompt erscheint nicht in OpenWebUI
- Prüfe: Command startet mit `/`
- Prüfe: Access ist auf `public` gesetzt
- Neuladen: Strg+R oder Seite neu laden

### Felder werden nicht angezeigt
- Syntax prüfen: `{{variable | type:placeholder="text":required}}`
- Typen: `url`, `text`, `textarea`, `number`, `select`

### Tests schlagen fehl
```bash
# System-Status komplett prüfen
./health_check.sh

# Einzelne Komponenten testen
systemctl status ollama
ps aux | grep openwebui_agent_server
nvidia-smi
curl -s http://127.0.0.1:8001/health | jq '.'
```

---

## 💡 Tipps & Best Practices

1. **Immer zuerst `connection_check` ausführen**
   - Stellt sicher, dass Basis-Infrastruktur läuft

2. **Performance-Tests regelmäßig durchführen**
   - Nach System-Updates
   - Nach Config-Änderungen
   - Vergleiche mit Baselines

3. **Logs im Blick behalten**
   - Bei Fehlern: Logs helfen sofort
   - `logs/` Verzeichnis regelmäßig checken

4. **Sandbox-Modus nutzen**
   - Verhindert ungewollte Systemänderungen
   - Alle Dateien in `~/localagent_sandbox/`

5. **GPU-Beschleunigung aktivieren**
   - 3-4x schneller
   - `./setup_gpu_acceleration.sh`

---

## 📝 Lizenz

Diese Prompts sind Teil von LocalAgent-Pro und unterliegen der gleichen Lizenz.

---

**Erstellt:** November 2025  
**Version:** 1.0  
**Kompatibel mit:** OpenWebUI 0.1.x, LocalAgent-Pro 1.0
