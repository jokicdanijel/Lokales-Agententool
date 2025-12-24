# Model Recommendation

Kurz: Empfohlen für dieses Repo

- Produktion: **Microsoft Foundry (empfohlen)** — stabile Deploys, unterstützte Governance und Observability.
- Entwicklung / Quickstart: **GitHub Models** (kostenfrei für erste Tests, einfacher Wechsel).

Empfehlung (konkret)

- Primär: `openai/gpt-4.1-mini`
  - Warum: guter Kompromiss aus Qualität, Latenz und Kosten; 1M Kontext für längere Agent‑Kontexte.
- Fallback (low‑latency / cost): `openai/gpt-4.1-nano`
  - Warum: stark reduzierte Latenz und Kosten, geeignet für high‑QPS agent calls.

Trade‑offs

- Foundry (Prod): + Governance, +observability, -Initial Setup & Deployment
- GitHub (Dev): +Schnell zu starten, -keine enterprise features

Env‑Konfiguration (Beispiel)

```bash
# Provider: github | foundry
export AGENT_PROVIDER=github
export AGENT_MODEL=openai/gpt-4.1-mini
# Use dry-run for CI / local tests
export AGENT_DRY_RUN=1
# API keys must be in env, never in repo
export GITHUB_MODEL_KEY="ghp_..."
```

Minimaler Integrations‑Snip (safe, dry‑run aware)

```python
# agent/integration.py (Beispiel)
import os
import requests

MODEL = os.environ.get("AGENT_MODEL", "openai/gpt-4.1-mini")
PROVIDER = os.environ.get("AGENT_PROVIDER", "github")
DRY = os.environ.get("AGENT_DRY_RUN", "1") in ("1", "true", "yes")

def call_model(prompt: str) -> str:
    if DRY:
        return f"[DRY_RUN] Simulated response for {len(prompt)} chars"

    # Example (GitHub models inference): use the models.github.ai endpoint
    api_key = os.environ.get("GITHUB_MODEL_KEY")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": MODEL, "input": prompt}
    resp = requests.post("https://models.github.ai/inference", json=payload, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json().get("output", "")
```

Verification / Smoke Checks

- Dry‑run agent smoke:
```bash
AGENT_DRY_RUN=1 python -c "from agent.core import run_sync; print(run_sync('Hallo'))"
```
- Real model smoke (after setting keys):
```bash
export AGENT_DRY_RUN=0
export AGENT_PROVIDER=github
export AGENT_MODEL=openai/gpt-4.1-mini
export GITHUB_MODEL_KEY=...
python -c "from agent.core import run_sync; print(run_sync('Test'))"
```

Success‑Metrics (empfohlen)

- Relevanz / Groundedness (Factuality) — primary quality metric
- Latenz (ms to first token & end‑to‑end)
- Cost per 1k tokens (budget awareness)

Hinweis

- Keine Schlüssel in Repo. Verwende env vars und CI secrets.
- Für Production mit Foundry: deploy Model in Foundry und setze `AGENT_PROVIDER=foundry` sowie passende endpoint creds.

---

Kurz und bündig: `openai/gpt-4.1-mini` für Balance, `openai/gpt-4.1-nano` als günstige Alternative; Foundry für Produktion, GitHub für schnelles Entwickeln.
