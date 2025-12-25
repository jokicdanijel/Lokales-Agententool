# Agent Verzeichnis-Struktur - PLAN

## 1. ZIEL

Erstelle **19 vollständige, isolierte Agent-Verzeichnisse** (wie 1.opena1&2_portier/, 2.openwebui/) unter Projektwurzel mit:

- Nummern-Präfix (3-21)
- Konsistente Struktur
- Vollständige Dateien (nicht leer)
- Einsatzbereit

---

## 2. AGENT-MAPPING (19 Agenten)

| #   | Verzeichnis          | Agent_ID | Port  | Beschreibung          | Kategorie   |
| --- | -------------------- | -------- | ----- | --------------------- | ----------- |
| 3   | opena1_coordinator   | opena1   | 12344 | Orchestrator Phase 1  | Core        |
| 4   | opena2_archivator    | opena2   | 12345 | File Storage System   | Core        |
| 5   | kordp_scheduler      | kordp    | 12346 | Event Coordination    | Core        |
| 6   | opena4_telegram      | opena4   | 12347 | Telegram Integration  | Integration |
| 7   | opena5_browser       | opena5   | 12348 | Browser Automation    | Tools       |
| 8   | opena6_email         | opena6   | 12349 | Email Management      | Tools       |
| 9   | opena7_whatsapp      | opena7   | 12350 | WhatsApp Integration  | Integration |
| 10  | opena8_telephone     | opena8   | 12351 | Telephone System      | Integration |
| 11  | opena9_call_tracking | opena9   | 12352 | Call Analytics        | Analytics   |
| 12  | opena10_unlock       | opena10  | 12353 | Security & Access     | Security    |
| 13  | opena11_social_media | opena11  | 12359 | Social Media Manager  | Integration |
| 14  | opena12_influencer   | opena12  | 12360 | Influencer Collab     | Tools       |
| 15  | opena13_calendar     | opena13  | 12361 | Calendar & Scheduling | Tools       |
| 16  | opena14_html         | opena14  | 12362 | HTML Generation       | Tools       |
| 17  | opena15_shop         | opena15  | 12363 | E-commerce System     | Business    |
| 18  | opena16_crm          | opena16  | 12364 | CRM Management        | Business    |
| 19  | opena17_analytics    | opena17  | 12365 | Data Analytics        | Analytics   |
| 20  | opena18_dashboard    | opena18  | 12366 | Dashboard UI          | UI          |
| 21  | opena19_workflow     | opena19  | 12367 | Workflow Automation   | Automation  |

---

## 3. VERZEICHNIS-STRUKTUR (pro Agent)

```
X.agent_name/
├── bin/
│   └── start.sh              # Start-Skript
├── config/
│   ├── agent.conf            # Konfiguration
│   └── logging.conf          # Logging-Konfiguration
├── tests/
│   ├── __init__.py
│   └── test_agent.py         # Basis-Test
├── logs/
│   └── .gitkeep              # Placeholder
├── docs/
│   └── README_DEV.md         # Entwicklungs-Docs
├── data/
│   └── .gitkeep              # Daten-Verzeichnis
├── api/
│   └── __init__.py           # API-Modul
├── main.py                   # Agent-Einstiegspunkt
├── requirements.txt          # Python-Abhängigkeiten
├── .env.template             # Umgebungs-Template
└── README.md                 # Hauptdokumentation
```

---

## 4. DATEI-INHALTE

### 4.1 main.py

- FastAPI-App
- `/health` Endpoint
- `/status` Endpoint
- `/invoke` Endpoint
- Logging zu `logs/app.log`

### 4.2 README.md

- Agent-Beschreibung
- Port & ID
- Quick Start
- Structure-Übersicht
- Registration mit Dashboard
- Logging-Info

### 4.3 requirements.txt

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
aiohttp==3.9.1
python-dotenv==1.0.0
```

### 4.4 .env.template

```
AGENT_ID=openaX
PORT=123XX
TOKEN=${DASHBOARD_ADMIN_TOKEN}
LOG_LEVEL=INFO
DASHBOARD_URL=http://127.0.0.1:12349
ARCHIVATOR_URL=http://127.0.0.1:12345
```

### 4.5 config/agent.conf

- [agent] Sektion mit ID, Port, Name
- [security] mit Token-Info
- [logging] mit Level
- [integrations] mit URLs

### 4.6 tests/test_agent.py

- Basis-Test-Template
- Health-Check-Test
- Invoke-Test

### 4.7 bin/start.sh

- Lade .env
- Setze PORT
- Starte `python main.py`

---

## 5. WAS NICHT TUN

❌ Keine Dateien aus 19.dashboard_agent kopieren
❌ Keine doppelten Agenten
❌ Keine leeren main.py
❌ Keine verwaisten Tests
❌ Keine Konflikte mit bestehendem Setup

---

## 6. UMSETZUNGS-SCHRITTE

1. **Skript schreiben** (`create_all_agents.sh`)
2. **Validieren:** Alle 19 Agenten ✓
3. **Ausführen:** Bash-Skript laufen lassen
4. **Verify:** `ls -la` zeigt 3.opena1_coordinator bis 21.opena19_workflow
5. **Test:** `cd 3.opena1_coordinator && python main.py` startet
6. **Git:** Alles committen & pushen

---

## 7. ERFOLGS-KRITERIEN

✅ 19 Verzeichnisse (3-21)
✅ Jedes mit 8 Unterverzeichnisse/Dateien
✅ Jedes main.py funktioniert
✅ Jedes README vollständig
✅ Alle in Git committbar

---

**Status:** PLAN ABGESCHLOSSEN
**Nächster Schritt:** Genehmigung + Ausführung
