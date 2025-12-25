# Developer Guide — Schnellreferenz 🧭

Zweck

Kurzreferenz für Entwickler: lokale Entwicklung, Tests und PR‑Checkliste.

Lokales Starten

- Convenience: `bin/start_all_components.sh`
  - `LOG_DIR` und `SKIP_DOCKER` sind die wichtigsten Optionen.

Tests

- Unit/Integration:

  ```bash
  venv/bin/pytest -q
  # oder für spezifische Tests
  pytest -q 1.opena1&2_portier/tests/test_portier_stack.py -k port_policy -s
  ```

- Wichtiger Testfall: `port_policy` prüft, ob `opena1` /health Policy‑Endpoints enthält.

CI/PR Checklist

- Linter / pre-commit laufen lokal (pre-commit hooks vorhanden)
- `scripts/elion_policy_doc_scan.py` ausführen, wenn du neue Services/Ports hinzufügst
- Falls du Änderungen an Workflows machst: prüfe, ob PR‑Comment Steps bei Fork‑PRs ausgelassen werden (Guard vorhanden)

Hilfe

- Für CI‑Fehler: `docs/CI.md`
- Für ELION Tools: `docs/ELION.md`

Danke — trage bitte Ergänzungen per PR ein.
