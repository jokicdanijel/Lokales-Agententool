# GitHub Copilot ↔ OpenWebUI Integration Guide

Nutze GitHub Copilot im VS Code Chat direkt mit Browser Agent Web-Automation!

## 🎯 Übersicht

**Direkter Workflow:**

```
VS Code Copilot Chat
    ↓
Browser Agent Slash Commands
    ↓
Tool Server (http://192.168.0.70:8765)
    ↓
Web-Automation Ausführung
    ↓
Result in Chat angezeigt
```

---

## 📦 Installation

### 1. VS Code Extensions installieren

```bash
# Öffne VS Code Extensions
Ctrl+Shift+X

# Installiere:
- GitHub Copilot
- GitHub Copilot Chat
- Python (optional, für Debugging)
```

### 2. Tool Server starten

```bash
cd LocalAgent-Pro/opena6
python3 tool_server.py --host 0.0.0.0 --port 8765
```

### 3. Settings konfigurieren

```json
{
  "browser-agent.serverUrl": "http://192.168.0.70:8765",
  "browser-agent.bearerToken": "sk_opena6_browser_v3_production",
  "browser-agent.enableCopilotIntegration": true
}
```

---

## 💬 Copilot Chat Commands

### Slash Commands

```
@browser /open <url>
@browser /extract <url> <selector>
@browser /screenshot <url>
@browser /click <url> <selector>
@browser /type <url> <selector> <text>
@browser /query <url> <selector>
@browser /scroll <url> <direction> [amount]
@browser /wait <url> <selector> [timeout]
```

---

## 🚀 Beispiele in Copilot Chat

### Beispiel 1: Website öffnen und Headline extrahieren

**Prompt:**

```
@browser öffne https://github.com und zeige mir die h1 headline
```

**Copilot antwortet:**

```
Ich öffne GitHub und extrahiere die Headline...

✅ Opened https://github.com
📄 Extracted content:
"Build and ship software on a single, collaborative platform"
```

---

### Beispiel 2: Screenshot machen

**Prompt:**

```
@browser mache einen screenshot von https://example.com
```

**Copilot antwortet:**

```
📸 Screenshot saved: /screenshots/example_2025-11-24.png
```

---

### Beispiel 3: Element anklicken

**Prompt:**

```
@browser klicke auf den sign-in button auf github.com
```

**Copilot antwortet:**

```
🖱️ Clicked: button[href*="/login"]
```

---

### Beispiel 4: Text eingeben und absenden

**Prompt:**

```
@browser öffne https://example.com, gib "hello" in input#search ein, und klicke submit
```

**Copilot antwortet:**

```
✅ Opened https://example.com
⌨️ Typed into input#search: hello
🖱️ Clicked: button.submit
```

---

## 🧠 Natürliche Sprache Prompts

Copilot versteht auch natürliche Sprachbefehle:

| Prompt                  | Command                             |
| ----------------------- | ----------------------------------- |
| "Öffne GitHub"          | `@browser /open https://github.com` |
| "Zeige die Headline"    | `@browser /extract h1`              |
| "Mach einen Screenshot" | `@browser /screenshot`              |
| "Klick den Button"      | `@browser /click button`            |
| "Scroll nach unten"     | `@browser /scroll down 5`           |

---

## 📋 Available Slash Commands

### `/browser /open <url>`

**Beschreibung:** Website öffnen
**Beispiel:** `@browser /open https://github.com`
**Response:**

```
✅ Opened https://github.com
Page Title: GitHub: The platform for modern software development
```

---

### `/browser /extract <url> <selector>`

**Beschreibung:** Text von Element extrahieren
**Beispiel:** `@browser /extract https://github.com h1`
**Response:**

```
📄 Extracted content:
"Build and ship software on a single, collaborative platform"
```

---

### `/browser /screenshot <url>`

**Beschreibung:** Screenshot der Website machen
**Beispiel:** `@browser /screenshot https://github.com`
**Response:**

```
📸 Screenshot saved: /screenshots/github_2025-11-24_10-30.png
View in: ![Screenshot](file:///screenshots/github_2025-11-24_10-30.png)
```

---

### `/browser /click <url> <selector>`

**Beschreibung:** Element anklicken
**Beispiel:** `@browser /click https://github.com button.sign-in`
**Response:**

```
🖱️ Clicked: button.sign-in
Element: Sign in to GitHub
```

---

### `/browser /type <url> <selector> <text>`

**Beschreibung:** Text in Feld eingeben
**Beispiel:** `@browser /type https://search.google.com input "github copilot"`
**Response:**

```
⌨️ Typed into input: github copilot
Ready to press Enter or click search button
```

---

### `/browser /query <url> <selector>`

**Beschreibung:** DOM-Element abfragen
**Beispiel:** `@browser /query https://github.com a[href*="/login"]`
**Response:**

```
Found 3 elements matching 'a[href*="/login"]'
- Text: "Sign in"
- Class: "HeaderMenu-link"
- Visible: true
```

---

### `/browser /scroll <url> <direction> [amount]`

**Beschreibung:** Seite scrollen
**Beispiel:** `@browser /scroll https://github.com down 5`
**Response:**

```
📜 Scrolled down by 5 steps
New viewport: 800x600 (scrolled 500px)
```

---

### `/browser /wait <url> <selector> [timeout]`

**Beschreibung:** Auf Element warten
**Beispiel:** `@browser /wait https://github.com .loader timeout=10`
**Response:**

```
⏳ Waited for .loader (timeout: 10s)
Element appeared after 2.3 seconds
```

---

## 🎯 Smart Copilot Features

### 1. Auto-Suggestion

Copilot schlägt automatisch Browser Commands vor:

```
You: "Ich möchte den GitHub Trending zu prüfen"
Copilot: "Soll ich https://github.com/trending öffnen?
          /browser /open https://github.com/trending"
```

### 2. Code Generation

Copilot generiert Code basierend auf Browser Actions:

```python
# You asked: "Extract all titles from the page"
# Copilot generated:

async def get_all_titles(url):
    result = await tool.extract_html(url, "h2, h3")
    titles = parse_html(result)
    return titles
```

### 3. Error Handling

Wenn ein Befehl fehlschlägt:

```
Error: Element not found: button.submit
Suggestions:
  1. Try: button[type="submit"]
  2. Try: .submit-button
  3. Wait for element: /wait <url> button.submit
```

### 4. Learning from History

Copilot merkt sich vorherige Aktionen:

```
Previous: Opened https://github.com
Previous: Clicked Sign in button
Next: Should I fill the login form?
```

---

## 🔧 Konfiguration

### settings.json

```json
{
  // Browser Agent Settings
  "browser-agent.serverUrl": "http://192.168.0.70:8765",
  "browser-agent.bearerToken": "sk_opena6_browser_v3_production",
  "browser-agent.enableCopilotIntegration": true,
  "browser-agent.autoSuggestActions": true,
  "browser-agent.showStatusBar": true,
  "browser-agent.debugMode": false,
  "browser-agent.timeout": 30,

  // Copilot Settings
  "github.copilot.enable": true,
  "github.copilot.chat.scopeSelection": true,

  // VS Code Chat
  "chat.commandCenter": true
}
```

---

## 💡 Pro Tipps

### Tip 1: Multi-Step Workflows

```
@browser:
1. Open https://github.com
2. Search for "GitHub Copilot"
3. Extract the first result's title
4. Screenshot the page
```

Copilot führt alle Schritte sequenziell aus!

---

### Tip 2: Context from Editor

Wenn eine URL in der Datei markiert ist:

```
const url = "https://example.com";
↓
@browser // wird automatisch diese URL nutzen
```

---

### Tip 3: Error Recovery

Bei Fehler schlägt Copilot Lösungen vor:

```
Error: Timeout waiting for button.submit
Suggestions:
  - Erhöhe timeout: /wait button.submit 20
  - Nutze anderen Selector: .form-submit
  - Screenshot für Debugging: /screenshot
```

---

### Tip 4: Browser Actions in Code

Generiere Code für Browser Automation:

```
@browser: Generate a function that scrapes GitHub trending
```

**Copilot generiert:**

```python
async def scrape_github_trending():
    """Scrape GitHub trending repositories"""
    await tool.open_website("https://github.com/trending")
    html = await tool.extract_html("body", "article")
    repos = parse_trending_repos(html)
    return repos
```

---

## 🐛 Troubleshooting

### Problem: Copilot erkennt Browser Commands nicht

**Lösung:**

```json
{
  "browser-agent.enableCopilotIntegration": true
}
```

Starte VS Code neu: `Cmd+Shift+P` → Restart Window

---

### Problem: "Server not responding"

**Lösung:**

```bash
# Check server status
curl http://192.168.0.70:8765/health

# Restart server
python3 tool_server.py --host 0.0.0.0 --port 8765
```

---

### Problem: Authorization Error

**Lösung:**

```json
{
  "browser-agent.bearerToken": "sk_opena6_browser_v3_production"
}
```

Token überprüfen: `echo $BEARER_TOKEN`

---

## 📊 Workflow Beispiele

### Web Scraping Workflow

```
User: "@browser Scrape alle Links von example.com"

Copilot:
1. Open website
2. Query all links
3. Extract href and text
4. Return as JSON
```

### Testing Workflow

```
User: "@browser Test the login form on example.com"

Copilot:
1. Open login page
2. Find input fields
3. Fill form
4. Click submit
5. Check for success message
```

### Documentation Workflow

```
User: "@browser Screenshot alle wichtigen Sections von docs.example.com"

Copilot:
1. Navigate to docs
2. Find main sections (h2 elements)
3. Screenshot each section
4. Create documentation with images
```

---

## ✅ Checkliste

- [ ] GitHub Copilot Extension installiert
- [ ] GitHub Copilot Chat Extension installiert
- [ ] Tool Server läuft (<http://192.168.0.70:8765/health>)
- [ ] Browser Agent online (<http://192.168.0.70:12350/health>)
- [ ] Copilot Integration aktiviert in settings.json
- [ ] Erste Browser Command getestet
- [ ] Multi-step Workflow funktioniert

---

## 🚀 Nächste Schritte

1. **Öffne VS Code**
2. **Öffne Copilot Chat** (`Cmd+I` oder `Ctrl+I`)
3. **Tippe ein:** `@browser /open https://github.com`
4. **Drücke Enter** - Copilot führt Command aus
5. **Sehe Result** im Chat

---

**Status**: 🟢 Copilot Integration Ready

Viel Spaß mit Web-Automation in Copilot! 🚀
