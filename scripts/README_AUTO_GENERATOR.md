# PORTIER 3.0 Auto-Generator

**🚀 Enterprise Agent Generator mit CI/CD Pipeline**

## 🎯 Überblick

Der PORTIER 3.0 Auto-Generator erstellt vollständige Enterprise-ready Agenten mit:

- **FastAPI Backend** mit Health Checks
- **HTML Dashboard** mit Dark Theme
- **Docker Container** mit Security Hardening
- **CI/CD Pipeline** mit GitHub Actions
- **Comprehensive Testing** mit pytest
- **Code Quality** mit flake8, black, bandit
- **PORTIER 3.0 Compliance** mit Option-2-Flow

## 🚀 Quick Start

```bash
# Generator ausführbar machen
chmod +x scripts/create-agent

# Neuen Agent erstellen (mit CI/CD)
./scripts/create-agent --name opena5_vscode --port 12350 --specialization development --ci

# Agent starten
cd opena5_vscode
python3 main.py

# Dashboard öffnen
open http://127.0.0.1:12350/
```

## ⚙️ Usage

### Basis Agent (ohne CI/CD)
```bash
./scripts/create-agent --name opena8_whatsapp --port 12353 --specialization messaging
```

### Enterprise Agent (mit CI/CD Pipeline)
```bash
./scripts/create-agent --name opena9_phone --port 12354 --specialization telephony --ci
```

### Parameter

| Parameter | Beschreibung | Beispiel |
|-----------|-------------|----------|
| `--name` | Agent Name (openaX_description) | `opena5_vscode` |
| `--port` | Port (12344-12399) | `12350` |
| `--specialization` | Agent Spezialisierung | `development` |
| `--ci` | Include CI/CD Pipeline | Flag |

## 📁 Generierte Struktur

```
openaX_example/
├── main.py                 # ✅ FastAPI Agent
├── requirements.txt        # ✅ Python Dependencies
├── Dockerfile              # ✅ Container Definition
├── .version                # ✅ Version Management
├── README.md               # ✅ Documentation
├── html/
│   └── index.html          # ✅ Dashboard UI
├── logs/                   # ✅ Log Directory
├── tests/
│   └── test_agent.py       # ✅ Unit Tests
└── .github/
    └── workflows/
        └── ci_cd.yml       # ✅ CI/CD Pipeline
```

## 🧪 Features

### ✅ **FastAPI Backend**
- Health Check (`/health`)
- Status Reporting (`/status`)
- Command Execution (`/command`)
- Metrics Export (`/metrics`)
- Log Access (`/logs`)
- HTML Dashboard (`/`)

### ✅ **HTML Dashboard**
- **Dark Theme** Enterprise UI
- **Real-time** Health Monitoring
- **Interactive** Command Execution
- **Responsive** Design
- **Auto-refresh** Status

### ✅ **Docker Container**
- **Python 3.13** Base Image
- **Non-root User** Security
- **Health Checks** Built-in
- **Multi-stage** Build
- **Production** Ready

### ✅ **CI/CD Pipeline**
- **Security Scanning** (Trivy, Bandit)
- **Code Quality** (flake8, black)
- **Unit Testing** (pytest)
- **Docker Build** & Push
- **Blue-Green Deploy** Strategy
- **Health Verification** Post-deploy

### ✅ **PORTIER 3.0 Compliance**
- **Port Range** 12344-12399
- **Bearer Auth** Ready
- **Structured Logging** JSON Format
- **Option-2-Flow** Compatible
- **Enterprise Standards** Built-in

## 🎆 CI/CD Pipeline

Wenn `--ci` Flag gesetzt:

```yaml
# Automatischer Workflow
1. 🛡️ Security Scan
2. 🔍 Code Quality (lint, format, type)
3. 🧪 Unit Tests
4. 📦 Docker Build & Push
5. 🎭 Deploy to Staging
6. 🔗 Integration Tests
7. 🏭 Blue-Green Production Deploy
8. 🩺 Post-Deploy Verification
9. 🧹 Cleanup
```

### GitHub Secrets (Required für CI/CD)

```bash
# Repository Secrets
DEPLOY_HOST=production-server.com
DEPLOY_USER=deploy
DEPLOY_KEY=<ssh-private-key>
STAGING_HOST=staging-server.com
STAGING_USER=deploy
STAGING_KEY=<ssh-private-key>
BEARER_TOKEN=<portier-bearer-token>
TELEGRAM_TOKEN=<agent-specific-token>
```

## 🚀 Deployment

### Lokal
```bash
python3 main.py
```

### Docker
```bash
docker build -t openaX_example .
docker run -d -p 12350:12350 openaX_example
```

### Production (via CI/CD)
```bash
# Push to main branch triggers automatic deployment
git push origin main
```

## 🔗 Integration

### PORTIER Stack Registration

Generierte Agenten registrieren sich automatisch:

```python
# Auto-Registration bei Agent Start
register_agent({
    "name": "openaX_example",
    "port": 12350,
    "specialization": "development",
    "capabilities": ["health_check", "command_execution"],
    "endpoints": ["/health", "/status", "/command"]
})
```

### Dashboard Integration

Agenten erscheinen automatisch im HYPER-DASHBOARD:

- 🩺 Health Status
- 📈 Performance Metrics
- 🔗 Quick Actions
- 📋 Log Access

## 🔧 Development

### Testing
```bash
cd openaX_example
pytest -v
flake8 .
black --check .
```

### Local Development
```bash
# Auto-reload für Development
uvicorn main:app --host 127.0.0.1 --port 12350 --reload
```

### Code Quality
```bash
# Format Code
black . --line-length 120

# Lint Code  
flake8 . --max-line-length=120

# Security Audit
bandit -r .
```

## 🎯 Examples

### Create Development Agent
```bash
./scripts/create-agent \
  --name opena5_vscode \
  --port 12350 \
  --specialization development \
  --ci
```

### Create Mobile Agent
```bash
./scripts/create-agent \
  --name opena8_whatsapp \
  --port 12353 \
  --specialization mobile_messaging \
  --ci
```

### Create Browser Agent
```bash
./scripts/create-agent \
  --name opena6_browser \
  --port 12351 \
  --specialization browser_automation \
  --ci
```

## 🐛 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| Port already in use | Use different port in range 12344-12399 |
| Permission denied | Run `chmod +x scripts/create-agent` |
| Invalid agent name | Use format `openaX_description` |
| CI/CD secrets missing | Add required secrets to GitHub repo |

### Debug

```bash
# Check generator
python3 scripts/create-agent --help

# Test generated agent
cd openaX_example
python3 main.py
curl http://127.0.0.1:12350/health

# Check logs
tail -f logs/agent.log
```

---

**🎆 PORTIER 3.0 Auto-Generator - Enterprise Ready!**  
**Generated:** 29. November 2025  
**Status:** ✅ Production Ready