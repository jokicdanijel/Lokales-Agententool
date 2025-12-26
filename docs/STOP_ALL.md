# STOP_ALL — Stopper für lokale Instanzen 🛑

Diese Datei beschreibt, wie vorhandene lokale Start‑Skripte und Docker‑Compose Stacks sicher gestoppt werden.

Beispiel:

```bash
# Stoppe Docker Compose (falls genutzt)
docker compose -f docker-compose.yml down --remove-orphans

# oder: vorhandene stop scripts verwenden
bin/stop_all_docker_or_scripts.sh --volumes
```

Weitere Hinweise zur sicheren Bereinigung und Datenaufbewahrung sollten projektspezifisch ergänzt werden.
