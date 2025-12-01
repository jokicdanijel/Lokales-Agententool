#!/bin/bash
# PORTIER 3.0 - Quick Agent Generator

BASE_DIR="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui"
AGENT_BASE_DIR="$BASE_DIR/LocalAgent-Pro"

echo ""
echo "=========================================="
echo "  PORTIER 3.0 - Agent Cluster Generator"
echo "=========================================="
echo ""

for AGENT_ID in {4..19}; do
  PORT=$((12344 + AGENT_ID))
  AGENT_DIR="$AGENT_BASE_DIR/opena$AGENT_ID"
  
  echo -n "🔧 Generating opena$AGENT_ID (Port $PORT)... "
  
  # Create directory
  mkdir -p "$AGENT_DIR"
  
  # Create config.json
  cat > "$AGENT_DIR/config.json" << CFGEOF
{
  "service_name": "opena$AGENT_ID",
  "port": $PORT,
  "host": "127.0.0.1",
  "version": "3.0.0",
  "role": "scalable-agent",
  "bearer_token": "sk_opena${AGENT_ID}_scalable_v3_prod",
  "coordinator": "http://127.0.0.1:12345",
  "archivator": "http://127.0.0.1:12346"
}
CFGEOF

  # Create main.py
  cat > "$AGENT_DIR/main.py" << PYEOF
#!/usr/bin/env python3
"""OpenA$AGENT_ID - PORTIER 3.0 Scalable Agent"""
import http.server, socketserver, json, time
PORT, SERVICE = $PORT, "opena$AGENT_ID"
START_TIME = time.time()
class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path=="/health": 
            self.send_json({"status":"online","service":SERVICE,"port":PORT})
        elif self.path=="/info": 
            self.send_json({"name":SERVICE,"role":"scalable-agent","id":$AGENT_ID})
        else: self.send_error(404)
    def send_json(self,d):
        self.send_response(200);self.send_header("Content-type","application/json");self.send_header("Access-Control-Allow-Origin","*");self.end_headers();self.wfile.write(json.dumps(d).encode())
    def log_message(self,*a):pass
try:
    print(f"\n✅ {SERVICE} running on http://127.0.0.1:{PORT}")
    with socketserver.TCPServer(("127.0.0.1",PORT),H) as h:h.serve_forever()
except:print(f"❌ Port {PORT} in use")
PYEOF

  chmod +x "$AGENT_DIR/main.py"
  
  # Create __init__.py
  echo '"""OpenA'$AGENT_ID' - PORTIER 3.0"""' > "$AGENT_DIR/__init__.py"
  
  echo "✅"
done

echo ""
echo "✅ All 16 agents created!"
echo ""

# Create startup script
mkdir -p "$BASE_DIR/bin"
cat > "$BASE_DIR/bin/start_agents.sh" << STARTEOF
#!/bin/bash
echo "🚀 Starting Agent Cluster (opena4-opena19)..."
cd "$BASE_DIR"
for AGENT_ID in {4..19}; do
  python3 LocalAgent-Pro/opena\$AGENT_ID/main.py > LocalAgent-Pro/logs/opena\$AGENT_ID.log 2>&1 &
done
sleep 2
echo "✅ All agents started!"
STARTEOF

chmod +x "$BASE_DIR/bin/start_agents.sh"
echo "�� Startup script created: bin/start_agents.sh"
echo ""
