# 🚀 PORTIER 3.0 - Deployment Guide (Phase 6)

**Version**: 3.0.0
**Status**: Production Ready
**Date**: 24. November 2025

---

## 📋 Deployment Modes

### Mode 1: Development (Foreground)

```bash
# Terminal 1
python3 LocalAgent-Pro/opena1/main.py

# Terminal 2
python3 LocalAgent-Pro/opena2/main.py

# Terminal 3
python3 LocalAgent-Pro/opena3/main.py

# Terminal 4
python3 LocalAgent-Pro/web_dashboard.py
```

### Mode 2: Production (Background)

```bash
# Start all services
nohup python3 LocalAgent-Pro/opena1/main.py > LocalAgent-Pro/logs/opena1.log 2>&1 &
nohup python3 LocalAgent-Pro/opena2/main.py > LocalAgent-Pro/logs/opena2.log 2>&1 &
nohup python3 LocalAgent-Pro/opena3/main.py > LocalAgent-Pro/logs/opena3.log 2>&1 &
nohup python3 LocalAgent-Pro/web_dashboard.py > LocalAgent-Pro/logs/dashboard.log 2>&1 &

# Verify
ps aux | grep -E "opena[123]|web_dashboard" | grep -v grep
```

### Mode 3: Systemd (Recommended)

Create service files for automatic startup:

```bash
# 1. Create service file for opena1
sudo tee /etc/systemd/system/portier-opena1.service << EOF
[Unit]
Description=PORTIER 3.0 - opena1 Coordinator
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui
ExecStart=/usr/bin/python3 LocalAgent-Pro/opena1/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 2. Create service file for opena2
sudo tee /etc/systemd/system/portier-opena2.service << EOF
[Unit]
Description=PORTIER 3.0 - opena2 Archivator
After=network.target portier-opena1.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui
ExecStart=/usr/bin/python3 LocalAgent-Pro/opena2/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 3. Create service file for opena3
sudo tee /etc/systemd/system/portier-opena3.service << EOF
[Unit]
Description=PORTIER 3.0 - opena3 Gateway
After=network.target portier-opena2.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui
ExecStart=/usr/bin/python3 LocalAgent-Pro/opena3/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 4. Create service file for dashboard
sudo tee /etc/systemd/system/portier-dashboard.service << EOF
[Unit]
Description=PORTIER 3.0 - Web Dashboard
After=network.target portier-opena3.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui
ExecStart=/usr/bin/python3 LocalAgent-Pro/web_dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 5. Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable portier-opena1.service
sudo systemctl enable portier-opena2.service
sudo systemctl enable portier-opena3.service
sudo systemctl enable portier-dashboard.service

# 6. Start services
sudo systemctl start portier-opena1
sudo systemctl start portier-opena2
sudo systemctl start portier-opena3
sudo systemctl start portier-dashboard

# 7. Check status
sudo systemctl status portier-opena1
sudo systemctl status portier-opena2
sudo systemctl status portier-opena3
sudo systemctl status portier-dashboard

# 8. View logs
sudo journalctl -u portier-opena1 -f
```

### Mode 4: Docker

#### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY LocalAgent-Pro/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY LocalAgent-Pro/ ./

# Create logs directory
RUN mkdir -p logs

# Default to opena1
ENV AGENT_ID=1
ENV PORT=12345

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:${PORT}/health')"

EXPOSE ${PORT}

CMD ["python3", "opena${AGENT_ID}/main.py"]
```

#### docker-compose.yml

```yaml
version: "3.8"

services:
  opena1:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - AGENT_ID=1
      - PORT=12345
    ports:
      - "12345:12345"
    restart: unless-stopped
    networks:
      - portier

  opena2:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - AGENT_ID=2
      - PORT=12346
    ports:
      - "12346:12346"
    restart: unless-stopped
    depends_on:
      - opena1
    networks:
      - portier

  opena3:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - AGENT_ID=3
      - PORT=12347
    ports:
      - "12347:12347"
    restart: unless-stopped
    depends_on:
      - opena2
    networks:
      - portier

  dashboard:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - AGENT_ID=20
      - PORT=8000
    ports:
      - "8000:8000"
    restart: unless-stopped
    depends_on:
      - opena3
    networks:
      - portier

networks:
  portier:
    driver: bridge
```

#### Start Docker Stack

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f opena1

# Stop services
docker-compose down
```

---

## 🛠️ Operations Scripts

### bin/ops.sh

```bash
#!/bin/bash
# PORTIER 3.0 Operations Script

BASE_DIR="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui"

case "$1" in
  start)
    echo "🚀 Starting PORTIER 3.0 Stack..."
    cd "$BASE_DIR"
    nohup python3 LocalAgent-Pro/opena1/main.py > logs/opena1.log 2>&1 &
    nohup python3 LocalAgent-Pro/opena2/main.py > logs/opena2.log 2>&1 &
    nohup python3 LocalAgent-Pro/opena3/main.py > logs/opena3.log 2>&1 &
    nohup python3 LocalAgent-Pro/web_dashboard.py > logs/dashboard.log 2>&1 &
    sleep 2
    echo "✅ All services started"
    ;;

  stop)
    echo "⏹️  Stopping PORTIER 3.0 Stack..."
    pkill -f "opena[123]|web_dashboard"
    sleep 1
    echo "✅ All services stopped"
    ;;

  restart)
    echo "🔄 Restarting PORTIER 3.0 Stack..."
    $0 stop
    sleep 2
    $0 start
    ;;

  status)
    echo "📊 PORTIER 3.0 Status:"
    ps aux | grep -E "opena[123]|web_dashboard" | grep -v grep || echo "❌ No services running"
    ;;

  verify)
    echo "🔍 Verifying PORTIER 3.0 Stack..."
    for port in 12345 12346 12347 8000; do
      curl -s http://127.0.0.1:$port/health > /dev/null && echo "✅ Port $port online" || echo "❌ Port $port offline"
    done
    ;;

  *)
    echo "Usage: $0 {start|stop|restart|status|verify}"
    exit 1
    ;;
esac
```

---

## 🔐 Firewall Configuration

### UFW (Uncomplicated Firewall)

```bash
# Allow internal ports only
sudo ufw allow from 127.0.0.1 to any port 12345
sudo ufw allow from 127.0.0.1 to any port 12346
sudo ufw allow from 127.0.0.1 to any port 12347
sudo ufw allow from 127.0.0.1 to any port 8000

# Or open for local network
sudo ufw allow from 192.168.1.0/24 to any port 12345
sudo ufw allow from 192.168.1.0/24 to any port 12346

# Enable firewall
sudo ufw enable
sudo ufw status verbose
```

### iptables

```bash
# Allow specific IPs
sudo iptables -A INPUT -p tcp --dport 12345 -s 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 12346 -s 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 12347 -s 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8000 -s 127.0.0.1 -j ACCEPT

# Save rules
sudo apt-get install iptables-persistent
sudo netfilter-persistent save
```

---

## 📊 Monitoring

### Health Check Script

```bash
#!/bin/bash
# Check all services every 60 seconds

while true; do
  echo "$(date) - Health Check"

  for port in 12345 12346 12347 8000; do
    status=$(curl -s http://127.0.0.1:$port/health | jq -r '.status' 2>/dev/null)
    if [ "$status" == "healthy" ] || [ "$status" == "online" ] || [ "$status" == "ok" ]; then
      echo "  ✅ Port $port: OK"
    else
      echo "  ❌ Port $port: FAILED"
      # Restart service
      systemctl restart portier-* 2>/dev/null || echo "  Manual restart required"
    fi
  done

  sleep 60
done
```

---

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check if port is already in use
lsof -i :12345

# Kill existing process
kill -9 <PID>

# Start service again
python3 LocalAgent-Pro/opena1/main.py
```

### High Memory Usage

```bash
# Find memory hogs
ps aux --sort=-%mem | head -10

# Restart specific service
systemctl restart portier-opena1
```

### Connection Refused

```bash
# Check if service is running
ps aux | grep opena1

# Check network connectivity
netstat -tlnp | grep 12345

# Test locally
curl http://127.0.0.1:12345/health
```

---

## ✅ Deployment Checklist

- [x] Services start without errors
- [x] Health endpoints respond
- [x] Ports are correctly configured
- [x] Logs are being written
- [x] Firewall rules are applied
- [x] Systemd services are configured
- [x] Docker images build successfully
- [x] Monitoring script is active

---

**Status**: ✨ Phase 6 Complete
**Next Phase**: Phase 17 (Monitoring with Prometheus/Grafana)
