# TODO – opena9 Telefonie Agent

**Port:** 12354
**Status:** 🟡 Planned
**Kürzel:** `telphonep`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [ ] FastAPI-Service `main_telephone_agent.py` erstellen (Port 12354)
- [ ] Config-Modul für SIP/Twilio-Credentials, Default Caller-ID, Timeout
- [ ] Health-Endpoint `/health` implementieren
- [ ] Auth-Middleware (Bearer Token) einrichten
- [ ] SIP-Client (pjsua/pjsip) oder Twilio SDK integrieren
- [ ] Call-State-Machine implementieren (Idle, Ringing, Connected, Ended)
- [ ] PID-basiertes Start/Stop-Skript (`bin/start_opena9.sh`)

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [ ] `/health` – Health-Check-Endpoint
- [ ] `/call/start` – Anruf initiieren (POST)
- [ ] `/call/hangup` – Anruf beenden (POST)
- [ ] `/call/status` – Anruf-Status abfragen (GET)
- [ ] `/webhook/status` – Twilio Status-Callback (POST)
- [ ] `/webhook/recording` – Aufnahme-Callback (POST, falls Recording aktiv)
- [ ] Pydantic-Schemas für:
  - `CallStartRequest` (to, from, timeout)
  - `CallHangupRequest` (call_id)
  - `CallStatusResponse` (call_id, status, duration)
  - `WebhookStatusUpdate` (call_sid, status, timestamp)
- [ ] Error-Handling für:
  - Invalid Number Format (400)
  - Busy/No Answer (486/487)
  - Call Failed (500)
  - Insufficient Balance (402, bei Twilio)

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [ ] Registrierung in `tool_registry.json` als `telphonep`
- [ ] kordp-Routing konfigurieren (Decision72 → telphonep)
- [ ] CMD-Safepoint für Call-Start (CMD mit Nummer/Caller-ID)
- [ ] RESP-Safepoint für Call-Status (RESP mit Duration/Status)
- [ ] Integration mit opena1 für orchestrierte Telefonie-Flows
- [ ] Test des vollständigen Option-2-Flows

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [ ] Strukturiertes JSON-Logging für alle Call-Events
- [ ] Nohup-Log (`logs/opena9.nohup.log`)
- [ ] Safepoint-Erstellung für:
  - Call-Start (CMD mit Nummer, RESP mit Call-ID)
  - Call-End (RESP mit Dauer/Status)
  - Webhook-Events (Status-Changes)
- [ ] Secret-Masking für SIP/Twilio-Credentials in Logs
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] Telefonnummern pseudonymisieren (keine Klartext-Speicherung)
- [ ] Call-Recordings extern speichern (nicht in Safepoints)

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Unit-Tests für Number-Validation, Call-State-Machine
- [ ] Integration-Tests gegen Test-SIP-Account / Twilio Test-Credentials
- [ ] Tests für Edge-Cases:
  - Ungültige Nummern
  - Besetzt-Signal
  - Timeout während Verbindungsaufbau
  - Webhook-Retry-Logic
- [ ] Mock für SIP/Twilio (keine echten Calls in CI/CD)
- [ ] E2E-Test: Call-Start → Status-Update → Hangup → Archivierung

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [ ] README.md mit:
  - SIP vs. Twilio Setup
  - Caller-ID-Konfiguration
  - Call-Recording-Richtlinien (rechtliche Aspekte)
- [ ] API-Dokumentation (alle Endpoints mit cURL-Beispielen)
- [ ] Security-Hinweise:
  - SIP/Twilio-Credentials niemals hardcoden
  - Webhook-Signature-Validation (Twilio)
  - Rate-Limiting gegen Missbrauch
- [ ] Architekturdiagramm (SIP-Server/Twilio ↔ opena9 ↔ Portier)
- [ ] Troubleshooting-Guide (Auth-Fehler, Network-Issues, Echo)
- [ ] Deployment-Anleitung (Docker, Firewall-Regeln für SIP)

---

**Letzte Aktualisierung:** 27. November 2025
**Maintainer:** Danijel Jokic (ELION Team)
