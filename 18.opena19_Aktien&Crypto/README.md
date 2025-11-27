# 📈 opena19 - Stocks & Crypto Agent

**Agent-ID:** `opena19`  
**Port:** 12364  
**Kürzel:** `stockcryptop`  
**Version:** 1.0  
**Status:** ✅ RUNNING (PID: 1819135)

---

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
