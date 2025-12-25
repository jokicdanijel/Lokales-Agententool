# ELION CI — Scanner & Policy

Repository includes a CI workflow that validates policy and scanner artifacts on pull requests.

Overview
- runs `scripts/policy_doc_scan.py` (strict URL ports & HTML contract)
- runs `pytest -q scripts/tests/test_elion_service_scanner.py`
- runs `scripts/elion_compose_merger.py` in a preview step and uploads `artifacts/merged/`

Local preflight (recommended)
- python3 scripts/policy_doc_scan.py --root . --strict-url-ports --check-html-contract
- pytest -q scripts/tests/test_elion_service_scanner.py

Artifacts
- `artifacts/policy_doc_scan_report.json`
- `artifacts/merged/compose.<plan>.yml` and `routes.<plan>.json`

Notes
- CI uses Python 3.12
- Policy scan is fail-fast; it will break PRs that contain direct agent-port links, forbidden ports (8080), or cleartext secrets.

If you'd like, I can also add a CI badge in the README and/or add the scanner to the main preflight script (`scripts/preflight_check.py`).
