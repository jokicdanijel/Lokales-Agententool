# GitHub Copilot CLI Tunnel für OpenWebUI

Verwende GitHub Copilot direkt über die `gh copilot` CLI in OpenWebUI!

## 🎯 Übersicht

**3 Einsatzmöglichkeiten:**

| Modus | Beschreibung | Beispiel |
|-------|-------------|---------|
| **chat** | Freie Anfrage an Copilot | "Erkläre Async/Await in Python" |
| **explain** | Code/Datei erklären lassen | Zeige Datei `main.py` |
| **commit** | Commit-Message generieren | Basierend auf `git diff` |

---

## 📦 Installation & Setup

### 1. GitHub CLI installieren

**macOS:**
```bash
brew install gh
```

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

**Verify:**
```bash
gh --version
```

---

### 2. GitHub Authentication

```bash
gh auth login
# Follow the interactive prompts:
# - GitHub.com or GitHub Enterprise? → GitHub.com
# - Protocol? → HTTPS oder SSH (HTTPS empfohlen)
# - Authenticate? → y
# - Browser? → y (öffnet Browser für Login)
```

**Verify:**
```bash
gh auth status
```

---

### 3. Copilot CLI Extension

```bash
gh extension install github/gh-copilot
```

**Verify:**
```bash
gh copilot --version
```

---

## ⚙️ Konfiguration in OpenWebUI

### Valves (Parameter)

```
MODE:              "chat" | "explain" | "commit"
PROMPT:            Dein Prompt/Frage (für chat/commit)
FILES:             Datei-Pfade (für explain: FILES[0])
CWD:               Arbeitsverzeichnis (Standard: ".")
OUT_DIR:           Log-Verzeichnis (Standard: "/mnt/data")
PREVIEW_ONLY:      true = nur anzeigen, nicht ausführen
TIMEOUT_SEC:       Timeout in Sekunden (Standard: 120)
TRUNCATE:          Output kürzen auf N Zeichen
LANGUAGE:          "de" oder "en"
INCLUDE_TIMESTAMPS: Zeitstempel speichern (true/false)
VERBOSE:           Debug-Logging aktivieren
```

---

## 💬 Beispiele

### 1. Chat Mode

**Prompt:**
```
MODE: chat
PROMPT: Schreibe eine Python-Funktion für Fibonacci
```

**Response:**
```python
def fibonacci(n):
    """Generate Fibonacci sequence up to n numbers"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]

    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib
```

---

### 2. Explain Mode

**Setup:**
```
MODE: explain
FILES: ["src/main.py"]
```

**Response:**
```
Diese Datei enthält die Hauptlogik für...
- Initialisierung der Datenbank
- Request-Handling
- Error-Handling und Logging

Wichtigste Funktionen:
- init_db(): Datenbankverbindung
- handle_request(): Request-Verarbeitung
```

---

### 3. Commit Mode

**Setup:**
```
MODE: commit
PROMPT: (leer) # Nutzt Default-Prompt
```

**Git Diff:**
```diff
+ def new_feature():
+     pass
- def old_feature():
-     pass
```

**Response:**
```
✨ feat: replace old feature with new implementation

- Removed deprecated old_feature function
- Added new_feature with improved logic
- Updated tests for new implementation
```

---

## 🔄 Workflow Beispiele

### Workflow 1: Code Review mit Copilot

1. Datei öffnen in OpenWebUI
2. `MODE: explain` → Copilot erklärt den Code
3. `PROMPT: "Welche Verbesserungen möglich?"` → Suggestions erhalten
4. Code anpassen
5. `MODE: commit` → Commit-Message generieren

---

### Workflow 2: Dokumentation generieren

```
MODE: chat
PROMPT: "Schreibe ausführliche README.md für dieses Projekt"
```

Copilot generiert komplette Dokumentation!

---

### Workflow 3: Debugging Hilfe

```
MODE: chat
PROMPT: "Ich bekomme diesen Fehler: [Fehlertext]. Wie behebe ich ihn?"
```

Copilot liefert Debugging-Tipps!

---

## 📊 Response-Struktur

```json
{
  "ok": true,
  "mode": "chat",
  "preview": false,
  "base": "/mnt/data",
  "command": ["gh", "copilot", "chat", "-p", "..."],
  "cwd": "/home/user/project",
  "exit_code": 0,
  "stdout": "Hier ist die Antwort von Copilot...",
  "stderr": "",
  "log_path": "/mnt/data/copilot_tunnel_logs/run_chat_1732446000.json",
  "timestamp": "2025-11-24T10:30:00.123456",
  "duration_sec": 2.45
}
```

---

## 🎨 Output-Formate

### stdout - Copilot Response

```
Die Antwort von GitHub Copilot wird direkt hier angezeigt.
- Kann Markdown enthalten
- Kann Code-Blöcke enthalten
- Kann Multi-line sein
```

### Logs - JSON Format

```
/mnt/data/copilot_tunnel_logs/run_chat_1732446000.json
```

Alle Requests und Responses werden geloggt!

---

## 🐛 Troubleshooting

### Problem: "GitHub CLI 'gh' nicht gefunden"

**Lösung:**
```bash
# Installiere GitHub CLI
brew install gh  # Mac
apt install gh   # Linux

# Verify
gh --version
which gh
```

---

### Problem: "Not authenticated"

**Lösung:**
```bash
gh auth login
gh auth status
```

---

### Problem: "gh copilot: command not found"

**Lösung:**
```bash
# Installiere gh-copilot Extension
gh extension install github/gh-copilot
gh copilot --version
```

---

### Problem: Timeout Error

**Lösung:**
```
Erhöhe TIMEOUT_SEC:
TIMEOUT_SEC: 180  # 3 Minuten
```

---

## ✅ Checkliste

- [ ] GitHub CLI installiert (`gh --version` läuft)
- [ ] GitHub Authentication aktiv (`gh auth status` erfolg)
- [ ] gh-copilot Extension installiert (`gh extension list` zeigt es)
- [ ] Copilot CLI Tunnel im OpenWebUI hinzugefügt
- [ ] Test mit Mode=chat (Preview-Mode)
- [ ] Test mit echtem Chat
- [ ] Test mit explain
- [ ] Test mit commit

---

## 🚀 Quick Start

```bash
# 1. GitHub CLI + Extension
brew install gh
gh extension install github/gh-copilot

# 2. Authentifizierung
gh auth login

# 3. In OpenWebUI
# - Füge Tool hinzu
# - MODE: "chat"
# - PROMPT: "Hello Copilot"
# - PREVIEW_ONLY: true (zum Testen)
# - Ausführen

# 4. Wenn Preview ok ist
# - PREVIEW_ONLY: false
# - Ausführen (echte Copilot Antwort!)
```

---

## 📋 API-Referenz

### Methods

```python
# Main execution
async def run(...) -> Dict[str, Any]:
    """Führt Copilot CLI Befehl aus"""

# Utility
async def get_status() -> Dict[str, Any]:
    """Überprüfe GitHub CLI Status"""

async def get_available_models() -> List[str]:
    """Liste verfügbare Modelle auf"""
```

---

## 🔐 Security Notes

- **Bearer Token:** Wird nicht verwendet (gh-auth übernimmt Auth)
- **Logs:** Werden in `/mnt/data/copilot_tunnel_logs/` gespeichert
- **Git Diff:** Wird lokal erfasst, nicht an externe Server gesendet
- **Commands:** Laufen lokal auf dem System

---

## 💡 Pro Tipps

### Tip 1: Locale/Language Einstellung

```
LANGUAGE: "de"  # Deutsche Prompts
LANGUAGE: "en"  # English Prompts
```

---

### Tip 2: Log Analysis

```bash
# Zeige letzte Logs
ls -lt /mnt/data/copilot_tunnel_logs/ | head -5

# Lese spezifisches Log
cat /mnt/data/copilot_tunnel_logs/run_chat_*.json | jq
```

---

### Tip 3: Batch Processing

```
MODE: chat
PROMPT: "Generiere 5 Python-Funktionen für..."
```

Copilot generiert mehrere zusammenhängende Funktionen!

---

### Tip 4: Commit Message Standards

```
MODE: commit
LANGUAGE: "de"
# Konventionelle Commits auf Deutsch:
# ✨ feat: neue Funktion
# 🐛 fix: Fehlerbehebung
# 📚 docs: Dokumentation
# 🎨 style: Code-Formatierung
```

---

## 📞 Support

- **GitHub CLI Help:** `gh --help`
- **Copilot Help:** `gh copilot --help`
- **Status Check:** `gh auth status`
- **Extension Info:** `gh extension list`

---

**Status**: 🟢 GitHub Copilot CLI Tunnel Ready

Nutze die Kraft von Copilot direkt in OpenWebUI! 🚀
