# 🚀 CUSTOM PROMPTS - COPY & PASTE FÜR OPENWEBUI

## SO INSTALLIERST DU DIE PROMPTS

1. **Öffne OpenWebUI:** <http://localhost:3000>
2. **Klicke:** Workspace (linke Sidebar) → Functions → **+** Icon
3. **Wähle:** "Create New Function"
4. **Kopiere** einen der Prompts unten
5. **Füge ein** und klicke **"Create"**

---

## ✅ PROMPT 1: CONNECTION CHECK

**In OpenWebUI einfügen:**

```
Teste die Verbindung zwischen OpenWebUI und LocalAgent-Pro API.

Führe folgende Schritte aus:

1. **API Health Check:**
   - URL: http://192.168.0.70:8001/health
   - Erwarte: Status 200, { "status": "ok" }

2. **Modelle prüfen:**
   - URL: http://192.168.0.70:8001/v1/models
   - Erwarte: localagent-pro, llama3.1

3. **Test-Request:**
   - Sende: "Hallo, bist du bereit?"
   - Erwarte: Erfolgreiche Response < 2s

**Gib strukturierten Report:**
✅ Health: ok
✅ Modelle: 2 verfügbar
✅ Response-Zeit: Xs
✅ System: Bereit
```

**Konfiguration:**

- **Name:** Connection Check
- **Command:** `/connection`
- **Access:** Public

---

## ✅ PROMPT 2: MODEL TEST

**In OpenWebUI einfügen:**

```
Teste das Modell "localagent-pro" auf Funktionalität.

**Test-Schritte:**

1. **Verfügbarkeit:**
   - Prüfe: Modell in /v1/models Liste
   - Status: Verfügbar?

2. **Smoke-Test:**
   - Prompt: "Was kannst du?"
   - Erwarte: Klare Antwort
   - Zeit: < 3s

3. **Performance:**
   - Messe: Tokens/Sekunde
   - GPU: Aktiv?
   - Benchmark: > 5 t/s

**Gib Report:**
✅ Verfügbar: Ja/Nein
✅ Response-Zeit: Xs
✅ Tokens/s: X t/s
✅ GPU: Aktiv/Inaktiv
```

**Konfiguration:**

- **Name:** Model Test
- **Command:** `/modeltest`
- **Access:** Public

---

## ✅ PROMPT 3: E2E TEST

**In OpenWebUI einfügen:**

```
Vollständiger End-to-End-Test: OpenWebUI → LocalAgent-Pro → Ollama

**Test-Sequenz:**

1. **Infrastruktur:**
   - Backend: http://192.168.0.70:8001/health
   - Ollama: Läuft?
   - OpenWebUI: http://localhost:3000

2. **API-Integration:**
   - Verbindung: Erfolgreich?
   - Modell: localagent-pro verfügbar?

3. **Funktionstest:**
   - Sende: "Erstelle Datei test.txt mit Hallo"
   - Erwarte: Tool ausgeführt, Datei erstellt

4. **Streaming:**
   - Test: Word-by-word Anzeige
   - Latenz: < 100ms pro Chunk

**Report:**
✅ Backend: Status
✅ API: Verbunden
✅ Tools: Funktionieren
✅ Streaming: Aktiv
✅ Performance: X t/s
```

**Konfiguration:**

- **Name:** E2E Test
- **Command:** `/e2etest`
- **Access:** Public

---

## 🎯 SCHNELLSTART

### Nach Installation der Prompts

1. **Teste Verbindung:**

   ```
   /connection
   ```

   ✅ Sollte zeigen: "System bereit"

2. **Teste Modell:**

   ```
   /modeltest
   ```

   ✅ Sollte zeigen: "Tokens/s: ~9 t/s"

3. **Teste Tool-System:**

   ```
   /e2etest
   ```

   ✅ Sollte Datei erstellen

---

## 🔧 ALTERNATIVE: DIREKT TESTEN (OHNE CUSTOM PROMPTS)

Falls du die Prompts nicht installieren möchtest, kannst du direkt testen:

### Test 1: Chat

```
Hallo, bist du bereit?
```

### Test 2: Datei erstellen

```
Erstelle Datei hello.txt mit "Hello from OpenWebUI"
```

### Test 3: Datei lesen

```
Lies Datei hello.txt
```

### Test 4: Verzeichnis

```
Liste alle Dateien auf
```

---

## ✅ API-VERBINDUNG (WICHTIG!)

**Stelle sicher, dass in OpenWebUI konfiguriert ist:**

```
Settings → Connections → OpenAI API

API Base URL: http://192.168.0.70:8001/v1
API Key: (leer lassen)

→ Save & Test
→ Sollte zeigen: "Connection successful"
```

---

## 📊 ERWARTETE ERGEBNISSE

### Connection Test

```
✅ Health: ok
✅ Modelle: localagent-pro, llama3.1
✅ Response-Zeit: 0.2s
✅ System: Bereit
```

### Model Test

```
✅ Verfügbar: Ja
✅ Response-Zeit: 1.2s
✅ Tokens/s: 9.2 t/s (GPU aktiv)
✅ GPU: NVIDIA GTX 1050 - 87% Auslastung
```

### E2E Test

```
✅ Backend: Läuft auf 192.168.0.70:8001
✅ API: Verbunden
✅ Tool: write_file() ausgeführt
✅ Datei: test.txt erstellt (5 bytes)
✅ Streaming: Aktiv (42 Chunks)
✅ Performance: 9.2 t/s
```

---

## 🆘 PROBLEME?

### "Connection failed"

```bash
cd LocalAgent-Pro
./restart_server.sh
```

### "Model not found"

```bash
ollama pull llama3.1
```

### "Slow response"

```bash
nvidia-smi  # GPU prüfen
```

---

**Du bist bereit! Viel Erfolg! 🚀**
