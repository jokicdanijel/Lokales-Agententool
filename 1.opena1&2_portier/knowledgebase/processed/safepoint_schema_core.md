# Safepoint-Schema - Processed Core Version

## 1. Naming Convention

### Format
```
SP<laufnummer>_src→dst_{CMD|RESP}.json
```

### Komponenten
- **SP** - Prefix (Safepoint)
- **<laufnummer>** - 5-stellig, zero-padded (00001, 00002, ...)
- **src** - Quell-Agent (opena1, kordp, etc.)
- **→** - Unicode-Pfeil U+2192 (PFLICHT)
- **dst** - Ziel-Agent (kordp, opena1, etc.)
- **{CMD|RESP}** - Type (Command oder Response)
- **.json** - Extension

### Beispiele
```
SP00001_opena1→kordp_CMD.json
SP00001_kordp→opena1_RESP.json
SP00042_opena2→tool_file_searcher_CMD.json
```

## 2. Unicode-Pfeil

### Zeichen
- Unicode: U+2192
- UTF-8: E2 86 92
- HTML: &rarr; oder &#8594;
- Display: →

### PFLICHT
- Muss in jedem Dateinamen vorhanden sein
- Keine ASCII-Alternative (->, =>, -->) erlaubt
- Cross-Platform-Kompatibilitaet pruefen
- UTF-8 Encoding zwingend

### Validierung
```python
def validate_safepoint_name(filename):
    if "→" not in filename:
        raise ValueError("Unicode-Pfeil fehlt")
    if "->" in filename or "=>" in filename:
        raise ValueError("Nur Unicode-Pfeil erlaubt")
```

## 3. Storage Structure

### Hierarchie
```
archivp/
├── YYYY/           # Jahr (4-stellig)
│   └── MM/         # Monat (2-stellig, zero-padded)
│       └── DD/     # Tag (2-stellig, zero-padded)
│           ├── SP00001_opena1→kordp_CMD.json
│           └── SP00001_kordp→opena1_RESP.json
└── index.jsonl     # Append-Only Index
```

### Pfad-Beispiel
```
archivp/2025/11/21/SP00001_opena1→kordp_CMD.json
```

### Datumspartitionierung
- Automatische Ordner-Erstellung
- UTC-Timestamps
- Keine manuelle Verwaltung

## 4. Index.jsonl

### Format
- Eine Zeile pro Safepoint
- JSON-Objekt pro Zeile
- Newline-getrennt
- Append-Only

### Entry-Schema
```json
{
  "sp_id": "00001",
  "timestamp": "2025-11-21T12:00:00Z",
  "src": "opena1",
  "dst": "kordp",
  "type": "CMD",
  "path": "2025/11/21/SP00001_opena1→kordp_CMD.json"
}
```

### Felder
- **sp_id** - Laufnummer (string, 5-stellig)
- **timestamp** - ISO-8601 Zulu
- **src** - Quell-Agent
- **dst** - Ziel-Agent
- **type** - "CMD" oder "RESP"
- **path** - Relativer Pfad ab archivp/

## 5. Append-Only Rules

### Erlaubt
- Neue Zeilen anhaengen
- Index lesen
- Suchen/Filtern

### Verboten
- Bestehende Zeilen aendern
- Zeilen loeschen
- Index neu schreiben
- Dateien ueberschreiben

### Enforcement
```python
def append_to_index(entry):
    with open("index.jsonl", "a") as f:  # "a" nicht "w"
        f.write(json.dumps(entry) + "\n")
```

## 6. Safepoint-Content

### Minimal-Schema
```json
{
  "sp_id": "00001",
  "timestamp": "2025-11-21T12:00:00Z",
  "src": "opena1",
  "dst": "kordp",
  "type": "CMD",
  "envelope": { ... },
  "strict": true
}
```

### Felder
- Metadaten (sp_id, timestamp, src, dst, type)
- envelope (vollstaendiger Request/Response)
- strict: true (Pflicht)

## 7. Validierung

### Pre-Write
- Naming-Convention pruefen
- Unicode-Pfeil vorhanden
- Pfad existiert
- Keine Duplikate

### Post-Write
- Datei existiert
- Index aktualisiert
- Permissions korrekt
- Groesse > 0

## 8. Error-Handling

### Invalid Name
```json
{
  "error": "INVALID_SAFEPOINT_NAME",
  "message": "Unicode-Pfeil fehlt",
  "expected": "SP00001_opena1→kordp_CMD.json",
  "received": "SP00001_opena1-kordp_CMD.json"
}
```

### Write Error
```json
{
  "error": "SAFEPOINT_WRITE_FAILED",
  "message": "Konnte Safepoint nicht schreiben",
  "path": "archivp/2025/11/21/SP00001_opena1→kordp_CMD.json",
  "reason": "Permission denied"
}
```
