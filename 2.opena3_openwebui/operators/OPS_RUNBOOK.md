# 🚀 PORTIER 3.0 - Operations Runbook
**Enterprise Multi-Agent Intelligence Platform**

Version: 3.0.0
Status: Production Ready
Last Updated: 24. November 2025

---

## 📋 Inhaltsverzeichnis

1. [Quick Start](#quick-start)
2. [System Architecture](#system-architecture)
3. [Stack Operations](#stack-operations)
4. [Health Monitoring](#health-monitoring)
5. [Troubleshooting](#troubleshooting)
6. [Backup & Recovery](#backup--recovery)
7. [Scaling Guide](#scaling-guide)
8. [Security Operations](#security-operations)

---

## 🎯 Quick Start

### System starten (Produktion)

```bash
# 1. Alle Services starten
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui
bin/ops.sh start

# 2. Status überprüfen
bin/ops.sh verify

# 3. Dashboard öffnen
xdg-open http://127.0.0.1:12349/dashboard

# 4. E2E Test
curl -X POST http://127.0.0.1:12349/api/e2e
```

### System stoppen

```bash
bin/ops.sh stop
```

### System Status

```bash
bin/ops.sh status
```

---

## 🏗️ System Architecture

### Services Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                    PORTIER 3.0 STACK                        │
├─────────────────────────────────────────────────────────────┤
│ CORE SERVICES (Host-basiert):                               │
│ ├─ opena1        (Port 12345) | Koordinator                 │
│ ├─ opena2        (Port 12346) | Archivator                  │
│ ├─ opena3        (Port 12347) | Gateway                     │
│ └─ opena20       (Port 12349) | Dashboard Agent             │
│                                                              │
│ INFRASTRUCTURE (Docker/Host):                               │
│ ├─ OpenWebUI     (Port 3000)  | LLM WebUI                   │
│ ├─ Ollama        (Port 11434) | LLM Inference               │
│ └─ Agent Cluster (opena4-19)   | Future Scaling             │
│                                                              │
│ OBSERVABILITY:                                              │
│ ├─ Prometheus    (Port 9090)  | Metrics (Phase 17)          │
│ ├─ Grafana       (Port 3001)  | Dashboards (Phase 17)       │
│ └─ Logs          (stdout/file)| Structured Logging          │
└─────────────────────────────────────────────────────────────┘
```

### Port Mapping (Enterprise)

| Service | Port | Protocol | Status | Owner |
|---------|------|----------|--------|-------|
| opena1 (Koordinator) | 12345 | HTTP | ✅ Live | Core |
| opena2 (Archivator) | 12346 | HTTP | ✅ Live | Core |
| opena3 (Gateway) | 12347 | HTTP | ✅ Live | Core |
| opena20 (Dashboard) | 12349 | HTTP | ✅ Live | Monitor |
| OpenWebUI | 3000 | HTTP | 🔄 Optional | UI |
| Ollama | 11434 | HTTP | 🔄 Optional | LLM |
| Prometheus | 9090 | HTTP | ⏳ Phase 17 | Monitor |
| Grafana | 3001 | HTTP | ⏳ Phase 17 | Monitor |

---

## 🎛️ Stack Operations

### 1. Services Starten

```bash
# Koordinator starten
python3 LocalAgent-Pro/opena1/main.py &

# Archivator starten
python3 LocalAgent-Pro/opena2/main.py &

# Gateway starten
python3 LocalAgent-Pro/opena3/main.py &

# Dashboard starten
python3 LocalAgent-Pro/web_dashboard.py &

# OpenWebUI starten (Docker)
docker-compose -f LocalAgent-Pro/docker-compose.yml up -d openwebui

# Ollama starten (Docker)
docker-compose -f LocalAgent-Pro/docker-compose.yml up -d ollama
```

### 2. Services Stoppen

```bash
# Mit Signal (graceful shutdown)
pkill -TERM -f "opena1|opena2|opena3|web_dashboard"

# Mit Force
pkill -9 -f "opena1|opena2|opena3|web_dashboard"

# Docker Services stoppen
docker-compose -f LocalAgent-Pro/docker-compose.yml down
```

### 3. Services Neu starten

```bash
# Einzelner Service
pkill -f opena1 && sleep 2 && python3 LocalAgent-Pro/opena1/main.py &

# Alle Core Services
pkill -f "opena[123]" && sleep 3 && \
python3 LocalAgent-Pro/opena1/main.py & \
python3 LocalAgent-Pro/opena2/main.py & \
python3 LocalAgent-Pro/opena3/main.py &
```

### 4. Service Logs

```bash
# Live Logs anzeigen
tail -f LocalAgent-Pro/logs/opena1.log
tail -f LocalAgent-Pro/logs/opena2.log
tail -f LocalAgent-Pro/logs/opena3.log

# Letzten 50 Zeilen
tail -50 LocalAgent-Pro/logs/opena1.log

# Mit Filterung
grep "ERROR" LocalAgent-Pro/logs/opena1.log
grep "2025-11-24" LocalAgent-Pro/logs/*.log | head -100
```

---

## 💚 Health Monitoring

### 1. Endpoint Health Checks

```bash
# Koordinator
curl -s http://127.0.0.1:12345/health | jq .
# Expected: { "status": "online", "service": "opena1", ... }

# Archivator
curl -s http://127.0.0.1:12346/health | jq .

# Gateway
curl -s http://127.0.0.1:12347/health | jq .

# Dashboard
curl -s http://127.0.0.1:12349/health | jq .
```

### 2. Dashboard Status

```bash
# Alle Services auf einen Blick
curl -s http://127.0.0.1:12349/api/status | jq .

# Metriken
curl -s http://127.0.0.1:12349/api/metrics | jq .

# Tool Verfügbarkeit
curl -s http://127.0.0.1:12349/api/tools | jq .
```

### 3. System Metrics

```bash
# CPU/Memory Auslastung
ps aux | grep opena | awk '{print $3, $4, $11}' | column -t

# Offene Ports
netstat -tuln | grep -E "12345|12346|12347|12349|3000|11434"

# Prozess Status
pgrep -a "opena[123]|web_dashboard"
```

### 4. Last 10 Archivator Safepoints

```bash
curl -s http://127.0.0.1:12346/archiv/last?n=10 | jq '.'
```

---

## 🔧 Troubleshooting

### Problem: Service läuft nicht

```bash
# 1. Prüfe ob Port belegt ist
lsof -i :12345  # für opena1
lsof -i :12346  # für opena2
lsof -i :12347  # für opena3
lsof -i :12349  # für Dashboard

# 2. Zombie-Prozesse aufräumen
pkill -9 python3 && sleep 2

# 3. Port freigeben
fuser -k 12345/tcp

# 4. Service neustarten
python3 LocalAgent-Pro/opena1/main.py
```

### Problem: High Memory Usage

```bash
# Memory Top 5
ps aux --sort=-%mem | head -6

# Spezifisch für opena Services
ps aux | grep opena | awk '{print $11, $6}' | sort -k2 -rn

# Memory Limit setzen (systemd)
systemctl set-property opena1.service MemoryLimit=512M
```

### Problem: Netzwerk-Timeouts

```bash
# Connectivity Check
curl -v http://127.0.0.1:12345/health

# TCP Verbindung testen
nc -zv 127.0.0.1 12345

# Firewall Rules
sudo iptables -L -n | grep -E "12345|12346|12347|12349"
```

### Problem: Database Lock

```bash
# SQLite Locks finden
lsof | grep .db

# Prozesse beenden
pkill -f "opena2"
sleep 3
# Neustarten
python3 LocalAgent-Pro/opena2/main.py &
```

---

## 💾 Backup & Recovery

### 1. Archivator Backup

```bash
# Safepoints exportieren
curl -s http://127.0.0.1:12346/archiv/export > backup_$(date +%Y%m%d_%H%M%S).json

# Safepoints komprimieren
tar -czf archiv_backup_$(date +%Y%m%d).tar.gz archivp_store/

# Mit Verification
curl -s http://127.0.0.1:12346/archiv/verify
```

### 2. Database Backup

```bash
# Dateien sichern
cp LocalAgent-Pro/logs/*.db ~/backups/

# Mit Timestamp
for db in LocalAgent-Pro/logs/*.db; do
  cp "$db" ~/backups/"$(basename $db).$(date +%s)"
done

# Größe überprüfen
du -sh ~/backups/
```

### 3. Recovery Prozess

```bash
# 1. Services stoppen
bin/ops.sh stop

# 2. Backup-Daten wiederherstellen
cp ~/backups/*.db LocalAgent-Pro/logs/

# 3. Services neustarten
bin/ops.sh start

# 4. Konsistenz verifizieren
curl -s http://127.0.0.1:12346/health | jq .
```

---

## 📈 Scaling Guide

### Phase 4: Agent-Cluster (opena4-opena19)

#### Option 1: Template-basiert

```bash
# Service Template kopieren
cp -r LocalAgent-Pro/opena3 LocalAgent-Pro/opena4

# Config anpassen
sed -i 's/12347/12348/g' LocalAgent-Pro/opena4/config.json
sed -i 's/opena3/opena4/g' LocalAgent-Pro/opena4/config.json

# Starten
python3 LocalAgent-Pro/opena4/main.py &
```

#### Option 2: Automatisiert

```bash
# Script zur Auto-Generation
python3 scripts/generate_scalable_services.py \
  --agents 4-19 \
  --base-port 12348 \
  --template LocalAgent-Pro/opena3
```

#### Health Check für neue Agents

```bash
# Loop über alle neuen Agents
for port in $(seq 12348 12364); do
  curl -s http://127.0.0.1:$port/health || echo "Port $port offline"
done
```

---

## 🔐 Security Operations

### 1. Bearer Token Management

```bash
# Tokens auflisten
cat LocalAgent-Pro/config/bearer_tokens.txt

# Neuen Token generieren
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Token rotieren (Phase 18)
# TODO: Implementierung in Phase 18
```

### 2. Service Key Rotation

```bash
# Keys sichern
cp LocalAgent-Pro/config/*.key ~/secure_backup/

# Neue Keys generieren
python3 LocalAgent-Pro/tools/generate_keys.py

# Keys deploy
scp ~/secure_backup/*.key prod:/etc/portier/
```

### 3. Audit Logging

```bash
# Alle API Calls auflisten
grep "API" LocalAgent-Pro/logs/*.log | tail -100

# Fehler tracken
grep "ERROR\|Exception" LocalAgent-Pro/logs/*.log

# Archivator Zugriffe
curl -s http://127.0.0.1:12346/audit/logs | jq .
```

### 4. Firewall Rules (ufw)

```bash
# Ports erlauben
sudo ufw allow 12345/tcp
sudo ufw allow 12346/tcp
sudo ufw allow 12347/tcp
sudo ufw allow 12349/tcp

# Nur localhost
sudo ufw allow from 127.0.0.1 to any port 12345
sudo ufw allow from 127.0.0.1 to any port 12346

# Status
sudo ufw status verbose
```

---

## 📊 Monitoring-Roadmap

### Phase 17: Prometheus & Grafana

```bash
# Prometheus starten (zukünftig)
docker run -d -p 9090:9090 prom/prometheus

# Grafana starten (zukünftig)
docker run -d -p 3001:3000 grafana/grafana

# Metriken exportieren
curl http://127.0.0.1:12349/metrics
```

### Phase 18: Advanced Observability

- [ ] Distributed Tracing (Jaeger)
- [ ] Custom Metrics (Latency, Throughput)
- [ ] Alert Rules
- [ ] Dashboards

### Phase 19-20: AI-powered Ops

- [ ] Auto-healing
- [ ] Predictive Scaling
- [ ] Anomaly Detection

---

## 🎯 Checklisten

### Daily Operations

- [ ] Health Check aller Services durchführen
- [ ] Logs auf Errors prüfen
- [ ] Disk Space überprüfen
- [ ] Backup-Status verifizieren

### Weekly Operations

- [ ] Database Maintenance
- [ ] Token Rotation
- [ ] Safepoint Export
- [ ] Performance Report generieren

### Monthly Operations

- [ ] Full System Backup
- [ ] Disaster Recovery Test
- [ ] Security Audit
- [ ] Capacity Planning

---

## 📞 Support & Escalation

### Service Issues

1. **Lokales Debugging**: Logs anschauen
2. **Health Check**: `curl /health`
3. **Port Check**: `lsof -i :<port>`
4. **Restart**: Service neu starten
5. **Escalation**: Senior Ops Engineer

### Critical Issues

- **System Down**: Sofort `bin/ops.sh start`
- **Data Corruption**: Recovery-Prozess starten
- **Security Breach**: Alle Services stoppen, Senior Lead kontaktieren

---

**Generated**: 24. November 2025
**Version**: PORTIER 3.0.0
**Status**: ✅ Production Ready
