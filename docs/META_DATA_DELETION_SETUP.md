# Meta WhatsApp Data Deletion Callback Setup

## 📋 Überblick

Dieses Setup stellt die **GDPR/Privacy-Compliance** für deine WhatsApp Business App sicher, indem es automatisch Nutzerdaten löscht, wenn diese bei Facebook/Meta eine Löschung beantragen.

## 🔧 Setup Schritte

### 1. Environment Konfiguration

Bearbeite `.env` und setze:

```bash
# Meta App Credentials
META_APP_SECRET=dein_facebook_app_secret
META_ACCESS_TOKEN=dein_access_token
META_PHONE_NUMBER_ID=deine_phone_number_id

# Data Deletion Service
DATA_DELETION_PORT=12370
BASE_URL=https://deine-domain.com  # Öffentlich erreichbare URL
```

### 2. Service starten

```bash
# Data Deletion Callback starten
bash bin/start_data_deletion.sh

# Überprüfung
curl http://127.0.0.1:12370/health
```

### 3. Facebook Developer Console Konfiguration

1. Gehe zu: [Facebook for Developers](https://developers.facebook.com/apps/)
2. Wähle deine WhatsApp Business App
3. Navigiere zu: **App Settings** → **Basic**
4. Scrolle zu: **Data Deletion Request Callback URL**
5. Setze: `https://deine-domain.com:12370/data-deletion-callback`
6. Speichern

### 4. Webhook URLs (zusätzlich)

**WhatsApp Webhook:**

- **Callback URL**: `https://deine-domain.com:12351/webhook`
- **Verify Token**: Der Wert aus `.env` → `META_WEBHOOK_VERIFY_TOKEN`

## 🧪 Testing

### Lokaler Test:

```bash
# Simuliere signed request
curl -X POST http://127.0.0.1:12370/data-deletion-callback \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "signed_request=test.payload"

# Status Check
curl "http://127.0.0.1:12370/deletion-status?code=abc123"
```

### Facebook Test:

1. In Facebook: **Apps and Websites** → Deine App entfernen
2. **View Removed Apps** → **Send Request** klicken
3. Facebook sendet POST an deinen Callback
4. Überprüfe Logs: `tail -f logs/data_deletion.log`

## 📂 Datenstrukturen

### Deletion Request Format:

```json
{
  "user_id": "218471",
  "confirmation_code": "abc123def456",
  "requested_at": "2025-11-12T10:30:00",
  "status": "pending|completed|error",
  "completed_at": "2025-11-12T10:35:00"
}
```

### Response Format (Required):

```json
{
  "url": "https://deine-domain.com:12370/deletion-status?code=abc123",
  "confirmation_code": "abc123def456"
}
```

## 🗂️ Was wird gelöscht?

1. **WhatsApp Nachrichten**: `data/messages/*user_id*`
2. **Archiv-Einträge**: Entfernt aus `archivp/archivp_store/index.jsonl`
3. **Log-Dateien**: Zeilen mit `user_id` werden entfernt
4. **Temporäre Daten**: Alle lokalen User-bezogenen Dateien

## 🔍 Status Tracking

Jede Löschung wird gespeichert in:

```
data/deletion_requests/deletion_{code}.json
```

Nutzer können Status prüfen mit:

```
https://deine-domain.com:12370/deletion-status?code={confirmation_code}
```

## ⚠️ Wichtige Hinweise

1. **Produktionsumgebung**: `BASE_URL` muss öffentlich erreichbar sein (HTTPS)
2. **SSL/TLS**: Facebook verlangt HTTPS für Callbacks
3. **App Secret**: Niemals in Git committen, nur in `.env`
4. **Backup**: Löschungen sind irreversibel
5. **Compliance**: Response muss innerhalb 30 Sekunden erfolgen

## 🚨 Troubleshooting

### Problem: "Invalid signed_request"

- **Ursache**: Falscher `META_APP_SECRET`
- **Lösung**: App Secret aus Facebook Developer Console kopieren

### Problem: "Callback URL nicht erreichbar"

- **Ursache**: Port 12370 nicht öffentlich erreichbar
- **Lösung**: Reverse Proxy (nginx) oder Ngrok verwenden

### Problem: "Missing user_id"

- **Ursache**: Signed Request Format falsch
- **Lösung**: Facebook Developer Tool verwenden für Test

## 📊 Monitoring

```bash
# Service Status
curl -s http://127.0.0.1:12370/health

# Aktive Löschungen
ls -la data/deletion_requests/

# Logs verfolgen
tail -f logs/data_deletion.log
```

## 📞 Support

Bei Problemen:

1. Prüfe Logs: `logs/data_deletion.log`
2. Teste Signed Request Parsing
3. Verifiziere App Secret in Facebook Console
4. Überprüfe Netzwerk-Erreichbarkeit

---

**Status**: ✅ GDPR-Compliant Data Deletion implementiert
**Port**: 12370
**Endpoints**: `/data-deletion-callback`, `/deletion-status`, `/health`
