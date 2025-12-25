#!/usr/b# mcp_server/.env.example
# Template file for MCP server configuration used by preflight checks and local setup.
# Copy to .env and fill with real secrets (DO NOT COMMIT .env).

# Server settings
MCP_HOST=127.0.0.1
MCP_PORT=12350

# Authentication
MCP_BEARER_TOKEN=your-secure-token-here

# Dashboard (placeholders)
DASHBOARD_ADMIN_TOKEN=your-dashboard-admin-token
BEARER_TOKEN=your-global-bearer-token

# Agent ports (examples; adjust per deployment)
OPENA1_PORT=12344
OPENA2_PORT=12345
OPENA3_PORT=12347

# Optional integration keys (placeholders)
OPENAI_API_KEY=sk-REPLACE_ME

# GitHub Copilot MCP API Configuration
# For MCP server integration with GitHub Copilot API
# Endpoint: https://api.githubcopilot.com/mcp/
GITHUB_COPILOT_API_KEY=your-github-copilot-api-key-here
GITHUB_COPILOT_MCP_ENDPOINT=https://api.githubcopilot.com/mcp/

# Environment
ENV=development
DEBUG=false

# Notes:
# - This file is intentionally minimal and contains placeholders only.
# - Never put real secrets into repository files; copy to .env for local runs.
# ELION MCP Server Konfiguration
# Kopiere diese Datei zu .env und passe die Werte an

# OpenAI API Key (optional, für Vector Store)
OPENAI_API_KEY=sk-your-key-here

# Vector Store ID (optional, für Dokumenten-Suche)
VECTOR_STORE_ID=vs_your_store_id

# Basis-URL für Zitationen
MCP_BASE_URL=https://hyperdashboard-one.de

# Server-Konfiguration
MCP_HOST=0.0.0.0
MCP_PORT=12350

# Debug-Modus
N8N_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiMjFhMTk1NS0wMTFkLTQzOTctYmNiMi03YTlmY2M2ZDkwNjkiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY1ODg5NjE1fQ.80vjxY8lSIr-cOsXMhNOnCwd28YcsH4xcIGbmrBl5As
CHATGPT_API_KEY=api key n8n &chatgpt!
MCP_DEBUG=false

# Bearer Token für Authentifizierung (optional)
MCP_BEARER_TOKEN=your-secure-token-here
# SCTA Configuration Template
# Copy to .env and fill with actual secrets
# DO NOT commit .env file!

# === Secrets (MUST be set in production) ===
DASHBOARD_ADMIN_TOKEN=your_secure_token_here
ADMIN_USERNAME=admin
# Strong password for Dashboard Admin (DO NOT COMMIT)
ADMIN_PASSWORD=change_me_in_production

# Bot 1: ELION Telegram Agent @elion_tgap_bot (opena4)
TELEGRAM_BOT_TOKEN=8521041310:AAGAQpvjUH-huQDihQF-iJTzPn_f1L8BLS0
# Bot 2: ELION Notification Bot @elion_notify_bot (opena7)
TELEGRAM_BOT_TOKEN_NOTIFY=8559430186:AAHvPZMA2TTBT8-qU5eUMb_TdbIs2uQzye0

TELEGRAM_WEBHOOK_SECRET=your_webhook_secret_here
TELEGRAM_ALLOWED_USERS=7664467819

# === Infrastructure (defaults provided) ===
SCTA_API_HOST=127.0.0.1
SCTA_API_PORT=3000
SCTA_ORCHESTRATOR_PORT=5000
SCTA_WORKERS_BASE_PORT=5001

# opena1 (Koordinator) Configuration
OPENA1_PORT=12344
OPENA1_BEARER_TOKEN=sk_opena1_coord_12344_strict_v1
OPENAI_MODEL_OPENA1=gpt-4o-mini

# opena2 (Archivator) Configuration
OPENA2_PORT=12345
OPENA2_BEARER_TOKEN=sk_opena2_arch_12345_strict_v1
OPENAI_MODEL_OPENA2=gpt-4o-mini

# === Database ===
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=scta_user
POSTGRES_PASSWORD=change_me_in_production
POSTGRES_DB=scta_db

# === Redis ===
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# === Qdrant (optional) ===
QDRANT_HOST=localhost
QDRANT_PORT=6333

# === Environment ===
ENV=development
LOG_LEVEL=INFO
DEBUG=false

# === OpenTelemetry (optional) ===
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://localhost:4318/v1/traces
OTEL_EXPORTER_OTLP_LOGS_ENDPOINT=http://localhost:4318/v1/logs
OTEL_SERVICE_NAME=elion-portier
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false

# PORTIER 3.0 Environment Configuration
# Generated: 2025-12-03 22:03:30 UTC
# Auto-sync: bin/sync_env.sh

# Dashboard Admin Token
DASHBOARD_ADMIN_TOKEN=baf54565-9eb3-4349-bdec-bcaf93b16977
BEARER_TOKEN=c899b90d-faf8-485b-afa4-078357cf5313

# OpenAI API Keys (opena1 + opena2 + opena20)
OPENAI_API_KEY_OPENA1=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
OPENAI_API_KEY_OPENA2=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
OPENAI_API_KEY_OPENA20=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
OPENAI_API_KEY_OPENA3=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
OPENAI_API_KEY_OPENA4=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
OPENAI_API_KEY_OPENA5=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
OPENAI_API_KEY_OPENA6=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
OPENAI_API_KEY_OPENA7=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
OPENAI_API_KEY_OPENA8=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
OPENAI_API_KEY_OPENA9=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
OPENAI_API_KEY_OPENA10=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
OPENAI_API_KEY_OPENA11=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
OPENAI_API_KEY_OPENA12=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
OPENAI_API_KEY_OPENA13=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
OPENAI_API_KEY_OPENA14=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
OPENAI_API_KEY_OPENA15=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
OPENAI_API_KEY_OPENA16=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
OPENAI_API_KEY_OPENA17=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
OPENAI_API_KEY_OPENA18=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
OPENAI_API_KEY_OPENA19=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
OPENAI_API_KEY_OPENA20=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
OPENAI_API_KEY_

# n8n key mail
N8N_MAIL_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiMjFhMTk1NS0wMTFkLTQzOTctYmNiMi03YTlmY2M2ZDkwNjkiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY1NDM4NTQ2fQ.04eW-SG7ov8AAhVZJgHzqPI9RPteD7fTqxRf0iv2Q4M

# Default OpenAI Key (für Skripte die OPENAI_API_KEY erwarten)
OPENAI_API_KEY=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

# Port Configuration
DASHBOARD_PORT=12349
OPENA1_PORT=12344
OPENA2_PORT=12345
OPENA3_PORT=12347
OPENA15_PORT=12360

# Service URLs
DASHBOARD_URL=http://127.0.0.1:12349
ARCHIVATOR_URL=http://127.0.0.1:12345

# Logging
LOG_LEVEL=INFO
OPENWEBUI_URL=http://127.0.0.1:3000

# ============================================================================
# ComfyUI API Configuration
# ============================================================================
COMFYUI_URL=http://77.42.23.168:8188
COMFYUI_API_KEY=comfyui-255052bc58046efdeb77d6ec88b4c81aebf60fd3ff9b810d522a4ed33ab0eff6
COMFYUI_WS_URL=ws://77.42.23.168:8188/ws
COMFYUI_UPLOAD_URL=http://77.42.23.168:8188/upload/image
COMFYUI_PROMPT_URL=http://77.42.23.168:8188/prompt
COMFYUI_HISTORY_URL=http://77.42.23.168:8188/history
COMFYUI_VIEW_URL=http://77.42.23.168:8188/view
COMFYUI_SYSTEM_STATS_URL=http://77.42.23.168:8188/system_stats
# ComfyUI Version: 0.3.76 (CPU Mode - kein GPU auf Server)

# GitHub Personal Access Token (für Git-Push/API-Zugriff)
GITHUB_TOKEN=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

# ============================================================================
# OpenTelemetry Tracing Configuration (AI Toolkit)
# ============================================================================
# AI Toolkit OTLP Endpoints (default: localhost)
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://localhost:4318/v1/traces
OTEL_EXPORTER_OTLP_LOGS_ENDPOINT=http://localhost:4318/v1/logs

# Enable GenAI message content capture in traces (optional)
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true

# Service name (set per agent, e.g., opena1, opena2, etc.)
# SERVICE_NAME=opena1


# Agent aktivieren/deaktivieren
AGENT_ENABLED=true

# HTML-Profil automatisch generieren
AUTO_GENERATE_HTML=true

# Optionale Umgebungsvariablen
# DEBUG_MODE=false
# LOG_LEVEL=INFO

/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier


# n8n ssh
: ssh-keygen -t ed25519"
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCikE126/l+62yWtu+9BqlepNJxWv2dczjj+0PRQuYVowAAAJjvbCLz72wi
8wAAAAtzc2gtZWQyNTUxOQAAACCikE126/l+62yWtu+9BqlepNJxWv2dczjj+0PRQuYVow
AAAED5jCLm79CXPH3QpQbMwEIa4mkT6mvU904opEiInkPiiKKQTXbr+X7rbJa2770GqV6k
0nFa/Z1zOOP7Q9FC5hWjAAAAE3h4am9raWMwMUBnbWFpbC5jb20BAg==
