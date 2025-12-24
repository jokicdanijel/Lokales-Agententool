# Tracing (OpenTelemetry) — Quick notes

This repository contains a small tracing bootstrap at `scripts/tracing.py`.

## How to use locally

1. Install tracing dependencies (recommended into your virtualenv):

   ```bash
   python -m pip install -r scripts/requirements-tracing.txt
   ```

2. Start a trace collector / OTLP endpoint. AI Toolkit defaults (for local development):
   - HTTP OTLP: `http://localhost:4318`
   - gRPC OTLP: `http://localhost:4317`

3. Optionally open the AI Toolkit trace viewer in VS Code (recommended):
   - Run the command: `ai-mlstudio.tracing.open` in VS Code

4. The scripts call `init_tracing(service_name)` on startup (where implemented). You can set
   `OTEL_EXPORTER_OTLP_ENDPOINT` if you run a collector on a non-default port.

## Notes

- The tracing bootstrap is resilient: if the OpenTelemetry packages are not available it becomes a no-op and will not break scripts.
- For CI or production, configure a real OTLP collector and secure it appropriately.
