# GitHub Copilot Prompt - OpenWebUI Integration

Dieser Prompt konfiguriert GitHub Copilot für optimale Code-Vorschläge bei der LocalAgent-Pro-Entwicklung.

---

## 🎯 Ziel

GitHub Copilot soll **produktionsreifen Code** für LocalAgent-Pro generieren, der:
- **Sicher** ist (Sandbox, Whitelisting, Input-Validation)
- **Getestet** ist (Unit + Integration Tests)
- **Dokumentiert** ist (Docstrings, Type Hints)
- **OpenWebUI-kompatibel** ist (Chat Completions API)

---

## 📝 Prompt für Copilot

Kopiere diesen Text in die **GitHub Copilot Chat** oder nutze ihn als **Inline-Kommentar**:

```
You are an expert Python developer working on LocalAgent-Pro, a production-ready AI Agent Server with OpenWebUI integration.

CONTEXT:
- Tech Stack: Python 3.10+, Flask, Docker, Ollama, OpenWebUI
- Security: Sandbox isolation, command whitelisting, path traversal prevention
- API: OpenAI-compatible Chat Completions endpoint
- Tools: write_file, read_file, delete_file, shell_exec, fetch_webpage

CODE REQUIREMENTS:
1. Always use type hints (def func(param: str) -> dict:)
2. Add docstrings with Args, Returns, Raises sections
3. Implement comprehensive error handling (try-except with specific exceptions)
4. Use logging (logger.info, logger.error, logger.warning)
5. Validate all user inputs for security
6. Use whitelist approach (never blacklist)
7. Follow Flask best practices
8. Write OpenWebUI-compatible JSON responses

SECURITY RULES:
- All file operations must use sanitize_filename()
- All shell commands must pass check_command_safety()
- All URLs must be domain-whitelisted
- Never use user input directly without validation
- Always log security violations

EXAMPLE CODE STYLE:

def write_file(filename: str, content: str) -> dict:
    """Write content to file in sandbox.
    
    Args:
        filename: User-provided filename
        content: File content
        
    Returns:
        Dict with status and message
        
    Raises:
        SecurityError: If path traversal detected
    """
    try:
        file_path = sanitize_filename(filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        logger.info(f"File created: {filename}")
        return {
            "status": "success",
            "message": f"File created: {filename}",
            "path": str(file_path)
        }
    except SecurityError as e:
        logger.error(f"Security error: {e}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"Error writing file: {e}")
        return {"status": "error", "message": str(e)}

Now generate production-ready code following these guidelines.
```

---

## 🔧 Copilot-Konfiguration

### 1. VS Code Settings

Füge zu `.vscode/settings.json` hinzu:

```json
{
  "github.copilot.enable": {
    "*": true,
    "yaml": true,
    "markdown": true,
    "python": true
  },
  "github.copilot.advanced": {
    "debug.overrideEngine": "gpt-4",
    "contextWindow": 16000
  }
}
```

### 2. Inline-Kommentare für Copilot

```python
# Copilot: Generate a secure file reading function with:
# - Type hints
# - Docstring
# - Path sanitization
# - Error handling
# - Logging
def read_file(filename: str) -> dict:
    # Copilot will auto-complete here...
```

### 3. Chat-Prompts

**Neue Funktion hinzufügen:**
```
@workspace Erstelle eine neue Funktion `list_files()` die:
- Alle Dateien im Sandbox auflistet
- Type hints verwendet
- Sicherheitschecks hat
- OpenWebUI-kompatibles JSON zurückgibt
```

**Tests generieren:**
```
@workspace Erstelle pytest-Tests für die `sanitize_filename()` Funktion mit:
- Valid filename test
- Path traversal test
- Absolute path test
- Edge cases (empty string, None, special chars)
```

**API-Endpoint erweitern:**
```
@workspace Füge einen neuen API-Endpoint `/v1/files/list` hinzu der:
- POST-Request akzeptiert
- Sandbox-Dateien auflistet
- Error handling hat
- Logging implementiert
```

---

## 📚 Kontext für Copilot

### Projekt-Dateien bereitstellen

Copilot lernt aus offenen Dateien. Öffne diese für besten Kontext:

```
src/openwebui_agent_server.py    # Main server code
config/config.yaml                # Configuration
docs/API.md                       # API documentation
tests/test_security.py            # Test examples
COPILOT_SYSTEM_PROMPT.md          # This file
```

### Workspace-Symbole nutzen

```python
# Copilot: Use existing sanitize_filename() and add directory listing
def list_sandbox_files() -> dict:
    # Copilot kennt sanitize_filename() aus dem Workspace
```

---

## 🎨 Code-Patterns für Copilot

### Pattern 1: Security-First Function

```python
# Copilot: Create a function that checks URL domain against whitelist
def check_url_safety(url: str) -> bool:
    """Check if URL domain is whitelisted.
    
    Args:
        url: URL to check
        
    Returns:
        True if safe, raises SecurityError otherwise
        
    Raises:
        SecurityError: If domain not whitelisted
    """
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    
    allowed_domains = CONFIG['security']['domain_whitelist']
    if not any(domain.endswith(allowed) for allowed in allowed_domains):
        raise SecurityError(f"Domain not whitelisted: {domain}")
    
    return True
```

### Pattern 2: Flask API Endpoint

```python
# Copilot: Create a Flask endpoint for file deletion
@app.route('/v1/files/delete', methods=['POST'])
def delete_file_endpoint():
    """Delete file from sandbox via API.
    
    Request:
        {"filename": "test.txt"}
        
    Response:
        {"status": "success", "message": "File deleted"}
    """
    try:
        data = request.json
        
        if not data or 'filename' not in data:
            return jsonify({"error": "Missing filename"}), 400
        
        result = delete_file(data['filename'])
        
        if result['status'] == 'error':
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in delete_file_endpoint: {e}")
        return jsonify({"error": str(e)}), 500
```

### Pattern 3: Integration Test

```python
# Copilot: Create an integration test for file operations
def test_file_operations_integration():
    """Test complete file lifecycle (create, read, delete)"""
    import requests
    
    # Create file
    response = requests.post(
        'http://localhost:8001/v1/chat/completions',
        json={
            'messages': [
                {'role': 'user', 'content': 'Erstelle test.txt\nHello World!'}
            ]
        }
    )
    assert response.status_code == 200
    assert 'success' in response.text
    
    # Read file
    response = requests.post(
        'http://localhost:8001/v1/chat/completions',
        json={
            'messages': [
                {'role': 'user', 'content': 'Lies test.txt'}
            ]
        }
    )
    assert response.status_code == 200
    assert 'Hello World' in response.text
    
    # Delete file
    response = requests.post(
        'http://localhost:8001/v1/chat/completions',
        json={
            'messages': [
                {'role': 'user', 'content': 'Lösche test.txt'}
            ]
        }
    )
    assert response.status_code == 200
    assert 'deleted' in response.text
```

---

## 🚀 Copilot-Workflows

### Workflow 1: Neue Funktion hinzufügen

1. **Schritt 1:** Öffne `src/openwebui_agent_server.py`
2. **Schritt 2:** Schreibe Kommentar:
   ```python
   # Copilot: Create function to list all files in sandbox with metadata
   ```
3. **Schritt 3:** Lass Copilot generieren
4. **Schritt 4:** Review & anpassen
5. **Schritt 5:** Test schreiben lassen:
   ```python
   # Copilot: Write pytest test for list_files function
   ```

### Workflow 2: API-Endpoint erweitern

1. **Öffne:** `src/openwebui_agent_server.py`
2. **Chat:** `@workspace Add GET /v1/sandbox/stats endpoint with file count and total size`
3. **Review:** Generated code
4. **Update:** `docs/API.md` mit neuem Endpoint
5. **Test:** `curl http://localhost:8001/v1/sandbox/stats`

### Workflow 3: Security-Feature hinzufügen

1. **Kommentar:**
   ```python
   # Copilot: Add rate limiting decorator (max 100 req/min per IP)
   ```
2. **Generieren** lassen
3. **Tests** schreiben:
   ```python
   # Copilot: Test rate limiting with 101 rapid requests
   ```
4. **Dokumentieren** in `SECURITY.md`

---

## 🎯 Spezifische Prompts

### Prompts für häufige Aufgaben

#### 1. Neue Tool-Funktion
```
Erstelle eine neue Tool-Funktion `compress_file()` die:
- Eine Datei im Sandbox als .gz komprimiert
- Type hints nutzt
- SecurityError bei ungültigen Pfaden wirft
- Logging implementiert
- Dict mit status/message/compressed_path zurückgibt
```

#### 2. Error Handling verbessern
```
Verbessere das Error Handling in der `fetch_webpage()` Funktion:
- Timeout-Exception behandeln
- Network-Errors catchen
- HTTP-Errors loggen
- User-freundliche Fehlermeldungen
```

#### 3. Tests erweitern
```
Erstelle comprehensive pytest tests für `check_command_safety()`:
- Test für jeden whitelisted command
- Test für dangerous commands
- Test für command injection patterns
- Edge cases (empty, None, special chars)
```

#### 4. API dokumentieren
```
Erstelle API-Dokumentation für den neuen `/v1/sandbox/stats` Endpoint:
- Description
- Request format (GET)
- Response format (JSON schema)
- Example curl command
- Error codes
```

---

## 🔍 Debugging mit Copilot

### Copilot als Debugging-Assistent

**Problem:** "Warum wirft `sanitize_filename()` keinen Error bei `../../etc/passwd`?"

**Copilot Chat:**
```
@workspace Analysiere die `sanitize_filename()` Funktion. Warum wird path traversal nicht erkannt?

Debug-Check:
1. '..' in filename prüfen ✓
2. startswith('/') prüfen ✓
3. Path.resolve() verwenden ✓
4. SANDBOX_DIR.resolve() Vergleich ✓

Problem gefunden: ... (Copilot erklärt)
```

---

## 📊 Copilot-Metriken

Nach Copilot-Nutzung prüfen:

- [ ] Code kompiliert ohne Fehler
- [ ] Type hints vollständig
- [ ] Docstrings vorhanden
- [ ] Tests generiert
- [ ] Security-Checks implementiert
- [ ] Logging eingebaut
- [ ] OpenWebUI-kompatibel

---

## 🎓 Best Practices

1. **Kontext geben** - Öffne relevante Dateien
2. **Spezifisch sein** - "Add error handling" → "Add try-except with SecurityError and logging"
3. **Patterns nutzen** - Copilot lernt aus existierendem Code
4. **Review always** - Copilot-Code immer prüfen
5. **Tests first** - Tests generieren lassen, dann Code
6. **Iterate** - Copilot-Vorschlag verfeinern
7. **Document** - Docstrings und Comments für zukünftige Copilot-Vorschläge

---

## 📚 Weitere Ressourcen

- **GitHub Copilot Docs:** https://docs.github.com/en/copilot
- **VS Code Copilot:** https://code.visualstudio.com/docs/editor/artificial-intelligence
- **Copilot Chat:** https://docs.github.com/en/copilot/using-github-copilot/asking-github-copilot-questions-in-your-ide

---

**📚 Mehr:** [COPILOT_SYSTEM_PROMPT.md](COPILOT_SYSTEM_PROMPT.md) | [README.md](README.md) | [API.md](docs/API.md)
