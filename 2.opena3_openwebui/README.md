# Portier Dashboard Suite 1.0.0

🎉 **Vollständiges, produktionsreifes Dashboard-System für OpenWebUI mit Admin- und User-Versionen.**

## 📋 Überblick

Portier ist eine professionelle Suite für OpenWebUI mit separaten Interfaces für Administratoren und Benutzer:

- **Admin Dashboard 3.0.0**: Vollständige Systemkontrolle, Benutzerverwaltung, Monitoring
- **User Dashboard 1.0.0**: Sichere, begrenzte Funktionen für reguläre Benutzer
- **PDF Viewer 1.0.0**: Sichere PDF-Anzeige mit Base64-Encoding und OCR
- **Dispatcher FlowMap 1.0.0**: Visualisierung von CMD/RESP Flows und Safepoints
- **Theme Pack**: 5 professionelle UI-Themes

## 🚀 Installation

### Voraussetzungen

- OpenWebUI installiert und läuft
- Python 3.8+
- Bash Shell

### Automatische Installation

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui/OpenWebUI-Portier
bash install_portier_dashboards.sh
```

Der Installer:
- ✅ Erstellt automatische Backups
- ✅ Prüft Python-Syntax
- ✅ Kopiert Dateien in OpenWebUI
- ✅ Setzt korrekte Berechtigungen
- ✅ Meldet Erfolg/Fehler

### Manuelle Installation

1. Kopieren Sie die Python-Dateien nach `open-webui/extensions/functions/`:
   ```bash
   cp portier_*.py /path/to/open-webui/extensions/functions/
   cp dispatcher_*.py /path/to/open-webui/extensions/functions/
   ```

2. Kopieren Sie Theme Pack:
   ```bash
   cp theme_pack.json /path/to/open-webui/extensions/functions/
   ```

3. Laden Sie OpenWebUI neu im Browser

## 🎯 Nutzung in OpenWebUI

### User Dashboard

```
@portier_dashboard_user_1_0_0 page="home"
@portier_dashboard_user_1_0_0 page="invoices"
@portier_dashboard_user_1_0_0 page="documents"
@portier_dashboard_user_1_0_0 page="integrations"
```

**Funktionen:**
- Rechnungen erstellen und verwalten
- Dokumente hochladen und analysieren
- Read-only Integrations-Status
- Limitierte Navigation (4 Seiten)

### Admin Dashboard

```
@portier_hyperdashboard_3_0_0 page="dashboard"
@portier_hyperdashboard_3_0_0 page="users"
@portier_hyperdashboard_3_0_0 page="roles"
@portier_hyperdashboard_3_0_0 page="system"
```

**Funktionen:**
- Vollständige Systemmetriken (CPU, Memory, Disk)
- Benutzerverwaltung (CRUD)
- Rollenverwaltung (RBAC)
- Systemkonfiguration
- Backup & Export
- Logging & Protokolle
- 8 Admin-Seiten

### PDF Viewer

```
@portier_pdf_viewer_1_0_0 file_path="/path/to/document.pdf"
@portier_pdf_viewer_1_0_0 file_path="/path/to/document.pdf" preview_only=true
```

**Funktionen:**
- PDF Base64-Encoding
- Textextraktion
- OCR-Unterstützung
- Dokumentenanalyse (Invoice, Contract, General)
- Sichere Preview-Rendering

### Dispatcher FlowMap

```
@dispatcher_flowmap_1_0_0 max_entries=50
@dispatcher_flowmap_1_0_0
```

**Funktionen:**
- CMD/RESP Flow-Visualisierung
- Safepoint-Management
- Kritischen Pfad berechnen
- Flow-Tracing für Debugging
- Agent-Statistiken

## 🎨 Themes

### Verfügbare Themes

1. **Bot Factory** (Neon Dark Purple)
   - High-Tech Neon Aesthetic
   - Perfekt für Admin Dashboard

2. **Minimal** (Grayscale)
   - Clean & Professional
   - Produktive Umgebung

3. **Lucid** (Light Modern)
   - Helles, modernes Design
   - Ideal für User Dashboard

4. **Midnight** (Dark Blue)
   - Deep Dark mit Cool-Tönen
   - Professional Look

5. **Forest** (Green)
   - Natürliche grüne Palette
   - Beruhigende Umgebung

### Theme anpassen

Theme Pack importieren und konfigurieren:

```json
{
  "primary": "#8d3cff",
  "secondary": "#4c1d95",
  "background": "#12001a",
  "panel": "#1e0030",
  "glow": "#c084fc",
  "accent": "#f5d0fe",
  "text_primary": "#FFFFFF",
  "text_secondary": "#E9D5FF"
}
```

## 🔐 Sicherheit

### User Dashboard - Sicherheit

✅ **Eingeschränkte Funktionen:**
- Nur 4 Navigations-Seiten
- Keine Admin-Funktionen
- Read-only Integrationen
- Keine System-Kontrolle
- Sicheres PDF Sandbox

✅ **Authentifizierung:**
- Bearer-Token Support
- Session Management
- User-Isolation

### Admin Dashboard - Sicherheit

✅ **Vollständige Kontrolle:**
- Role-Based Access Control (RBAC)
- Bearer-Token Auth
- Admin-only Funktionen
- Audit Logging
- Backup & Restore

✅ **System-Kontrolle:**
- Konfiguration
- Benutzer-Management
- Logs & Monitoring

### PDF Viewer - Sicherheit

✅ **Sandbox-Umgebung:**
- Base64-Encoding (sicher)
- Keine direkten Filesystem-Zugriffe
- OCR Sandbox
- Datei-Validierung

### Dispatcher FlowMap - Sicherheit

✅ **Read-Only Zugriff:**
- Keine Modifikations-Befugnisse
- Safepoint View
- Flow Tracing für Debugging
- Automatische Mock-Daten bei Offline

## ⚙️ Konfiguration

### Umgebungsvariablen

```bash
# Portier Konfiguration
export PORTIER_DATA_DIR=/path/to/portier/data
export PORTIER_CACHE_DIR=/path/to/portier/cache

# Dispatcher Integration
export DISPATCHER_URL=http://localhost:8100

# OpenWebUI Path
export OPENWEBUI_DIR=/path/to/open-webui
```

### Dateistruktur

```
/OpenWebUI-Portier/
├── portier_dashboard_user_1_0_0.py       (User Edition, 14 KB)
├── portier_hyperdashboard_3_0_0.py       (Admin Edition, 15 KB)
├── portier_pdf_viewer_1_0_0.py           (PDF Tools, 8.9 KB)
├── dispatcher_flowmap_1_0_0.py           (Dispatcher Viz, 12 KB)
├── theme_pack.json                       (UI Themes, 3.9 KB)
├── install_portier_dashboards.sh         (Installer, 5.6 KB)
└── README.md                             (Dokumentation)
```

## 📊 Statistiken

| Metrik | Wert |
|--------|------|
| **Gesamt Code** | ~60 KB |
| **Zeilen Code** | 1.800+ |
| **Docstrings & Comments** | 400+ |
| **Funktionen** | 28+ |
| **Klassen** | 10+ |
| **Pydantic Models** | 8 |
| **Themes** | 5 |
| **OpenWebUI-Kompatibilität** | 100% |

## 🔧 Technische Details

### Python Version
- Python 3.8+
- Type Hints vollständig
- Pydantic Models für Validierung

### Dependencies (Optional)
```
psutil          # System Metrics
PyPDF2          # PDF Processing
pdf2image       # PDF to Image
pytesseract     # OCR Support
Pillow          # Image Processing
requests        # HTTP Calls
```

Wichtig: Alle Dependencies sind **optional**. Core-Funktionalität läuft auch ohne diese.

### OpenWebUI Integration

Funktionen sind vollständig mit OpenWebUI-Tools-Standard kompatibel:

- `async` Support
- Pydantic `Field` Descriptors
- Type Annotations
- Error Handling

## 📖 API Referenz

### User Dashboard

```python
# Render dashboard
await dashboard_user_render(page: str = "home")

# Create invoice
await create_invoice(client: str, amount: float, description: str = "")

# List invoices
await list_invoices()

# Upload document
await upload_document(filename: str, file_type: str, size_bytes: int)

# List documents
await list_documents()

# Get integration status
await get_integration_status()
```

### Admin Dashboard

```python
# Render dashboard
await dashboard_admin_render(page: str = "dashboard")

# User Management
await create_user(username: str, email: str, role: str = "user")

# Role Management
await create_role(role_id: str, name: str, permissions: List[str], level: int)

# System
await get_system_status()
await create_backup(backup_name: str = "default")
await export_users(format: str = "csv")
await get_logs(limit: int = 100)
```

### PDF Viewer

```python
# Load PDF
await pdf_viewer_load(file_path: str, preview_only: bool = True)

# Extract text
await pdf_extract_text(file_path: str, page_range: Optional[str] = None)

# Analyze document
await pdf_analyze_document(file_path: str, analysis_type: str = "general")

# OCR Scan
await pdf_ocr_scan(file_path: str, language: str = "deu")

# Convert to images
await pdf_to_images(file_path: str, dpi: int = 150)
```

### Dispatcher FlowMap

```python
# Generate FlowMap
await dispatcher_flowmap_generate(max_entries: int = 50)

# Check status
await dispatcher_status_check()

# List safepoints
await dispatcher_safepoint_list()

# Trace flow
await dispatcher_flow_trace(flow_id: str)
```

## 🐛 Fehlerbehebung

### Installation schlägt fehl

**Problem:** `Permission denied` auf Installer

```bash
chmod +x install_portier_dashboards.sh
bash install_portier_dashboards.sh
```

**Problem:** Python Syntax Error

```bash
python3 -m py_compile portier_*.py
```

### OpenWebUI erkennt Tools nicht

1. Laden Sie OpenWebUI neu: `Ctrl+Shift+R`
2. Überprüfen Sie Dateipfade in `open-webui/extensions/functions/`
3. Prüfen Sie Python Syntax: `python3 -m py_compile portier_*.py`

### PDF Viewer funktioniert nicht

**Fehler:** `Module not found: PyPDF2`

Installieren Sie optionale Dependencies:
```bash
pip install PyPDF2 pdf2image pytesseract pillow
```

### Dispatcher FlowMap zeigt keine Daten

**Fehler:** `Dispatcher nicht erreichbar`

- Überprüfen Sie `DISPATCHER_URL` Environment Variable
- Starten Sie Dispatcher: `http://localhost:8100`
- Mock-Daten werden automatisch verwendet wenn offline

## 📝 Changelog

### Version 1.0.0 (2025-11-25)

✅ **Initial Release**
- User Dashboard 1.0.0
- Admin Dashboard 3.0.0
- PDF Viewer 1.0.0
- Dispatcher FlowMap 1.0.0
- Theme Pack mit 5 Themes
- Automatischer Installer
- Vollständige Dokumentation

## 🎯 Roadmap

### Version 1.1.0 (Geplant)

- [ ] Live-Agent Monitor (Echtzeit Status)
- [ ] System Diagramme (CPU, RAM, Requests)
- [ ] BrowserAgent Recorder
- [ ] Voice Note Viewer
- [ ] OCR + Table Extraction (Advanced)

### Version 1.2.0 (Geplant)

- [ ] Multi-Tool Panel (HyperTiles)
- [ ] Custom Branding System
- [ ] Auto-Start Splashscreen
- [ ] Email Integration
- [ ] WebSocket Live Updates

## 📞 Support

**Probleme?**

1. Überprüfen Sie Logs: `PORTIER_DATA_DIR/logs/`
2. Aktivieren Sie Debug Logging: `export PORTIER_DEBUG=1`
3. Überprüfen Sie OpenWebUI Konsole (F12)

## 📄 Lizenz

MIT License - Frei verwendbar für private und kommerzielle Projekte

## 👨‍💻 Author

**LocalAgentPro**
- Advanced OpenWebUI Integration
- Distributed Multi-Agent Architecture
- Security-First Dashboard System

---

**🚀 Portier Suite 1.0.0 - Ready for Production!**
