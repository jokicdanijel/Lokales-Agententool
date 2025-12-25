# TODO – opena19 Aktien & Crypto Agent

**Port:** 12364
**Status:** 🟡 Planned
**Kürzel:** `stockcryptop`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [ ] FastAPI-Service `main_stockcrypto_agent.py` erstellen (Port 12364)
- [ ] Config-Modul für Marktdaten-APIs (Alpha Vantage, CoinGecko, Binance)
- [ ] Health-Endpoint `/health` implementieren
- [ ] Auth-Middleware (Bearer Token) einrichten
- [ ] API-Clients für Aktien- und Krypto-Daten integrieren
- [ ] Caching-Layer (Redis) für Rate-Limit-Schonung
- [ ] PID-basiertes Start/Stop-Skript (`bin/start_opena19.sh`)

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [ ] `/health` – Health-Check-Endpoint
- [ ] `/prices` – Aktueller Kurs (GET)
- [ ] `/history` – Historische Daten (GET)
- [ ] `/portfolio` – Portfolio-Übersicht (GET/POST)
- [ ] `/alerts` – Kurs-Alerts verwalten (GET/POST/DELETE)
- [ ] `/metrics` – Performance-Metriken (GET)
- [ ] Pydantic-Schemas für:
  - `PriceRequest` (symbols, market)
  - `HistoryRequest` (symbol, from_date, to_date, interval)
  - `Portfolio` (positions, total_value, pnl)
  - `AlertCreate` (symbol, condition, threshold, notification)
- [ ] Error-Handling für:
  - Symbol Not Found (404)
  - Rate Limit Exceeded (429)
  - Market Closed (503)
  - API Down (502)

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [ ] Registrierung in `tool_registry.json` als `stockcryptop`
- [ ] kordp-Routing konfigurieren (Decision72 → stockcryptop)
- [ ] CMD-Safepoint für Price-Queries
- [ ] RESP-Safepoint mit Kurs-Daten
- [ ] Integration mit opena1 für orchestrierte Markt-Analysen
- [ ] Test des vollständigen Option-2-Flows

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [ ] Strukturiertes JSON-Logging für alle API-Calls
- [ ] Nohup-Log (`logs/opena19.nohup.log`)
- [ ] Safepoint-Erstellung für:
  - Price-Queries (CMD mit Symbols, RESP mit Prices)
  - Alert-Triggers (CMD mit Alert-ID, RESP mit Notification)
  - Portfolio-Updates (CMD mit Trades, RESP mit New-Value)
- [ ] Secret-Masking für API-Keys in Logs
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] Cache-TTL-Strategie dokumentieren

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Unit-Tests für Price-Calculation, Alert-Logic
- [ ] Integration-Tests gegen Sandbox-APIs
- [ ] Tests für Edge-Cases:
  - Delisted Symbols
  - After-Hours-Trading
  - Split-Adjusted Prices
  - Crypto-Pair-Conversions
- [ ] Mock für Market-APIs (keine echten Calls in CI/CD)
- [ ] E2E-Test: Price-Query → Cache-Hit → Alert-Check → Archivierung

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [ ] README.md mit:
  - API-Provider-Setup (Alpha Vantage, CoinGecko)
  - Rate-Limiting-Strategien
  - Caching-Policies
- [ ] API-Dokumentation (alle Endpoints mit cURL-Beispielen)
- [ ] Security-Hinweise:
  - API-Keys niemals hardcoden
  - Portfolio-Daten verschlüsselt speichern
  - Rate-Limits strikt einhalten
- [ ] Architekturdiagramm (Market-APIs ↔ Cache ↔ opena19 ↔ Portier)
- [ ] Troubleshooting-Guide (API-Limits, Symbol-Errors, Cache-Invalidation)
- [ ] Deployment-Anleitung (Docker, Redis-Setup, API-Key-Rotation)

---

**Letzte Aktualisierung:** 27. November 2025
**Maintainer:** Danijel Jokic (ELION Team)
