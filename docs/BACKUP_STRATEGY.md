# 🔄 BACKUP-STRATEGIE FÜR ELION HYPER-DASHBOARD

**Version:** 2025-12-24
**Status:** ✅ PRODUCTION READY
**Komponenten:** Vault (opena11) + PostgreSQL + Configs

---

## 📋 BACKUP-ARCHITEKTUR

```
ELION Backup System (3-Tier Strategy)
│
├─ TIER 1: LOCAL BACKUPS (Daily, 7 Tage Retention)
│  ├── Vault Snapshots (opena11 Raft Storage)
│  ├── PostgreSQL Full Dumps (pg_dump)
│  └── Config Snapshots (Git + Files)
│
├─ TIER 2: CLOUD BACKUPS (Weekly, 90 Tage Retention)
│  ├── S3 Vault Backups (GLACIER Storage)
│  ├── S3 PostgreSQL Backups (GLACIER Storage)
│  └── S3 Config Snapshots (Standard → GLACIER)
│
└─ TIER 3: MONITORING & RECOVERY
   ├── Backup Verification (Checksums)
   ├── Alert System (Failed Backups)
   └── PITR Capability (PostgreSQL Time-Machine)
```

---

## 🔐 KOMPONENTE 1: VAULT BACKUP (opena11)

**Kritikalität:** 🔴 **CRITICAL** - Secrets Management

### Backup-Typ
```
Raft Storage Snapshots (Point-in-Time)
+ Seal Key Metadaten
+ Transit Encryption Status
```

### Backup-Strategie
```
Häufigkeit:  Täglich (2 AM)
Retention:   90 Tage (lokal: 7 Tage, cloud: 90 Tage)
Speicherort: backups/vault/local/ + S3
Größe:       ~500MB - 2GB pro Backup
Typ:         Raft-binary, komprimiert
```

### Recovery-Prozess
```
1. Abrufen des letzten gültigen Snapshots
2. Stop Vault Service
3. Restore über Vault API
4. Verify Seal Status
5. Unlock & Test
```

### Befehle

```bash
# Backup erstellen
bash scripts/backup_vault.sh --backup

# Verfügbare Backups auflisten
bash scripts/backup_vault.sh --list

# Integrität prüfen
bash scripts/backup_vault.sh --verify

# Restore (KRITISCH - Bestätigung erforderlich)
bash scripts/backup_vault.sh --restore /path/to/snapshot.snap
```

---

## 🗄️ KOMPONENTE 2: POSTGRESQL BACKUP (PITR)

**Kritikalität:** 🔴 **CRITICAL** - Datenbank-Integrität

### Backup-Typen

#### 1. Full Backup
```
Typ:        pg_dump (Custom Format, komprimiert)
Häufigkeit: Täglich (2:30 AM)
Retention:  7 Tage lokal, 90 Tage cloud
Größe:      ~1-5GB pro Backup
Kompression: gzip-9 (90% Ratio)
```

#### 2. WAL Archive (Write-Ahead Logs)
```
Typ:        Continuous WAL Archivierung
Häufigkeit: Real-time (alle ~16MB WAL)
Retention:  30 Tage
Zweck:      Point-in-Time Recovery (PITR)
```

### Point-in-Time Recovery (PITR)

**Fähigkeit:** Recovery zu jeder beliebigen Sekunde in den letzten 30 Tagen

```bash
# Restore zu spezifischem Zeitpunkt
bash scripts/backup_postgres.sh --restore "2025-12-24 10:00:00"

# Prozess:
# 1. Finde Latest Full Backup vor der Zeit
# 2. Restore Full Backup
# 3. Replay WAL bis zur gewünschten Zeit
# 4. Verify Datenbank-Integrität
```

### Befehle

```bash
# Full Backup erstellen
bash scripts/backup_postgres.sh --full

# WAL-Logs archivieren
bash scripts/backup_postgres.sh --wal-archive

# Integrität prüfen
bash scripts/backup_postgres.sh --verify

# Verfügbare Backups auflisten
bash scripts/backup_postgres.sh --list

# Point-in-Time Recovery (PITR)
bash scripts/backup_postgres.sh --restore "2025-12-24 10:30:00"
```

---

## 📝 KOMPONENTE 3: CONFIG VERSIONING

**Kritikalität:** 🟡 **HIGH** - Konfigurationskonsistenz

### Backup-Strategie

#### 1. Datei-Snapshots
```
Dateien:    system_baseline.yaml, entitlements.json, .env.*, docker-compose.yml
Häufigkeit: Bei jedem Deployment (oder manuell)
Format:     Gzip-komprimiert (JSON + YAML)
Retention:  90 Tage Snapshots
Checksum:   SHA256 für Integrität
```

#### 2. Git-basiert
```
Commits:    Automatische Config-Commits
Tags:       Release-Tags mit Snapshots
Branches:   config/* für verschiedene Environments
Retention:  Unbegrenzt (Git History)
```

### Kritische Config-Dateien

```yaml
System:
  - system_baseline.yaml        (Master Config)
  - entitlements.json           (User Entitlements)
  - pyproject.toml              (Python Dependencies)

Environment:
  - .env.production             (Prod Settings)
  - .env.staging                (Staging Settings)
  - docker-compose.yml          (Service Definitions)

Agent Configs:
  - */config/*                  (Pro Agent)
  - 10.opena11_unlock/config/   (Vault Config)
  - 19.opena20_dashboard_agent/config/ (Dashboard Config)
```

### Befehle

```bash
# Config-Snapshot erstellen
bash scripts/backup_configs.sh --snapshot

# Snapshot + Git Commit
bash scripts/backup_configs.sh --commit

# Integrität prüfen
bash scripts/backup_configs.sh --verify

# Verfügbare Snapshots auflisten
bash scripts/backup_configs.sh --list

# Restore von Snapshot
bash scripts/backup_configs.sh --restore snapshot_2025-12-24
```

---

## 🎯 MASTER ORCHESTRATOR

Koordiniert alle 3 Komponenten in einem Zyklus

### Full Backup-Zyklus

```bash
bash scripts/backup_orchestrator.sh --full
```

**Ablauf:**
1. ✅ Vault Backup (opena11)
2. ✅ PostgreSQL Backup (PITR-ready)
3. ✅ Config Versioning (Git + Snapshots)
4. ✅ Cloud Upload (S3, GLACIER Storage)
5. ✅ Verification (Checksums, Integrität)
6. ✅ Report & Logging

**Duration:** ~5-10 Minuten (abhängig von DB-Größe)

### Täglicher Zyklus

```bash
bash scripts/backup_orchestrator.sh --daily
```

**Leichtere Version für tägliche Backups:**
- PostgreSQL Full Dump
- Config Versioning
- Keine Cloud Upload (nur wöchentlich)

### Status Check

```bash
bash scripts/backup_orchestrator.sh --status
```

**Output:** JSON mit Status aller Komponenten und Durations

---

## 📊 RETENTION & STORAGE POLICY

| Komponente | Local | Cloud | Total | Strategy |
|------------|-------|-------|-------|----------|
| **Vault** | 7 Tage | 90 Tage | ~150GB | Daily Snapshots |
| **PostgreSQL** | 7 Tage | 90 Tage | ~20-50GB | Full + WAL |
| **Configs** | 90 Tage | 365 Tage | ~5GB | Git + Snapshots |

### Cloud Storage (S3)
```
Vault:      GLACIER (cold storage, minimal cost)
PostgreSQL: GLACIER (after 30 days)
Configs:    STANDARD (quick access)

Lifecycle Policy:
  - 0-30 days:  STANDARD (warm, accessible)
  - 30-90 days: GLACIER (cold, archival)
  - 90+ days:   Expire or Delete (configurable)
```

---

## 🔍 VERIFICATION & INTEGRITY

### Automatische Checks

```bash
bash scripts/backup_orchestrator.sh --verify
```

**Prüft:**
- ✅ Vault Snapshot Integrität
- ✅ PostgreSQL Backup Checksums
- ✅ Config Snapshot Validity
- ✅ File Completeness
- ✅ Space Requirements

### Manuelle Verifikation

```bash
# Vault
bash scripts/backup_vault.sh --verify

# PostgreSQL
bash scripts/backup_postgres.sh --verify

# Configs
bash scripts/backup_configs.sh --verify
```

---

## ⏰ AUTOMATED SCHEDULING (Cron)

```bash
# Zeige Cron-Setup Anleitung
bash scripts/backup_orchestrator.sh --cron-setup
```

**Empfohlener Schedule:**

```bash
# Daily Backup at 2 AM
0 2 * * * cd /path/to/repo && bash scripts/backup_orchestrator.sh --daily >> /var/log/backup.log 2>&1

# Weekly Full Backup on Sunday at 3 AM
0 3 * * 0 cd /path/to/repo && bash scripts/backup_orchestrator.sh --full >> /var/log/backup.log 2>&1

# Monthly Verification on 1st at 4 AM
0 4 1 * * cd /path/to/repo && bash scripts/backup_orchestrator.sh --verify >> /var/log/backup.log 2>&1
```

---

## 🚨 DISASTER RECOVERY PROCEDURES

### Szenario 1: Vault Secrets kompromittiert

```bash
# 1. Backup prüfen
bash scripts/backup_vault.sh --list

# 2. Wähle sicheren Checkpoint
# 3. Restore durchführen
bash scripts/backup_vault.sh --restore backups/vault/local/vault_snapshot_2025-12-23.snap

# 4. Verify
curl http://localhost:8200/v1/sys/health
```

### Szenario 2: Datenbank Corruption

```bash
# 1. Letzte gültigen Backup auswählen
bash scripts/backup_postgres.sh --list

# 2. Point-in-Time Recovery
bash scripts/backup_postgres.sh --restore "2025-12-24 10:00:00"

# 3. Verify
psql -c "SELECT COUNT(*) FROM your_table;"
```

### Szenario 3: Falsche Config-Änderung

```bash
# 1. Verfügbare Snapshots auflisten
bash scripts/backup_configs.sh --list

# 2. Restore von bekanntem guten Zustand
bash scripts/backup_configs.sh --restore snapshot_2025-12-23

# 3. Restart Services
docker-compose restart
```

---

## 📞 MONITORING & ALERTS

### Backup-Health Dashboard

```bash
# Status JSON (für Monitoring-Integration)
cat backups/.backup_status.json | jq '.'

# Output-Beispiel:
{
  "start_time": "2025-12-24T02:00:00Z",
  "status": "success",
  "components": {
    "vault": {"status": "success", "duration": 120},
    "postgres": {"status": "success", "duration": 240},
    "configs": {"status": "success", "duration": 30},
    "cloud_upload": {"status": "success", "duration": 180}
  }
}
```

### Alert-Bedingungen

- ❌ Backup fehlgeschlagen (Status != success)
- ❌ Checksum-Fehler (Integrität)
- ❌ Disk-Space kritisch (< 10% verfügbar)
- ⚠️ Backup dauert länger als 15 Minuten
- ⚠️ Keine Backup für 48 Stunden

---

## 📚 BEST PRACTICES

1. **Regelmäßige Recovery-Tests**
   ```bash
   # Monatlich PITR testen (in Staging!)
   bash scripts/backup_postgres.sh --restore "before 1 day"
   ```

2. **Offsite-Backups**
   - Vault: S3 mit GLACIER (separate AWS Account)
   - PostgreSQL: S3 mit GLACIER
   - Configs: Git-basiert (GitHub mit 2FA)

3. **Separate Credentials**
   - BACKUP_S3_BUCKET != Production S3
   - DB_PASSWORD != other passwords
   - AWS Keys: Separate IAM Roles

4. **Retention-Balancing**
   - Kurz (7d) für schnelle Recovery
   - Mittelfristig (90d) für Audit-Trail
   - Langfristig (Archival) für Compliance

5. **Documentaton & Runbooks**
   - Backup-Prozeduren dokumentieren
   - Recovery-Prozeduren testen
   - Team Training durchführen

---

## 🔐 SECURITY CONSIDERATIONS

### Encryption

- ✅ Vault Backup: Sealed (Auto-Unseal mit Transit)
- ✅ PostgreSQL Backup: gzip (nicht encrypted) → nutze S3-side encryption
- ✅ Config Snapshots: No sensitive data (separate secrets in Vault)

### Access Control

```bash
# Restrict Backup Access
chmod 700 backups/                # Only owner
chmod 600 backups/**/*.snap       # No group/other
chmod 600 backups/**/*.sql.gz     # No group/other

# IAM (S3 Cloud)
# - Separate IAM user for backups
# - Limited to backup S3 bucket
# - No delete permissions
```

---

## 📈 MONITORING INTEGRATION

### Prometheus Metrics

```yaml
# Beispiel-Exporter
backup_last_timestamp{component="vault"}
backup_duration_seconds{component="postgres"}
backup_size_bytes{component="configs"}
backup_status{component="all", status="success"}
```

### Grafana Dashboard

- Backup Status (✅/❌)
- Backup Duration Trends
- Storage Usage Over Time
- Recovery Time Objective (RTO)
- Recovery Point Objective (RPO)

---

## 📞 SUPPORT & TROUBLESHOOTING

**Problem:** Vault Backup schlägt fehl
```bash
# 1. Prüfe Vault Health
curl http://localhost:8200/v1/sys/health | jq '.'

# 2. Prüfe Token
echo $VAULT_TOKEN

# 3. Logs
tail -100 backups/logs/vault_*.log
```

**Problem:** PostgreSQL Backup zu langsam
```bash
# 1. Prüfe DB Size
psql -c "SELECT pg_size_pretty(pg_database_size('postgres'));"

# 2. Prüfe Disk I/O
iostat -x 1 10

# 3. Nutze inkrementelle Backups
bash scripts/backup_postgres.sh --incremental
```

**Problem:** Disk-Space voll
```bash
# Cleanup alte Backups
find backups/ -mtime +90 -delete

# Prüfe Größen
du -sh backups/*/
```

---

**Status:** ✅ PRODUCTION READY
**Last Updated:** 2025-12-24
**Version:** 1.0.0-stable
