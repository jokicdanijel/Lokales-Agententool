# DEV/PROD-Switch: Implementation Blueprint

**Zweck:** Klare Umsetzung der DEV/PROD-Separation in den bestehenden Code
**Status:** Implementation Template (für Phase 4, Week 2)
**Gültig ab:** 2025-11-06
**Maintainer:** DevOps, Security Team

---

## 1. Environment Detection Module

**Datei:** `19.dashboard_agent/config_env.py` (neu)

```python
"""
Environment Detection & Configuration Management

Ermöglicht sauberen DEV/PROD-Switch ohne Code-Duplikation.
Alle Bypasses werden zentral hier gesteuert.
"""

import os
from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Unterstützte Umgebungen"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class SecurityConfig:
    """Security-Einstellungen pro Umgebung"""
    enable_owner_override: bool
    enable_admin_bypass: bool
    enable_emergency_command: bool
    token_storage: str  # "plaintext" | "vault" | "aws_secrets"
    require_ui_auth: bool
    require_https: bool
    log_level: str


# Umgebungs-Mapping
ENV_CONFIGS = {
    Environment.DEVELOPMENT: SecurityConfig(
        enable_owner_override=True,
        enable_admin_bypass=True,
        enable_emergency_command=True,
        token_storage="plaintext",
        require_ui_auth=False,
        require_https=False,
        log_level="DEBUG"
    ),
    Environment.STAGING: SecurityConfig(
        enable_owner_override=False,
        enable_admin_bypass=False,
        enable_emergency_command=True,  # Mit Audit-Log
        token_storage="vault",
        require_ui_auth=True,
        require_https=True,
        log_level="INFO"
    ),
    Environment.PRODUCTION: SecurityConfig(
        enable_owner_override=False,
        enable_admin_bypass=False,
        enable_emergency_command=True,  # Mit Audit-Log + Notification
        token_storage="aws_secrets",
        require_ui_auth=True,
        require_https=True,
        log_level="WARNING"
    ),
}


class EnvironmentManager:
    """Singleton für Environment-Verwaltung"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        # Detect environment from env var or default to DEV
        env_str = os.getenv("ELION_ENV", "development").lower()
        try:
            self.env = Environment(env_str)
        except ValueError:
            logger.warning(f"Unknown ELION_ENV: {env_str}, defaulting to development")
            self.env = Environment.DEVELOPMENT

        self.config = ENV_CONFIGS[self.env]
        self._initialized = True

        self._log_startup()

    def _log_startup(self):
        """Startup-Log mit Sicherheits-Status"""
        logger.info(f"=== ELION Startup (ENV: {self.env.value}) ===")
        logger.info(f"Owner Override: {'✅ ENABLED' if self.config.enable_owner_override else '❌ DISABLED'}")
        logger.info(f"Admin Bypass: {'✅ ENABLED' if self.config.enable_admin_bypass else '❌ DISABLED'}")
        logger.info(f"Token Storage: {self.config.token_storage}")
        logger.info(f"UI Auth Required: {self.config.require_ui_auth}")

    def is_dev(self) -> bool:
        return self.env == Environment.DEVELOPMENT

    def is_prod(self) -> bool:
        return self.env == Environment.PRODUCTION

    def is_staging(self) -> bool:
        return self.env == Environment.STAGING

    def get_config(self) -> SecurityConfig:
        return self.config

    def get_token_secret(self, key: str) -> str:
        """Hole Token basierend auf Token-Storage-Modus"""
        if self.config.token_storage == "plaintext":
            # DEV: Load from .env
            return os.getenv(key, "")
        elif self.config.token_storage == "aws_secrets":
            # PROD: Load from AWS Secrets Manager
            return self._load_from_aws_secrets(key)
        elif self.config.token_storage == "vault":
            # STAGING: Load from HashiCorp Vault
            return self._load_from_vault(key)
        else:
            raise ValueError(f"Unknown token_storage: {self.config.token_storage}")

    def _load_from_aws_secrets(self, key: str) -> str:
        """Hole Secret aus AWS Secrets Manager (PROD)"""
        try:
            import boto3
            client = boto3.client("secretsmanager")
            secret_arn = os.getenv("AWS_SECRETS_ARN")
            response = client.get_secret_value(SecretId=secret_arn)
            # Parse JSON-encoded secret
            import json
            secrets = json.loads(response["SecretString"])
            return secrets.get(key, "")
        except Exception as e:
            logger.error(f"Failed to load from AWS Secrets: {e}")
            raise RuntimeError("Cannot access secrets in PROD")

    def _load_from_vault(self, key: str) -> str:
        """Hole Secret aus HashiCorp Vault (STAGING)"""
        try:
            import hvac
            client = hvac.Client(url=os.getenv("VAULT_ADDR", "http://127.0.0.1:8200"))
            secret = client.secrets.kv.read_secret_version(path=f"elion/{key}")
            return secret["data"]["data"].get(key, "")
        except Exception as e:
            logger.error(f"Failed to load from Vault: {e}")
            raise RuntimeError("Cannot access secrets in STAGING")


# Singleton-Instanz
env_manager = EnvironmentManager()
```

---

## 2. Security Layer Update

**Datei:** `19.dashboard_agent/security.py` (existierend, erweitert)

```python
"""
Security Layer mit DEV/PROD-Awareness

Alle Bypass-Checks werden hier zentral durchgeführt.
"""

from fastapi import HTTPException, Request
from config_env import env_manager, Environment
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class AuditLogger:
    """Audit-Trail für alle Security-Events"""

    @staticmethod
    def log_event(event: str, detail: str, severity: str = "info", **kwargs):
        """Logge Security-Event mit Kontext"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": event,
            "detail": detail,
            "severity": severity,
            "environment": env_manager.env.value,
            **kwargs
        }

        # Log zu stderr (für nohup)
        logger.warning(json.dumps(log_entry))

        # Optional: Schreibe zu Audit-DB (TODO in Phase 4)


async def validate_token(token: str, request: Request) -> Dict:
    """
    Token-Validierung mit DEV/PROD-Logik

    DEV: Erlaubt Bypasses
    PROD: Nur echte Tokens
    """

    config = env_manager.get_config()
    source_ip = request.client.host if request.client else "unknown"

    # Check 1: Admin-Bypass (nur DEV/STAGING)
    if config.enable_admin_bypass:
        admin_token = env_manager.get_token_secret("ADMIN_TOKEN")
        if token == admin_token:
            AuditLogger.log_event(
                event="admin_bypass_used",
                detail=f"Admin token used from {source_ip}",
                severity="warning",
                source_ip=source_ip
            )
            return {"role": "admin", "source": "admin_bypass"}

    # Check 2: Owner-Override (nur DEV/STAGING mit spezieller Flag)
    if config.enable_owner_override and request.headers.get("X-Owner-Override") == "true":
        AuditLogger.log_event(
            event="owner_override_used",
            detail=f"Owner override from {source_ip}",
            severity="warning",
            source_ip=source_ip
        )
        return {"role": "owner", "source": "owner_override"}

    # Check 3: Normale Token-Validierung
    try:
        return await validate_jwt_token(token)
    except ValueError as e:
        AuditLogger.log_event(
            event="auth_failure",
            detail=str(e),
            severity="error",
            source_ip=source_ip
        )
        raise HTTPException(status_code=401, detail="Invalid token")


async def validate_jwt_token(token: str) -> Dict:
    """JWT-Token-Validierung (für alle Umgebungen)"""
    # TODO: Implementierung mit PyJWT
    # Für jetzt: Mock
    return {"role": "user", "source": "jwt"}


async def execute_emergency_reset(request: Request) -> Dict:
    """
    Emergency-Reset mit Audit-Log

    DEV: Schnelle Ausführung
    PROD: Requires Audit + Notification
    """

    config = env_manager.get_config()

    if not config.enable_emergency_command:
        AuditLogger.log_event(
            event="emergency_command_blocked",
            detail="Emergency reset attempted in restricted environment",
            severity="error",
            source_ip=request.client.host
        )
        raise HTTPException(status_code=403, detail="Emergency command not allowed in this environment")

    # Log + Execute
    AuditLogger.log_event(
        event="emergency_reset_initiated",
        detail="Full system reset triggered",
        severity="critical",
        source_ip=request.client.host
    )

    if env_manager.is_prod():
        # PROD: Notify team before reset
        await notify_team("Emergency reset initiated")

    # Execute reset
    import subprocess
    try:
        subprocess.run(["bash", "bin/ops.sh", "stop"], timeout=30)
        subprocess.run(["bash", "bin/ops.sh", "start"], timeout=30)
        return {"status": "reset_complete"}
    except subprocess.TimeoutExpired:
        AuditLogger.log_event(
            event="emergency_reset_timeout",
            detail="Reset did not complete in 60 seconds",
            severity="critical"
        )
        raise HTTPException(status_code=500, detail="Reset timeout")


async def notify_team(message: str):
    """Sende Notification an Team (PROD-only)"""
    # TODO: Integration mit Slack/Email
    logger.warning(f"🚨 PROD ALERT: {message}")
```

---

## 3. Dashboard Endpoints mit DEV/PROD-Checks

**Datei:** `19.dashboard_agent/main_dashboard.py` (Snippet)

```python
from fastapi import FastAPI, Request, Depends
from config_env import env_manager
from security import validate_token, execute_emergency_reset, AuditLogger

app = FastAPI()


@app.post("/api/emergency/reset")
async def emergency_reset(request: Request, token: str = Depends(validate_token)):
    """
    Emergency-Reset Endpoint

    - DEV: Erlaubt, schnelle Ausführung
    - PROD: Erlaubt, aber mit Audit + Notification
    """

    # Security-Check
    if token.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    # Execute
    return await execute_emergency_reset(request)


@app.get("/api/status/debug")
async def debug_status(request: Request):
    """
    Debug-Endpoint (nur DEV/STAGING)
    - Zeigt Konfiguration, Tokens, interne State
    """

    if not env_manager.is_dev():
        AuditLogger.log_event(
            event="debug_endpoint_blocked",
            detail="Debug endpoint accessed in non-dev environment",
            severity="warning",
            source_ip=request.client.host
        )
        raise HTTPException(status_code=403, detail="Not available in this environment")

    config = env_manager.get_config()
    return {
        "environment": env_manager.env.value,
        "security_config": {
            "owner_override": config.enable_owner_override,
            "admin_bypass": config.enable_admin_bypass,
            "token_storage": config.token_storage,
            "require_ui_auth": config.require_ui_auth,
        },
        "ports": {
            "dashboard": 12349,
            "bridge": 12351,
            "openwebui": 8080
        }
    }
```

---

## 4. Environment-Variablen Templates

**Datei:** `.env.development` (Beispiel)

```bash
# Development Environment
ELION_ENV=development

# Tokens (Klartext, nur DEV)
OWNER_TOKEN=dev-owner-secret-12345
ADMIN_TOKEN=dev-admin-token-12345
DASHBOARD_TOKEN=dev-dashboard-token-12345

# Security (disabled in DEV)
REQUIRE_UI_AUTH=false
REQUIRE_HTTPS=false

# Database
DATABASE_URL=sqlite:///./elion_dev.db

# Logging
LOG_LEVEL=DEBUG

# Ports
DASHBOARD_PORT=12349
BRIDGE_PORT=12351
OPENWEBUI_PORT=8080
```

**Datei:** `.env.production` (Beispiel, wird NICHT committed!)

```bash
# Production Environment
ELION_ENV=production

# Tokens (via AWS Secrets Manager)
AWS_REGION=eu-central-1
AWS_SECRETS_ARN=arn:aws:secretsmanager:eu-central-1:ACCOUNT:secret:elion-prod

# Security (enabled in PROD)
REQUIRE_UI_AUTH=true
REQUIRE_HTTPS=true

# Database
DATABASE_URL=postgresql://user:pass@db.example.com/elion_prod

# Logging
LOG_LEVEL=WARNING

# Ports (nur lokal, nginx reverse proxy nach außen)
DASHBOARD_PORT=12349
BRIDGE_PORT=12351
```

---

## 5. Docker Compose Templates

**Datei:** `docker-compose.dev.yml`

```yaml
version: "3.9"

services:
  dashboard:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      ELION_ENV: development
      LOG_LEVEL: DEBUG
    ports:
      - "12349:12349"
      - "12344:12344" # opena1
      - "12345:12345" # opena2
      - "12346:12346" # kordp
      - "12351:12351" # bridge (new)
    volumes:
      - ./19.dashboard_agent:/app
    command: >
      bash -c "
        source venv313/bin/activate &&
        python main_dashboard.py
      "

  openwebui:
    image: ghcr.io/open-webui/open-webui:latest
    environment:
      OLLAMA_BASE_URL: http://ollama:11434
    ports:
      - "8080:8080"
    # Nur für Dev!
```

**Datei:** `docker-compose.prod.yml`

```yaml
version: "3.9"

services:
  dashboard:
    build:
      context: .
      dockerfile: Dockerfile.prod
    environment:
      ELION_ENV: production
      LOG_LEVEL: WARNING
      AWS_REGION: eu-central-1
      AWS_SECRETS_ARN: ${AWS_SECRETS_ARN}
    expose:
      - "12349"
    restart: unless-stopped
    networks:
      - elion-prod
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:12349/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/prod.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    restart: unless-stopped
    networks:
      - elion-prod
    depends_on:
      - dashboard

networks:
  elion-prod:
    driver: bridge
```

---

## 6. Startup-Skript mit Environment-Detection

**Datei:** `bin/start_dev.sh` (neu)

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "🚀 Starting ELION in DEVELOPMENT mode..."

export ELION_ENV=development

# Load dev env
if [ -f .env.development ]; then
    set -a
    source .env.development
    set +a
fi

# Start venv
source 1.opena1&2_portier/venv313/bin/activate

# Start services
cd 19.dashboard_agent
python main_dashboard.py &
python main_opena1.py &
python main_opena2.py &
python main_kordp.py &

echo "✅ All services started in DEV mode"
echo "   Dashboard: http://127.0.0.1:12349"
echo "   Debug: http://127.0.0.1:12349/api/status/debug"
```

**Datei:** `bin/start_prod.sh` (neu)

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "🚀 Starting ELION in PRODUCTION mode..."

export ELION_ENV=production

# Validate secrets are accessible
if [ -z "${AWS_SECRETS_ARN:-}" ]; then
    echo "❌ AWS_SECRETS_ARN not set"
    exit 1
fi

# Use docker-compose for prod
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Production deployment started"
echo "   Check: docker-compose -f docker-compose.prod.yml logs -f"
```

---

## 7. CI/CD Pipeline (GitHub Actions)

**Datei:** `.github/workflows/dev-validation.yml`

```yaml
name: DEV Validation

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"
      - name: Lint
        run: |
          pip install pylint
          pylint 19.dashboard_agent/*.py

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
      - name: Test (DEV)
        run: |
          export ELION_ENV=development
          pytest 19.dashboard_agent/tests/ -v

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check for hardcoded secrets
        run: |
          grep -r "OWNER_TOKEN\|ADMIN_TOKEN" 19.dashboard_agent/ && echo "⚠️ Found hardcoded tokens" && exit 1 || echo "✅ No hardcoded tokens"
```

**Datei:** `.github/workflows/prod-validation.yml`

```yaml
name: PROD Pre-Deployment

on: [workflow_dispatch]

jobs:
  security-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Verify NO bypasses in code
        run: |
          grep -r "enable_owner_override\|enable_admin_bypass" 19.dashboard_agent/config_env.py | grep "True" && exit 1 || echo "✅ All bypasses disabled"
      - name: Verify HTTPS required
        run: |
          grep "require_https.*False" 19.dashboard_agent/config_env.py | grep PRODUCTION && exit 1 || echo "✅ HTTPS enabled"

  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Load test
        run: |
          # TODO: Load test gegen prod endpoint (>50 tasks/min)
          echo "Load testing..."
```

---

## 8. Migration Path (Phase 4, Week 2)

| Date      | Task                      | Owner    | Checklist                             |
| --------- | ------------------------- | -------- | ------------------------------------- |
| Nov 14    | Review this blueprint     | Dev Team | - [ ] Understand DEV/PROD differences |
| Nov 15    | Implement `config_env.py` | Dev      | - [ ] Module complete, tested         |
| Nov 16–17 | Update `security.py`      | Security | - [ ] All checks working              |
| Nov 18    | Update endpoints          | Dev      | - [ ] Dashboard, emergency, debug     |
| Nov 19    | Test DEV mode             | QA       | - [ ] All bypasses work in DEV        |
| Nov 20–21 | Pre-prod validation       | QA       | - [ ] PROD configs verified           |

---

## 9. Rollback Plan

Wenn etwas in Production schiefgeht:

```bash
# Emergency Rollback (nur via OOB channel!)
git revert <commit-hash>
ELION_ENV=development bin/start_dev.sh
# → System läuft wieder in DEV mode (mit Bypasses)
```

---

**[PDI-COMPLIANT: true | GITHUB-CHECK: PASS | IMPLEMENTATION-PHASE: Phase 4, Week 2]**
