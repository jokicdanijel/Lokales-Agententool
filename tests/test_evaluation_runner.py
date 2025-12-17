import json
import os
from evaluation.runner import Runner


def test_load_dataset(tmp_path):
    p = tmp_path / "ds.jsonl"
    p.write_text('{"id":"1","input":"a","expected":"a"}\n')
    r = Runner()
    data = r.load_dataset(str(p))
    assert len(data) == 1
    assert data[0]["id"] == "1"


def test_run_sample_monkeypatch(monkeypatch):
    r = Runner(endpoint="http://example.local/test")

    class DummyResp:
        def __init__(self):
            self.headers = {"content-type": "application/json"}

        def json(self):
            return {"response": "Hello World"}

    def fake_post(url, json, timeout):
        return DummyResp()

    monkeypatch.setattr("requests.post", fake_post)
    sample = {"id": "1", "input": "x", "expected": "Hello World"}
    out = r.run_sample(sample)
    assert out["metrics"]["exact_match"] == 1
