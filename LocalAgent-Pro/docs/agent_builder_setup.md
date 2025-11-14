# Agent‑Builder‑Setup für LocalAgent‑Pro

Dieses Dokument erklärt, wie du LocalAgent‑Pro in den OpenAI Agent‑Builder integrierst. Ziel ist es, dass dein lokaler Agent die bereitgestellten Tools verwenden kann, um Dateisystem‑, Shell‑ und Web‑Operationen auszuführen.

## 1. Workflow anlegen

1. Melde dich auf [platform.openai.com](https://platform.openai.com/) an und öffne den Agent‑Builder.
2. Klicke auf „New Agent“ oder wähle einen vorhandenen Agent‑Entwurf aus.
3. Vergib einen Namen und optional eine Beschreibung für den Agenten.

## 2. System‑Prompt importieren

1. Öffne die Datei `config/system_prompt.txt` in diesem Repository.
2. Kopiere den gesamten Inhalt.
3. Füge ihn im Agent‑Builder in das Feld „System Instructions“ bzw. „Core Prompt“ ein. Damit legt du fest, wie sich der Agent verhalten soll.

## 3. Tools definieren

LocalAgent‑Pro verwendet fünf Tools. Diese müssen im Agent‑Builder als „Functions“ angelegt werden.

1. Öffne das Verzeichnis `tools/` und öffne `all_tools.json`. Dort findest du die vollständigen JSON‑Definitionen der Tools.
2. Für jedes Tool (read_file, write_file, list_files, run_shell, fetch):
   - Klicke im Agent‑Builder auf „Add Function“.
   - Gib den Namen des Tools aus der JSON‑Datei an.
   - Kopiere die `description` in das Beschreibungsfeld.
   - Kopiere den Abschnitt unter `parameters` in das JSON‑Schema‑Feld. Stelle sicher, dass die Struktur korrekt übernommen wird.
3. Wiederhole dies für alle Tools.

## 4. Konfiguration anpassen

Die Parameter für Sandbox‑Modus, Sandbox‑Pfad, Whitelist und LLM befinden sich in `config/config.yaml`. Passe sie vor dem Start des Agenten an deine Umgebung an. Der Agent‑Builder selbst speichert keine Umgebungsvariablen – die Tools nutzen diese Datei auf dem Server, auf dem dein Agent‑Backend läuft.

## 5. Agent testen

1. Speichere die Einstellungen im Agent‑Builder.
2. Starte deinen lokalen Agent‑Server (z. B. die Flask‑App, die auf die Tools zugreift).
3. Richte in OpenWebUI einen Custom Endpoint ein, der auf den lokalen Agent‑Server zeigt (z. B. `http://localhost:8001/agent`).
4. Führe Testanfragen aus, z. B.:
   - „Liste alle Dateien im aktuellen Verzeichnis auf“
   - „Erstelle eine Datei hello.py mit dem Inhalt print('Hallo Welt')“
   - „Lade die Wikipedia‑Seite über Künstliche Intelligenz herunter und gib die ersten 500 Zeichen zurück“

Wenn alles korrekt eingerichtet ist, sollte dein lokaler Agent echte Datei‑Operationen ausführen und Webseiten abfragen können, ohne den sicheren Rahmen zu verlassen.