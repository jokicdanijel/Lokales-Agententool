# OpenWebUI Connector - Processed Core Version

## 1. Zweck

### Hauptfunktion

- Lokaler Dateimanager fuer Gesamtprojekt
- REST-API: Read/Write/Delete
- Plugin-Kompatibel
- Sicher gegen Pfad-Traversal

### Use-Cases

- Datei-Upload via OpenWebUI
- Datei-Download via OpenWebUI
- Ordner-Erstellung
- Datei-Loeschung
- Datei-Listing

## 2. Endpunkte

### Core API

```
GET  /health              # Health-Check
GET  /files               # List Files
POST /file                # Create/Upload File
PUT  /file                # Update File
DELETE /file              # Delete File
POST /folder              # Create Folder
```

### Request-Schemas

#### GET /files

```json
{
  "path": "/path/to/folder",
  "recursive": true
}
```

#### POST /file

```json
{
  "path": "/path/to/file.txt",
  "content": "base64-encoded-content"
}
```

#### DELETE /file

```json
{
  "path": "/path/to/file.txt"
}
```

## 3. Port-Policy

### Allowed Ports

- 12344-12349 (Core Backend)
- 12355 (Connector)

### Forbidden Ports

- 8080 (UI-only fuer OpenWebUI)

### OpenWebUI

- OpenWebUI selbst nutzt nur Loopback: 127.0.0.1:8080
- Keine Backend-Services auf 8080
- Docker-Container: open-webui/open-webui:main

## 4. Sicherheitsmerkmale

### \_resolve_safe()

```python
def _resolve_safe(base_path, user_path):
    resolved = (base_path / user_path).resolve()
    if not resolved.is_relative_to(base_path):
        raise ValueError("Pfad-Traversal erkannt")
    return resolved
```

### Funktionen

- Verhindert Pfad-Traversal
- Validiert alle User-Pfade
- Base-Path-Enforcement
- Absolute-Path-Resolution

### Ausschluss venv

```python
EXCLUDED_DIRS = ["venv", "venv313", ".git", "__pycache__"]

def is_excluded(path):
    return any(excl in path.parts for excl in EXCLUDED_DIRS)
```

### CORS aktiv

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

## 5. Integration

### Mit OpenWebUI

- Plugin-Interface
- REST-API-Calls
- File-Upload/Download
- Folder-Management

### Mit Portier

- Option-2-Flow-Compliance
- Safepoint-Logging
- Archivator-Integration

## 6. Error-Handling

### 400 Bad Request

```json
{
  "error": "INVALID_PATH",
  "message": "Pfad ungueltig oder ausserhalb Base-Path"
}
```

### 403 Forbidden

```json
{
  "error": "PATH_TRAVERSAL",
  "message": "Pfad-Traversal erkannt"
}
```

### 404 Not Found

```json
{
  "error": "FILE_NOT_FOUND",
  "message": "Datei nicht gefunden"
}
```

### 500 Internal Server Error

```json
{
  "error": "FILE_OPERATION_FAILED",
  "message": "Datei-Operation fehlgeschlagen",
  "details": "..."
}
```

## 7. Deployment

### Standalone

```bash
python connector.py --port 12355
```

### Via Docker

```yaml
services:
  connector:
    build: .
    ports:
      - "12355:12355"
    volumes:
      - ./:/workspace
```

## 8. Testing

### Health-Check

```bash
curl -s http://127.0.0.1:12355/health | jq .
```

### List Files

```bash
curl -s "http://127.0.0.1:12355/files?path=/" | jq .
```

### Upload File

```bash
curl -X POST http://127.0.0.1:12355/file \
  -H "Content-Type: application/json" \
  -d '{"path": "/test.txt", "content": "SGVsbG8gV29ybGQ="}'
```

### Delete File

```bash
curl -X DELETE http://127.0.0.1:12355/file \
  -H "Content-Type: application/json" \
  -d '{"path": "/test.txt"}'
```
