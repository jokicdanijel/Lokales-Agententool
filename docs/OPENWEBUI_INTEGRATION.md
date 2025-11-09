# OpenWebUI Integration (opena3)

1. Starte OpenWebUI lokal auf Port 8080.
2. Registriere den Agenten:
   ```bash
   ./bin/ops.sh agents:register
   ```
3. Prüfe Dashboard-Status:
   ```bash
   ./bin/ops.sh status | jq .
   ```

Erwartung: `opena3` mit Endpoint `http://127.0.0.1:8080`.
