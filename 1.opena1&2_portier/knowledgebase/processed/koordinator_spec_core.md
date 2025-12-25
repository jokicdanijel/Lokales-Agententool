# Koordinator (opena1) - Processed Core Version

## 1. Rolle

- Eingang aller User-Nachrichten (Schema 7.1)
- strikte Validierung
- deterministische Toolwahl
- DB-Updates
- CMD-Envelope-Erstellung
- Weiterleitung ueber opena2

## 2. Port-Policy

- Port: 12344
- Zulaessig: 12344-12399
- Verboten: 8080
- Einhaltung zwingend
- Enforcement via Middleware

## 3. Eingabeschema (7.1)

- request_id (UUID v4)
- timestamp (ISO-8601 Zulu)
- command (string)
- payload (object)
- routing.resolved_path (string|null)
- project{id,name}
- strict:true
- additionalProperties: false

## 4. Ausgabeschema (7.2)

- request_id (UUID v4)
- timestamp (ISO-8601 Zulu)
- source: "opena1"
- decision:
  - selected_tool (string)
  - reason (string)
  - resolved_path (string)
- db_updates[] (array)
- archivator_forward{} (object)
- next: "DISPATCHED_VIA_ARCHIVATOR"
- strict:true
- additionalProperties: false

## 5. Tool-Registry

- tool_text_analyzer
- tool_file_searcher
- tool_scheduler
- tool_monitor
- Auswahl per command-Mapping oder target_preference
- Zentrale Registry: config/registry.json

## 6. DB-Modelle

- projects (id, name, status)
- files (id, path, project_id)
- tools (id, name, port, status)
- events (id, request_id, timestamp, type)

## 7. Verantwortungen

- Request-Validierung
- Tool-Selektion
- Envelope-Bau
- DB-Persistierung
- Response-Generierung
- Archivator-Integration

## 8. Ablauf

1. POST Request empfangen
2. Schema 7.1 validieren
3. Tool auswaehlen
4. CMD-Envelope bauen
5. DB aktualisieren
6. An opena2 forwarden
7. Auf RESP warten
8. Schema 7.2 generieren
9. An OpenAI zurueck
