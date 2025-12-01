# 🧠 SYSTEM_OVERVIEW – ELION Hyper-Dashboard

**Version:** 3.0  
**Datum:** 27. November 2025  
**Status:** ✅ **PRODUCTION-READY**  
**Scope:** Vollständige Systemübersicht für alle Stakeholder

---

## 📋 Überblick über die Projektstruktur

Die beiden zentralen Wissensdokumente (`.github/copilot-instructions.md` und `.github/copilot-master-prompt.md`) bilden das **zentrale Wissenssystem** für das ELION Hyper-Dashboard Projekt.

Es handelt sich um ein **Multi-Agenten-System** basierend auf:

- **Python 3.13**
- **FastAPI**
- **Ubuntu 25.04**
- **venv313** (virtuelle Umgebung)

Das System orchestriert verschiedene Dienste mit einer **strikten Architektur** und klar definierten Kommunikationswegen.

---

## ✅ Die Completion Checklist (copilot-instructions.md)

Dieses Dokument ist eine **detaillierte Projektabschlusscheckliste** mit **40 abgeschlossenen Aufgaben**, unterteilt in drei Phasen:

### Phase 1: Core Infrastructure (20 Tasks)

Umfasst:

- VS Code-Konfigurationen (`.vscode/launch.json`, `.vscode/tasks.json`)
- Orchestrierungsskripte (`bin/ops.sh`)
- Service-Management-Tools (`start_all.sh`, `stop_all.sh`, `verify_stack.sh`)
- Umfangreiche Dokumentation (`docs/OPERATIONS.md`, `docs/OPENWEBUI_INTEGRATION.md`)

**Besonders wichtig:** Die **Root-Wrapper-Skripte**, die zentrale Befehle vom Projektroot aus delegieren.

### Phase 2: OpenWebUI-Integration (20 Tasks)

Hier wurden implementiert:

- **HTTP-Adapter** (Port 12350)
- **Dedizierter Agent opena3** (Port 12347)
- **Dashboard-Erweiterungen** (Port 12349)

Die Integration umfasst eine **komplette UI-Erweiterung** mit:

- Modal-Dialog für Chat
- Bearer-Token-Authentifizierung
- Server-Sent Events (SSE) für Echtzeit-Updates

### Phase 3: AI-Dokumentation (1 Task)

- **200+ Zeilen umfassende Anleitung** für GitHub Copilot
- Beschreibt Architektur, Ports, Workflows und Konventionen

---

## 🚀 Der Hyper-Master-Prompt (copilot-master-prompt.md)

Dieses Dokument ist das **absolute Referenzsystem** – ein umfassender Systemprompt für alle KI-Interaktionen.

Es definiert die Rolle eines **"allwissenden" Co-Piloten**, der:

- Die **komplette Systemarchitektur** kennt
- **Niemals von festgelegten Regeln** abweichen darf
- Immer **architekturkonform**, **portkonform**, **strict-schema-konform** arbeitet

---

## 🏛️ Systemarchitektur (Abschnitt 1-2)

### Zielsystem

- **OS:** Ubuntu 25.04
- **Python:** 3.13.x
- **Virtuelle Umgebung:** `venv313`
- **Runtime:** FastAPI + uvicorn

### Projektstamm

```
/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt
```

### Ordnerstruktur (unveränderlich)

| Ordner | Funktion | Ports |
|--------|----------|-------|
| `1.opena1&2_portier` | Kernagenten (Koordinator, Archivator) | 12344-12346 |
| `2.opena3_openwebui` | Terminal-Agent | 12347 |
| `19.opena20_dashboard_agent` | FastAPI-Backend + Dashboard | 12349-12350 |
| `3-18, 20` | Spezialisierte Agenten | 12348-12367 |

### Agentennamen (fixiert, unveränderbar)

- **opena1** = Koordinator (12344)
- **opena2** = Archivator (12345)
- **kordp** = Koordinatport (12346)
- **archivp** = Filesystem-Archiv

Diese Namen dürfen **niemals geändert werden**, da sie die **fundamentale Identität** des Systems darstellen.

---

## 🔄 Option-2-Nachrichtenfluss (heiligste Regel)

Dies ist die **heiligste Regel** des Systems: Alle Nachrichten müssen einem **festen Pfad** folgen:

### ➡️ Hinweg (Command-Flow)

```
OpenAI → opena1 → opena2 → kordp → Tool
```

### ⬅️ Rückweg (Response-Flow)

```
Tool → opena2 → opena1 → OpenAI
```

### ❌ Verboten

- Direktverbindungen (z.B. `OpenAI → Tool`)
- Shortcuts (z.B. `opena1 → kordp`)
- Backdoors
- Bypasses
- Tool-zu-Tool-Kommunikation ohne Koordinator

**Der Archivator (opena2) ist immer in der Kette**, um jeden Schritt zu protokollieren.

---

## 🔌 Port-Policy (gesetztes Gesetz)

### Erlaubte Backend-Ports

```
12344–12399
```

### Port-Mapping (Standard)

| Service | Port | Typ |
|---------|------|-----|
| opena1 (Koordinator) | 12344 | FastAPI |
| opena2 (Archivator) | 12345 | FastAPI |
| kordp (Koordinatport) | 12346 | FastAPI |
| opena3 (OpenWebUI) | 12347 | FastAPI |
| Dashboard | 12349 | FastAPI + SSE |
| OpenWebUI Adapter | 12350 | FastAPI |

### Port 8080 (exklusiv)

**Port 8080 ist exklusiv für die OpenWebUI-Benutzeroberfläche reserviert** und darf **niemals für Backend-Services** genutzt werden.

### Enforcement

Diese Regel wird durch **Middleware** in jedem FastAPI-Service durchgesetzt:

```python
PORT_POLICY_MIDDLEWARE = PortPolicyMiddleware(
    allowed_ports=range(12344, 12400),
    forbidden_ports=[8080]
)
```

---

## 📦 Safepoints & Archivator (fundamentales Kernsystem)

Das System verwendet ein **Append-Only-Archiv** mit strikten Namenskonventionen:

### Naming Convention

```
SP<laufnummer>_src→dst_{CMD|RESP}.json
```

**Kritisch:** Der Unicode-Pfeil `→` (U+2192) ist **Pflicht**.

### Speicherstruktur

```
archivp/
├── YYYY/
│   └── MM/
│       └── DD/
│           ├── SP00001_opena1→kordp_CMD.json
│           └── SP00001_kordp→opena1_RESP.json
└── index.jsonl  (append-only)
```

### Unveränderbare Regeln

- ✅ **Nur anhängen** (append-only)
- ❌ **Niemals überschreiben**
- ❌ **Niemals löschen**
- ❌ **Niemals modifizieren**
- ✅ Archivator ist **immer in der Kette**
- ✅ Timestamps in **UTC**
- ✅ **Full envelope logging**

Die **Integrität des Archivs ist fundamental** für das System.

---

## 🧱 JSON-Schemas & Sicherheit (Abschnitt 6-9)

### Strict Mode (non-negotiable)

Alle Pydantic-Modelle müssen **Strict Mode** verwenden:

```python
class MyModel(BaseModel):
    class Config:
        extra = "forbid"  # Keine zusätzlichen Properties erlaubt
```

### Dashboard (Port 12349)

Das Dashboard verwendet:

- **HTTPBearer-Authentifizierung** (JWT-Token aus `.env`)
- **CORS-Middleware** mit Port-Validierung
- **Rate-Limiting** (5 Requests/Minute für Chat-Endpoints)
- **Eigener SSEBus** für Server-Sent Events

### Security-Policies

- ✅ Alle Secrets aus `.env` laden
- ❌ **Niemals hardcoden** (API-Keys, Tokens)
- ✅ Token-Bootstrap via `bin/env_bootstrap.sh` (generiert UUID-Token)
- ✅ Secret-Masking in Logs
- ✅ Audit-Trails für kritische Operationen

---

## 🌐 OpenWebUI-Integration (Abschnitt 8)

### Architektur-Flow

```
User → OpenWebUI (8080) → Adapter (12350) → opena3 (12347) → Option-2-Flow
```

### Komponenten

1. **OpenWebUI (8080)**
   - Docker-Container `open-webui/open-webui:main`
   - **Nur Frontend-Assets** (keine Backend-Logik)

2. **Adapter (12350)**
   - `openwebui_adapter.py`
   - Forwardet HTTP-Requests: `Dashboard → OpenWebUI`

3. **opena3 (12347)**
   - `main_openwebui_agent.py`
   - Agenten-Wrapper um OpenWebUI-Terminal
   - Endpoints: `/health`, `/command`, `/invoke`

4. **Dashboard (12349)**
   - `GET /api/openwebui/status` – Health-Check opena3
   - `POST /api/openwebui/chat` – Chat-Request (rate-limited, SSE)

5. **UI (`ui_index.html`)**
   - Chat-Modal (`#openwebuiModal`)
   - Token-Handling via `localStorage.getItem('bearer_token')`
   - State-Indicators: `loading`, `ok`, `error`

---

## 🧪 Codequalität & Verhalten

### Must-Have-Kriterien

- ✅ Python 3.13 kompatibel
- ✅ Vollständige Module (keine Stubs)
- ✅ **Keine TODOs** im Production-Code
- ✅ **Keine fiktiven Platzhalter** (`# TODO: implement`)
- ✅ Keine leeren Files
- ✅ Tests lauffähig (`pytest -v`)

### Code-Style

```bash
# Black formatting
black --line-length 120 .

# Flake8 linting
flake8 --max-line-length=120 --ignore=E203,W503

# Type-Checking (optional)
mypy --strict main.py
```

---

## ⚡ Systemstart & Operations

### Stack starten

```bash
bin/ops.sh start
```

Startet alle Services:

- opena1 (12344)
- opena2 (12345)
- kordp (12346)
- opena3 (12347)
- Dashboard (12349)
- OpenWebUI Adapter (12350)

### Stack stoppen

```bash
bin/ops.sh stop
```

### Status prüfen

```bash
bin/ops.sh status | jq .
```

### Logs anzeigen

```bash
bin/ops.sh logs
# Oder einzeln:
tail -f logs/opena1.nohup.log
```

### Integration testen

```bash
bin/verify_stack.sh
```

Prüft: Ports, Health-Checks, Option-2-Flow, Safepoints

---

## 📚 Referenzen & Weitere Dokumentation

| Dokument | Pfad | Zweck |
|----------|------|-------|
| **Completion Checklist** | `.github/copilot-instructions.md` | Phase 1-3 Tracking |
| **Master Prompt** | `.github/copilot-master-prompt.md` | Vollständiges Systemwissen |
| **Operations Guide** | `docs/OPERATIONS.md` | Runtime-Befehle |
| **OpenWebUI Integration** | `docs/OPENWEBUI_INTEGRATION.md` | opena3 + Adapter Specs |
| **Troubleshooting** | `docs/TROUBLESHOOTING.md` | Fehlerszenarien + Lösungen |
| **API Documentation** | `docs/OPENWEBUI_API.md` | Endpoint-Specs |
| **Quick Start** | `README_STACK_START.md` | Schnelleinstieg |

---

## 🔥 Kurzmodus: Unveränderbare Kernregeln

| Regel | Details |
|-------|---------|
| **Option-2-Kette** | Immer `opena1 → opena2 → kordp → Tool` |
| **Ports** | 12344–12399 (Backend), 8080 (UI-only) |
| **Safepoints** | Append-only, Unicode-Pfeil `→`, `YYYY/MM/DD` |
| **JSON-Schemas** | `extra="forbid"`, strict mode |
| **Agentennamen** | opena1, opena2, kordp, archivp (fest) |
| **Top-Level-Struktur** | Keine neuen Ordner, keine Umbenennungen |
| **Backdoors** | Keine, niemals, unter keinen Umständen |
| **Code-Qualität** | Produktiv, vollständig, keine Platzhalter |
| **ENV-Secrets** | Niemals hardcoded |

---

**Ende des SYSTEM_OVERVIEW.**  
**Maintainer:** Danijel Jokic (ELION Team)  
**Letzte Aktualisierung:** 27. November 2025  
**Status:** ✅ **PRODUCTION-READY**
