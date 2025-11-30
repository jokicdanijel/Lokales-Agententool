# Docker / OpenWebUI - Processed Core Version

## 1. OpenWebUI Startregeln

### Port 8080 ausschliesslich Loopback


```yaml
ports:
  - "127.0.0.1:8080:8080"
```


### Restrictions

- Nur localhost Zugriff
- Kein externes Binding
- Kein 0.0.0.0:8080
- Security First


### Container-Name

```yaml
container_name: openwebui

```

### Data-Volume

```yaml
volumes:

  - ./data:/app/backend/data
```

### Netzwerk

```yaml
networks:
  - portier_net

```

## 2. Dienste

### openwebui Service

```yaml
services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:latest
    container_name: openwebui
    restart: unless-stopped
    ports:
      - "127.0.0.1:8080:8080"
    volumes:
      - ./data:/app/backend/data
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - WEBUI_AUTH=true

      - TZ=Europe/Vienna
    networks:
      - portier_net
```


### Environment-Variables

- **OPENAI_API_KEY** - Aus .env geladen
- **WEBUI_AUTH** - Authentication aktiviert
- **TZ** - Timezone Europe/Vienna

### Restart-Policy


- unless-stopped
- Auto-Restart bei Crash
- Kein Restart bei manueller Stop
- Persistent ueber Reboots


## 3. Port-Policy

### Allowed Backend-Ports

```
12344-12399

```

### Forbidden Ports

- **8080** - Strikt verboten fuer Backend-Services
- Nur fuer OpenWebUI UI
- Keine FastAPI auf 8080
- Keine Agent-Services auf 8080


### Network-Binding

```
Backend: 0.0.0.0:12344-12399 (erlaubt)
OpenWebUI: 127.0.0.1:8080 (UI-only)
```

## 4. Daten


### Data-Directory

```
./data/
├── db.sqlite3         # OpenWebUI Datenbank

├── uploads/           # User-Uploads
├── models/            # Model-Configs
└── prompts/           # Saved Prompts
```

### Persistenz-Regeln

- Agents, Prompts, Einstellungen liegen unter `/app/backend/data`
- Dateien niemals ueberschreiben ohne Backup
- Volume schuetzt Persistenz

- Backup vor Updates

### Backup-Strategy

```bash
# Vor Updates

docker-compose down
cp -r data data.backup.$(date +%Y%m%d)
docker-compose up -d
```

## 5. Sicherheit

### Host-Port-Policy


- Kein Host-Port ausser 8080
- 8080 nur localhost
- Keine externen Exposes
- Firewall-Rules enforced

### Network-Isolation


```yaml
networks:
  portier_net:
    driver: bridge
    internal: false
```

### Access-Control

- WEBUI_AUTH=true (Pflicht)
- User-Authentication
- Session-Management
- CORS-Restrictions

## 6. docker-compose.prod.yml

### Complete Configuration

```yaml
version: '3.8'

services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:latest
    container_name: openwebui
    restart: unless-stopped
    ports:
      - "127.0.0.1:8080:8080"
    volumes:
      - ./data:/app/backend/data
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}

      - WEBUI_AUTH=true
      - TZ=Europe/Vienna
    networks:
      - portier_net
    healthcheck:

      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3


networks:
  portier_net:
    driver: bridge
```


## 7. Deployment

### Start

```bash
docker-compose -f docker-compose.prod.yml up -d
```


### Stop

```bash
docker-compose -f docker-compose.prod.yml down
```


### Logs

```bash
docker-compose -f docker-compose.prod.yml logs -f openwebui
```


### Health-Check

```bash
curl -s http://127.0.0.1:8080/health | jq .
```

## 8. Integration mit Portier


### opena3 Agent

- Port 12347
- Wrapper um OpenWebUI
- Option-2-Flow-Compliance
- Safepoint-Logging

### Adapter

- Port 12350
- HTTP-Forwarder

- Request-Transformation
- Response-Mapping

### Dashboard

- Port 12349
- OpenWebUI-Status
- Chat-Integration
- SSE-Events


## 9. Troubleshooting

### OpenWebUI nicht erreichbar

```bash
# Check Container
docker ps | grep openwebui

# Check Logs
docker logs openwebui

# Check Port
lsof -i :8080
```

### Data-Volume-Fehler

```bash
# Check Permissions
ls -la data/

# Fix Permissions
sudo chown -R 1000:1000 data/
```

### Network-Fehler

```bash
# Recreate Network
docker-compose down
docker network prune
docker-compose up -d
```
