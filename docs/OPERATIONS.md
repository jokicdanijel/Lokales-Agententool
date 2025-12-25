# ELION Hyper-Dashboard – Operations

## Ports

- Dashboard: 12349
- opena1: 12344
- opena2: 12345 (Archivator)
- kordp: 12346
- OpenWebUI: 8080 (optional)

## Schnellstart

```bash
./bin/ops.sh start
./bin/ops.sh agents:register
./bin/ops.sh status | jq .
```

## Write-Test

```bash
./bin/ops.sh write:test
```

## Logs

```bash
./bin/ops.sh logs
```

## Häufige Fehler

- 403/401 → fehlender/inkorrekter Token: `.env` prüfen.
- 404 bei `/store/archivp` → Archivator läuft nicht oder falscher Pfad.
- Port in use → `./bin/ops.sh stop` und erneut starten.

## Tracing (OpenTelemetry) 🔧

Für lokale Tests kann ein OTLP-kompatibler Collector gestartet werden:

```bash
# Start local collector
./bin/start_tracing_collector.sh
```

Aktiviere Tracing in den Services durch Setzen der OTEL-Variablen in der `.env` (Beispiel):

```env
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
OTEL_SERVICE_NAME=telegram_multi
```

Verifiziere mit dem Hilfs-Skript:

```bash
python3 tracing/check_tracing.py
```

Wenn die Pakete fehlen, läuft der Service weiterhin, Tracing wird in diesem Fall übersprungen.
