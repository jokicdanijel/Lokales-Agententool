# GitHub Copilot Commit Instructions

## Commit Message Konventionen

Verwende prägnante, aussagekräftige Commit-Nachrichten, die den Conventional Commits Standard folgen:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: Neues Feature
- `fix`: Bug-Fix
- `docs`: Dokumentationsänderungen
- `style`: Code-Formatierung (keine funktionalen Änderungen)
- `refactor`: Code-Umstrukturierung ohne Verhaltensänderung
- `test`: Tests hinzufügen oder ändern
- `chore`: Build-Prozess oder Hilfswerkzeuge
- `perf`: Performance-Verbesserungen
- `ci`: CI/CD-Konfigurationsänderungen
- `security`: Sicherheitsrelevante Änderungen

### Scope (optional)

Bereich des Codes, der geändert wird:

- `api`: API-Endpunkte
- `tools`: Tool-Funktionen (file, shell, web)
- `config`: Konfigurationsdateien
- `security`: Sicherheitsrelevante Änderungen
- `monitoring`: Prometheus/Grafana
- `docs`: Dokumentation
- `tests`: Test-Suite
- `docker`: Docker/Deployment

### Subject

- Kurz und prägnant (max. 50 Zeichen)
- Imperativ (z.B. "Add" statt "Added" oder "Adds")
- Kein Punkt am Ende
- Beginnt mit Großbuchstaben (außer bei Fortsetzung des Typs)

### Body (optional)

- Erklärt **was** und **warum**, nicht **wie**
- Zeilenumbruch nach 72 Zeichen
- Kann mehrere Absätze haben

### Footer (optional)

- Breaking Changes: `BREAKING CHANGE: <description>`
- Issue-Referenzen: `Fixes #123`, `Closes #456`
- Reviewer: `Reviewed-by: Name`

## Beispiele

### Feature hinzufügen

```
feat(tools): add file deletion capability

Implementiert delete_file tool mit Sandbox-Validierung
und Sicherheitsprüfungen. Unterstützt nur Dateien innerhalb
der konfigurierten Sandbox-Umgebung.

Fixes #42
```

### Bug beheben

```
fix(api): correct loop detection timeout

Erhöht timeout von 1s auf 2s um false positives bei
langsamen Ollama-Responses zu vermeiden.
```

### Dokumentation aktualisieren

```
docs: update API endpoint documentation

- Fügt Beispiele für alle /v1/chat/completions Endpunkte hinzu
- Dokumentiert neue Environment-Variablen
- Aktualisiert Troubleshooting-Sektion
```

### Refactoring

```
refactor(tools): extract common validation logic

Zentralisiert Pfad-Validierung in shared utility function
um Code-Duplikation zu reduzieren.
```

### Tests hinzufügen

```
test(api): add integration tests for chat endpoint

Fügt 10 neue Tests für verschiedene Chat-Szenarien hinzu:
- Tool-Execution
- Error-Handling
- Loop-Detection
```

### Security-Fix

```
security(tools): prevent path traversal in file operations

Fügt zusätzliche Validierung hinzu um Zugriff außerhalb
der Sandbox zu verhindern. Blockiert Pfade mit ../ und
symbolische Links.

BREAKING CHANGE: Symbolische Links werden nicht mehr
unterstützt in sandbox-Operationen.
```

### Breaking Change

```
feat(config)!: change default sandbox path

BREAKING CHANGE: Standard Sandbox-Pfad wurde von /tmp/sandbox
zu /var/lib/localagent/sandbox geändert. Bestehende Installationen
müssen config.yaml aktualisieren.
```

## Best Practices

1. **Atomic Commits**: Ein Commit = eine logische Änderung
2. **Tested Code**: Code sollte getestet sein bevor committed wird
3. **No WIP Commits**: Keine "Work in Progress" Commits im main Branch
4. **Reference Issues**: Verlinke relevante GitHub Issues
5. **Sign Commits**: Verwende GPG-Signierung für Security-relevante Änderungen

## Zeilen die mit '#' beginnen

Zeilen die mit '#' beginnen werden von Git ignoriert und erscheinen
nicht in der finalen Commit-Nachricht. Nutze sie für temporäre Notizen
während du die Commit-Nachricht schreibst.

## Commit-Message-Template

Du kannst dieses Template als Basis verwenden:

```
# <type>(<scope>): <short summary>
#
# <longer explanation>
#
# Fixes #<issue-number>
```

## Hilfreiche Git Aliases

```bash
# Füge zu ~/.gitconfig hinzu:
[alias]
    cm = commit -m
    ca = commit --amend
    co = checkout
    st = status -sb
    lg = log --oneline --graph --decorate
```

## Commit vor Push prüfen

```bash
# Zeige letzte Commit-Nachricht
git log -1 --pretty=%B

# Zeige Änderungen im letzten Commit
git show --stat

# Commit-Nachricht ändern (vor Push)
git commit --amend
```

## Pre-Commit Hooks

Empfohlene Pre-Commit-Checks (`.git/hooks/pre-commit`):

```bash
#!/bin/bash
# LocalAgent-Pro Pre-Commit Hook

cd LocalAgent-Pro

# Formatierung prüfen
black --check src/ tests/ || {
    echo "❌ Black formatting failed. Run: black src/ tests/"
    exit 1
}

# Import-Sortierung prüfen
isort --check-only src/ tests/ || {
    echo "❌ isort check failed. Run: isort src/ tests/"
    exit 1
}

# Linting
flake8 src/ tests/ --max-line-length=120 || {
    echo "❌ Flake8 linting failed"
    exit 1
}

# Tests
pytest tests/ -v || {
    echo "❌ Tests failed"
    exit 1
}

echo "✅ All pre-commit checks passed"
```
