# TODO – opena16 Shop Agent

**Port:** 12361  
**Status:** 🟡 Planned  
**Kürzel:** `shopp`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [ ] FastAPI-Service `main_shop_agent.py` erstellen (Port 12361)
- [ ] Config-Modul für Shop-System-APIs (Shopify, WooCommerce, Custom)
- [ ] Health-Endpoint `/health` implementieren
- [ ] Auth-Middleware (Bearer Token) einrichten
- [ ] Shop-API-Clients (Shopify SDK, WooCommerce REST API) integrieren
- [ ] Product-Sync-Queue (Redis/SQLite) für Batch-Updates
- [ ] PID-basiertes Start/Stop-Skript (`bin/start_opena16.sh`)

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [ ] `/health` – Health-Check-Endpoint
- [ ] `/products/sync` – Produkte synchronisieren (POST)
- [ ] `/products/update` – Produkt aktualisieren (PUT)
- [ ] `/products/list` – Produkte auflisten (GET)
- [ ] `/orders/list` – Bestellungen abrufen (GET)
- [ ] `/inventory/update` – Lagerbestand aktualisieren (POST)
- [ ] Pydantic-Schemas für:
  - `ProductSync` (products, mode)
  - `ProductUpdate` (id, title, price, inventory)
  - `OrderListRequest` (status, date_from, date_to)
  - `InventoryUpdate` (sku, quantity, warehouse)
- [ ] Error-Handling für:
  - Product Not Found (404)
  - Insufficient Stock (409)
  - Price Out of Range (422)
  - Shop API Down (502)

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [ ] Registrierung in `tool_registry.json` als `shopp`
- [ ] kordp-Routing konfigurieren (Decision72 → shopp)
- [ ] CMD-Safepoint für Product-Updates
- [ ] RESP-Safepoint mit Sync-Ergebnissen
- [ ] Integration mit opena1 für orchestrierte Shop-Operationen
- [ ] Test des vollständigen Option-2-Flows

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [ ] Strukturiertes JSON-Logging für alle Shop-Ops
- [ ] Nohup-Log (`logs/opena16.nohup.log`)
- [ ] Safepoint-Erstellung für:
  - Product-Sync (CMD mit Product-IDs, RESP mit Updated-Count)
  - Price-Updates (CMD mit SKU/Price, RESP mit Status)
  - Inventory-Updates (CMD mit SKU/Quantity, RESP mit New-Stock)
- [ ] Secret-Masking für Shop-API-Keys in Logs
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] Audit-Trail für kritische Preisänderungen

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Unit-Tests für Product-Validation, Price-Calculation
- [ ] Integration-Tests gegen Shopify/WooCommerce Sandbox
- [ ] Tests für Edge-Cases:
  - Batch-Updates (>1000 Produkte)
  - Duplicate SKUs
  - Negative Inventory
  - Currency-Mismatch
- [ ] Mock für Shop-APIs (keine echten Updates in CI/CD)
- [ ] E2E-Test: Product-Sync → Price-Update → Inventory-Adjust → Archivierung

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [ ] README.md mit:
  - Shop-System-Setup (Shopify, WooCommerce)
  - API-Credential-Generierung
  - Sync-Strategien (Full vs. Incremental)
- [ ] API-Dokumentation (alle Endpoints mit cURL-Beispielen)
- [ ] Security-Hinweise:
  - API-Keys niemals hardcoden
  - Rate-Limiting beachten
  - Sandbox-Tests vor Produktion
- [ ] Architekturdiagramm (Shop-System ↔ opena16 ↔ Queue ↔ Portier)
- [ ] Troubleshooting-Guide (Sync-Fehler, API-Limits, Inventory-Konflikte)
- [ ] Deployment-Anleitung (Docker, Credentials-Rotation, Monitoring)

---

**Letzte Aktualisierung:** 27. November 2025  
**Maintainer:** Danijel Jokic (ELION Team)
