# ELION Hyper-Dashboard – Operations

## Ports
- Dashboard: 12349
- opena1:    12344
- opena2:    12345 (Archivator)
- kordp:     12346
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
* 403/401 → fehlender/inkorrekter Token: `.env` prüfen.
* 404 bei `/store/archivp` → Archivator läuft nicht oder falscher Pfad.
* Port in use → `./bin/ops.sh stop` und erneut starten.
