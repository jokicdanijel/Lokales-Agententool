# TODO – opena8 WhatsApp Agent

**Port:** 12353  
**Status:** 🟡 Planned  
**Kürzel:** `whatsappp`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [ ] FastAPI-Service `main_whatsapp_agent.py` erstellen (Port 12353)
- [ ] Config-Modul für WhatsApp Business Cloud API, Access Token, Phone Number ID
- [ ] Health-Endpoint `/health` implementieren
- [ ] Auth-Middleware (Bearer Token) einrichten
- [ ] WhatsApp Client SDK integrieren (offizieller Meta SDK oder httpx-basiert)
- [ ] Webhook-Verification-Logic implementieren
- [ ] PID-basiertes Start/Stop-Skript (`bin/start_opena8.sh`)

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [ ] `/health` – Health-Check-Endpoint
- [ ] `/webhook` – WhatsApp Webhook-Endpoint (POST, GET für Verification)
- [ ] `/send` – Nachricht senden (POST)
- [ ] `/template/send` – Template-Nachricht senden (POST)
- [ ] `/media/upload` – Medien hochladen (POST)
- [ ] `/conversations` – Gespräche auflisten (GET)
- [ ] Pydantic-Schemas für:
  - `SendMessageRequest` (to, type, text, image, video)
  - `SendTemplateRequest` (to, template_name, language, parameters)
  - `WebhookUpdate` (entry, changes, messages)
  - `MediaUploadRequest` (file, mime_type)
- [ ] Error-Handling für:
  - Invalid Phone Number (400)
  - Template Not Found (404)
  - Rate Limit Exceeded (429)
  - Webhook Signature Invalid (401)

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [ ] Registrierung in `tool_registry.json` als `whatsappp`
- [ ] kordp-Routing konfigurieren (Decision72 → whatsappp)
- [ ] CMD-Safepoint für ausgehende Nachrichten
- [ ] RESP-Safepoint für eingehende Nachrichten (Webhook)
- [ ] Integration mit opena1 für orchestrierte WhatsApp-Flows
- [ ] Test des vollständigen Option-2-Flows

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [ ] Strukturiertes JSON-Logging für alle Nachrichten
- [ ] Nohup-Log (`logs/opena8.nohup.log`)
- [ ] Safepoint-Erstellung für:
  - Gesendete Nachrichten (CMD mit to/text, RESP mit Message-ID)
  - Empfangene Nachrichten (Webhook → RESP)
  - Template-Sends (CMD mit Template-Name, RESP mit Status)
- [ ] Secret-Masking für Access Token in Logs
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] Telefonnummern pseudonymisieren (keine Klartext-Speicherung)

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Unit-Tests für Webhook-Parsing, Message-Send-Logic
- [ ] Integration-Tests gegen WhatsApp Test Business Account
- [ ] Tests für Edge-Cases:
  - Große Mediendateien
  - Template-Parameter-Substitution
  - Webhook-Retry-Logic
  - Fehlende Opt-In
- [ ] Mock für WhatsApp API (keine echten Calls in CI/CD)
- [ ] E2E-Test: Nachricht senden → Webhook empfangen → Archivierung

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [ ] README.md mit:
  - WhatsApp Business API Setup (Meta App, Phone Number)
  - Webhook-URL-Konfiguration
  - Template-Approval-Prozess
- [ ] API-Dokumentation (alle Endpoints mit cURL-Beispielen)
- [ ] Security-Hinweise:
  - Webhook-Signature-Validation pflicht
  - Access Token niemals hardcoden
  - Rate-Limiting beachten (1000 msg/24h für Free Tier)
- [ ] Architekturdiagramm (WhatsApp Cloud API ↔ opena8 ↔ Portier)
- [ ] Troubleshooting-Guide (Template-Fehler, Webhook-Fails, Opt-In-Probleme)
- [ ] Deployment-Anleitung (Docker, HTTPS für Webhooks, Ngrok für Dev)

---

**Letzte Aktualisierung:** 27. November 2025  
**Maintainer:** Danijel Jokic (ELION Team)
