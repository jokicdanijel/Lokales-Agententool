# Port-Policy - Processed Core Version

## 1. Allowed Ports

### Backend-Ports
```
12344-12399
```

### Zuordnung
| Service               | Port  |
| --------------------- | ----- |
| opena1 (Koordinator)  | 12344 |
| opena2 (Archivator)   | 12345 |
| kordp (Koordinatport) | 12346 |
| opena3 (OpenWebUI)    | 12347 |
| opena4 (Telegram)     | 12348 |
| Dashboard             | 12349 |
| OpenWebUI Adapter     | 12350 |

### Verfuegbar
```
12351-12399 (49 freie Slots)
```

## 2. Forbidden Ports

### Port 8080
- **Exklusiv fuer OpenWebUI UI**
- Niemals Backend
- Niemals API
- Niemals FastAPI-Services
- Docker-Container: open-webui/open-webui:main

### Gruende
- Legacy-Konflikt-Vermeidung
- Klare Trennung UI/Backend
- Security-Policy
- Zentrale Enforcement

## 3. Enforcement

### Middleware
```python
class PortPolicyMiddleware:
    allowed_ports = range(12344, 12400)
    forbidden_ports = [8080]
    
    def check(self, port):
        if port in self.forbidden_ports:
            raise Forbidden("Port 8080 verboten")
        if port not in self.allowed_ports:
            raise Forbidden("Port ausserhalb 12344-12399")
```

### In jedem Service
```python
# main.py
from middleware import PortPolicyMiddleware

app.add_middleware(
    PortPolicyMiddleware,
    allowed_ports=range(12344, 12400),
    forbidden_ports=[8080]
)
```

## 4. Registry

### config/registry.json
```json
{
  "tools": {
    "opena1": {"port": 12344, "type": "coordinator"},
    "opena2": {"port": 12345, "type": "archiver"},
    "kordp": {"port": 12346, "type": "dispatcher"}
  },
  "ports": {
    "allowed": [12344, 12345, 12346, 12347, 12348, 12349, 12350],
    "forbidden": [8080]
  }
}
```

### Single Source of Truth
- Zentrale Port-Verwaltung
- Automatische Validierung
- Konsistenz-Checks
- Startup-Validierung

## 5. Validierung

### Startup
```bash
python scripts/validate_ports.py
# Prueft:
# - Alle Ports in erlaubtem Bereich
# - Keine verbotenen Ports
# - Keine Duplikate
# - Registry-Konsistenz
```

### Runtime
- Middleware prueft jeden Request
- Health-Checks validieren Ports
- Monitoring detektiert Abweichungen

## 6. Error-Handling

### 8080 Violation
```json
{
  "error": {
    "code": "FORBIDDEN_PORT",
    "message": "Port 8080 ist fuer Backend verboten",
    "details": {
      "attempted_port": 8080,
      "allowed_range": "12344-12399",
      "ui_only": true
    }
  }
}
```

### Out-of-Range
```json
{
  "error": {
    "code": "INVALID_PORT",
    "message": "Port ausserhalb erlaubtem Bereich",
    "details": {
      "attempted_port": 9000,
      "allowed_range": "12344-12399"
    }
  }
}
```

## 7. Best Practices
- Immer Registry konsultieren
- Niemals hardcoded Ports
- Environment-Variables nutzen
- Validation vor Start
- Monitoring aktivieren
