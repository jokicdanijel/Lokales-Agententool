# 🔒 **GOVERNANCE EXECUTION CHECKLIST**

**Datum:** 27. November 2025
**Zweck:** Sichere Ausführung der 3 Governance-Fix-Skripte
**Kritisch:** Befolge **ALLE** Schritte vor Ausführung

---

## ⚠️ **KRITISCHE WARNUNG**

Diese Skripte **VERÄNDERN** die Repo-Struktur:

- **GOVERNANCE_FIX_ARCHIV.sh** → Verschiebt 42+ Safepoints
- **GOVERNANCE_FIX_VENV_LEAKS.sh** → Löscht 4 Dateien aus src/pkg/
- **GOVERNANCE_FIX_TESTS.sh** → Verschiebt 10+ Tests

**Keine Ausführung ohne vollständige Checkliste!**

---

## 📋 **PRE-EXECUTION CHECKLIST (ZWINGEND)**

Markiere **JEDES** Item mit `[x]` vor Ausführung:

### **1. Git-Safety**

- [ ] **Git-Status clean:** `git status` zeigt keine uncommitted changes
- [ ] **Feature-Branch erstellt:** `git checkout -b governance-fix-2025-11-27`
- [ ] **Backup-Branch:** `git branch governance-backup-$(date +%Y%m%d)`
- [ ] **Remote synchronized:** `git fetch origin` ausgeführt
- [ ] **Kein main/master:** Du bist NICHT auf main/master Branch

**Validation Command:**

```bash
git status --porcelain  # MUSS LEER SEIN
git branch --show-current  # DARF NICHT main/master SEIN
```

---

### **2. Environment-Checks**

- [ ] **Python Version:** `python3 --version` → 3.12+ (idealerweise 3.13)
- [ ] **venv aktiviert:** `which python3` zeigt auf venv313 oder venv_local
- [ ] **pytest installiert:** `pytest --version` funktioniert
- [ ] **Disk Space:** `df -h .` zeigt mind. 1GB freien Speicher
- [ ] **Permissions:** Du hast Write-Rechte auf PROJECT_ROOT

**Validation Command:**

```bash
python3 --version
pytest --version || echo "⚠️ pytest fehlt – pip install pytest"
df -h . | grep -E "Avail|Filesystem"
```

---

### **3. Backup-Strategy**

- [ ] **Full Repo Backup:** `tar -czf ../Gesamtprojekt_backup_$(date +%Y%m%d).tar.gz .`
- [ ] **configs/ Backup:** `cp -r configs/ configs_backup_$(date +%Y%m%d)/`
- [ ] **src/pkg/ Backup:** `cp -r src/pkg/ src/pkg_backup_$(date +%Y%m%d)/`
- [ ] **tests/ Backup:** `cp -r 19.dashboard_agent/tests/ tests_backup_$(date +%Y%m%d)/`
- [ ] **Backup-Location notiert:** Pfad zu Backups dokumentiert

**Validation Command:**

```bash
ls -lh ../Gesamtprojekt_backup_*.tar.gz  # MUSS EXISTIEREN
ls -d configs_backup_* src/pkg_backup_* tests_backup_*  # MUSS EXISTIEREN
```

---

### **4. Pre-Flight Dry-Run**

- [ ] **ARCHIV Dry-Run:** `DRY_RUN=true ./GOVERNANCE_FIX_ARCHIV.sh` durchgelaufen
- [ ] **VENV Dry-Run:** `DRY_RUN=true ./GOVERNANCE_FIX_VENV_LEAKS.sh` durchgelaufen
- [ ] **TESTS Dry-Run:** `DRY_RUN=true ./GOVERNANCE_FIX_TESTS.sh` durchgelaufen
- [ ] **Logs reviewed:** Alle 3 Log-Dateien manuell überprüft
- [ ] **Keine Errors:** Keine ERROR-Meldungen in Dry-Run-Logs

**Validation Command:**

```bash
cat GOVERNANCE_FIX_ARCHIV.log | grep -i error
cat GOVERNANCE_FIX_VENV_LEAKS.log | grep -i error
cat GOVERNANCE_FIX_TESTS.log | grep -i error
# Alle MÜSSEN LEER SEIN
```

---

### **5. Manual Review**

- [ ] **rename_map.csv gelesen:** Zeilen 295-544 manuell durchgeschaut
- [ ] **Import-Scan ausgeführt:** `grep -R "src.pkg" . | grep -v ".git" | wc -l` → 0
- [ ] **Safepoint-Count:** `find configs/ -name "SP*.json" | wc -l` notiert (Soll: 42+)
- [ ] **Conflicts-Count:** `find _conflicts/ -type f | wc -l` notiert
- [ ] **Test-List:** Liste der kritischen Tests erstellt (test_archivator.py, etc.)

**Validation Command:**

```bash
echo "Safepoints in configs/: $(find configs/ -name 'SP*.json' | wc -l)"
echo "Dateien in _conflicts/: $(find _conflicts/ -type f 2>/dev/null | wc -l)"
grep -R "src\.pkg\.\(typing_extensions\|socks\|py\)" . 2>/dev/null | grep -v ".git" | wc -l
```

---

## 🚀 **EXECUTION ORDER (STRICT)**

**NUR nach vollständiger Checklist ausführen!**

### **Phase 1: ARCHIV Rollback** (CRITICAL)

```bash
# 1. Letzter Check
git status  # MUSS CLEAN SEIN

# 2. Ausführung
DRY_RUN=false ./GOVERNANCE_FIX_ARCHIV.sh

# 3. Validierung
find configs/ -name "SP*.json" | wc -l  # MUSS 0 SEIN
find */ARCHIV/ */archivp/ -name "SP*.json" | wc -l  # MUSS 42+ SEIN

# 4. Git Commit
git add .
git commit -m "fix(governance): ARCHIV rollback - Safepoints zurück in YYYY/MM/DD"
```

**⏸ PAUSE:** Review Commit, prüfe Diff, teste opena2 Config

---

### **Phase 2: venv-Leaks Cleanup** (HIGH)

```bash
# 1. Import-Scan (final)
grep -R "src\.pkg\.\(typing_extensions\|socks\|py\)" . 2>/dev/null | grep -v ".git"
# MUSS LEER SEIN – sonst STOP!

# 2. Ausführung
DRY_RUN=false ./GOVERNANCE_FIX_VENV_LEAKS.sh

# 3. Validierung
ls src/pkg/typing_extensions.py 2>/dev/null  # DATEI DARF NICHT EXISTIEREN
ls src/pkg/socks.py 2>/dev/null  # DATEI DARF NICHT EXISTIEREN
grep "PySocks" requirements.txt  # MUSS VORHANDEN SEIN

# 4. Dependency-Install
pip install -r requirements.txt

# 5. Git Commit
git add .
git commit -m "fix(governance): venv-leaks cleanup - third-party aus src/pkg/ entfernt"
```

**⏸ PAUSE:** Test imports (`python3 -c "import socks; print('OK')"`)

---

### **Phase 3: Tests Rescue** (HIGH)

```bash
# 1. Ausführung
DRY_RUN=false ./GOVERNANCE_FIX_TESTS.sh

# 2. Validierung
pytest 19.dashboard_agent/tests/test_archivator.py  # MUSS PASSED SEIN
pytest 19.dashboard_agent/tests/test_openwebui_agent.py  # MUSS PASSED SEIN

# 3. Git Commit
git add .
git commit -m "fix(governance): tests rescue - produktive Tests aus _conflicts/ wiederhergestellt"
```

**⏸ PAUSE:** Run full test suite (`pytest tests/`)

---

## ✅ **POST-EXECUTION VALIDATION**

Nach **ALLEN 3 Phasen**:

### **1. Governance Compliance Check**

```bash
# Check 1: Keine Safepoints in configs/
find configs/ -name "SP*.json" | wc -l
# Erwartete Ausgabe: 0

# Check 2: Safepoints in ARCHIV/archivp/
find */ARCHIV/ */archivp/ -name "SP*.json" | wc -l
# Erwartete Ausgabe: 42+

# Check 3: Keine venv-Leaks in src/pkg/
ls src/pkg/{typing_extensions,socks,py,sockshandler}.py 2>/dev/null
# Erwartete Ausgabe: (Fehler – Dateien nicht gefunden)

# Check 4: Tests in tests/
pytest 19.dashboard_agent/tests/ --collect-only | grep "test session starts"
# Erwartete Ausgabe: Mindestens 10 Tests gefunden

# Check 5: Dependencies installiert
pip list | grep -E "PySocks|pytest"
# Erwartete Ausgabe: Beide Pakete vorhanden
```

---

### **2. Architecture Integrity Check**

```bash
# opena2 Config prüfen
grep -R "ARCHIV\|archivp" 1.opena1&2_portier/config/ 19.dashboard_agent/config/
# Sollte auf archivp/ARCHIV/ zeigen, NICHT configs/

# Option-2-Flow Test
bin/verify_stack.sh
# Sollte alle Agents als "healthy" zeigen
```

---

### **3. Git Housekeeping**

```bash
# Status prüfen
git status  # Sollte clean sein

# Log prüfen
git log --oneline -3
# Sollte 3 Commits zeigen: ARCHIV, venv-leaks, tests

# Merge zu main (NUR wenn alles OK)
git checkout main
git merge governance-fix-2025-11-27
git push origin main

# Backup-Branch behalten
git branch  # governance-backup-* sollte noch da sein
```

---

## 🆘 **ROLLBACK (FALLS ETWAS SCHIEFGEHT)**

### **Sofort-Rollback (vor Git Commit):**

```bash
# Dateien wiederherstellen
git checkout .
git clean -fd

# Backups zurückkopieren
cp -r configs_backup_*/* configs/
cp -r src/pkg_backup_*/* src/pkg/
cp -r tests_backup_*/* 19.dashboard_agent/tests/
```

### **Post-Commit-Rollback:**

```bash
# Letzten Commit rückgängig
git revert HEAD

# Oder: Hard Reset (ACHTUNG: Commits gehen verloren)
git reset --hard HEAD~3  # Nur wenn noch nicht gepusht!
```

### **Full Disaster Recovery:**

```bash
# Backup-Tarball extrahieren
cd ..
tar -xzf Gesamtprojekt_backup_$(date +%Y%m%d).tar.gz -C Gesamtprojekt_recovery/
cd Gesamtprojekt_recovery/
# Review + selektiv übernehmen
```

---

## 📞 **ESKALATION**

Bei Problemen:

1. **STOP** – keine weiteren Änderungen
2. **Git Status sichern:** `git status > emergency_status.txt`
3. **Logs sichern:** `cp *.log logs_backup_emergency/`
4. **Backup prüfen:** Stelle sicher, dass Tarball intakt ist
5. **Review mit Architektur-Verantwortlichem:** Siehe `.github/copilot-master-prompt.md`

---

## ✅ **FINAL SIGN-OFF**

**Ich bestätige:**

- [ ] Alle 5 Checklisten-Abschnitte **vollständig** abgearbeitet
- [ ] Alle Backups erstellt und validiert
- [ ] Alle Dry-Runs erfolgreich ohne Errors
- [ ] Feature-Branch erstellt, nicht auf main/master
- [ ] Execution Order strikt befolgt (ARCHIV → venv → tests)
- [ ] Post-Execution Validation erfolgreich
- [ ] opena2 Config zeigt auf ARCHIV/, nicht configs/
- [ ] Tests laufen durch (`pytest tests/`)
- [ ] Git Commits sauber dokumentiert

**Unterschrift:** ****************\_****************
**Datum:** ********\_\_\_********
**Branch:** ********\_\_\_********

---

**Ende der Checklist.**
**Keine Ausführung ohne vollständigen Sign-Off!**
