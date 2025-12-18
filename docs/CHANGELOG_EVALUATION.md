# Changelog - Evaluation Framework

## [Unreleased] - 2025-12-16

### Added
- `evaluation/` package: `runner.py`, `metrics.py`, `reporting.py` (lightweight evaluation harness)
- Sample datasets: `evaluation/datasets/sample.jsonl`, `openwebui_arena.jsonl`
- CI workflow: `.github/workflows/evaluation.yml` (daily + on push to main)
- Documentation: `docs/EVALUATION.md`
- Unit tests and integration test (opt-in): `tests/test_evaluation_*.py`

### Notes
- Integration tests are opt-in (set `RUN_EVAL_INTEGRATION=1` to enable against live endpoints).
- The runner is intentionally minimal and extensible (BLEU/ROUGE integration planned).
