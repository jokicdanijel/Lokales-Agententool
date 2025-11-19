# OpenWebUI – Verbindungsprüfung

**Befehl:** `/openwebui_connection`  
**Zugriff:** `public`

## Eingabeaufforderung

Verifizieren Sie die OpenWebUI-Verbindung und bestätigen Sie, dass die API-Endpunkte erreichbar sind. Führen Sie eine vollständige Diagnose durch.

## Eingabefelder

```
{{api_base_url | url:placeholder="z.B. http://127.0.0.1:8001/v1":required}}
{{openwebui_port | number:placeholder="Port (z.B. 3000)":default=3000:required}}
{{model | select:options=["tinyllama","localagent-pro","llama2:latest","llama3.1"]:default="tinyllama":required}}
{{health_endpoint | text:placeholder="Health-Check-Endpunkt":default="/health":required}}
{{description | textarea:placeholder="Zusätzliche Hinweise oder Fehlerfälle (optional)"}}
```

## Prompt-Template

```
🔍 **OpenWebUI-Verbindungstest**

Führe folgende Schritte durch:

1. **API-Erreichbarkeit prüfen:**
   - Teste Health-Check: {{api_base_url}}{{health_endpoint}}
   - Erwarteter Status: 200 OK
   - Prüfe Response-Zeit (< 1s)

2. **Modell-Verfügbarkeit:**
   - Teste: {{api_base_url}}/models
   - Verifiziere, dass "{{model}}" verfügbar ist
   - Liste alle verfügbaren Modelle auf

3. **OpenWebUI-Verbindung:**
   - Prüfe, ob OpenWebUI auf Port {{openwebui_port}} läuft
   - Teste Websocket-Verbindung (falls verfügbar)

4. **Diagnose-Output:**
   ✅ **Erfolgreich:** Alle Endpoints erreichbar
   ⚠️ **Warnung:** [Beschreibe Probleme]
   ❌ **Fehler:** [Detaillierte Fehlermeldung]

**Zusätzliche Hinweise:**
{{description}}

**Führe die Tests aus und gib eine strukturierte Zusammenfassung.**
```

---

## Beispiel-Verwendung

1. In OpenWebUI: Workspace → Functions → Custom Prompts
2. "New Prompt" klicken
3. Oben stehenden Prompt einfügen
4. Speichern
5. Im Chat: `/openwebui_connection` eingeben und Felder ausfüllen

---

## Erwarteter Output

```
🔍 OpenWebUI-Verbindungstest - Ergebnisse:

1. ✅ API Health-Check
   - URL: http://127.0.0.1:8001/v1/health
   - Status: 200 OK
   - Response-Zeit: 0.12s
   - Server-Info: {
       "status": "ok",
       "model": "tinyllama",
       "sandbox": true
     }

2. ✅ Modell-Verfügbarkeit
   - Endpoint: http://127.0.0.1:8001/v1/models
   - Verfügbare Modelle:
     • tinyllama ✅ (ausgewählt)
     • localagent-pro
     • llama3.1

3. ✅ OpenWebUI-Verbindung
   - Port 3000: Aktiv
   - Frontend: Erreichbar
   - API-Integration: Funktionsfähig

📊 Zusammenfassung:
✅ Alle Tests bestanden
🚀 System bereit für Nutzung
```

---

## Troubleshooting

### Problem: "Connection refused"
```bash
# Server-Status prüfen
ps aux | grep openwebui_agent_server

# Server starten (falls nicht läuft)
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Lokales\ Agententool/LocalAgent-Pro
./start_server.sh
```

### Problem: "Model not found"
```bash
# Verfügbare Modelle anzeigen
ollama list

# Modell herunterladen
ollama pull tinyllama
```

### Problem: "Health check failed"
```bash
# Logs prüfen
tail -f logs/localagent_pro_main.log

# Ollama-Status
systemctl status ollama
```
