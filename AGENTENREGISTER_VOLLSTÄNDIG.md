# 🧭 PORTIER-AGENTENARCHITEKTUR — VOLLSTÄNDIGES REGISTER

**Version:** 2.0 (Definitive Produktionsübersicht)
**Gültig ab:** 2025-11-24
**Portbereich:** 12344 – 12399 (Regel: 8080 nur OpenWebUI, alle anderen Agents vom Pool)
**Kommunikationsmodell:** Option 2 (Zentraler Archiv-Agent)

---

## 🔗 Quick Navigation

| Document | Purpose |
|----------|---------|
| **QUICK_START.md** | Start here (5 min setup) |
| **MASTERPROMPT_OPENWEBUI.md** | 4-Phase initialization system |
| **API_REFERENCE.md** | REST API documentation |
| **SECURITY_AUDIT_REPORT.md** | Security & compliance |
| **FUNCTIONAL_TEST_REPORT.md** | Test results & coverage |
| **DEPLOYMENT_GUIDE.md** | Production deployment |
| **AUDIT_REPORT_2025-11-24.md** | Final system audit |

---

## 🎯 KERNARCHITEKTUR

```
OpenAI-API
    ↓
┌─────────────────────────────────────────────────────────────┐
│                    opena1 (KOORDINATOR)                     │
│  • Validiert Anfragen                                       │
│  • Wählt Ziel-Agent                                         │
│  • Triggert Safepoints über opena2                          │
│  • Port: 12344                                              │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│               opena2 (ARCHIV-AGENT / ARCHIVATOR)            │
│  • Schreibt CMD/RESP Safepoints                             │
│  • Pflegt Index + DB                                        │
│  • Koordiniert kordp                                        │
│  • Port: 12345                                              │
│  • Archivpfad: archivp/YYYY/MM/DD/                          │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│                kordp (KOORDINAT-PORT)                       │
│  • Transport-Layer (zustandslos)                            │
│  • Dispatch zu Ziel-Agent                                   │
│  • Port: 12346                                              │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│           opena(3–19) — FACH-AGENTEN                        │
│  • Führen Aufgabe aus                                       │
│  • Senden Response zurück → opena2 → opena1 → OpenAI       │
│  • Ports: 12347 – 12362                                     │
└─────────────────────────────────────────────────────────────┘

RÜCKWEG: Ziel-Agent → opena2 → opena1 → OpenAI
REGEL: Alle Bewegungen archivieren über opena2!
```

---

## 📋 AGENTENREGISTER (1–20)

### 🔴 **opena1 — KOORDINATOR**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Zentrale Steuerinstanz; Validierung, Delegation, Safepoint-Triggering |
| **Aufgaben** | • Empfängt OpenAI-Befehle<br>• Parsed Intent & Parameter<br>• Bestimmt Ziel-Agent<br>• Ruft opena2.store_safepoint() auf<br>• Dispatcht über kordp<br>• Sammelt Response |
| **Standort** | `/home/danijel-jd/.../1.opena1&2_portier/opena1/` |
| **Port(e)** | `12344` (HTTP/REST) |
| **Endpunkte** | • `GET /health` → `{"status": "online", "uptime": "..."}` |
| | • `POST /command` → akzeptiert OpenAI-JSON, parsed & dispatcht |
| | • `GET /logs` → zeigt aktuelle opena1-Logs |
| **Abhängigkeiten** | → opena2 (Safepoint-Speicherung) |
| | → kordp (Dispatch) |
| **Besonderheit** | **Keine direkten Operationen!** Nur Entscheidungs- + Delegationslogik. |

**Typischer Workflow:**
```python
POST /command
{
  "user_id": "user123",
  "message": "Schreib mir einen Blog-Post über Python",
  "intent": "content_generation",
  "target_agent": "opena15_html"
}

# opena1:
1. Validiert Input
2. Ruft opena2.store_safepoint(cmd=..., source="opena1", target="opena15")
3. Dispatcht über kordp zu opena15_html
4. Wartet auf Response
5. Archiviert RESP in opena2
6. Returniert zu OpenAI
```

---

### 🔵 **opena2 — ARCHIV-AGENT / ARCHIVATOR**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Persistence Layer; schreibt alle CMD/RESP, verwaltet Index, koordiniert kordp |
| **Aufgaben** | • Empfängt Safepoints von opena1 (CMD)<br>• Schreibt in archivp/YYYY/MM/DD/<br>• Pflegt Index-DB (SQLite/JSON)<br>• Speichert RESP nach Ausführung<br>• Koordiniert kordp für Dispatch<br>• Bietet Archiv-Query-API |
| **Standort** | `/home/danijel-jd/.../1.opena1&2_portier/opena2/` |
| **Port(e)** | `12345` (HTTP/REST) |
| **Endpunkte** | • `GET /health` → Health-Status |
| | • `POST /store/archivp` → speichert CMD/RESP<br>  ```{ "type": "cmd|resp", "source": "opena1", "target": "opena15", "payload": {...}, "timestamp": "..." }``` |
| | • `GET /finalize/opena2` → zeigt Archiv-Index |
| | • `GET /index?date=2025-11-24` → listet alle Safepoints |
| **Abhängigkeiten** | → archivp (physisch: Dateisystem) |
| | ← opena1 (CMD-Quelle) |
| | ← opena(3–19) (RESP-Quelle) |
| **Besonderheit** | **Zentraler Hub für Nachvollziehbarkeit!** Jede Bewegung = Audit Trail. |

**Archivstruktur:**
```
archivp/
├─ 2025/
│   └─ 11/
│       └─ 24/
│           ├─ opena1_to_opena15_001.json    (CMD)
│           ├─ opena15_to_opena2_001.json    (RESP)
│           ├─ opena1_to_opena7_002.json     (CMD)
│           ├─ opena7_to_opena2_002.json     (RESP)
│           └─ index.db  (SQLite: alle Einträge mit Hash + Status)
```

---

### ⚪ **kordp — KOORDINAT-PORT**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Transport-Layer; zustandslos, skalierbar, führt Dispatch aus |
| **Aufgaben** | • Empfängt Dispatch-Order von opena2<br>• Schickt HTTP-Request an Ziel-Agent<br>• Wartet auf Antwort<br>• Sendet Antwort zurück an opena2<br>• Loggt Transfers |
| **Standort** | `/home/danijel-jd/.../1.opena1&2_portier/kordp/` |
| **Port(e)** | `12346` (HTTP/REST) |
| **Endpunkte** | • `GET /health` → Health-Status |
| | • `POST /dispatch/kordp` → akzeptiert Dispatch-Order |
| | • `GET /transfers` → zeigt laufende/historische Transfers |
| **Abhängigkeiten** | ← opena2 (Dispatch-Order) |
| | → opena(3–19) (Request) |
| **Besonderheit** | **Keine Entscheidung — nur Transport!** → Ermöglicht einfache Skalierung. |

**Dispatch-Beispiel:**
```python
POST /dispatch/kordp
{
  "target_agent": "opena15_html",
  "target_port": 12358,
  "cmd_id": "cmd_001",
  "payload": {
    "message": "Erstelle HTML-Seite",
    "user_id": "user123"
  }
}

# kordp:
1. Schickt POST zu http://127.0.0.1:12358/execute
2. Wartet auf Response
3. Sendet Antwort zurück zu opena2
4. Loggt Transfer
```

---

### 🔐 **archivp — ARCHIV-PORT (Physisch)**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Physische Ablage; Dateisystem-basiert, nur über opena2 zugänglich |
| **Struktur** | `archivp/YYYY/MM/DD/` (tagesweise) |
| **Zugriff** | • Nur über opena2 REST-API |
| | • Kein direkter Dateisystem-Zugriff |
| **Inhalte** | • CMD-Safepoints (JSON)<br>• RESP-Safepoints (JSON)<br>• Index-DB (SQLite)<br>• Hash-Prüfsummen |
| **Besonderheit** | **IMMUTABLE nach Schreibvorgabe.** Keine Löschung, nur Append. |

---

## 🧩 FACH-AGENTEN (3 – 19)

### ⚫ **opena3 — OpenWebUI GATEWAY**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Web-Benutzeroberfläche; Chat-Gateway, UI-Loopback |
| **Aufgaben** | • Empfängt User-Input (Browser)<br>• Leitet an opena1 weiter<br>• Zeigt Responses grafisch<br>• Session-Management |
| **Standort** | `/home/danijel-jd/.../2.openwebui/` |
| **Port(e)** | `8080` (**nur Loopback: 127.0.0.1:8080**) |
| **Endpunkte** | • `GET /` → HTML-Chat-UI |
| | • `POST /send` → User-Message an opena1 |
| | • `GET /history` → Chat-Verlauf |
| **Abhängigkeiten** | → opena1 (über HTTP) |
| **Besonderheit** | **Port 8080 RESERVIERT für OpenWebUI.** Alle anderen: 12344–12399. |

---

### 🔷 **opena4 — TELEGRAM CONNECTOR**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Telegram Bot; empfängt/sendet Messages, Webhook-basiert |
| **Aufgaben** | • Empfängt Telegram-Nachrichten (Webhook)<br>• Delegiert an opena1<br>• Sendet Responses zurück zu Telegram<br>• Verwaltet User-Sessions |
| **Standort** | `/home/danijel-jd/.../3.opena4_telegram/` |
| **Port(e)** | `12347` |
| **Endpunkte** | • `GET /health` |
| | • `POST /inbox` → empfängt Telegram-Updates |
| | • `POST /outbox` → sendet Telegram-Nachrichten |
| | • `GET /sessions` → aktive Chat-Sessions |
| **Abhängigkeiten** | → opena1 (delegiert Nachrichten) |
| | ← Telegram API (Webhook) |
| **Besonderheit** | **Asynchron & Event-basiert.** Kein Polling. |

---

### 🔶 **opena5 — VS CODE BRIDGE**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Development Bridge; Editor-Sync, File-Push zwischen IDE und Portier |
| **Aufgaben** | • Monitort VS Code für Änderungen<br>• Pusht Datei-Änderungen zu opena1<br>• Zieht Lint/Format-Vorschläge<br>• Speichert Sync-State |
| **Standort** | `/home/danijel-jd/.../4.opena5_vscode/` |
| **Port(e)** | `12348` |
| **Endpunkte** | • `GET /health` |
| | • `POST /sync` → Datei-Sync-Trigger |
| | • `POST /push` → pusht Datei an opena1 |
| | • `GET /lint` → Lint-Vorschläge |
| **Abhängigkeiten** | → opena1 (Dispatch)<br>← VS Code Extension (WebSocket/Polling) |
| **Besonderheit** | **Baut auf bestehender Extension auf.** Kein Breaking Change. |

---

### 🔸 **opena6 — BROWSER AUTOMATION AGENT**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Automatisierte Web-Steuerung; Selenium/Playwright |
| **Aufgaben** | • Navigiert zu URLs<br>• Klickt Buttons, füllt Formulare<br>• Capturen von Screenshots<br>• Scraping von Inhalten |
| **Standort** | `/home/danijel-jd/.../5.opena6_browser/` |
| **Port(e)** | `12349` |
| **Endpunkte** | • `GET /health` |
| | • `POST /navigate` → `{ "url": "...", "actions": [...] }` |
| | • `GET /screenshot` → Screenshot des aktuellen State |
| | • `POST /scrape` → Scraping-Regel |
| **Abhängigkeiten** | → opena1 (Befehle)<br>← Chrome/Firefox (lokal) |
| **Besonderheit** | **Erfordert lokale Browser-Installation.** Headless oder GUI. |

---

### 🟠 **opena7 — E-MAIL CHATBOT**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Mail In/Out Automation; IMAP + SMTP |
| **Aufgaben** | • Monitort IMAP-Postfach<br>• Parsed E-Mails in strukturierte Befehle<br>• Delegiert an opena1<br>• Sendet Responses via SMTP<br>• Verwaltet Anhänge |
| **Standort** | `/home/danijel-jd/.../6.opena7_mail/` |
| **Port(e)** | `12350` |
| **Endpunkte** | • `GET /health` |
| | • `POST /mail/in` → neue E-Mails (Push-Trigger) |
| | • `POST /mail/out` → E-Mail senden |
| | • `GET /inbox` → Mailbox-Status |
| **Abhängigkeiten** | → opena1 (Befehle)<br>← IMAP/SMTP (konfigurierte Accounts) |
| **Besonderheit** | **Polling oder Push?** Beide Modi. Konfigurierbar pro Mailbox. |

---

### 🟡 **opena8 — WHATSAPP CHATBOT**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | WhatsApp Business API Connector |
| **Aufgaben** | • Empfängt WhatsApp-Nachrichten (Webhook)<br>• Delegiert an opena1<br>• Sendet Responses via WhatsApp-API<br>• Verwaltet Medien (Bilder, Dokumente) |
| **Standort** | `/home/danijel-jd/.../7.opena8_whats/` |
| **Port(e)** | `12351` |
| **Endpunkte** | • `GET /health` |
| | • `POST /msg/in` → empfängt Nachrichten |
| | • `POST /msg/out` → sendet Nachrichten |
| | • `POST /media` → Media-Upload |
| **Abhängigkeiten** | → opena1 (Befehle)<br>← WhatsApp Business API |
| **Besonderheit** | **API-Tokens sicher lagern** (Environment/Vault). |

---

### 🟢 **opena9 — TELEFON-ANTWORT BOT (Inbound)**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Spracherkennung + TTS; Inbound-Anrufe |
| **Aufgaben** | • Empfängt Anruf (Asterisk/FreePBX oder Cloud-API)<br>• Spracherkennung (STT)<br>• Delegiert Text an opena1<br>• Sprachsynthese (TTS) der Response<br>• Hangup-Handling |
| **Standort** | `/home/danijel-jd/.../8.opena9_voicein/` |
| **Port(e)** | `12352` |
| **Endpunkte** | • `GET /health` |
| | • `POST /call/in` → neuer Anruf |
| | • `POST /stt` → Transkription |
| | • `POST /tts` → Text → Audio |
| **Abhängigkeiten** | → opena1 (Befehle)<br>← PBX/SIP (Anruf-Empfang)<br>← STT/TTS-Engine (lokal oder Cloud) |
| **Besonderheit** | **Latenz kritisch.** Real-time Processing erforderlich. |

---

### 🔵 **opena10 — TELEFON-ANRUF BOT (Outbound)**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Outbound-Calls / Benachrichtigungen |
| **Aufgaben** | • Startet Outbound-Call auf Ziel-Nummer<br>• Liest Text via TTS<br>• Akzeptiert Drücktasten-Input (DTMF)<br>• Fehler-Handling (busy, no-answer) |
| **Standort** | `/home/danijel-jd/.../9.opena10_voiceout/` |
| **Port(e)** | `12353` |
| **Endpunkte** | • `GET /health` |
| | • `POST /call/out` → `{ "to": "+49...", "message": "...", "dtmf_expected": true }` |
| | • `GET /calls` → laufende/historische Calls |
| **Abhängigkeiten** | → opena1 (Befehle)<br>← PBX/SIP (Call-Initiierung)<br>← TTS-Engine |
| **Besonderheit** | **Kostenüberwachung!** Jeder Call = Kostenpunkt. Logging essentiell. |

---

### 🟣 **opena11 — UNLOCK MASTER (Authentifizierung & Override)**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Sicherheit & Notfall-Override; Multi-Factor-Auth, Backup-Codes |
| **Aufgaben** | • Validiert Benutzer-Authentifizierung (MFA)<br>• Generiert/speichert Backup-Codes<br>• Emergency-Override (Admin-only)<br>• Audit-Logs für Unlock-Events |
| **Standort** | `/home/danijel-jd/.../10.opena11_unlock/` |
| **Port(e)** | `12354` |
| **Endpunkte** | • `GET /health` |
| | • `POST /verify` → `{ "user_id": "...", "mfa_code": "..." }` |
| | • `POST /unlock` → Emergency-Override (Admin) |
| | • `GET /audit` → Audit-Logs |
| **Abhängigkeiten** | ← opena1 (bei kritischen Ops)<br>← User-DB (lokal/LDAP) |
| **Besonderheit** | **KRITISCH für Sicherheit.** Nur Admin-Zugriff. |

---

### 🟠 **opena12 — SOCIAL MEDIA AUTOMATION**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Planung & Posting; Facebook, X (Twitter), LinkedIn |
| **Aufgaben** | • Plant Posts für mehrere Plattformen<br>• Schedulet Veröffentlichung<br>• Managed Bilder/Videos/Links<br>• Verwaltet Hashtags & Kampagnen<br>• API-Sync mit Plattformen |
| **Standort** | `/home/danijel-jd/.../11.opena12_socialauto/` |
| **Port(e)** | `12355` |
| **Endpunkte** | • `GET /health` |
| | • `POST /schedule` → `{ "platforms": ["fb", "x", "linkedin"], "content": "...", "schedule_time": "..." }` |
| | • `POST /publish` → sofortiges Posting |
| | • `GET /queue` → geplante Posts |
| **Abhängigkeiten** | → opena1 (Befehle)<br>← Facebook/X/LinkedIn APIs |
| **Besonderheit** | **Erfordert API-Credentials** pro Plattform. Rate-Limits beachten. |

---

### 🟡 **opena13 — INFLUENCER AGENT**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Content-Optimierung + Engagement-Analyse |
| **Aufgaben** | • Analyzed Engagement-Metriken<br>• Optimiert Hashtags/Wording<br>• Generiert Content-Vorschläge<br>• Tracked Influencer-Performance<br>• A/B-Testing Support |
| **Standort** | `/home/danijel-jd/.../12.opena13_influencer/` |
| **Port(e)** | `12356` |
| **Endpunkte** | • `GET /health` |
| | • `POST /analyze` → `{ "post_id": "...", "platform": "..." }` |
| | • `POST /optimize` → Content-Optimierungsvorschläge |
| | • `GET /metrics` → Performance-Metriken |
| **Abhängigkeiten** | → opena1 (Befehle)<br>← Social Media APIs (Daten-Fetch) |
| **Besonderheit** | **Data-Heavy.** Requires caching + Batch-Processing. |

---

### 🟢 **opena14 — CALENDAR AGENT**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Terminverwaltung; Sync mit Google/Outlook |
| **Aufgaben** | • Synct mit Google Calendar / Outlook<br>• Erstellt/ändert/löscht Events<br>• Verwaltet Einladungen<br>• Reminder-Management<br>• Verfügbarkeits-Abfragen |
| **Standort** | `/home/danijel-jd/.../13.opena14_calendar/` |
| **Port(e)** | `12357` |
| **Endpunkte** | • `GET /health` |
| | • `POST /events` → erstellt Event |
| | • `GET /availability` → `{ "date": "...", "duration": "..." }` |
| | • `POST /sync` → manueller Sync mit Google/Outlook |
| **Abhängigkeiten** | → opena1 (Befehle)<br>← Google Calendar / Outlook API |
| **Besonderheit** | **OAuth2-Refresh-Token Management essentiell.** Timeout-Handling. |

---

### 🔵 **opena15 — HTML CREATOR**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Webseiten-Abschnitte / Landing Pages generieren |
| **Aufgaben** | • Generiert HTML aus Vorlagen oder KI-Prompts<br>• CSS-Integration (inline oder external)<br>• Responsiveness-Check<br>• Asset-Management (Bilder, Fonts)<br>• Export zu Dateiensystem |
| **Standort** | `/home/danijel-jd/.../14.opena15_html/` |
| **Port(e)** | `12358` |
| **Endpunkte** | • `GET /health` |
| | • `POST /render` → `{ "template": "landing", "content": {...} }` |
| | • `GET /preview` → HTML-Preview |
| | • `POST /export` → speichert zu Datei |
| **Abhängigkeiten** | → opena1 (Befehle)<br>← Dateisystem (Ablage) |
| **Besonderheit** | **Kann aus opena2-Archiv Kontext laden.** Keine externen CDNs (lokale Assets). |

---

### 🟣 **opena16 — SHOP CREATOR**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | E-Commerce-Module; Produkt-/Bestellverwaltung |
| **Aufgaben** | • Generiert Produkt-Katalog (HTML/JSON)<br>• Verwaltet Warenkorb & Checkout<br>• Integriert mit Payment-Gateways (Stripe, PayPal)<br>• Trackst Bestellungen<br>• Managed Inventar |
| **Standort** | `/home/danijel-jd/.../15.opena16_shop/` |
| **Port(e)** | `12359` |
| **Endpunkte** | • `GET /health` |
| | • `POST /catalog` → generiert Produktliste |
| | • `POST /order` → erstellt Bestellung |
| | • `GET /orders` → Bestellverlauf |
| | • `POST /payment` → zahlungsabwicklung (Webhook) |
| **Abhängigkeiten** | → opena1 (Befehle)<br>← Payment-Gateways (Stripe, PayPal)<br>← Bestellverwaltungs-DB |
| **Besonderheit** | **PCI-DSS Compliance erforderlich!** Keine direkten Kartendetails. |

---

### 🟠 **opena17 — HOMEPAGE CREATOR**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Vollständiger Webpräsenz-Generator (CMS-Export) |
| **Aufgaben** | • Generiert komplette Website (Multi-Page)<br>• Managed Navigation & Struktur<br>• SEO-Optimierung (Meta-Tags, Sitemap)<br>• Sitemap + Robots.txt Generierung<br>• CMS-Export (z.B. zu WordPress) |
| **Standort** | `/home/danijel-jd/.../16.opena17_homepage/` |
| **Port(e)** | `12360` |
| **Endpunkte** | • `GET /health` |
| | • `POST /site/create` → `{ "name": "...", "pages": [...] }` |
| | • `POST /deploy` → exportiert zu lokalen/Remote-Hosting |
| | • `GET /seo/check` → SEO-Audit |
| **Abhängigkeiten** | → opena1 (Befehle)<br>← opena15 (HTML-Rendering)<br>← Hosting-API (FTP/SSH) |
| **Besonderheit** | **Orchestriert opena15 für Pages.** Baukasten-Ansatz. |

---

### 🟡 **opena18 — LOCAL ARCHIV AGENT**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Lokale/Offline-Spiegelung; Backup auf Medien |
| **Aufgaben** | • Synct archivp zu lokalen Medien (USB, HDD)<br>• Komprimiert alte Archiv-Dateien<br>• Managed Retention Policy<br>• Offline-Query-Support<br>• Disaster-Recovery Setup |
| **Standort** | `/home/danijel-jd/.../17.opena18_localarch/` |
| **Port(e)** | `12361` |
| **Endpunkte** | • `GET /health` |
| | • `POST /sync/local` → startet Backup-Sync |
| | • `POST /backup` → Full/Incremental Backup |
| | • `GET /status` → Backup-Status |
| **Abhängigkeiten** | ← opena2 (liest archivp)<br>← Lokale/externe Medien |
| **Besonderheit** | **Asynchron.** Läuft im Hintergrund. Cron-Job freundlich. |

---

### 🟢 **opena19 — AKTIEN & CRYPTO AGENT**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Datenfeeds, Preise, Alerts, Reporting |
| **Aufgaben** | • Fetcht Live-Preise (Aktien, Crypto)<br>• Managed Alerts (Preis-Schwelle)<br>• Generates Berichte (täglich/wöchentlich)<br>• Tracked Portfolio<br>• Newsfeeds zu Assets |
| **Standort** | `/home/danijel-jd/.../18.opena19_finance/` |
| **Port(e)** | `12362` |
| **Endpunkte** | • `GET /health` |
| | • `POST /market` → Preis-Query |
| | • `POST /alert` → erstellt Preisalert |
| | • `GET /portfolio` → Portfolio-Übersicht |
| | • `GET /report` → generiert Bericht |
| **Abhängigkeiten** | → opena1 (Befehle)<br>← Market-Data APIs (Alpha Vantage, CoinGecko etc.) |
| **Besonderheit** | **API-Rate-Limits beachten.** Caching essentiell. |

---

### 🔷 **opena20 — DASHBOARD AGENT (Monitoring)**

| Eigenschaft | Wert |
|---|---|
| **Funktion** | Zentrale Visualisierung & Status-Monitor |
| **Aufgaben** | • Liest Health-Status aller opena(1–19)<br>• Sammelt Logs und Metriken<br>• Displays grafisches Dashboard (Web)<br>• Alert-Management<br>• System-Performance Überwachung |
| **Standort** | `/home/danijel-jd/.../19.dashboard_agent/` |
| **Port(e)** | `12363` |
| **Endpunkte** | • `GET /health` |
| | • `GET /health/all` → Health aller Agenten |
| | • `GET /metrics` → Aggregierte Metriken |
| | • `GET /dashboard` → HTML-Dashboard |
| | • `GET /logs` → Zentrale Logs |
| **Abhängigkeiten** | ← opena(1–19) (Health-Polling)<br>← opena2 (Archiv-Zugriff für Logs) |
| **Besonderheit** | **READ-ONLY Zugriff auf alle Agenten.** Kein direktes State-Management. |

**Dashboard-Beispiel:**
```
┌─────────────────────────────────────────────────────────────┐
│  🤖 OPENA DASHBOARD — 2025-11-24 14:32:45                  │
├─────────────────────────────────────────────────────────────┤
│  🟢 opena1 (Koordinator)        ✅ ONLINE  | Uptime: 48:12 │
│  🟢 opena2 (Archiv-Agent)       ✅ ONLINE  | Archiv: 2.3GB │
│  🟢 opena3 (OpenWebUI)          ✅ ONLINE  | Users: 5      │
│  🟢 opena4 (Telegram)           ✅ ONLINE  | Msgs: 142     │
│  🟢 opena5 (VS Code)            ✅ ONLINE  | Syncs: 23     │
│  🟡 opena7 (Mail)               ⚠️  WARN   | Queue: 8      │
│  🟢 opena15 (HTML Creator)      ✅ ONLINE  | Pages: 12     │
│  🔴 opena19 (Finance)           ❌ OFFLINE | Last: 2h ago  │
├─────────────────────────────────────────────────────────────┤
│  Last Errors: 3 | Total Requests (24h): 12,847             │
│  Avg Response Time: 145ms | Peak Load: 14:15 (2.3 req/s)   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 KOMMUNIKATIONSFLÜSSE

### Flow 1: User-Anfrage via OpenWebUI (opena3)

```
1. User tippt in OpenWebUI:  "Schreib mir eine Landing Page"
2. opena3 (OpenWebUI) → opena1 (Koordinator)
   POST http://127.0.0.1:12344/command
   {
     "user_id": "user123",
     "message": "Schreib mir eine Landing Page",
     "intent": "content_generation",
     "target_agent": "opena15"
   }

3. opena1 (Koordinator):
   a) Validiert Input
   b) Ruft opena2 auf: POST /store/archivp
      { "type": "cmd", "source": "opena1", "target": "opena15", "payload": {...} }
   c) Dispatcht über kordp: POST /dispatch/kordp
      { "target_agent": "opena15_html", "target_port": 12358, ... }

4. kordp (Transport):
   Sendet zu opena15: POST http://127.0.0.1:12358/execute
   { "message": "Schreib mir eine Landing Page", "user_id": "user123" }

5. opena15 (HTML Creator):
   a) Generiert HTML
   b) Sendet Response zu kordp
   c) kordp sendet zu opena2

6. opena2 (Archiv-Agent):
   a) Speichert Response in archivp/YYYY/MM/DD/
   b) Bestätigt zu opena1

7. opena1 (Koordinator):
   Sends Response zu opena3

8. opena3 (OpenWebUI):
   Zeigt HTML im Browser
```

---

### Flow 2: Telegram-Nachricht (opena4)

```
1. Nutzer sendet Telegram-Nachricht zu Bot

2. Telegram-Webhook → opena4 (Telegram Agent)
   POST http://127.0.0.1:12347/inbox
   { "user_id": "...", "message": "Was ist der BTC Preis?", "chat_id": "..." }

3. opena4:
   Delegiert an opena1: POST /command
   { "source": "telegram", "chat_id": "...", "message": "...", "target_agent": "opena19" }

4. opena1 → opena2 (Archiv) → kordp → opena19 (Finance Agent)
   [Wie in Flow 1]

5. opena19 (Finance):
   Fetcht BTC-Preis von API
   Sendet Response zurück

6. opena2 (Archiv):
   Speichert

7. opena1 → opena4 (Telegram Agent):
   Sends Response

8. opena4:
   Sendet Telegram-Nachricht zurück zu Bot:
   POST https://api.telegram.org/bot.../sendMessage
   { "chat_id": "...", "text": "BTC Preis: $43,250" }
```

---

### Flow 3: E-Mail-Anfrage (opena7)

```
1. E-Mail kommt an: "Erstelle einen Blog-Post über AI"

2. opena7 (Mail Agent) — monitort IMAP:
   Parsed E-Mail
   Delegiert an opena1: POST /command
   { "source": "email", "from": "user@...", "subject": "...", "target_agent": "opena15" }

3. opena1 → opena2 (Archiv) → kordp → opena15
   [Wie in Flow 1]

4. opena15 (HTML Creator):
   Generiert HTML mit Blog-Post

5. opena2 (Archiv) → opena1 → opena7

6. opena7:
   Sendet E-Mail zurück:
   SMTP: { "to": "user@...", "subject": "Re: Blog-Post erstellt", "body": "HTML..." }
```

---

### Flow 4: Scheduled Job via opena14 (Calendar)

```
1. Admin setzt Reminder: "Täglich 9 Uhr — generiere Daily Report"

2. opena14 (Calendar Agent):
   Scheduled Job triggered um 09:00 Uhr
   Sendet zu opena1: POST /command
   { "source": "schedule", "job_id": "daily_report", "target_agent": "opena19" }

3. opena1 → opena2 (Archiv) → kordp → opena19 (Finance)

4. opena19:
   Generiert Daily Financial Report
   Sendet Response

5. opena2 (Archiv) → opena1 → opena14

6. opena14:
   Erstellt Calendar-Event mit Report als Anhang
   Sendet Notification an User
```

---

## 🔐 SICHERHEIT & COMPLIANCE

### Authentication & Authorization
- **opena1 (Koordinator):** validiert Requests gegen User-DB + Permission-Matrix
- **opena11 (Unlock Master):** Multi-Factor Auth, Backup-Codes, Emergency-Override
- **opena2 (Archiv-Agent):** nur über opena1 erreichbar (keine direkten Requests)

### Data Protection
- **archivp (Archiv-Port):** IMMUTABLE, Append-Only
- **Encryption:** Safepoints können mit FERNET verschlüsselt werden (optional)
- **Audit Trail:** Jede Bewegung in opena2 archiviert mit Timestamp + Hash

### Rate Limiting
- **Pro Agent:** Max. X Requests/Minute (konfigurierbar)
- **Pro User:** Max. Y Requests/Stunde
- **Pro Source:** Telegram, Mail, Voice — separate Limits

### Whitelisting & Sandboxing
- **opena6 (Browser):** läuft in isoliertem Container (Docker optional)
- **opena7 (Mail):** nur konfigurierte IMAP/SMTP-Accounts
- **opena4 (Telegram):** nur autorisierte Chat-IDs

---

## 📊 PORTBEREICH — VOLLSTÄNDIGE ÜBERSICHT

| Port | Agent | Status |
|---|---|---|
| **8080** | opena3 (OpenWebUI) | **LOOPBACK ONLY** (127.0.0.1) |
| **12344** | opena1 (Koordinator) | HTTP/REST |
| **12345** | opena2 (Archiv-Agent) | HTTP/REST |
| **12346** | kordp (Transport) | HTTP/REST |
| **12347** | opena4 (Telegram) | HTTP/REST + Webhook |
| **12348** | opena5 (VS Code) | HTTP/REST + WebSocket |
| **12349** | opena6 (Browser) | HTTP/REST |
| **12350** | opena7 (Mail) | HTTP/REST |
| **12351** | opena8 (WhatsApp) | HTTP/REST + Webhook |
| **12352** | opena9 (Voice In) | HTTP/REST + SIP |
| **12353** | opena10 (Voice Out) | HTTP/REST + SIP |
| **12354** | opena11 (Unlock Master) | HTTP/REST |
| **12355** | opena12 (Social Media) | HTTP/REST |
| **12356** | opena13 (Influencer) | HTTP/REST |
| **12357** | opena14 (Calendar) | HTTP/REST |
| **12358** | opena15 (HTML Creator) | HTTP/REST |
| **12359** | opena16 (Shop Creator) | HTTP/REST |
| **12360** | opena17 (Homepage Creator) | HTTP/REST |
| **12361** | opena18 (Local Archiv) | HTTP/REST |
| **12362** | opena19 (Finance) | HTTP/REST |
| **12363** | opena20 (Dashboard) | HTTP/REST |

---

## 📁 DIRECTORY STRUCTURE (Zielzustand)

```
/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/
│
├─ 1.opena1&2_portier/                    ← Kern-System
│   ├─ opena1/                          (Koordinator, 12344)
│   │   ├─ main.py
│   │   ├─ config.json
│   │   └─ health.py
│   │
│   ├─ opena2/                          (Archiv-Agent, 12345)
│   │   ├─ main.py
│   │   ├─ store.py
│   │   └─ index.db (SQLite)
│   │
│   ├─ kordp/                           (Transport, 12346)
│   │   ├─ main.py
│   │   └─ dispatch.py
│   │
│   └─ archivp/                         (Physisches Archiv)
│       ├─ 2025/11/24/
│       │   ├─ opena1_to_opena15_001.json
│       │   ├─ opena15_to_opena2_001.json
│       │   └─ index.db
│       └─ backup/ (Local-Archiv Spiegeln)
│
├─ 2.openwebui/                         (OpenWebUI, Port 8080)
│   ├─ web_dashboard.py
│   ├─ index.html
│   └─ api/
│
├─ 3.opena4_telegram/                   (Telegram, 12347)
│   ├─ main.py
│   ├─ bot.py
│   └─ sessions/
│
├─ 4.opena5_vscode/                     (VS Code, 12348)
│   ├─ main.py
│   ├─ sync.py
│   └─ extension/ (VS Code Extension)
│
├─ 5.opena6_browser/                    (Browser, 12349)
│   ├─ main.py
│   ├─ selenium_driver.py
│   └─ screenshots/
│
├─ 6.opena7_mail/                       (Mail, 12350)
│   ├─ main.py
│   ├─ imap_monitor.py
│   ├─ smtp_sender.py
│   └─ queue/
│
├─ 7.opena8_whats/                      (WhatsApp, 12351)
│   ├─ main.py
│   ├─ api_connector.py
│   └─ media/
│
├─ 8.opena9_voicein/                    (Voice In, 12352)
│   ├─ main.py
│   ├─ stt_engine.py
│   ├─ tts_engine.py
│   └─ call_handler.py
│
├─ 9.opena10_voiceout/                  (Voice Out, 12353)
│   ├─ main.py
│   ├─ outbound_handler.py
│   └─ cost_tracker.py
│
├─ 10.opena11_unlock/                   (Security, 12354)
│   ├─ main.py
│   ├─ mfa.py
│   ├─ vault.py
│   └─ audit.log
│
├─ 11.opena12_socialauto/               (Social Media, 12355)
│   ├─ main.py
│   ├─ scheduler.py
│   ├─ fb_connector.py
│   ├─ twitter_connector.py
│   └─ linkedin_connector.py
│
├─ 12.opena13_influencer/               (Influencer, 12356)
│   ├─ main.py
│   ├─ analytics.py
│   └─ optimizer.py
│
├─ 13.opena14_calendar/                 (Calendar, 12357)
│   ├─ main.py
│   ├─ google_connector.py
│   ├─ outlook_connector.py
│   └─ scheduler.py
│
├─ 14.opena15_html/                     (HTML Creator, 12358)
│   ├─ main.py
│   ├─ templates/
│   │   ├─ landing.html
│   │   ├─ blog.html
│   │   └─ product.html
│   └─ exports/
│
├─ 15.opena16_shop/                     (Shop, 12359)
│   ├─ main.py
│   ├─ catalog.py
│   ├─ payments.py
│   └─ orders/
│
├─ 16.opena17_homepage/                 (Homepage, 12360)
│   ├─ main.py
│   ├─ builder.py
│   └─ exports/
│
├─ 17.opena18_localarch/                (Local Archiv, 12361)
│   ├─ main.py
│   ├─ backup.py
│   └─ /media/ (USB/HDD Mounts)
│
├─ 18.opena19_finance/                  (Finance, 12362)
│   ├─ main.py
│   ├─ market_feed.py
│   ├─ alerts.py
│   └─ reports/
│
├─ 19.dashboard_agent/                  (Dashboard, 12363)
│   ├─ main.py
│   ├─ collector.py
│   ├─ dashboard.html
│   └─ metrics/
│
└─ AGENTENREGISTER_VOLLSTÄNDIG.md       ← Diese Datei
```

---

## 🚀 START-PROZEDUR (Produktiv)

### Phase 1: Core-System starten
```bash
# Terminal 1: opena1 (Koordinator)
cd /home/danijel-jd/.../1.opena1&2_portier/opena1
python3 main.py

# Terminal 2: opena2 (Archiv-Agent)
cd /home/danijel-jd/.../1.opena1&2_portier/opena2
python3 main.py

# Terminal 3: kordp (Transport)
cd /home/danijel-jd/.../1.opena1&2_portier/kordp
python3 main.py
```

### Phase 2: Interface-Agenten starten
```bash
# Terminal 4: OpenWebUI (8080 Loopback)
cd /home/danijel-jd/.../2.openwebui
python3 web_dashboard.py

# Terminal 5: Telegram (12347)
cd /home/danijel-jd/.../3.opena4_telegram
python3 main.py

# Terminal 6: Mail (12350)
cd /home/danijel-jd/.../6.opena7_mail
python3 main.py
```

### Phase 3: Spezial-Agenten (nach Bedarf)
```bash
# opena15 (HTML Creator)
cd /home/danijel-jd/.../14.opena15_html
python3 main.py

# opena20 (Dashboard)
cd /home/danijel-jd/.../19.dashboard_agent
python3 main.py
```

### Überprüfung
```bash
# Health-Check aller Agenten
curl http://127.0.0.1:12363/health/all

# Sollte zeigen: Alle grün (✅ ONLINE)
```

---

## ⚠️ KRITISCHE REGELN

1. **Port 8080 = OpenWebUI nur.** Alles andere: 12344–12399.
2. **Alle Anfragen müssen über opena1 gehen.** Keine direkten Agent-zu-Agent Requests.
3. **Archivierung = Pflicht.** Jede CMD/RESP in opena2.
4. **archivp = IMMUTABLE.** Append-only, nie löschen.
5. **kordp = zustandslos.** Skalierbar, replizierbar.
6. **opena2 = Single Point of Truth.** Nur über REST-API, kein direkter Dateisystem-Zugriff.

---

## 📞 SUPPORT & DEBUG

### Health-Check (Alle Agenten)
```bash
curl http://127.0.0.1:12363/health/all | jq .
```

### Logs prüfen
```bash
# opena1 Logs
tail -f /home/danijel-jd/.../1.opena1&2_portier/opena1/logs/opena1.log

# opena2 Archiv-Index
curl http://127.0.0.1:12345/finalize/opena2

# Dashboard
open http://127.0.0.1:12363/dashboard
```

### Problembehebung

| Problem | Lösung |
|---|---|
| Port bereits in use | `lsof -i :PORT` → `kill -9 PID` |
| opena2 nicht erreichbar | Prüfe: `curl http://127.0.0.1:12345/health` |
| Archivp voll | Prüfe Retention Policy; Local-Archiv (opena18) starten |
| Telegram-Webhook funktioniert nicht | IP-Whitelist prüfen; ngrok/Cloudflare Tunnel Setup |
| TLS/SSL erforderlich? | Reverse-Proxy vor opena3 (nginx/caddy) setzen |

---

## 🎯 NÄCHSTE SCHRITTE

1. **Diese Dokumentation teilen** mit allen Team-Mitgliedern
2. **Pro Agent ein Implementierungs-Ticket** (später, wenn Coding-Phase beginnt)
3. **Ports reservieren** (Firewall, etc.)
4. **API-Credentials organisieren** (Telegram, Google, Mail, Stripe, etc.)
5. **Hardware-Anforderungen prüfen** (20 Agenten = mindestens 8GB RAM)

---

**Version:** 2.0
**Status:** ✅ Freigegeben zur Umsetzung
**Nächste Überprüfung:** Nach Phase 1 (opena1-3)

---

*Dieser Plan folgt Option 2 der Portier-Architektur:*
*Hinweg: OpenAI → opena1 → opena2 → kordp → Ziel-Agent*
*Rückweg: Ziel-Agent → opena2 → opena1 → OpenAI*
*Alles archiviert, alle Bewegungen nachverfolgbar.*
