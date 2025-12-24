# Evaluation Framework

Kurz: Minimaler, reproducible evaluation runner für Agenten.

Contents
- `evaluation/dataset/sample_conversations.jsonl` — kleine Testdaten
- `evaluation/run_eval.py` — Runner, schreibt `evaluation/artifacts/eval_results_*.json` und `latest_eval.json`
- `evaluation/metrics.py` — scoring helpers (exact_match, contains_expected, score_response)
- `evaluation/tests/test_eval_runner.py` — pytest test for runner

How to run (local):

```bash
# Dry-run (agent core returns simulated responses)
python3 evaluation/run_eval.py --dataset evaluation/dataset/sample_conversations.jsonl

# Run unit tests
python3 -m pytest -q evaluation/tests/test_eval_runner.py
```

Metrics used (simple baseline):
- exact match (1.0)
- contains expected (0.75)
- else (0.0)

Next steps (suggested):
- Add human judged metrics (factuality) with LLM-as-judge
- Add more diverse dataset with conversation contexts
- Add CI job to run evaluation and fail if avg_score < threshold
