# VSCode Extension 3.0 - PORTIER Integration

Vollständige VSCode Extension für PORTIER 3.0 Stack Integration mit opena5_vscode API Connection.

## Struktur

```
vscode-extension/
├── package.json         # Extension Manifest
├── extension.js         # Hauptlogik & Commands
├── src/
│   └── api.js          # PORTIER API Client
├── media/
│   └── panel.html      # Sidebar Webview
└── README.md           # Installation Guide
```

## Installation

```bash
# 1. Dependencies installieren
npm install vsce -g

# 2. Extension Package erstellen
vsce package

# 3. In VSCode installieren
# Extensions → Install from VSIX → portier-vscode-agent-3.0.0.vsix
```

## Commands

- **PORTIER: Run Command on VSCode Agent**
- **PORTIER: Analyze Active File**
- **PORTIER: Auto-Refactor**
- **PORTIER: Explain Code**
- **PORTIER: Generate Unit Tests**
- **PORTIER: Open Agent Dashboard**
- **PORTIER: View Logs**

## API Integration

Die Extension verbindet sich automatisch mit opena5_vscode Agent auf Port 12348.

## Features

- ✅ Inline CodeLens Actions
- ✅ StatusBar Integration
- ✅ Commands Palette
- ✅ AI-Powered Development
- ✅ Real-time Agent Status
- ✅ Direct Dashboard Access
