import json
import subprocess


def run_scan(tmp_path, content_files, extra_args=None):
    sd = tmp_path / "service"
    sd.mkdir(exist_ok=True)
    for name, content in content_files.items():
        p = sd / name
        p.write_text(content)
    args = ["python3", "scripts/elion_service_scanner.py", "--service-dir", str(sd), "--plan", "basic"]
    if extra_args:
        args += extra_args
    res = subprocess.run(args, capture_output=True, text=True)
    return res


def test_scan_pass(tmp_path):
    files = {
        "app.py": "print('hello')\n# PORT=12349\n",
        "README.md": "This is a service. health: /health - returns {'status':'healthy'}",
    }
    res = run_scan(tmp_path, files)
    assert "=== ELION_SCAN_BEGIN ===" in res.stdout
    assert "status: PASS" in res.stdout
    assert res.returncode == 0


def test_scan_forbidden_port_detected(tmp_path):
    files = {
        "app.py": "# uses 8080 port\nPORT=8080\n",
    }
    res = run_scan(tmp_path, files)
    assert "=== ELION_SCAN_BEGIN ===" in res.stdout
    assert "status: FAIL" in res.stdout
    assert "Forbidden port mention '8080'" in res.stdout
    assert res.returncode == 1


def test_scan_host_port_mapping_and_compose(tmp_path):
    files = {
        "Dockerfile": "EXPOSE 5432\n# mapping 12380:5432 in docs\n",
        "service_manifest.json": json.dumps({"container_port": 5432, "host_port": 12380}),
    }

    # By default, exposure defaults to internal_only for unknown services -> host_port set but exposure != edge_only -> FAIL
    res = run_scan(tmp_path, files)
    assert "status: FAIL" in res.stdout
    assert "host_port set but exposure != edge_only" in res.stdout

    # If exposure is explicitly set to edge_only, it should PASS and map ports
    res2 = run_scan(tmp_path, files, extra_args=["--exposure", "edge_only"])
    assert "status: PASS" in res2.stdout or "status: WARN" in res2.stdout
    assert "--- COMPOSE_FRAGMENT_YAML_BEGIN ---" in res2.stdout
    assert "ports:" in res2.stdout
    # host mapping 12380 should be present
    assert "12380" in res2.stdout
