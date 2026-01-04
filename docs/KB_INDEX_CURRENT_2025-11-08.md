# 📚 opena1 Wissensdatenbank – Master Index

**Erstellt:** Nov 8, 2025 18:45 UTC
**Version:** 1.0 – Initial 6-Module KB
**Status:** 🟢 ACTIVE FOR SPRINT

---

## 🎯 Überblick

**6 Module** dokumentieren das Nov 8 System-State (5/6 Services live).
**Fokus:** Koordinator-Wissen + Integrationen für Nov 9 Dashboard-Start.
**Struktur:** Append-Only (keine Löschungen, nur Erweiterungen).

---

## 📑 KB-Module (Vollständige Liste)

### 🔴 Modul 1: Telegram-Bridge (opena4_telegram)

**Datei:** `KB_TELEGRAM_BRIDGE_2025-11-08.md`

| Info          | Wert                                      |
| ------------- | ----------------------------------------- |
| **Port**      | 12346                                     |
| **File**      | main_opena4_telegram.py (13 KB)           |
| **Status**    | ✅ LIVE & TESTED                          |
| **Test Rate** | 8/8 Passed (Nov 8, 18:11)                 |
| **Endpoints** | 5 (webhook, send, recent, health, config) |
| **Routing**   | Telegram→Finance (3 commands)             |
| **Archive**   | 15+ verified entries                      |

**Schnell-Zugriff:**

- Webhook Handler: `/webhook/telegram`
- Commands: /balance, /accounts, /transactions, /help
- Secret: 31-char validation (X-Telegram-Bot-Api-Secret-Token)
- User Whitelist: .env TELEGRAM_ALLOWED_USERS

---

### 🟠 Modul 2: Dashboard Integration (opena19)

**Datei:** `KB_DASHBOARD_INTEGRATION_2025-11-08.md`

| Info             | Wert                                                      |
| ---------------- | --------------------------------------------------------- |
| **Port**         | 12349                                                     |
| **File**         | main_dashboard.py (FastAPI)                               |
| **Status**       | ⏳ READY FOR NOV 9 STARTUP                                |
| **Python Fixes** | 3 Applied (security.py, sse_bus.py, main_dashboard.py) ✅ |
| **Endpoints**    | 4 (health, register, status, dashboard)                   |
| **Event Bus**    | SSE (Server-Sent Events)                                  |
| **Registry**     | JSON-based Agent Registry                                 |

**Schnell-Zugriff:**

- Bootstrap: `python3 main_dashboard.py`
- Health: `GET /health`
- Register Agent: `POST /api/agent/register`
- Status: `GET /api/agent/status`
- Events: `GET /events` (SSE stream)

**Python Fixes Applied:**

1. ✅ security.py – Function ordering (generate_token moved up)
2. ✅ sse_bus.py – Async generator syntax fixed
3. ✅ main_dashboard.py – AgentRegistry() init fixed

---

### 🟡 Modul 3: Archive Patterns (opena2)

**Datei:** `KB_ARCHIVE_PATTERNS_2025-11-08.md` (kommend)

| Info        | Wert                           |
| ----------- | ------------------------------ |
| **Port**    | 12345                          |
| **Status**  | ✅ RUNNING                     |
| **Storage** | Append-Only archivp/ directory |
| **Index**   | index.jsonl (JSONL format)     |
| **Dedup**   | Hash-based (SHA-256)           |
| **Entries** | 15+ verified (Nov 8)           |

---

### 🟢 Modul 4: Coordinator (opena1)

**Datei:** `KB_OPENA1_COORDINATOR_2025-11-08.md` (kommend)

| Info             | Wert                         |
| ---------------- | ---------------------------- |
| **Port**         | 12344                        |
| **Role**         | Central Orchestrator         |
| **Status**       | ✅ RUNNING                   |
| **Registry**     | Agent discovery & monitoring |
| **Health Check** | Every 5 seconds              |
| **Event Bus**    | Main message broker          |

---

### 🔵 Modul 5: System Integration Flows

**Datei:** `KB_SYSTEM_INTEGRATION_FLOWS_2025-11-08.md` (kommend)

| Info               | Wert                                |
| ------------------ | ----------------------------------- |
| **Scope**          | End-to-end data flows               |
| **Main Flow**      | Telegram→Finance→Archive (verified) |
| **Boot Sequence**  | All 6 services startup order        |
| **Error Handling** | Fallback scenarios documented       |
| **Performance**    | Baseline metrics (Nov 8)            |

---

## 🧭 Quick Navigation

### "Wie starte ich opena19 (Dashboard)?"

→ **KB_DASHBOARD_INTEGRATION_2025-11-08.md** → Section "Bootstrap Sequence"

### "Was ist ein Safepoint?"

→ **KB_ARCHIVE_PATTERNS_2025-11-08.md** → Section "Safepoint Format"

### "Wie funktioniert der /balance Command?"

→ **KB_TELEGRAM_BRIDGE_2025-11-08.md** → Section "Command Routing Matrix"

### "Wie registriere ich einen neuen Agent?"

→ **KB_OPENA1_COORDINATOR_2025-11-08.md** → Section "REST API"

### "Welche Fehler können auftreten?"

→ **KB_SYSTEM_INTEGRATION_FLOWS_2025-11-08.md** → Section "Error Scenarios"

### "Wie ist der Nov 8 Boot-Prozess?"

→ **KB_SYSTEM_INTEGRATION_FLOWS_2025-11-08.md** → Section "Service Boot Sequence"

---

## 🏷️ Tag-System

Alle KB-Dateien sind getagged für Suchbarkeit:

| Tag              | Module     | Zweck                            |
| ---------------- | ---------- | -------------------------------- |
| #telegram        | Modul 1    | Telegram integration & routing   |
| #dashboard       | Modul 2    | Dashboard startup & integration  |
| #archive         | Modul 3    | Persistent storage & audit trail |
| #coordinator     | Modul 4    | Agent orchestration              |
| #integration     | Modul 5    | System-wide data flows           |
| #api             | Alle       | REST endpoint documentation      |
| #security        | Modul 1, 2 | Auth, secrets, validation        |
| #testing         | Modul 1    | Test suites & results            |
| #troubleshooting | Alle       | Common issues & fixes            |
| #nov9            | Modul 2, 5 | Nov 9 startup & checklist        |

---

## 📊 Services-Übersicht (Nov 8 Status)

| Service              | Port  | Status     | KB-Modul     | Letzer Test    |
| -------------------- | ----- | ---------- | ------------ | -------------- |
| opena1 (Coordinator) | 12344 | ✅ Running | Modul 4      | Kontinuierlich |
| opena2 (Archive)     | 12345 | ✅ Running | Modul 3      | 18:35 UTC      |
| kordp (Relay)        | 12346 | ✅ Running | Modul 5      | 18:35 UTC      |
| opena_finance        | 12347 | ✅ Running | (Finance KB) | 17:28 UTC      |
| opena4_telegram      | 12346 | ✅ Running | Modul 1      | 18:11 UTC      |
| opena19 (Dashboard)  | 12349 | ⏳ Nov 9   | Modul 2      | N/A            |

---

## 🔗 Inter-Modul-Dependencies

```
Modul 2 (Dashboard)
  ↓ depends on
Modul 4 (Coordinator)
  ↓ depends on
Modul 3 (Archive)
  ↓ stores messages from
Modul 1 (Telegram) + Modul 5 (Integration)
```

**Startup Order (Nov 9):**

1. opena1 (Modul 4) – Coordinator ready
2. opena2 (Modul 3) – Archive ready
3. opena4_telegram (Modul 1) – Telegram ready
4. opena19 (Modul 2) – Dashboard discovers all agents

---

## 📋 Verwendete Formate

Alle KB-Dateien nutzen:

- **Markdown** für strukturierte Lesbarkeit
- **Tables** für Übersichten
- **Code Blocks** für Beispiele
- **Sections** mit # Headers für Navigation
- **Bash Commands** für Copy-Paste Ready
- **JSON Examples** für API-Payloads
- **Internal Links** für Cross-Reference

---

## ✅ What Each Module Contains

### Modul 1 (Telegram) – 5-7 KB

- Service Overview
- Architecture (Webhook Handler, Command Router, Message Logger)
- Security (Secret, User Whitelist, Token Management)
- REST API (5 Endpoints documented)
- Integration Points (opena_finance, opena2 Archive)
- Archive Integration (Message Format, Query Patterns)
- Testing (8 Test Cases, All Passing)
- Startup & Lifecycle (Start Script, Logs, Monitoring)
- Troubleshooting (Port Conflict, Secret Issues, Fallback Patterns)
- Performance Notes

### Modul 2 (Dashboard) – 6-8 KB

- Service Overview
- Nov 8 Python Fixes Detail (3 fixes documented)
- Bootstrap Sequence (Nov 9 Start-Anleitung)
- REST API (4 Endpoints: health, register, status, dashboard)
- Agent Registry Pattern (Registration Flow, State File)
- Event Bus (SSE Endpoint, JavaScript Example)
- Logs & Monitoring (Log File Locations, Watch Commands)
- Dependencies (Python Imports, External Services)
- Nov 9 Startup Checklist (Pre-Startup, Startup, Post-Startup, Integration)
- Troubleshooting (Port Conflict, Import Errors, Health 500, Registration Fails)
- Performance Notes
- Nov 9→10 Plan

### Modul 3 (Archive) – 4-5 KB

- Safepoint Format (SP<TS>\_SRC→DST_KIND.json)
- File Structure (JSON Schema)
- Query Patterns (/archiv/last, /archiv/date, /archiv/source)
- Index Structure (index.jsonl)
- Deduplication (Hash-based, Example)
- Audit Trail (Verification)
- Usage Examples (curl commands)

### Modul 4 (Coordinator) – 4-5 KB

- Mission Statement
- Port 12344
- Responsibilities (Start/Stop, Health-Monitor, Registry, Event-Forwarding)
- Input Sources (opena2, Dashboard, External APIs)
- Output Targets (opena2, All Agents, Dashboard)
- Key Endpoints (6 endpoints)
- Error Handling (Dead Agent, Archive Write Failure, Port Conflict)
- Integration with Nov 8 System (Monitoring Matrix)

### Modul 5 (Integration Flows) – 6-8 KB

- Full Data Flow: Telegram→Finance→Archive (Diagram + Step-by-Step)
- Service Boot Sequence (6 Services, Startup Order)
- Error Scenarios & Fallback (3 Scenarios documented)
- Health Checks (5s Polling Format)
- Performance Metrics (Latency, Throughput)
- Scaling Considerations (Horizontal, DB Limits, Archive Scale)
- Nov 9 Verification Checklist (Pre, During, Post-Startup)

---

## 📈 Größen-Schätzung

| Modul          | KB     | Seiten (A4) |
| -------------- | ------ | ----------- |
| 1. Telegram    | 5-7    | 1.5-2       |
| 2. Dashboard   | 6-8    | 2-2.5       |
| 3. Archive     | 4-5    | 1-1.5       |
| 4. Coordinator | 4-5    | 1-1.5       |
| 5. Integration | 6-8    | 2-2.5       |
| **Index**      | 3-4    | 1           |
| **TOTAL**      | ~28-37 | ~8-11       |

---

## 🚀 Verwendung

### Für Nov 9 Startup

1. Öffne `KB_DASHBOARD_INTEGRATION_2025-11-08.md`
2. Gehe zu Section "Bootstrap Sequence"
3. Folge den Schritt-für-Schritt Anweisungen

### Für Troubleshooting

1. Öffne `KB_INDEX_CURRENT_2025-11-08.md` (diese Datei)
2. Nutze "Quick Navigation" Tabelle
3. Gehe zum relevanten Modul + Troubleshooting Section

### Für System-Verständnis

1. Starte mit `KB_SYSTEM_INTEGRATION_FLOWS_2025-11-08.md`
2. Lese "Service Boot Sequence" für Überblick
3. Nutze "Full Data Flow" Diagramm

### Für API-Dokumentation

1. Nutze Tag-Filter (#api)
2. Gehe zum relevanten Modul (Telegram, Dashboard, etc.)
3. Suche "REST API" Section

---

## 🔐 Governance

**KB-Struktur Rules:**

- Append-Only (neue Dateien nur, nie löschen)
- Timestamped (Dateiname: KB\_\*\_2025-11-08.md)
- Versioniert (v1.0, v1.1, etc. in Header)
- Indexed (dieser Index ist Master-Reference)
- Tagged (Tags am Anfang jeder Section)

---

## 📞 Schnell-Referenz

**Nur 1-2 Fragen?**

- "How to start opena19?" → `KB_DASHBOARD_INTEGRATION_2025-11-08.md` → Bootstrap
- "What's a Safepoint?" → `KB_ARCHIVE_PATTERNS_2025-11-08.md` → Safepoint Format
- "How to add new agent?" → `KB_OPENA1_COORDINATOR_2025-11-08.md` → REST API

**Vollständiges Verständnis?**

- Starte mit Index (diese Datei)
- Lese Modul 5 (Integration Flows) für Überblick
- Tiefe dich dann in spezifische Module ein

---

**Status:** 🟢 ACTIVE
**Last Updated:** Nov 8, 2025 18:45 UTC
**Version:** 1.0
**Maintained by:** ELION Sprint Team

---

## 📚 Anhang: Alle Dateien im System

```
1.opena1&2_portier/knowledgebase/opena1/
├── KB_INDEX_CURRENT_2025-11-08.md ................. (Diese Datei)
├── KB_TELEGRAM_BRIDGE_2025-11-08.md .............. (Modul 1)
├── KB_DASHBOARD_INTEGRATION_2025-11-08.md ........ (Modul 2)
├── KB_ARCHIVE_PATTERNS_2025-11-08.md ............. (Modul 3 – kommend)
├── KB_OPENA1_COORDINATOR_2025-11-08.md ........... (Modul 4 – kommend)
├── KB_SYSTEM_INTEGRATION_FLOWS_2025-11-08.md ..... (Modul 5 – kommend)
└── (Existing historic KB files)
    ├── Portier_wissensdatenbank_t1.txt
    ├── MASTER-PROMPT_Textfassung_zweischichtig.txt
    └── ... (13 more)
```

---

**Next:** Gehe zu `KB_TELEGRAM_BRIDGE_2025-11-08.md` für erste Modul-Details.
