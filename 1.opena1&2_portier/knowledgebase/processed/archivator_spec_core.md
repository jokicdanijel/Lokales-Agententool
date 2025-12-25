# Archivator (opena2) - Processed Core Version

## 1. Rolle

- Empfaengt CMD-Envelopes von opena1
- Erzeugt Safepoint CMD
- Leitet an kordp weiter
- Empfaengt RESP von kordp
- Erzeugt Safepoint RESP
- Leitet RESP an opena1 zurueck

## 2. Port

- Port: 12345
- FastAPI Service
- Async Operations
- Health-Check: GET /health

## 3. CMD/RESP-Flow

### CMD-Flow

1. Empfang von opena1
2. Validierung
3. Safepoint-Generierung
4. Dateisystem-Schreiben
5. Index-Update
6. Forward an kordp

### RESP-Flow

1. Empfang von kordp
2. Validierung
3. Safepoint-Generierung
4. Dateisystem-Schreiben
5. Index-Update
6. Forward an opena1

## 4. Safepoints

### Naming Convention

```
SP<laufnummer>_src→dst_{CMD|RESP}.json
```

### Beispiel

```
SP00001_opena1→kordp_CMD.json
SP00001_kordp→opena1_RESP.json
```

### Unicode-Pfeil

- Zeichen: → (U+2192)
- PFLICHT in jedem Safepoint-Namen
- Keine ASCII-Alternative erlaubt

## 5. Speicherstruktur

### Hierarchie

```
archivp/
├── YYYY/
│   └── MM/
│       └── DD/
│           ├── SP00001_opena1→kordp_CMD.json
│           └── SP00001_kordp→opena1_RESP.json
└── index.jsonl
```

### Index-Format (JSONL)

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

## 6. Index.jsonl

### Regeln

- Append-Only
- Niemals ueberschreiben
- Niemals loeschen
- Eine Zeile pro Safepoint
- JSON-Format pro Zeile
- Newline-getrennt

### Felder

- sp_id (string)
- timestamp (ISO-8601)
- src (string)
- dst (string)
- type ("CMD"|"RESP")
- path (string)

## 7. Routing

### Hinweg

opena1 → opena2 → kordp → Tool

### Rueckweg

Tool → kordp → opena2 → opena1

### Keine Abkuerzungen

- Kein opena1 → kordp direkt
- Kein Tool → opena1 direkt
- Immer ueber opena2

## 8. Error-Handling

- Validation-Errors → 400
- File-Write-Errors → 500
- Forward-Errors → 502
- Strukturierte Error-Responses
- Logging auf ERROR level
