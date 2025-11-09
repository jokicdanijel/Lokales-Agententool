# PROJECT CHARTER – Hyper Dashboard / Portier OpenAI

**Projektname:** Hyper Dashboard / Portier OpenAI  
**Projektwurzel:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt`  
**Erstellt am:** 2025-11-09 UTC  
**Verantwortlich:** *(Team/Person eintragen)*  
**Version:** 1.0  

**Regeln:** Append-only · Dedupe (SHA-256/IDs) · keine Doppelblobs · Auditierbarkeit durchgängig

---

## 1) Ziel & Kontext

### Projektmission

Ein durchgängig **auditierbares Agenten-System** mit mehreren Modulen aufbauen (z.B. Telegram-Bridge, OpenWebUI, Monitoring, VS Code-Bridge), das nach klar definierten Routen funktioniert, **keine Doppelblobs erzeugt**, vollständige **Audit-Spur wahrt** und konsistente **Port-/Governance-Regeln** einhält.

### Geschäftlicher Hintergrund

- Der Nutzer (Danijel) betreibt ein verteiltes Agenten-Ökosystem mit Schnittstellen zu Telegram, UI/IDE, Monitoring
- Module wie „opena4" (Telegram-Bridge), „opena3" (UI), „opena2" (Archivator), „opena5" (VS Code) sollen sauber zusammenwirken
- **Infrastruktur-Anforderung:** Port-Governance (12344–12399), 8080 exklusiv für UI
- **Datenschutz & Compliance:** Append-only Speicherung, SHA-256-Dedupe, keine Überschreibungen, Audit-Index, HEADS/INTEGRITY Struktur
- **Zielgruppe:** Dev-Teams, Enterprise-Agenten, Monitoring-Systeme

---

## 2) Umfang (Scope)

### Was das Projekt **umfasst:**

✅ Einrichtung der **Projektstruktur** (Datei/Verzeichnislayout) unter der Projektwurzel  
✅ Definition und Dokumentation aller **Agenten-Routen** und ihrer Verantwortlichkeiten  
✅ Implementierung der **Governance-Regeln** für Ports, Logging, Secrets, Dedupe  
✅ Aufbau der **Persistenz- und Archiv-Mechanismen:** Safepoints, Blobs, Indexe  
✅ Einrichtung von **CI/Pre-Commit/QC:** Linting, Schema-Prüfung, Port-Check  
✅ Dokumentation: **Schritt-Weise Spezifikationen** für jeden Agent (z.B. Schritt 4 für opena4, Schritt 5 für opena5)  
✅ **7 Schritte Architektur-Roadmap:** Von Projektinitialisierung bis Monitoring/Release

### Was **NICHT** im Scope enthalten ist:

❌ Vollständige Implementierung der Logik aller Agenten oder Funktionen (z.B. spezialisierte Business-Agenten außerhalb der Infrastruktur)  
❌ Umfangreiche UI/UX-Designs oder externe Dienstintegrationen, die nicht Teil der Kerninfrastruktur sind  
❌ Migration bestehender Systeme – Fokus liegt auf **Neubau**  
❌ Skalierung auf Multi-Cloud oder Kubernetes (stand-alone VM-Fokus)

---

## 3) Hauptakteure & Rollen

| Rolle | Verantwortlich | Aufgaben | Kontakt |
|-------|-----------------|----------|---------|
| **Projektleitung** | *(Name eintragen)* | Gesamtverantwortung, Ressourcen, Zeitplan, Risiko-Management | — |
| **Infrastruktur-Lead** | *(Name)* | Aufbau Verzeichnisstruktur, Governance-Regeln, Port-Leases, CI/CD | — |
| **Archivator (opena2)** | Modul "opena2" Team | Persistenz, Dedupe, Audit-Index, Blob-Verwaltung, HEADS/INTEGRITY | — |
| **Bridge Telegram (opena4)** | Modul "opena4" Team | Telegram-Anbindung (Webhook/Long-Polling), Task-Queue, Safepoints | — |
| **VS Code Bridge (opena5)** | Modul "opena5" Team | VS Code Integration, Edit/Diff Workflow, Workspace-Management | — |
| **UI/WebUI (opena3)** | Modul "opena3" Team | UI/Frontend, Buttons, Routing, Display Logic | — |
| **Monitoring (opena20)** | Modul "opena20" Team | Health Checks, Metrics Collection, Alerting, Dashboard | — |
| **Qualitätssicherung** | *(Name)* | Code-Reviews, CI/Pre-Commit, Tests, Audit-Compliance | — |

---

## 4) Meilensteine & Zeitplan

| Meilenstein | Beschreibung | Abhängigkeiten | Zieltermin | Status |
|-------------|-------------|-----------------|-----------|--------|
| **M1 – Projektstruktur** | Verzeichnislayout, README, .env-Beispiele, port_leases.json | — | *(Datum)* | ✅ In Progress |
| **M2 – Governance Regeln** | Port-Pool definiert, Sekret-Handhabung, Dedupe Regeln, CI Policies | M1 | *(Datum)* | ⏳ Queued |
| **M3 – Archivator Setup (opena2)** | Persistenz, Indexstruktur, Dedupe-Engine, HEADS/INTEGRITY | M2 | *(Datum)* | ⏳ Queued |
| **M4 – Schritt 1: 7.1-Validierung (opena1)** | Pydantic Schemas, Request71, Error-Schema 8.3 | M2 | 2025-11-09 | ✅ Complete |
| **M5 – Schritt 2: Tool-Registry** | Service Endpoints Mapping, Tool Dispatch | M4 | *(Datum)* | ⏳ Queued |
| **M6 – Schritt 3: Safepoint Format** | SP<ts>_src→dst_EVENT.json, Index, Dedupe-Validierung | M3, M5 | *(Datum)* | ⏳ Queued |
| **M7 – Schritt 4: Telegram (opena4)** | Webhook Integration, Task-Queue, Audit | M6 | *(Datum)* | ⏳ Queued |
| **M8 – Schritt 5: VS Code (opena5)** | IDE Bridge, Edit/Diff Workflow, Workspace Mgmt | M6 | *(Datum)* | 📋 Spec Ready |
| **M9 – Schritt 6: Monitoring (opena20)** | Health/Metrics/Alerting Pipeline | M3, M7, M8 | *(Datum)* | ⏳ Queued |
| **M10 – MVP Release** | End-to-End Funktionalität: Telegram → Edit → UI | M4–M9 | *(Datum)* | ⏳ Queued |
| **M11 – Production Deployment** | Hardening, Security Audit, SLA-Docs | M10 | *(Datum)* | ⏳ Queued |

---

## 5) Qualitäts- & Sicherheitsanforderungen

### 5.1 Architektur-Anforderungen

- ✅ **Append-only Speicherung:** Keine Überschreibungen von Blobs/Indexen. Nur neue Dateien oder Referenzen.
- ✅ **Dedupe mittels SHA-256:** Vor jedem Write Hash prüfen; bei Treffer: keine neue Datei, nur Audit-Vermerk.
- ✅ **Port-Governance:** Ports nur im Bereich **12344–12399**. Port **8080 ausschließlich für opena3**.
- ✅ **Secrets:** Nur über .env-Datei; keine Tokens in Logs; Maskierung bei Ausgaben.
- ✅ **Audit-Spur:** Jeder Safepoint (CMD/RESP), jeder Blob, Indexeintrag muss dokumentiert und nachvollziehbar sein.

### 5.2 CI/Pre-Commit & Code Quality

- ✅ **Linting:** Python (flake8/pylint), JSON (jsonschema), YAML (yamllint)
- ✅ **Schema-Prüfung:** Pydantic v2 Validierung, Request71/8.3 Compliance
- ✅ **Port-Policy Check:** grep für Ports außerhalb [12344–12399]; 8080-Veto (außer opena3)
- ✅ **Hash-Integrität:** Dedupe-Index-Konsistenz, HEADS.json Validierung
- ✅ **Type Hints:** 100% Coverage für API-Endpoints

### 5.3 Sicherheit

- ✅ **RBAC & Auth:** Telegram User IDs in erlaubter Liste; Webhook-Secret-Header Pflicht; Rollenhaften Zugriff
- ✅ **TLS/HTTPS für Webhook:** Mindestens TLS 1.2; Reverse-Proxy bei Webhook Eingangs-Endpoint
- ✅ **Secrets Management:** .env mit Token-Maskierung, kein Hardcoding
- ✅ **Input Validation:** Pydantic `extra='forbid'`, Diff-Validierung, Safepoint-Format Checks
- ✅ **Audit Logging:** Jede Aktion im index.jsonl + Safepoint-Datei

### 5.4 Performance & Reliability

- ✅ **Request Timeout:** 30s für Dedupe-Lookup, 60s für Archive Write
- ✅ **Retry Logic:** Exponential Backoff für Archive-Zugriff
- ✅ **Health Checks:** GET /health auf allen Agents, Port-Policy Validator läuft in CI
- ✅ **Error Recovery:** Graceful Degradation bei Archive-Ausfällen, keine Daten-Verlust

---

## 6) Risiken & Annahmen

### Annahmen

✅ Der Host hat öffentlich erreichbaren Domain/Nginx für Webhook (falls Webhook-Modus gewählt)  
✅ Entwickler haben Zugriff auf Projektwurzeln-Verzeichnis und nötige Rechte (Lesen/Schreiben)  
✅ Aggregierte Module (opena2, opena3, opena4, opena5, opena20) werden einzeln entwickelt aber im selben Governance-Rahmen  
✅ Python 3.13+ mit venv313 verfügbar; Pydantic v2 kompatibel  

### Risiken & Mitigationen

| Risiko | Eintrittswahrscheinlichkeit | Impact | Mitigation |
|--------|---------------------------|--------|-----------|
| **Portkonflikte (unberechtigt 8080)** | Mittel | Hoch | Pre-Commit Check, CI Port-Policy Validator |
| **Doppel-Writes/Blobs ohne Dedupe** | Mittel | Hoch | Dedupe-Engine mit Hash-Check vor Write |
| **Telegram API Limits/Rate-Limits** | Hoch | Mittel | Queue-Based Batching, Exponential Backoff |
| **Unsichere Secrets/Logs** | Mittel | Kritisch | .env-basiertes Secrets, Maskierung-Filter in Logs |
| **Fehlende CI/Pre-Commit** | Niedrig | Mittel | GitHub Actions + Pre-Commit Hooks enforced |
| **Archive-Ausfälle** | Niedrig | Kritisch | Health-Check, Retry-Logic, redundante Backups |
| **Diff-Apply-Fehler (VSCode)** | Mittel | Mittel | Validierung vor Apply, Rollback-Mechanism |

---

## 7) Erfolgs-Kriterien (Definition of Done)

✅ **Infrastruktur:**
- Alle 7 Schritte dokumentiert & spec'd
- Port-Governance enforced in CI
- Dedupe-Engine läuft, 0 Doppel-Blobs
- Audit-Index compliant, 100% Nachverfolgbarkeit

✅ **Funktionalität:**
- opena1 (Koordinator) mit 7.1-Validation läuft
- opena2 (Archivator) mit Persistenz/Dedupe läuft
- opena4 (Telegram) Bot antwortet auf Commands
- opena5 (VS Code) öffnet Workspace, zeigt Diffs
- opena3 (UI) zeigt Agenten-Status live

✅ **Qualität:**
- 80%+ Unit-Test Coverage
- 0 Critical Security Findings
- CI/CD 100% Green (Linting, Tests, Port-Check)
- Dokumentation: 5/5 Schritte complete

✅ **Operations:**
- Health-Checks auf allen Agents
- Monitoring/Alerting läuft (opena20)
- Production Runbook verfügbar
- SLA-Komitment: 99.9% Uptime for Core Services

---

## 8) Dokumentation & Artefakte

### Verzeichnisstruktur

```
/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/
├── README.md                          # Projekt-Übersicht & Setup
├── .env.example                       # Secrets-Template
├── .pre-commit-config.yaml            # Pre-Commit Hooks
├── .github/workflows/portier-ci.yml   # CI/CD Pipeline
│
├── docs/
│   ├── PROJECT_CHARTER.md             # Dieses Dokument
│   ├── SCHRITT_01_INIT.md             # Projektinitialisierung
│   ├── SCHRITT_02_TOOL_REGISTRY.md    # Tool-Mapping & Registry
│   ├── SCHRITT_03_SAFEPOINT_FORMAT.md # Safepoint & Audit-Trail
│   ├── SCHRITT_04_OPENA4_TELEGRAM.md  # Telegram-Bridge Spec
│   ├── SCHRITT_05_OPENA5_VSCODE_BRIDGE.md  # VS Code Integration
│   ├── SCHRITT_06_OPENA2_ARCHIVATOR.md     # Archivator Deep-Dive
│   ├── SCHRITT_07_MONITORING.md       # Monitoring & Release
│   │
│   ├── examples/
│   │   ├── opena4.service             # Systemd Service File
│   │   ├── opena5.service
│   │   └── nginx-webhook.conf         # HTTPS Proxy Config
│   │
│   └── OPERATIONS.md                  # Operator Guide
│
├── 1.portier_openai/                  # Core opena1 Module
│   ├── schemas.py                     # Pydantic Models
│   ├── koordinator.py                 # REST Endpoints
│   ├── main_production.py             # Entry Point
│   └── venv313/                       # Python 3.13 venv
│
├── 4.opena2_archivator/               # Archivator Module
│   ├── persistor.py
│   ├── dedupe_engine.py
│   └── audit_index.py
│
└── .runtime/
    ├── port_leases.json               # Active Port Assignments
    ├── HEADS.json                     # Latest Commit Hashes
    └── INTEGRITY.json                 # Checksum Manifest
```

---

## 9) Governance & Policies

### Commit Policy

- **Message Format:** `<type>: <scope> – <message>`
  - `feat:` Neue Features, opena-Module
  - `fix:` Bugfixes, Compliance-Fixes
  - `docs:` Dokumentation
  - `chore:` Maintenance, Port-Leases
  - `test:` Tests, QA

- **Example:** `feat: implement step 1 - 7.1 strict validation for opena1 coordinator`

### Review Policy

- **Minimum Reviewers:** 1 (Infra-Lead)
- **Checks:** CI Pass + Port-Policy Validator + Schema-Check
- **Approval:** Code-Owner sign-off

### Release Policy

- **Release Tag Format:** `v1.0.0-opena<N>-YYYYMMDD`
- **Frequency:** Weekly Snapshots, Monthly Releases
- **Deployment:** CD to staging, manual promotion to prod

---

## 10) Kommunikation & Eskalation

### Status Reporting

- **Weekly:** Meilenstein-Updates, Risiko-Review
- **Daily:** CI/CD Status, Incident Alerts
- **Monthly:** Release Planning, Retrospective

### Eskalation Path

1. **Developer** → **Infrastruktur-Lead** (Governance Issues)
2. **Infrastruktur-Lead** → **Projektleitung** (Scope Changes)
3. **Projektleitung** → **Executive** (Budget/Resource Issues)

---

## 11) Sign-Off

| Rolle | Name | Datum | Unterschrift |
|-------|------|-------|-------------|
| Projektleitung | — | — | — |
| Infrastruktur-Lead | — | — | — |
| QS-Lead | — | — | — |

---

**Projekt-ID:** `HYPER-DASHBOARD-001`  
**Version History:**  
- v1.0 – 2025-11-09 UTC – Initial Charter

**Referenzen:**
- GitHub Repo: https://github.com/jokicdanijel/Gesamtprojekt-start
- Jira Board: *(ggf. Link)*
- Slack Channel: *(ggf. Channel)*
