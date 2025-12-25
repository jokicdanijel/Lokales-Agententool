# LocalAgent-Pro – Developer Notes

---

## Pydantic/Framework-Migration – Stand: 2025-12-01

### INVENTORY Ergebnis

| Eigenschaft          | Wert                                 |
| -------------------- | ------------------------------------ |
| **Framework**        | Flask (flask, flask-cors)            |
| **Pydantic-Modelle** | ❌ Keine (nur Python-Dicts + typing) |
| **BaseSettings**     | ❌ Nicht verwendet                   |
| **Konfiguration**    | `config/config.yaml` (YAML)          |

### Migrationsaktionen

| Phase                      | Anwendbar? | Aktion                                                        |
| -------------------------- | ---------- | ------------------------------------------------------------- |
| **Phase 1 (Pydantic V2)**  | ❌ NEIN    | Keine Pydantic-Klassen vorhanden                              |
| **Phase 2 (Framework)**    | ❌ NEIN    | Flask hat kein `@app.on_event` – kein Äquivalent zu migrieren |
| **Phase 3 (Sanity-Check)** | ✅ JA      | Tests ausgeführt, Endpoints geprüft                           |

### Test-Status

```
pytest tests/test_api.py tests/test_security.py tests/test_web_fetch_binary.py
→ Tests laufen, /health + /v1/models + /v1/chat/completions funktionieren
→ Keine Deprecation-Warnings
```

### Fazit

**Keine Migration nötig.**
LocalAgent-Pro verwendet:

- **Flask** (ohne Deprecations)
- **Reine Python-Dicts** (kein Pydantic)
- **YAML-Config** (kein BaseSettings)

API-Signaturen, Business-Logik und Sandbox-Verhalten **unverändert**.

---

## Ollama-Anbindung (Stand: 2025-12-01)

### Aktuell verwendeter Endpoint

- **URL:** `http://localhost:11434/api/chat`
- **Methode:** POST
- **Modell-ID:** `llama3.1:8b` (konfigurierbar in `config/config.yaml`)

### Request-Format (Ollama /api/chat)

```json
{
  "model": "llama3.1:8b",
  "messages": [{ "role": "user", "content": "..." }],
  "stream": false
}
```

### Response-Mapping

- Ollama: `response.message.content`
- → OpenAI-Format: `choices[0].message.content`

### Fehler-Handling

- HTTP != 200 von Ollama → LocalAgent-Pro gibt 502 mit Fehlerdetails zurück
- Timeout (120s) → 504
- Connection Error → 503

### Wichtige Hinweise

1. **Modell muss in Ollama geladen sein:** `ollama pull llama3.1:8b`
2. **Bei Ollama-Updates:** API-Endpunkte prüfen (`/api/chat` vs `/api/generate`)
3. **Logs:** Fehler werden in `logs/localagent.log` protokolliert

---

## LocalAgent-Pro Connectivity (Stand: 2025-12-01)

### Healthcheck-Ergebnisse

| Endpoint               | Host         | Status | Details                                                           |
| ---------------------- | ------------ | ------ | ----------------------------------------------------------------- |
| `/health`              | 127.0.0.1    | ✅ OK  | `status: healthy`, sandbox: `/home/danijel-jd/localagent_sandbox` |
| `/health`              | 192.168.0.70 | ✅ OK  | LAN-Zugriff funktioniert                                          |
| `/v1/models`           | 127.0.0.1    | ✅ OK  | Modelle: `llama3.1:8b`                                            |
| `/v1/chat/completions` | 127.0.0.1    | ✅ OK  | Testprompt → Antwort erhalten                                     |

### OpenWebUI-Integration

| Parameter        | Wert                                                            |
| ---------------- | --------------------------------------------------------------- |
| **Base URL**     | `http://192.168.0.70:8001/v1` (oder `http://127.0.0.1:8001/v1`) |
| **Model**        | `llama3.1:8b`                                                   |
| **Content-Type** | `application/json`                                              |
| **Host-Binding** | `0.0.0.0:8001` (alle Interfaces)                                |

### Bekannte Fehlerquellen

| Fehler                 | HTTP-Code | Ursache                                   | Lösung                       |
| ---------------------- | --------- | ----------------------------------------- | ---------------------------- |
| Duplicate Request      | 429       | Identischer Request innerhalb kurzer Zeit | Cache leert sich automatisch |
| Bad Request            | 400       | Falsches JSON-Format                      | Payload prüfen               |
| Unsupported Media Type | 415       | Kein `Content-Type: application/json`     | Header setzen                |
| 500 in OpenWebUI       | –         | Base URL oder Model falsch                | Siehe Checkliste unten       |

### OpenWebUI-Fehler-Checkliste

Wenn "500: WebUI öffnen: Serververbindungsfehler" auftritt:

1. ✅ **Base URL prüfen:** `http://192.168.0.70:8001/v1` (mit `/v1`!)
2. ✅ **Model prüfen:** Exakt `llama3.1:8b` (wie in `/v1/models` angezeigt)
3. ✅ **API Key:** Beliebiger Wert (z.B. `localagent-pro`)
4. ✅ **LocalAgent-Pro läuft:** `curl http://127.0.0.1:8001/health`
5. ✅ **Host-Binding:** Config muss `host: 0.0.0.0` haben

---

## LocalAgent-Pro Sandbox-Policy (Stand: 2025-12-01)

### Ziel der Sandbox

Der Ordner `/home/danijel-jd/localagent_sandbox` dient als **Arbeits- und Spielwiese** für LocalAgent-Pro:

- temporäre Dateien
- Tool-Outputs
- Test-Dateien
- Experimentierfläche für Copilot-/Agent-Aktionen

Die Sandbox darf **belastungsfrei aufgeräumt** werden – aber nur nach klaren Regeln, um den Betrieb nicht zu gefährden.

---

### 1. Kritische Assets (NICHT ANFASSEN)

Folgende Dateien/Ordner gelten als **betriebsrelevant** und dürfen weder gelöscht noch umbenannt werden:

- `LocalAgent-Pro/`
- `downloads/`
- `home/`
- `config.yaml`
- `localagent-actions.log`

**Policy:**

- Diese Einträge sind für den Agent und die Systemintegration **read-only**.
- Cleanup-Skripte und Tools müssen diese Pfade explizit ausnehmen.

---

### 2. „Komische" Dateien aus Auto-Runs & Tests

In der Vergangenheit wurden durch Tools/Tests Dateien mit problematischen Namen erzeugt, z. B.:

- `Task:`
- `History:`
- `lesen:`
- `soll:`
- `-`
- `(Linux-Mint-optimiert)`

Diese Dateinamen sind:

- für viele Tools unpraktisch (Doppelpunkt, Klammern, Ein-Buchstaben-Namen)
- nicht Teil des produktiven Workflows
- rein aus Testläufen / Experimenten entstanden

**Status (Stand 2025-12-01):**
Diese Altlasten wurden **entfernt**.

---

### 3. Cleanup-Policy (für Copilot / Automatisierung)

Wenn ein Agent oder ein Script einen Sandbox-Cleanup durchführt, gilt:

#### 3.1. Vor jedem Cleanup: INVENTORY

1. `ls -la /home/danijel-jd/localagent_sandbox`
2. Dateien/Ordner klassifizieren in:
   - **PROTECTED** – nicht löschen (siehe Abschnitt 1)
   - **CANDIDATE** – potenziell löschbar (siehe Regeln unten)

#### 3.2. Löschbare Kandidaten (CANDIDATE-Regeln)

Eine Datei darf automatisiert gelöscht werden, wenn **alle** folgenden Bedingungen erfüllt sind:

1. Sie ist **nicht** in der PROTECTED-Liste und
2. **Mindestens eine** der folgenden Heuristiken trifft zu:

- Dateiname endet auf `:`
  - Beispiele: `Task:`, `History:`, `lesen:`, `soll:`
- Dateiname ist exakt `-`
- Dateiname ist exakt `(Linux-Mint-optimiert)`
- Dateiname entspricht einem rein temporären Testmuster
  - z. B. `*_test.txt`, `*_legacy_*.txt`, wenn sie nicht in DEV_NOTES dokumentiert sind

**Empfehlung:**

- Bei größeren Dateien (> 100 KB) optional einmal `head`/`tail` prüfen, bevor sie automatisiert gelöscht werden.

#### 3.3. Ausführung (Beispiel-Befehle)

**Manuelles Cleanup-Beispiel:**

```bash
cd /home/danijel-jd/localagent_sandbox

# Kandidaten anzeigen
ls -la

# Problemdateien entfernen (Beispiele)
rm -v -- 'Task_legacy_1.txt' 'lesen:' 'soll:' '(Linux-Mint-optimiert)' '-' 2>&1
```

---

### 4. Verhalten für Copilot-/Agent-Systeme

Jeder Agent, der in der Sandbox arbeitet (z. B. LocalAgent-Pro, Portier-Agents, Copilot-Tools), muss:

1. **Immer zuerst Inventory machen**
   - Verzeichnis lesen
   - Kritische Assets identifizieren
   - Löschkandidaten nur nach obiger Policy markieren

2. **Keinen produktiven Code / Konfiguration löschen**
   - `LocalAgent-Pro/`, `config.yaml` etc. sind tabu

3. **Cleanup-Aktion dokumentieren**
   - z. B. Eintrag in `localagent-actions.log`:
   ```
   [YYYY-MM-DD HH:MM:SS] SANDBOX_CLEANUP: removed ['Task_legacy_1.txt','lesen:','soll:','(Linux-Mint-optimiert)','-']
   ```

---

### 5. Aktueller Status (Stand 2025-12-01)

Alle historisch problematischen Dateinamen wurden bereinigt:

| Datei                    | Aktion               |
| ------------------------ | -------------------- |
| `Task:`                  | umbenannt → entfernt |
| `History:`               | entfernt             |
| `lesen:`                 | entfernt             |
| `soll:`                  | entfernt             |
| `(Linux-Mint-optimiert)` | entfernt             |
| `-`                      | entfernt             |

**Sandbox ist aktuell sauber und konsistent:**

- Kritische Verzeichnisse & Files sind vorhanden
- Keine „Sonderzeichen-Leichen" mehr im Root der Sandbox

---

### 6. TL;DR für zukünftige dich & Copilot

- **Finger weg von:** `LocalAgent-Pro/`, `downloads/`, `home/`, `config.yaml`, `localagent-actions.log`
- **Löschen ist ok für:**
  - Dateien, die mit `:` enden
  - Datei `-`
  - alte Test-/Legacy-Dateien, die keine produktive Funktion haben
- **Immer zuerst INVENTORY, dann CLEANUP, dann LOG-EINTRAG.**
