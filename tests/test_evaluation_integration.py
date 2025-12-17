import os
import tempfile
import pytest
from evaluation.runner import Runner


@pytest.mark.skipif(os.getenv("RUN_EVAL_INTEGRATION") != "1", reason="Integration tests disabled by default")
def test_integration_runner_against_openwebui():
    ds = os.path.join(os.path.dirname(__file__), "../evaluation/datasets/sample.jsonl")
    out = tempfile.mktemp(suffix=".json")
    runner = Runner()
    report = runner.run(ds, out)
    assert report["summary"]["count"] == 2
    assert "exact_match" in report["summary"]
