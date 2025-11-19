# 🚀 Custom Prompts in OpenWebUI installieren - Schritt-für-Schritt

## 📋 Übersicht

Du hast 3 Custom Prompts verfügbar:

| Prompt | Befehl | Zweck |
|--------|--------|-------|
| **Connection Check** | `/openwebui_connection` | Teste API-Verbindung |
| **Models Test** | `/openwebui_models_test` | Teste Modell-Performance |
| **E2E Test** | `/openwebui_e2e_test` | Vollständiger Integration-Test |

---

## ✅ **Schritt 1: OpenWebUI öffnen**

```bash
# OpenWebUI ist bereits gestartet auf:
xdg-open http://localhost:3000
```

Oder manuell im Browser: **http://localhost:3000**

---

## ✅ **Schritt 2: API-Verbindung konfigurieren**

**WICHTIG:** Zuerst die API-Verbindung einrichten!

1. **Klicke auf dein Profil-Icon** (rechts oben)
2. **Wähle "Settings" (⚙️)**
3. **Gehe zu "Connections"**
4. **Unter "OpenAI API":**
   - **API Base URL:** `http://192.168.0.70:8001/v1`
   - **API Key:** (leer lassen)
5. **Klicke "Save & Test"**

✅ **Du solltest sehen:** "Connection successful"

---

## ✅ **Schritt 3: Prompts installieren**

### **Option A: Via Workspace (Empfohlen)**

1. **Klicke in der linken Sidebar auf "Workspace"** 📁
2. **Wähle "Functions"**
3. **Klicke auf das **+** Icon** (oben rechts) → "Create New Function"

#### **Prompt 1: Connection Check**

**Kopiere diesen Inhalt:**

```markdown
---
name: OpenWebUI Connection Check
command: /openwebui_connection
description: Teste die Verbindung zwischen OpenWebUI und LocalAgent-Pro API
---

# 🔍 OpenWebUI Connection Check

Dieser Prompt testet die grundlegende Verbindung zwischen OpenWebUI und LocalAgent-Pro.

## 📋 Konfiguration

**API Base URL:**
{{api_base_url | url:placeholder="http://192.168.0.70:8001/v1":default="http://192.168.0.70:8001/v1"}}

**OpenWebUI Port:**
{{openwebui_port | number:placeholder="3000":default="3000"}}

**Modell:**
{{model | select:options=["localagent-pro","llama3.1","tinyllama"]:default="localagent-pro"}}

---

## 🧪 Test-Ablauf

### 1. API Health Check
Prüfe: `{{api_base_url}}/health`

### 2. Modell-Verfügbarkeit
Prüfe: `{{api_base_url}}/models`
Erwartete Modelle: localagent-pro, {{model}}

### 3. OpenWebUI erreichbar
Prüfe: `http://localhost:{{openwebui_port}}`

### 4. Test-Request
Sende: "Hallo, bist du bereit?"
An: `{{api_base_url}}/chat/completions`

---

## ✅ Erwartete Ergebnisse

- ✅ Health-Status: "ok"
- ✅ Modelle verfügbar: ≥2
- ✅ OpenWebUI läuft: Status 200
- ✅ Response-Zeit: <1s

---

## 🔧 Bei Problemen

**Connection refused:**
→ `cd LocalAgent-Pro && ./start_server.sh`

**Model not found:**
→ `ollama pull {{model}}`

**Port-Fehler:**
→ Prüfe OpenWebUI-Container: `docker ps`
```

**Einfügen:**
1. Füge den Text oben ein
2. **Command:** `/openwebui_connection`
3. **Access:** Public
4. Klicke **"Create"**

---

#### **Prompt 2: Models Test**

**Kopiere diesen Inhalt:**

```markdown
---
name: OpenWebUI Models Test
command: /openwebui_models_test
description: Teste einzelne Modelle auf Verfügbarkeit und Performance
---

# 🧪 OpenWebUI Models Test

Testet ein spezifisches Modell auf Funktionalität und Performance.

## 📋 Konfiguration

**API Base URL:**
{{api_base_url | url:placeholder="http://192.168.0.70:8001/v1":default="http://192.168.0.70:8001/v1"}}

**Modell:**
{{model | select:options=["localagent-pro","llama3.1","tinyllama"]:default="localagent-pro"}}

**Test-Typ:**
{{test_type | select:options=["smoke-test","health-check","performance","end-to-end"]:default="smoke-test"}}

---

## 🧪 Test-Typen

### **smoke-test** (Schnell)
- ✅ Modell verfügbar?
- ✅ Antwortet es?
- ⏱️ Dauer: ~5s

### **health-check** (Minimal)
- ✅ Nur Verfügbarkeit
- ⏱️ Dauer: ~1s

### **performance** (Detailliert)
- ✅ Response-Zeit
- ✅ Tokens/Sekunde
- ✅ GPU-Nutzung
- ⏱️ Dauer: ~30s

### **end-to-end** (Vollständig)
- ✅ Alle obigen Tests
- ✅ Tool-Ausführung
- ✅ Streaming
- ⏱️ Dauer: ~60s

---

## 🎯 Test: {{test_type}}

**Sende an:** `{{api_base_url}}/chat/completions`
**Modell:** `{{model}}`
**Prompt:** "Hallo, was kannst du?"

---

## ✅ Erwartete Ergebnisse

**smoke-test:**
- ✅ Response vorhanden
- ✅ Format korrekt

**performance:**
- ✅ Response-Zeit: <2s
- ✅ Tokens/s: >5 (CPU) / >40 (GPU)
- ✅ GPU aktiv: ja (falls verfügbar)

**end-to-end:**
- ✅ Alle Tests bestanden
- ✅ Tools funktionieren
- ✅ Streaming aktiv

---

## 🔧 Bei Problemen

**Langsame Performance (<5 t/s):**
→ GPU-Beschleunigung aktivieren:
```bash
cd LocalAgent-Pro
./setup_gpu_acceleration.sh
```

**Modell nicht gefunden:**
→ `ollama pull {{model}}`
```

**Einfügen wie bei Prompt 1**

---

#### **Prompt 3: E2E Test**

**Kopiere diesen Inhalt:**

```markdown
---
name: OpenWebUI E2E Test
command: /openwebui_e2e_test
description: Vollständiger End-to-End-Test über alle Komponenten
---

# 🚀 OpenWebUI End-to-End Test

Testet die komplette Integration: OpenWebUI → LocalAgent-Pro → Ollama → Tools

## 📋 Konfiguration

**API Base URL:**
{{api_base_url | url:placeholder="http://192.168.0.70:8001/v1":default="http://192.168.0.70:8001/v1"}}

**OpenWebUI URL:**
{{openwebui_url | url:placeholder="http://localhost:3000":default="http://localhost:3000"}}

**Modell:**
{{model | select:options=["localagent-pro","llama3.1"]:default="localagent-pro"}}

**Test-Prompt:**
{{sample_prompt | textarea:placeholder="z.B. Erstelle Datei test.txt mit Hallo Welt":default="Erstelle Datei test.txt mit Hallo Welt"}}

**Erwartetes Ergebnis:**
{{expected_result | textarea:placeholder="z.B. Datei erstellt, Bestätigungsnachricht":default="Datei erstellt"}}

---

## 🧪 Test-Ablauf

### 1️⃣ **Infrastruktur-Test**
- ✅ Backend läuft: `{{api_base_url}}/health`
- ✅ Ollama läuft: `systemctl status ollama`
- ✅ OpenWebUI läuft: `{{openwebui_url}}`

### 2️⃣ **API-Test**
- ✅ `/v1/models` - Modelle verfügbar
- ✅ `/v1/chat/completions` - Chat funktioniert

### 3️⃣ **OpenWebUI-Integration**
- ✅ Verbindung zu API
- ✅ Modell-Auswahl
- ✅ Chat-Interface

### 4️⃣ **Modell-Inferenz**
- 📝 Prompt: `{{sample_prompt}}`
- ✅ Response vorhanden
- ✅ Format korrekt

### 5️⃣ **Tool-Ausführung**
- ✅ Tool erkannt
- ✅ Aktion ausgeführt
- ✅ Ergebnis: `{{expected_result}}`

### 6️⃣ **Streaming**
- ✅ Streaming aktiv
- ✅ Chunks korrekt

---

## ✅ Erwartete Ergebnisse

**Alle Komponenten:**
- ✅ Backend: Status "ok"
- ✅ Ollama: Active (running)
- ✅ OpenWebUI: HTTP 200

**Integration:**
- ✅ API erreichbar
- ✅ Modelle verfügbar
- ✅ Chat funktioniert

**Tool-Execution:**
- ✅ Datei erstellt (falls file-tool)
- ✅ Bestätigung erhalten
- ✅ Kein Error

**Performance:**
- ✅ Response-Zeit: <3s
- ✅ Tokens/s: >5

---

## 🔧 Bei Problemen

**Backend nicht erreichbar:**
```bash
cd LocalAgent-Pro
./restart_server.sh
```

**Ollama nicht aktiv:**
```bash
systemctl start ollama
```

**OpenWebUI nicht erreichbar:**
```bash
docker restart open-webui
```

**Tool-Ausführung fehlgeschlagen:**
→ Prüfe `config/config.yaml`:
```yaml
sandbox: false  # Für direkten Workspace-Zugriff
```

---

## 📊 Performance-Benchmark

**CPU (ohne GPU):**
- Response-Zeit: 2-5s
- Tokens/s: 5-10

**GPU (mit CUDA):**
- Response-Zeit: 0.5-1s
- Tokens/s: 40-60

**Streaming:**
- Chunks: Kontinuierlich
- Latenz: <100ms
```

**Einfügen wie bei Prompt 1 & 2**

---

## ✅ **Schritt 4: Prompts testen**

### **Test 1: Connection Check**
1. Öffne einen neuen Chat in OpenWebUI
2. Tippe: `/openwebui_connection`
3. Drücke **Enter**
4. Fülle die Felder aus (Standard-Werte sind OK)
5. Klicke **Submit**

✅ **Erwartung:** "✅ Health-Status: ok, Modelle verfügbar: 2"

---

### **Test 2: Models Test**
1. Neuer Chat
2. Tippe: `/openwebui_models_test`
3. **Test-Typ:** smoke-test
4. **Submit**

✅ **Erwartung:** "✅ Response vorhanden, Format korrekt"

---

### **Test 3: E2E Test**
1. Neuer Chat
2. Tippe: `/openwebui_e2e_test`
3. **Sample Prompt:** "Erstelle test.txt mit Hello from OpenWebUI"
4. **Expected Result:** "Datei erstellt"
5. **Submit**

✅ **Erwartung:** "✅ Tool erkannt, Datei erstellt"

---

## 🎯 **Fertig!**

Du hast jetzt 3 leistungsstarke Test-Prompts in OpenWebUI:

- 🔍 `/openwebui_connection` - Schneller Health-Check
- 🧪 `/openwebui_models_test` - Performance-Testing
- 🚀 `/openwebui_e2e_test` - Vollständiger Workflow-Test

---

## 📚 **Weitere Hilfe**

- **Logs prüfen:**
  ```bash
  cd LocalAgent-Pro
  tail -f logs/*.log
  ```

- **Server neustarten:**
  ```bash
  ./restart_server.sh
  ```

- **Docker-Container prüfen:**
  ```bash
  docker ps
  docker logs open-webui
  ```

---

**Viel Erfolg! 🚀**
