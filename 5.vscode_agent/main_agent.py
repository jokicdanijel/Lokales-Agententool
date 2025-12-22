#!/usr/bin/env python3
import http.server
import json
import socketserver

HOST = "127.0.0.1"
PORT = 12348


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path == "/health":
            msg = json.dumps({"service": "vscode_agent", "status": "healthy", "port": PORT}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):  # noqa: A002
        pass


if __name__ == "__main__":
    with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
        print(f"vscode_agent shim listening on http://{HOST}:{PORT}")
        httpd.serve_forever()
