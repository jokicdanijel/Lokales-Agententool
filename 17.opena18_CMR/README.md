# 🤖 opena18 - CRM / Local Archiv

**Agent-ID:** `opena18`  
**Port:** 12364  
**Kürzel:** `crmp`  
**Version:** 3.0  
**Status:** 🟡 **Planned** (PORTIER 3.0 Architecture Ready)  
**Letzte Aktualisierung:** 29. November 2025

---

## 📖 Überblick

**opena18** ist der **CRM / Local Archiv** im ELION Hyper-Dashboard System - ein spezialisierter Agent für die PORTIER 3.0 Multi-Agent-Architektur.

### 🎯 PORTIER 3.0 Integration

opena18 ist architektonisch vorbereitet für die PORTIER 3.0 Integration:

- ✅ **Option-2-Flow Ready:** OpenAI → opena1 → opena2 → kordp → opena18
- ✅ **Port Policy Compliant:** Port 12364 (Backend-Range 12344-12399)
- ✅ **Safepoint Integration:** Automatische Archivierung via opena2
- ✅ **Bearer Token Security:** Authentifizierung vorbereitet
- 🟡 **Implementation Status:** Ordnerstruktur vorhanden, Code pending

### 🚀 Zukünftige Features

- 🔄 **Multi-Agent Coordination:** Integration mit anderen Agenten
- 📊 **Real-time Monitoring:** Dashboard-Integration (opena20)
- 🛡️ **Security First:** Vollständige Bearer Token Implementation
- ⚡ **High Performance:** Async FastAPI Architecture

---

## 📡 API-Endpoints (Planned)

### `GET /health`

Health-Check des Agents.

```bash
curl http://127.0.0.1:12364/health | jq .
```

### `POST /invoke`

Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12364/invoke \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "service_action",
    "params": {...}
  }'
```

---

## 🚀 Quick Start (When Implemented)

### Agent starten

```bash
cd 17.opena18_CMR
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12364/health | jq .
```

---

## 🔗 Integration mit PORTIER 3.0

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena18",
    "endpoint": "http://127.0.0.1:12364",
    "program_target": "crmp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "crmp",
    "action": "service_action",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur (Planned)

```txt
17.opena18_CMR/
├── main.py                  # FastAPI Agent Entry Point (planned)
├── config.py                # Konfiguration (planned)
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script (planned)
├── tests/
│   └── test_opena18.py  # Unit-Tests (planned)
└── README.md                # Diese Datei
```

---

## 🔐 Sicherheit

- ✅ **Bearer-Token** für alle Endpoints außer `/health`
- ✅ **Port-Policy** Enforcement (12344-12399)
- ✅ **Strict JSON** (Pydantic `extra="forbid"`)
- ✅ **Option-2-Flow** Compliance

---

## 🧪 Testing (Planned)

```bash
# Unit-Tests
pytest tests/test_opena18.py -v

# Health-Check
curl http://127.0.0.1:12364/health

# Integration-Test via Portier
python3 ../scripts/test_opena18_integration.py
```

---

## 📊 Monitoring (Planned)

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12364/metrics
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** Danijel Jokic (ELION Team)  
**Letzte Aktualisierung:** 29. November 2025  
**Status:** 🟡 **Architecture Ready** (Implementation Pending)

## 📖 Überblick

**opena18** ist der **CRM Agent** - Customer Relationship Management für Kontakte, Organisationen, Deals und Aktivitäten.

### Kernfunktionen

- 📇 **Contact Management** - Kontakte erstellen/bearbeiten/löschen (CRUD)
- 🏢 **Organization Management** - Organisationen verwalten (Industry, Size, Website)
- 💰 **Deal Pipeline** - Deals mit Stages (Lead, Qualified, Proposal, Negotiation, Closed)
- 📝 **Activity Tracking** - Calls, Emails, Meetings, Notes, Tasks loggen
- 🔍 **Global Search** - Volltextsuche über alle Entities (Contacts, Orgs, Deals)
- 🔗 **Relations** - Contacts ↔ Organizations ↔ Deals ↔ Activities

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena18 (12363) ← Dieser Agent
    ↓
OpenA2 (12345) → Portier (12344)
    ↓
Client/UI
```

**Integration:** Vollständig in Option-2-Flow integriert.

---

## 📡 API-Endpoints

### `GET /health`
Health-Check des Agents.

```bash
curl http://127.0.0.1:12363/health | jq .
```

**Response:**
```json
{
  "status": "ok",
  "service": "opena18",
  "kuerzel": "crmp",
  "port": 12363,
  "uptime_seconds": 303.19,
  "total_contacts": 2,
  "total_organizations": 1,
  "total_deals": 1,
  "total_activities": 1
}
```

### `POST /contacts`
Kontakt erstellen.

```bash
curl -X POST http://127.0.0.1:12363/contacts \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Max",
    "last_name": "Mustermann",
    "email": "max.mustermann@example.com",
    "phone": "+49 123 456789",
    "position": "CEO",
    "tags": ["vip", "decision-maker"]
  }'
```

### `PUT /contacts/{contact_id}`
Kontakt aktualisieren.

```bash
curl -X PUT http://127.0.0.1:12363/contacts/<contact_id> \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "position": "Managing Director",
    "phone": "+49 987 654321"
  }'
```

### `GET /contacts`
Kontakte auflisten.

```bash
curl -X GET "http://127.0.0.1:12363/contacts?search=Max&max_results=50" \
  -H "Authorization: Bearer $BEARER_TOKEN"
```

### `POST /organizations`
Organisation erstellen.

```bash
curl -X POST http://127.0.0.1:12363/organizations \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ACME Corp",
    "industry": "Technology",
    "size": "large",
    "website": "https://acme.example.com"
  }'
```

### `POST /deals`
Deal erstellen.

```bash
curl -X POST http://127.0.0.1:12363/deals \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Enterprise License Deal",
    "value": 50000.00,
    "currency": "EUR",
    "stage": "proposal",
    "contact_id": "<contact_id>",
    "probability": 60
  }'
```

### `POST /activities`
Aktivität erstellen.

```bash
curl -X POST http://127.0.0.1:12363/activities \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "activity_type": "call",
    "subject": "Follow-up call",
    "description": "Discussed pricing",
    "contact_id": "<contact_id>",
    "deal_id": "<deal_id>",
    "duration_minutes": 30
  }'
```

### `POST /search`
Globale Suche.

```bash
curl -X POST http://127.0.0.1:12363/search \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Max",
    "entity_types": ["contacts", "organizations", "deals"],
    "max_results": 50
  }'
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 17.opena18_CMR
./bin/start_opena18.sh

# Oder via ops.sh (root)
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12363/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena18",
    "endpoint": "http://127.0.0.1:12363",
    "program_target": "crmp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "crmp",
    "action": "create_contact",
    "params": {
      "first_name": "Max",
      "last_name": "Mustermann",
      "email": "max@example.com",
      "position": "CEO"
    }
  }'
```

---

## 📁 Verzeichnisstruktur

```
17.opena18_CMR/
├── main_crm_agent.py        # FastAPI Entry Point (1100 LOC)
├── bin/
│   ├── start_opena18.sh     # Start-Script
│   └── stop_opena18.sh      # Stop-Script
├── test_opena18.py          # Integration Tests (15 Tests, 100%)
├── data/
│   ├── contacts.json        # Contacts Database
│   ├── organizations.json   # Organizations Database
│   ├── deals.json           # Deals Database
│   ├── activities.json      # Activities Database
│   └── crm_history.jsonl    # Append-only History
├── logs/
│   ├── opena18.pid
│   └── opena18.nohup.log
└── README.md                # Diese Datei
```

---

## 🔐 Sicherheit

- ✅ **Bearer-Token** für alle Endpoints außer `/health`
- ✅ **Port-Policy** Enforcement (12344-12399)
- ✅ **Strict JSON** (Pydantic `extra="forbid"`)
- ✅ **Option-2-Flow** Compliance

---

## 🧪 Testing

```bash
# Integration Tests (15 Tests)
python3 test_opena18.py

# Health-Check
curl http://127.0.0.1:12363/health | jq .

# Stop Service
./bin/stop_opena18.sh
```

---

## 📊 Monitoring

```bash
# Service Logs (real-time)
tail -f logs/opena18.nohup.log

# CRM History (JSONL)
tail -f data/crm_history.jsonl | jq .
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 27. November 2025
