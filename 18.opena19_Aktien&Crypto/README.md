# 🤖 opena19 - Aktien & Crypto

**Agent-ID:** `opena19`  
**Port:** 12365  
**Kürzel:** `stockcryptop`  
**Version:** 3.0  
**Status:** 🟡 **Planned** (PORTIER 3.0 Architecture Ready)  
**Letzte Aktualisierung:** 29. November 2025

---

## 📖 Überblick

**opena19** ist der **Aktien & Crypto** im ELION Hyper-Dashboard System - ein spezialisierter Agent für die PORTIER 3.0 Multi-Agent-Architektur.

### 🎯 PORTIER 3.0 Integration

opena19 ist architektonisch vorbereitet für die PORTIER 3.0 Integration:

- ✅ **Option-2-Flow Ready:** OpenAI → opena1 → opena2 → kordp → opena19
- ✅ **Port Policy Compliant:** Port 12365 (Backend-Range 12344-12399)
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
curl http://127.0.0.1:12365/health | jq .
```

### `POST /invoke`

Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:12365/invoke \
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
cd 18.opena19_Aktien&Crypto
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12365/health | jq .
```

---

## 🔗 Integration mit PORTIER 3.0

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena19",
    "endpoint": "http://127.0.0.1:12365",
    "program_target": "stockcryptop"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "stockcryptop",
    "action": "service_action",
    "params": {...}
  }'
```

---

## 📁 Verzeichnisstruktur (Planned)

```txt
18.opena19_Aktien&Crypto/
├── main.py                  # FastAPI Agent Entry Point (planned)
├── config.py                # Konfiguration (planned)
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script (planned)
├── tests/
│   └── test_opena19.py  # Unit-Tests (planned)
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
pytest tests/test_opena19.py -v

# Health-Check
curl http://127.0.0.1:12365/health

# Integration-Test via Portier
python3 ../scripts/test_opena19_integration.py
```

---

## 📊 Monitoring (Planned)

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:12365/metrics
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

**opena19** ist der **Stocks & Crypto Agent** - Marktdaten, Portfolio & Alerts für Aktien und Kryptowährungen.

### Kernfunktionen

- 📈 **Stock Prices** - Aktienkurse abrufen (AAPL, TSLA, etc.) via Alpha Vantage
- 💰 **Crypto Prices** - Kryptokurse abrufen (BTC, ETH, etc.) via CoinGecko
- 📊 **Portfolio Management** - Positionen verwalten, PnL berechnen, Total Value
- 🔔 **Price Alerts** - Kurs-Alarme erstellen (above/below threshold)
- 💾 **Caching** - 5min TTL für API-Schonung
- 🔗 **Option-2-Flow** - Vollständige Integration

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena19 (12364) ← Dieser Agent
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
curl http://127.0.0.1:12364/health | jq .
```

**Response:**
```json
{
  "status": "ok",
  "service": "opena19",
  "kuerzel": "stockcryptop",
  "port": 12364,
  "uptime_seconds": 787.63,
  "total_positions": 2,
  "total_alerts": 1,
  "active_alerts": 1
}
```

### `GET /prices`
Aktuelle Kurse abrufen.

```bash
curl -X GET "http://127.0.0.1:12364/prices?symbols=AAPL,TSLA&market=stock" \
  -H "Authorization: Bearer $BEARER_TOKEN"
```

### `POST /portfolio`
Portfolio-Position hinzufügen.

```bash
curl -X POST http://127.0.0.1:12364/portfolio \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "market": "stock",
    "quantity": 10.0,
    "avg_price": 150.0
  }'
```

### `GET /portfolio`
Portfolio-Übersicht abrufen.

```bash
curl -X GET http://127.0.0.1:12364/portfolio \
  -H "Authorization: Bearer $BEARER_TOKEN"
```

### `POST /alerts`
Kurs-Alarm erstellen.

```bash
curl -X POST http://127.0.0.1:12364/alerts \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "bitcoin",
    "market": "crypto",
    "condition": "above",
    "threshold": 100000.0,
    "notification": "Email"
  }'
```

### `GET /alerts`
Aktive Alarme auflisten.

```bash
curl -X GET "http://127.0.0.1:12364/alerts?active_only=true" \
  -H "Authorization: Bearer $BEARER_TOKEN"
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 18.opena19_Aktien&Crypto
./bin/start_opena19.sh

# Oder via ops.sh (root)
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12364/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena19",
    "endpoint": "http://127.0.0.1:12364",
    "program_target": "stockcryptop"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "stockcryptop",
    "action": "get_prices",
    "params": {
      "symbols": ["AAPL", "TSLA"],
      "market": "stock"
    }
  }'
```

---

## 📁 Verzeichnisstruktur

```
18.opena19_Aktien&Crypto/
├── main_stocks_crypto_agent.py  # FastAPI Entry Point (950 LOC)
├── bin/
│   ├── start_opena19.sh     # Start-Script
│   └── stop_opena19.sh      # Stop-Script
├── test_opena19.py          # Integration Tests (15 Tests, 100%)
├── data/
│   ├── prices_cache.json    # Price Cache (5min TTL)
│   ├── portfolio.json       # Portfolio Positions
│   ├── alerts.json          # Price Alerts
│   └── stockcrypto_history.jsonl  # Append-only History
├── logs/
│   ├── opena19.pid
│   └── opena19.nohup.log
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
python3 test_opena19.py

# Health-Check
curl http://127.0.0.1:12364/health | jq .

# Stop Service
./bin/stop_opena19.sh
```

---

## 📊 Monitoring

```bash
# Service Logs (real-time)
tail -f logs/opena19.nohup.log

# History (JSONL)
tail -f data/stockcrypto_history.jsonl | jq .
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
<AgentRoot>/   → z. B. 16.opena17_homepagecreator
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
