# Agent Discovery (Deterministic)

Kurz: Statischer, deterministischer Discovery‑Job, der alle Agent‑Ordner rekursiv scannt, Metadaten extrahiert und ein auditierbares `artifacts/agent_inventory.json` erzeugt.

Scripts
- `scripts/agent_discovery.py` — Hauptskript (read‑only, no exec, stable ordering)
- `scripts/discover_agents.py` — lightweight discovery (human‑friendly) (älter)

Was wird extrahiert
- Per Datei: relative path, size, sha256
- Aus Python: imports (AST), FastAPI/Flask endpoints, port literals (filtered to baseline port range or forbidden ports), openaX references
- Aus HTML/JSON/YAML/TXT: data-* attributes, forms/nav, port literals, openaX references
- Per Agent: file_count, imports, endpoints, ports_detected, agent_references, flags (has_main, has_requirements, has_tests, has_dockerfile)

Validations (fehlerschwer)
- Fehlende/Leere Agent‑Ordner → FAIL
- Unbekannte Agent‑Referenzen (openaX nicht in baseline) → FAIL
- Verwendete verbotene Ports (z. B. 8080/3000) → FAIL
- Wenn Ports in Dateien gefunden werden und sie unterscheiden sich von Baseline → FAIL

Output
- `artifacts/agent_inventory.json` (stable ordering, includes `baseline_hash` and `timestamp`)

Wie ausführen

```bash
# Einfach ausführen
python3 scripts/agent_discovery.py

# Test via pytest
python3 -m pytest -c /dev/null evaluation/tests/test_agent_discovery.py -q
```

Designhinweise
- Determinismus: Dateien werden lexisch sortiert, Agenten sortiert nach ID (opena1..opena21)
- Port‑Erkennung: Nur Zahlen innerhalb `port_policy.allowed_range` oder ausdrücklich in `port_policy.forbidden_ports` werden als Portkandidaten betrachtet (verringert false positives)
- Keine Ausführung von Code oder Netzwerkzugriff — Analyse ist rein statisch und sicher

Nächste Schritte
- (Optional) Ausgabe filtern, z. B. .mypy_cache ignorieren, falls Inventory zu groß
- CI‑Integration: Lauf vor Build und fail on non-empty errors array
