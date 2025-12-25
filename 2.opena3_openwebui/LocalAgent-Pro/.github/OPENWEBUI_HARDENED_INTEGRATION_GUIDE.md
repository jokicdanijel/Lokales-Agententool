# 🔒 OpenWebUI Hardened Copilot Instructions - Integration Guide

**Datum:** 25. November 2025
**Status:** ✅ Production Ready
**Version:** 1.0

---

## 📌 Überblick

Die Datei `.github/copilot-instructions-openwebui-hardened.md` definiert das Verhalten des Copilot **ausschließlich für OpenWebUI-Instanzen** des LocalAgent-Pro Systems.

### Wichtige Unterscheidungen

| Kontext                    | Datei                                                | Verhalten                  |
| -------------------------- | ---------------------------------------------------- | -------------------------- |
| **VSCode**                 | `.github/copilot-instructions.md`                    | Normal (unrestricted)      |
| **OpenWebUI**              | `.github/copilot-instructions-openwebui-hardened.md` | 🔒 Scan-First (Hardened)   |
| **Browser-Agent (opena6)** | Keine Beschränkungen                                 | ✅ 100% Frei & Unlimitiert |

---

## 🎯 Warum Scan-First?

### Das Problem (Ohne Scan-First)

```
User: „Erstelle einen neuen Agenten"
Copilot: *Erstellt blind neue Datei, ohne zu prüfen*
Ergebnis:
  ❌ Datei existiert bereits
  ❌ Überschreibt kritischen Code
  ❌ Bricht Abhängigkeiten
  ❌ Keine Audit-Spur
```

### Die Lösung (Mit Scan-First)

```
User: „Erstelle einen neuen Agenten"
Copilot: *INVENTORY MODE aktiviert*
  ✅ Scannt Projekt-Struktur
  ✅ Prüft existierende Dateien
  ✅ Identifiziert Abhängigkeiten
  ✅ Simuliert Aktion (Dry-Run)
Copilot: „Bereit? Ja/Nein?"
User: „Ja"
Copilot: *EXECUTION MODE startet*
  ✅ Erstellt nur wenn geprüft
  ✅ Mit vollständiger Audit-Spur
  ✅ Reversibel dokumentiert
```

---

## 🧠 Die zwei Phasen

### Phase 1: INVENTORY MODE (Automatisch)

Bei **jedem neuen Prompt** wird automatisch:

1. **PROJEKT SCANNEN** - Struktur erfassen
2. **DATEIEN ZUORDNEN** - Komponenten identifizieren
3. **RISIKEN ERKENNEN** - Potenzielle Probleme
4. **DRY-RUN SIMULIEREN** - Was würde passieren?
5. **ERGEBNIS ZEIGEN** - Übersicht anzeigen
6. **BESTÄTIGUNG FRAGEN** - User-Input abwarten

**Ohne Bestätigung = Keine Aktion!**

### Phase 2: EXECUTION MODE (Nur nach Freigabe)

Nach Bestätigung mit „Ja", „Go", „Confirm", etc.:

1. **Aktion ausführen** - NUR auf geprüften Dateien
2. **Keine Zusätze** - Genau das, was gefragt
3. **Keine Spekulationen** - Nur bekannte Dateien
4. **Erfolg bestätigen** - Mit Audit-Spur

---

## 📋 INVENTORY CHECK - Was wird geprüft?

### Strukturelle Elemente

```
✓ Ordnerstrukturen (src/, scripts/, docs/, tests/)
✓ Python-Module & Packaging
✓ Test-Suites & Fixtures
✓ Konfigurationsdateien (YAML, JSON)
✓ Shell-Skripte
✓ Logs & Temp-Verzeichnisse
```

### Komponenten-Erkennung

```
✓ Agent-Struktur (opena1-opena20)
✓ Tool-Module (Voice-Tools)
✓ Browser-Agent (opena6)
✓ Dispatcher & Tool-Server
✓ OpenWebUI-Integrationen
✓ Externe Access (ngrok, SSH, CLI)
```

### Kritikalität-Analyse

```
🔴 LEBENSNOTWENDIG
   → openwebui_agent_server.py
   → shared/auth.py
   → vscode_copilot_bridge.sh

🟠 KRITISCH
   → config files
   → requirements.txt
   → opena6/tool_server.py

🟡 UNTERSTÜTZEND
   → Logger, Helpers
   → Tool-Module
   → Test-Utilities

🟢 OPTIONAL
   → Extra-Tests
   → Doc-Dateien
   → Examples

⚫ TOT/DEPRECATED
   → Alte Backup-Dateien
   → Ungenutzte Scripts

⚪ PHANTOM
   → Sollte existieren, tut aber nicht
```

---

## 🚫 SCHUTZSCHILDE (Was ist verboten)

| Verboten                      | Grund                            | Schutz                            |
| ----------------------------- | -------------------------------- | --------------------------------- |
| Code generieren ohne Prüfung  | Könnte Duplikate erzeugen        | Inventory erzwingt Prüfung        |
| Kritische Datei überschreiben | Könnte System brechen            | Kritische Dateien werden markiert |
| Unbekannte Dateien ändern     | Risiko: Unvorhergesehene Effekte | Nur geprüfte Dateien              |
| Spekulativ handeln            | Raten statt wissen               | Bei Unsicherheit: Erneut prüfen   |
| Ohne Bestätigung ausführen    | User-Intent nicht geklärt        | Blockierer vor Phase 2            |

---

## ⚡ ERLAUBTE AKTIONEN (OpenWebUI)

```
✅ „Analysiere das Projekt"
✅ „Gib mir eine Übersicht"
✅ „Zeige kritische Dateien"
✅ „Generiere Tests"
✅ „Reorganisiere Struktur"
✅ „ZIP Export"
✅ „Starte VSCode Bridge"
✅ „Öffne Datei X"
✅ „Finde Datei X"
✅ „Zeige Problemstellen"
✅ „Erstelle Fix für Datei X (nach Prüfung)"
✅ „Health-Check"
✅ „Alles ausführen"
✅ „Debugging & Repair"
```

Alle Aktionen folgen: **Inventory → Bestätigung → Execution**

---

## 🔧 IMPLEMENTATION

### Wie wird diese Datei genutzt?

1. **In OpenWebUI Chat:**

   ```
   User: „Analysiere das Projekt für mich"

   Copilot: [INVENTORY MODE aktiviert]
   • Scannt LocalAgent-Pro Struktur
   • Identifiziert 20 Agenten
   • Findet 6 Voice-Tools
   • Markiert kritische Dateien
   • Prüft Abhängigkeiten

   [Zeigt Ergebnis]

   Copilot: „Bestätigung erforderlich?"
   ```

2. **Bei Änderungen:**

   ```
   User: „Füge einen neuen Test hinzu"

   Copilot: [INVENTORY MODE]
   • Prüft tests/ Struktur
   • Schaut on test_auth.py existiert
   • Identifiziert verfügbare Fixtures
   • Simuliert neue Funktion

   [Zeigt Inventory-Ergebnis]

   User: „Ja, go"

   Copilot: [EXECUTION MODE]
   • Fügt test_new_function() hinzu
   • Validiert mit pytest
   • Bestätigt Erfolg
   ```

---

## 📊 AUDIT-SICHERHEIT

Diese Implementierung ist audit-sicher, weil:

✅ **Nicht spekulativ** - Jede Aktion basiert auf realer Prüfung
✅ **Rückverfolgbar** - Alle Schritte sind dokumentiert
✅ **Revertierbar** - Änderungen sind bekannt
✅ **Benutzerkontrolliert** - Explizite Bestätigung erforderlich
✅ **Fehler-vermeidend** - Risiken werden proaktiv erkannt
✅ **Abhängigkeits-bewusst** - Alle Effekte sind bekannt

---

## 🔐 SICHERHEITS-CHECKLISTE

Bei jeder geplanten Änderung wird geprüft:

- [ ] Existiert die Datei physisch?
- [ ] Kenne ich alle Abhängigkeiten?
- [ ] Wer hängt von dieser Datei ab?
- [ ] Könnte dies das System brechen?
- [ ] Gibt es Tests zur Validierung?
- [ ] Kann ich die Änderung rückgängig machen?
- [ ] Hat der User bestätigt?
- [ ] Ist dies die minimal-invasive Lösung?

**Wenn ein „Nein" → STOP → Weitere Prüfung erforderlich**

---

## 📝 BEISPIEL-WORKFLOWS

### Workflow 1: Neuen Test generieren

```
INPUT: „Generiere einen Test für die Auth-Funktion"

🧠 INVENTORY MODE
═══════════════════════════════════
• shared/auth.py gefunden ✓
• tests/unit/ Struktur vorhanden ✓
• pytest.ini konfiguriert ✓
• conftest.py mit Fixtures ✓
• bcrypt Abhängigkeit verfügbar ✓

📋 ERGEBNIS:
🔴 KRITISCH: shared/auth.py (nicht ändern)
🟡 UNTERSTÜTZEND: tests/unit/test_auth.py (test hinzufügen)
✅ RISIKEN: Keine

Bereit?

USER: „Ja"

✅ EXECUTION MODE
═══════════════════════════════════
• Neue test_auth_bcrypt_validation() hinzufügen
• Nutze existierende Fixtures
• pytest --cov validiert

✅ FERTIG
test_auth_bcrypt_validation() erfolgreich hinzugefügt
```

### Workflow 2: Projekt-Struktur analysieren

```
INPUT: „Zeige mir alle kritischen Dateien"

🧠 INVENTORY MODE
═══════════════════════════════════
• Scanne gesamtes Projekt
• Identifiziere Komponenten
• Bewerte Kritikalität

📋 ERGEBNIS:
🔴 LEBENSNOTWENDIG (5 Dateien):
   - openwebui_agent_server.py
   - shared/auth.py
   - vscode_copilot_bridge.sh
   - config/config.yaml
   - requirements.txt

🟠 KRITISCH (12 Dateien):
   - opena6/tool_server.py
   - opena*/main.py (20 Dateien)
   - tests/conftest.py
   - ...

Weitere Details?
```

### Workflow 3: ZIP-Export mit Sicherheit

```
INPUT: „Erstelle ZIP-Export für Deployment"

🧠 INVENTORY MODE
═══════════════════════════════════
• Alle Dateien scannen
• Kritische Dateien identifizieren
• Exclude-Patterns prüfen
• Größe simulieren (~45 MB)

📋 ERGEBNIS:
✅ WILL EXPORT:
   - src/ vollständig
   - tests/ mit Fixtures
   - docs/ mit Guides
   - config/ mit Examples

❌ WILL EXCLUDE:
   - .git/ Verzeichnis
   - .venv/ Verzeichnis
   - __pycache__/
   - *.pyc Dateien
   - .pytest_cache/

📊 SIZE: ~45 MB
⚠️ RISKS: Keine

Bestätigung erforderlich?

USER: „Ja, ZIP Export"

✅ EXECUTION MODE
═══════════════════════════════════
@vscode_copilot_bridge { "action": "zip_export" }

[VSCode Bridge wird getriggert]
[ZIP erstellt auf Desktop]
[MANIFEST.txt generiert]

✅ FERTIG
ZIP: LocalAgent-Pro-Autobuild_20251125_120200.zip (45 MB)
```

---

## 🎯 BEST PRACTICES

### Für OpenWebUI-Benutzer

1. **Sei spezifisch:**
   - ✅ „Generiere einen Test für die Auth-Funktion"
   - ❌ „Mach irgendwas mit Tests"

2. **Warte auf Inventory:**
   - ✅ Lese das Inventory-Ergebnis
   - ❌ Bestätige blind

3. **Bestätige bewusst:**
   - ✅ „Ja, die Analyse sieht gut aus"
   - ❌ Sofortiges „Ja" ohne Prüfung

4. **Nutze Logs:**
   - ✅ Prüfe logs/copilot*bridge*\*.log nach jeder Aktion
   - ❌ Ignoriere Logs

---

## 🚀 AKTIVIERUNG

### In OpenWebUI

Diese Datei wird automatisch geladen, wenn:

1. User einen neuen Chat startet
2. LocalAgent-Pro Copilot aufgerufen wird
3. Automatisch im OpenWebUI System-Prompt

### Fallback

Wenn die Datei nicht geladen wird:

```bash
# Manuell in System-Prompt kopieren:
cat .github/copilot-instructions-openwebui-hardened.md
```

Dann in OpenWebUI Chat-Settings einfügen.

---

## ⚠️ WICHTIGE HINWEISE

### Was diese Datei NICHT macht

❌ Sie schränkt **Browser-Agent (opena6) nicht ein** - Der bleibt 100% frei
❌ Sie schränkt **VSCode-Version nicht ein** - Die hat eigene Instructions
❌ Sie generiert keine Dateien automat - Alles braucht Bestätigung
❌ Sie "löscht" oder "überschreibt" nichts - Das macht der User

### Was diese Datei TUN

✅ Sie schützt vor spekulativem Code
✅ Sie erzwingt Audit-Spur
✅ Sie verhindert unbeabsichtigte Fehler
✅ Sie gibt User vollständige Kontrolle
✅ Sie dokumentiert jede Entscheidung

---

## 📞 SUPPORT

Wenn etwas unklar ist:

```
🔐 INVENTORY FEHLER

Ich konnte nicht feststellen: [Was?]
Grund: [Warum?]

Bitte sag mir:
• Existiert Datei X? (Ja/Nein)
• Ist Y abhängig von Z? (Ja/Nein)
• Soll ich das Projekt neu scannen?

→ Ich warte auf Klarstellung.
```

---

## 🎉 ZUSAMMENFASSUNG

| Aspekt                | Status                          |
| --------------------- | ------------------------------- |
| **Audit-Sicherheit**  | ✅ Maximal                      |
| **User-Kontrolle**    | ✅ Vollständig                  |
| **Fehler-Vorbeugung** | ✅ Umfassend                    |
| **Performance**       | ✅ Schnell (Scan ~2-3 Sekunden) |
| **Integration**       | ✅ OpenWebUI-ready              |
| **Dokumentation**     | ✅ Vollständig                  |

---

**Datei:** `.github/copilot-instructions-openwebui-hardened.md`
**Status:** ✅ Production Ready
**Version:** 1.0 Hardened
**Gültig für:** OpenWebUI LocalAgent-Pro Instanz
**Datum:** 25. November 2025

---

**🔒 Scan-First ist jetzt dein Schutzschild.**
