# TODO – opena7 E-Mail Client Agent

**Port:** 12352
**Status:** 🟡 Planned
**Kürzel:** `emailp`

---

## 1. Architektur & Setup – Rolle, Config, FastAPI-Entry

- [ ] FastAPI-Service `main_email_agent.py` erstellen (Port 12352)
- [ ] Config-Modul für IMAP/SMTP-Server, TLS/SSL, Credentials
- [ ] Health-Endpoint `/health` implementieren
- [ ] Auth-Middleware (Bearer Token) einrichten
- [ ] IMAP-Client (imaplib/aioimaplib) integrieren
- [ ] SMTP-Client (smtplib/aiosmtplib) integrieren
- [ ] PID-basiertes Start/Stop-Skript (`bin/start_opena7.sh`)

---

## 2. API-Design – Endpunkte, Pydantic-Schemas, Error-Handling

- [ ] `/health` – Health-Check-Endpoint
- [ ] `/inbox/list` – E-Mails auflisten (GET/POST mit Filter)
- [ ] `/message/get` – E-Mail abrufen (POST mit Message-ID)
- [ ] `/message/send` – E-Mail senden (POST)
- [ ] `/message/search` – E-Mails suchen (POST mit Query)
- [ ] `/folders/list` – IMAP-Ordner auflisten
- [ ] Pydantic-Schemas für:
  - `InboxListRequest` (folder, limit, offset, filter)
  - `MessageGetRequest` (message_id, include_body)
  - `MessageSendRequest` (to, cc, bcc, subject, body, attachments)
  - `SearchRequest` (query, folder, date_from, date_to)
- [ ] Error-Handling für:
  - Auth Failed (401)
  - Mailbox Full (507)
  - Message Not Found (404)
  - SMTP Rejected (550)

---

## 3. Portier-Integration – Tool-Registry, kordp-Routing, Option-2-Flow

- [ ] Registrierung in `tool_registry.json` als `emailp`
- [ ] kordp-Routing konfigurieren (Decision72 → emailp)
- [ ] CMD-Safepoint für:
  - Gesendete E-Mails (CMD mit Empfänger/Betreff)
  - Inbox-Abfragen (CMD mit Filter)
- [ ] RESP-Safepoint mit Metadaten (keine vollen E-Mail-Bodies)
- [ ] Integration mit opena1 für orchestrierte E-Mail-Workflows
- [ ] Test des vollständigen Option-2-Flows

---

## 4. Logging & Safepoints – Strukturiertes Logging, Archivierung

- [ ] Strukturiertes JSON-Logging für alle E-Mail-Operationen
- [ ] Nohup-Log (`logs/opena7.nohup.log`)
- [ ] Safepoint-Erstellung für:
  - Gesendete E-Mails (CMD mit Metadaten, RESP mit Message-ID)
  - Empfangene E-Mails (nur Metadaten, nicht Body)
  - Suchvorgänge (CMD mit Query, RESP mit Trefferzahl)
- [ ] Secret-Masking für SMTP/IMAP-Credentials in Logs
- [ ] Log-Rotation (max. 10 MB, 5 Generationen)
- [ ] DSGVO-konforme Speicherung (keine personenbezogenen Daten im Klartext)

---

## 5. Tests & Qualität – Unit-Tests, Integrationstests, Doku

- [ ] Pytest-Suite mit ≥80% Coverage
- [ ] Unit-Tests für Message-Parsing, SMTP-Send-Logic
- [ ] Integration-Tests gegen Test-Mailbox
- [ ] Tests für Edge-Cases:
  - Große Attachments (>10 MB)
  - HTML-E-Mails
  - Mehrere Empfänger (CC/BCC)
  - Spam-Ordner
- [ ] Mock für IMAP/SMTP (keine echten E-Mails in CI/CD)
- [ ] E2E-Test: E-Mail senden → Inbox abrufen → Archivierung

---

## 6. Dokumentation – README, API-Übersicht, Security-Hinweise

- [ ] README.md mit:
  - IMAP/SMTP-Server-Konfiguration
  - TLS/SSL-Anforderungen
  - Credential-Management (`.env`)
- [ ] API-Dokumentation (alle Endpoints mit cURL-Beispielen)
- [ ] Security-Hinweise:
  - TLS/SSL pflicht
  - Keine Klartext-Credentials
  - Rate-Limiting gegen Spam
- [ ] Architekturdiagramm (E-Mail-Server ↔ opena7 ↔ Portier)
- [ ] Troubleshooting-Guide (Auth-Fehler, Timeout, Encoding)
- [ ] Deployment-Anleitung (Docker, Credentials-Rotation)

---

**Letzte Aktualisierung:** 27. November 2025
**Maintainer:** Danijel Jokic (ELION Team)
