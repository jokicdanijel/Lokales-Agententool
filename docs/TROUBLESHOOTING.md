# Troubleshooting Guide

## Dashboard antwortet 401

**Problem:** HTTP 401 bei API-Aufrufen

**Ursachen:**

- `.env` Token fehlt oder ist leer
- Token-Format ungültig
- Authorization Header nicht gesendet

**Lösung:**

```bash
# Token prüfen
cat .env

# Bei leerer .env neu generieren
bin/env_bootstrap.sh

# In curl korrekt verwenden
TOK=$(cat .env)
curl -H "Authorization: Bearer $TOK" http://127.0.0.1:12349/api/status/all
```

---

## Archivator (opena2) antwortet 404

**Problem:** HTTP 404 bei `/store/archivp`

**Ursachen:**

- opena2 läuft nicht
- Port 12345 falsch
- Falcher Pfad

**Lösung:**

```bash
# Port prüfen
bin/check_ports.sh | grep 12345

# Service starten
bin/ops.sh start

# Logs prüfen
tail -f logs/opena2.nohup.log
```

---

## OpenWebUI nicht erreichbar

**Problem:** HTTP 502/503 bei OpenWebUI-Endpunkten

**Ursachen:**

- OpenWebUI läuft nicht (Port 8080)
- Agent (opena3) läuft nicht (Port 12347)
- Netzwerk-Fehler

**Lösung:**

```bash
# Status prüfen
bin/openwebui_status.sh

# OpenWebUI in 2.openwebui/ starten
cd 2.openwebui && docker-compose up -d

# opena3 Agent starten
cd 19.dashboard_agent
bin/start_opena3.sh

# Logs prüfen
tail -f logs/opena3.nohup.log
```

---

## Port bereits in Verwendung

**Problem:** "Address already in use"

**Ursache:** Service läuft bereits oder falscher Port

**Lösung:**

```bash
# Alle Services stoppen
bin/ops.sh stop

# Ports prüfen
bin/check_ports.sh

# Ggf. Process manuell killen
lsof -i :12347  # opena3 Port
kill -9 <PID>

# Neu starten
bin/ops.sh start
```

---

## Token ungültig

**Problem:** HTTP 403 "invalid token"

**Ursache:** Token abgelaufen oder falsch

**Lösung:**

```bash
# Neuen Token generieren
bin/env_bootstrap.sh

# Agents neu registrieren
bin/ops.sh agents:register
```

---

## Logs ansehen

**Schneller Zugriff:**

```bash
# Alle Logs
bin/ops.sh logs

# Live-Follow
bin/log_tail.sh

# Spezifische Service
tail -f logs/opena3.nohup.log
tail -f logs/dashboard_runtime.log
```

---

## Health-Checks

```bash
# Dashboard
bin/ops.sh health

# All Agents
bin/ops.sh status | jq .

# OpenWebUI
bin/openwebui_status.sh
```

---

## SSE Events nicht ankommend

**Problem:** Live-Events funktionieren nicht

**Lösung:**

```bash
# SSE-Bus prüfen
curl -N http://127.0.0.1:12349/api/events/live

# Sollte "heartbeat" Events ausgeben (alle 15s)
```

---

## Agent registriert sich nicht

**Problem:** Agent sichtbar aber Status immer "null"

**Lösung:**

```bash
# Agent direkt prüfen
curl http://127.0.0.1:12344/health

# Falls 200: registrieren
bin/ops.sh agents:register

# Status neu laden
bin/ops.sh status | jq .
```
