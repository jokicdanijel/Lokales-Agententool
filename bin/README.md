# bin/ — Developer Helper Scripts 🔧

Enthält kleine Shell‑Skripte für die lokale Entwicklung und tägliche Tasks.

Enthaltene Skripte

- `start_all_components.sh` — Startet lokale Uvicorn‑Services (opena1, opena2, opena20, opena11), legt Logs und PID‑Dateien an und führt Health‑Checks aus.

Usage

- Einfach ausführen (im Repo root):

  ```bash
  bin/start_all_components.sh
  ```

- Optionen:
  - `LOG_DIR` — Verzeichnis für Logs/PIDs (Standard `logs/`)
  - `SKIP_DOCKER=1` — Docker Compose überspringen

Beispiel:

```bash
LOG_DIR=/tmp/project-logs SKIP_DOCKER=1 bin/start_all_components.sh
```

Hinweis

- Das Skript ist als Entwicklerhilfsmittel gedacht — für CI/Production nutze die entsprechenden Compose/Deployment‑Konfigurationen.
