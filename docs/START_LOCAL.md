# START_LOCAL — Lokales Start‑Hilfsprogramm 🔧

Kurz: `bin/start_opena_local.sh` startet eine einzelne App lokal in einer `venv312`‑Umgebung und lädt `./.env` (falls vorhanden).

Wichtige Sicherheitsregeln:
- Das Skript verweigert standardmäßig Ausführung in CI (Exit 2).
- Du musst explizit `ALLOW_UNLIMITED_START=1` setzen, um das Skript auszuführen (Opt‑in; Exit 3 bei Fehlen).

Usage:

```bash
# aus dem Agenten‑Ordner
ALLOW_UNLIMITED_START=1 bin/start_opena_local.sh .    # startet App aus dem aktuellen Verzeichnis

# optional: PORT, UVICORN_APP override
ALLOW_UNLIMITED_START=1 PORT=8080 UVICORN_APP="myapp.asgi:app" bin/start_opena_local.sh .
```

Logs werden nach `artifacts/logs/start_local/<timestamp>/start.log` geschrieben.

Tipps:
- Nutze dieses Skript lokal für Entwickler‑Runs und Debugging.
- Für automatisierte CI/Runner nutze definierte Smokes / Integrationstests statt dieses Skripts.
