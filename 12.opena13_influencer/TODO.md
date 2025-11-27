# TODO – opena13 Influencer Agent

**Port:** 12358  
**Status:** 🟡 Planned  
**Kürzel:** `influp`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [ ] FastAPI-Service `main_influencer_agent.py` erstellen (Port 12358)
- [ ] Config-Modul für DB-Anbindung (Influencer-Profile), API-Keys (Social-Analytics)
- [ ] Health-Endpoint `/health` implementieren
- [ ] Auth-Middleware (Bearer Token) einrichten
- [ ] SQLAlchemy-Models für InfluencerProfile, Campaign, Match
- [ ] Integration mit opena12 (Social Media) für Content-Koordination
- [ ] PID-basiertes Start/Stop-Skript (`bin/start_opena13.sh`)

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [ ] `/health` – Health-Check-Endpoint
- [ ] `/profiles` – Influencer-Profile auflisten/suchen (GET/POST)
- [ ] `/profiles/create` – Profil erstellen (POST)
- [ ] `/match` – Influencer für Kampagne vorschlagen (POST)
- [ ] `/campaigns` – Kampagnen verwalten (GET/POST/PUT/DELETE)
- [ ] `/metrics` – Reichweiten-/Engagement-Metriken abrufen (GET)
- [ ] Pydantic-Schemas für:
  - `InfluencerProfile` (name, platform, followers, engagement_rate, niche)
  - `MatchRequest` (campaign_id, filters, max_results)
  - `MatchResponse` (profiles, scores, reasoning)
  - `CampaignCreate` (name, budget, target_audience, start_date)
- [ ] Error-Handling für:
  - Profile Not Found (404)
  - Invalid Filter (400)
  - No Matches Found (404)
  - Budget Exceeded (402)

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [ ] Registrierung in `tool_registry.json` als `influp`
- [ ] kordp-Routing konfigurieren (Decision72 → influp)
- [ ] CMD-Safepoint für Matching-Operationen
- [ ] RESP-Safepoint mit Matching-Ergebnissen
- [ ] Integration mit opena12 (Social Media) für koordinierte Kampagnen
- [ ] Test des vollständigen Option-2-Flows

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [ ] Strukturiertes JSON-Logging für alle Operationen
- [ ] Nohup-Log (`logs/opena13.nohup.log`)
- [ ] Safepoint-Erstellung für:
  - Matching-Anfragen (CMD mit Kampagne, RESP mit Top-Matches)
  - Profil-Erstellung (CMD mit Daten, RESP mit Profile-ID)
  - Metriken-Abfragen (CMD mit Filter, RESP mit Aggregationen)
- [ ] Secret-Masking für Analytics-API-Keys
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] Datenschutz: Influencer-Daten nur mit Einwilligung speichern

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Unit-Tests für Matching-Algorithmus, Filter-Logic
- [ ] Integration-Tests mit Dummy-Profiles
- [ ] Tests für Edge-Cases:
  - Leere Kampagnen
  - Negative Engagement-Rates
  - Duplikate-Erkennung
  - Multi-Platform-Profile
- [ ] Mock für Analytics-APIs (keine echten Calls in CI/CD)
- [ ] E2E-Test: Kampagne erstellen → Matching → Top-3 Influencer → Archivierung

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [ ] README.md mit:
  - Influencer-Profil-Format
  - Matching-Algorithmus-Beschreibung
  - Kampagnen-Setup
- [ ] API-Dokumentation (alle Endpoints mit cURL-Beispielen)
- [ ] Security-Hinweise:
  - DSGVO-Compliance (Einwilligungen, Löschfristen)
  - Influencer-Daten niemals öffentlich exposen
  - Analytics-API-Keys sicher verwalten
- [ ] Architekturdiagramm (opena12 ↔ opena13 ↔ DB ↔ Portier)
- [ ] Troubleshooting-Guide (Matching-Fehler, Fehlende Metriken)
- [ ] Deployment-Anleitung (Docker, DB-Backup, Analytics-API-Integration)

---

**Letzte Aktualisierung:** 27. November 2025  
**Maintainer:** Danijel Jokic (ELION Team)
