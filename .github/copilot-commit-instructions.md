# GitHub Copilot — Commit Message Guidelines

**Anweisungen für AI-generierte Commits** — damit Copilot präzise, projektspezifische Commit-Messages erstellt.

---

## 📋 Repository-Kontext

**Projekt:** LocalAgent-Pro — Flask-basierter AI-Agent-Server mit OpenWebUI-Integration  
**Owner:** jokicdanijel  
**Repository:** Lokales-Agententool  
**Branch:** main  
**Sprache:** Deutsch (für Commit-Messages)

---

## ✅ Commit-Message-Format (Conventional Commits)

### Standard-Format:

```
<typ>(<scope>): <kurze Beschreibung>

<ausführliche Beschreibung (optional)>

<footer (optional)>
```

### Typen (verwende diese präzise):

- **feat:** Neue Funktion/Feature
- **fix:** Bugfix oder Problem-Lösung
- **docs:** Nur Dokumentation geändert
- **style:** Code-Formatierung (keine Logik-Änderung)
- **refactor:** Code-Umstrukturierung (keine Features/Fixes)
- **perf:** Performance-Verbesserung
- **test:** Tests hinzugefügt/geändert
- **chore:** Build, Dependencies, Tools
- **ci:** CI/CD-Konfiguration
- **security:** Sicherheits-Fix

### Scopes (projektspezifisch):

- **config:** Konfigurationsdateien (`config.yaml`, `.gitignore`)
- **server:** Flask-Server (`openwebui_agent_server.py`)
- **tools:** Tool-Implementierungen
- **sandbox:** Sandbox-Funktionalität
- **docs:** Dokumentation
- **venv:** Virtual Environment (nur für Cleanup)
- **deps:** Dependencies (`requirements.txt`)
- **logging:** Logging-System
- **security:** Sicherheits-Features (Loop-Protection, Whitelist)
- **git:** Git-Konfiguration

---

## 🎯 Beispiele für korrekte Commit-Messages

### Beispiel 1: venv entfernen (aktueller Fall)

```
fix(venv): Entferne Virtual Environment aus Repository

- Alle venv-Dateien aus Git-Tracking entfernt (git rm -r --cached venv/)
- venv/ war bereits in .gitignore, wurde aber vor dessen Erstellung committed
- Reduziert Repository-Größe um ~3000 Dateien
- Lokale venv-Dateien bleiben unberührt und funktionsfähig

Relates-to: Repository-Cleanup
```

### Beispiel 2: Loop-Problem beheben

```
fix(security): Implementiere Loop-Protection für Shell-Commands

- Shell-Execution standardmäßig deaktiviert (config.yaml)
- Loop-Detection mit max_retries: 1 hinzugefügt
- Strikte Command-Validierung implementiert
- Safe-Mode-Config bereitgestellt (config_safe.yaml)

Fixes: #Loop-Problem (siehe LOOP_PROBLEM_ANALYSIS.md)
```

### Beispiel 3: Neue Dokumentation

```
docs(readme): Füge Copilot-Instructions und Quick-Start hinzu

- .github/copilot-instructions.md für AI-Agent-Kontext
- QUICK_START.md für schnellen Projekteinstieg
- Aktualisierte README.md mit Projektübersicht

Improves: Developer-Onboarding
```

### Beispiel 4: Config-Änderung

```
feat(config): Aktiviere Safe-Mode mit erweiterten Sicherheitsfeatures

- Loop-Protection aktiviert
- Shell-Execution standardmäßig deaktiviert
- Rate-Limiting auf 30 req/min gesetzt
- Domain-Whitelist auf vertrauenswürdige Sites beschränkt

Breaking-Change: shell_execution.enabled jetzt default: false
```

### Beispiel 5: Workspace-Optimierung

```
chore(vscode): Optimiere Workspace-Settings für Performance

- venv/, node_modules aus Suche/Indexierung ausgeschlossen
- GitLens Token-Verbrauch reduziert (CodeLens deaktiviert)
- File-Watchers für große Verzeichnisse deaktiviert
- Python Analysis auf User-Code beschränkt

Fixes: Memory-Leaks und Token-Limit-Errors
```

---

## 🚫 Anti-Patterns (NICHT verwenden)

### ❌ Schlechte Commit-Messages:

```
Updated files
Fixed stuff
WIP
asdf
Merge
Changes
.
```

### ❌ Zu generisch:

```
fix: Fixed bug
feat: Added feature
docs: Updated docs
```

### ❌ Englisch/Deutsch gemischt:

```
fix(config): Update configuration für Sandbox
feat: Neue feature added
```

---

## 📝 Spezielle Szenarien

### Szenario 1: Große Datei-Mengen (z.B. venv-Cleanup)

**Problem:** 1713 Dateien geändert (+63470/-257)

**Richtige Message:**
```
fix(venv): Entferne Virtual Environment aus Repository

- 1713 venv-Dateien aus Git-Tracking entfernt (git rm -r --cached)
- venv/ bereits in .gitignore, wurde aber vor dessen Erstellung committed
- Reduziert Repository-Größe signifikant (~3000 Python-Package-Dateien)
- Lokale Entwicklungsumgebung bleibt unberührt

Details:
- Betroffene Packages: flask, werkzeug, yaml, requests, urllib3, pip, etc.
- Command: git rm -r --cached LocalAgent-Pro/venv/
- .gitignore Entry: venv/ (bereits vorhanden)

Relates-to: Repository-Cleanup, Best-Practices
```

### Szenario 2: Breaking Changes

**Präfix:** `BREAKING CHANGE:` im Footer

```
feat(config): Aktiviere Sandbox-Modus standardmäßig

- sandbox: true als Default gesetzt
- Alle Datei-Operationen jetzt in ~/localagent_sandbox/
- Shell-Execution deaktiviert für Sicherheit

BREAKING CHANGE: Dateien werden nicht mehr im Projekt-Root erstellt.
Migrationsschritte siehe MIGRATION.md
```

### Szenario 3: Multi-File-Änderungen mit Zusammenhang

```
refactor(server): Modularisiere Tool-System

Geänderte Dateien:
- src/openwebui_agent_server.py: Tool-Registry extrahiert
- src/tools/__init__.py: Neues Tool-Registry-Modul
- src/tools/file_tools.py: Datei-Operationen ausgelagert
- src/tools/shell_tools.py: Shell-Commands modularisiert
- config/config.yaml: Tool-Konfiguration hinzugefügt

Vorteile:
- Bessere Wartbarkeit
- Einfacheres Testing
- Klare Verantwortlichkeiten

No breaking changes
```

---

## 🔍 Wichtige Regeln für AI-Commits

### 1. **Immer Deutsch schreiben** (außer technische Begriffe)
   - ✅ "Entferne Virtual Environment"
   - ❌ "Remove Virtual Environment"

### 2. **Scope angeben** wenn möglich
   - ✅ `fix(venv): ...`
   - ❌ `fix: ...`

### 3. **Kontext erklären** (Warum, nicht nur Was)
   - ✅ "venv/ war bereits in .gitignore, wurde aber vor dessen Erstellung committed"
   - ❌ "Deleted venv files"

### 4. **Auswirkungen dokumentieren**
   - ✅ "Reduziert Repository-Größe signifikant"
   - ✅ "Lokale venv-Dateien bleiben unberührt"

### 5. **Bezüge herstellen**
   - ✅ "Fixes: #Loop-Problem"
   - ✅ "Relates-to: LOOP_PROBLEM_ANALYSIS.md"
   - ✅ "Breaking-Change: ..."

### 6. **Listen für Klarheit**
   ```
   - Punkt 1
   - Punkt 2
   - Punkt 3
   ```

### 7. **Technische Details im Footer**
   ```
   Details:
   - Command: git rm -r --cached venv/
   - Files: 1713 geändert
   - Size: +63470/-257 Zeilen
   ```

---

## 🎯 Template für typische Commit-Typen

### Template: Cleanup/Removal

```
fix(<scope>): Entferne <was> aus Repository

- <Hauptaktion beschreiben>
- <Grund/Kontext erklären>
- <Auswirkungen nennen>
- <Wichtige Details>

Relates-to: <Bezug>
```

### Template: Feature

```
feat(<scope>): Füge <feature> hinzu

- <Was wurde implementiert>
- <Wie funktioniert es>
- <Warum ist es nützlich>

Beispiel-Nutzung:
<Code-Beispiel oder Befehl>
```

### Template: Bugfix

```
fix(<scope>): Behebe <problem>

Problem:
- <Beschreibung des Bugs>

Lösung:
- <Implementierte Lösung>
- <Warum diese Lösung>

Fixes: <Issue/Bezug>
```

### Template: Dokumentation

```
docs(<scope>): <was dokumentiert>

- <Neue/geänderte Dokumentation>
- <Zielgruppe>
- <Wichtige Inhalte>

Improves: <was verbessert wird>
```

---

## 🚀 Auto-Compose Empfehlungen

### Für große Changesets (>100 Dateien):

1. **Gruppiere logisch zusammengehörende Änderungen**
2. **Erstelle mehrere Commits** wenn möglich
3. **Erkläre im Detail** was passiert ist
4. **Nenne Kontext** (z.B. "vor .gitignore committed")

### Für venv-Cleanup speziell:

```
fix(venv): Entferne Virtual Environment aus Git-Tracking

Hintergrund:
- Virtual Environment wurde versehentlich committed (3000+ Dateien)
- .gitignore enthält bereits venv/ Eintrag
- Dateien wurden vor .gitignore-Erstellung hinzugefügt

Durchgeführte Aktion:
- Command: git rm -r --cached LocalAgent-Pro/venv/
- Alle Python-Package-Dateien aus Git-Index entfernt
- Lokale venv-Dateien bleiben erhalten (--cached Flag)

Auswirkungen:
- Repository-Größe drastisch reduziert
- Sauberer Git-History
- Keine Auswirkungen auf lokale Entwicklung
- Zukünftige pip-Installationen werden nicht getrackt

Betroffene Packages:
- flask, werkzeug, yaml, requests, urllib3
- pip, setuptools, wheel
- Alle Dependencies aus requirements.txt

Nächste Schritte:
- Git push zum Remote
- Team-Mitglieder sollten git pull ausführen
- Bei Merge-Konflikten: lokales venv/ löschen und neu erstellen

Relates-to: Repository-Best-Practices, .gitignore-Konfiguration
```

---

## ✅ Checkliste für AI-Commits

Bevor "Finish & Commit" klicken:

- [ ] **Typ korrekt?** (fix/feat/docs/chore/etc.)
- [ ] **Scope angegeben?** (venv/config/server/etc.)
- [ ] **Auf Deutsch?** (außer Code-Begriffe)
- [ ] **Kontext erklärt?** (Warum diese Änderung?)
- [ ] **Auswirkungen genannt?** (Was ändert sich?)
- [ ] **Bezüge gesetzt?** (Fixes/Relates-to)
- [ ] **Keine Rechtschreibfehler?**
- [ ] **Listen korrekt formatiert?**

---

**Für Copilot:** Nutze diese Guidelines, um präzise, hilfreiche Commit-Messages zu generieren, die den Projektkontext berücksichtigen und Reviewern helfen, Änderungen schnell zu verstehen.

**Letzte Aktualisierung:** 19.11.2025
