# Dashboard Debug & Local Smoke Testing

Kurz: Schnelle Anleitung, um das Dashboard lokal zu starten, Health zu prüfen und schnelle Logs zu sammeln (entspricht dem CI‑Smoke‑Test).

Voraussetzungen
- Bash, curl, jq
- Startskript vorhanden: `19.opena20_dashboard_agent/bin/start_opena20.sh`
- Port: `12349`

Schnelle Schritte (lokal)

1) Starten (im Hintergrund)

```bash
chmod +x 19.opena20_dashboard_agent/bin/start_opena20.sh
nohup 19.opena20_dashboard_agent/bin/start_opena20.sh > /tmp/opena20.log 2>&1 &
PID=$!
echo "Dashboard started (PID=$PID)"
```

2) Health prüfen (wartet bis zu ~60s)

```bash
for i in {1..30}; do
  if curl -fsS http://127.0.0.1:12349/health >/dev/null 2>&1; then
    echo "✅ Dashboard healthy"
    break
  fi
  echo "Waiting... ($i/30)"
  sleep 2
done

if ! curl -fsS http://127.0.0.1:12349/health >/dev/null 2>&1; then
  echo "❌ Dashboard not healthy. See logs:"
  tail -n 200 /tmp/opena20.log
fi
```

3) Logs & common pitfalls
- Logs: `tail -n 500 /tmp/opena20.log` oder unter `19.opena20_dashboard_agent/webpanel/logs/*` falls vorhanden.
- Häufige Fehler:
  - Missing dependencies → Start skript schlägt fehl (Prüfe virtualenv, Python version, pip deps)
  - Port already in use → `ss -ltnp | grep 12349`
  - Missing templates/static → `ls 19.opena20_dashboard_agent/templates 19.opena20_dashboard_agent/static`

4) Stoppen

```bash
kill "$PID" || true
```

CI-Relevanz
- CI führt denselben Ablauf als Smoke Test aus. Wenn der Smoke Test fehlschlägt, liefert CI einen Tail der letzten 200 Zeilen aus `/tmp/opena20.log` im Runner-Log.

Tipps für Entwickler
- Nutze `./19.opena20_dashboard_agent/webpanel/build-and-run.sh` (falls vorhanden) für reproduzierbare Dev-Start.
- Wenn du den Service in Docker testen willst, bau das Image und starte lokal mit `docker compose -f 19.opena20_dashboard_agent/webpanel/docker-compose.yml up --build`.
