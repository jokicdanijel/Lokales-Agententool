# opena6 — Browser Automation Agent: Monitoring → Diagnose → Fix

**Version:** 1.0.0  
**Status:** Implementierungsreife Anleitung  
**Datum:** 4. Januar 2026  
**Authority:** `.github/copilot-instructions.md` (Governance) + `system_baseline.yaml` (Ports)

---

## 0) Zielbild: Was opena6 liefert

opena6 ist dein **deterministischer Browser** — wie wenn du selbst im Browser sitzt, aber:

- **Reproduzierbar** (nicht zufällig)
- **Auditierbar** (jeder Schritt wird geloggt + archiviert)
- **Governanced** (keine unkontrollierten Änderungen ohne Approval)

### Funktionen:

| Funktion | Beschreibung | Beispiel |
|----------|------------|---------|
| **Synthetic Checks** | Seite öffnen → Selector warten → Text prüfen | Login-Flow testen, UI-Verfügbarkeit |
| **Evidence** | Screenshot, HTML-Dump, Console-Errors | Debugging von fehlgeschlagenen Tests |
| **Diagnose** | "Warum ist das down?" (Timeout, 403, Redirect-Loop, Selector-Fehler) | Automatische Fehleranalyse |
| **Approval-basierte Fixes** | Nur mit Human-Approval (kein "Agent löscht zufällig Dateien") | Form-Submit, Passwort-Reset, Kauf |

---

## 1) Ops-Standard: Start-Reihenfolge

**Wichtig:** Die Startreihenfolge ist kritisch. Wenn du sie nicht einhältst, läuft opena6 ins Leere (keine Koordination über opena1).

### 1.1 Core Stack (opena1, opena2, kordp)

```bash
cd Gesamtprojekt/1.opena1&2_portier

# Falls bin/start_stack.sh nicht vorhanden: manuell
./bin/start_opena1.sh
./bin/start_opena2.sh
./bin/start_kordp.sh

# Health-Check
curl http://127.0.0.1:12344/health  # opena1
curl http://127.0.0.1:12345/health  # opena2
```

### 1.2 opena20 (Dashboard) — optional, aber empfohlen

```bash
cd Gesamtprojekt/19.opena20_dashboard_agent

./bin/start_opena20.sh

# Prüfe auf http://127.0.0.1:12349
curl http://127.0.0.1:12349/api/status/all
```

### 1.3 Feature-Agenten nach Plan (opena6 ist Premium)

```bash
cd Gesamtprojekt/5.opena6_browser

# Setup venv, installiere Abhängigkeiten
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Starte opena6
python3 app/main.py

# Oder mit Uvicorn
uvicorn app.main:app --host 127.0.0.1 --port 12351
```

**Port:** opena6 läuft auf `12351` (immutable, siehe `system_baseline.yaml`)

---

## 2) Tools, die opena6 nutzt

opena6 stellt dir **Actions** zur Verfügung. Das ist wie HTTP + SSH im Tutorial — nur "browser-native".

### 2.1 Vorhandene Action-Set (aus `app/models.py`)

| Action | Parameter | Beispiel | Zweck |
|--------|-----------|---------|-------|
| `goto` | `url`, `wait` | `{"action": "goto", "url": "https://example.org", "wait": "load"}` | Seite öffnen, auf Page-Load warten |
| `screenshot` | `label`, `full_page` | `{"action": "screenshot", "label": "homepage", "full_page": true}` | Screenshot machen (archiviert) |
| `click` | `selector`, `timeout_ms` | `{"action": "click", "selector": "button#login", "timeout_ms": 5000}` | Button/Link klicken |
| `fill` | `selector`, `text` | `{"action": "fill", "selector": "input[name=email]", "text": "user@example.org"}` | Formularfeld ausfüllen |
| `wait_for` | `selector`, `timeout_ms` | `{"action": "wait_for", "selector": ".modal", "timeout_ms": 3000}` | Element abwarten |
| `extract` | `selector`, `mode` | `{"action": "extract", "selector": "p.error", "mode": "text"}` | Text/HTML/Attribut extrahieren |
| `submit` | `selector` | `{"action": "submit", "selector": "form#login"}` | Form abschicken |
| `select` | `selector`, `text` | `{"action": "select", "selector": "select[name=country]", "text": "Germany"}` | Dropdown-Option wählen |
| `hover` | `selector` | `{"action": "hover", "selector": "div.submenu"}` | Element hovern (für Menüs) |
| `keyboard` | `keys`, `timeout_ms` | `{"action": "keyboard", "keys": "Enter"}` | Keyboard-Input (Enter, Escape, etc.) |
| `wait` | `timeout_ms` | `{"action": "wait", "timeout_ms": 2000}` | Einfach warten (Delay) |
| `download` | `type`, `selector`, `label` | `{"action": "download", "type": "pdf", "selector": "a.pdf-link", "label": "invoice"}` | Datei herunterladen |

### 2.2 Execution Modes & Config

```json
{
  "request_id": "uuid",
  "steps": [ /* actions wie oben */ ],
  "user_agent": "desktop",        // desktop, mobile, oder custom UA
  "headless": true,               // Browser-Modus
  "viewport": {
    "width": 1280,
    "height": 800
  },
  "compliance": {
    "allow_domains": ["example.org", "localhost"],
    "obey_robots": true
  },
  "archiv": {
    "attach_screenshot": true,
    "attach_html": true,
    "attach_pdf": false,
    "attach_har": false
  },
  "strict": true                  // Fehler auf Action-Fehler (nicht nur Log)
}
```

---

## 3) Output-Contract: Structured JSON Response

opena6 antwortet **maschinenlesbar**. So kannst du Fehlerbehandlung programmieren:

### 3.1 Success Response

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "artifacts": {
    "screenshots": [
      {
        "label": "homepage",
        "path": "archivp/2026-01-04/opena6/550e8400/screenshot-1.png",
        "sha256": "a3c0d...",
        "size_bytes": 524288,
        "mime_type": "image/png"
      }
    ],
    "html": [
      {
        "label": "homepage-dom",
        "path": "archivp/2026-01-04/opena6/550e8400/dom.html",
        "sha256": "b4d1e...",
        "mime_type": "text/html"
      }
    ],
    "extractions": {
      "login_title": "Welcome to Example Corp",
      "error_count": 0
    }
  },
  "extractions": {
    "login_title": "Welcome to Example Corp"
  },
  "timings": {
    "total_ms": 3250,
    "per_step_ms": {
      "step_0_goto": 2100,
      "step_1_screenshot": 450,
      "step_2_extract": 700
    }
  },
  "error": null,
  "strict": true
}
```

### 3.2 Failure Response

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "failed",
  "artifacts": {},
  "extractions": {},
  "timings": {
    "total_ms": 5000
  },
  "error": {
    "code": "SELECTOR_NOT_FOUND",
    "message": "Could not find element matching selector '#login-button' within 5000ms",
    "step": 1,
    "selector": "#login-button"
  },
  "strict": true
}
```

### 3.3 IF/SWITCH Logik (für deine Orchestrierung)

```python
# Pseudo-Code
response = await opena6_execute(playbook)

if response['status'] == 'success':
    if response['artifacts']['screenshots']:
        log(f"✅ Check passed, screenshot: {response['artifacts']['screenshots'][0]['path']}")
    else:
        log("⚠️ Check passed but no evidence collected")

elif response['status'] == 'failed':
    error_code = response['error']['code']
    
    if error_code == 'TIMEOUT':
        alert("Page took too long to load")
    elif error_code == 'SELECTOR_NOT_FOUND':
        alert("UI changed (selector missing)")
    elif error_code == 'HTTP_403':
        alert("Access denied (might need re-auth)")
    else:
        alert(f"Unknown error: {response['error']['message']}")
```

---

## 4) Human-in-the-Loop: Approval vor gefährlichen Aktionen

**Lektion aus dem Tutorial:** Agent darf nicht eigenständig Production-Änderungen durchführen.

### 4.1 Read-Only vs. Write/Side-Effect

| Kategorie | Aktionen | Approval nötig? |
|-----------|----------|-----------------|
| **Read-Only** | `goto`, `screenshot`, `extract`, `wait_for`, `wait`, `hover` | ❌ Nein |
| **Write/Side-Effect** | `click` (auf kritische Button), `fill`, `submit`, `select`, `download` (Payments, Löschungen) | ✅ **Ja** |

### 4.2 Approval-Flow (über opena4 Telegram)

```
1. opena6 erkennt write-Action (z. B. form.submit)
   ↓
2. Erstellt Approval-Request
   {
     "action": "submit",
     "selector": "form#delete-user",
     "confirmation_text": "This will permanently delete user account #12345",
     "request_id": "550e8400-..."
   }
   ↓
3. Sendet über opena4 → Telegram an Admin
   "⚠️ Browser Agent opena6 requests approval:\n
    Action: FORM SUBMIT\n
    Form: form#delete-user\n
    Confirm? /approve_550e8400 or /deny_550e8400"
   ↓
4. Admin antwortet: /approve_550e8400
   ↓
5. opena6 erhält Approval, führt submit() aus
   ↓
6. Ergebnis in opena2 archiviert mit Approval-Token
```

### 4.3 Request-Response Format (Approval)

**Request** (opena6 → opena4):
```json
{
  "target": "telegram",
  "action": "send_approval_request",
  "chat_id": "admin-browser-checks",
  "request_id": "550e8400-...",
  "action_type": "form_submit",
  "prompt": "User account deletion for user#12345. PERMANENT ACTION.",
  "timeout_seconds": 300
}
```

**Response** (opena4 ← Admin via Telegram):
```json
{
  "request_id": "550e8400-...",
  "approved": true,
  "approved_by": "@admin_user",
  "approved_at": "2026-01-04T15:30:00Z"
}
```

---

## 5) Audit & Safepoints: Gerichtsfest

Bei dir ist das **append-only Archiv** der Hebel. Jeder opena6-Lauf wird dokumentiert:

### 5.1 CMD-Phase (Request)

```
opena20 → opena1 (coordinator)
  ↓
opena1 → opena6
  CMD-Safepoint geschrieben nach opena2:
  {
    "src": "opena1",
    "dst": "opena6",
    "kind": "CMD",
    "request_id": "550e8400-...",
    "payload": { /* PlaybookRequest */ }
  }
```

**Archiviert unter:** `archivp/2026-01-04/safepoints/550e8400-CMD.json`

### 5.2 RESP-Phase (Response)

```
opena6 → opena2 (archivator)
  RESP-Safepoint geschrieben:
  {
    "src": "opena6",
    "dst": "opena2",
    "kind": "RESP",
    "request_id": "550e8400-...",
    "payload": { /* PlaybookResponse mit Artifacts */ }
  }
```

**Archiviert unter:** `archivp/2026-01-04/safepoints/550e8400-RESP.json`

### 5.3 Audit-Trail Ansicht

```bash
# Zeige alle opena6-Läufe eines Tags
ls archivp/2026-01-04/safepoints/ | grep "550e8400"
#  → 550e8400-CMD.json
#  → 550e8400-RESP.json
#  → Evidence (screenshots, HTML, etc.)

# Nachverfolgung:
cat archivp/2026-01-04/safepoints/550e8400-CMD.json  # Was wurde angefordert?
cat archivp/2026-01-04/safepoints/550e8400-RESP.json # Was war das Ergebnis?
```

**Dein Vorteil:** Später kannst du immer sagen:
- *"Warum wurde ein Alarm ausgelöst?"* → Safepoints + Evidence
- *"Wer hat genehmigt?"* → opena4-Telegram-Approval-Log
- *"Was hat sich geändert?"* → Hash-Vergleich (Baseline vs. Ist)

---

## 6) Konkreter Workflow: 1:1 nachbaubar

### 6.1 Monitor-Loop (z. B. alle 5 Minuten)

```
Input (von Cronjob, Webhook, oder Manual):
  schedule_trigger = "browser_check_login_5min"

Step 1: Erstelle Playbook
  {
    "request_id": "monitor-login-001-2026-01-04T15-00",
    "steps": [
      {
        "action": "goto",
        "url": "https://example.org/login",
        "wait": "load"
      },
      {
        "action": "screenshot",
        "label": "login-page"
      },
      {
        "action": "wait_for",
        "selector": "form#login-form",
        "timeout_ms": 5000
      },
      {
        "action": "extract",
        "selector": "h1.page-title",
        "mode": "text"
      }
    ],
    "compliance": {
      "allow_domains": ["example.org"],
      "obey_robots": true
    },
    "archiv": {
      "attach_screenshot": true,
      "attach_html": true
    }
  }

Step 2: Execute (POST /run)
  curl -X POST http://127.0.0.1:12351/run \
    -H "Content-Type: application/json" \
    -d @playbook.json

Step 3: Parse Response
  response = await opena6.execute(playbook)

Step 4: Switch auf Status
  if response['status'] == 'success':
    log("✅ Login page is reachable")
    
    if response['extractions']['page_title'] == "Sign In":
      log("✅ Page title correct")
    else:
      alert("⚠️ Page title changed (maybe redirect loop?)")
  
  elif response['status'] == 'failed':
    error = response['error']
    
    if error['code'] == 'TIMEOUT':
      alert("🚨 Login page too slow")
      suggest_action = "check_server_logs_or_db_connections"
    
    elif error['code'] == 'SELECTOR_NOT_FOUND':
      alert("🚨 Form selector changed (UI update?)")
      suggest_action = "update_selectors_in_playbook"
    
    elif error['code'] == 'HTTP_403':
      alert("🚨 Access denied (IP banned?)")
      suggest_action = "check_firewall_rules"
    
    # Optional: Suggestion an opena20 Dashboard senden
    send_to_dashboard({
      "agent": "opena6",
      "status": "CHECK_FAILED",
      "error": error['code'],
      "suggestion": suggest_action,
      "evidence_path": response['artifacts']['screenshots'][0]['path']
    })
```

### 6.2 Fix-Beispiele (nur nach Approval)

#### Fix A: Session Reset / Logout

```json
{
  "request_id": "fix-session-reset-001",
  "steps": [
    {"action": "goto", "url": "https://example.org/logout"},
    {"action": "wait", "timeout_ms": 1000},
    {"action": "goto", "url": "https://example.org/login"},
    {"action": "screenshot", "label": "after-logout"}
  ]
}
```

#### Fix B: Cache Busting

```json
{
  "request_id": "fix-cache-bust-001",
  "steps": [
    {"action": "goto", "url": "https://example.org/login?v=2026-01-04-15-30"},
    {"action": "keyboard", "keys": "Control+Shift+Delete"},
    {"action": "wait", "timeout_ms": 500},
    {"action": "screenshot", "label": "after-clear-cache"}
  ]
}
```

#### Fix C: Alternative Login-Methode

```json
{
  "request_id": "fix-alt-login-001",
  "steps": [
    {"action": "goto", "url": "https://example.org/login"},
    {"action": "click", "selector": "button.login-with-google"},
    {"action": "screenshot", "label": "google-oauth-flow"}
  ]
}
```

---

## 7) Mini-Testplan: Abnahme-Kriterien

Bevor opena6 "live" geht:

### ✅ Checklist

- [ ] **opena6 /health** gibt `{"status": "ok"}` zurück
- [ ] **POST /run** mit einfachem Playbook (goto + screenshot) funktioniert
- [ ] **Artifacts archiviert** unter `archivp/2026-01-04/...`
- [ ] **Safepoints geschrieben** zu opena2 (CMD + RESP)
- [ ] **Read-only Checks** produzieren keine Alerts (kein Spam)
- [ ] **Approval-Flow** funktioniert (opena4 ← opena6 ← Telegram)
- [ ] **Error-Handling** bei Timeout/403/Selector-Fehler
- [ ] **Integration mit opena20** Dashboard
- [ ] **Port 12351** ist eindeutig (kein Konflikt)
- [ ] **Compliance-Config** setzt `allow_domains` korrekt

---

## 8) Endpoints: API-Referenz

### Health & Readiness

```
GET /health
  200: {"service": "opena6", "status": "ok", "port": 12351, "ts": "2026-01-04T...Z"}

GET /ready
  200: {"ready": true, "browser": "playwright-chromium", "version": "1.0.0"}
```

### Execution

```
POST /run
  Request: PlaybookRequest (siehe 3.1)
  Response: PlaybookResponse (success/failed)
  
POST /cancel
  Request: {"request_id": "..."}
  Response: {"request_id": "...", "canceled": bool}
```

### Observability

```
GET /metrics
  200: Prometheus-compatible metrics
  
GET /logs
  200: {"count": N, "files": [...]}
  
GET /api/status
  200: {"service": "opena6", "port": 12351, "browser_ready": true, ...}
```

### Debug

```
GET /
  200: Root info + endpoint list

GET /docs
  FastAPI Swagger UI + OpenAPI spec

POST /api/test-playbook
  Einfacher Test: navigate example.org + screenshot
```

---

## 9) Häufige Probleme & Lösungen

| Problem | Symptom | Diagnose | Fix |
|---------|---------|----------|-----|
| **Browser nicht gestartet** | `503 Service Unavailable` | `GET /ready` → `"ready": false` | Logs checken: `tail -f logs/opena6.jsonl` |
| **Selector nicht gefunden** | `ERROR: SELECTOR_NOT_FOUND` | UI hat sich geändert | Playbook-Selector aktualisieren, Screenshot reviewen |
| **Timeout auf DOM-Ready** | `ERROR: TIMEOUT` | Seite zu langsam oder nicht erreichbar | `wait` erhöhen oder `wait_condition` ändern |
| **HTTP 403 / Access Denied** | `ERROR: HTTP_403` | IP geblockt oder Auth erforderlich | User-Agent, Proxy, oder Cookie-Handling prüfen |
| **Redirect Loop** | Screenshot zeigt Redirect | URL ändert sich in Schleife | Fallback-URL oder Alternative Login nutzen |
| **Port 12351 bereits in Benutzung** | `Bind error` | Anderer Prozess auf dem Port | `lsof -i :12351` und terminieren oder Port in config ändern |

---

## 10) Integration mit opena20 (Dashboard)

opena6 wird über **opena20 → opena1 → opena6** angesteuert (Option-2 Message Flow):

```
opena20 (User startet "Browser Check")
  ↓ POST /route/execute
opena1 (Koordinator leitet zu opena6 weiter)
  ↓ POST /run
opena6 (Führt Playbook aus)
  ↓ Safepoint CMD/RESP zu opena2
opena2 (Archivar speichert Beweise)
  ↓ Index + Notification
opena20 (Dashboard zeigt Ergebnis mit Evidence)
```

**Wichtig:** Benutze **nie** direkten opena6-Zugriff aus dem Frontend. Gehe immer über opena1!

---

## 11) Nächste Schritte

1. **Starten:** `./bin/start_opena6.sh` (oder Uvicorn manuell)
2. **Testen:** `curl http://127.0.0.1:12351/health`
3. **Playbook erstellen:** Siehe 6.1 Monitor-Loop
4. **Approval integrieren:** opena4 Telegram-Bot konfigurieren
5. **Dashboard:** opena20 UI mit opena6-Check-UI erweitern
6. **Monitoring:** Safepoints + Metrics in Observability-Stack

---

**Fragen?** Siehe `.github/copilot-instructions.md` (Governance) oder `system_baseline.yaml` (Ports/IDs).
