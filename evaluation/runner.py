"""Simple evaluation runner.

- Loads JSONL dataset: each line is {"id":"...","input":"...","expected":"..."}
- Sends request to configured endpoint (or uses a local evaluator function)
- Computes metrics from evaluation.metrics and writes JSON report
"""
import os
import json
import time
from typing import List, Dict, Any, Optional
import requests
from .metrics import exact_match, contains_frac, length_ratio, aggregate


DEFAULT_ENDPOINT = os.getenv("EVALUATION_ENDPOINT", "http://127.0.0.1:12349/api/openwebui/chat")


class Runner:
    def __init__(self, endpoint: Optional[str] = None):
        self.endpoint = endpoint or DEFAULT_ENDPOINT

    def load_dataset(self, path: str) -> List[Dict[str, Any]]:
        items = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                items.append(json.loads(line))
        return items

    def run_sample(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """Send one sample to the endpoint and compute metrics.

        Uses env EVALUATION_BEARER_TOKEN or BEARER_TOKEN for Authorization if present.
        Sends JSON payload with `message` field (matches Dashboard /openwebui/chat API).
        """
        token = os.getenv("EVALUATION_BEARER_TOKEN") or os.getenv("BEARER_TOKEN")
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        payload = {"message": sample.get("input", "")}

        text = ""
        timeout_val = int(os.getenv("EVALUATION_TIMEOUT", "30"))
        max_attempts = int(os.getenv("EVALUATION_RETRIES", "2"))
        attempt = 0
        while attempt < max_attempts:
            try:
                resp = requests.post(self.endpoint, json=payload, headers=headers, timeout=timeout_val)
                # Handle non-200 gracefully
                if resp.status_code != 200:
                    text = ""
                else:
                    ctype = resp.headers.get("content-type", "")
                    if ctype.startswith("application/json"):
                        data = resp.json()
                        # attempt to extract a sensible text/str from common keys
                        if isinstance(data, dict):
                            # common OpenAI-like Chat completion format
                            if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                                first = data["choices"][0]
                                # try several nested shapes
                                if isinstance(first.get("message"), dict) and "content" in first["message"]:
                                    val = first["message"]["content"]
                                elif "text" in first:
                                    val = first.get("text")
                                else:
                                    val = first
                            elif "response" in data:
                                val = data.get("response")
                            elif "output" in data:
                                val = data.get("output")
                            elif "message" in data and isinstance(data.get("message"), str):
                                val = data.get("message")
                            else:
                                val = data
                        else:
                            val = data

                        if isinstance(val, str):
                            text = val
                        else:
                            # Try to extract a reasonable string from nested structures
                            if isinstance(val, dict) and "message" in val and isinstance(val["message"], dict) and "content" in val["message"]:
                                text = val["message"]["content"]
                            else:
                                try:
                                    text = json.dumps(val, ensure_ascii=False)
                                except Exception:
                                    text = str(val)
                    else:
                        text = resp.text
                break
            except requests.exceptions.ReadTimeout:
                attempt += 1
                # retry with increased timeout
                timeout_val = timeout_val * 2
                if attempt >= max_attempts:
                    text = ""
            except Exception:
                text = ""
                break
        em = exact_match(text, sample.get("expected", ""))
        cf = contains_frac(text, sample.get("expected", ""))
        lr = length_ratio(text, sample.get("expected", ""))
        return {
            "id": sample.get("id"),
            "input": sample.get("input"),
            "expected": sample.get("expected"),
            "output": text,
            "metrics": {"exact_match": em, "contains_frac": cf, "length_ratio": lr},
        }

    def run(self, dataset_path: str, out_path: Optional[str] = None) -> Dict[str, Any]:
        data = self.load_dataset(dataset_path)
        results = []
        scores = {"exact_match": [], "contains_frac": [], "length_ratio": []}
        for s in data:
            r = self.run_sample(s)
            results.append(r)
            scores["exact_match"].append(r["metrics"]["exact_match"])
            scores["contains_frac"].append(r["metrics"]["contains_frac"])
            scores["length_ratio"].append(r["metrics"]["length_ratio"])
            time.sleep(0.05)
        agg = aggregate(scores)
        report = {"summary": agg, "results": results, "timestamp": time.time(), "endpoint": self.endpoint}
        if out_path:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run evaluation dataset against an endpoint")
    parser.add_argument("dataset", help="Path to JSONL dataset")
    parser.add_argument("--out", default="evaluation/results/report.json", help="Output report path")
    parser.add_argument("--endpoint", default=None, help="Override endpoint URL")
    args = parser.parse_args()
    runner = Runner(endpoint=args.endpoint)
    report = runner.run(args.dataset, args.out)
    print(json.dumps(report["summary"], indent=2))
