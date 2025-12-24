# Stack QuickStart

```bash
# venv aktivieren (Beispiel)
source ../1.opena1&2_portier/venv313/bin/activate

# Start/Verify
./bin/ops.sh start
./bin/ops.sh agents:register
./bin/ops.sh status | jq .
./bin/ops.sh write:test
```

Wenn `status` leer ist → `.env` prüfen und `./bin/ops.sh agents:register`.
