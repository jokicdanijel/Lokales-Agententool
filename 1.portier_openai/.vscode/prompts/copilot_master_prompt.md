# 🤖 Copilot Project Executor - Safe Mode

## Systemkontext

### Projektidentifikation
- **Name:** Portier / ELION Hyper-Dashboard 2.0
- **Version:** 1.0 Production
- **Umgebung:** Linux Mint
- **Python:** 3.13.x (venv313)
- **Hauptpfad:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt`

### Architekturmodus
- **Option 2:**
  - Hinweg: OpenAI → opena1 → opena2 → kordp → Tool
  - Rückweg: Tool → opena2 → opena1 → OpenAI

### Port-Policy
- ✅ Erlaubt: 12344-12399
- ❌ Verboten: 8080 (außer internes OpenWebUI)

## Projektregeln

### 1. Strict Mode
```python
"strict": true  # Immer aktiviert
```

### 2. Safepoint-System
```
archivp/YYYY/MM/DD/SP<nummer>_src→dst_{CMD|RESP}.json
```

### 3. Audit-Trail
- Lückenlose Dokumentation in `index.jsonl`
- Append-only Logging

### 4. Sicherheit
- OpenAI-Keys nur aus `.env`
- Token-basierte Authentifizierung
- Rate Limiting: 60 req/min

## Implementierungsrichtlinien

### Dateistruktur
```
project_root/
├── opena1/  # Koordinator
├── opena2/  # Archivator
├── kordp/   # Dispatcher
└── tools/   # Agenten
```

### Codierungsstandards
```python
# Copilot Instruction: Jede Funktion benötigt:
# 1. Beschreibende Docstring
# 2. Typ-Annotationen
# 3. Fehlerbehandlung
# 4. Logging
def example_function(param: str) -> bool:
    """
    Funktionsbeschreibung hier.
    """
    try:
        # Implementation
        return True
    except Exception as e:
        log.error(f"Fehler: {e}")
        return False
```

### API-Endpunkte
```python
# Copilot Instruction: Alle Endpunkte müssen:
# 1. Port-Policy befolgen
# 2. Health-Check anbieten
# 3. Strict Mode aktivieren
# 4. Safepoints erzeugen
```

## Qualitätssicherung

### Tests
```python
# Copilot Instruction: Teste:
# 1. Port-Policy-Konformität
# 2. Safepoint-Generierung
# 3. Strict Mode
# 4. Fehlerbehandlung
```

### Logging
```python
# Copilot Instruction: Logge:
# 1. Alle API-Aufrufe
# 2. Safepoint-Erzeugung
# 3. Fehler mit Kontext
# 4. Audit-relevante Events
```

## Sicherheitsrichtlinien

### Token-Handling
```python
# Copilot Instruction: Tokens:
# 1. Nur aus .env laden
# 2. Nie im Code speichern
# 3. Rate Limiting aktivieren
```

### Port-Sicherheit
```python
# Copilot Instruction: Ports:
# 1. Nur 12344-12399 erlaubt
# 2. Port 8080 blockieren
# 3. Health-Checks aktivieren
```

## Deployment

### Voraussetzungen
```bash
# Copilot Instruction: Setup:
# 1. Python 3.13 venv
# 2. Abhängigkeiten aus requirements.txt
# 3. .env Konfiguration
```

### Start
```bash
# Copilot Instruction: Start:
# 1. Preflight-Checks
# 2. Port-Validierung
# 3. Safepoint-Initialisierung
```

## Wartung

### Logs
```python
# Copilot Instruction: Log-Rotation:
# 1. Tägliche Archivierung
# 2. Append-only Index
# 3. Backup-Strategie
```

### Monitoring
```python
# Copilot Instruction: Überwache:
# 1. API-Gesundheit
# 2. Port-Nutzung
# 3. Token-Verbrauch
```