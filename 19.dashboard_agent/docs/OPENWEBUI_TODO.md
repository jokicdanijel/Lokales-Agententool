# OpenWebUI Integration – Offene Aufgaben

## Feature-Implementierung

- [ ] UI-Integration abschließen (ui_index.html mit OpenWebUI Chat-Button)
- [ ] Adapter in Docker nutzen (docker-compose für standalone Adapter)
- [ ] Systemd-Service für opena3 anlegen
- [ ] Datenbankpersistierung für Agent-Registry
- [ ] WebSocket-Unterstützung für Live-Chat

## Testing & QA

- [ ] End-to-End Tests (Dashboard → OpenWebUI)
- [ ] Load-Tests (parallel Requests an opena3)
- [ ] Fehlerfall-Tests (OpenWebUI offline, Timeout, etc.)
- [ ] Security-Audit für Token-Handling

## Dokumentation

- [ ] Deployment-Guide (Docker, Kubernetes)
- [ ] API-Referenz erweitern (Request/Response-Schemas)
- [ ] Tuning-Guide (Performance, Memory)
- [ ] Troubleshooting erweitern (mehr Fehlerszenarien)

## Infrastruktur

- [ ] Logging centralisieren (ELK Stack oder ähnlich)
- [ ] Monitoring einrichten (Prometheus, Grafana)
- [ ] Backup-Strategie für archivp
- [ ] CI/CD Pipeline (GitHub Actions)

## Optimierungen

- [ ] Caching für häufige Prompts
- [ ] Batch-Processing für mehrere Prompts
- [ ] Rate-Limiting pro Client/Token
- [ ] Async-Verbindungspooling

## Known Issues

- [ ] SSE-Events manchmal verzögert (Heartbeat-Tuning nötig)
- [ ] Token-Refresh-Mechanismus fehlt (aktuell fix)
- [ ] Keine Rollback-Funktion für Migrations

## Optionale Features

- [ ] GraphQL-API als Alternative zu REST
- [ ] WebUI für Agent-Verwaltung
- [ ] Prompt-Templates speichern
- [ ] Analytics für Agenten-Nutzung
