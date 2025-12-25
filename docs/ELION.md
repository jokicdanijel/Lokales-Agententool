# ELION Toolchain — Scanner & Merger 🔎

Kurz: ELION besteht aus 3 Scanner‑Skripten und einem Merger, die Infrastruktur‑/Compose‑Fragmente erzeugen.

Wichtige Tools

- `scripts/elion_service_scanner.py` — scannt Services und erzeugt Metadaten (ports, exposures, hints)
- `scripts/elion_policy_doc_scan.py` — prüft Policy‑Regeln (forbidden ports, secrets, HTML issues)
- `scripts/elion_compose_merger.py` — erzeugt plan‑spezifische `compose.*.yml` Fragmente

Policy Rules (Beispiele)

- Zulässige Host‑Ports: 12344–12399
- Verboten: 8080
- Keine direkten Agent‑Port URLs in Compose/Env
- Secret‑Detektion: einfache heuristische Suche nach `key`, `secret`, `token` in config‑Dateien

Usage

Die Tools sind für CI und lokale Validierung gedacht. Beispiele:

```bash
python scripts/elion_policy_doc_scan.py
python scripts/elion_compose_merger.py --plan basic
```

Ergänzungen

Wenn du neue Services hinzufügst, erweitere die Scanner‑Regeln / hints entsprechend.
