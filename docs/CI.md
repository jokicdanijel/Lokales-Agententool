# CI — Policy Validator & Troubleshooting 🛠️

Zweck

Dieses Dokument beschreibt die Policy‑Validatoren und typische CI‑Probleme.

Wichtige Skripte

- `1.portier_openai/skripte/validate_portier.sh` — Policy validator, wird in CI ausgeführt. Minimaler Inhalt (Platzhalter) besteht, sollte aber mittelfristig mit echten Prüfungen ersetzt werden.
- `scripts/elion_policy_doc_scan.py` — durchsucht das Repo nach Port‑/Secret/HTML‑Verstößen (ELION toolchain)

Typische CI‑Fehler

- `❌ Policy validator missing` → Fehlende `validate_portier.sh` prüfen; Lösung: Datei hinzufügen oder Workflow anpassen.
- PR‑Post‑Comments mit 403 → Workflows wurden so angepasst, dass Kommentare nur bei gleichen‑Repo‑PRs ausgeführt werden oder `continue-on-error: true` vorhanden ist.

Empfohlene Schritte zur Fehlerbehebung

1. Logs in GitHub Actions öffnen (Run → View logs)
2. Prüfe, ob `artifacts/agent_inventory.json` valide JSON ist
3. Prüfe die Presence von `1.portier_openai/skripte/validate_portier.sh`
4. Falls PR‑Kommentar 403s auftreten, prüfe `github.event.pull_request.head.repo.full_name == github.repository` Guard

Kontakt

Erstelle einen Issue mit relevanten Run‑Logs und Steps to reproduce.
