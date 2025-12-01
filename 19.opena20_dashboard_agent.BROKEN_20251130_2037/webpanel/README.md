# OpenWebUI Agent V2 - Web Panel

**PORTIER 3.0 Enterprise Control Panel**

## 🎯 Überblick

**Service:** Web Panel Control Interface  
**Port:** 8088 (Docker)  
**Target API:** http://127.0.0.1:12347  
**Technologie:** HTML/CSS/JavaScript + Docker
**Status:** ✅ Production Ready

## 🚀 Quick Start

### Docker (Empfohlen)

```bash
# Build & Run (One-liner)
./build-and-run.sh

# Manual Docker
docker build -t opena3-webpanel .
docker run -d -p 8088:80 opena3-webpanel
```

### Direkter Zugriff

```bash
# Statische Files
python3 -m http.server 8088
# Oder
nginx -c nginx.conf
```

## 🌐 Web Interface

**URL:** http://localhost:8088

### Features

- **🔐 Bearer Token Authentication**
- **🩺 Health Check** - Service Status
- **💬 Native Chat** - Direkte Chat-Kommunikation  
- **🛠️ CMD Dispatch** - Option-2-Flow Commands
- **🚦 Dispatch Ready** - Routing Status
- **🧪 Self-Test** - Vollständiger Systemtest

### UI Components

- **Dark Theme** - Enterprise GitHub-Style
- **Responsive Design** - Mobile & Desktop
- **Real-time Logs** - JSON-formatierte Ausgabe
- **Token Persistence** - localStorage Management
- **Error Handling** - User-friendly Fehlermeldungen

## ⚙️ Konfiguration

### config.js

```javascript
const CONFIG = {
    BASE_URL: "http://127.0.0.1:12347",  // OpenWebUI Integration Server
    VERSION: "2.0.0",
    PORTIER_COMPLIANCE: "3.0"
};
```

### Environment Detection

- **Development:** `localhost:8088` → `127.0.0.1:12347`
- **Production:** Automatische HTTPS-Erkennung
- **Docker:** Container-friendly Konfiguration

## 🧪 Testing

### 1. Service Health

1. Öffne http://localhost:8088
2. Klicke "Health Check"
3. Erwarte: `{"status": "ok", ...}`

### 2. Bearer Token

1. Gib Bearer Token ein
2. Token wird in localStorage gespeichert
3. Alle API-Calls verwenden Token

### 3. Native Chat

1. Gib Nachricht ein
2. Klicke "Senden"
3. Erwarte Chat-Response

### 4. CMD Dispatch

1. Bearbeite JSON-Payload
2. Klicke "Senden"
3. Erwarte Option-2-Flow Response

## 📁 Dateistruktur

```
webpanel/
├── index.html          # Haupt-Interface
├── app.js              # JavaScript API Client
├── style.css           # Dark Theme Styling
├── config.js           # Konfiguration
├── assets/
│   └── logo.svg        # OpenA3 Logo
├── Dockerfile          # Container Build
├── build-and-run.sh    # Docker Automation
└── README.md           # Diese Datei
```

## 🔧 Development

### Lokale Entwicklung

```bash
# Live Reload (Python)
python3 -m http.server 8088

# Oder Nginx
nginx -p . -c nginx.conf
```

### Code-Stil

- **Vanilla JavaScript** - Keine Frameworks
- **CSS Grid/Flexbox** - Modernes Layout
- **Mobile First** - Responsive Design
- **Dark Theme** - GitHub-Style Enterprise UI

### API Integration

```javascript
// Beispiel API Call
const response = await api('/health', 'GET');
setLog('health_output', response);
```

## 🐳 Docker Details

### Base Image

```dockerfile
FROM nginx:alpine
```

### Features

- **Nginx** - Produktions-webserver
- **SPA Support** - Single Page Application Routing
- **Security Headers** - CORS, XSS Protection
- **Health Checks** - Container Health Monitoring

### Container Management

```bash
# Status
docker ps | grep opena3-webpanel

# Logs
docker logs opena3-webpanel-container

# Stop/Remove
docker stop opena3-webpanel-container
docker rm opena3-webpanel-container
```

## 🔗 Integration

### PORTIER 3.0 Stack

- **opena3 (12347)** - OpenWebUI Integration Server
- **kordp (12346)** - Gateway & Routing
- **Dashboard (12349)** - HYPER-DASHBOARD 3.0
- **OpenWebUI (8080)** - UI-only (extern)

### API Endpoints

| Endpoint | Methode | Beschreibung |
|----------|---------|-------------|
| `/health` | GET | Service Health Check |
| `/native` | POST | Native Chat Request |
| `/cmd` | POST | CMD Dispatch (Option-2) |
| `/dispatch_ready` | GET | Routing Status |
| `/selftest` | GET | Vollständiger Systemtest |

## 🚨 Troubleshooting

### Häufige Probleme

| Problem | Ursache | Lösung |
|---------|---------|--------|
| 401 Unauthorized | Fehlendes Bearer Token | Token in UI eingeben |
| CORS Error | Falscher Origin | API Server CORS prüfen |
| Connection Refused | API Server offline | opena3 (Port 12347) starten |
| 404 Not Found | Falscher Endpoint | URL in config.js prüfen |

### Debug Commands

```bash
# API Server Health
curl -s http://127.0.0.1:12347/health

# Container Logs
docker logs opena3-webpanel-container

# Network Test
telnet 127.0.0.1 12347
```

---

**Version:** 2.0.0  
**Build:** 2025-11-29  
**PORTIER Compliance:** 3.0  
**Status:** ✅ Production Ready
EXTREM WICHTIG — FILE-SCAN-PFLICHT FÜR DIESEN AGENT
Bevor du irgendeine Datei erzeugst, MUSST du folgendes tun:

✔ 1. Projektverzeichnis scannen
Scanne rekursiv das Verzeichnis dieses Agents:

css
￼Code kopieren
<AgentRoot>/   → z. B. 16.opena17_homepagecreator
    main.py
    routes.py
    models.py
    agent_logic.py
    config.py
    security.py
    bin/
    data/
    templates/
    tests/
✔ 2. Existierende Dateien feststellen
Alle vorhandenen Dateien müssen analysiert werden:

nicht löschen

nicht überschreiben

nicht ignorieren

nicht neuschreiben

Du musst sie weiterverwenden.

✔ 3. Wenn eine Datei existiert, MUSST du sie patchen, nicht ersetzen
Patch-Regeln:

Nur fehlende Funktionen ergänzen

Nur fehlerhafte Bereiche reparieren

Nur neue Features anhängen

Nichts entfernen, außer explizit erlaubt

Keine Duplikate erzeugen

Beispiel:

less
￼Code kopieren
Wenn main.py vorhanden ist:
→ erweitere main.py
→ verbessere main.py
→ implementiere fehlende Endpoints
→ füge neue Klassen hinzu
→ aber überschreibe NIEMALS main.py komplett
✔ 4. Wenn eine Datei NICHT existiert, dann erst erstellen
Neue Dateien dürfen nur erstellt werden, wenn sie wirklich fehlen:

sql
￼Code kopieren
if file_exists:
    patch
else:
    create new file
✔ 5. PRIORITÄT: EXISTING > NEW
Immer:

sql
￼Code kopieren
EXISTIERENDE STRUKTUR BEWAHREN
LOGIK ONLY ERWEITERN
NIEMALS Dateien ersetzen
NIEMALS alles neu generieren
✔ 6. Workflow-Agent opena21 MUSS besonders strikt sein
opena21 darf:

andere Agents analysieren

deren Dateien lesen

fehlende Workflows ergänzen