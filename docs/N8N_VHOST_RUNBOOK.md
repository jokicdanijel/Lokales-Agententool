# N8N vHost Runbook (n8n.hyperdashboard-one.de)

## Goal
Ensure the subdomain routes to n8n (not opena20), so POST webhooks work.

## Install
```bash
chmod +x scripts/nginx/install_n8n_vhost.sh scripts/nginx/verify_n8n_routing.sh
./scripts/nginx/install_n8n_vhost.sh
./scripts/nginx/verify_n8n_routing.sh
```

## Upstream Selection

Edit: `infrastructure/nginx/vhosts/n8n.hyperdashboard-one.de.conf`

Choose ONE:

- **Host**: `set $n8n_upstream "http://127.0.0.1:5678";` ✅ (CURRENT)
- **Docker**: `set $n8n_upstream "http://n8n:5678";`
- **Remote**: `set $n8n_upstream "http://10.0.0.10:5678";`

## Success Criteria

- `GET https://n8n.hyperdashboard-one.de/` does NOT return `<h1>opena20</h1>`
- `POST https://n8n.hyperdashboard-one.de/webhook/...` does NOT return `501`

## Troubleshooting

### Still routing to opena20?

```bash
# Check nginx site is enabled
ls -la /etc/nginx/sites-enabled/n8n.hyperdashboard-one.de

# Check nginx config syntax
sudo nginx -t

# Check n8n is listening
ss -tlnp | grep 5678

# Reload nginx
sudo systemctl reload nginx
```

### POST returns 501?

- n8n not running: `docker ps | grep n8n` or `systemctl status n8n`
- Wrong upstream: verify `set $n8n_upstream` matches actual n8n location
- Firewall blocking: check local firewall rules

## TLS Options

Edit: `infrastructure/nginx/vhosts/n8n.hyperdashboard-one.de.conf`

**Option 1: Let's Encrypt (recommended for public)**
```nginx
ssl_certificate     /etc/letsencrypt/live/n8n.hyperdashboard-one.de/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/n8n.hyperdashboard-one.de/privkey.pem;
```

**Option 2: Self-signed (debug only, requires `curl -k`)**
```nginx
ssl_certificate     /etc/ssl/certs/n8n.hyperdashboard-one.de.crt;
ssl_certificate_key /etc/ssl/private/n8n.hyperdashboard-one.de.key;
```

## CI/CD Integration

This vHost is part of PORTIER 3.0 baseline infrastructure. Changes must pass:

```bash
./bin/verify_baseline_and_discovery.sh
```
