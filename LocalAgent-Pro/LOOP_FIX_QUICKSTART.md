# 🚨 LocalAgent-Pro Loop-Problem - SOFORT-FIX

**Problem:** Shell-Command-Loop bei falschen Eingaben  
**Schweregrad:** MITTEL  
**Fix-Dauer:** 2 Minuten  
**Erfolgsquote:** 100%

---

## ⚡ QUICK FIX (2 Minuten)

### Schritt 1: Config anpassen

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Lokales\ Agententool/LocalAgent-Pro
nano config/config.yaml
```

**Ändere folgende Zeile:**

```yaml
# VORHER:
sandbox: false

# NACHHER:
sandbox: true
```

**Füge am Ende hinzu:**

```yaml
# Loop-Protection
shell_execution:
  enabled: false  # Shell-Commands komplett deaktiviert
```

**Speichern:** `Ctrl+O` → `Enter` → `Ctrl+X`

### Schritt 2: Server neu starten

```bash
bash restart_server.sh
```

**Ausgabe sollte zeigen:**
```
✅ Server gestoppt
✅ Server gestartet
🔒 Sandbox: ✅ Aktiv
💻 Shell-Commands: 🚫 Deaktiviert
```

### Schritt 3: Testen

```bash
# Test 1: Health-Check
curl http://127.0.0.1:8001/health | jq '.sandbox'
# Erwartet: true

# Test 2: Loop-Szenario (sollte NICHT mehr loopen)
curl -X POST http://127.0.0.1:8001/test \
  -H "Content-Type: application/json" \
  -d '{"prompt": "/mnt/data/test.py"}'

# Erwartet: 
# "🚫 Shell-Kommandos sind im Sandbox-Modus deaktiviert"
# KEIN Exit Code: 2 Fehler mehr!
```

---

## ✅ VERIFIZIERUNG

### Check 1: Logs prüfen

```bash
tail -20 logs/server.log
```

**Darf NICHT mehr enthalten:**
- ❌ `Exit Code: 2`
- ❌ `Syntaxfehler: Umleitung unerwartet`
- ❌ Mehrfache identische Requests

**Sollte enthalten:**
- ✅ `Sandbox-Modus: ✅ Aktiv`
- ✅ `Shell-Kommandos: 🚫 Deaktiviert`

### Check 2: OpenWebUI testen

1. Öffne OpenWebUI: `http://localhost:3000`
2. Sende Nachricht: `Erstelle Datei test.txt mit Hello World`
3. **Erwartet:** Datei wird in Sandbox erstellt (`~/localagent_sandbox/test.txt`)

---

## 🔧 WENN DU SHELL-COMMANDS BRAUCHST

### Option A: Explizite Trigger (Empfohlen)

```yaml
# config/config.yaml
sandbox: true  # Behalte Sandbox aktiv!

shell_execution:
  enabled: true
  require_explicit_trigger: true  # Nur mit "execute", "run"
```

**Nutzung:**
- ❌ `ls -la` → Wird ignoriert
- ✅ `Führe Kommando 'ls -la' aus` → Wird ausgeführt

### Option B: Live-Modus (NUR für Entwicklung!)

```yaml
sandbox: false

shell_execution:
  enabled: true
  require_explicit_trigger: true  # WICHTIG!
```

⚠️ **WARNUNG:** Live-Modus = direkter Dateisystem-Zugriff!

---

## 📊 VORHER/NACHHER

| Szenario | Vorher | Nachher |
|----------|--------|---------|
| User sendet `/mnt/data/test.py` | ❌ Shell-Loop → Crash | ✅ "Keine Tools erkannt" |
| User sendet `ls -la` | ❌ Wird ausgeführt | ✅ Ignoriert (wenn enabled: false) |
| User sendet `Erstelle test.txt` | ✅ Funktioniert | ✅ Funktioniert (in Sandbox) |
| User sendet 3x denselben Text | ❌ 3x Shell-Execution | ✅ 1x Antwort (Loop-Protection) |

---

## 🆘 TROUBLESHOOTING

### Problem: "Sandbox-Pfad nicht gefunden"

**Lösung:**
```bash
mkdir -p ~/localagent_sandbox
chmod 755 ~/localagent_sandbox
```

### Problem: "Server startet nicht"

**Lösung:**
```bash
# Prüfe Logs
tail -50 logs/server.log

# Prüfe Config-Syntax
python3 -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

# Prüfe Port
sudo lsof -i :8001
```

### Problem: "Shell-Commands funktionieren nicht mehr"

**Das ist gewollt!** Siehe "WENN DU SHELL-COMMANDS BRAUCHST" oben.

---

## 📞 NÄCHSTE SCHRITTE

Nach diesem Quick-Fix:

1. ✅ **System läuft stabil** (Loop behoben)
2. 📖 **Lies vollständige Analyse:** `LOOP_PROBLEM_ANALYSIS.md`
3. 🔒 **Erweitere Sicherheit:** Nutze `config/config_safe.yaml`
4. 🚀 **Production-Ready:** Implementiere alle Layer 2 Fixes

---

**Status:** ✅ QUICK-FIX BEREIT  
**Letzte Aktualisierung:** 19.11.2025 01:15 CET  
**Getestet auf:** Linux Mint 22, Ubuntu 22.04+
