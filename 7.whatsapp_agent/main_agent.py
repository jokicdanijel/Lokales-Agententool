#!/usr/bin/env python3
import http.server
import socketserver
import json

HOST = "127.0.0.1"
PORT = 12350

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            msg = json.dumps({
                "service": "whatsapp_agent",
                "status": "healthy",
                "port": 12350
            }).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
        print(f"whatsapp_agent listening on http://{HOST}:{PORT}")
        httpd.serve_forever()
