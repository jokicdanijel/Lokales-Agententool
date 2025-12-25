# ⚠️ VERALTET / DEPRECATED

**Diese Datei ist veraltet und wird nicht mehr aktualisiert.**

**Bitte verwende stattdessen:** [`README.md`](./README.md)

---

# OpenA1 (kordp) & OpenA2 (archivp) – API Nutzung

## Dienste & Ports

- OpenA1 (Coordinator, **kordp**) → `http://127.0.0.1:12344`
- OpenA2 (Archivator, **archivp**) → `http://127.0.0.1:12345`

## Health

```bash
curl -s http://127.0.0.1:12344/health | jq
curl -s http://127.0.0.1:12345/health | jq
```

## Routen setzen (Copilot/Tools → OpenA1)

```bash
curl -s -X POST http://127.0.0.1:12344/route/update \
  -H 'content-type: application/json' \
  -d '{
        "agent":"openwebui",
        "agent_id":"opena3",
        "port":12346,
        "program":"openweb",
        "archivator_port":12345,
        "mapping_ts":"2025-11-10T00:00:00Z",
        "mapping":{"intent":"ensure_transfer_to_archivator"}
      }' | jq
```

## Dispatch senden (Client/System → OpenA1)

```bash
curl -s -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H 'content-type: application/json' \
  -d '{"agent":"openwebui","action":"refresh_index","data":{"scope":"daily"}}' | jq
```

OpenA1 bestätigt und schreibt über OpenA2 einen Safepoint (`kind=DISPATCH`).

## Logging (alle → OpenA1)

```bash
curl -s -X POST http://127.0.0.1:12344/log/opena1 \
  -H 'content-type: application/json' \
  -d '{"source":"test","event":"ping","payload":{"note":"hello"},"strict":true}' | jq
```

## Safepoints speichern (OpenA1/Clients → OpenA2)

```bash
curl -s -X POST http://127.0.0.1:12345/store/archivp \
  -H 'content-type: application/json' \
  -d '{"src":"client","dst":"archivp","kind":"NOTE","body":{"k":"v"}}' | jq
```

## Finalisieren (Auditabschluss → OpenA2)

```bash
curl -s -X POST http://127.0.0.1:12345/finalize/opena2 \
  -H 'content-type: application/json' \
  -d '{"ticket":"T-2025-001","status":"closed","notes":"ok"}' | jq
```

## Speicherorte

- Safepoints: `1.opena1&2_portier/archivp_store/YYYY/MM/DD/SP<ts>_<src>→<dst>_<kind>.json`
- Index: `1.opena1&2_portier/archivp_store/index.jsonl`

## Start (je Dienst)

```bash
# OpenA1
python /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/opena1_app.py
# OpenA2
python /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/opena2_app.py
```
