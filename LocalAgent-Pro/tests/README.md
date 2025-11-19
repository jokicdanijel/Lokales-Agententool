# LocalAgent-Pro Test Suite

Umfassende Test-Suite für LocalAgent-Pro mit Unit-Tests, Integration-Tests und Security-Tests.

## 📋 Übersicht

- **Unit-Tests:** 100+ Tests für Core-Funktionen
- **Integration-Tests:** End-to-End Workflow-Tests
- **Security-Tests:** Shell-Blocking, Sandbox-Isolation, Command-Injection
- **Coverage:** Ziel ≥80% Code-Coverage

## 🚀 Schnellstart

### Test-Suite ausführen

```bash
# Alle Tests
./run_tests.sh

# Nur Unit-Tests
./run_tests.sh unit

# Nur Integration-Tests
./run_tests.sh integration

# Nur Security-Tests
./run_tests.sh security

# Schnelle Tests (ohne slow-Tests)
./run_tests.sh fast

# Mit Coverage-Report
./run_tests.sh coverage
```

### Einzelne Test-Dateien

```bash
# pytest direkt nutzen
pytest tests/unit/test_command_validation.py -v
pytest tests/unit/test_loop_protection.py -v
pytest tests/integration/test_workflows.py -v
```

## 📁 Test-Struktur

```
tests/
├── __init__.py
├── conftest.py              # Pytest Fixtures & Configuration
├── unit/                    # Unit-Tests
│   ├── __init__.py
│   ├── test_command_validation.py    # 40+ Tests für _is_valid_command()
│   ├── test_tool_detection.py        # 15+ Tests für analyze_and_execute()
│   ├── test_sandbox_isolation.py     # 12+ Tests für Sandbox-Pfade
│   ├── test_shell_blocking.py        # 25+ Tests für Shell-Security
│   └── test_loop_protection.py       # 15+ Tests für Loop-Detection
└── integration/             # Integration-Tests
    ├── __init__.py
    └── test_workflows.py             # 10+ End-to-End Tests
```

## 🧪 Test-Kategorien

### Unit-Tests (`tests/unit/`)

#### test_command_validation.py
Tests für `_is_valid_command()` Funktion:
- ✅ Valide Commands (ls, pwd, cat, grep, etc.)
- ❌ Invalide Commands (nur Pfade, nur Dateinamen)
- 🔍 Edge Cases (leere Strings, lange Prompts, Sonderzeichen)

**Beispiele:**
```python
def test_valid_ls_with_args():
    assert _is_valid_command("ls -la") is True

def test_invalid_absolute_path():
    assert _is_valid_command("/home/user/file.txt") is False
```

#### test_tool_detection.py
Tests für `analyze_and_execute()` Tool-Erkennung:
- 📝 write_file Detection ("Erstelle Datei...")
- 📖 read_file Detection ("Lies Datei...")
- 🗑️ delete_file Detection ("Lösche Datei...")
- 🔧 Shell Command Detection ("SHELL:", "RUN:")
- 🌐 fetch_webpage Detection (URL-Erkennung)

**Beispiele:**
```python
@patch('openwebui_agent_server.write_file')
def test_detect_write_file_german_create(mock_write):
    analyze_and_execute("Erstelle Datei test.txt mit Inhalt Hello")
    assert mock_write.called
```

#### test_sandbox_isolation.py
Tests für Sandbox-Isolation:
- 📁 Pfadauflösung zu Sandbox
- 🚫 Verhinderung von Pfad-Escapes
- 🔒 Parent-Directory-Traversal-Blocking
- 🔗 Symlink-Escape-Prevention

**Beispiele:**
```python
def test_sandbox_prevents_absolute_path_escape():
    result = resolve_path("/etc/passwd")
    assert str(sandbox_path) in str(result)
```

#### test_shell_blocking.py
Tests für Shell-Security:
- ✅ Safe Commands (ls, pwd, cat, grep)
- ❌ Dangerous Commands (rm -rf, sudo, dd, chmod 777)
- 🚨 Command-Injection-Verhinderung
- ⏱️ Timeout-Handling

**Beispiele:**
```python
@pytest.mark.security
def test_shell_blocks_dangerous_rm_rf():
    result = run_shell("rm -rf /home/user")
    assert "blockiert" in result.lower()
```

#### test_loop_protection.py
Tests für Loop-Detection:
- 🔁 Identische Requests erkennen
- ⏱️ 2-Sekunden-Timeout
- 🔢 Max 1 Retry-Limit
- 🔐 MD5-Hash-Tracking

**Beispiele:**
```python
def test_loop_detection_identical_requests():
    is_loop1 = is_loop_request("Test")  # False
    is_loop2 = is_loop_request("Test")  # True (Loop!)
    assert is_loop2 is True
```

### Integration-Tests (`tests/integration/`)

#### test_workflows.py
End-to-End Workflow-Tests:
- 🔄 Chat Request → Tool-Execution → Response
- 🔁 Loop-Protection Integration
- 🌐 Domain-Whitelist Integration
- 📊 Prometheus-Metrics Integration
- ❌ Error-Handling

**Beispiele:**
```python
def test_chat_request_write_file_workflow(app_client):
    response = app_client.post('/v1/chat/completions', json={...})
    assert response.status_code == 200
```

## 📊 Coverage-Report

Nach `./run_tests.sh coverage` wird ein HTML-Report generiert:

```bash
# Coverage-Report öffnen
firefox htmlcov/index.html
# oder
google-chrome htmlcov/index.html
```

### Coverage-Ziele

| Modul | Ziel | Aktuell |
|-------|------|---------|
| openwebui_agent_server.py | ≥80% | TBD |
| logging_config.py | ≥70% | TBD |
| ollama_integration.py | ≥60% | TBD |
| **Gesamt** | **≥80%** | **TBD** |

## 🏷️ Test-Marker

Tests können mit Markern kategorisiert werden:

```python
@pytest.mark.unit          # Unit-Test
@pytest.mark.integration   # Integration-Test
@pytest.mark.security      # Security-Test
@pytest.mark.slow          # Langsamer Test (>2s)
```

### Nur bestimmte Marker ausführen

```bash
# Nur Security-Tests
pytest -m security -v

# Alle außer slow-Tests
pytest -m "not slow" -v
```

## 🔧 Fixtures

Vordefinierte Fixtures in `conftest.py`:

- `temp_sandbox` - Temporäres Sandbox-Verzeichnis
- `mock_ollama_response` - Gemockter Ollama-Response
- `sample_chat_request` - Beispiel-Chat-Request
- `app_client` - Flask Test-Client

**Verwendung:**
```python
def test_my_function(temp_sandbox):
    # temp_sandbox ist automatisch erstellt und wird nach Test gelöscht
    test_file = temp_sandbox / "test.txt"
    test_file.write_text("Hello")
```

## 🐛 Debugging

### Einzelnen Test debuggen

```bash
# Mit verbose Output
pytest tests/unit/test_command_validation.py::TestCommandValidation::test_valid_ls_with_args -v -s

# Mit Debugger (pdb)
pytest tests/unit/test_command_validation.py -v --pdb
```

### Test-Logs anzeigen

```bash
# Alle Logs anzeigen (auch bei erfolgreichen Tests)
pytest tests/ -v -s --log-cli-level=DEBUG
```

### Coverage-Bericht für einzelne Datei

```bash
pytest tests/unit/test_command_validation.py --cov=src.openwebui_agent_server --cov-report=term-missing
```

## 🚨 Bekannte Probleme & Lösungen

### Import-Fehler

```bash
# Lösung: PYTHONPATH setzen
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
pytest tests/
```

### Sandbox-Pfad existiert nicht

```bash
# Lösung: Sandbox-Verzeichnis erstellen
mkdir -p ~/localagent_sandbox
```

### Ollama nicht verfügbar

Für Tests wird Ollama gemockt:
```python
@patch('openwebui_agent_server.ollama_client.chat')
def test_with_mocked_ollama(mock_ollama):
    mock_ollama.return_value = {...}
```

## 📈 CI/CD Integration

Tests werden automatisch bei jedem Push ausgeführt:

### GitHub Actions

`.github/workflows/test.yml` führt automatisch aus:
- ✅ Unit-Tests
- ✅ Integration-Tests
- ✅ Security-Scan (Bandit)
- ✅ Coverage-Upload (Codecov)
- ✅ Docker-Build

### Lokaler CI-Test

```bash
# Simuliere GitHub Actions lokal
act push
```

## 🎓 Best Practices

### Test-Naming

```python
# ✅ Gute Test-Namen
def test_write_file_creates_in_sandbox():
def test_loop_detection_triggers_on_identical_requests():
def test_shell_blocks_dangerous_rm_rf():

# ❌ Schlechte Test-Namen
def test_1():
def test_function():
def test_something():
```

### Assertions

```python
# ✅ Spezifische Assertions
assert result == "expected_value"
assert "error" in result.lower()
assert mock_function.called
assert mock_function.call_count == 2

# ❌ Schwache Assertions
assert result
assert result is not None
```

### Mocking

```python
# ✅ Mocking von externen Abhängigkeiten
@patch('openwebui_agent_server.ollama_client.chat')
@patch('openwebui_agent_server.write_file')
def test_with_mocks(mock_write, mock_ollama):
    ...

# ❌ Testen von Implementierungsdetails
@patch('openwebui_agent_server._internal_helper_function')
```

## 📚 Weitere Ressourcen

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

## 🤝 Contribution

Bei neuen Features bitte Tests hinzufügen:

1. Unit-Tests für neue Funktionen
2. Integration-Tests für neue Endpoints
3. Security-Tests für sicherheitsrelevante Änderungen
4. Coverage ≥80% beibehalten

```bash
# Tests vor Commit ausführen
./run_tests.sh all
```

---

**Status:** ✅ Test-Suite vollständig implementiert (100+ Tests)  
**Coverage-Ziel:** ≥80%  
**Letztes Update:** 19. November 2025
