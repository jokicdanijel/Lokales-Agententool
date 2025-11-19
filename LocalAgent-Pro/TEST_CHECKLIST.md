# LocalAgent-Pro - Test-Checkliste

**Version:** 1.0  
**Datum:** 16. November 2025  
**System:** LocalAgent-Pro mit OpenWebUI-Integration

---

## ✅ Grundlegende System-Tests

### 1. Backend-Server
- [ ] **Server startet erfolgreich**
  ```bash
  ./start_server.sh
  # Erwarte: Server läuft auf Port 8001
  ```

- [ ] **Health-Check funktioniert**
  ```bash
  curl -s http://127.0.0.1:8001/health | jq '.'
  # Erwarte: status: "ok", allowed_domains: ["*"]
  ```

- [ ] **Models-Endpoint antwortet**
  ```bash
  curl -s http://127.0.0.1:8001/v1/models | jq '.data[].id'
  # Erwarte: "localagent-pro", "llama3.1"
  ```

---

## 🔧 Ollama-Integration Tests

### 2. Ollama-Service
- [ ] **Ollama läuft**
  ```bash
  systemctl status ollama
  # Erwarte: active (running)
  ```

- [ ] **GPU-Beschleunigung aktiv**
  ```bash
  journalctl -u ollama -n 50 | grep "GPU"
  # Erwarte: "offloaded to GPU", "VRAM"
  ```

- [ ] **Modelle verfügbar**
  ```bash
  ollama list
  # Erwarte: tinyllama, llama3.1
  ```

- [ ] **Direkte Ollama-Anfrage**
  ```bash
  curl -s http://127.0.0.1:11434/api/generate -d '{
    "model": "tinyllama",
    "prompt": "Hallo",
    "stream": false
  }' | jq '.response'
  # Erwarte: Erfolgreiche Antwort
  ```

---

## 🛠️ Tool-System Tests

### 3. Datei-Operationen

- [ ] **Datei erstellen**
  ```
  In OpenWebUI: "Erstelle Datei test_write.txt mit Test Content 123"
  Verifizierung: cat ~/localagent_sandbox/test_write.txt
  Erwarte: "Test Content 123"
  ```

- [ ] **Datei lesen**
  ```
  In OpenWebUI: "Lies Datei test_write.txt"
  Erwarte: Content wird angezeigt
  ```

- [ ] **Verzeichnis auflisten**
  ```
  In OpenWebUI: "Liste alle Dateien auf"
  Erwarte: Liste der Sandbox-Dateien
  ```

- [ ] **Sandbox-Isolation testen**
  ```bash
  ls -lh ~/localagent_sandbox/
  # Erwarte: Alle erstellten Dateien hier, nicht im System-Root
  ```

---

### 4. Web-Fetch Tests

- [ ] **Interne API abrufen**
  ```
  In OpenWebUI: "Lade die Webseite http://172.17.0.1:8001/v1/models"
  Erwarte: JSON mit Modellen
  ```

- [ ] **Externe Domain (erlaubt)**
  ```
  In OpenWebUI: "Lade github.com"
  Erwarte: HTML-Content
  ```

- [ ] **Wildcard funktioniert**
  ```
  In OpenWebUI: "Lade example.com"
  Erwarte: Erfolg (weil allowed_domains: ["*"])
  ```

---

### 5. Shell-Kommando Tests

- [ ] **Shell blockiert im Sandbox-Modus**
  ```
  In OpenWebUI: "Führe Kommando 'ls -la' aus"
  Erwarte: "Shell-Kommandos sind im Sandbox-Modus deaktiviert"
  ```

- [ ] **Shell funktioniert ohne Sandbox** (optional)
  ```bash
  # 1. Config ändern: sandbox: false
  # 2. Server neu starten
  # 3. In OpenWebUI: "Führe Kommando 'pwd' aus"
  # Erwarte: Aktuelles Verzeichnis angezeigt
  ```

---

## 🌐 OpenWebUI-Integration Tests

### 6. Verbindung & Konfiguration

- [ ] **OpenWebUI läuft**
  ```bash
  docker ps | grep open-webui
  # Erwarte: Container "open-webui" running
  ```

- [ ] **API-Verbindung konfiguriert**
  ```
  OpenWebUI → Settings → Connections
  API Base URL: http://172.17.0.1:8001/v1
  Erwarte: Grüner Haken oder "Connected"
  ```

- [ ] **Modelle erscheinen in Dropdown**
  ```
  OpenWebUI → Chat → Modell-Dropdown
  Erwarte: localagent-pro, llama3.1 sichtbar
  ```

---

### 7. Chat-Funktionalität

- [ ] **Einfache Konversation**
  ```
  In OpenWebUI: "Hallo, wie geht es dir?"
  Erwarte: Freundliche Antwort von Ollama
  ```

- [ ] **Tool + KI Hybrid**
  ```
  In OpenWebUI: "Erstelle Datei hello.txt mit Hello World und erkläre was du gemacht hast"
  Erwarte: Datei erstellt + Erklärung
  ```

- [ ] **Streaming funktioniert**
  ```
  In OpenWebUI: "Erkläre Künstliche Intelligenz in 5 Sätzen"
  Erwarte: Word-by-word Streaming-Anzeige
  ```

---

## 🚀 Performance-Tests

### 8. GPU-Performance

- [ ] **GPU-Auslastung während Inferenz**
  ```bash
  # Terminal 1:
  watch -n 1 nvidia-smi
  
  # Terminal 2 / OpenWebUI:
  "Schreibe eine Geschichte über Roboter (200 Wörter)"
  
  # Erwarte: GPU-Auslastung 80-100%, VRAM 1-2 GB
  ```

- [ ] **Token-Geschwindigkeit messen**
  ```bash
  python benchmark_cpu_vs_gpu.py
  # Erwarte: 6-10 t/s (tinyllama, GPU)
  ```

- [ ] **Response-Zeit akzeptabel**
  ```
  In OpenWebUI: "Hi"
  Erwarte: Antwort in < 2s
  ```

---

## 📊 Logging-Tests

### 9. Log-Dateien

- [ ] **Logs werden geschrieben**
  ```bash
  ls -lh logs/
  # Erwarte: localagent_pro_main.log, api.log, tools.log, ollama.log
  ```

- [ ] **Main-Log prüfen**
  ```bash
  tail -50 logs/localagent_pro_main.log
  # Erwarte: Server-Start-Meldungen, keine kritischen Fehler
  ```

- [ ] **API-Log zeigt Requests**
  ```bash
  tail -50 logs/localagent_pro_api.log
  # Erwarte: Chat Completion Requests, Health Checks
  ```

- [ ] **Tool-Log zeigt Ausführungen**
  ```bash
  tail -50 logs/localagent_pro_tools.log
  # Erwarte: write_file, read_file, list_files Einträge
  ```

---

## 🔒 Sicherheits-Tests

### 10. Sandbox-Sicherheit

- [ ] **Dateien bleiben in Sandbox**
  ```bash
  # Erstelle in OpenWebUI: "Erstelle Datei ../escape.txt mit Test"
  # Prüfe:
  ls ~/localagent_sandbox/../escape.txt
  # Erwarte: Datei existiert NICHT außerhalb Sandbox
  
  ls ~/localagent_sandbox/escape.txt
  # Erwarte: Datei hier (relativ zur Sandbox)
  ```

- [ ] **Shell-Kommandos blockiert**
  ```
  In OpenWebUI: "Führe 'rm -rf /' aus"
  Erwarte: Blockiert (Sandbox-Modus)
  ```

- [ ] **Gefährliche Kommandos abgefangen**
  ```
  Falls Sandbox deaktiviert:
  "Führe 'sudo apt-get update' aus"
  Erwarte: "Gefährliches Kommando blockiert"
  ```

---

## 🧪 Custom Prompts Tests (falls installiert)

### 11. Custom Prompts

- [ ] **Connection Check Prompt**
  ```
  /openwebui_connection
  API Base URL: http://172.17.0.1:8001/v1
  OpenWebUI Port: 3000
  Modell: localagent-pro
  
  Erwarte: Alle Tests bestanden (Health, Models, Connection)
  ```

- [ ] **Models Test Prompt**
  ```
  /openwebui_models_test
  API Base URL: http://172.17.0.1:8001/v1
  Modell: tinyllama
  Test-Typ: smoke-test
  
  Erwarte: Modell verfügbar, Response < 5s
  ```

- [ ] **E2E Test Prompt**
  ```
  /openwebui_e2e_test
  API Base URL: http://172.17.0.1:8001/v1
  OpenWebUI URL: http://localhost:3000
  Modell: localagent-pro
  Sample Prompt: "Erstelle Datei test.txt mit Test"
  
  Erwarte: Alle Phasen erfolgreich
  ```

---

## 🔄 Stress-Tests

### 12. Lasttests

- [ ] **Mehrere Requests parallel**
  ```bash
  for i in {1..5}; do
    curl -s -X POST http://127.0.0.1:8001/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{"model":"localagent-pro","messages":[{"role":"user","content":"Test '$i'"}]}' &
  done
  wait
  # Erwarte: Alle Requests erfolgreich
  ```

- [ ] **Lange Session**
  ```
  In OpenWebUI: 10 verschiedene Prompts nacheinander
  Erwarte: Keine Performance-Degradation
  ```

- [ ] **Großer Prompt**
  ```
  In OpenWebUI: "Schreibe einen Aufsatz über KI (500 Wörter)"
  Erwarte: Vollständige Antwort, kein Timeout
  ```

---

## 📱 Browser-Kompatibilität

### 13. OpenWebUI UI-Tests

- [ ] **Chat-Interface funktioniert**
  - Nachrichten senden ✓
  - Streaming sichtbar ✓
  - Modell-Wechsel funktioniert ✓

- [ ] **Datei-Uploads** (falls unterstützt)
  - Datei hochladen
  - Content verarbeiten

- [ ] **History funktioniert**
  - Frühere Chats sichtbar
  - Kontext erhalten

---

## 🐛 Error-Handling Tests

### 14. Fehlerbehandlung

- [ ] **Ungültige Requests**
  ```bash
  curl -X POST http://127.0.0.1:8001/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"invalid": "data"}'
  # Erwarte: Error-Response, Server läuft weiter
  ```

- [ ] **Timeout-Verhalten**
  ```bash
  # Ollama stoppen:
  sudo systemctl stop ollama
  
  # In OpenWebUI: Chat-Anfrage senden
  # Erwarte: Timeout-Meldung, kein Crash
  
  # Ollama wieder starten:
  sudo systemctl start ollama
  ```

- [ ] **Fehlende Datei**
  ```
  In OpenWebUI: "Lies Datei nonexistent.txt"
  Erwarte: "Datei nicht gefunden", kein Crash
  ```

---

## 🔧 Wartungs-Tests

### 15. System-Wartung

- [ ] **Log-Rotation**
  ```bash
  ./cleanup_logs.sh
  # Erwarte: Alte Logs archiviert/gelöscht
  ```

- [ ] **Disk-Space prüfen**
  ```bash
  du -sh ~/localagent_sandbox/
  du -sh logs/
  # Erwarte: Angemessene Größen
  ```

- [ ] **Server-Neustart ohne Datenverlust**
  ```bash
  # 1. Erstelle Datei in Sandbox
  # 2. Server neu starten
  # 3. Prüfe ob Datei noch existiert
  ```

---

## 📈 Monitoring-Tests

### 16. System-Monitoring

- [ ] **Resource-Nutzung akzeptabel**
  ```bash
  htop  # oder top
  # Prüfe: CPU, RAM, VRAM
  # Erwarte: Keine Memory Leaks
  ```

- [ ] **Ollama-Service stabil**
  ```bash
  journalctl -u ollama --since "1 hour ago" | grep -i error
  # Erwarte: Keine kritischen Fehler
  ```

- [ ] **Network-Traffic normal**
  ```bash
  netstat -tupln | grep 8001
  # Erwarte: Port 8001 LISTEN
  ```

---

## 🎯 Funktionale Anforderungen

### 17. Feature-Checkliste

- [ ] **Alle 5 Tools funktionieren**
  - ✅ read_file
  - ✅ write_file
  - ✅ list_files
  - ✅ run_shell (oder blockiert wenn Sandbox aktiv)
  - ✅ fetch

- [ ] **OpenAI-API-Kompatibilität**
  - ✅ /v1/models
  - ✅ /v1/chat/completions
  - ✅ Streaming-Support

- [ ] **Ollama-Integration**
  - ✅ GPU-Beschleunigung
  - ✅ Modell-Wechsel
  - ✅ Performance optimal

---

## 📋 Abnahme-Checkliste

### 18. Production-Ready?

- [ ] **Alle Basic-Tests bestanden** (1-9)
- [ ] **Sicherheits-Tests bestanden** (10)
- [ ] **Performance akzeptabel** (8)
- [ ] **Error-Handling robust** (14)
- [ ] **Logs funktionieren** (9)
- [ ] **OpenWebUI voll funktionsfähig** (6-7)
- [ ] **Dokumentation vollständig**
  - [ ] README.md
  - [ ] INSTALLATION.md
  - [ ] GPU_SETUP.md
  - [ ] Custom Prompts README

---

## 🚀 Next Steps nach Tests

### Nach erfolgreichen Tests:

1. **Production-Deployment**
   - Server als systemd-Service einrichten
   - Automatischer Start bei Boot
   - Log-Rotation konfigurieren

2. **Backup-Strategie**
   - Sandbox regelmäßig sichern
   - Config-Backups
   - Logs archivieren

3. **Monitoring einrichten**
   - Prometheus/Grafana (optional)
   - Alert bei Fehlern
   - Performance-Tracking

4. **Skalierung** (optional)
   - Load Balancer für mehrere Instanzen
   - Redis für Session-Management
   - Nginx als Reverse Proxy

---

## 📊 Test-Ergebnis-Template

```markdown
# Test-Durchlauf vom [DATUM]

## Zusammenfassung
- Getestete Features: X/Y
- Erfolgsquote: XX%
- Kritische Fehler: X
- Warnings: Y

## Details
- Backend: ✅/❌
- Ollama: ✅/❌
- Tools: ✅/❌
- OpenWebUI: ✅/❌
- Performance: ✅/❌
- Sicherheit: ✅/❌

## Offene Issues
1. [Beschreibung]
2. [Beschreibung]

## Notizen
- [Besonderheiten]
- [Verbesserungsvorschläge]
```

---

**Status:** System bereit für umfassende Tests! 🎯  
**Nächster Schritt:** Arbeite diese Checkliste systematisch ab!
