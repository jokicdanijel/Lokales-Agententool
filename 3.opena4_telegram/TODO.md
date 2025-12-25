# TODO – opena4 Telegram Bot Agent

**Port:** 12348
**Status:** 🟡 Planned
**Kürzel:** `telep`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [ ] FastAPI-Service `main_telegram_agent.py` erstellen (Port 12348)
- [ ] Config-Modul für Telegram Bot Token, Webhook-URL, Allowed Users
- [ ] Health-Endpoint `/health` implementieren
- [ ] Auth-Middleware (Bearer Token) einrichten
- [ ] Telegram Bot API Client integrieren (python-telegram-bot oder aiogram)
- [ ] Webhook-Modus vs. Polling-Modus konfigurierbar machen
- [ ] PID-basiertes Start/Stop-Skript (`bin/start_opena4.sh`)

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [ ] `/health` – Health-Check-Endpoint
- [ ] `/webhook` – Telegram Webhook-Endpoint (POST)
- [ ] `/send` – Nachricht senden (POST)
- [ ] `/status` – Bot-Status und aktive Chats
- [ ] Pydantic-Schemas für:
  - `TelegramMessage` (chat_id, text, parse_mode)
  - `WebhookUpdate` (update_id, message, callback_query)
  - `SendRequest` (chat_id, text, reply_markup)
- [ ] Error-Handling für:
  - Telegram API Rate Limits (429)
  - Invalid Chat IDs (400)
  - Webhook Verification Failures

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [ ] Registrierung in `tool_registry.json` als `telep`
- [ ] kordp-Routing konfigurieren (Decision72 → telep)
- [ ] CMD-Safepoint für ausgehende Nachrichten
- [ ] RESP-Safepoint für eingehende Nachrichten (Webhook)
- [ ] Integration mit opena1 für orchestrierte Telegram-Flows
- [ ] Test des vollständigen Option-2-Flows (OpenAI → opena1 → opena2 → kordp → telep)

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [ ] Strukturiertes JSON-Logging für alle Bot-Events
- [ ] Nohup-Log (`logs/opena4.nohup.log`)
- [ ] Safepoint-Erstellung für:
  - Gesendete Nachrichten (CMD)
  - Empfangene Nachrichten (RESP)
  - Webhook-Events
- [ ] Secret-Masking für Bot-Token in Logs
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] Chat-Historie in archivp (ohne personenbezogene Daten im Klartext)

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Unit-Tests für Message-Parsing, Send-Logic
- [ ] Integration-Tests gegen Telegram Test-Bot
- [ ] Webhook-Signature-Validation-Tests
- [ ] Load-Tests (100+ Nachrichten/Sekunde)
- [ ] Mock für Telegram API (keine echten Calls in CI/CD)
- [ ] E2E-Test: Nachricht senden → Bot antwortet → Archivierung

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [ ] README.md mit:
  - Bot-Setup-Anleitung (BotFather, Token-Generierung)
  - Webhook vs. Polling-Konfiguration
  - Allowed Users / Chat IDs
- [ ] API-Dokumentation (alle Endpoints mit cURL-Beispielen)
- [ ] Security-Hinweise:
  - Bot-Token niemals hardcoden
  - Webhook-Signature-Validation
  - Rate-Limiting gegen Spam
- [ ] Architekturdiagramm (Telegram API ↔ opena4 ↔ Portier)
- [ ] Troubleshooting-Guide (häufige Fehler, Webhook-Setup)
- [ ] Deployment-Anleitung (Docker, systemd, HTTPS für Webhooks)

---

**Letzte Aktualisierung:** 27. November 2025
**Maintainer:** Danijel Jokic (ELION Team)
