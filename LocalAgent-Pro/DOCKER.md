# 🐳 LocalAgent-Pro Docker Deployment

Vollständiges Docker-Setup für LocalAgent-Pro mit Ollama, Prometheus und Grafana.

## 🚀 Quick Start

### Minimal Setup (nur LocalAgent-Pro + Ollama)

```bash
cd LocalAgent-Pro
docker-compose up -d
```

### Mit Monitoring (Prometheus + Grafana)

```bash
docker-compose --profile monitoring up -d
```

## 📋 Services

| Service | Port | Description |
|---------|------|-------------|
| **localagent-pro** | 8001 | AI Agent Server |
| **ollama** | 11434 | LLM Backend |
| **prometheus** | 9090 | Metrics Collection (optional) |
| **grafana** | 3001 | Dashboard (optional) |

## 🔧 Konfiguration

### Environment Variables

Erstelle `.env` Datei für Custom-Config:

```bash
# LocalAgent-Pro
SANDBOX_PATH=/app/sandbox
LOG_LEVEL=INFO
OLLAMA_HOST=http://ollama:11434

# Ollama
OLLAMA_ORIGINS=*

# Grafana
GF_SECURITY_ADMIN_PASSWORD=admin
```

### Volumes

```yaml
volumes:
  - ./sandbox:/app/sandbox        # Sandbox-Dateien
  - ./logs:/app/logs              # Log-Dateien
  - ./config:/app/config:ro       # Config (Read-Only)
```

## 🏗️ Build & Run

### Image bauen

```bash
docker build -t localagent-pro:latest .
```

### Einzelner Container

```bash
docker run -d \
  --name localagent-pro \
  -p 8001:8001 \
  -v $(pwd)/sandbox:/app/sandbox \
  -v $(pwd)/logs:/app/logs \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  localagent-pro:latest
```

### docker-compose Services

```bash
# Alle Services starten
docker-compose up -d

# Nur bestimmte Services
docker-compose up -d localagent-pro ollama

# Mit Monitoring
docker-compose --profile monitoring up -d

# Logs anzeigen
docker-compose logs -f localagent-pro

# Services stoppen
docker-compose down

# Services und Volumes löschen
docker-compose down -v
```

## 🔍 Health Checks

### Container-Status

```bash
docker ps
docker-compose ps
```

### Health-Endpoint

```bash
curl http://localhost:8001/health
```

### Ollama-Status

```bash
curl http://localhost:11434/api/tags
```

## 📊 Monitoring

### Prometheus-Metriken

```bash
# Metriken abfragen
curl http://localhost:8001/metrics

# Prometheus UI öffnen
open http://localhost:9090
```

### Grafana-Dashboard

```bash
# Grafana öffnen
open http://localhost:3001

# Login:
# Username: admin
# Password: admin (siehe .env)
```

## 🐛 Troubleshooting

### Container-Logs

```bash
# Alle Logs
docker-compose logs -f

# Nur LocalAgent-Pro
docker-compose logs -f localagent-pro

# Nur Ollama
docker-compose logs -f ollama

# Letzte 100 Zeilen
docker-compose logs --tail=100 localagent-pro
```

### Container-Shell

```bash
# Shell in LocalAgent-Pro
docker exec -it localagent-pro /bin/bash

# Shell in Ollama
docker exec -it ollama /bin/bash
```

### Ollama-Modell installieren

```bash
# In Ollama-Container
docker exec -it ollama ollama pull llama3.1:8b-instruct-q4_K_M

# Oder
docker-compose exec ollama ollama pull llama3.1:8b-instruct-q4_K_M
```

### Netzwerk-Probleme

```bash
# Netzwerk prüfen
docker network ls
docker network inspect localagent_localagent-network

# DNS-Test
docker exec -it localagent-pro ping ollama
```

### Ports belegt

```bash
# Port-Konflikte prüfen
sudo lsof -i :8001
sudo lsof -i :11434

# Ports in docker-compose ändern
# ports:
#   - "8002:8001"  # Externer Port 8002
```

## 🔒 Security

### Non-Root User

Container läuft als `localagent` User (UID 1000):

```dockerfile
USER localagent
```

### Read-Only Config

```yaml
volumes:
  - ./config:/app/config:ro  # Read-Only Mount
```

### Network Isolation

Services kommunizieren über dediziertes Netzwerk:

```yaml
networks:
  localagent-network:
    driver: bridge
```

## 📦 Production Deployment

### Image veröffentlichen

```bash
# Tag Image
docker tag localagent-pro:latest yourdockerhub/localagent-pro:v1.0.0

# Push zu Docker Hub
docker push yourdockerhub/localagent-pro:v1.0.0

# Oder GitHub Container Registry
docker tag localagent-pro:latest ghcr.io/username/localagent-pro:v1.0.0
docker push ghcr.io/username/localagent-pro:v1.0.0
```

### Production docker-compose.yml

```yaml
services:
  localagent-pro:
    image: yourdockerhub/localagent-pro:v1.0.0  # Nutze Image statt build
    restart: always  # Auto-Restart
    environment:
      - LOG_LEVEL=WARNING  # Weniger Logs
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
```

## 🧪 Testing

### Build-Test

```bash
# Image bauen und testen
docker build -t localagent-pro:test .
docker run --rm localagent-pro:test python --version
```

### Integration-Test

```bash
# Services starten
docker-compose up -d

# Warte auf Health Checks
sleep 10

# Test API
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"localagent-pro","messages":[{"role":"user","content":"Erstelle Datei test.txt"}]}'

# Cleanup
docker-compose down
```

## 📈 Performance

### Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # Max 2 CPU Cores
      memory: 2G       # Max 2GB RAM
    reservations:
      cpus: '0.5'
      memory: 512M
```

### Logging Driver

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🔄 Updates

### Image aktualisieren

```bash
# Neues Image pullen
docker pull yourdockerhub/localagent-pro:latest

# Services neu starten
docker-compose up -d

# Alte Images entfernen
docker image prune
```

### Rollback

```bash
# Alte Version wiederherstellen
docker-compose down
docker pull yourdockerhub/localagent-pro:v1.0.0
# docker-compose.yml editieren (image: ...v1.0.0)
docker-compose up -d
```

## 🗑️ Cleanup

### Container & Volumes löschen

```bash
# Alle Services stoppen und entfernen
docker-compose down -v

# Ungenutzte Images löschen
docker image prune -a

# Ungenutzte Volumes löschen
docker volume prune
```

---

**Status:** ✅ Docker-Setup vollständig  
**Image-Size:** ~200MB (Multi-Stage Build)  
**Health-Check:** ✅ Implementiert  
**Letztes Update:** 19. November 2025
