# ELION Upgrade Guide v0.6.37

## Executive Summary
Comprehensive upgrade path for OpenWebUI + LocalAgent-Pro integration with advanced security hardening, performance optimization, and agent orchestration.

## 8 Upgrade Phases

### PHASE A: Pre-Deployment Validation
```bash
# 1. Verify environment
python3 --version
docker --version
pip list | grep -E "(openwebui|ollama|pydantic)"

# 2. Backup critical data
cp -r LocalAgent-Pro/config ~/.backup_la_config_v0.6.36
cp ~/.env ~/.env.backup

# 3. Check disk space
df -h | grep -E "^/dev"
```

### PHASE B: Docker Container Preparation
```bash
# 1. Build new image
cd LocalAgent-Pro
docker build -f Dockerfile -t localagent-pro:0.6.37 .

# 2. Tag version
docker tag localagent-pro:0.6.37 localagent-pro:latest

# 3. Verify image
docker images | grep localagent-pro
```

### PHASE C: Database Migration
```bash
# 1. Export knowledge base
python3 tools/knowledge_db_query.py --export knowledge_backup.json

# 2. Run migrations
python3 scripts/migrate_v0.6.36_to_v0.6.37.py

# 3. Validate integrity
python3 tools/knowledge_db_query.py --validate
```

### PHASE D: Service Deployment
```bash
# 1. Stop existing services
docker-compose down
sudo systemctl stop openwebui

# 2. Update docker-compose
cp docker-compose.yml docker-compose.yml.bak
# Apply patches from ELION_PATCH_REPORT.md

# 3. Start new services
docker-compose up -d
sleep 10
docker-compose logs | head -20
```

### PHASE E: Agent Integration
```bash
# 1. Register agents in LocalAgent-Pro
for agent in opena{1..20}; do
    python3 tools/agent_registry.py --register $agent
done

# 2. Verify registrations
python3 tools/agent_registry.py --list

# 3. Test basic connectivity
curl -s http://localhost:5000/api/agents/status | jq .
```

### PHASE F: Security Hardening
```bash
# 1. Enable TLS
certbot certonly --standalone -d yourdomain.com

# 2. Configure SSL in nginx
# Add to nginx config:
# ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

# 3. Restrict API access
iptables -A INPUT -p tcp --dport 5000 -s 127.0.0.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 5000 -j DROP
```

### PHASE G: Performance Tuning
```bash
# 1. Optimize memory
export OLLAMA_MAX_LOADED_MODELS=3
export OPENWEB_MEMORY_LIMIT=8G

# 2. Enable caching layer
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# 3. Benchmark performance
python3 tools/performance_benchmark.py --full
```

### PHASE H: Validation & Troubleshooting
```bash
# 1. Run integration tests
pytest tests/integration/test_elion_*.py -v

# 2. Check logs
docker-compose logs | grep -E "ERROR|WARNING"

# 3. Health check
curl -s http://localhost:3000/api/health | jq .

# 4. Performance metrics
curl -s http://localhost:9090/api/v1/query?query=up | jq .
```

## Rollback Plan

If issues occur:
```bash
# 1. Stop services
docker-compose down

# 2. Restore previous version
docker tag localagent-pro:0.6.36 localagent-pro:latest

# 3. Restore database
mysql < knowledge_backup.sql

# 4. Restart
docker-compose up -d
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Container won't start | Check logs: `docker-compose logs agent` |
| Database migration fails | Run: `python3 scripts/validate_migration.py` |
| API timeouts | Increase timeout: `export API_TIMEOUT=30` |
| Memory errors | Reduce agents: `export OLLAMA_MAX_LOADED_MODELS=2` |

## Support

- Documentation: https://github.com/jokicdanijel/LocalAgent-Pro/wiki
- Issues: https://github.com/jokicdanijel/LocalAgent-Pro/issues
- Contact: danijel@example.com
