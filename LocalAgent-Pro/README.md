# LocalAgent‑Pro

LocalAgent‑Pro ist ein komplett lokales KI‑Agentensystem, das nach dem Prinzip von ChatGPT arbeitet, jedoch ohne externe Abhängigkeiten. Es ermöglicht das Lesen und Schreiben von Dateien, das Ausführen von Shell‑Befehlen und den kontrollierten Zugriff auf das Internet über eine Whitelist.

Dieses Repository enthält sämtliche Komponenten, die du benötigst, um den Agenten auf deinem eigenen Rechner aufzusetzen und mit dem OpenAI Agent‑Builder zu verbinden.

## Inhaltsverzeichnis

1. [Features](#features)
2. [Projektstruktur](#projektstruktur)
3. [Installation](#installation)
4. [Konfiguration](#konfiguration)
5. [Agent‑Builder‑Setup](#agent‑builder‑setup)
6. [Beispiele](#beispiele)

## Features

- **Lokaler Betrieb**: Keine Verbindung zu externen ChatGPT‑Servern notwendig.
- **Sandbox‑Modus**: Sicherheitsmechanismus, der Dateizugriffe in ein isoliertes Verzeichnis umleitet.
- **Dateioperationen**: Lesen, Schreiben und Auflisten von Dateien über definierte Tools.
- **Shell‑Ausführung**: Führen von Shell‑Kommandos im Live‑Modus (standardmäßig deaktiviert).
- **Web‑Zugriff**: Abrufen von Webseiteninhalten ausschließlich von vorher definierten Domains.
- **Modularer Aufbau**: Alle Tools sind als JSON‑Definitionen verfügbar und lassen sich leicht in den OpenAI Agent‑Builder importieren.

## Projektstruktur

```
LocalAgent-Pro/
├── config/               # Konfigurationsdateien und System-Prompt
│   ├── system_prompt.txt
│   └── config.yaml
├── docs/                 # Ausführliche Dokumentation
│   ├── installation.md
│   ├── agent_builder_setup.md
│   └── examples.md
├── sandbox/              # Leeres Verzeichnis für Sandbox-Dateien
├── src/                  # Platz für zusätzlichen Source-Code
├── tools/                # Tool-Definitionen für den Agent-Builder
│   ├── all_tools.json
│   ├── read_file.json
│   ├── write_file.json
│   ├── list_files.json
│   ├── run_shell.json
│   └── fetch.json
└── setup.sh              # Installationsskript
```

## Installation

1. Stelle sicher, dass du ein Linux‑System mit Python 3 und `pip` verwendest.
2. Klone dieses Repository oder kopiere den `LocalAgent‑Pro`‑Ordner auf deinen Rechner.
3. Wechsle in das Verzeichnis und führe das Setup-Skript aus:

   ```bash
   cd LocalAgent-Pro
   bash setup.sh
   ```

   Das Skript installiert die benötigten Python‑Pakete (falls notwendig) und legt das Sandbox‑Verzeichnis an. Passe die Pfade in `config/config.yaml` an deine Umgebung an.

4. Installiere ein lokales Sprachmodell (z. B. über [Ollama](https://ollama.com/)) und starte den dazugehörigen Server. Hinterlege die API‑URL und das Modell in `config/config.yaml`.

## Konfiguration

Die Datei `config/config.yaml` enthält sämtliche Einstellungen. Wichtige Parameter:

- `sandbox`: Aktiviert (true) oder deaktiviert (false) den Sandbox‑Modus.
- `sandbox_path`: Pfad zum Sandbox‑Verzeichnis, in dem Dateien abgelegt werden, wenn der Sandbox‑Modus aktiv ist.
- `allowed_domains`: Liste der Domains, von denen Web‑Anfragen erlaubt sind.
- `llm.base_url` und `llm.model`: API‑Endpunkt und Name des lokalen Sprachmodells.

Passe diese Werte nach deinen Bedürfnissen an.

## Agent‑Builder‑Setup

Eine Anleitung zur Integration in den OpenAI Agent‑Builder findest du in der Datei [`docs/agent_builder_setup.md`](docs/agent_builder_setup.md). Dort wird beschrieben, wie du den System‑Prompt importierst und die Tools anlegst.

## Beispiele

Siehe [`docs/examples.md`](docs/examples.md) für Beispielanfragen und mögliche Workflows.

## Lizenz

Dieses Projekt steht unter keiner spezifischen Lizenz. Nutze es nach eigenem Ermessen für private oder kommerzielle Zwecke.