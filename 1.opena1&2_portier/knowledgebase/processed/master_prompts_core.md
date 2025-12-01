# Master-Prompts - Processed Core Version

## 1. Portier-Gesetze

### Option-2 verbindlich

- Immer: OpenAI → opena1 → opena2 → kordp → Tool
- Immer: Tool → opena2 → opena1 → OpenAI
- Keine Abkuerzungen
- Keine Backdoors
- Keine Shortcuts

### Safepoint-Pflicht

- Jeder Command erzeugt CMD-Safepoint
- Jede Response erzeugt RESP-Safepoint
- Format: SP<n>_src→dst_{CMD|RESP}.json
- Unicode-Pfeil → (U+2192) PFLICHT
- Append-Only

### Strict:true immer

- additionalProperties: false
- JSON Schema Draft 2020-12
- Keine zusaetzlichen Felder
- Vollstaendige Validierung

### Keine Abweichung der Rollenbezeichnungen

- opena1 = Koordinator
- opena2 = Archivator
- kordp = Koordinatport
- archivp = Archivport
- Unveraenderlich

### Keine Placeholder

- Kein "TODO: implement"
- Kein "...existing code..."
- Kein "# Platzhalter"
- Immer vollstaendige Implementation

## 2. Zwei-Ebenen-Denken (PDI)

### Meta-Ebene

- Selbstpruefung
- Validierung
- Konsistenz-Checks
- Policy-Enforcement
- Qualitaets-Gates

### Objekt-Ebene

- Generieren
- Korrigieren
- Freigeben
- Implementieren
- Testen

### Wechselspiel

1. Meta: Analysiere Anforderung
2. Objekt: Generiere Loesung
3. Meta: Validiere Loesung
4. Objekt: Korrigiere Fehler
5. Meta: Freigabe oder Iteration

## 3. Kapitelprozess

### 1. Analyse

- Anforderung verstehen
- Kontext sammeln
- Dependencies identifizieren
- Constraints definieren

### 2. Struktur

- Architektur-Entscheidungen
- Modulaufteilung
- Interface-Definitionen
- Schema-Design

### 3. Generierung

- Code schreiben
- Dokumentation erstellen
- Tests implementieren
- Config bereitstellen

### 4. Kommentar

- Code-Review
- Architektur-Review
- Policy-Check
- Konsistenz-Pruefung

### 5. Verbesserung

- Fehler beheben
- Optimierungen
- Refactoring
- Cleanup

### 6. Validierung

- Unit-Tests
- Integration-Tests
- Schema-Validierung
- Port-Policy-Check

### 7. Selbstpruefung

- Meta-Ebene-Review
- Vollstaendigkeit
- Konformitaet
- Qualitaet

### 8. Freigabe

- Production-Ready
- Dokumentiert
- Getestet
- Validiert

## 4. Tool-Module

### Analytik

- Anforderungs-Analyse
- Dependency-Analyse
- Impact-Analyse
- Konsistenz-Analyse

### Linguistik

- Namenskonventionen
- Dokumentations-Stil
- Code-Kommentare
- Error-Messages

### Technik

- Code-Generierung
- Schema-Validierung
- Testing
- Deployment

### Validierung

- Schema-Checks
- Port-Policy-Checks
- Option-2-Flow-Checks
- Safepoint-Checks

### GitHub-Simulation

- Branch-Strategie
- Commit-Messages
- Pull-Request-Beschreibungen
- Issue-Tracking

## 5. Ausgaberegel

### Keine unvollstaendigen Dateien

- Immer vollstaendige Module
- Immer vollstaendige Funktionen
- Immer vollstaendige Tests
- Immer vollstaendige Dokumentation

### Keine TODOs

- Keine "TODO: implement"
- Keine "FIXME: ..."
- Keine "XXX: ..."
- Immer produktionsreifer Code

### Konsistente Struktur

- Einheitliche Formatierung
- Einheitliche Namenskonventionen
- Einheitliche Fehlerbehandlung
- Einheitliche Logging

## 6. Code-Qualitaet

### Python

- Black formatting (line-length 120)
- Ruff linting
- isort imports
- Type hints (mypy)

### JSON

- Strict schemas
- additionalProperties: false
- Vollstaendige Validierung
- Pretty-printed

### Markdown

- Einheitliche Struktur
- Code-Bloecke mit Sprache
- Tabellen formatiert
- Listen einheitlich

## 7. Error-Handling

### Strukturiert

```python
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": { ... }
  }
}
```

### Logged

- ERROR level fuer kritische Fehler
- WARNING level fuer Warnungen
- INFO level fuer normale Operationen
- DEBUG level nur in DEV-Mode

### Nicht schlucken

- Immer propagieren
- Immer loggen
- Immer strukturiert
- Immer mit Context

## 8. Testing

### Unit-Tests

- Pytest
- 100% Coverage fuer kritische Pfade
- Mocking fuer externe Services
- Fixtures fuer Test-Daten

### Integration-Tests

- End-to-End-Tests
- Option-2-Flow-Tests
- Safepoint-Tests
- Port-Policy-Tests

### Validation-Tests

- Schema-Validierung
- Port-Policy-Validierung
- Option-2-Flow-Validierung
- Konsistenz-Tests

## 9. Master-Prompts Referenzen

### Vollstaendige Service-Prompts

Die detaillierten Master-Prompts für die Kern-Services sind hier dokumentiert:

- **opena1 (Koordinator):** `knowledge/prompts/MASTER_PROMPT_OPENA1.md`
- **opena2 (Archivator):** `knowledge/prompts/MASTER_PROMPT_OPENA2.md`
- **Integration Guide:** `knowledge/prompts/PROMPT_INTEGRATION_GUIDE.md`

### opena1 Kern-Aufgaben

1. **Request Intake (Request71)**
   - Schema-Validierung (Pydantic `extra="forbid"`)
   - Pflichtfelder: request_id, timestamp, source, (user_query | action+metadata)
   - Fehler → VALIDATION_ERROR Safepoint

2. **Decision72 – Routing-Entscheidung**
   - Service-Mapping via Routing-Matrix
   - Delegation an kordp oder direkte Antwort
   - Nur dokumentierte service_target/action nutzen

3. **Safepoint-Erzeugung (CMD/RESP)**
   - CMD vor jedem Dispatch
   - RESP nach jedem Tool-Ergebnis
   - Struktur: src, dst, kind, body, strict:true

4. **Knowledgebase-Hierarchie**
   - Priorität 1: KB_OPENA1_COORDINATOR, KB_SYSTEM_INTEGRATION_FLOWS, KB_ARCHIVE_PATTERNS
   - Priorität 2: KB_DASHBOARD_INTEGRATION, KB_TELEGRAM_BRIDGE, KB_PROGRESS_REPORT
   - Priorität 3: KB_EXPANSION_PLAN, KB_INDEX_CURRENT

### opena2 Kern-Aufgaben

1. **Safepoint-Store (Append-Only)**
   - Validierung eingehender Safepoints
   - Persistierung: archivp/YYYY/MM/DD/SP<TS>_src→dst_kind.json
   - Index: index.jsonl (jede Zeile = 1 Safepoint)

2. **Dateiname-Konvention**
   - Unicode-Pfeil U+2192 (→) PFLICHT
   - Format: SP<TIMESTAMP>_<src>→<dst>_<kind>.json
   - Beispiel: SP20251127T143052_opena1→kordp_CMD.json

3. **Secrets & Redaction**
   - Automatische Erkennung: password, api_key, token, secret, authorization
   - Ersetzung: "_**REDACTED**_"
   - Niemals Klartext in Safepoints oder index.jsonl

4. **Query-Operationen**
   - GET /archiv/last?n=10
   - GET /archiv/by_day?date=YYYY-MM-DD
   - GET /archiv/search?src=opena1&dst=kordp

### Port-Policy (erweitert)

**Backend-Services (PORTIER-Core):**

- Range: 12344–12399
- opena1: 12344, opena2: 12345, kordp: 12346, Dashboard: 12349

**Externe Services (außerhalb PORTIER):**

- OpenWebUI: 3000 (Upstream, via Adapter 12347/12350)
- ComfyUI: 8188 (Upstream, via Adapter 1235x)
- Port 8080: UI-only (z.B. OpenWebUI UI), KEIN Backend

**Enforcement:**

- Backend auf 8080 → ablehnen + SECURITY_OP Safepoint
- Backend außerhalb 12344–12399 → ablehnen + SECURITY_OP Safepoint

### HTML-Wissensdatenbank

**Datei:** `knowledge/ui/opena1_knowledge_dashboard.html`

**Features:**

- Live-Status von opena1 (GET /health)
- Knowledgebase-Dokumenten-Links (Priorität 1–3)
- Safepoints-Tabelle (GET /archiv/last?n=10)
- Routing-Matrix-Übersicht
- Option-2-Flow Visualisierung
- Port-Policy Enforcement-Hinweise

**Hosting:**

- Kann von opena21 (Dashboard) oder eigenständigem Webserver gehostet werden
- JavaScript für dynamisches Nachladen von Status + Safepoints

### Integration in AI-Systeme

**ChatGPT / Custom GPTs:**

- System Instructions: MASTER_PROMPT_OPENA1.md kopieren
- Knowledge Files: KB-Dokumente hochladen (Priorität 1–3)
- Test: "Welche Schritte führst du als opena1 durch?"

**VS Code Copilot:**

- .github/copilot-instructions.md erweitern mit Prompt-Referenzen
- .vscode/settings.json → contextFiles ergänzen
- Chat-Modus: @workspace Wie implementiere ich Option-2-konforme Route?

**Python/FastAPI Agent-Start:**

```python
from pathlib import Path

def load_system_prompt() -> str:
    prompt_path = Path(__file__).parent / "knowledge/prompts/MASTER_PROMPT_OPENA1.md"
    return prompt_path.read_text(encoding="utf-8")

system_prompt = load_system_prompt()
# Nutzen in OpenAI API Calls
```

**CI/CD Validierung:**

- Pre-Commit Hook: Prüfe Existenz + Unicode-Pfeil
- GitHub Actions: validate-prompts.yml workflow
- Semantic Versioning für Prompt-Updates (Major.Minor.Patch)

### Fehlerverhalten (erweitert)

**opena1-spezifisch:**

- Keine "erfundenen" Aktionen
- Agent unreachbar → ERROR_RESP Safepoint
- Option-2-Kette niemals bypassen
- Fehlerstruktur: code, message, details

**opena2-spezifisch:**

- I/O-Fehler → klar kommunizieren, nicht schlucken
- Transaktionale Garantie: Datei + Index konsistent
- Fehler in Datei → kein Index-Eintrag
- Fehler in Index → Datei löschen oder INCOMPLETE

### Onboarding neue Entwickler

**Pflichtlektüre (vor Code-Schreiben):**

1. MASTER_PROMPT_OPENA1.md
2. MASTER_PROMPT_OPENA2.md
3. PORTIER_3.0_SYSTEM_ARCHITECTURE.md
4. master_prompts_core.md (dieses Dokument)

**Onboarding-Checklist:**

- [ ] Master-Prompt opena1 gelesen
- [ ] Master-Prompt opena2 gelesen
- [ ] Option-2-Flow verstanden
- [ ] Port-Policy memoriert
- [ ] Safepoint-Naming gelernt
- [ ] Ersten Test-Safepoint erzeugt
- [ ] Health-Check erfolgreich (curl <http://127.0.0.1:12344/health>)
