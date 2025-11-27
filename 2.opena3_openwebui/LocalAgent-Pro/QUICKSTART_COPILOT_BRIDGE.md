# 🚀 VSCode Copilot Bridge - Quick Start Guide

**Status:** ✅ Produktionsreif
**Datum:** 25. November 2025
**Version:** 1.0

---

## 📌 Was ist das?

Ein vollautomatisiertes Bash-Skript, das LocalAgent-Pro mit VSCode Copilot verbindet für:

- ✅ **Automatische Test-Generierung** (pytest)
- ✅ **Projektstruktur-Optimierung**
- ✅ **ZIP-Deployment-Export**
- ✅ **Health-Checks** (System-Validierung)

---

## 🎯 5-Minuten Setup

### 1. Navigiere zum Projekt
```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui/LocalAgent-Pro
```

### 2. Starte das Skript
```bash
./scripts/vscode_copilot_bridge.sh
```

### 3. Wähle eine Aktion
```
1️⃣  TEST-Generierung (10 Sek)
2️⃣  Struktur reorganisieren (30 Sek)
3️⃣  ZIP Export (45 Sek)
4️⃣  ALLES (2 Min)
6️⃣  Health-Check (15 Sek)
```

---

## 📋 Was macht jede Aktion?

### 🧪 Option 1: TEST-Generierung

**Erstellt:**
```
tests/
├── unit/
│   ├── core/
│   ├── server/
│   ├── tools/
│   ├── agents/
│   └── test_server.py
├── integration/
├── fixtures/
├── conftest.py
└── __init__.py
```

**Plus Dateien:**
- `pytest.ini` - Pytest-Konfiguration
- `.coveragerc` - Coverage-Konfiguration

**Ausführen:**
```bash
pytest -v --cov=src
```

---

### 📁 Option 2: Struktur optimieren

**Neue Struktur:**
```
LocalAgent-Pro/
├── src/
│   ├── core/
│   ├── server/
│   ├── tools/
│   ├── agents/
│   └── utils/
├── scripts/
│   ├── health/
│   ├── deploy/
│   └── *.sh
├── docs/
│   └── PROJECT_MAP.md
└── config/
```

**Und generiert:**
- `docs/PROJECT_MAP.md` - Vollständige Struktur-Dokumentation

---

### 📦 Option 3: ZIP Export

**Erstellt auf Desktop:**
```
LocalAgent-Pro-Autobuild_20251125_120200.zip
LocalAgent-Pro-Autobuild_20251125_120200_MANIFEST.txt
```

**Enthält:**
- Kompletten Quellcode
- Tests & Fixtures
- Dokumentation
- Konfiguration
- Shell-Skripte

**Nicht enthalten (automatisch ausgeschlossen):**
- `.git/`, `.venv/`, `__pycache__/`
- `*.pyc`, `.pytest_cache/`

---

### 🏥 Option 6: Health-Check

**Prüft:**
- ✅ VSCode Installation
- ✅ Python-Version
- ✅ Abhängigkeiten (Flask, requests, pytest, etc.)
- ✅ Git-Repository
- ✅ Verzeichnis-Struktur
- ✅ Kritische Dateien
- ✅ Port-Verfügbarkeit
- ✅ Disk-Space
- ✅ Test-Suite
- ✅ Copilot-Integration

**Output-Beispiel:**
```
✅ VSCode installiert: 1.96.0
✅ Python3 vorhanden: Python 3.12.3
✅ Python-Version ausreichend: 3.12
✅ pip vorhanden
✅ Modul vorhanden: flask
...
🎉 ALLES IN ORDNUNG! System ist bereit.
System Health: 98%
```

---

## 💡 Häufige Workflows

### Schneller Komplett-Run
```bash
./scripts/vscode_copilot_bridge.sh
# Wähle: 4 (ALLES)
# Warte ~2 Min
```

### Nur Tests
```bash
./scripts/vscode_copilot_bridge.sh
# Wähle: 1
cd tests
pytest -v
```

### Vorbereitung für Deployment
```bash
./scripts/vscode_copilot_bridge.sh
# Wähle: 4 (ALLES)
# Wähle: 6 (Health-Check)
# ZIP-Datei findet sich auf Desktop
```

---

## 🔍 Log-Dateien

Alle Aktionen werden protokolliert:

```bash
# Letzte Logs ansehen
tail -f logs/copilot_bridge_*.log

# Alle Errors suchen
grep "ERROR" logs/copilot_bridge_*.log

# Spezifischen Run ansehen
cat logs/copilot_bridge_20251125_120200.log
```

---

## 🛠️ Fehlerbehebung

### Problem: "Command not found"
```bash
# Lösung:
chmod +x ./scripts/vscode_copilot_bridge.sh
```

### Problem: "VSCode nicht gefunden"
```bash
# Prüfe:
which code

# Oder setze manuell:
VSCODE_CMD="/usr/bin/code" ./scripts/vscode_copilot_bridge.sh
```

### Problem: "Permission denied"
```bash
# Lösung:
chmod +x ./scripts/*.sh
chmod +x ./scripts/health/*.sh
```

### Problem: "ZIP Erstellung fehlgeschlagen"
```bash
# Prüfe:
zip --version  # Sollte installiert sein

# Falls nicht:
sudo apt install zip

# Oder nutze /tmp statt Desktop:
# Das Skript fällt automatisch zurück
```

---

## 📊 Konfiguration anpassen

Bearbeite für benutzerdefinierte Einstellungen:

```bash
# Konfigurationsdatei öffnen
code config/.copilot_bridge_config.yaml
```

**Wichtige Einstellungen:**
```yaml
project:
  root: "/pfad/zum/projekt"

vscode:
  auto_open: true

python:
  pytest:
    coverage_threshold: 80

zip_export:
  target_dir: "${HOME}/Desktop"
```

---

## 📚 Zusätzliche Dokumentation

- `COPILOT_BRIDGE_README.md` - Ausführliche Dokumentation
- `config/.copilot_bridge_config.yaml` - Alle Einstellungen
- `docs/PROJECT_MAP.md` - Projekt-Struktur (wird generiert)

---

## 🚀 Nächste Schritte

1. ✅ Skript testen: `./scripts/vscode_copilot_bridge.sh` → Option 6
2. ✅ Tests generieren: Option 1
3. ✅ Struktur optimieren: Option 2
4. ✅ ZIP Export: Option 3
5. ✅ Deployment durchführen

---

## 📞 Support & Troubleshooting

**Log-Fehler?**
```bash
tail -50 logs/copilot_bridge_*.log | grep ERROR
```

**Script hängt?**
```bash
# Abort und neu starten
Ctrl+C
./scripts/vscode_copilot_bridge.sh
```

**Struktur verändert?**
```bash
# Führe Check aus:
./scripts/health/check_system.sh
```

---

## ✅ Checkliste vor Production

- [ ] Health-Check erfolgreich (Option 6)
- [ ] Tests generiert (Option 1)
- [ ] Coverage > 80%
- [ ] Struktur optimiert (Option 2)
- [ ] ZIP-Export erstellt (Option 3)
- [ ] Logs überprüft
- [ ] Deployment-Paket getestet

---

**🎉 Du bist fertig! Das System ist produktionsreif.**

Starte jederzeit mit: `./scripts/vscode_copilot_bridge.sh`

---

**Version:** 1.0
**Status:** ✅ Production Ready
**Letzte Aktualisierung:** 25. November 2025
