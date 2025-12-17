# 🚀 ELION Hyper-Dashboard – Production Deployment Steps

**Target:** Deploy ELION Stack to `https://hyperdashboard-one.de` with Nginx Reverse Proxy + SSL/TLS

**Prerequisites Completed:**
- ✅ Local stack tested and working (`bin/ops.sh start`)
- ✅ 18 Agenten registriert
- ✅ Dashboard UI erreichbar auf `http://127.0.0.1:12349/static/index.html`
- ✅ All endpoints tested locally
- ✅ Nginx config prepared (in `DEPLOYMENT_OPENA4.md`)

---

## Step 1: Server Preparation (SSH onto Server)

```bash
# Connect to server
ssh ubuntu@<SERVER_IP>

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y nginx certbot python3-certbot-nginx git docker.io docker-compose

# Enable services
sudo systemctl enable nginx docker
sudo systemctl start docker
```

✅ **Check:**
```bash
docker --version    # Should be v20+
docker ps           # Should return empty list
```

---

## Step 2: DNS Configuration

**In your DNS provider (e.g., Namecheap, Google Domains, Route53):**
1. Go to DNS Settings for `hyperdashboard-one.de`
2. Add/Update A Record:
   - **Type:** A
   - **Name:** @ (or hyperdashboard-one.de)
   - **Value:** `<YOUR_SERVER_IP>`
   - **TTL:** 3600

3. Wait 5-15 minutes for DNS propagation

✅ **Verify DNS:**
```bash
nslookup hyperdashboard-one.de
# Should show: Name: hyperdashboard-one.de, Address: <SERVER_IP>
```

---

## Step 3: Deploy Code

```bash
# On server, create deployment directory
sudo mkdir -p /var/www/hyperdashboard
sudo chown -R ubuntu:ubuntu /var/www/hyperdashboard
cd /var/www/hyperdashboard

# Clone repository
git clone https://github.com/jokicdanijel/Gesamtprojekt-start.git .

# Or if you have SSH key configured:
git clone git@github.com:jokicdanijel/Gesamtprojekt-start.git .
```

---

## Step 4: Configure Environment

```bash
# Copy .env template
cp mcp_server/.env.example .env

# Edit .env with your secrets
nano .env

# CRITICAL: Set these values:
DASHBOARD_ADMIN_TOKEN=your-strong-secret-token-here
OPENAI_API_KEY_OPENA1=sk-...
OPENAI_API_KEY_OPENA2=sk-...
WEBHOOK_SECRET=your-webhook-secret
DATABASE_URL=postgresql://elion:password@localhost:5432/elion_db
REDIS_URL=redis://localhost:6379/0
```

✅ **Verify .env:**
```bash
grep -E "^(DASHBOARD_ADMIN_TOKEN|OPENAI_API_KEY)" .env | head -5
```

---

## Step 5: Start Services

```bash
# From /var/www/hyperdashboard
cd /var/www/hyperdashboard

# Start all services
bash bin/ops.sh start

# Wait 5 seconds
sleep 5

# Health check
bash bin/ops.sh health
```

✅ **Expected Output:**
```
✅ opena1 Health: ok
✅ opena2 Health: ok
✅ Dashboard Health: healthy
✅ 18 agents registered
```

---

## Step 6: Configure Nginx Reverse Proxy

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/hyperdashboard-one.de
```

**Paste this content (from `DEPLOYMENT_OPENA4.md`):**

```nginx
# HTTP → HTTPS redirect
server {
    listen 80;
    server_name hyperdashboard-one.de;
    return 301 https://$server_name$request_uri;
}

# HTTPS server block (certificates added in Step 7)
server {
    listen 443 ssl http2;
    server_name hyperdashboard-one.de;

    # SSL placeholders (will be updated by certbot)
    ssl_certificate /etc/letsencrypt/live/hyperdashboard-one.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/hyperdashboard-one.de/privkey.pem;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Main upstream
    upstream dashboard {
        server 127.0.0.1:12349;
    }

    # opena4 upstream (Telegram)
    upstream opena4 {
        server 127.0.0.1:12348;
    }

    # Root path → Dashboard
    location / {
        proxy_pass http://dashboard/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }

    # opena4 path → Telegram agent
    location /opena4/ {
        proxy_pass http://opena4/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    # Telegram webhook endpoint
    location /telegram/webhook/ {
        proxy_pass http://opena4/telegram/webhook/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

✅ **Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/hyperdashboard-one.de /etc/nginx/sites-enabled/
sudo nginx -t
# Should return: nginx: configuration file test is successful
```

---

## Step 7: Install SSL Certificate (Let's Encrypt)

```bash
# BEFORE: Nginx must be running and accessible on port 80
sudo systemctl start nginx

# Install certificate using certbot
sudo certbot certonly --webroot -w /var/www/html -d hyperdashboard-one.de

# Or simpler with nginx plugin:
sudo certbot --nginx -d hyperdashboard-one.de
```

✅ **Verify certificate:**
```bash
sudo ls -la /etc/letsencrypt/live/hyperdashboard-one.de/
# Should show: fullchain.pem, privkey.pem, etc.
```

✅ **Auto-renewal:**
```bash
sudo certbot renew --dry-run
sudo systemctl enable certbot.timer
```

---

## Step 8: Restart Nginx

```bash
# Reload Nginx with SSL config
sudo systemctl reload nginx

# Verify running
sudo systemctl status nginx
```

---

## Step 9: Test External Access

### Local tests (from server):
```bash
# Test HTTPS locally
curl -k https://localhost/health | jq .
curl -k https://localhost/api/agents | jq '.agents | length'
```

### Remote tests (from any internet-connected device):
```bash
# Test HTTPS external
curl https://hyperdashboard-one.de/health | jq .

# Test agent registry
curl https://hyperdashboard-one.de/api/agents | jq '.'

# Test opena4 (Telegram)
curl https://hyperdashboard-one.de/opena4/docs
```

### Browser test:
```
https://hyperdashboard-one.de/static/index.html
```

✅ **Expected:** Dashboard UI loads, no SSL warnings, all agents visible

---

## Step 10: Monitoring & Logs

```bash
# Monitor service status
tail -f /var/www/hyperdashboard/logs/dashboard.nohup.log

# Monitor Nginx access
sudo tail -f /var/log/nginx/access.log

# Monitor Nginx errors
sudo tail -f /var/log/nginx/error.log

# Monitor system
docker ps
docker logs <container-id>
```

---

## Step 11: Setup Health Monitoring (Optional)

```bash
# Create health check cron job
sudo nano /etc/cron.d/elion-health
```

**Add:**
```bash
# Health check every 5 minutes
*/5 * * * * curl -s https://hyperdashboard-one.de/health >> /var/log/elion-health.log 2>&1
```

---

## Step 12: Firewall Configuration (Optional)

```bash
# If using UFW
sudo ufw allow 22/tcp    # SSH (CHANGE PORT IF NOT 22!)
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Verify
sudo ufw status
```

---

## ✅ Final Verification Checklist

- [ ] DNS resolves: `nslookup hyperdashboard-one.de` ✅
- [ ] HTTPS works: `curl -I https://hyperdashboard-one.de` → 200 ✅
- [ ] Dashboard loads: `https://hyperdashboard-one.de/static/index.html` ✅
- [ ] API responds: `https://hyperdashboard-one.de/api/agents` ✅
- [ ] 18 Agents registered ✅
- [ ] SSL certificate valid (no warnings in browser) ✅
- [ ] HTTP redirects to HTTPS ✅
- [ ] Services log to files (no errors) ✅
- [ ] Monitoring cron running ✅

---

## 🎯 Production URLs

| Endpoint | URL | Purpose |
|----------|-----|---------|
| Main Dashboard | `https://hyperdashboard-one.de/static/index.html` | Web UI |
| API Agents | `https://hyperdashboard-one.de/api/agents` | Agent Registry |
| API Status | `https://hyperdashboard-one.de/api/status/all` | System Status |
| Health | `https://hyperdashboard-one.de/health` | Health Check |
| opena4 Swagger | `https://hyperdashboard-one.de/opena4/docs` | Telegram API |
| Telegram Webhook | `https://hyperdashboard-one.de/telegram/webhook/{bot_key}` | Webhook Endpoint |

---

## 🔧 Troubleshooting

**HTTPS Not Working:**
```bash
# Check SSL certificate
sudo certbot certificates

# Check Nginx config
sudo nginx -t

# Check Nginx logs
sudo tail -50 /var/log/nginx/error.log
```

**Services Not Responding:**
```bash
# Check if services running
curl http://127.0.0.1:12349/health
curl http://127.0.0.1:12348/health

# Check logs
tail -50 /var/www/hyperdashboard/logs/dashboard.nohup.log
```

**DNS Not Resolving:**
```bash
# Clear DNS cache
sudo systemctl restart systemd-resolved

# Re-check
nslookup hyperdashboard-one.de +nocmd
```

---

## 📞 Support

- Docs: `docs/DEPLOYMENT_OPENA4.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`
- Architecture: `docs/opena4_telegram.md`

---

**Status:** ✅ Ready for Production  
**Date:** 2025-12-17  
**Last Updated:** 2025-12-17

