# Evaluation Framework (ELION Workspace)

## Ziel
Ein leichtgewichtiger, wiederholbarer Evaluations-Framework für Modelle und Endpunkte im Repository.

## Inhalt
- `evaluation/runner.py` – Haupt-Runner, JSONL-Dataset-Eingabe, JSON-Report-Ausgabe
- `evaluation/metrics.py` – Einfache, leicht prüfbare Metriken (exact_match, contains_frac, length_ratio)
- `evaluation/datasets` – Beispiel-Datasets im JSONL-Format
- `evaluation/results` – Bewertungsergebnisse (Reports als JSON)
- `requirements-eval.txt` – Dependencies für Evaluation (requests, pytest)

## Schnellstart
1. Installiere Dev-Abhängigkeiten:

```bash
python3 -m pip install -r requirements-eval.txt
```

2. Führe Beispiel-Evaluation aus:

```bash
python3 -m evaluation.runner evaluation/datasets/sample.jsonl --out evaluation/results/report.json
cat evaluation/results/report.json | jq .summary
```

3. Beispiel: OpenWebUI Arena Evaluation

```bash
# Optional: set endpoint (falls Dashboard/OpenWebUI nicht auf Standard läuft)
export EVALUATION_ENDPOINT=http://127.0.0.1:12349/api/openwebui/chat
python3 evaluation/examples/openwebui_example.py
cat evaluation/results/openwebui_arena_report.json | jq .summary
```


## CI-Integration
Es existiert eine GitHub Action (`.github/workflows/evaluation.yml`) die die Evaluation plant und ein Report-Artefakt hochlädt.

## Integration Tests
Integrationstests gegen laufende Endpunkte sind optional und standardmäßig deaktiviert. Setze die Umgebungsvariable `RUN_EVAL_INTEGRATION=1` und `EVALUATION_ENDPOINT` (falls nötig), z. B.:

```bash
# Setze OpenWebUI/Dashboard Endpoint wenn nötig
export EVALUATION_ENDPOINT=http://127.0.0.1:12349/api/openwebui/chat
export RUN_EVAL_INTEGRATION=1
python -m pytest -q tests/test_evaluation_integration.py -q
```

## Erweiterungen
- Unterstützung für BLEU/ROUGE
- Gruppierung nach tasks und dataset-tags
- Prometheus / Grafana-Integration für Metriken
