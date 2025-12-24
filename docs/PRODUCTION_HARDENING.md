# 🏗️ Production Hardening Guide

**ELION Hyper-Dashboard – Production Deployment**

---

## 📋 Prerequisites

### System Requirements

- **OS:** Ubuntu 22.04 LTS (recommended) or similar
- **CPU:** 4 cores minimum (8+ recommended)
- **RAM:** 8 GB minimum (16+ recommended)
- **Disk:** 50 GB minimum (100+ recommended, SSD)
- **Docker:** 24.0+ with Compose V2
- **Ports:** 80, 443, 5432, 6379, 8200, 9090, 3000

### Domain Setup

1. **Register domain:** hyperdashboard-one.de
2. **DNS A Records:**
   ```
   @ (root)        → Server IP
   www             → Server IP
   ```
3. **Wait for DNS propagation** (check: `dig hyperdashboard-one.de`)

---

## 🚀 Deployment Steps

### Step 1: Clone Repository

```bash
git clone https://github.com/jokicdanijel/Gesamtprojekt-start.git
cd Gesamtprojekt-start
```

### Step 2: Environment Configuration

```bash
# Copy environment template
cp .env.production .env

# Edit with secure values
nano .env
```

**Generate secure secrets:**

```bash
# Database password
openssl rand -base64 32

# Redis password
openssl rand -base64 32

# Auth secret key
openssl rand -hex 64

# Vault root token
openssl rand -base64 32
```

**Fill in .env:**

```bash
DB_PASSWORD=<generated_password>
REDIS_PASSWORD=<generated_password>
AUTH_SECRET_KEY=<generated_key>
VAULT_ROOT_TOKEN=<generated_token>
GRAFANA_PASSWORD=<secure_password>
LETSENCRYPT_EMAIL=your@email.com
```

### Step 3: SSL Certificates (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install -y certbot

# Get certificates
sudo certbot certonly --standalone \
  -d hyperdashboard-one.de \
  -d www.hyperdashboard-one.de \
  --email your@email.com \
  --agree-tos \
  --non-interactive

# Copy to project
sudo cp /etc/letsencrypt/live/hyperdashboard-one.de/fullchain.pem infrastructure/nginx/ssl/
sudo cp /etc/letsencrypt/live/hyperdashboard-one.de/privkey.pem infrastructure/nginx/ssl/

# Set permissions
sudo chmod 644 infrastructure/nginx/ssl/*
```

### Step 4: Deploy with Docker

```bash
# Build and start
make -f Makefile.production deploy

# Or manually:
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d

# Check status
make -f Makefile.production status
```

### Step 5: Verify Deployment

```bash
# Check all services are healthy
docker-compose -f docker-compose.production.yml ps

# Test health endpoints
for port in 12344 12345 12349 12368 12370 12371 12372; do
  curl -f http://localhost:$port/health && echo " ✅" || echo " ❌"
done

# Test website
curl https://hyperdashboard-one.de
```

---

## 🔒 Security Hardening

### 1. Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow essential ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Block direct access to internal ports
sudo ufw deny 5432/tcp   # PostgreSQL
sudo ufw deny 6379/tcp   # Redis
sudo ufw deny 8200/tcp   # Vault

# Check status
sudo ufw status
```

### 2. SSL/TLS Configuration

**Nginx SSL settings** (already in nginx.conf):
- ✅ TLS 1.2 and 1.3 only
- ✅ Strong cipher suites
- ✅ HSTS header
- ✅ Security headers (X-Frame-Options, etc.)

### 3. Rate Limiting

**Already configured in Nginx:**
- API: 10 requests/second
- Login: 5 requests/minute

---

## 📊 Monitoring Setup

### Prometheus

**Access:** http://localhost:9090

**Targets:**
- All agents (health endpoints)
- PostgreSQL exporter
- Redis exporter
- Nginx exporter

### Grafana

**Access:** http://localhost:3000
**Login:** admin / (from .env)

**Dashboards:**
1. System Overview
2. Agent Health
3. Database Performance
4. API Request Rates
5. Error Rates

---

## 🔄 Backup Strategy

### Database Backup (Daily)

```bash
# Manual backup
make -f Makefile.production backup-db

# Automated backup (cron)
0 2 * * * cd /path/to/project && make -f Makefile.production backup-db
```

### Configuration Backup

```bash
# Backup all configs
tar -czf backup_configs_$(date +%Y%m%d).tar.gz \
  .env \
  config/ \
  infrastructure/nginx/ssl/
```

---

## 🛠️ Maintenance

### Update System

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
make -f Makefile.production restart
```

### View Logs

```bash
# All services
make -f Makefile.production logs

# Specific service
make -f Makefile.production logs SERVICE=auth

# Follow logs
docker-compose -f docker-compose.production.yml logs -f auth
```

---

## ⚠️ Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose -f docker-compose.production.yml logs SERVICE_NAME

# Check health
docker-compose -f docker-compose.production.yml ps

# Restart specific service
docker-compose -f docker-compose.production.yml restart SERVICE_NAME
```

### Database Connection Issues

```bash
# Test connection
docker-compose -f docker-compose.production.yml exec postgres psql -U eden_user -d eden -c "SELECT 1;"

# Check PostgreSQL logs
docker-compose -f docker-compose.production.yml logs postgres
```

---

## ✅ Production Checklist

- [ ] ✅ All environment variables set (no defaults)
- [ ] ✅ Strong passwords for all services
- [ ] ✅ SSL certificates installed and valid
- [ ] ✅ Firewall configured
- [ ] ✅ All services healthy
- [ ] ✅ Monitoring dashboards accessible
- [ ] ✅ Backup strategy configured
- [ ] ✅ DNS configured correctly
- [ ] ✅ HTTPS redirect working
- [ ] ✅ Rate limiting active
- [ ] ✅ Health checks passing

---

**Production hardening complete!** 🎉

System is now ready for real users.
