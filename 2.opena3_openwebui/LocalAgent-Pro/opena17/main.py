#!/usr/bin/env python3
import http.server
import socketserver
import json
import time
PORT = 12361
SERVICE_NAME = "opena17"
TOKEN = "sk_opena17_compute_v3_production"

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "online", "service": SERVICE_NAME, "port": PORT}).encode())
            return
        self.send_response(404)
        self.end_headers()
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"🚀 {SERVICE_NAME} on port {PORT}")
        try: httpd.serve_forever()
        except KeyboardInterrupt: print("\n⏹️  Shutting down...")
