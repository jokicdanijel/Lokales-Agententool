# 🚀 Deployment Checklist für v2025.12.24-tracing

**Release:** v2025.12.24-tracing
**PR:** #78 (Tracing Integration)
**Status:** PRODUCTION READY ✅
**Rollback Strategy:** Hybrid (Tag-based + File-based)

---

## PRE-DEPLOYMENT VERIFICATION

### ✅ Git-Status

```bash
git status  # Clean working tree
git describe --tags  # v2025.12.24-tracing
```

### ✅ requirements.txt & Dependencies

```bash
ls -la requirements.txt  # Sollte existieren (1016 Bytes)
python3 -m pip check    # Keine Konflikte
```

### ✅ CI/CD Workflow

```bash
python3 scripts/preflight_check.py  # Alle 9 Checks ✅
```

### ✅ .gitignore Validierung

```bash
# Prüfe dass folgende ignoriert werden:
- logs/
- *.log
- preflight_report.json
- .git/merge_checkpoint
- MERGE_HEAD, MERGE_MSG, MERGE_STATE
```

---

## ROLLBACK PROCEDURES (Hybrid Strategy)

### 🔙 OPTION 1: File-based Rollback (Schnell, < 2 Minuten)

```bash
# Checkpoint prüfen
cat .git/merge_checkpoint
# Output: main:0516dede

# Rollback ausführen
git reset --hard $(cat .git/merge_checkpoint | cut -d: -f2)
git push origin main --force

echo "✅ Rollback abgeschlossen"
```

**Wann verwenden:**

- Lokale schnelle Recovery erforderlich
- Einfache Revertierung

---

### 🔙 OPTION 2: Tag-based Rollback (Sicher, Audit-Trail)

```bash
# Backup-Tag verwenden (reproduzierbar)
git reset --hard v2025.12.24-tracing.backup
git push origin main --force

# Verifikation
git describe --tags
```

**Wann verwenden:**

- Audit-Trail erforderlich
- Production-kritisch
- Multi-Team Rollback

---

### 🔙 OPTION 3: Automatischer Hybrid-Rollback (Empfohlen)

```bash
# Script versucht zuerst File-based, fallback zu Tag-based
bash bin/merge_finalize.sh --rollback
```

**Output:**

```
✅ File-based Rollback zu main @ 0516dede
ODER
✅ Tag-based Rollback zu v2025.12.24-tracing.backup
```

---

## TROUBLESHOOTING

### ❌ Checkpoint-Datei fehlt

```bash
# Manuelle Erstellung
echo "main:$(git rev-parse HEAD)" > .git/merge_checkpoint

# Nutze stattdessen Tag-based Rollback
git reset --hard v2025.12.24-tracing.backup
```

### ❌ opena20 startet nicht

```bash
# Sofort Rollback ausführen
bash bin/merge_finalize.sh --rollback

# Services neu starten
docker-compose down
docker-compose up -d

# Health-Check
curl http://localhost:12349/health
```

### ❌ CI/CD Workflow schlägt fehl

```bash
# Verbose Preflight-Output
python3 scripts/preflight_check.py -v

# Rollback
git reset --hard v2025.12.24-tracing.backup
git push origin main --force
```

---

## POST-DEPLOYMENT VERIFICATION

- [ ] `curl http://localhost:12349/health` → 200 OK
- [ ] `curl http://localhost:12350/health` → 200 OK
- [ ] Jaeger Dashboard: `curl http://localhost:16686` → verfügbar
- [ ] Logs sauber: `tail -100 logs/* | grep -i error` → keine Errors
- [ ] Keine unerwarteten MERGE_HEAD-Dateien im Repo

---

## Hybrid Rollback Strategy erklärt

| Methode        | Vorteil                     | Nachteil                | Best For     |
| -------------- | --------------------------- | ----------------------- | ------------ |
| **File-based** | Lokal, schnell, < 1 Min     | Nur auf dieser Maschine | Lokale Tests |
| **Tag-based**  | Audit-Trail, reproduzierbar | Etwas langsamer         | Production   |
| **Hybrid**     | Beste Lösung, automatisch   | -                       | **Go-Live**  |

---

**Status:** ✅ APPROVED FOR PRODUCTION
**Letzte Aktualisierung:** 2025-12-24
