#!/usr/bin/env bash
# ELION Hyper-Dashboard – Quick Reference Cheat Sheet

cat << 'EOF'

╔══════════════════════════════════════════════════════════════════════════╗
║                 🚀 ELION Hyper-Dashboard Quick Reference                 ║
╚══════════════════════════════════════════════════════════════════════════╝

📍 PROJECT ROOT: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 TELEGRAM MULTI-BOT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

START SERVICES:
  cd telegram_multi && docker-compose up -d

REGISTER BOTS (localhost):
  bash scripts/register_bots.sh http://127.0.0.1:8000

REGISTER BOTS (production):
  bash scripts/register_bots.sh https://api.your-domain.com

QUICK START:
  bash bin/quickstart_telegram_bots.sh

HEALTH CHECK:
  curl http://127.0.0.1:8000/health | jq .

VIEW LOGS:
  docker-compose logs -f api

STOP SERVICES:
  docker-compose down

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 OPENTELEMETRY TRACING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

START COLLECTOR:
  ./bin/start_tracing_collector.sh

ENABLE TRACING (set in .env):
  OTEL_ENABLED=true
  OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318

VERIFY TRACING:
  python3 tracing/check_tracing.py

ACCESS GRAFANA:
  http://localhost:3000 (admin/admin)

OTEL COLLECTOR PORTS:
  - Port 4317 (gRPC)
  - Port 4318 (HTTP/OTLP)
  - Port 3000 (Grafana UI)

STOP COLLECTOR:
  docker-compose -f docker-compose.otel.yml down

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

UPDATE BOT TOKENS (.env):
  BOT_TOKENS_MAPPING={"bot_key": "YOUR_TOKEN"}

ADMIN KEY (.env):
  ADMIN_KEY=your-secret-key

ENABLE DEBUG LOGS (.env):
  LOG_LEVEL=DEBUG

RELOAD SERVICES:
  cd telegram_multi && docker-compose down && docker-compose up -d

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💾 DATABASE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONNECT TO POSTGRESQL:
  docker-compose exec postgres psql -U telegram_user -d telegram_multi_db

LIST TABLES:
  \dt

QUERY BOTS:
  SELECT * FROM bots;

REDIS CLI:
  docker-compose exec redis redis-cli

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 DOCUMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Documentation Index:
  docs/INDEX.md

Telegram Operations:
  telegram_multi/OPERATIONS_TELEGRAM.md

Tracing Setup Guide:
  docs/TRACING_GUIDE.md

General Operations:
  docs/OPERATIONS.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆘 TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

API WON'T START:
  1. Check logs: docker-compose logs api
  2. Rebuild: docker-compose build --no-cache
  3. Verify port 8000 is free: lsof -i :8000

BOT REGISTRATION FAILS:
  1. Check admin key: grep ADMIN_KEY .env
  2. Check tokens: grep BOT_TOKENS_MAPPING .env
  3. Test API: curl http://127.0.0.1:8000/health

TRACING NOT WORKING:
  1. Check packages: python3 -c "import opentelemetry"
  2. Check endpoint: curl http://127.0.0.1:4318/v1/traces
  3. Check .env: grep OTEL_ENABLED .env

PORT IN USE:
  Kill process: lsof -i :{port} | awk 'NR!=1 {print $2}' | xargs kill -9

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 SERVICE PORTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

telegram_multi API:    8000
PostgreSQL:            5432
Redis:                 6379
OTLP (HTTP):           4318
OTLP (gRPC):           4317
Grafana UI:            3000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ TIP: Save this cheat sheet!
  cat > ~/cheatsheet.txt << 'CHEAT'
  $(cat $0)
  CHEAT

📚 Full docs: docs/INDEX.md

EOF
