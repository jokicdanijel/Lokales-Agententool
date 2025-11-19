## Ziel

Kurze, handlungsorientierte Hinweise für KI-Coding-Agenten, damit sie in diesem Repo sofort produktiv sind.

## Aktueller Repository-Status (erkennbar)

- Aktuell sind keine Quellcode- oder Manifestdateien im Workspace sichtbar.
- Es existieren VS Code tasks (siehe Workspace Tasks):
  - `GCPT Koordinator starten` — startet einen einfachen Python-HTTP-Server und eine SQLite-Datei `projekte.db`. Der Server bietet:
    - GET `/api/projekte` — listet Projekte
    - POST `/api/projekte` — legt ein Projekt an
    - Statisch gerenderte HTML-Seite unter `/` (UI + JS zur Anzeige/Speicherung)
    - Liefert standardmäßig auf Port 5001
  - `build` — ruft `msbuild` auf (falls .NET-Projektdateien vorhanden sind)

Wenn du diese Datei siehst: passe Verhalten an den tatsächlichen Code an; viele Hinweise hier sind conditional, weil das Repo derzeit leer wirkt.

## Wie du vorgehst (konkrete Checkliste für Agenten)

1. Workspace-Scan: Suche nach typischen Manifesten und Einstiegspunkten in dieser Reihenfolge: `package.json`, `pyproject.toml`, `requirements.txt`, `Pipfile`, `requirements-dev.txt`, `setup.py`, `Cargo.toml`, `pom.xml`, `*.sln`, `Dockerfile`, `.github/workflows/**`.
2. Falls nichts gefunden: Informiere den Nutzer, dass das Repo leer ist und biete 2–3 sinnvolle Starter-Vorschläge (z. B. minimaler Flask-API-Server, Node/Express-Template, .NET WebAPI) — frage nach Präferenz.
3. Falls die oben beschriebene Task `GCPT Koordinator starten` existiert: starte sie lokal (oder bitte den Nutzer, sie zu starten), öffne `http://localhost:5001` und überprüfe das Verhalten der Endpunkte `/` und `/api/projekte`.
4. Suche nach persistantem Storage: `projekte.db` (SQLite) — Änderungen an API-Endpunkten müssen die DB-Migration/Schema-Änderung berücksichtigen.
5. Wenn du Code änderst: suche nach einheitlichen Patterns (z. B. serverseitig: handler functions im gleichen Modul; clientseitig: inline HTML+JS) und erweitere beide Seiten konsistent.

## Projekt-spezifische Hinweise (aus Tasks/Server-Code ableitbar)

- Der simple HTTP-Server kombiniert UI und API in einer Datei. Bei Erweiterungen:
  - Ändere sowohl HTML/JS (client) als auch die Handler-Methoden (`do_GET`/`do_POST`) zusammen.
  - `projekte.db` wird per SQLite direkt vom Server verwaltet; keine ORM/Frameworks im Task-Code — migrations bewusst minimal halten.
- Konvention: Timestamps werden als ISO-8601-Strings in Spalte `erstellt_am` gespeichert.

## Dev-/Debug-Workflows

- Schnelles Locally-run: Verwende die vorhandene VS Code Task `GCPT Koordinator starten` zum Starten des Demo-Servers (Port 5001).
- Falls ein .NET-Solution (`*.sln`) oder `msbuild`-konfigurationen auftauchen: nutze die `build`-Task (Label: `build`) um projektübergreifende Builds zu starten.
- Tests: Falls erkannt, führe lokale Test-Runner (`pytest`, `npm test`, `dotnet test`) — otherwise, be explicit and ask the user to add tests before making behavioural changes.

## Patterns & Anti-Patterns

- Pattern: kleine, single-file demo-Server mit inlined HTML+JS. Wenn du daraus ein Feature machst, splitte server/static in `server/` und `static/` oder nutze ein minimal templating (Flask/Jinja, Express/EJS) — aber frage vorher.
- Anti-Pattern zu vermeiden: direkte destructive DB-Änderungen ohne Migration oder Backup. Bei Änderungen am Schema: erst Migration-Skript oder neue DB-Version anlegen.

## Integration Points

- Local SQLite DB: `projekte.db`
- HTTP API endpoints: `/api/projekte` (GET, POST), root `/` serves UI
- Default dev port: 5001 (siehe Task)

## Beispiele für nützliche, präzise Aufforderungen an dich (Agent)

- "Finde alle Manifestdateien und gib mir eine Prioritätenliste der Build- / Run- Befehle." 
- "Starte den Demo-Server lokal (oder beschreibe exakt, wie ich das lokal mit Python starte) und rufe `/api/projekte` ab — gib Antwort-JSON-Beispiel." 
- "Füge `DELETE /api/projekte/:id` hinzu: erstelle Server-Handler, teste manuell gegen laufenden Server und dokumentiere die Änderung in README."

## Chat-Local-Skript Nutzung

Falls das Skript `chat-local.sh` im Repo existiert, kannst du damit lokale Agenten-Interaktionen ausführen:

```bash
./chat-local.sh 'Liste alle Dateien im workspace Verzeichnis auf'
./chat-local.sh 'Erstelle eine Datei hello.txt mit "Hallo Welt"'
./chat-local.sh 'Zeige mir den Inhalt von config.yaml'
./chat-local.sh 'Wie trainiere ich ein neuronales Netz?'
```

Diese Beispiele zeigen typische Anwendungsfälle: Dateisystem-Operationen, Datei-Erstellung, Lesen von Configs und allgemeine Wissensfragen. 

## Commit- und PR-Konvention für Agenten

- Kleine, getestete Commits mit erklärendem Commit-Text. Wenn du API-Contracts änderst: erhöhe minor/patch in README und dokumentiere Migrationsschritte.

---
Wenn etwas unklar ist oder du Zugriff auf weitere Dateien brauchst, frage den Repo-Besitzer nach fehlenden Pfaden oder bevorzugten Technologie-Stacks. Soll ich die Datei ins Repo schreiben und eine erste Iteration eines README/Scaffold-Vorschlags anlegen? 
