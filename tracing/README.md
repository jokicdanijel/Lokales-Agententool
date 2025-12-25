# Tracing (OpenTelemetry)

This project contains optional OpenTelemetry tracing support. It is implemented
safely so services do not fail if OpenTelemetry Python packages are not installed.

Quick guide

1. Install OpenTelemetry in your environment or inside each service image:

   pip install -r telegram_multi/requirements.txt

2. Enable tracing via environment variables (example):

   OTEL_ENABLED=true
   OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
   OTEL_SERVICE_NAME=telegram_multi

3. Restart the service. The `pkg.observability.init_tracing(...)` helper will
   initialize tracing if enabled and required packages are available.

Local verification

Run a simple import check (no network call required):

```bash
python3 -c "from pkg.observability import init_tracing; print('OK', callable(init_tracing))"
```

Example OTEL collector (docker-compose snippet)

```yaml
services:
  otel-collector:
    image: grafana/otel-lgtm:latest
    environment:
      - ENABLE_OTEL=true
      - OTEL_EXPORTER_OTLP_INSECURE=true
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
    ports:
      - 4318:4318
```

Notes

- Tracing is optional and non-blocking: if packages are missing it logs a warning and continues.
- Use a compatible OTLP collector (Grafana Agent/Tempo/Jaeger/OTel Collector) in production.
