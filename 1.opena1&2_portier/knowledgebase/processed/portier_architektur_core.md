# Portier-System - Architektur (Processed Core Version)

## 1. Systemumgebung
- Ubuntu 25.04
- Python 3.13.x
- Virtuelle Umgebung: venv313
- Ports erlaubt: 12344-12399
- Port 8080 strikt verboten (UI-only fuer OpenWebUI)

## 2. Architekturprinzip
- Zwei Hauptrollen:
  - **opena1** (Koordinator, Port 12344)
  - **opena2** (Archivator, Port 12345)

- **Hinweg:** OpenAI → opena1 → opena2 → kordp → Tool
- **Rueckweg:** Tool → opena2 → opena1 → OpenAI

## 3. Rollenuebersicht

### opena1 - Koordinator
- nimmt 7.1-Schema entgegen
- validiert strict:true
- waehlt deterministisches Tool
- erstellt CMD-Envelope
- leitet an opena2 weiter

### opena2 - Archivator
- erzeugt CMD/RESP-Safepoints
- schreibt Archivdateien
- pflegt index.jsonl
- leitet an kordp weiter
- schleift RESP zurueck

### kordp - Koordinatport (Port 12346)
- dispatcht Commands an Tools
- sammelt Responses
- leitet zurueck an opena2

### archivp - Archivport (Filesystem)
- speichert Safepoints
- Unicode-Pfeil Naming
- Datums-Partitionierung

## 4. Endpunkte
- `POST /log/opena1` - Pre-Safepoint CMD
- `POST /finalize/opena2` - Post-Safepoint RESP
- `POST /dispatch/kordp` - Tool-Dispatch
- `POST /store/archivp` - Snapshot

## 5. Safepoint-Logik
- Dateiname: `SP<nummer>_src→dst_{CMD|RESP}.json`
- Unicode-Pfeil: → (U+2192) PFLICHT
- Ablage: `/archivp/YYYY/MM/DD/`
- Index: `/archivp/index.jsonl` (append-only)
- Regeln:
  - Nur anhaengen
  - Niemals ueberschreiben
  - Niemals loeschen
  - Niemals modifizieren

## 6. Prozessfluss

### Hinweg (Command-Flow)
1. OpenAI → opena1
2. Schema-Check (7.1)
3. Tool-Wahl
4. opena1 → opena2 CMD
5. opena2 → Safepoint CMD
6. opena2 → kordp
7. kordp → Tool

### Rueckweg (Response-Flow)
1. Tool → kordp
2. kordp → opena2 RESP
3. opena2 → Safepoint RESP
4. opena2 → opena1
5. opena1 → OpenAI (7.2)

## 7. Tools
- tool_text_analyzer
- tool_file_searcher
- tool_scheduler
- tool_monitor

## 8. Entwicklerregeln
- Immer produktionsreife Dateien
- Keine Platzhalter
- Keine TODOs
- Safepoint-Pflicht
- Strict:true (additionalProperties: false)
- Keine Abweichung von Port-Policy
- Option-2-Flow unveraenderlich
