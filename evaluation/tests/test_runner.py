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
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path.startswith('/api/openwebui/chat'):
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                data = json.loads(body)
                inp = data.get('message', '')
            except Exception:
                inp = ''
            resp = {'response': f'received: {inp}'}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode('utf-8'))
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


def test_run_with_mocked_ports(tmp_path, simple_server):
    port = simple_server

    # Create a Runner pointing to our test server endpoint
    endpoint = f'http://127.0.0.1:{port}/api/openwebui/chat'
    r = runner.Runner(endpoint=endpoint)

    ds = tmp_path / 'cases.jsonl'
    ds.write_text('{"id":"1","input":"hello","expected":"contains: received: hello"}\n')

    out = tmp_path / 'report.json'
    report = r.run(str(ds), str(out))
    assert 'summary' in report
    assert report['summary']['relevance_pass_rate'] == 1.0


def test_health_check_failure(tmp_path):
    # Use an endpoint that won't respond (port unlikely to be used)
    endpoint = 'http://127.0.0.1:9/api/openwebui/chat'
    r = runner.Runner(endpoint=endpoint)
    ds = tmp_path / 'cases.jsonl'
    ds.write_text('{"id":"1","input":"x","expected":"contains: nothing"}\n')
    out = tmp_path / 'report.json'
    report = r.run(str(ds), str(out))
    assert 'summary' in report
    assert report['summary']['relevance_pass_rate'] == 0.0
