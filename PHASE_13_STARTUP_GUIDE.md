# 🟣 PHASE 13: PRODUCTION STARTUP PROCEDURE

**Datum:** 24. November 2025
**Firma:** JD Smart Vision EU
**Erfinder:** Danijel Jokic
**Status:** ✅ READY TO DEPLOY

---

## 📋 PRE-FLIGHT CHECKLIST

```bash
✅ opena1 (Koordinator)       - Python main.py verfügbar
✅ opena2 (Archivator)        - opena2_app.py bereit
✅ kordp (Gateway)            - tool_dispatcher.py aktiv
✅ opena3 (WebUI)             - main_openwebui_bridge_v2.py ready
✅ opena20 (Dashboard)        - main.py + metrics_exporter.py OK
✅ Safepoints System          - data/ Struktur vorbereitet
✅ Dokumentation              - MASTER_PROMPT + SECURITY.md + NOTICE.md
✅ Configuration Files        - .env.template vorhanden
```

---

## 🚀 STARTUP SEQUENCE (AUTOMATISCH)

### **STEP 1: Dependency Check (30s)**

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# Python 3.12+ Check
python3 --version

# Required Packages: FastAPI, Pydantic, OpenAI SDK, etc.
pip list | grep -E "fastapi|pydantic|openai|requests"
```

### **STEP 2: Environment Setup (1min)**

```bash
# Generate .env from templates if missing
for template in $(find . -name ".env.template"); do
  dir=$(dirname $template)
  if [ ! -f "$dir/.env" ]; then
    cp $template $dir/.env
    echo "Created .env in $dir"
  fi
done

# Verify critical .env variables
echo "CHECKING BEARER TOKEN..."
grep -i "bearer\|token\|api_key" .env.example
```

### **STEP 3: Service Startup Order (Option-2-Flow)**

#### **3A. opena2 (Archivator) FIRST - Port 12345**

```bash
cd 1.opena1&2_portier

# Start archivator (needs to be first - append-only safepoints)
python3 opena2_app.py &
PID_OPENA2=$!

# Wait for initialization
sleep 3

# Verify health
curl -s http://127.0.0.1:12345/health | jq .
```

#### **3B. opena1 (Koordinator) - Port 12344**

```bash
# Start coordinator (depends on archivator being ready)
python3 main.py &
PID_OPENA1=$!

# Wait for initialization
sleep 3

# Verify health
curl -s http://127.0.0.1:12344/health | jq .
```

#### **3C. kordp (Gateway) - Port 12346**

```bash
# Start gateway (routes to tools)
python3 tool_dispatcher.py &
PID_KORDP=$!

sleep 2

# Verify health
curl -s http://127.0.0.1:12346/health | jq .
```

#### **3D. opena3 (OpenWebUI Terminal) - Port 12347**

```bash
cd ../2.opena3_openwebui

# Start WebUI bridge
python3 main_openwebui_bridge_v2.py &
PID_OPENA3=$!

sleep 2

# Test WebUI endpoint
curl -s http://127.0.0.1:12347/dashboard
```

#### **3E. opena20 (Dashboard) - Port 12349**

```bash
cd ../19.opena20_dashboard_agent

# Start dashboard
python3 main.py &
PID_OPENA20=$!

sleep 2

# Verify health
curl -s http://127.0.0.1:12349/health | jq .
```

---

## ✅ POST-STARTUP VERIFICATION

### **Health Check - All Services**

```bash
echo "=== HEALTH CHECK ===" && \
curl -s http://127.0.0.1:12344/health && echo "" && \
curl -s http://127.0.0.1:12345/health && echo "" && \
curl -s http://127.0.0.1:12346/health && echo "" && \
curl -s http://127.0.0.1:12347/dashboard | head -50 && \
curl -s http://127.0.0.1:12349/health
```

### **Process Status**

```bash
jobs -l
ps aux | grep -E "opena|python" | grep -v grep
```

### **Port Verification**

```bash
netstat -tlnp | grep -E "12344|12345|12346|12347|12349"
# oder:
lsof -i -P -n | grep LISTEN
```

### **Safepoint Test**

```bash
# Create test safepoint
curl -X POST http://127.0.0.1:12345/safepoint \
  -H "Authorization: Bearer TEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "opena1",
    "command": "test",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }'

# Check if saved
find data/safepoints -name "*→*" -type f | head -5
```

---

## 🎯 NEXT: Access Points

### **Dashboards & UIs**

| Service            | URL                    | Port  | Purpose         |
| ------------------ | ---------------------- | ----- | --------------- |
| opena1 Coordinator | http://127.0.0.1:12344 | 12344 | Request Router  |
| opena2 Archivator  | http://127.0.0.1:12345 | 12345 | Safepoint Store |
| kordp Gateway      | http://127.0.0.1:12346 | 12346 | Tool Dispatcher |
| opena3 WebUI       | http://127.0.0.1:12347 | 12347 | Terminal UI     |
| opena20 Dashboard  | http://127.0.0.1:12349 | 12349 | Live Monitoring |

### **API Endpoints (Option-2-Flow)**

```bash
# Request Entry Point
POST http://127.0.0.1:12344/request
  Header: Authorization: Bearer <TOKEN>
  Body: {
    "source": "openai",
    "user_query": "...",
    "context": {}
  }

# Response from Archivator
GET http://127.0.0.1:12345/safepoints
  Query: ?date=2025-11-24

# Tool Dispatch
POST http://127.0.0.1:12346/execute_tool
  Body: {
    "tool_name": "file_manager",
    "args": {...}
  }
```

---

## 🔧 TROUBLESHOOTING

### If opena1 fails to start:

```bash
# Check if port 12344 is in use
lsof -i :12344

# Kill existing process
kill -9 $(lsof -t -i :12344)

# Restart
python3 main.py
```

### If opena2 (Archivator) is not responding:

```bash
# Check safepoint directory permissions
ls -la data/safepoints

# Verify disk space
df -h

# Check if Unicode arrows are saved
find data/safepoints -name "*→*"
```

### If opena20 Dashboard shows blank:

```bash
# Check metrics exporter
curl http://127.0.0.1:12349/metrics

# Verify dependencies
pip list | grep prometheus
```

---

## 📊 MONITORING

### **Real-time Logs**

```bash
# Follow opena1 logs
tail -f /var/log/opena1.log

# Follow all agent logs
tail -f /var/log/portier/*.log 2>/dev/null || echo "No logs found"
```

### **Performance Metrics**

```bash
# CPU/Memory usage per service
ps aux | grep opena

# Active connections
netstat -an | grep ESTABLISHED | wc -l
```

---

## 🎯 PHASE 13 SUCCESS CRITERIA

✅ All 5 core services responding on their ports
✅ Option-2-Flow routing working (test via curl)
✅ Safepoints being created with Unicode → markers
✅ Dashboard showing live metrics
✅ No errors in logs
✅ Response time <500ms for test queries

---

## 📝 QUICK START (TL;DR)

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# 1. Setup env
for f in $(find . -name ".env.template"); do cp $f ${f%.template}; done

# 2. Start services in order (background)
cd 1.opena1&2_portier && \
python3 opena2_app.py > /tmp/opena2.log 2>&1 & \
sleep 2 && \
python3 main.py > /tmp/opena1.log 2>&1 & \
sleep 2 && \
python3 tool_dispatcher.py > /tmp/kordp.log 2>&1 & \
cd ../2.opena3_openwebui && \
python3 main_openwebui_bridge_v2.py > /tmp/opena3.log 2>&1 & \
cd ../19.opena20_dashboard_agent && \
python3 main.py > /tmp/opena20.log 2>&1 &

# 3. Health check
sleep 5
for port in 12344 12345 12346 12347 12349; do
  curl -s http://127.0.0.1:$port/health 2>/dev/null && echo "Port $port: ✅" || echo "Port $port: ❌"
done

# 4. Open dashboard
xdg-open http://127.0.0.1:12349

echo "🟣 PHASE 13 PRODUCTION STARTED!"
```

---

_Generated for JD Smart Vision EU - PHASE 13 Production Deployment_
