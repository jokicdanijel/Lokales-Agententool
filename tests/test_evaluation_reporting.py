import tempfile

from evaluation.reporting import write_markdown_summary, write_summary_csv


def test_reporting_roundtrip():
    report = {
        "summary": {"count": 2, "exact_match": 0.5},
        "results": [
            {"id": "1", "metrics": {"exact_match": 1, "contains_frac": 1.0, "length_ratio": 1.0}},
            {"id": "2", "metrics": {"exact_match": 0, "contains_frac": 0.0, "length_ratio": 0.0}},
        ],
    }
    csvp = tempfile.mktemp(suffix=".csv")
    mdp = tempfile.mktemp(suffix=".md")
    write_summary_csv(report, csvp)
    write_markdown_summary(report, mdp)
    assert open(csvp).read().count("\n") >= 2
    assert "Evaluation Summary" in open(mdp).read()
