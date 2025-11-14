# Installation von LocalAgent‑Pro

In diesem Dokument erfährst du, wie du LocalAgent‑Pro auf deinem lokalen Linux‑System installierst und einrichtest.

## Voraussetzungen

- Ein Linux‑Betriebssystem (getestet mit Ubuntu, Debian, Fedora, Arch und Linux Mint).
- Python 3.x inklusive `pip`.
- Optional: Ein lokales LLM, z. B. [Ollama](https://ollama.com/).

## Schritte

1. **Repository klonen oder kopieren**

   Lade den Ordner `LocalAgent‑Pro` auf deinen Rechner. Wenn du das Repository geclont hast, wechsle in das Verzeichnis:

   ```bash
   cd LocalAgent-Pro
   ```

2. **Setup-Skript ausführen**

   Führe das Installationsskript aus, um das Sandbox‑Verzeichnis anzulegen und notwendige Pakete zu installieren:

   ```bash
   bash setup.sh
   ```

   Das Skript führt folgende Schritte aus:
   - Aktualisierung der Paketliste (`apt update`).
   - Installation von Python 3 und `pip`, falls sie noch nicht installiert sind.
   - Erstellung eines Sandbox‑Verzeichnisses unter `$HOME/localagent_sandbox`.

3. **Konfiguration anpassen**

   Öffne die Datei `config/config.yaml` und passe folgende Einstellungen an:

   - `sandbox`: Setze auf `false`, wenn du direkt im Live‑Dateisystem arbeiten möchtest. Für erste Tests empfiehlt sich `true`.
   - `sandbox_path`: Lege hier das Verzeichnis fest, in dem Dateien im Sandbox‑Modus gespeichert werden.
   - `allowed_domains`: Liste der Domains, die für Web‑Requests zugelassen sind.
   - `llm.base_url`: URL deines lokalen LLM‑Servers (z. B. `http://localhost:11434/v1` für Ollama).
   - `llm.model`: Name des Modells, das dein LLM‑Server verwendet.

4. **Lokales Sprachmodell installieren**

   LocalAgent‑Pro nutzt ein Sprachmodell über eine OpenAI‑kompatible API. Mit [Ollama](https://ollama.com/) kannst du ein Modell wie LLaMA 3 lokal installieren und den Dienst starten:

   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama run llama3:instruct
   ollama serve
   ```

   Hinterlege anschließend die API‑URL und das Modell in `config/config.yaml`.

5. **Optional: Benötigte Python‑Pakete installieren**

   Wenn dein Agent zusätzliche Python‑Abhängigkeiten benötigt, installiere sie mit `pip` (z. B. `flask`, `pyyaml`, `requests`).

## Fertig!

Nach der Installation kannst du den Agenten mit dem OpenAI Agent‑Builder verbinden. Lies dafür weiter in [`docs/agent_builder_setup.md`](agent_builder_setup.md).