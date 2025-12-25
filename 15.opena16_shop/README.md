# 🤖 opena16 - Shop Creator

**Agent-ID:** `opena16`
**Port:** 12362
**Kürzel:** `shopp`
**Version:** 3.0
**Status:** 🟡 **Planned** (PORTIER 3.0 Architecture Ready)
**Letzte Aktualisierung:** 29. November 2025

---

## 📖 Überblick

**opena16** ist der **Shop Creator** im ELION Hyper-Dashboard System - ein spezialisierter Agent für die PORTIER 3.0 Multi-Agent-Architektur.

### 🎯 PORTIER 3.0 Integration

opena16 ist architektonisch vorbereitet für die PORTIER 3.0 Integration:

- ✅ **Option-2-Flow Ready:** OpenAI → opena1 → opena2 → kordp → opena16
- ✅ **Port Policy Compliant:** Port 12362 (Backend-Range 12344-12399)
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
curl http://127.0.0.1:12362/health | jq .
```

### `POST /invoke`

Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12362/invoke \
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
cd 15.opena16_shop
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12362/health | jq .
```

---

## 🔗 Integration mit PORTIER 3.0

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena16",
    "endpoint": "http://127.0.0.1:12362",
    "program_target": "shopp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "shopp",
    "action": "service_action",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur (Planned)

```txt
15.opena16_shop/
├── main.py                  # FastAPI Agent Entry Point (planned)
├── config.py                # Konfiguration (planned)
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script (planned)
├── tests/
│   └── test_opena16.py  # Unit-Tests (planned)
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
pytest tests/test_opena16.py -v

# Health-Check
curl http://127.0.0.1:12362/health

# Integration-Test via Portier
python3 ../scripts/test_opena16_integration.py
```

---

## 📊 Monitoring (Planned)

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12362/metrics
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

**opena16** ist der **Shop Management Agent** - spezialisiert auf E-Commerce, Produkt-Verwaltung und Bestellabwicklung.

### Kernfunktionen

- 🛒 **Product Management** - Produkte erstellen/bearbeiten/löschen (CRUD)
- 💰 **Price Management** - Preise, Währungen, SKUs verwalten
- 📦 **Order Management** - Bestellungen erstellen, auflisten, filtern
- 📊 **Inventory Tracking** - Lagerbestand in Echtzeit aktualisieren
- 📚 **Category Management** - Produktkategorien organisieren
- 🔍 **Product Search** - Suche nach Titel, Beschreibung, Status

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena16 (12361) ← Dieser Agent
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
curl http://127.0.0.1:12358/health | jq .
```

**Response:**

```json
{
  "status": "ok",
  "service": "opena16",
  "kuerzel": "shopp",
  "port": 12361,
  "uptime_seconds": 114.7,
  "total_products": 1,
  "total_orders": 1
}
```

### `POST /products/create`

Produkt erstellen.

```bash
curl -X POST http://127.0.0.1:12361/products/create \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Premium Widget",
    "description": "High-quality widget",
    "sku": "WIDGET-001",
    "price": 29.99,
    "currency": "EUR",
    "status": "active",
    "tags": ["premium", "widget"]
  }'
```

### `POST /products/list`

Produkte auflisten (mit Filter).

```bash
curl -X POST http://127.0.0.1:12361/products/list \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "active",
    "search": "widget",
    "max_results": 50
  }'
```

### `PUT /products/update`

Produkt aktualisieren.

```bash
curl -X PUT http://127.0.0.1:12361/products/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "<product_id>",
    "title": "Premium Widget (Updated)",
    "price": 39.99
  }'
```

### `POST /inventory/update`

Lagerbestand aktualisieren.

```bash
curl -X POST http://127.0.0.1:12361/inventory/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "WIDGET-001",
    "quantity": 100,
    "warehouse": "main"
  }'
```

### `POST /orders/create`

Bestellung erstellen.

```bash
curl -X POST http://127.0.0.1:12361/orders/create \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "items": [{"sku": "WIDGET-001", "quantity": 2}],
    "currency": "EUR",
    "shipping_address": "Main St 123, 12345 City"
  }'
```

### `POST /orders/list`

Bestellungen auflisten.

```bash
curl -X POST http://127.0.0.1:12361/orders/list \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "pending",
    "max_results": 50
  }'
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 15.opena16_shop
./bin/start_opena16.sh

# Oder via ops.sh (root)
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12361/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena16",
    "endpoint": "http://127.0.0.1:12361",
    "program_target": "shopp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "shopp",
    "action": "create_product",
    "params": {
      "title": "Widget",
      "sku": "WIDGET-001",
      "price": 29.99,
      "currency": "EUR",
      "status": "active"
    }
  }'
```

---

## 📁 Verzeichnisstruktur

```
15.opena16_shop/
├── main_shop_agent.py       # FastAPI Agent Entry Point (900 LOC)
├── bin/
│   ├── start_opena16.sh     # Start-Script
│   └── stop_opena16.sh      # Stop-Script
├── test_opena16.py          # Integration Tests (14 Tests, 100%)
├── data/
│   ├── products.json        # Product Database
│   ├── orders.json          # Orders Database
│   ├── inventory.json       # Inventory Tracking
│   ├── categories.json      # Product Categories
│   └── shop_history.jsonl  # Append-only History
├── logs/
│   ├── opena16.pid
│   └── opena16.nohup.log
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
# Integration Tests (14 Tests)
python3 test_opena16.py

# Health-Check
curl http://127.0.0.1:12361/health | jq .

# Stop Service
./bin/stop_opena16.sh
```

---

## 📊 Monitoring

```bash
# Service Logs (real-time)
tail -f logs/opena16.nohup.log

# Shop Operations History (JSONL)
tail -f data/shop_history.jsonl | jq .
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team
**Letzte Aktualisierung:** 27. November 2025
EXTREM WICHTIG — FILE-SCAN-PFLICHT FÜR DIESEN AGENT
Bevor du irgendeine Datei erzeugst, MUSST du folgendes tun:

✔ 1. Projektverzeichnis scannen
Scanne rekursiv das Verzeichnis dieses Agents:

css
￼Code kopieren
<AgentRoot>/ → z. B. 16.opena17_homepagecreator
main.py
routes.py
models.py
agent_logic.py
config.py
security.py
bin/
data/
templates/
tests/
✔ 2. Existierende Dateien feststellen
Alle vorhandenen Dateien müssen analysiert werden:

nicht löschen

nicht überschreiben

nicht ignorieren

nicht neuschreiben

Du musst sie weiterverwenden.

✔ 3. Wenn eine Datei existiert, MUSST du sie patchen, nicht ersetzen
Patch-Regeln:

Nur fehlende Funktionen ergänzen

Nur fehlerhafte Bereiche reparieren

Nur neue Features anhängen

Nichts entfernen, außer explizit erlaubt

Keine Duplikate erzeugen

Beispiel:

less
￼Code kopieren
Wenn main.py vorhanden ist:
→ erweitere main.py
→ verbessere main.py
→ implementiere fehlende Endpoints
→ füge neue Klassen hinzu
→ aber überschreibe NIEMALS main.py komplett
✔ 4. Wenn eine Datei NICHT existiert, dann erst erstellen
Neue Dateien dürfen nur erstellt werden, wenn sie wirklich fehlen:

sql
￼Code kopieren
if file_exists:
patch
else:
create new file
✔ 5. PRIORITÄT: EXISTING > NEW
Immer:

sql
￼Code kopieren
EXISTIERENDE STRUKTUR BEWAHREN
LOGIK ONLY ERWEITERN
NIEMALS Dateien ersetzen
NIEMALS alles neu generieren
✔ 6. Workflow-Agent opena21 MUSS besonders strikt sein
opena21 darf:

andere Agents analysieren

deren Dateien lesen

fehlende Workflows ergänzen
