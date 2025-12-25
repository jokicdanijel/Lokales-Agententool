#!/usr/bin/env python3
"""
Generiert README.md Dateien für alle ELION Agenten basierend auf der CSV-Mapping-Tabelle.
"""

AGENTS = [
    # Nr, Agent, Port, Kürzel, Rolle, Ordner
    (4, "opena5", 12347, "vscop", "VS Code Programmier-Bridge", "4.opena5_vscode"),
    (5, "opena6", 12348, "browsp", "Browser-Bedienung (Automation)", "5.opena6_browser"),
    (6, "opena7", 12349, "emailp", "E-Mail Chatbot", "6.opena7_email"),
    (7, "opena8", 12350, "whatp", "WhatsApp Chatbot", "7.opena8_whatsapp"),
    (8, "opena9", 12351, "calp", "Telefon Antwort Chatbot (Ton)", "8.opena9_telephone"),
    (9, "opena10", 12352, "answp", "Telefon Anruf Chatbot", "9.opena10_call_tracking"),
    (10, "opena11", 12353, "onlockp", "Unlock Master (Aufsperr-Decode)", "10.opena11_unlock"),
    (11, "opena12", 12354, "somep", "Social Media Automatisierung", "11.opena12_social_media"),
    (12, "opena13", 12355, "infmep", "Social Media Influencer", "12.opena13_influencer"),
    (13, "opena14", 12356, "kalp", "Kalender Agent", "13.opena14_calendar"),
    (14, "opena15", 12357, "htmlp", "HTML Creator Tool", "14.opena15_html"),
    (15, "opena16", 12358, "shopp", "Shop Creator & Servicetool", "15.opena16_shop"),
    (16, "opena17", 12359, "homep", "Homepage Creator & Servicetool", "16.opena17_homepagecreator"),
    (17, "opena18", 12360, "locp", "Lokaler Archiv Agent", "17.opena18_CMR"),
    (18, "opena19", 12361, "aktienp", "Aktien & Crypto Trading Agent", "18.opena19_Aktien&Crypto"),
    (19, "opena20", 12362, "dashp", "Dashboard Agent (Kunden)", "19.opena20_dashboard_agent"),
]

README_TEMPLATE = """# {emoji} {agent} - {rolle}

**Agent-ID:** `{agent}`
**Port:** {port}
**Kürzel:** `{kurzel}`
**Version:** 2.0
**Status:** ✅ Production

---

## 📖 Überblick

**{agent}** ist der **{rolle}** - ein spezialisierter Agent im ELION Hyper-Dashboard Ökosystem.

### Kernfunktionen

{funktionen}

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
{agent} ({port}) ← Dieser Agent
    ↓
OpenA2 (12345) → Portier (12344)
    ↓
Client/UI
```

**Integration:** Vollständig in Option-2-Flow integriert.

---

## 📡 API-Endpoints

### `GET /health`
Health-Check des Agents.

```bash
curl http://127.0.0.1:{port}/health | jq .
```

**Response:**
```json
{{
  "status": "ok",
  "service": "{agent}",
  "port": {port},
  "program_target": "{kurzel}",
  "uptime_seconds": 3661.23
}}
```

### `POST /invoke`
Service-spezifische Aktion ausführen.

```bash
curl -X POST http://127.0.0.1:{port}/invoke \\
  -H "Authorization: Bearer $BEARER_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "action": "{default_action}",
    "params": {{...}}
  }}'
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd {ordner}
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:{port}/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \\
  -H "Authorization: Bearer $BEARER_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "service_name": "{agent}",
    "endpoint": "http://127.0.0.1:{port}",
    "program_target": "{kurzel}"
  }}'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \\
  -H "Authorization: Bearer $BEARER_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "service_target": "{kurzel}",
    "action": "{default_action}",
    "params": {{...}}
  }}'
```

---

## 📁 Verzeichnisstruktur

```
{ordner}/
├── main.py                  # FastAPI Agent Entry Point
├── config.py                # Konfiguration
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script
├── tests/
│   └── test_{agent}.py      # Unit-Tests
└── README.md                # Diese Datei
```

---

## 🔐 Sicherheit

- ✅ **Bearer-Token** für alle Endpoints außer `/health`
- ✅ **Port-Policy** Enforcement (12344-12399)
- ✅ **Strict JSON** (Pydantic `extra="forbid"`)
- ✅ **Option-2-Flow** Compliance

---

## 🧪 Testing

```bash
# Unit-Tests
pytest tests/test_{agent}.py -v

# Health-Check
curl http://127.0.0.1:{port}/health

# Integration-Test via Portier
python3 ../scripts/test_{agent}_integration.py
```

---

## 📊 Monitoring

```bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:{port}/metrics
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team
**Letzte Aktualisierung:** 21. November 2025
"""

EMOJI_MAP = {
    "vscop": "💻",
    "browsp": "🌐",
    "emailp": "📧",
    "whatp": "💬",
    "calp": "☎️",
    "answp": "📞",
    "onlockp": "🔓",
    "somep": "📱",
    "infmep": "⭐",
    "kalp": "📅",
    "htmlp": "📝",
    "shopp": "🛒",
    "homep": "🏠",
    "locp": "💾",
    "aktienp": "📈",
    "dashp": "📊",
}

FUNKTIONEN_MAP = {
    "vscop": "- 💻 **Code Execution** - Python/JavaScript ausführen\n- 🔧 **Task Automation** - VS Code Tasks steuern\n- 📂 **File Operations** - Dateien lesen/schreiben\n- 🐛 **Debug Support** - Debugging-Integration",
    "browsp": "- 🌐 **Browser Automation** - Selenium/Playwright Integration\n- 🔍 **Web Scraping** - Daten extrahieren\n- 📸 **Screenshots** - Webseiten-Captures\n- 🤖 **Form Automation** - Formulare ausfüllen",
    "emailp": "- 📧 **Send Email** - E-Mails versenden (SMTP)\n- 📥 **Read Email** - Posteingang abrufen (IMAP)\n- 📎 **Attachments** - Anhänge verarbeiten\n- 🏷️ **Labels/Folders** - E-Mail-Organisation",
    "whatp": "- 💬 **Send Message** - WhatsApp-Nachrichten senden\n- 📥 **Receive Messages** - Eingehende Nachrichten\n- 📎 **Media Support** - Bilder, Videos, Dokumente\n- 👥 **Group Management** - Gruppen-Interaktion",
    "calp": "- ☎️ **Voice Response** - Sprachantworten generieren\n- 🎙️ **Speech-to-Text** - Anrufe transkribieren\n- 📞 **Call Handling** - Anrufe annehmen/beenden\n- 📊 **Call Analytics** - Anruf-Statistiken",
    "answp": "- 📞 **Outbound Calls** - Ausgehende Anrufe tätigen\n- 🤖 **IVR Integration** - Interactive Voice Response\n- 📋 **Call Logging** - Anrufprotokolle\n- 🔊 **TTS Support** - Text-to-Speech",
    "onlockp": "- 🔓 **Decode** - Verschlüsselte Daten entschlüsseln\n- 🔑 **Key Management** - Schlüsselverwaltung\n- 🛡️ **Security Analysis** - Sicherheitsanalyse\n- 📜 **Audit Logging** - Zugriffsprotokolle",
    "somep": "- 📱 **Post Automation** - Posts planen & veröffentlichen\n- 📊 **Analytics** - Engagement-Metriken\n- 👥 **Multi-Platform** - Twitter, Facebook, Instagram, LinkedIn\n- 🔔 **Notifications** - Social Media Alerts",
    "infmep": "- ⭐ **Influencer Tracking** - Influencer überwachen\n- 📈 **Campaign Management** - Kampagnen steuern\n- 💬 **Engagement Analysis** - Interaktionsanalyse\n- 🎯 **Target Audience** - Zielgruppenanalyse",
    "kalp": "- 📅 **Event Management** - Termine erstellen/bearbeiten\n- 🔔 **Reminders** - Erinnerungen senden\n- 👥 **Shared Calendars** - Kalender teilen\n- 🔄 **Sync Support** - Google/Outlook Integration",
    "htmlp": "- 📝 **HTML Generation** - HTML-Code generieren\n- 🎨 **Template Engine** - Vorlagen verwenden\n- 🔍 **SEO Optimization** - Meta-Tags, Keywords\n- 📱 **Responsive Design** - Mobile-optimiert",
    "shopp": "- 🛒 **Product Management** - Produkte verwalten\n- 💳 **Payment Integration** - Zahlungsabwicklung\n- 📦 **Order Processing** - Bestellungen bearbeiten\n- 📊 **Inventory** - Lagerverwaltung",
    "homep": "- 🏠 **Page Builder** - Webseiten erstellen\n- 🎨 **Design Templates** - Vorlagen nutzen\n- 📝 **CMS Integration** - Content-Management\n- 🚀 **Deployment** - Hosting & Veröffentlichung",
    "locp": "- 💾 **Local Storage** - Dateien lokal speichern\n- 📂 **File Indexing** - Suchindex erstellen\n- 🔍 **Full-Text Search** - Volltextsuche\n- 🗄️ **Archive Management** - Archivverwaltung",
    "aktienp": "- 📈 **Stock Tracking** - Aktienkurse überwachen\n- 💰 **Crypto Trading** - Krypto-Handel\n- 📊 **Portfolio Management** - Portfolio verwalten\n- 🔔 **Price Alerts** - Kursalarme",
    "dashp": "- 📊 **Dashboard UI** - Kunden-Dashboard\n- 📈 **Analytics** - Metriken & KPIs\n- 👥 **User Management** - Benutzerverwaltung\n- 🔐 **Access Control** - Zugriffssteuerung",
}

DEFAULT_ACTIONS = {
    "vscop": "execute_code",
    "browsp": "navigate",
    "emailp": "send_email",
    "whatp": "send_message",
    "calp": "answer_call",
    "answp": "make_call",
    "onlockp": "decode",
    "somep": "post",
    "infmep": "track_influencer",
    "kalp": "create_event",
    "htmlp": "generate_html",
    "shopp": "add_product",
    "homep": "build_page",
    "locp": "store_file",
    "aktienp": "track_stock",
    "dashp": "get_metrics",
}


def generate_readme(nr, agent, port, kurzel, rolle, ordner):
    """Generiert README.md für einen Agenten"""
    emoji = EMOJI_MAP.get(kurzel, "🔧")
    funktionen = FUNKTIONEN_MAP.get(kurzel, "- 🔧 **Generic Function** - Standard-Aktion ausführen")
    default_action = DEFAULT_ACTIONS.get(kurzel, "execute")

    content = README_TEMPLATE.format(
        nr=nr,
        agent=agent,
        port=port,
        kurzel=kurzel,
        rolle=rolle,
        ordner=ordner,
        emoji=emoji,
        funktionen=funktionen,
        default_action=default_action,
    )

    filepath = f"{ordner}/README.md"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Erstellt: {filepath}")


def main():
    """Hauptfunktion"""
    print("🚀 Generiere Agenten-READMEs...")
    print("=" * 60)

    for nr, agent, port, kurzel, rolle, ordner in AGENTS:
        try:
            generate_readme(nr, agent, port, kurzel, rolle, ordner)
        except Exception as e:
            print(f"❌ Fehler bei {agent}: {e}")

    print("=" * 60)
    print(f"✅ {len(AGENTS)} READMEs erfolgreich generiert!")


if __name__ == "__main__":
    main()
