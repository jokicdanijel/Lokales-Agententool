# openwebui (opena3 → openweb)

- **program_target**: `openweb`
- **endpoint_base**: `http://localhost:12344-12349/openweb`
- **local_port**: `12346`
- **service_id**: `opena3`

## Start

1. Core starten (`opena1` + `opena2`):

   ```bash
   bash scripts/start_core.sh
   ```

2. Service starten:

   ```bash
   ./.venv/bin/python3 -m uvicorn src.services.openwebui.service:app --host 127.0.0.1 --port 12346
   ```

3. Registrieren:
   ```bash
   bash scripts/register_openwebui.sh
   ```

## Testen

```bash
# Health check
curl -s http://127.0.0.1:12346/health | jq .

# Ping
curl -s http://127.0.0.1:12346/openwebui/ping | jq .

# Call (prompt)
curl -s -X POST http://127.0.0.1:12346/openwebui/call \
  -H 'content-type: application/json' \
  -d '{"action":"prompt","data":{"text":"hello"}}' | jq .

# Verify route registration
curl -s http://127.0.0.1:12344/health | jq '.routes_count'
```

## Safepoints

Jede Anfrage erzeugt einen Safepoint bei OpenA2:

- `ROUTE` — beim Startup (Route-Registrierung)
- `CALL` — bei jedem `/openwebui/call` Request

Finde sie unter: `1.opena1&2_portier/archivp_store/YYYY/MM/DD/`

## Akzeptanzkriterien

- ✅ `/health` → 200 + `component=openwebui`, `port=12346`
- ✅ POST `/route/update` bei OpenA1 akzeptiert; OpenA2 schreibt `ROUTE`-Safepoint
- ✅ POST `/openwebui/call` → 200, echo ohne Secret-Leak; OpenA2 schreibt `CALL`-Safepoint
- ✅ Tests grün: `pytest -q tests/test_openwebui_service.py`
- ✅ Keine Secret-Leaks (Redaction aktiv)
