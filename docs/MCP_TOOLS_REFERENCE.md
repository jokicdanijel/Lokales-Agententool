# 🔧 MCP Tools Reference Guide

**Letzte Aktualisierung:** 24. Dezember 2025
**Status:** Vollständig dokumentiert
**Verfügbare Tools:** 50+ (GitHub, Playwright, Web Search)

---

## 📋 Übersicht

Model Context Protocol (MCP) stellt umfangreiche Tools für Automation und Integration bereit. Diese Dokumentation beschreibt alle verfügbaren Tools in den Kategorien:

1. **GitHub MCP Server** (40+ Tools)
2. **Playwright Browser Automation** (20+ Tools)
3. **Web Search & Analysis**

---

## 🐙 GitHub MCP Server Tools

### Workflow & Actions Management

#### `get_workflow_runs`
**Beschreibung:** Ruft GitHub Actions Workflow-Läufe ab
**Verwendung:** Workflow-Status monitoren, Fehler analysieren

```bash
# Beispiel: Letzte 10 Läufe von opena5 abrufen
github-mcp-server/get_workflow_runs:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  workflow_id: "opena5.yml"
  per_page: 10
```

**Rückgabewerte:**
- `id`: Eindeutige Run-ID
- `status`: queued, in_progress, completed, requested, waiting
- `conclusion`: success, failure, neutral, cancelled, skipped, timed_out
- `run_number`: Läufige Nummer
- `created_at`, `updated_at`: Zeitstempel
- `head_commit`: Commit SHA

**Filtern:**
```
status:
  - queued
  - in_progress
  - completed
  - requested
  - waiting

event:
  - push, pull_request, schedule, workflow_dispatch
  - workflow_call, registry_package, release
```

---

#### `get_job_logs`
**Beschreibung:** Ruft Logs von GitHub Actions Jobs ab
**Verwendung:** Debugging von fehlgeschlagenen Workflows

```bash
# Option 1: Logs für einzelnen Job
github-mcp-server/get_job_logs:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  job_id: 12345678
  tail_lines: 500
  return_content: true

# Option 2: Alle fehlgeschlagenen Jobs in Run abrufen
github-mcp-server/get_job_logs:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  run_id: 8765432
  failed_only: true
  tail_lines: 1000
```

**Rückgabewerte:**
- `logs[]`: Array mit Log-Einträgen
- `url`: URL zum Log im GitHub UI
- `status`: Job-Status
- `conclusion`: Job-Ergebnis

---

### Commit & Version Management

#### `get_commit`
**Beschreibung:** Ruft Commit-Details mit optionalen Diffs ab
**Verwendung:** Code-Review, Change-Tracking

```bash
github-mcp-server/get_commit:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  sha: "febf0792"
  include_diff: true
  perPage: 100
```

**Rückgabewerte:**
- `sha`: Commit-Hash
- `message`: Commit-Nachricht
- `author`, `committer`: Name, Email, Datum
- `files[]`: Geänderte Dateien mit Stats
  - `filename`: Dateiname
  - `additions`, `deletions`: Zeilenänderungen
  - `changes`: Gesamtänderungen
  - `patch`: Diff (falls `include_diff: true`)

---

#### `list_commits`
**Beschreibung:** Listet Commits eines Branches auf
**Verwendung:** Commit-Historie durchsuchen

```bash
github-mcp-server/list_commits:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  sha: "main"
  author: "jokicdanijel"
  page: 1
  perPage: 50
```

---

### Release & Tag Management

#### `get_latest_release`
**Beschreibung:** Ruft die neueste Release ab
**Verwendung:** Versions-Tracking, Deployment-Validierung

```bash
github-mcp-server/get_latest_release:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
```

**Rückgabewerte:**
- `tag_name`: z.B. "v1.0.0"
- `name`: Release-Name
- `draft`, `prerelease`: Status-Flags
- `created_at`, `published_at`: Datum
- `assets[]`: Anhänge/Binärdateien

---

#### `get_release_by_tag`
**Beschreibung:** Ruft Release zu spezifischem Tag ab

```bash
github-mcp-server/get_release_by_tag:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  tag: "opena7-v1.0.0-production"
```

---

#### `get_tag`
**Beschreibung:** Git-Tag Details abrufen

```bash
github-mcp-server/get_tag:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  tag: "opena7-v1.0.0-production"
```

---

#### `list_tags`
**Beschreibung:** Alle Tags eines Repos auflisten

```bash
github-mcp-server/list_tags:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  page: 1
  perPage: 50
```

---

### Issue & Pull Request Management

#### `issue_read`
**Beschreibung:** Issue-Details abrufen mit verschiedenen Methoden
**Methoden:**

```bash
# get: Basis-Info
github-mcp-server/issue_read:
  method: "get"
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  issue_number: 80

# get_comments: Kommentare abrufen
github-mcp-server/issue_read:
  method: "get_comments"
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  issue_number: 80
  perPage: 100

# get_labels: Labels abrufen
github-mcp-server/issue_read:
  method: "get_labels"
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  issue_number: 80

# get_sub_issues: Sub-Issues abrufen
github-mcp-server/issue_read:
  method: "get_sub_issues"
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  issue_number: 80
```

---

#### `list_issues`
**Beschreibung:** Alle Issues mit Filterung

```bash
github-mcp-server/list_issues:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  state: "OPEN"
  labels: ["bug", "ci-cd"]
  orderBy: "CREATED_AT"
  direction: "DESC"
  perPage: 50
```

---

#### `pull_request_read`
**Beschreibung:** Pull Request Details mit Methoden

```bash
# get: PR-Info
github-mcp-server/pull_request_read:
  method: "get"
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  pullNumber: 45

# get_diff: PR-Diff
github-mcp-server/pull_request_read:
  method: "get_diff"
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  pullNumber: 45

# get_files: Geänderte Dateien
github-mcp-server/pull_request_read:
  method: "get_files"
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  pullNumber: 45
  perPage: 100

# get_reviews: Reviews abrufen
github-mcp-server/pull_request_read:
  method: "get_reviews"
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  pullNumber: 45

# get_review_comments: Review-Kommentare
github-mcp-server/pull_request_read:
  method: "get_review_comments"
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  pullNumber: 45
  perPage: 100

# get_comments: Kommentare
github-mcp-server/pull_request_read:
  method: "get_comments"
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  pullNumber: 45

# get_status: Commit-Status
github-mcp-server/pull_request_read:
  method: "get_status"
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  pullNumber: 45
```

---

#### `list_pull_requests`
**Beschreibung:** Alle PRs mit Filterung

```bash
github-mcp-server/list_pull_requests:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  state: "open"
  base: "main"
  sort: "created"
  direction: "desc"
  perPage: 50
```

---

### Security & Code Quality

#### `list_code_scanning_alerts`
**Beschreibung:** Code-Scanning Alerts (z.B. CodeQL)

```bash
github-mcp-server/list_code_scanning_alerts:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  state: "open"
  severity: "high"
  tool_name: "CodeQL"
```

---

#### `get_code_scanning_alert`
**Beschreibung:** Einzelnes Code-Scanning Alert

```bash
github-mcp-server/get_code_scanning_alert:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  alertNumber: 42
```

---

#### `list_secret_scanning_alerts`
**Beschreibung:** Secret-Scanning Alerts (exposed tokens, keys, etc.)

```bash
github-mcp-server/list_secret_scanning_alerts:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  state: "open"
  secret_type: "github_personal_access_token"
```

---

#### `get_secret_scanning_alert`
**Beschreibung:** Einzelnes Secret Alert

```bash
github-mcp-server/get_secret_scanning_alert:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  alertNumber: 15
```

---

### Repository & Branch Management

#### `get_file_contents`
**Beschreibung:** Datei- oder Verzeichnis-Inhalte abrufen

```bash
# Datei abrufen
github-mcp-server/get_file_contents:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  path: "agent_directories.json"
  ref: "main"

# Verzeichnis auflisten
github-mcp-server/get_file_contents:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  path: ".github/workflows"
  ref: "main"
```

---

#### `list_branches`
**Beschreibung:** Branches auflisten

```bash
github-mcp-server/list_branches:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  page: 1
  perPage: 50
```

---

#### `list_releases`
**Beschreibung:** Alle Releases auflisten

```bash
github-mcp-server/list_releases:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  page: 1
  perPage: 30
```

---

### Search & Discovery

#### `search_code`
**Beschreibung:** Quellcode durchsuchen (GitHub-Syntax)

```bash
# Funktion finden
github-mcp-server/search_code:
  query: "function setup_tracing language:python repo:jokicdanijel/Gesamtprojekt-start"

# Imports finden
github-mcp-server/search_code:
  query: "from opentelemetry import trace language:python"

# Config-Pattern
github-mcp-server/search_code:
  query: "PORT.*12350 language:python"
```

**Syntax-Beispiele:**
```
- language:python
- language:javascript
- path:*.yml
- repo:owner/name
- NOT is:archived
- content:"specific string"
```

---

#### `search_issues`
**Beschreibung:** Issues durchsuchen

```bash
github-mcp-server/search_issues:
  query: "label:bug is:open repo:jokicdanijel/Gesamtprojekt-start"
  sort: "created"
  direction: "desc"
```

---

#### `search_pull_requests`
**Beschreibung:** PRs durchsuchen

```bash
github-mcp-server/search_pull_requests:
  query: "is:merged author:jokicdanijel repo:jokicdanijel/Gesamtprojekt-start"
  sort: "updated"
```

---

#### `search_repositories`
**Beschreibung:** Repositories suchen

```bash
github-mcp-server/search_repositories:
  query: "language:python stars:>100 topic:agent"
  sort: "stars"
  direction: "desc"
  minimal_output: true
```

---

#### `search_users`
**Beschreibung:** GitHub-Benutzer suchen

```bash
github-mcp-server/search_users:
  query: "location:Germany followers:>50"
  sort: "followers"
```

---

### Label & Metadata

#### `get_label`
**Beschreibung:** Label-Details abrufen

```bash
github-mcp-server/get_label:
  owner: "jokicdanijel"
  repo: "Gesamtprojekt-start"
  name: "ci-cd"
```

---

#### `list_issue_types`
**Beschreibung:** Verfügbare Issue-Typen der Organisation

```bash
github-mcp-server/list_issue_types:
  owner: "jokicdanijel"
```

---

## 🎭 Playwright Browser Automation Tools

### Navigation & Page Management

#### `browser_navigate`
**Beschreibung:** Zu URL navigieren

```bash
playwright/browser_navigate:
  url: "https://www.hyperdashboard-one.de"
```

---

#### `browser_navigate_back`
**Beschreibung:** Zurück-Navigation

```bash
playwright/browser_navigate_back
```

---

### Snapshots & Screenshots

#### `browser_snapshot`
**Beschreibung:** Accessibility Snapshot der Seite (besser als Screenshot)

```bash
playwright/browser_snapshot
# Rückgabe: Strukturierte DOM-Beschreibung mit Accessibility-Info
```

---

#### `browser_take_screenshot`
**Beschreibung:** Screenshot aufnehmen

```bash
playwright/browser_take_screenshot:
  type: "png"
  fullPage: true
  filename: "dashboard.png"
```

---

### Element Interaction

#### `browser_click`
**Beschreibung:** Element anklicken

```bash
playwright/browser_click:
  element: "Login Button"
  ref: "#login-btn"
  doubleClick: false
  button: "left"
```

---

#### `browser_type`
**Beschreibung:** Text in Element eingeben

```bash
playwright/browser_type:
  element: "Email Input"
  ref: "input[type='email']"
  text: "user@example.com"
  submit: false
```

---

#### `browser_fill_form`
**Beschreibung:** Mehrere Formular-Felder ausfüllen

```bash
playwright/browser_fill_form:
  fields:
    - name: "Username"
      type: "textbox"
      ref: "#username"
      value: "testuser"
    - name: "Password"
      type: "textbox"
      ref: "#password"
      value: "secure123"
    - name: "Remember Me"
      type: "checkbox"
      ref: "#remember"
      value: "true"
```

---

#### `browser_select_option`
**Beschreibung:** Dropdown-Option wählen

```bash
playwright/browser_select_option:
  element: "Agent Selector"
  ref: "select#agents"
  values: ["opena5", "opena7"]
```

---

#### `browser_hover`
**Beschreibung:** Über Element hovern (ohne Klick)

```bash
playwright/browser_hover:
  element: "Menu Item"
  ref: "#menu-agents"
```

---

#### `browser_drag`
**Beschreibung:** Drag & Drop zwischen Elementen

```bash
playwright/browser_drag:
  startElement: "Task Item"
  startRef: "#task-1"
  endElement: "Completed List"
  endRef: "#completed-list"
```

---

### Form & Input Management

#### `browser_press_key`
**Beschreibung:** Taste drücken

```bash
playwright/browser_press_key:
  key: "Enter"

# Weitere Keys: ArrowUp, ArrowDown, Tab, Escape, etc.
```

---

#### `browser_file_upload`
**Beschreibung:** Dateien hochladen

```bash
playwright/browser_file_upload:
  paths:
    - "/tmp/requirements.txt"
    - "/tmp/Dockerfile"
```

---

### Page State & Information

#### `browser_console_messages`
**Beschreibung:** Alle Console-Meldungen abrufen

```bash
playwright/browser_console_messages
# Rückgabe: Array mit {type, message} (log, warn, error, info)
```

---

#### `browser_network_requests`
**Beschreibung:** Alle Network-Requests seit Page-Load

```bash
playwright/browser_network_requests
# Rückgabe: Array mit {method, url, status, responseTime}
```

---

### Dialog & Tab Management

#### `browser_handle_dialog`
**Beschreibung:** Dialog (Alert, Confirm, Prompt) handhaben

```bash
playwright/browser_handle_dialog:
  accept: true
  promptText: "optional text for prompt dialogs"
```

---

#### `browser_tabs`
**Beschreibung:** Tabs verwalten

```bash
# List tabs
playwright/browser_tabs:
  action: "list"

# New tab
playwright/browser_tabs:
  action: "new"

# Close tab
playwright/browser_tabs:
  action: "close"
  index: 1

# Select tab
playwright/browser_tabs:
  action: "select"
  index: 0
```

---

### Advanced JavaScript Execution

#### `browser_evaluate`
**Beschreibung:** JavaScript im Browser ausführen

```bash
playwright/browser_evaluate:
  function: "() => { return document.title; }"

# Mit Element-Context
playwright/browser_evaluate:
  function: "(element) => { return element.innerText; }"
  element: "Agent Name"
  ref: "#agent-title"
```

---

### Page Waiting

#### `browser_wait_for`
**Beschreibung:** Auf Text warten oder Zeit verstreichen

```bash
# Auf Text warten
playwright/browser_wait_for:
  text: "Dashboard loaded"

# Auf Text-Verschwinden warten
playwright/browser_wait_for:
  textGone: "Loading..."

# Zeit warten
playwright/browser_wait_for:
  time: 5
```

---

### Browser Configuration

#### `browser_resize`
**Beschreibung:** Browser-Fenster resizen

```bash
playwright/browser_resize:
  width: 1920
  height: 1080
```

---

#### `browser_close`
**Beschreibung:** Browser/Tab schließen

```bash
playwright/browser_close
```

---

#### `browser_install`
**Beschreibung:** Browser aus Konfiguration installieren

```bash
playwright/browser_install
# Nützlich bei Browser-Fehlern
```

---

## 🔍 Web Search & Analysis

#### `web_search`
**Beschreibung:** AI-gesteuerte Web-Suche mit Citations

```bash
github-mcp-server/web_search:
  query: "Latest features in React 19"

# Weitere Beispiele:
# - "Current status of James Webb Space Telescope"
# - "Recent developments in quantum computing"
# - "How to setup OpenTelemetry tracing in Python"
```

**Rückgabewerte:**
- `response`: AI-generierte Antwort mit Inline-Citations
- `sources[]`: Array von Quellen mit URLs

---

## 📊 Best Practices & Patterns

### Pattern 1: Workflow-Fehler Debugging

```bash
# 1. Letzte Läufe abrufen
get_workflow_runs(workflow="opena5.yml")

# 2. Fehlgeschlagene Läufe filtern
→ Status: "completed", Conclusion: "failure"

# 3. Job-Logs abrufen
get_job_logs(run_id=<failed_run_id>, failed_only=true, tail_lines=1000)

# 4. Root Cause analysieren
→ Prüfe auf: Secrets, Dependencies, Syntax-Fehler, Port-Konflikte
```

---

### Pattern 2: Security Audit

```bash
# 1. Secret-Scanning
list_secret_scanning_alerts(state="open")

# 2. Code-Scanning
list_code_scanning_alerts(severity="high")

# 3. Datei-Inhalte prüfen
get_file_contents(path=".env*", ref="main")

# 4. Git-Historie durchsuchen
search_code(query="ghp_|sk-|AKIA language:python")
```

---

### Pattern 3: Automated Testing Workflow

```bash
# 1. PR erstellen/auflisten
search_pull_requests(state="open", sort="updated")

# 2. Änderungen abrufen
pull_request_read(method="get_files", pullNumber=<nr>)

# 3. Tests im Browser durchführen
browser_navigate("https://example.com/test")
browser_snapshot()
→ Prüfe auf Errors in Console
```

---

### Pattern 4: Version Control & Release

```bash
# 1. Commits durchsuchen
get_commit(sha="<hash>", include_diff=true)

# 2. Release erstellen
get_latest_release()

# 3. Tags verwalten
list_tags(page=1, perPage=50)

# 4. Change-Log generieren
list_commits(sha="<tag1>..<tag2>")
```

---

## ⚠️ Häufige Fehler & Lösungen

### "Tool nicht gefunden"
**Problem:** Tool-Name falsch geschrieben
**Lösung:** Nutze Namespace: `github-mcp-server/get_commit`, nicht `get_commit`

### "Authentifizierung fehlgeschlagen"
**Problem:** Keine GitHub-Credentials
**Lösung:** Stelle sicher, dass GitHub CLI konfiguriert ist: `gh auth login`

### "Rate Limit exceeded"
**Problem:** Zu viele API-Requests
**Lösung:** Nutze Pagination, warte 1 Stunde, oder upgrade GitHub Plan

### Browser-Tool schlägt fehl
**Problem:** Playwright nicht installiert
**Lösung:** Führe `playwright/browser_install` aus

---

## 📚 Weitere Ressourcen

- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Playwright Documentation](https://playwright.dev)
- [MCP Specification](https://modelcontextprotocol.io)

---

**Ende der MCP Tools Dokumentation**
