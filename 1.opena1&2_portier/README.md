# 🔄 opena1 & opena2 - Portier & OpenA2 (Core Infrastructure)

**Agent-IDs:** `opena1` (kordp), `opena2` (archivp)  
**Ports:** 12344 (Portier), 12345 (OpenA2)  
**Version:** 2.0  
**Status:** ✅ Production

---

## 📖 Überblick

Dieses Modul enthält die **Kern-Infrastructure** des ELION Hyper-Dashboards:

### **opena1 - Portier (Koordinator)**

- **Port:** 12344
- **Kürzel:** `kordp`
- **Rolle:** Zentraler Koordinator & Dispatcher
- **Funktion:** Orchestriert alle Service-Requests via Option-2-Flow

### **opena2 - OpenA2 (Archivator)**

- **Port:** 12345
- **Kürzel:** `archivp`
- **Rolle:** Longtime-Gedächtnis & Safepoint-Manager
- **Funktion:** Append-only JSONL-Archive mit Unicode-Pfeil → Notation

---

## 🏗️ Architektur

```
Client/UI
    ↓
opena1 (Portier, 12344)
    ↓
opena2 (OpenA2, 12345) ← Safepoint CMD
    ↓
kordp (Dispatcher)
    ↓
Target Service (opena3-opena20)
    ↓
opena2 (OpenA2, 12345) ← Safepoint RESP
    ↓
opena1 (Portier, 12344)
    ↓
Client/UI
```

---

## 📡 API-Endpoints

### opena1 (Portier) - 12344

#### `GET /health`

Health-Check (keine Authentifizierung erforderlich).

```bash
curl -s http://127.0.0.1:12344/health | jq
```

#### `POST /route/update`

Service-Registrierung im Route-Registry (Agent-Setup).

```bash
curl -s -X POST http://127.0.0.1:12344/route/update \
  -H 'Content-Type: application/json' \
  -d '{
    "agent": "openwebui",
    "agent_id": "opena3",
    "port": 12346,
    "program": "openweb",
    "archivator_port": 12345,
    "mapping_ts": "2025-11-10T00:00:00Z",
    "mapping": {"intent": "ensure_transfer_to_archivator"}
  }' | jq
```

**Älteres Format (weiterhin unterstützt):**

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "telegram",
    "endpoint": "http://127.0.0.1:12346",
    "program_target": "telep"
  }'
```

#### `POST /dispatch/kordp`

Command-Routing an Zielservice via Option-2-Flow.

```bash
curl -s -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H 'Content-Type: application/json' \
  -d '{
    "agent": "openwebui",
    "action": "refresh_index",
    "data": {"scope": "daily"}
  }' | jq
```

**Älteres Format (weiterhin unterstützt):**

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "telep",
    "action": "send_message",
    "params": {"chat_id": 12345, "message": "Hello"}
  }'
```

**Effekt:** opena1 bestätigt, schreibt Safepoint (`kind=DISPATCH`) via opena2.

#### `POST /log/opena1`

Ereignis-Logging (zentrale Log-Erfassung).

```bash
curl -s -X POST http://127.0.0.1:12344/log/opena1 \
  -H 'Content-Type: application/json' \
  -d '{
    "source": "test",
    "event": "ping",
    "payload": {"note": "hello"},
    "strict": true
  }' | jq
```

---

### opena2 (OpenA2) - 12345

#### `GET /health`

Health-Check (keine Authentifizierung erforderlich).

```bash
curl -s http://127.0.0.1:12345/health | jq
```

#### `POST /store/archivp`

Safepoint-Speicherung (CMD/RESP/NOTE/DISPATCH).

```bash
curl -s -X POST http://127.0.0.1:12345/store/archivp \
  -H 'Content-Type: application/json' \
  -d '{
    "src": "client",
    "dst": "archivp",
    "kind": "NOTE",
    "body": {"k": "v"}
  }' | jq
```

**Erweitert (mit Strict-Mode):**

```bash
curl -X POST http://127.0.0.1:12345/store/archivp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "src": "kordp",
    "dst": "telep",
    "kind": "CMD",
    "body": {"action": "send_message", "params": {...}},
    "strict": true
  }'
```

**Safepoint-Speicherorte:**

```
archivp_store/
├── index.jsonl
└── YYYY/
    └── MM/
        └── DD/
            ├── SP<timestamp>_kordp→telep_CMD.json
            └── SP<timestamp>_telep→kordp_RESP.json
```

**Naming Convention:** `SP<ts>_<src>→<dst>_<kind>.json` (Unicode-Pfeil → ist Pflicht)

#### `GET /query/archivp`

Safepoint-Suche (Filter nach src/dst/kind).

```bash
curl "http://127.0.0.1:12345/query/archivp?src=kordp&dst=telep&limit=10" | jq
```

#### `POST /finalize/opena2`

Audit-Finalisierung (Ticket-Abschluss).

```bash
curl -s -X POST http://127.0.0.1:12345/finalize/opena2 \
  -H 'Content-Type: application/json' \
  -d '{
    "ticket": "T-2025-001",
    "status": "closed",
    "notes": "ok"
  }' | jq
```

---

## 🚀 Quick Start

### Starten

```bash
# opena1 (Portier)
cd 1.opena1&2_portier
python3 opena1_app.py

# opena2 (OpenA2)
python3 opena2_app.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12344/health | jq .
curl http://127.0.0.1:12345/health | jq .
```

---

## 📁 Verzeichnisstruktur

```
1.opena1&2_portier/
├── opena1_app.py           # Portier FastAPI App
├── opena2_app.py           # OpenA2 FastAPI App
├── koordinator.py          # Option-2 Koordinations-Logik
├── tool_registry.py        # Service-Registry
├── tool_dispatcher.py      # kordp Dispatcher
├── schemas.py              # Pydantic Models
├── archivp_store/          # Safepoint-Archive
│   ├── index.jsonl
│   └── YYYY/MM/DD/
├── knowledgebase/          # Agent-Wissensbasis
├── config/                 # Konfigurationsdateien
├── bin/                    # Start-Scripts
├── tests/                  # Unit-Tests
└── README.md               # Diese Datei
```

---

## 🔐 Sicherheit

- ✅ **Bearer-Token** für alle Endpoints außer `/health`
- ✅ **Archiv-Anonymisierung** (Tokens maskiert in Safepoints)
- ✅ **Strict JSON** (Pydantic `extra="forbid"`)
- ✅ **Port-Policy** (12344-12399 erlaubt, 8080 verboten)

---

## 🧪 Testing

```bash
# Unit-Tests
pytest tests/ -v

# Integration-Test
python3 tests/test_archivator.py

# Load-Test
python3 ../scripts/load_test_20_services.py
```

---

## 📚 Weitere Dokumentation

- [Option-2-Flow](../.github/copilot-master-prompt.md)
- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 21. November 2025
