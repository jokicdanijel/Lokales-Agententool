# Prompts & Agenten – Copilot-Governance

**Projekt:** LocalAgent-Pro / Hyper Dashboard  
**Owner:** Danijel Jokic  
**Letzte Aktualisierung:** 19. November 2025  
**Status:** ✅ Produktiv

---

## 📋 Einleitung

Diese Seite definiert **alle Regeln und Standards** für die Arbeit mit:

- **GitHub Copilot** (Code-Assistent in der IDE)
- **LocalAgent-Pro** (AI-Agent-Server für Automationen)
- **Agenten-Prompts** (strukturierte AI-Workflows)

**Zweck:** Klare Governance, Sicherheit und Reproduzierbarkeit bei allen AI-gestützten Operationen.

---

## 🎯 Grundprinzipien

### 1. Copilot ≠ Autopilot

- ✅ **Copilot:** Code-Helfer für **explizite, eng eingegrenzte Aufgaben**
  - Beispiele: Funktion refaktorisieren, Docstring ergänzen, Test schreiben
- ❌ **NICHT:** „Mach mal alles schöner", „Geh über das ganze Repo drüber"

### 2. LocalAgent-Pro ist der Orchestrator

- **Business-Logik, Automationen, Workflows** → LocalAgent-Pro (OpenWebUI)
- **Code-Completion, kleine Refactorings** → GitHub Copilot
- **Klare Trennung:** Copilot = Helfer, LocalAgent-Pro = Orchestrator

### 3. Sicherheit & Reproduzierbarkeit first

- ✅ Kritische Dateien nur mit **klaren Prompts + Review**
- ✅ Alle Prompts sind **versionierbar** (im Wissensspeicher)
- ✅ Keine stillen Änderungen an Produktions-Code

---

## 🤖 GitHub Copilot – Regeln & Standards

### Wofür Copilot genutzt werden darf

#### ✅ **ERLAUBT:**

- **Erweiterung/Refactoring** innerhalb einer vorhandenen Datei
- **Ergänzen von:**
  - Typannotationen (`def foo(x: int) -> str:`)
  - Docstrings (PEP 257)
  - Kommentaren
  - Kleine Hilfsfunktionen (< 20 Zeilen)
- **Vorschläge für Tests:**
  - Unit-Tests (pytest)
  - Kleine Integrationstests
- **Boilerplate:**
  - FastAPI-Endpunkte
  - Dataclassen (`@dataclass`)
  - Enums

#### ❌ **NICHT ERLAUBT:**

- **Änderungen an kritischen Dateien:**
  - `config/config.yaml` (Produktiv-Config)
  - `src/agent_server.py` (Core-Server)
  - `src/openwebui_agent_server.py` (Production-Server)
  - Sicherheitsmodule (Shell-Execution, Auth-Logik)
- **Erstellen/Löschen von:**
  - Backup-/Config-Kopien (`config_backup_*.yaml`)
  - System-/Binärdateien (`.pyc`, `__pycache__`)
  - Komplexen Migrationsskripten ohne Review
- **Globale Operationen:**
  - „Geh über das ganze Projekt und mach es besser"
  - Multi-File-Refactorings ohne Plan

---

## 📜 Standard-Prompt für Copilot (Code-Arbeiten)

**Zweck:** Copilot verhält sich wie ein **kontrollierter Junior-Dev**, nicht wie ein hyperaktiver Skript-Kid.

### Verbindlicher Copilot-Prompt

```markdown
**Rolle:**
Du arbeitest im Repository „LocalAgent-Pro" / „Hyper Dashboard" als vorsichtiger, regelkonformer Coding-Assistent.

**Ziele:**
1. Nur lokal begrenzte Änderungen vornehmen.
2. Keine kritischen Dateien antasten (Config, Server, Infra).
3. Code lesbarer, stabiler und wartbarer machen.

**Harte No-Gos:**
- KEINE Änderungen an `config.yaml`, `agent_server.py` oder anderen produktiven Konfigurationsdateien.
- KEINE Binärdateien, Downloads, externen Artefakte.
- KEINE neuen Backups oder Kopien von Configs ins Repo schreiben.
- KEINE `__pycache__/`, `*.pyc`, `*.log` Dateien committen.

**Arbeitsweise:**
1. Konzentriere dich ausschließlich auf den aktuell geöffneten Codebereich / die selektierte Datei.
2. Mache kleine, nachvollziehbare Änderungen.
3. Schreibe klaren, kommentierten Code (PEP 8).
4. Erzeuge KEINEN Code, der Shell-Befehle ausführt oder systemkritische Operationen ohne explizite Anweisung vornimmt.

**Output:**
- Klare, testbare Funktionen.
- Keine Magic-Einzeiler.
- Defensive Programmierung (Input-Validierung, Error-Handling).
```

**Status:** ✅ **VERBINDLICH** für alle Copilot-Interaktionen in diesem Repo.

---

## 🔒 No-Go-Liste für Copilot

### Kritische Dateien (NICHT ANFASSEN)

```
LocalAgent-Pro/config/config.yaml
LocalAgent-Pro/config/config_safe.yaml
LocalAgent-Pro/src/agent_server.py
LocalAgent-Pro/src/openwebui_agent_server.py
LocalAgent-Pro/src/ollama_integration.py (nur mit Review)
.git/*
.env (falls vorhanden)
```

### Verbotene Patterns

```
**/__pycache__/**
*.pyc
*.pyo
*.log
*_backup_*.yaml
*.bak
*.tmp
```

### Verbotene Operationen

- ❌ `git commit` ohne Review
- ❌ `rm -rf` oder destruktive Shell-Commands
- ❌ Secrets/API-Keys generieren oder committen
- ❌ Multi-File-Refactorings ohne expliziten Plan

---

## ✅ Review-Pflicht mit Git

**Jede Copilot-Änderung durchläuft:**

### 1. Pre-Commit-Check

```bash
# Diff anzeigen
git diff
# ODER staged changes
git diff --cached

# Checkliste:
# ✅ Keine __pycache__/, *.pyc, .log, Binärfiles
# ✅ Keine Änderungen an config.yaml, agent_server.py
# ✅ Keine random generierten Dateien (config_backup_*.yaml)
# ✅ Commit-Message ist präzise (Conventional Commits)
```

### 2. Commit nur wenn ALLE Checks grün

```bash
git add <files>
git commit -m "feat(scope): Beschreibung"
```

### 3. Push-Strategie

```bash
# Lokal testen
pytest tests/

# Dann push
git push origin main
```

---

## 🤖 LocalAgent-Pro – Agenten & Prompts

### Zielbild

Agenten sind:

- ✅ **Stabil** – Vorhersagbares Verhalten
- ✅ **Dokumentiert** – Klar definierte Rolle & Ein-/Ausgabe
- ✅ **Standardisiert** – Einheitliche Prompt-Struktur
- ✅ **Sicher** – Boundaries (No-Gos, Sicherheitsregeln)

### Modell-Standard

**Default-Modell:**

```yaml
model: gpt-5-nano
```

**Regel:**

- ✅ `gpt-5-nano` für **alle Normal-Tasks**
- ⚠️ Ausnahmen nur **explizit dokumentiert** (z.B. für spezielle Aufgaben)
- 📝 Alle Konfig-Beispiele, Prompts und Agent-Definitionen gehen von `gpt-5-nano` aus

**Im Wissensspeicher festgehalten:**

> „Standardmodell für dieses Projekt ist immer `gpt-5-nano`, außer explizit anders dokumentiert."

---

## 📂 Agenten-Kategorien

### 1. System-Agenten

**Zweck:** Koordinieren, Validieren, Regeln durchsetzen

**Beispiele:**

- **LocalAgent-Pro Orchestrator**
  - Rolle: Master-Koordinator
  - Tools: Alle (File, Shell, Web, Git)
  - Boundaries: Strikte Sandbox, Domain-Whitelist

### 2. Tool-Agenten

**Zweck:** Spezifische Tool-Execution

**Beispiele:**

- **Shell-Executor** (nur wenn `shell_execution.enabled: true`)
- **Datei-Handler** (read, write, list)
- **Web-Fetcher** (HTTP-Requests, Scraping)
- **Git-Helper** (Status, Diff, Log)

### 3. Business-Agenten

**Zweck:** Fachliche Aufgaben

**Beispiele:**

- **Prompts-Designer** – Erstellt/optimiert AI-Prompts
- **Config-Generator** – Erzeugt YAML/JSON-Configs
- **Doku-Writer** – Schreibt Markdown-Dokumentation
- **Test-Generator** – Erzeugt pytest-Tests

---

## 📋 Standard-Struktur für Agenten-Prompts

**Für jeden Agenten im Wissensspeicher:**

### Template

```markdown
## Agent: [NAME]

### 1. Rolle & Kontext
- **Was bist du?** [Beschreibung]
- **Projekt:** LocalAgent-Pro / Hyper Dashboard
- **Modell:** gpt-5-nano (default)

### 2. Aufgabenbeschreibung
- **Ziel:** [Was soll der Agent tun?]
- **Input:** [Erwartetes Input-Format]
- **Output:** [Erwartetes Output-Format]

### 3. Einschränkungen & Regeln
- **Erlaubte Dateien:** [Liste]
- **Verbotene Dateien:** [Liste]
- **Erlaubte Tools:** [Liste: file, shell, web, git]
- **Sicherheitsregeln:** [Sandbox, Whitelist, etc.]

### 4. Output-Format
- **Typ:** JSON / YAML / Markdown / Code-Block
- **Validierung:** [Muss output ausführbar/parsbar sein?]

### 5. Qualitätskriterien
- ✅ Kein unsauberer Code
- ✅ Kein „Guessing" bei Unsicherheit → lieber nachfragen
- ✅ Keine stillschweigende Annahmen bei riskanten Operationen
- ✅ Defensive Programmierung (Input-Validierung, Error-Handling)

### 6. Beispiele
[Beispiel-Input → Beispiel-Output]
```

---

## 🔄 Copilot vs. LocalAgent-Pro – Vergleichstabelle

| Aspekt | **GitHub Copilot** | **LocalAgent-Pro (OpenWebUI)** |
|--------|-------------------|-------------------------------|
| **Scope** | Code-Vorschläge in IDE | End-to-End-Flows (Dateien, Shell, Web, Doku) |
| **Einsatz** | Lokale Änderungen in einzelnen Dateien | Automatisierung, Generierung, Analyse |
| **Governance** | Strikte No-Gos (Config, Server, Infra) | Master-Prompts + Wissensspeicher-Regeln |
| **Kontrolle** | `git diff`-Pflicht | Logging, definierte Output-Formate, Tests |
| **Modell** | GitHub-seitig (proprietär) | `gpt-5-nano` (lokal, Ollama) |
| **Tools** | Keine | File, Shell (optional), Web, Git |
| **Sandbox** | N/A | ✅ Aktiv (`/home/danijel-jd/localagent_sandbox`) |
| **Review** | Manuell (git diff) | Automatisch (Logging, Metrics) |

---

## 📊 Modell-Policy

### Default-Modell: `gpt-5-nano`

**Regel:**

- ✅ **Standard für alle Agenten:** `gpt-5-nano`
- ✅ **Nur dokumentierte Ausnahmen erlaubt**
- ✅ **Alle Prompts/Configs gehen von `gpt-5-nano` aus**

**Ausnahmen (dokumentiert):**

| Aufgabe | Modell | Grund |
|---------|--------|-------|
| *Noch keine definiert* | - | - |

**Zukünftige Ausnahmen:**

Wenn ein anderes Modell (z.B. `llama3.1:8b-instruct-q4_K_M`) für spezielle Tasks genutzt werden soll:

1. **Dokumentiere** in dieser Tabelle
2. **Begründe** warum `gpt-5-nano` nicht ausreicht
3. **Review** durch Owner (Dani)

---

## 🛠️ Praktische Workflows

### Workflow 1: Copilot für kleine Refactorings

```bash
# 1. Datei in IDE öffnen
code LocalAgent-Pro/src/my_module.py

# 2. Copilot-Prompt (in Kommentar):
# "Refactor this function to use type hints and add docstring"

# 3. Änderung reviewen
git diff

# 4. Wenn OK:
git add LocalAgent-Pro/src/my_module.py
git commit -m "refactor(my_module): Add type hints and docstring"
```

### Workflow 2: LocalAgent-Pro für Automation

```bash
# 1. OpenWebUI öffnen (http://localhost:3000)

# 2. Agent-Prompt senden:
# "Erstelle pytest-Tests für alle Funktionen in src/file_tools.py"

# 3. Output reviewen (in Sandbox)

# 4. Wenn OK, manuell übernehmen:
cp ~/localagent_sandbox/tests/test_file_tools.py LocalAgent-Pro/tests/unit/

# 5. Tests ausführen
pytest LocalAgent-Pro/tests/unit/test_file_tools.py
```

---

## 📚 Wissensspeicher-Integration

**Diese Seite ist Teil des Wissensspeichers:**

- **Pfad:** `docs/PROMPTS_AGENTEN_COPILOT.md`
- **Verknüpfungen:**
  - `docs/COMPLETE_GUIDE.md` → Vollständige Projekt-Doku
  - `.github/copilot-commit-instructions.md` → Commit-Guidelines
  - `config/config.yaml` → Agent-Konfiguration

**Regelmäßige Reviews:**

- ✅ Nach jedem Major-Release (v1.x, v2.x)
- ✅ Bei neuen Agenten-Typen
- ✅ Bei Security-Incidents

---

## ✅ Checkliste für neue Agenten

Wenn du einen neuen Agenten erstellst:

- [ ] Rolle & Kontext definiert
- [ ] Aufgabenbeschreibung klar
- [ ] Ein-/Ausgabe-Format spezifiziert
- [ ] Einschränkungen & No-Gos dokumentiert
- [ ] Modell definiert (`gpt-5-nano` default)
- [ ] Qualitätskriterien festgelegt
- [ ] Beispiele hinzugefügt
- [ ] In Wissensspeicher eingetragen

---

## 🚨 Notfall-Prozedur bei Copilot-Schäden

**Wenn Copilot kritische Dateien geändert hat:**

### 1. Sofort-Stop

```bash
# Alle Änderungen verwerfen
git checkout -- .

# ODER nur spezifische Datei
git checkout -- LocalAgent-Pro/config/config.yaml
```

### 2. Damage-Assessment

```bash
# Was wurde geändert?
git diff HEAD

# Welche Dateien betroffen?
git status --short
```

### 3. Selective Restore

```bash
# Nur sichere Änderungen behalten
git add <safe_files>
git checkout -- <critical_files>
```

### 4. Post-Mortem

- Dokumentiere: Was lief schief?
- Update: Copilot-Prompt/No-Go-Liste
- Review: Sind weitere Schutzmaßnahmen nötig?

---

## 📝 Änderungshistorie

| Datum | Änderung | Author |
|-------|----------|--------|
| 19.11.2025 | Initial-Version erstellt | Dani |

---

**Status:** ✅ Produktiv  
**Owner:** Danijel Jokic  
**Letzte Review:** 19. November 2025
