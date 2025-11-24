# GitHub Copilot Commit Message Guidelines

Guidelines für strukturierte, aussagekräftige Commit-Messages im LocalAgent-Pro-Projekt.

---

## 📝 Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

---

## 🏷️ Types

Verwende diese Prefixes:

- `feat:` - Neue Features
- `fix:` - Bugfixes
- `docs:` - Dokumentationsänderungen
- `style:` - Code-Formatierung (keine Logic-Änderung)
- `refactor:` - Code-Refactoring
- `test:` - Tests hinzufügen/ändern
- `chore:` - Build-Tasks, Dependencies, etc.
- `security:` - Sicherheits-Fixes
- `perf:` - Performance-Verbesserungen

---

## 🎯 Scopes

Projekt-Bereiche:

- `server` - Flask-Server (`openwebui_agent_server.py`)
- `security` - Security-Features (Sandbox, Whitelisting)
- `tools` - Tool-Functions (write_file, read_file, etc.)
- `api` - API-Endpoints
- `docker` - Docker/Docker Compose
- `config` - Konfigurationsdateien
- `docs` - Dokumentation
- `tests` - Tests
- `ci` - CI/CD
- `deps` - Dependencies

---

## ✍️ Subject

- **Imperativ:** "Add feature" statt "Added feature"
- **Kurz:** Max 50 Zeichen
- **Kleinbuchstaben** (außer Eigennamen)
- **Kein Punkt** am Ende

### ✅ Gute Subjects

```
feat(tools): add compress_file function
fix(security): prevent path traversal in sanitize_filename
docs(api): update chat completions endpoint
test(security): add tests for command whitelisting
```

### ❌ Schlechte Subjects

```
Added new feature.
Fixed bug
Update
WIP
```

---

## 📄 Body

- **Optional** (nur bei komplexen Changes)
- **Erkläre WARUM**, nicht WAS
- **Wrap bei 72 Zeichen**
- **Bullet Points** für mehrere Änderungen

### Beispiel

```
feat(tools): add file compression support

Implements gzip compression for sandbox files to save space.

- Add compress_file() function with security checks
- Update config.yaml with max_compressed_size setting
- Add integration test for compression workflow

Closes #42
```

---

## 🔗 Footer

- **Breaking Changes:** `BREAKING CHANGE: <description>`
- **Issues:** `Closes #123`, `Fixes #456`, `Refs #789`
- **Co-authors:** `Co-authored-by: Name <email>`

---

## 📋 Beispiele

### Feature hinzufügen

```
feat(api): add sandbox statistics endpoint

Adds GET /v1/sandbox/stats endpoint to retrieve file count,
total size, and last modified timestamp.

Returns JSON:
{
  "file_count": 42,
  "total_size_bytes": 1024000,
  "last_modified": "2025-11-21T10:30:00"
}

Closes #15
```

### Bugfix

```
fix(security): sanitize filename before path resolution

Prevents path traversal by checking for '..' before calling
Path.resolve(). Previous implementation only checked after
resolution, allowing symbolic link attacks.

Fixes #23
```

### Dokumentation

```
docs(readme): add password reset section

Links to PASSWORD_RESET.md guide for OpenWebUI admin password
reset procedures. Includes automatic script and manual methods.
```

### Tests hinzufügen

```
test(security): add comprehensive command safety tests

Covers:
- Whitelisted commands (ls, cat, grep)
- Dangerous commands (rm, dd, mkfs)
- Command injection patterns
- Edge cases (empty, None, special chars)
```

### Refactoring

```
refactor(server): extract tool detection logic

Moves tool detection from process_tool_call() to separate
detect_tool() function for better testability and readability.

No functional changes.
```

### Security-Fix

```
security(api): add request deduplication

Implements MD5-based request caching to prevent duplicate
processing and potential DoS attacks.

- Cache size limited to 1000 entries
- Returns 429 status for duplicates
- Logs duplicate attempts

SECURITY: Prevents request replay attacks
```

### Performance

```
perf(tools): optimize sandbox file listing

Replaces recursive os.walk() with pathlib.glob() for 10x faster
directory traversal. Reduces /v1/sandbox/stats response time
from 200ms to 20ms on large sandboxes.

Benchmarked with 1000+ files.
```

### Breaking Change

```
feat(api)!: change response format to OpenAI schema

BREAKING CHANGE: Chat completions now return OpenAI-compatible
JSON format instead of custom schema.

Old:
{
  "response": "text",
  "status": "success"
}

New:
{
  "choices": [{
    "message": {"content": "text"}
  }]
}

Migration guide: See docs/MIGRATION.md
```

---

## 🤖 Copilot Integration

### VS Code Copilot Chat

```
@workspace Generate commit message for staged changes
```

Copilot analysiert Änderungen und generiert:

```
feat(tools): add file metadata retrieval

Adds get_file_metadata() function to retrieve creation time,
modification time, size, and permissions for sandbox files.

- Type hints and docstrings
- Security checks (path sanitization)
- Error handling and logging
- Unit tests included
```

### CLI Copilot

```bash
# GitHub CLI mit Copilot
gh copilot suggest -t git

# Copilot generiert:
git commit -m "feat(api): add health check metrics"
```

---

## 🎨 Commit Message Templates

### Feature Template

```
feat(<scope>): <concise description>

<why was this needed?>

Changes:
- <change 1>
- <change 2>
- <change 3>

Closes #<issue>
```

### Fix Template

```
fix(<scope>): <problem fixed>

<root cause>

Solution:
- <how it was fixed>

Fixes #<issue>
```

### Docs Template

```
docs(<scope>): <what was documented>

<details>

Updated files:
- <file 1>
- <file 2>
```

---

## 🔍 Commit Message Checklist

Vor dem Commit prüfen:

- [ ] Type korrekt? (feat/fix/docs/etc.)
- [ ] Scope angegeben?
- [ ] Subject im Imperativ?
- [ ] Subject < 50 Zeichen?
- [ ] Body erklärt WARUM (wenn nötig)?
- [ ] Breaking changes dokumentiert?
- [ ] Issues verlinkt?
- [ ] Kein WIP/TODO/temp?

---

## 📊 Commit Frequency

**Best Practices:**

- **Atomic commits** - Ein logischer Change pro Commit
- **Frequent commits** - Lieber viele kleine als ein großer
- **Working state** - Jeder Commit sollte kompilieren/testen
- **Descriptive** - Kein "fix", "update", "changes"

### Beispiel-Historie

```
feat(tools): add delete_file function
test(tools): add delete_file tests
docs(api): document delete endpoint
feat(api): expose delete_file via REST

# Nicht:
feat(tools): add delete stuff
fix: oops
WIP
final fix
actually final
```

---

## 🚀 Automation

### Pre-commit Hook

Erstelle `.git/hooks/commit-msg`:

```bash
#!/bin/bash
# Validate commit message format

commit_msg=$(cat "$1")

# Check format: type(scope): subject
if ! echo "$commit_msg" | grep -qE '^(feat|fix|docs|style|refactor|test|chore|security|perf)(\(.+\))?: .{1,50}$'; then
    echo "❌ Invalid commit message format!"
    echo ""
    echo "Format: <type>(<scope>): <subject>"
    echo ""
    echo "Examples:"
    echo "  feat(api): add new endpoint"
    echo "  fix(security): prevent XSS"
    echo "  docs(readme): update installation"
    exit 1
fi

echo "✅ Commit message format valid"
```

```bash
chmod +x .git/hooks/commit-msg
```

### Commitlint (Node.js)

```bash
npm install --save-dev @commitlint/{config-conventional,cli}

# commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', [
      'feat', 'fix', 'docs', 'style', 'refactor',
      'test', 'chore', 'security', 'perf'
    ]],
    'scope-enum': [2, 'always', [
      'server', 'security', 'tools', 'api', 'docker',
      'config', 'docs', 'tests', 'ci', 'deps'
    ]]
  }
}
```

---

## 📚 Changelog Generierung

Aus strukturierten Commits automatisch Changelog erstellen:

```bash
# Install
npm install -g conventional-changelog-cli

# Generate
conventional-changelog -p angular -i CHANGELOG.md -s

# Output: CHANGELOG.md
## [1.1.0] - 2025-11-21

### Features
- **tools:** add compress_file function (#42)
- **api:** add sandbox statistics endpoint (#15)

### Bug Fixes
- **security:** sanitize filename before path resolution (#23)

### Documentation
- **readme:** add password reset section
```

---

## 🎓 Best Practices Summary

1. **Atomic Commits** - Ein Change, ein Commit
2. **Descriptive** - Subject erklärt WAS, Body erklärt WARUM
3. **Conventional** - Folge dem Format konsequent
4. **Link Issues** - Closes/Fixes/Refs #123
5. **Test Before Commit** - Jeder Commit sollte grün sein
6. **No WIP** - Kein "Work in Progress" in main branch
7. **Review Messages** - Commit Message ist auch Dokumentation

---

**📚 Mehr:** [README.md](../README.md) | [COPILOT_SYSTEM_PROMPT.md](../COPILOT_SYSTEM_PROMPT.md)
