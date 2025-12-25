# 🎙️ Voice Input Extension für VS Code - Architektur & Module

## 📦 Extension-Komponenten

### 1. **Recognition Engine** (`recognition-engine.ts`)

Kernmodul für Spracherkennung mit Web Speech API.

**Hauptklasse**: `VoiceRecognitionEngine`

**Features**:

- Real-time Spracherkennung
- Automatische Stille-Erkennung
- Sprachumschaltung
- Event-basierte Callbacks
- Transkript-Verwaltung

**Wichtigste Methoden**:

```typescript
start(): void                              // Recording starten
stop(): void                               // Recording stoppen
abort(): void                              // Abrupt abbrechen
setLanguage(language: string): void        // Sprache setzen
setSilenceThreshold(ms: number): void      // Stille-Schwellenwert
isRecognizing(): boolean                   // Status prüfen
getTranscript(): string                    // Transkript abrufen
clearTranscript(): void                    // Transkript löschen
```

**Events**:

- `onStart`: Recording begonnen
- `onTranscript`: Transkript empfangen
- `onError`: Fehler aufgetreten
- `onEnd`: Recording beendet

---

### 2. **Settings Manager** (`settings.ts`)

Verwaltet alle Konfigurationseinstellungen der Extension.

**Hauptklasse**: `VoiceInputSettings`

**Kategorien**:

- **Recognition**: Sprache, Stille, Dauer
- **Copilot**: Auto-Send, Command Detection
- **UI/UX**: Status Bar, Output, Sounds
- **Advanced**: Continuous Mode, Interim Results, Confidence

**Wichtigste Methoden**:

```typescript
getLanguages(): string[]                   // Unterstützte Sprachen
getDefaultLanguage(): string               // Standardsprache
getSilenceThreshold(): number              // Stille-Schwellenwert
isAutoSendEnabled(): boolean               // Auto-Send Status
updateSetting(key, value, global?): void   // Einstellung aktualisieren
getAllSettings(): Record<string, any>      // Alle Einstellungen
resetToDefaults(): void                    // Auf Standard zurücksetzen
onSettingsChanged(callback): Disposable    // Listener registrieren
```

---

### 3. **Copilot Integration** (`copilot-integration.ts`)

Verwaltung der Kommunikation mit GitHub Copilot.

**Hauptklasse**: `CopilotIntegrationHandler`

**Features**:

- Copilot Chat API Integration
- Editor-Integration
- Kopilot-Command-Erkennung
- Automatisches Senden
- Format-Anpassung

**Wichtigste Methoden**:

```typescript
sendToCopilotChat(transcript: string): Promise<boolean>
insertIntoEditor(transcript: string): Promise<boolean>
processTranscript(transcript: string, autoSend: boolean): void
isCopilotCommand(transcript: string): boolean
formatForCopilot(transcript: string): string
logSuccess(action: string, details: string): void
logError(action: string, error: any): void
```

---

### 4. **Analytics** (`analytics.ts`)

Umfassendes Analytics- und Logging-System.

**Hauptklassen**:

- `AnalyticsManager`: Session-Tracking und Metriken
- `EventLogger`: Strukturiertes Logging

**Analytics Features**:

```typescript
recordSession(session: VoiceSession): void
getMetrics(): PerformanceMetrics
getSessionsInRange(start, end): VoiceSession[]
getSessionsByLanguage(lang): VoiceSession[]
getFailedSessions(): VoiceSession[]
exportMetricsAsJson(): string
exportSessionsAsCsv(): string
```

**Gemessene Metriken**:

- Anzahl Sitzungen
- Erfolgs-/Fehlerrate
- Durchschnittliche Transkript-Länge
- Durchschnittliche Konfidenz
- Durchschnittliche Sitzungsdauer
- Meistgenutzte Sprache
- An Copilot gesendete Transkripte

**Event Logging**:

- Informations-Level
- Warnings
- Errors
- Zeitstempel
- Detaillierte Kontextinformationen

---

### 5. **Command Handler** (`commands.ts`)

Verwaltet alle Befehle und Benutzerinteraktionen.

**Hauptklasse**: `CommandHandler`

**Verfügbare Commands**:

- `showSettings()`: Einstellungen öffnen
- `showAnalytics()`: Statistiken anzeigen
- `exportAnalytics()`: Analytics exportieren
- `switchLanguage()`: Sprache wechseln
- `clearHistory()`: Verlauf löschen
- `resetSettings()`: Auf Standard zurücksetzen
- `showHelp()`: Hilfe anzeigen
- `toggleContinuousMode()`: Kontinuierlicher Modus
- `testMicrophone()`: Mikrofon testen

---

### 6. **Main Extension** (`extension-advanced.ts`)

Haupt-Extension-Modul mit Integration aller Komponenten.

**Hauptklasse**: `AdvancedVoiceInputManager`

**Verantwortung**:

- Initialisierung aller Module
- Command-Registrierung
- Event-Handling
- Status Bar Management
- Session-Tracking
- Ressourcen-Verwaltung

**Exported Functions**:

```typescript
activate(context: vscode.ExtensionContext): void
deactivate(): void
```

---

## 🔗 Modul-Abhängigkeiten

```
extension-advanced.ts (Main)
    ├── recognition-engine.ts
    ├── settings.ts
    ├── copilot-integration.ts
    ├── commands.ts
    │   ├── settings.ts
    │   ├── copilot-integration.ts
    │   ├── analytics.ts
    │   └── event-logger (aus analytics.ts)
    └── analytics.ts
        ├── AnalyticsManager
        ├── EventLogger
        └── globalAnalytics (Singleton)
```

---

## 📝 Datenfluss

```
┌─────────────────────┐
│   Voice Input (User)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────┐
│ Recognition Engine      │
│ (Web Speech API)        │
└──────────┬──────────────┘
           │
           ├─→ Transcript
           ├─→ Confidence
           └─→ Language
           │
           ▼
┌─────────────────────────────────┐
│  Extension Manager              │
│  - Handle Transcript            │
│  - Format for Copilot           │
│  - Insert in Editor             │
│  - Record Analytics             │
└──────────┬──────────────────────┘
           │
           ├─────────────────┬──────────────┐
           │                 │              │
           ▼                 ▼              ▼
    ┌──────────┐    ┌───────────────┐   ┌────────┐
    │  Editor  │    │ Copilot Chat  │   │Analytics│
    └──────────┘    └───────────────┘   └────────┘
```

---

## 🎛️ Settings-Hierarchie

```
voiceInput (Configuration Scope)
├── Recognition Settings
│   ├── languages: string[]
│   ├── defaultLanguage: string
│   ├── silenceThreshold: number
│   └── maxDuration: number
├── Copilot Integration
│   ├── autoSend: boolean
│   ├── detectCopilotCommands: boolean
│   └── autoFocusEditor: boolean
├── UI/UX Settings
│   ├── showStatusBar: boolean
│   ├── statusBarPosition: 'left' | 'right'
│   ├── showOutput: boolean
│   ├── enableSounds: boolean
│   ├── soundVolume: number
│   └── notifyOnEnd: boolean
└── Advanced Settings
    ├── continuousMode: boolean
    ├── showInterimResults: boolean
    └── confidenceThreshold: number
```

---

## 🔌 Command-Registrierung

| Command                           | Beschreibung    | Keybinding   |
| --------------------------------- | --------------- | ------------ |
| `voiceInput.toggle`               | An/Aus schalten | Ctrl+Shift+V |
| `voiceInput.start`                | Starten         | -            |
| `voiceInput.stop`                 | Stoppen         | -            |
| `voiceInput.showOutput`           | Output anzeigen | -            |
| `voiceInput.showSettings`         | Einstellungen   | -            |
| `voiceInput.switchLanguage`       | Sprache         | Ctrl+Shift+L |
| `voiceInput.toggleContinuousMode` | Kontinuierlich  | -            |
| `voiceInput.showAnalytics`        | Analytics       | Ctrl+Shift+S |
| `voiceInput.exportAnalytics`      | Export          | Ctrl+Shift+E |
| `voiceInput.clearHistory`         | Löschen         | -            |
| `voiceInput.showHelp`             | Hilfe           | -            |
| `voiceInput.testMicrophone`       | Test            | -            |
| `voiceInput.resetSettings`        | Reset           | -            |

---

## 🏗️ Projektstruktur

```
voice-input-extension/
├── src/
│   ├── extension-advanced.ts     # Main Entry Point
│   ├── recognition-engine.ts     # Speech Recognition
│   ├── settings.ts               # Configuration Management
│   ├── copilot-integration.ts    # Copilot Integration
│   ├── commands.ts               # Command Handlers
│   └── analytics.ts              # Analytics & Logging
├── out/                          # Compiled JavaScript
├── .vscode/
│   ├── launch.json              # Debug Configuration
│   └── tasks.json               # Build Tasks
├── package.json                  # Extension Manifest
├── tsconfig.json                # TypeScript Config
├── build.sh                     # Build Script
├── README.md                    # Documentation
├── INSTALLATION.md              # Installation Guide
└── ARCHITECTURE.md              # This file
```

---

## 📦 Dependencies

### Development

- `@types/vscode`: VS Code API Types
- `@types/node`: Node.js Types
- `typescript`: TypeScript Compiler
- `@typescript-eslint/parser`: ESLint Parser
- `@typescript-eslint/eslint-plugin`: ESLint Plugin
- `eslint`: Code Linter

### Runtime

- `web-speech-api`: Web Speech API Polyfill (optional)

---

## 🚀 Build Process

```
TypeScript Sources (src/*.ts)
         │
         ▼
    TypeScript Compiler
    (npm run compile)
         │
         ▼
JavaScript Output (out/*.js)
         │
         ▼
VS Code Extension Bundle
```

---

## 🧪 Testing

```bash
# Lint-Fehler prüfen
npm run lint

# Tests ausführen
npm run test

# Watch-Modus für Entwicklung
npm run watch
```

---

## 📊 Performance Considerations

### Memory Management

- Session-Puffer begrenzt auf 1000 Einträge
- Event-Logs begrenzt auf 5000 Einträge
- Automatische Cleanup bei Overflow

### CPU Usage

- Lazy Loading von Modulen
- Debouncing bei Einstellungsänderungen
- Effiziente Event-Handler

### Network

- Optional Cloud-Integrationen
- Lokal-First Architecture
- Kein Tracking ohne Konsent

---

## 🔐 Security & Privacy

✅ **Local Processing**

- Alle Verarbeitung auf Benutzer-Rechner
- Keine automatischen Cloud-Uploads

✅ **Data Protection**

- Transkripte bleiben im Editor
- Analytics lokal gespeichert
- Benutzer kontrolliert Export

✅ **Permissions**

- Explizite Mikrofonberechtigung
- Settings Scope Management
- Fehlerbehandlung mit Sicherheit

---

## 🔄 State Management

### Extension State

- `isRecording`: Boolean
- `currentTranscript`: Transcript Object
- `sessionId`: String
- `sessionStartTime`: Date

### User Settings (Persistent)

- Alle Einstellungen in VS Code Settings
- Workspace & Global Scope
- Automatische Synchronisierung

### Runtime Analytics

- Session History (In-Memory)
- Event Logs (In-Memory)
- Exportierbar zu JSON/CSV

---

## 🎨 UI Components

### Status Bar

- Recording Status Indicator
- Click to Toggle
- Tooltip with Keybinding

### Output Channel

- Real-time Event Logging
- Colored Status Messages
- Auto-Show on Activity

### Dialogs

- Language Picker (QuickPick)
- Analytics Display (InfoMessage)
- Help Panel (WebView)

### Commands Palette

- Alle Befehle integriert
- Suchbar mit Kategorien
- Icons und Beschreibungen

---

## 📈 Scalability

**Kann erweitert werden mit**:

- Additional Language Support
- Custom Dictionaries
- Voice Command Macros
- Advanced Noise Filtering
- Integration mit weiteren AI Tools
- Custom Analytics Dashboards

---

**Extension Version**: 1.0.0
**Architecture Version**: 1.0
**Last Updated**: 2025-11-25
**Status**: Production Ready ✅
