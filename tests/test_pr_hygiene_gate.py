from scripts import pr_hygiene_gate as gate


def test_make_md_report_empty():
    md = gate.make_md_report([], [], ["owner/repo"], "fast")
    assert "Status: OK" in md


def test_scan_repo_fast_mock(monkeypatch, tmp_path):
    # Simulate run_gh_search returning sample PRs
    sample = [
        {
            "number": 1,
            "title": "WIP PR",
            "url": "https://github.com/x/y/pull/1",
            "labels": [{"name": "wip"}],
            "reviewDecision": None,
        }
    ]

    def fake_run_gh_search(repo, base, checks=None, query_extra=None):
        if checks == "failure":
            return []
        if checks == "pending":
            return []
        if "label" in (query_extra or ""):
            return sample
        if query_extra == "is:draft":
            return []
        return []

    monkeypatch.setattr(gate, "run_gh_search", fake_run_gh_search)
    policy = gate.Policy(block_on_labels=["wip"])
    blockers = gate.scan_repo_fast("owner/repo", ["main"], policy)
    assert any(b.reason == "blocked_label" for b in blockers)
