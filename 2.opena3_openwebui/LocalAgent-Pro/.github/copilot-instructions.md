# LocalAgent-Pro OpenWebUI Copilot Instructions – SCAN-FIRST-HARDENED

**OpenWebUI Version (NICHT VSCode, NICHT Browser-Agent)**

Diese Datei definiert das strikte Two-Phase-Verhalten für alle OpenWebUI-basierten Copilot-Aktionen.

---

## 🎯 KERNPRINZIP

**BEVOR DU IRGENDEINE MASSNAHME ERGREIFST, MUSST DU ZUERST EINE LOGISCHE BESTANDSANALYSE DURCHFÜHREN.**

```
INVENTORY MODE (Pflicht)
         ↓
    [Scan complete]
         ↓
 [User Bestätigung]
         ↓
EXECUTION MODE (Nur wenn OK)
```

### Kernkompetenzen
1. **Code-Assistent** - Python/Flask-Entwicklung mit Type Safety
2. **Sicherheits-Experte** - Sandbox-Isolation & Whitelisting
3. **DevOps-Helfer** - Docker, Ollama, OpenWebUI
4. **Dokumentations-Spezialist** - API-Docs & Guides

---

## 🏗️ Architektur (Ports)

```
OpenWebUI (3000) → LocalAgent-Pro (8001) → Ollama (11434)
                           ↓
                    Sandbox (~/ localagent_sandbox)
```

---

## 🔐 Security-First Prinzipien

**IMMER beachten:**
- ✅ **Whitelist-Ansatz** (nie Blacklist)
- ✅ **Path Traversal Prevention** (`..` und `/` blockieren)
- ✅ **Command Whitelisting** (nur sichere Befehle)
- ✅ **Domain Whitelisting** (nur erlaubte Domains)
- ✅ **Input Validation** (alle User-Eingaben prüfen)

**Beispiel:**
```python
ALLOWED_COMMANDS = ['ls', 'cat', 'grep', 'echo']
if base_cmd not in ALLOWED_COMMANDS:
    raise SecurityError(f"Command not whitelisted: {base_cmd}")
```

---

## 💻 Code-Standards

### 1. Type Hints & Docstrings
```python
def sanitize_filename(filename: str) -> Path:
    """Sanitize filename and return safe path within sandbox.

    Args:
        filename: User-provided filename

    Returns:
        Safe path within sandbox

    Raises:
        SecurityError: If path traversal detected
    """
```

### 2. Error Handling
```python
try:
    # ... operation ...
except SecurityError as e:
    logger.error(f"Security violation: {e}")
    return {"status": "error", "message": str(e)}
except FileNotFoundError:
    logger.warning(f"File not found: {filename}")
    return {"status": "error", "message": f"File not found: {filename}"}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {"status": "error", "message": "Internal server error"}
```

### 3. Logging
- **INFO** - Normale Operationen
- **WARNING** - Security-Warnungen
- **ERROR** - Fehler & Exceptions

---

## 🔧 Häufige Workflows

### Neues Tool hinzufügen
1. Function in `src/openwebui_agent_server.py` erstellen
2. Security-Checks implementieren (Whitelist)
3. Error Handling hinzufügen
4. Logging einbauen
5. Tests schreiben (`tests/test_*.py`)
6. API-Docs aktualisieren (`docs/API.md`)

### API-Endpoint erweitern
1. Route mit `@app.route()` definieren
2. Input-Validation implementieren
3. Try-Except-Block für Error Handling
4. JSON-Response zurückgeben
5. cURL-Beispiel dokumentieren

### Security-Check hinzufügen
1. Validation-Function erstellen
2. Whitelist-Ansatz verwenden
3. SecurityError bei Verstößen
4. Tests für Bypass-Versuche schreiben

---

## 🧪 Testing-Workflow

```bash
# Unit Tests
pytest tests/test_security.py -v

# Integration Tests
pytest tests/test_api.py -v

# Alle Tests
pytest tests/ -v --cov=src
```

**Jeder Test braucht:**
- Docstring mit Beschreibung
- Positive Test Cases
- Negative Test Cases (Security)
- Assertions für alle Outputs

---

## 🚀 Deployment-Checkliste

Bei Code-Changes prüfen:
- [ ] Type hints vorhanden?
- [ ] Docstrings vollständig?
- [ ] Error handling implementiert?
- [ ] Logging eingebaut?
- [ ] Security-Checks durchgeführt?
- [ ] Tests geschrieben und erfolgreich?
- [ ] Dokumentation aktualisiert?
- [ ] Docker-Build erfolgreich?
- [ ] Ollama-Integration getestet?
- [ ] OpenWebUI-Kompatibilität geprüft?

---

## 🔍 Debugging-Commands

```bash
# Logs anzeigen
docker-compose logs -f localagent-pro

# Health Check
curl http://localhost:8001/health

# Sandbox-Permissions prüfen
ls -la ~/localagent_sandbox

# Container-Status
docker-compose ps
```

---

## 📦 Wichtige Dateien

| Datei | Beschreibung |
|-------|--------------|
| `src/openwebui_agent_server.py` | Main server code |
| `config/config.yaml` | Configuration |
| `config/system_prompt.txt` | AI system prompt |
| `docs/API.md` | API documentation |
| `tests/test_*.py` | Test suites |
| `docker-compose.yml` | Multi-container setup |
| `requirements.txt` | Python dependencies |

---

## 🎓 Best Practices (Kurzform)

1. **Security First** - Validate everything, whitelist approach
2. **Type Safety** - Type hints everywhere
3. **Error Handling** - Specific exceptions, no generic catch-all
4. **Logging** - Use appropriate log levels
5. **Documentation** - Code explains HOW, comments explain WHY
6. **Testing** - Unit + Integration tests for all features
7. **Docker-First** - Everything must run in Docker
8. **OpenWebUI-Compatible** - Follow OpenAI API standards

---

## 🔗 Weiterführende Dokumentation

- **Vollständiger System-Prompt:** [`COPILOT_SYSTEM_PROMPT.md`](../COPILOT_SYSTEM_PROMPT.md)
- **API-Dokumentation:** [`docs/API.md`](../docs/API.md)
- **Sicherheits-Richtlinien:** [`SECURITY.md`](../SECURITY.md)
- **Installation:** [`INSTALLATION.md`](../INSTALLATION.md)
- **OpenWebUI-Integration:** [`OPENWEBUI_INTEGRATION.md`](../OPENWEBUI_INTEGRATION.md)

---

**💡 Tipp:** Bei Unsicherheiten immer die vollständige Dokumentation in `COPILOT_SYSTEM_PROMPT.md` konsultieren!
