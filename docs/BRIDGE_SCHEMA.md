# Bridge Schema (bridge_schema.json)

Kurz: `configs/bridge_schema.json` ist ein *generiertes* Artefakt (OpenAPI/JSON Schema), das normalerweise nicht in jedem Commit vorhanden ist.

Wann generieren

- Lokale Generierung (schnell):

```bash
# Starte den Service, dann:
curl http://127.0.0.1:12351/openapi.json | jq . > configs/bridge_schema.json
```

- Verwendung: Das erzeugte `configs/bridge_schema.json` dient als OpenAPI/Bridge‑Schema zur Dokumentation und als Grundlage für Validierungen.

Policy / CI‑Hinweis

- Wenn `bridge_schema.json` Teil eines verbindlichen Contracts ist, sollte die Datei ins Repo committed werden (Option: `git add configs/bridge_schema.json`).
- Wenn die Datei jedoch aus dem Build/Generator stammt und **nicht** versioniert werden soll, dann ist es korrekt, sie **nicht** im Repo zu haben. In diesem Fall haben wir eine gezielte Ausnahme im Pre‑commit Hook (`check-json`) konfiguriert, damit CI nicht fehlschlägt, wenn die Datei fehlt.

Empfehlung

- Für Contract‑Stability: committe eine minimal gültige `configs/bridge_schema.json` und dokumentiere das Upgrade‑Verfahren.
- Für generator‑only: behalte die Hook‑Exclude‑Regel und dokumentiere das Erzeugungsverfahren (siehe oben).
