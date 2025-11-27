# opena7 — Mail Agent

**Automatisierte E-Mail-Kommunikation (Ein- und Ausgang)**

## Überblick

opena7 ist ein FastAPI-basierter Mail-Agent für das ELION Hyper-Dashboard. Er verbindet das System mit E-Mail-Infrastrukturen über IMAP/SMTP, automatisiert die Verarbeitung eingehender Mails, klassifiziert diese nach Sentiment/Dringlichkeit und archiviert jede Transaktion unveränderbar via opena2.

**Kernmerkmale:**

- 📧 IMAP/SMTP-Integration (SSL/TLS obligatorisch)
- 🤖 Automatische Klassifizierung (Sentiment, Sprache, Dringlichkeit)
- 💾 Attachment-Handling mit Sicherheitsprüfung
- 🔒 Absender-Allowlist + Audit-Trail
- 📊 Prometheus-Metriken + strukturierte Logs (JSONL)
- 🔗 Vollständige Safepoint-Integration (opena2 Archivierung)

---

## Installation

### 1. Lokale Entwicklung

```bash
# Repository navigieren
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# Virtual Environment aktivieren
source .venv/bin/activate

# Dependencies installieren
pip install -r 6.opena7_mail/requirements.txt
```

### 2. Docker-Deployment

```bash
# Bau und Start
cd 6.opena7_mail
docker build -t opena7:latest .
docker run -d \
  --name opena7 \
  -p 127.0.0.1:12350:12350 \
  -e MAIL_IMAP_HOST=imap.provider.at \
  -e MAIL_SMTP_HOST=smtp.provider.at \
  -e MAIL_USER=bot@example.org \
  -e OPENA1_URL=http://opena1:12344 \
  -e OPENA2_URL=http://opena2:12345 \
  opena7:latest

# Mit docker-compose
docker-compose up -d
```

### 3. systemd-Service

```bash
sudo cp 6.opena7_mail/deploy/opena7_mail.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start opena7_mail
sudo systemctl status opena7_mail
```

---

## Konfiguration

**Wichtig:** Mail-Passwörter gehören NIEMALS in `.env`! Verwende stattdessen einen Secret Store.

```bash
# .env.example kopieren und anpassen
cp 6.opena7_mail/.env.example .env

# Minimale Konfiguration:
MAIL_IMAP_HOST=imap.provider.at
MAIL_IMAP_PORT=993
MAIL_SMTP_HOST=smtp.provider.at
MAIL_SMTP_PORT=587
MAIL_USER=bot@example.org
MAIL_PASS_ENVKEY=ENV:MAIL_PASS_TOKEN  # Secret Store!
MAIL_ALLOWLIST=@example.org,@partners.de
AUTOREPLY_ENABLED=true
```

---

## Quickstart

### 1. Health-Check

```bash
curl http://127.0.0.1:12350/health | jq .
```

**Antwort:**

```json
{
  "service": "opena7",
  "status": "ok",
  "component": "mail",
  "port": 12350,
  "mailbox": "bot@example.org",
  "imap_connected": true,
  "smtp_connected": true,
  "ts": "2025-11-10T14:00:00Z"
}
```

### 2. Mails abrufen (Fetch)

```bash
curl -X POST http://127.0.0.1:12350/run \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "test-001",
    "action": "fetch",
    "payload": {
      "mailbox": "INBOX",
      "max_count": 5
    }
  }' | jq .
```

**Antwort:**

```json
{
  "request_id": "test-001",
  "status": "success",
  "action": "fetch",
  "processed": 3,
  "succeeded": 3,
  "messages": [
    {
      "msg_id": "12345",
      "subject": "Important: System Alert",
      "sender": "alerts@partners.de",
      "recipients": ["bot@example.org"],
      "date": "2025-11-10T13:55:00Z",
      "body_text": "System status: All green.",
      "body_preview": "System status: All green.",
      "sentiment": "neutral",
      "urgency": 5,
      "language": "en",
      "attachments": []
    }
  ],
  "processing_ms": 2340
}
```

### 3. Mails mit Auto-Reply

```bash
curl -X POST http://127.0.0.1:12350/run \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "test-002",
    "action": "fetch_and_reply",
    "payload": {
      "mailbox": "support@example.org",
      "mode": "unread_only",
      "reply_template": "templates/auto_reply.md",
      "max_count": 10
    }
  }' | jq .
```

### 4. Mail versenden

```bash
curl -X POST http://127.0.0.1:12350/run \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "test-003",
    "action": "send",
    "payload": {
      "recipient": "user@example.org",
      "subject": "Important Update",
      "body_text": "Your request has been processed."
    }
  }' | jq .
```

---

## API-Referenz

### Aktionen (Actions)

| Aktion | Beschreibung | Payload |
|--------|-------------|---------|
| `fetch` | Abrufen neuer Mails | `mailbox`, `max_count`, `mode` |
| `fetch_and_reply` | Abrufen + Auto-Reply | `mailbox`, `reply_template`, `max_count` |
| `send` | Mail versenden | `recipient`, `subject`, `body_text` |
| `mark_spam` | Als Spam markieren | `msg_id`, `mailbox` |
| `delete` | Löschen | `msg_id`, `mailbox` |
| `forward` | Weiterleiten | `msg_id`, `to`, `mailbox` |

### Klassifizierung

**Sentiment-Analyse:**

- `positive` — Zufriedene/dankbare Nachrichten
- `neutral` — Informativ
- `negative` — Probleme/Beschwerden
- `urgent` — Dringende Anfragen

**Dringlichkeit (0-10):**

- 0-3: Low Priority
- 4-6: Normal
- 7-9: High Priority
- 10: Critical/URGENT

**Sprache:**

- `en` — English
- `de` — Deutsch
- `null` — Unbekannt

### Fehlerbehandlung

**Fehlercodes:**

| Code | Ursache | Aktion |
|------|--------|--------|
| `AUTH_FAILED` | Login fehlgeschlagen | Credentials prüfen, Retry |
| `MAILBOX_LOCKED` | IMAP-Lock aktiv | Auto-Backoff 60s |
| `SMTP_REJECTED` | Empfänger nicht akzeptiert | NACK, Report an opena2 |
| `ATTACHMENT_TOO_LARGE` | > Size-Limit | Attachment skip, Warnung |
| `VIRUS_DETECTED` | Attachment verdächtig | Mail blockiert, Audit-Log |

**Error-Response:**

```json
{
  "request_id": "test-001",
  "status": "failed",
  "error_code": "AUTH_FAILED",
  "error_message": "IMAP authentication failed: Invalid credentials",
  "retryable": false
}
```

---

## Sicherheit & Compliance

### Domain Allowlist

Nur E-Mails von vertrauenswürdigen Absendern werden verarbeitet:

```bash
MAIL_ALLOWLIST=@example.org,@partners.de,trusted@vendor.com
```

**Enforcement:** Vor Verarbeitung wird der Absender geprüft. Bei Mismatch: NACK.

### Attachment-Sicherheit

```bash
# Gefährliche Dateitypen
.exe, .dll, .zip, .rar, .bat, .cmd, .scr, .vbs, .js

# Größenlimit
MAIL_ATTACHMENT_LIMIT_MB=25

# Scanning
SCAN_ATTACHMENTS=true  # ClamAV-Hook
```

### PII-Schutz

- Passwörter, Tokens, IBANs = **NICHT** im Klartext
- Secrets via `ENV:ENVKEY` (Secret Store)
- Logs automatisch reduziert (Passwörter maskiert)

### Audit-Trail

Jede Mail-Operation erzeugt einen Safepoint via opena2:

```json
{
  "ts": "2025-11-10T14:00:00Z",
  "src": "opena7",
  "dst": "opena2",
  "kind": "RESP",
  "request_id": "test-001",
  "action": "fetch",
  "payload": {...}
}
```

---

## Monitoring & Observability

### Health-Endpoints

```bash
# Health
curl http://127.0.0.1:12350/health

# Metriken (Prometheus)
curl http://127.0.0.1:12350/metrics

# Status
curl http://127.0.0.1:12350/api/status
```

### Metriken

```
opena7_mail_in_total — Total inbound emails
opena7_mail_out_total — Total outbound emails
opena7_errors_total — Processing errors
opena7_attachment_bytes_total — Attachment volume
opena7_processing_seconds_bucket — Latency histogram
```

### Logs (JSONL)

```bash
# Abrufen
ls logs/opena7/2025/11/10/*.jsonl

# Format (jede Zeile ein Event):
{
  "ts": "2025-11-10T14:00:00.512Z",
  "request_id": "test-001",
  "action": "fetch",
  "msg_id": "12345",
  "sender": "user@example.org",
  "status": "ok",
  "processing_ms": 2150
}
```

---

## Best Practices

✅ **DO:**

- TLS/SSL erzwingen (Port 993 für IMAP, 587 für SMTP)
- Allowlist verwenden (Domain-Einschränkung)
- Secrets via Secret Store (keine .env)
- Regelmäßig Logs archivieren
- Metriken monitoren (Error-Rate, Latenz)

❌ **DON'T:**

- Passwörter im Klartext speichern
- Zu große Attachment-Limits
- Robots-ähnliche Flooding-Pattern
- Sensitive Daten im Response-Log
- Alte Mails unkontrolliert speichern

---

## Troubleshooting

### IMAP Connection Failed

```bash
# Logs prüfen
tail -f logs/opena7.nohup.log

# Manual Test
python3 -c "
import imaplib
imap = imaplib.IMAP4_SSL('imap.provider.at', 993)
imap.login('bot@example.org', 'password')
print('✅ Connected')
imap.logout()
"
```

### Authentication Error

```bash
# Credentials prüfen
echo \$MAIL_PASS_ENVKEY

# Secret Store Test
curl http://127.0.0.1:12345/secret/get?key=MAIL_PASS_TOKEN

# Manueller Login
echo -ne "\x00bot@example.org\x00password" | openssl s_client -connect imap.provider.at:993
```

### Attachment Processing Issues

```bash
# Größenlimit erhöhen
MAIL_ATTACHMENT_LIMIT_MB=50

# Gefährliche Erweiterungen erlauben
# (Nur mit explizitem Antivirus!)

# Logs prüfen
grep "attachment" logs/opena7.nohup.log
```

---

## Tests

### Unit Tests (ohne Mail-Server)

```bash
pytest tests/test_mail_service.py -v

# Nur Mock-Tests
pytest tests/test_mail_service.py::TestMockMailClient -v

# Coverage
pytest tests/test_mail_service.py --cov=6.opena7_mail
```

### Integration Tests

```bash
# Benötigt konfigurierte Mail-Server
pytest tests/test_mail_service.py::TestMailClient -v

# Einzelner Test
pytest tests/test_mail_service.py::TestMailClassifier::test_sentiment_classification -v
```

---

## Performance SLOs

| Metrik | Ziel |
|--------|------|
| **Verfügbarkeit** | ≥ 99.5% |
| **Fetch-Latenz** | ≤ 5s (10 Mails) |
| **Send-Latenz** | ≤ 2s |
| **Error-Rate** | < 1% |
| **Durchsatz** | ≥ 100 Mails/min |

---

## Support & Debugging

```bash
# Live-Logs
tail -f logs/opena7.nohup.log

# Metriken live
watch -n 1 'curl -s http://127.0.0.1:12350/metrics | head -20'

# Health-Loop
while true; do
  curl -s http://127.0.0.1:12350/health | jq .
  sleep 2
done

# Archive-Index
curl http://127.0.0.1:12345/archiv/last?n=10 | jq '.items[] | select(.payload.src=="opena7")'
```

---

**Letzte Aktualisierung:** 27. November 2025  
**Status:** ✅ Production
