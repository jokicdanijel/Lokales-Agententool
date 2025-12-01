# 🎙️ Voice Input Extension for VS Code - Vollständige Installationsanleitung

## 📋 Anforderungen

- **VS Code**: Version 1.80.0 oder später
- **Node.js**: Version 16.x oder später
- **npm**: Version 8.0 oder später
- **TypeScript**: Version 5.1 oder später
- **Modernes Browser mit Web Speech API Support**

### Systemanforderungen

- **RAM**: Mindestens 2 GB
- **Speicher**: 500 MB für Extension und Dependencies
- **Mikrofon**: Für Voice Input erforderlich
- **Internet**: Für npm dependencies erforderlich

## 🚀 Installation

### Schritt 1: Vorbedingungen installieren

```bash
# Node.js und npm prüfen
node --version  # sollte v16 oder höher sein
npm --version   # sollte 8.0 oder höher sein
```

Falls nicht installiert:

- **macOS**: `brew install node`
- **Ubuntu/Debian**: `sudo apt-get install nodejs npm`
- **Windows**: Besuchen Sie <https://nodejs.org>

### Schritt 2: Extension-Verzeichnis besuchen

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui/voice-input-extension
```

### Schritt 3: Abhängigkeiten installieren

```bash
npm install
```

Dies installiert:

- **vscode**: VS Code API
- **typescript**: TypeScript Compiler
- **eslint**: Code Linter
- **@types/node**: Node.js Type Definitions
- **web-speech-api**: Web Speech API Polyfill

### Schritt 4: Extension kompilieren

```bash
# Option 1: Schnelle Kompilierung
npm run compile

# Option 2: Watch-Modus (auto-compile)
npm run watch

# Option 3: Mit Build-Script
bash build.sh
```

### Schritt 5: Extension testen

```bash
# Methode 1: Mit F5 in VS Code
1. Öffnen Sie das Extension-Verzeichnis in VS Code
2. Drücken Sie F5
3. Eine neue VS Code Fenster öffnet sich mit der Extension

# Methode 2: Mit npm
npm run compile
```

## 🎙️ Erste Benutzung

### Voice Input aktivieren

1. **Öffne VS Code**
2. **Drücke Ctrl+Shift+V** (oder Cmd+Shift+V auf Mac)
3. **Starten Sie zu sprechen**
4. **Schweigen Sie für 2+ Sekunden**, um automatisch zu stoppen
5. **Transkript wird in den Editor eingefügt**

### Verfügbare Tastenkombinationen

| Tastenkombination | Aktion | Plattform |
|---|---|---|
| Ctrl+Shift+V | Toggle Voice Recognition | Windows/Linux |
| Cmd+Shift+V | Toggle Voice Recognition | macOS |
| Ctrl+Shift+L | Sprache wechseln | Windows/Linux |
| Cmd+Shift+L | Sprache wechseln | macOS |
| Ctrl+Shift+S | Analytics anzeigen | Windows/Linux |
| Cmd+Shift+S | Analytics anzeigen | macOS |
| Ctrl+Shift+E | Analytics exportieren | Windows/Linux |
| Cmd+Shift+E | Analytics exportieren | macOS |

### Verfügbare Befehle

Öffne die Befehlspalette (Ctrl+Shift+P) und suche nach:

- **Voice Input: Toggle Voice Recognition** - Voice Input an/aus
- **Voice Input: Start Voice Recognition** - Voice Input starten
- **Voice Input: Stop Voice Recognition** - Voice Input stoppen
- **Voice Input: Show Voice Output** - Output Channel anzeigen
- **Voice Input: Voice Input Settings** - Einstellungen öffnen
- **Voice Input: Switch Language** - Sprache wechseln
- **Voice Input: Toggle Continuous Mode** - Kontinuierlicher Modus
- **Voice Input: Show Analytics** - Statistiken anzeigen
- **Voice Input: Export Analytics** - Statistiken exportieren
- **Voice Input: Clear History** - Verlauf löschen
- **Voice Input: Show Help** - Hilfe anzeigen
- **Voice Input: Test Microphone** - Mikrofon testen
- **Voice Input: Reset Settings** - Einstellungen zurücksetzen

## ⚙️ Konfiguration

### Einstellungen öffnen

1. Drücken Sie Ctrl+, (Komma)
2. Suchen Sie nach "Voice Input"
3. Bearbeiten Sie die Einstellungen

### Wichtigste Einstellungen

#### Sprache

- **Unterstützt**: Deutsch, Englisch, Französisch, Spanisch, Italienisch, Portugiesisch, Niederländisch, Japanisch
- **Standard**: Deutsch (de)

```json
"voiceInput.defaultLanguage": "de"
```

#### Auto-Send an Copilot

- **Aktiviert**: Transkripte werden automatisch an Copilot Chat gesendet
- **Standard**: Deaktiviert

```json
"voiceInput.autoSend": true
```

#### Schweigen-Schwellenwert

- **Bereich**: 500-10000 ms
- **Standard**: 2000 ms
- **Beschreibung**: Zeit bis automatisches Stoppen nach Schweigen

```json
"voiceInput.silenceThreshold": 2000
```

#### Maximale Aufnahmedauer

- **Bereich**: 10-300 Sekunden
- **Standard**: 60 Sekunden

```json
"voiceInput.maxDuration": 60
```

#### Status Bar anzeigen

- **Standard**: Aktiviert

```json
"voiceInput.showStatusBar": true
```

#### Lautstärke für Feedback

- **Bereich**: 0.0 - 1.0
- **Standard**: 0.5

```json
"voiceInput.soundVolume": 0.5
```

#### Zwischenergebnisse anzeigen

- **Standard**: Aktiviert
- **Beschreibung**: Teilweise Transkripte während des Sprechens anzeigen

```json
"voiceInput.showInterimResults": true
```

#### Kontinuierlicher Modus

- **Standard**: Deaktiviert
- **Beschreibung**: Weiter zuhören zwischen Aufnahmen

```json
"voiceInput.continuousMode": false
```

## 📊 Funktionen

### Core Features

✅ **Echtzeit-Spracherkennung**

- Kontinuierliche Verarbeitung während des Sprechens
- Echte Transkripte mit hoher Genauigkeit

✅ **Copilot Integration**

- Direktes Senden an Copilot Chat
- Auto-Send Modus für Hände-frei-Workflow

✅ **Multi-Language Support**

- 8 Sprachen unterstützt
- Schnelles Sprachumschalten

✅ **Intelligente Spracherkennung**

- Automatisches Stoppen nach Schweigen
- Maximale Aufnahmedauer
- Konfidenz-Schwellenwert

### Analytics & Reporting

📊 **Umfassende Statistiken**

- Anzahl Sitzungen
- Erfolgsrate
- Durchschnittliche Transkript-Länge
- Durchschnittliche Konfidenz
- Meistgenutzte Sprache
- An Copilot gesendete Transkripte

📁 **Export-Optionen**

- JSON Format
- CSV Format
- Formatierter Text

### Erweiterte Features

🔧 **Anpassbare Einstellungen**

- Language, Silence, Duration
- Sound Feedback, Notifications
- Continuous Mode, Interim Results

🎵 **Audio Feedback**

- Start/Stop Sounds
- Bestätigungstöne
- Einstellbare Lautstärke

📝 **Logging & Debugging**

- Detaillierte Event-Logs
- Error Tracking
- Performance Metrics

## 🐛 Fehlerbehandlung

### Problem: "Speech Recognition not supported"

**Ursache**: Browser oder OS unterstützt Web Speech API nicht

**Lösung**:

1. Verwenden Sie Chrome, Edge oder einen anderen Chromium-Browser
2. Update auf die neueste VS Code Version
3. Prüfen Sie OS-Kompatibilität

### Problem: Mikrofon wird nicht erkannt

**Ursache**: Fehlende Berechtigungen oder nicht verbundenes Mikrofon

**Lösung**:

1. Überprüfen Sie Mikrofonverbindung
2. Geben Sie VS Code Mikrofonzugriff
   - **Windows**: Einstellungen > Datenschutz > Mikrofon
   - **macOS**: Systemeinstellungen > Sicherheit > Datenschutz > Mikrofon
   - **Linux**: Prüfen Sie PulseAudio Einstellungen

### Problem: Transkript wird nicht eingefügt

**Ursache**: Kein aktiver Editor

**Lösung**:

1. Öffnen Sie eine Datei oder eine neue Registerkarte
2. Klicken Sie in den Editor
3. Versuchen Sie Voice Input erneut

### Problem: Zu viele Fehler bei der Erkennung

**Ursache**: Hintergrundgeräusche oder schlechte Mikrofonqualität

**Lösung**:

1. Reduzieren Sie Hintergrundgeräusche
2. Erhöhen Sie Schweigen-Schwellenwert
3. Testen Sie mit Test Microphone Befehl

## 📈 Performance Tipps

1. **Schweigen-Schwellenwert erhöhen** für schnelleres Stoppen
2. **Zwischenergebnisse deaktivieren** für bessere Performance
3. **Maximal-Dauer senken** um Speicher zu sparen
4. **Sound Feedback deaktivieren** in zeitkritischen Szenarien

## 🔐 Datenschutz

- ✅ Alle Verarbeitung lokal auf Ihrem Rechner
- ✅ Keine Cloud-Upload standardmäßig
- ✅ Keine Benutzerdaten-Tracking
- ✅ Transkripte bleiben in Ihrem Editor

## 📚 Weitere Ressourcen

- **VS Code Extension API**: <https://code.visualstudio.com/api>
- **Web Speech API**: <https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API>
- **GitHub Copilot**: <https://github.com/features/copilot>

## 🤝 Support

Bei Problemen:

1. Aktivieren Sie Output Channel (Voice Input > Show Voice Output)
2. Aktivieren Sie Loglevel (Command: Show Logs)
3. Kopieren Sie Logs und Fehlermeldungen
4. Erstellen Sie ein Issue mit Logs

## 📝 Changelog

### Version 1.0.0

- ✅ Initiale Version
- ✅ Voice Recognition Engine
- ✅ Copilot Integration
- ✅ Settings Management
- ✅ Analytics & Reporting
- ✅ Multi-Language Support
- ✅ Command Handler

---

**Version**: 1.0.0
**Status**: Production Ready ✅
**Kompatibilität**: VS Code 1.80+, Node 16+
**Lizenz**: MIT
