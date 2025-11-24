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
