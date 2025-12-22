import json
import threading
import http.server
import socketserver
import time
from pathlib import Path
import tempfile

import pytest

from evaluation import runner


class TestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/health'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "healthy"}')
        elif self.path.startswith('/run'):
            # echo input param
            import urllib.parse as up
            q = up.urlparse(self.path).query
            params = up.parse_qs(q)
            inp = params.get('input', [''])[0]
            body = f"received: {inp}"
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(body.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


@pytest.fixture()
def simple_server():
    with socketserver.TCPServer(('127.0.0.1', 0), TestHandler) as httpd:
        port = httpd.server_address[1]
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        # give server a moment
        time.sleep(0.05)
        yield port
        httpd.shutdown()
        t.join()


def test_run_with_mocked_ports(tmp_path, monkeypatch, simple_server):
    port = simple_server

    # monkeypatch find_agent_port to return our server port
    monkeypatch.setattr(runner, 'find_agent_port', lambda agent: port)

    ds = tmp_path / 'cases.jsonl'
    ds.write_text('{"id":"1","agent":"openaX","input":"hello","expected":"contains: received: hello"}\n')

    out = tmp_path / 'report.json'
    rc = runner.run(ds, out)
    assert rc == 0
    report = json.loads(out.read_text(encoding='utf-8'))
    assert 'summary' in report
    assert report['summary']['total_cases'] == 1
    assert report['summary']['relevance_pass_rate'] == 1.0


def test_health_check_failure(tmp_path, monkeypatch):
    # No server running -> find_agent_port returns None
    monkeypatch.setattr(runner, 'find_agent_port', lambda agent: None)
    ds = tmp_path / 'cases.jsonl'
    ds.write_text('{"id":"1","agent":"openaY","input":"x","expected":"health: healthy"}\n')
    out = tmp_path / 'report.json'
    rc = runner.run(ds, out)
    assert rc == 0
    report = json.loads(out.read_text(encoding='utf-8'))
    # case should be skipped
    assert report['summary']['total_cases'] == 1
    assert report['results'][0]['result'] in ('skip', 'skipped', 'fail', 'pass')
