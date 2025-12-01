# 📋 ELION Agent Registry - Vollständige Übersicht

**Version:** 2.0  
**Stand:** 21. November 2025  
**Status:** ✅ Production  
**Agenten:** 21 (opena1-opena21 geplant, opena1-opena20 dokumentiert)

---

## 🎯 Ziel dieser Registry

Diese Registry dient als **zentrale Quelle der Wahrheit** für:

- ✅ **Deterministische Port-Zuordnung** - Jeder Agent hat genau einen Port
- ✅ **Vollständige Nachvollziehbarkeit** - Audit Logs für alle Zuordnungen
- ✅ **Kein Doppel-Porting** - Ein Port = Ein Agent
- ✅ **Klare Pfade** - OpenAI-Verbindung & Tool-Reaktion dokumentiert

---

## 📊 Agenten-Tabelle (Vollständig)

| Nr | Agent | Port | Kürzel | Rolle | Ordner | OpenAI Verbindung | Tool Reaktion |
|----|-------|------|--------|-------|--------|-------------------|---------------|
| **0** | **opena1** | 12344 | `kordp` | Koordinator (Portier) | [1.opena1&2_portier](../1.opena1%262_portier/) | `/opena1/kordp/archivp` | `/kordp/archivp/opena1` |
| **1** | **opena2** | 12345 | `archivp` | Archivator (OpenA2) | [1.opena1&2_portier](../1.opena1%262_portier/) | `/opena2/kordp/archivp` | `/archivp/archivp/opena2` |
| **2** | **opena3** | 3000* | `openweb` | OpenWebUI Terminal | [2.opena3_openwebui](../2.opena3_openwebui/) | `/opena3/kordp/archivp/openweb` | `/openweb/archivp/opena3` |
| **3** | **opena4** | 12346 | `telep` | Telegram Mobile | [3.opena4_telegram](../3.opena4_telegram/) | `/opena4/kordp/archivp/telep` | `/telep/archivp/opena4` |
| **4** | **opena5** | 12347 | `vscop` | VS Code Bridge | [4.opena5_vscode](../4.opena5_vscode/) | `/opena5/kordp/archivp/vscop` | `/vscop/archivp/opena5` |
| **5** | **opena6** | 12348 | `browsp` | Browser Automation | [5.opena6_browser](../5.opena6_browser/) | `/opena6/kordp/archivp/browsp` | `/browsp/archivp/opena6` |
| **6** | **opena7** | 12349 | `emailp` | E-Mail Chatbot | [6.opena7_email](../6.opena7_email/) | `/opena7/kordp/archivp/emailp` | `/emailp/archivp/opena7` |
| **7** | **opena8** | 12350 | `whatp` | WhatsApp Chatbot | [7.opena8_whatsapp](../7.opena8_whatsapp/) | `/opena8/kordp/archivp/whatp` | `/whatp/archivp/opena8` |
| **8** | **opena9** | 12351 | `calp` | Telefon Antwort | [8.opena9_telephone](../8.opena9_telephone/) | `/opena9/kordp/archivp/calp` | `/calp/archivp/opena9` |
| **9** | **opena10** | 12352 | `answp` | Telefon Anruf | [9.opena10_call_tracking](../9.opena10_call_tracking/) | `/opena10/kordp/archivp/answp` | `/answp/archivp/opena10` |
| **10** | **opena11** | 12353 | `onlockp` | Unlock Master | [10.opena11_unlock](../10.opena11_unlock/) | `/opena11/kordp/archivp/onlockp` | `/onlockp/archivp/opena11` |
| **11** | **opena12** | 12354 | `somep` | Social Media | [11.opena12_social_media](../11.opena12_social_media/) | `/opena12/kordp/archivp/somep` | `/somep/archivp/opena12` |
| **12** | **opena13** | 12355 | `infmep` | Influencer | [12.opena13_influencer](../12.opena13_influencer/) | `/opena13/kordp/archivp/infmep` | `/infmep/archivp/opena13` |
| **13** | **opena14** | 12356 | `kalp` | Kalender | [13.opena14_calendar](../13.opena14_calendar/) | `/opena14/kordp/archivp/kalp` | `/kalp/archivp/opena14` |
| **14** | **opena15** | 12357 | `htmlp` | HTML Creator | [14.opena15_html](../14.opena15_html/) | `/opena15/kordp/archivp/htmlp` | `/htmlp/archivp/opena15` |
| **15** | **opena16** | 12358 | `shopp` | Shop Creator | [15.opena16_shop](../15.opena16_shop/) | `/opena16/kordp/archivp/shopp` | `/shopp/archivp/opena16` |
| **16** | **opena17** | 12359 | `homep` | Homepage Creator | [16.opena17_homepagecreator](../16.opena17_homepagecreator/) | `/opena17/kordp/archivp/homep` | `/homep/archivp/opena17` |
| **17** | **opena18** | 12360 | `locp` | Local Archiv | [17.opena18_CMR](../17.opena18_CMR/) | `/opena18/kordp/archivp/locp` | `/locp/archivp/opena18` |
| **18** | **opena19** | 12361 | `aktienp` | Aktien & Crypto | [18.opena19_Aktien&Crypto](../18.opena19_Aktien%26Crypto/) | `/opena19/kordp/archivp/aktienp` | `/aktienp/archivp/opena19` |
| **19** | **opena20** | 12362 | `dashp` | Dashboard | [19.opena20_dashboard_agent](../19.opena20_dashboard_agent/) | `/opena20/kordp/archivp/dashp` | `/dashp/archivp/opena20` |
| **20** | **opena21** | 12363 | `workp` | Workflow Engine | [20.opena21_workflow](../20.opena21_workflow/) | `/opena21/kordp/archivp/workp` | `/workp/archivp/opena21` |

*Port 3000 ist UI-Only (kein Backend!), Agent-Backend läuft auf Port 12347

---

## 🔌 Port-Zuordnungs-Policy

### ✅ Erlaubte Port-Ranges

- **12344-12399:** Backend-Services (56 Slots)
- **3000:** UI-Only (OpenWebUI Frontend)

### 🎯 Bevorzugte Ports

| Modul | Bevorzugter Port | Regel |
|-------|------------------|-------|
| **Portier (opena1)** | **12344** | Immer erster Kandidat |
| **OpenA2 (opena2)** | **12345** | Direkt nach Portier |
| **Weitere Agenten** | **12346+** | Sequenziell aufsteigend |

### ❌ Verbotene Ports

- **< 12344:** Ungültig für Backend
- **8080:** Legacy-Konflikt (historisch verboten)
- **3000 als Backend:** UI-Port, kein Backend!

### 🔓 Verfügbare Slots

- **12363-12399:** 37 freie Slots für zukünftige Agenten

---

## 🔄 Option-2-Flow (Kommunikationsweg)

**Alle Agenten folgen diesem strikten Flow:**

```
Client/UI
    ↓
opena1 (Portier, 12344) ← Koordinator
    ↓
opena2 (OpenA2, 12345) ← Safepoint CMD
    ↓
kordp (Dispatcher)
    ↓
openaX (Zielservice)
    ↓
opena2 (OpenA2, 12345) ← Safepoint RESP
    ↓
opena1 (Portier, 12344)
    ↓
Client/UI
```

**Verbotene Kommunikation:**
- ❌ `UI → Agent` (direkt)
- ❌ `Agent → Agent` (ohne Portier)
- ❌ `Agent → OpenA2` (ohne Portier)

---

## 🛣️ Pfad-Konventionen

### OpenAI Verbindung (Hinweg)
```
/openaX/kordp/archivp/{target_kurzel}
```

**Beispiel:** `/opena4/kordp/archivp/telep`

### Tool Reaktion (Rückweg)
```
/{target_kurzel}/archivp/openaX
```

**Beispiel:** `/telep/archivp/opena4`

---

## 📊 Kategorien

### 🔧 Core Infrastructure (2 Agenten)
- opena1 (kordp) - Portier
- opena2 (archivp) - OpenA2

### 📡 Kommunikation (7 Agenten)
- opena3 (openweb) - OpenWebUI
- opena4 (telep) - Telegram
- opena5 (vscop) - VS Code
- opena6 (browsp) - Browser
- opena7 (emailp) - E-Mail
- opena8 (whatp) - WhatsApp
- opena9 (calp) - Telefon Antwort

### 🧠 Business Logic (11 Agenten)
- opena10 (answp) - Telefon Anruf
- opena11 (onlockp) - Unlock Master
- opena12 (somep) - Social Media
- opena13 (infmep) - Influencer
- opena14 (kalp) - Kalender
- opena15 (htmlp) - HTML Creator
- opena16 (shopp) - Shop Creator
- opena17 (homep) - Homepage Creator
- opena18 (locp) - Local Archiv
- opena19 (aktienp) - Aktien & Crypto
- opena20 (dashp) - Dashboard

### 🔄 Automation (1 Agent, geplant)
- opena21 (workp) - Workflow Engine

---

## 🔐 Sicherheits-Layer

Alle Agenten implementieren:

- ✅ **Bearer-Token Authentifizierung** (außer `/health`)
- ✅ **Port-Policy Enforcement** (12344-12399)
- ✅ **Strict JSON Schemas** (Pydantic `extra="forbid"`)
- ✅ **Option-2-Flow Compliance**
- ✅ **Safepoint Archivierung** (via OpenA2)

---

## 📚 Dokumentations-Links

| Agent | README | API Docs | Tests |
|-------|--------|----------|-------|
| opena1/opena2 | [README](../1.opena1%262_portier/README.md) | [API](../docs/PORTIER_API.md) | [Tests](../1.opena1%262_portier/tests/) |
| opena3 | [README](../2.opena3_openwebui/README.md) | [API](../docs/OPENWEBUI_API.md) | [Tests](../2.opena3_openwebui/tests/) |
| opena4 | [README](../3.opena4_telegram/README.md) | - | [Tests](../3.opena4_telegram/tests/) |
| opena5 | [README](../4.opena5_vscode/README.md) | - | [Tests](../4.opena5_vscode/tests/) |
| opena6 | [README](../5.opena6_browser/README.md) | - | [Tests](../5.opena6_browser/tests/) |
| opena7 | [README](../6.opena7_email/README.md) | - | [Tests](../6.opena7_email/tests/) |
| opena8 | [README](../7.opena8_whatsapp/README.md) | - | [Tests](../7.opena8_whatsapp/tests/) |
| opena9 | [README](../8.opena9_telephone/README.md) | - | [Tests](../8.opena9_telephone/tests/) |
| opena10 | [README](../9.opena10_call_tracking/README.md) | - | [Tests](../9.opena10_call_tracking/tests/) |
| opena11 | [README](../10.opena11_unlock/README.md) | - | [Tests](../10.opena11_unlock/tests/) |
| opena12 | [README](../11.opena12_social_media/README.md) | - | [Tests](../11.opena12_social_media/tests/) |
| opena13 | [README](../12.opena13_influencer/README.md) | - | [Tests](../12.opena13_influencer/tests/) |
| opena14 | [README](../13.opena14_calendar/README.md) | - | [Tests](../13.opena14_calendar/tests/) |
| opena15 | [README](../14.opena15_html/README.md) | - | [Tests](../14.opena15_html/tests/) |
| opena16 | [README](../15.opena16_shop/README.md) | - | [Tests](../15.opena16_shop/tests/) |
| opena17 | [README](../16.opena17_homepagecreator/README.md) | - | [Tests](../16.opena17_homepagecreator/tests/) |
| opena18 | [README](../17.opena18_CMR/README.md) | - | [Tests](../17.opena18_CMR/tests/) |
| opena19 | [README](../18.opena19_Aktien%26Crypto/README.md) | - | [Tests](../18.opena19_Aktien%26Crypto/tests/) |
| opena20 | [README](../19.opena20_dashboard_agent/README.md) | [API](../19.opena20_dashboard_agent/docs/API.md) | [Tests](../19.opena20_dashboard_agent/tests/) |

---

## 🚀 Schnellstart (Alle Agenten)

```bash
# Alle Agenten starten
bin/ops.sh start

# Status prüfen
bin/ops.sh status | jq .

# Agenten registrieren
bin/ops.sh agents:register

# Health-Checks (alle Agenten)
for port in {12344..12363}; do
  echo "Port $port:"
  curl -s http://127.0.0.1:$port/health 2>/dev/null | jq -c '{service, status, port}' || echo "offline"
done
```

---

## 📈 Erweiterbarkeit

**Zukünftige Agenten (Slots verfügbar):**

- **opena21** (workp) - Workflow Engine (Port 12363) - geplant
- **opena22** - Port 12364 - verfügbar
- **opena23** - Port 12365 - verfügbar
- ...
- **opena56** - Port 12399 - verfügbar

**Gesamt:** 37 freie Slots für neue Agenten

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 21. November 2025  
**Version:** 2.0
