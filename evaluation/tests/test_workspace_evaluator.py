from scripts.workspace_evaluation import WorkspaceEvaluator


def test_evaluate_file_structure(tmp_path):
    # Prepare minimal workspace structure
    (tmp_path / "scripts").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "configs").mkdir()
    (tmp_path / "pyproject.toml").write_text("[tool.poetry]")
    (tmp_path / "requirements.txt").write_text("")
    (tmp_path / ".gitignore").write_text(".env")
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "workflows").mkdir()

    evaluator = WorkspaceEvaluator(tmp_path)
    res = evaluator.evaluate_file_structure()

    # All critical_paths should exist
    assert res["failed"] == 0
    assert len(res["details"]) > 0
    for d in res["details"]:
        assert d["exists"] is True


def test_evaluate_service_ports_monkeypatch(monkeypatch, tmp_path):
    evaluator = WorkspaceEvaluator(tmp_path)

    # Force check_port_in_use to return False for deterministic result
    monkeypatch.setattr(evaluator, "check_port_in_use", lambda p, host="127.0.0.1": False)
    res = evaluator.evaluate_service_ports()

    # All ports reported as available => no failures
    assert res["failed"] == 0
    assert len(res["available"]) > 0
