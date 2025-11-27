# 📅 opena14 - Calendar Management

**Agent-ID:** `opena14`  
**Port:** 12359  
**Kürzel:** `calp`  
**Version:** 1.0  
**Status:** ✅ RUNNING (PID: 1754254)

---

## 📖 Überblick

**opena14** ist der **Calendar Management Agent** - spezialisiert auf Event-Verwaltung, iCalendar-Support und Recurring Events.

### Kernfunktionen

- 🗓️ **Event Management** - Termine erstellen/bearbeiten/löschen (CRUD)
- 📅 **iCalendar Support** - Import/Export im iCal-Format (.ics)
- 🔄 **Recurring Events** - Serientermine mit RRULE-Support
- 🌐 **Timezone Handling** - Multi-Timezone mit pytz
- 📂 **Multi-Calendar** - Mehrere Kalender verwalten
- 👥 **Attendees** - Teilnehmer-Listen und Meeting-Koordination

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena14 (12359) ← Dieser Agent
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
curl http://127.0.0.1:12356/health | jq .
```

**Response:**
```json
{
  "status": "ok",
  "service": "opena14",
  "kuerzel": "calp",
  "port": 12359,
  "uptime_seconds": 92.89,
  "total_events": 5,
  "total_calendars": 2,
  "ical_support": false
}
```

### `POST /calendars/create`
Kalender erstellen.

```bash
curl -X POST http://127.0.0.1:12359/calendars/create \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Work Calendar",
    "description": "Professional meetings",
    "timezone": "Europe/Berlin",
    "color": "#FF5733"
  }'
```

### `POST /events/create`
Event erstellen.

```bash
curl -X POST http://127.0.0.1:12359/events/create \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "calendar_id": "<calendar_id>",
    "summary": "Team Meeting",
    "start": "2025-11-28T09:00:00Z",
    "end": "2025-11-28T10:00:00Z",
    "description": "Weekly sync",
    "location": "Conference Room A",
    "attendees": ["alice@example.com", "bob@example.com"],
    "all_day": false
  }'
```

### `POST /events/list`
Events auflisten (mit Filter).

```bash
curl -X POST http://127.0.0.1:12359/events/list \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "calendar_id": "<calendar_id>",
    "start_date": "2025-11-27T00:00:00Z",
    "end_date": "2025-12-31T23:59:59Z",
    "max_results": 50
  }'
```

### `PUT /events/update`
Event aktualisieren.

```bash
curl -X PUT http://127.0.0.1:12359/events/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "<event_id>",
    "summary": "Team Meeting (Updated)",
    "location": "Conference Room B"
  }'
```

### `DELETE /events/delete`
Event löschen.

```bash
curl -X DELETE http://127.0.0.1:12359/events/delete \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "<event_id>",
    "calendar_id": "<calendar_id>"
  }'
```

### `GET /events/{event_id}/ical`
iCalendar Export (.ics).

```bash
curl -X GET http://127.0.0.1:12359/events/<event_id>/ical \
  -H "Authorization: Bearer $BEARER_TOKEN"
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 13.opena14_calendar
./bin/start_opena14.sh

# Oder via ops.sh (root)
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12359/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena14",
    "endpoint": "http://127.0.0.1:12359",
    "program_target": "calp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "calp",
    "action": "create_event",
    "params": {
      "calendar_id": "default",
      "summary": "Important Meeting",
      "start": "2025-11-29T14:00:00Z",
      "end": "2025-11-29T15:00:00Z"
    }
  }'
```

---

## 📁 Verzeichnisstruktur

```
13.opena14_calendar/
├── main_calendar_agent.py   # FastAPI Agent Entry Point (850 LOC)
├── bin/
│   ├── start_opena14.sh     # Start-Script
│   └── stop_opena14.sh      # Stop-Script
├── test_opena14.py          # Integration Tests (12 Tests, 100%)
├── data/                    # JSON Persistence
│   ├── events.json
│   ├── calendars.json
│   └── event_history.jsonl  # Append-only History
├── logs/
│   ├── opena14.pid
│   └── opena14.nohup.log
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
# Integration Tests (12 Tests)
python3 test_opena14.py

# Health-Check
curl http://127.0.0.1:12359/health | jq .

# Stop Service
./bin/stop_opena14.sh
```

---

## 📊 Monitoring

```bash
# Service Logs (real-time)
tail -f logs/opena14.nohup.log

# Event History (JSONL)
tail -f data/event_history.jsonl | jq .
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 27. November 2025
