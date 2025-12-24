# 🔙 QUICK REFERENCE: Hybrid Rollback Strategy

**Version:** v2025.12.24-tracing
**PR:** #78
**Last Updated:** 2025-12-24

---

## ⚡ EMERGENCY ROLLBACK (< 2 minutes)

### Fastest Option: Automatic Hybrid Rollback

```bash
cd /path/to/repo
bash bin/merge_finalize.sh --rollback
```

**Das Script wird:**
1. ✅ Versuchen, File-based Rollback zu verwenden (< 1 Minute)
2. ⚠️ Fallback zu Tag-based Rollback, wenn Checkpoint fehlt (< 2 Minuten)
3. ✅ Automatisch zu Git pushen

---

## 🔧 OPTION 1: File-based Rollback (Schnell)

**Best für:** Lokale schnelle Recovery

```bash
# 1. Checkpoint auslesen
cat .git/merge_checkpoint
# Output: main:0516dede

# 2. Rollback ausführen
COMMIT=$(cat .git/merge_checkpoint | cut -d: -f2)
git reset --hard $COMMIT

# 3. Push
git push origin main --force

# 4. Verifikation
git log -1 --oneline
```

**Voraussetzungen:**
- ✅ Checkpoint-Datei vorhanden
- ✅ Lokaler Zugriff auf Repository
- ✅ Push-Berechtigung

---

## 🔐 OPTION 2: Tag-based Rollback (Sicher)

**Best für:** Audit-Trail, Compliance, Production

```bash
# 1. Liste verfügbare Tags
git tag -l | grep "v2025"
# Output:
# v2025.12.24-tracing
# v2025.12.24-tracing.backup

# 2. Rollback zu Backup-Tag
git reset --hard v2025.12.24-tracing.backup

# 3. Push
git push origin main --force

# 4. Verifikation
git describe --tags
# Output: v2025.12.24-tracing.backup-...-...
```

**Voraussetzungen:**
- ✅ Git Tags auf Remote verfügbar
- ✅ Push-Berechtigung
- ✅ GitHub-Zugriff

---

## 📋 WHEN TO USE WHICH OPTION

| Situation | Option | Befehl |
|-----------|--------|--------|
| **Unbekannt** | Hybrid (Auto) | `bash bin/merge_finalize.sh --rollback` |
| **Schnell & lokal** | File-based | `git reset --hard $(cat .git/merge_checkpoint \| cut -d: -f2)` |
| **Audit-sicher** | Tag-based | `git reset --hard v2025.12.24-tracing.backup` |
| **Automatisch** | Hybrid | Hybrid versucht File → Tag |

---

## 🚨 MANUAL STEP-BY-STEP (Wenn alle Optionen fehlschlagen)

```bash
# 1. Backup der aktuellen Probleme
mkdir -p logs/emergency-rollback-$(date +%s)
git log --oneline -20 > logs/emergency-rollback-$(date +%s)/commits.log
docker-compose logs > logs/emergency-rollback-$(date +%s)/docker.log 2>&1

# 2. Finde letzten stabilen Punkt
git log --oneline | head -20  # Zeige letzte 20 Commits

# 3. Wähle einen stabilen Commit (ACHTUNG: Wähle mit Bedacht!)
# Normalerweise: Der Commit VOR dem Merge
STABLE_COMMIT="0516dede"  # Ersetze mit richtigem Hash

# 4. Reset
git reset --hard $STABLE_COMMIT
git push origin main --force

# 5. Verifikation
git log -1 --oneline
curl http://localhost:12349/health
```

---

## ✅ VERIFICATION AFTER ROLLBACK

```bash
# 1. Git Status
git status           # Should be: On branch main, nothing to commit
git describe --tags  # Should show OLD tag

# 2. Application Health
curl http://localhost:12349/health    # Dashboard
curl http://localhost:12350/health    # Workflow

# 3. Database
psql -U postgres -c "SELECT 'OK';"

# 4. Logs
tail -20 logs/*/error.log             # Should be empty OR old errors
docker-compose logs | grep ERROR       # No new errors

# 5. Services
docker-compose ps                      # All UP
```

---

## 🔍 TROUBLESHOOTING ROLLBACK

### Problem: "fatal: Not a valid ref or SHA"

```bash
# Cause: Commit hash tidak valid
# Fix:
git log --oneline | head -5  # Ambil commit valid baru
VALID_COMMIT="<hash>"
git reset --hard $VALID_COMMIT
```

### Problem: "error: Your local changes would be overwritten"

```bash
# Cause: Ada uncommitted changes
# Fix:
git stash                    # Simpan changes
git reset --hard <commit>   # Reset
git stash pop               # Restore (optional)
```

### Problem: "permission denied: origin/main"

```bash
# Cause: Tidak punya push permission
# Fix: Gunakan correct credentials atau ask team lead
# Untuk sekarang, hanya reset locally:
git reset --hard <commit>   # Jangan push
# Hubungi DevOps untuk force-push
```

### Problem: ".git/merge_checkpoint tidak ada"

```bash
# Fallback ke Tag-based
git reset --hard v2025.12.24-tracing.backup
git push origin main --force
```

---

## 🧭 CHECKPOINT FILE FORMAT

```
Location: .git/merge_checkpoint
Format:   BRANCH:COMMIT_HASH
Example:  main:0516dede

Extrahieren:
  Branch: cat .git/merge_checkpoint | cut -d: -f1  # main
  Commit: cat .git/merge_checkpoint | cut -d: -f2  # 0516dede
```

---

## 📊 ROLLBACK DECISION TREE

```
┌─────────────────────────────────┐
│ Rollback Required?              │
└──────────────┬──────────────────┘
               │ YES
               ▼
┌──────────────────────────────────────┐
│ Which severity?                      │
├───────┬────────────────┬────────────┤
│ LOW   │ MEDIUM/HIGH    │ CRITICAL   │
│ (Test)│ (Production)   │ (Prod Down)│
├───────┼────────────────┼────────────┤
│       │                │            │
▼       ▼                ▼            ▼
Tag-b   Hybrid-Auto    File-based  Manual
(Safe)  (Best)         (Fast)      (Team)
  │       │              │           │
  │       │              │       [ALERT]
  │       ▼              ▼       TEAM
  │   Option 3        Option 1   LEAD
  │       │              │
  └───────┴──────────────┘
          │
          ▼
    [git reset/push]
          │
          ▼
    [VERIFY HEALTH]
          │
      ✅/❌
```

---

## 📞 WHEN TO CALL FOR HELP

| Issue | Action | Contact |
|-------|--------|---------|
| Rollback fails | Stop & wait | DevOps Lead |
| Multiple DBs affected | Stop & wait | DBA |
| Application won't start | Rollback + Monitor | On-Call Eng |
| Unsure which commit | Consult log | Team Lead |
| Need force-push | Provide context | Git Admin |

---

## 🔗 RELATED RESOURCES

- **Merge Script:** `bin/merge_finalize.sh` (auto rollback available)
- **Deployment Guide:** `docs/DEPLOYMENT_CHECKLIST.md`
- **Hybrid Strategy Docs:** Below ⬇️

---

## 📚 HYBRID STRATEGY EXPLANATION

### Was ist Hybrid?

```
Hybrid = File-based + Tag-based
       = Schnelligkeit + Sicherheit
       = Best of Both Worlds
```

### Wie funktioniert es?

1. **File-based (schnell):**
   - Checkpoint vor Merge gespeichert
   - Einfach zu lesen: `cat .git/merge_checkpoint`
   - Rollback: < 1 Minute

2. **Tag-based (sicher):**
   - Audit-Trail in Git Tags
   - Reproduzierbar weltweit
   - Selbsterklärend durch Tag-Namen

3. **Hybrid (automatic):**
   - Versuche zuerst File → Tag
   - Fallback automatisch
   - Script wählt beste Methode

### Vorteile

| Aspect | Benefit |
|--------|---------|
| Speed | < 2 minutes total |
| Safety | Audit trail preserved |
| Redundancy | 2 independent methods |
| Automation | Script handles it |
| Recovery | 100% reproducible |

---

**Last Tested:** 2025-12-24
**Status:** ✅ VERIFIED WORKING
**Maintainer:** DevOps / Release Team
