# Knowledge Base - Elion Hyper-Dashboard

## Uebersicht

Diese Knowledge Base enthaelt das vollstaendige Wissen des Portier / ELION Hyper-Dashboard 2.0 Systems.

## Struktur

```
knowledge/
├── manifest.json       # System-Metadaten
├── index.json         # Zentrale Wissensstruktur
├── map.md            # Thematische Navigation
├── README.md         # Diese Datei
├── raw/              # Unverarbeitete Quelldateien
├── processed/        # Segmentierte, normalisierte Inhalte
└── vectors/          # Embedding-Datenbanken
```

## Verwendung

### 1. Rohdaten hinzufuegen

```bash
cp <quelle>.md knowledge/raw/
```

### 2. Index aktualisieren

```bash
python scripts/update_knowledge_index.py
```

### 3. Embeddings generieren

```bash
python scripts/generate_embeddings.py
```

### 4. Suche durchfuehren

```bash
python scripts/search_knowledge.py "Option-2-Flow"
```

## Validierung

- Alle Dateien UTF-8
- Strict JSON (additionalProperties: false)
- Port-Policy eingehalten
- Keine Platzhalter
- Keine TODOs

## Integration

Die Knowledge Base ist vollstaendig in das Dashboard (opena20) integriert:

- Endpunkt: GET /api/knowledge/search
- Bearer-Token erforderlich
- SSE-Events bei Updates

## Status

- Struktur: Produktionsreif
- Index: Initialisiert
- Embeddings: Bereit fuer Generierung
- Dashboard-Integration: Vorbereitet
