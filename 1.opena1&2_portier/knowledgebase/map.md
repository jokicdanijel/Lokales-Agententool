# Wissenskarte - Elion Hyper-Dashboard Knowledge Base v1.0

## 1) Kernrollen

### Core Infrastructure

- **opena1 - Koordinator** (Port 12344)
  - Validiert Eingaben (Schema 7.1)
  - Waehlt Tools basierend auf Command
  - Baut CMD-Envelopes
  - Erzeugt 7.2-Responses

- **opena2 - Archivator** (Port 12345)
  - Safepoints (CMD + RESP)
  - Ablage unter archivp/YYYY/MM/DD/
  - Indexpflege ueber index.jsonl
  - Append-Only Archivierung

- **kordp - Kordinatport** (Port 12346)
  - Fuehrt Tools aus
  - Dispatcht Commands
  - Sammelt Responses

- **archivp - Archivport** (Filesystem)
  - Speichert Safepoints
  - Unicode-Pfeil Naming (SP<n>_src→dst_{CMD|RESP}.json)
  - Datums-Partitionierung

### Extended Services

- **opena3 - OpenWebUI Terminal** (Port 12347)
- **opena4 - Telegram** (Port 12346)
- **opena5 - VS Code Bridge** (Port 12349)
- **opena20 - Dashboard** (Port 12362)

## 2) Option-2-Flow (Heilige Regel)

### Hinweg (Command-Flow)

```
OpenAI → opena1 → opena2 → kordp → Tool
```

### Rueckweg (Response-Flow)

```
Tool → opena2 → opena1 → OpenAI
```

### Verboten

- Direktcalls (OpenAI → Tool)
- Shortcuts (opena1 → kordp ohne opena2)
- Backdoors
- Tool-zu-Tool ohne Koordinator

## 3) Inhaltliche Gruppen

### Portier-System

- Systemarchitektur
- Routing OpenAI → opena1 → opena2 → kordp
- Safepoint-Struktur
- Endpunkte:
  - POST /log/opena1 (Pre-Safepoint CMD)
  - POST /dispatch/kordp (Tool-Dispatch)
  - POST /finalize/opena2 (Post-Safepoint RESP)
  - POST /store/archivp (Snapshot)

### Archivator

- CMD/RESP Verarbeitung
- JSON-Dateistruktur
- index.jsonl Regeln (append-only)
- Forwarding-Prozesse
- Unicode-Pfeil → (U+2192) Pflicht

### Koordinator

- Schema 7.1 (Request) und 7.2 (Response)
- Tool-Registry Integration
- Validierung (strict: true, additionalProperties: false)
- Entscheidungslogik (command → target_preference)

### Routing

- Telegram Integration (opena4)
- OpenWebUI Integration (opena3 + Adapter)
- Agenten-Kommunikation
- Dedup-Mechanismen

### Dashboard

- Statusmodule (opena20)
- Hyper-Dashboard-Konfigurationen
- Agentenstatus
- SSE-Events (Server-Sent Events)
- Bearer-Token Security

### Port-Policy

- Erlaubte Ports: 12344-12349 (Backend)
- Verbotene Ports: 8080 (UI-only fuer OpenWebUI)
- Zentrale Registry: config/registry.json
- Middleware-Enforcement

### Schemas

- JSON Schema Draft 2020-12
- Strict Mode (additionalProperties: false)
- 7.1 Request Schema
- 7.2 Response Schema
- 8.1 Archivator Request
- 8.2 Archivator Response

## 4) Quellen (knowledge/raw/)

### Architektur-Dokumente

- portier-system.md
- option-2-flow.md
- port-policy.md
- agent-registry.md

### Service-Spezifikationen

- koordinator-opena1.md
- archivator-opena2.md
- dashboard-opena20.md
- openwebui-opena3.md

### Schemas

- schemas-71-72.md
- safepoint-format.md

### Integration

- routing-patterns.md
- security-policies.md

## 5) Verarbeitung

### processed/

- Segmentierte Abschnitte nach Themen
- Konsolidierte technische Beschreibungen
- Regeln & Policies
- API-Endpunkt-Dokumentation

### vectors/

- Embeddings fuer Tool-Agents
- Modell: text-embedding-3-large
- Provider: OpenAI
- Document-Chunk-Zuordnung

### index.json

- Zentrale Wissensstruktur
- File-Metadaten
- Document-Registry
- Embedding-Mapping

### manifest.json

- System-Metadaten
- Port-Policy-Definition
- Agent-Mapping
- Path-Konfiguration

## 6) Status

- Knowledge Base vollstaendig initialisiert
- Rohdaten-Struktur bereit
- Index generiert
- Map erstellt
- Manifest fertig
- Strict-konform
- Produktionsreif

## 7) Naechste Schritte

1. **Rohdaten befuellen** (knowledge/raw/)
   - Portier-Dokumentation
   - Archivator-Specs
   - Koordinator-Logik
   - Dashboard-Konfiguration
   - OpenWebUI-Integration
   - Routing-Patterns

2. **Verarbeitung** (knowledge/processed/)
   - Automatische Segmentierung
   - Thematische Gruppierung
   - Normalisierung
   - KI-freundliche Aufbereitung

3. **Embeddings** (knowledge/vectors/)
   - Vollstaendige Vektorisierung
   - Tool-Agent-Zuordnung
   - Suchindex-Erstellung

4. **Dashboard-Integration**
   - Knowledge-Base-Modul in opena20
   - Live-Suche
   - Agent-Zugriff

## 8) Validierung

- Alle Dateien UTF-8
- Kein Platzhalter-Code
- Keine TODO-Tags
- Strikte Policy-Konformitaet
- Port-Policy eingehalten
- Option-2-Flow respektiert
- Schema-Validierung aktiv
