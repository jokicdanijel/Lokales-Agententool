[PDI-ACTIVE: TRUE | MANIFEST | GITHUB-CHECK: PASS]

# PDI-Manifest für ELION Hyper-Dashboard

## 1. Projekt-Metadaten

| Feld             | Wert                      |
| ---------------- | ------------------------- |
| **Projekt-Name** | ELION Hyper-Dashboard 2.0 |
| **Projekt-ID**   | elion-dashboard-2025      |
| **Version**      | 2.0.0                     |
| **PDI-Version**  | 1.0.0                     |
| **Erstellt**     | 2025-11-09                |
| **Author**       | Danijel (ELION Team)      |
| **Status**       | ACTIVE                    |

---

## 2. Pflicht-Validierungs-Module

Alle generierten Inhalte müssen diese Module durchlaufen **in dieser Reihenfolge**:

| #   | Modul          | Zweck                                             | Gatekeeper                     |
| --- | -------------- | ------------------------------------------------- | ------------------------------ |
| 1   | **LINGUISTIC** | Verständlichkeit, Klarheit                        | Native Speaker / Dokumentation |
| 2   | **TECHNICAL**  | Schnittstellen, Datenflüsse                       | Architect                      |
| 3   | **CORRECTION** | Normen, Lint, Standards                           | Code Reviewer                  |
| 4   | **ANALYTICS**  | Funktionsbäume, Abhängigkeiten                    | QA                             |
| 5   | **CONTROL**    | Gates, Rollbacks, Richtlinien                     | Project Manager                |
| 6   | **GITHUB**     | Copilot-Checks (Syntax, Logic, Runtime, Security) | CI/CD                          |

---

## 3. Validierungs-Gates (Pflicht)

Jede Stufe endet mit automatischer Kontrollprüfung (intern + GitHub-Simulation):

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT                                                       │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ [GATE-1] Syntaxprüfung (GITHUB)                             │
│ ├─ Keine ungültigen Zeichen                                │
│ ├─ Korrekte JSON/YAML (wenn relevant)                      │
│ ├─ Python: keine Syntax-Fehler                             │
│ └─ Bash: korrekte Bash-Syntax                              │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ [GATE-2] Linguistische Validierung                          │
│ ├─ Verständlichkeit                                        │
│ ├─ Konsistenz der Terminologie                             │
│ ├─ Vollständigkeit der Dokumentation                       │
│ └─ Zielgruppen-Angemessenheit                              │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ [GATE-3] Technische Validierung                             │
│ ├─ Korrekte Schnittstellen-Definition                      │
│ ├─ Datenflüsse nachverfolgbar                              │
│ ├─ Abhängigkeiten explizit                                 │
│ └─ Performance-Anforderungen erfüllt                       │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ [GATE-4] Logik-Prüfung (GITHUB)                             │
│ ├─ Keine offensichtlichen Fehler                           │
│ ├─ Edge-Cases berücksichtigt                               │
│ ├─ Error-Handling vorhanden                                │
│ └─ Test-Cases möglich                                      │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ [GATE-5] Sicherheitsprüfung (GITHUB)                        │
│ ├─ Keine hardcodierten Secrets                             │
│ ├─ Keine eval()/exec() Calls                               │
│ ├─ Authentifizierung/Autorisierung korrekt                 │
│ └─ Input-Validierung vorhanden                             │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ [GATE-6] Integrations-Prüfung                               │
│ ├─ Mit bestehenden APIs kompatibel                         │
│ ├─ Abhängigkeiten auflösbar                                │
│ ├─ Keine Konflikte mit anderen Modulen                     │
│ └─ Versionierung korrekt                                   │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ ✓ FREIGABE: [PDI-ACTIVE: TRUE | VALIDATED |                 │
│                GITHUB-CHECK: PASS]                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. PDI-Header (Pflicht für alle Artifacts)

Jede freigegeben Datei (Code, Docs, Config) beginnt mit:

```
[PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]
[MODULES: LINGUISTIC | TECHNICAL | CORRECTION | ANALYTICS | CONTROL | GITHUB]
[GATES: 1,2,3,4,5,6 ✓]
[VALIDATION-TIMESTAMP: 2025-11-09T12:34:56Z]
[AUTHOR: danijel | REVIEWED-BY: system]
```

### Beispiel (Python):

```python
"""
[PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]
[MODULES: TECHNICAL | CORRECTION | GITHUB]
[GATES: 1,3,5,6 ✓]

Beschreibung des Moduls...
"""
```

### Beispiel (Bash):

```bash
#!/usr/bin/env bash
# [PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]
# [MODULES: TECHNICAL | CORRECTION]
# [GATES: 1,5,6 ✓]
```

### Beispiel (Markdown):

```markdown
[PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]
[MODULES: LINGUISTIC | TECHNICAL]
[GATES: 2,3,4 ✓]

# Dokumentation

...
```

---

## 5. Kochrezept – Praktische Ausführung

### Phase 1: Vorbereitung

```bash
# 1. Input übernehmen
pdi = PDICore("project-name", "project-id")
pdi.process_input(input_text, author="user")

# 2. Manifest erstellen
echo $pdi.manifest → PDI_MANIFEST.json

# 3. Kapitelplan anlegen
pdi.create_chapter_plan(num_chapters=5)
```

### Phase 2: Kapitel erzeugen (pro Kapitel: 8 Stufen)

```
Für Kapitel N:

Stufe 1: Kommentierung (LINGUISTIC)
  → Code/Text mit Erklärungen versehen
  → Verständlichkeit + Formatierung prüfen

Stufe 2: Verbesserungsvorschläge (TECHNICAL)
  → Architektur + Schnittstellen-Design
  → Performance + Skalierbarkeit

Stufe 3: Validierung (CORRECTION)
  → Normen + Lint-Regeln
  → Code-Style + Konventionen

Stufe 4: Selbstprüfung (ANALYTICS)
  → Funktionsbäume + Abhängigkeiten
  → Metriken + Komplexität

Stufe 5: Kontrollprüfung (CONTROL)
  → Gates prüfen
  → Rollback-Punkte definieren

Stufe 6: GitHub-Simulation (GITHUB)
  → Syntax-Check
  → Logic-Check
  → Runtime-Check
  → Security-Check

Stufe 7: Freigabe-Check
  → Alle Checks erfolgreich?
  → JA: Header anhängen + Release
  → NEIN: Zu Gate 1 zurück (Feedback)

Stufe 8: Logging
  → Validation-Report speichern
  → Artifact in validated-store
```

### Phase 3: Finalisierung

```bash
# Alle Kapitel durch 8-Stufen-Prozess
for chapter in 1..N:
  pdi.validate_artifact(chapter_id, "doc", content)

# Validation-Report exportieren
pdi.get_validation_report() → PDI_VALIDATION_REPORT.json

# Projekt freigeben
[PDI-ACTIVE: TRUE | ALL GATES PASSED | READY FOR PRODUCTION]
```

---

## 6. Systemverankerung

### Regel 1: PDI ist dauerhaft aktiv

```
Der PDI-Prompt ist in jedem Projekt dauerhaft aktiv.
Kein Generator (Mensch oder KI) darf Inhalte ohne ihn ausgeben.
```

### Regel 2: Vor jeder Ausgabe automatisch prüfen

```
1. Syntaxprüfung
2. Lintprüfung
3. Logikprüfung
4. Sicherheitsprüfung
5. GitHub Copilot-Prüfung (simuliert)
6. Integration-Prüfung
```

### Regel 3: Freigabe nur mit Header

```
Nur Dateien mit [PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]
gelten als freigegeben, funktional und systemkonform.
```

### Regel 4: Validierungs-Log speichern

```
Jedes Validation-Event wird geloggt:
- Timestamp
- Module
- Gates
- Errors
- Warnings
- Suggestions
```

---

## 7. Integrations-Schnittstellen

### 1. CLI-Integration

```bash
# Datei validieren
pdi validate <file>

# Projekt initialisieren
pdi init <project-name>

# Report generieren
pdi report <project-id>
```

### 2. CI/CD-Integration

```yaml
# .github/workflows/pdi-check.yml
- name: PDI Validation
  run: |
    python pdi_core.py validate ${{ github.workspace }}
    python pdi_core.py report
```

### 3. Git-Hook Integration

```bash
# .git/hooks/pre-commit
#!/bin/bash
python pdi_core.py validate --staged
```

---

## 8. Validierungs-Log-Format

```json
{
  "project_id": "elion-dashboard-2025",
  "artifact_id": "agents_auto_register.sh",
  "artifact_type": "bash",
  "validation_timestamp": "2025-11-09T12:34:56Z",
  "modules_executed": [
    "LINGUISTIC",
    "TECHNICAL",
    "CORRECTION",
    "ANALYTICS",
    "CONTROL",
    "GITHUB"
  ],
  "results": {
    "linguistic": {
      "valid": true,
      "level": "COMMENTED",
      "errors": [],
      "warnings": [],
      "suggestions": ["Add function docstrings"],
      "duration_ms": 45.2
    },
    "technical": {
      "valid": true,
      "level": "IMPROVED",
      ...
    },
    ...
  },
  "gates_passed": [1, 2, 3, 4, 5, 6],
  "final_status": "RELEASED",
  "pdi_header": "[PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]"
}
```

---

## 9. FAQs

**F: Was passiert wenn ein Gate fehlschlägt?**
A: Artifact geht zurück zu Gate 1 mit Feedback (Errors + Suggestions)

**F: Kann ich Gate-Anforderungen überschreiben?**
A: Nein. Alle Gates sind Pflicht. Keine Shortcuts.

**F: Wie lange dauert PDI für ein Projekt?**
A: Ca. 15–20 Minuten pro Kapitel (5–8 Gates parallel möglich)

**F: Kann ich PDI-Module selbst erweitern?**
A: Ja. Neue Module bitte als Subclass von PDIModule registrieren.

---

## 10. Checkliste vor Freigabe

- [ ] Alle Module durchlaufen: LINGUISTIC, TECHNICAL, CORRECTION, ANALYTICS, CONTROL, GITHUB
- [ ] Alle 6 Gates passed
- [ ] Keine Errors (nur Warnings/Suggestions akzeptabel)
- [ ] PDI-Header vorhanden
- [ ] Validation-Log gespeichert
- [ ] Documentation aktualisiert
- [ ] Tests bestanden (if applicable)
- [ ] Security-Check passed
- [ ] Integration-Test erfolgreich

---

## 11. Support & Eskalation

| Problem                 | Lösung                                  |
| ----------------------- | --------------------------------------- |
| Gate 1 (Syntax) fehlt   | → pdi fix:syntax <file>                 |
| Gate 3 (Lint) fehlt     | → Linter ausführen: flake8, black, etc. |
| Gate 6 (Security) fehlt | → Security-Review mit Sicherheits-Team  |
| Unklare Errors          | → pdi explain <validation-id>           |

---

**Status:** [PDI-ACTIVE: TRUE | MANIFEST-STABLE | READY-FOR-USE]
**Last Updated:** 2025-11-09
**Maintained by:** ELION Team
