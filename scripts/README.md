# scripts/

Kurzbeschreibung: Kleines Hilfsskript zum Builden/Starten aller Docker Compose Projekte unter `dist/`.

script: `scripts/compose_all.sh`

Usage:

- Basis-Aufruf (iteriert `dist/*` und baut & startet alle Compose-Projekte):

  ```bash
  ./scripts/compose_all.sh
  ```

- Optionen:
  - `--dist DIR` — Verzeichnis mit den Distribution-Subprojekten (Standard: `dist`)
  - `--service NAME` — Beschränke `docker compose up` auf einen bestimmten Service
  - `--no-build` — `up -d` ohne `--build`
  - `--help` — Hilfe anzeigen

Beispiele:

- Build & Start aller Projekte unter `dist/`:
  ```bash
  ./scripts/compose_all.sh
  ```

- Nur Service `opena8` in `dist/opena8` neu bauen und starten:
  ```bash
  ./scripts/compose_all.sh --dist dist/opena8 --service opena8
  ```

- Start ohne Build:
  ```bash
  ./scripts/compose_all.sh --no-build
  ```

Hinweise:
- Dieses Skript erwartet, dass `docker` und `docker compose` im PATH verfügbar sind.
- Es prüft auf vorhandene `docker-compose.yml` / `docker-compose.yaml` Dateien im Subprojekt.

Lizenz: Selbes Projekt-Lizenzmodell wie Repository.
