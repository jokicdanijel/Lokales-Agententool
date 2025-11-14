# Beispiele für LocalAgent‑Pro

In diesem Dokument findest du Beispielanfragen und kurze Erklärungen dazu, wie LocalAgent‑Pro diese verarbeitet.

## Dateien auflisten

**Anfrage**:

```
Liste die Dateien im Verzeichnis /var/log auf
```

**Ablauf**:

1. Der Agent erkennt, dass ein Zugriff auf das Dateisystem verlangt wird.
2. Er ruft das Tool `list_files` mit dem Argument `path: "/var/log"` auf.
3. Im Sandbox‑Modus wird der Pfad unter `sandbox_path` aufgelöst (z. B. `/home/USER/localagent_sandbox/var/log`).
4. Das Ergebnis (Dateiliste) wird als Antwort zurückgegeben.

## Datei erstellen

**Anfrage**:

```
Erstelle eine Datei notes.txt mit dem Inhalt "Meine ersten Notizen"
```

**Ablauf**:

1. Der Agent ruft das Tool `write_file` mit `path: "notes.txt"` und `content: "Meine ersten Notizen"` auf.
2. Im Sandbox‑Modus wird die Datei unter `sandbox_path/notes.txt` geschrieben.
3. Nach erfolgreichem Schreiben bestätigt der Agent den Vorgang.

## Shell‑Kommando ausführen (Live‑Modus)

**Anfrage**:

```
Führe das Shell‑Kommando "ls -l" aus
```

**Ablauf**:

1. Der Agent prüft den Sandbox‑Status. Ist `sandbox: true`, gibt er einen Hinweis zurück, dass Shell‑Kommandos nur im Live‑Modus erlaubt sind.
2. Wird `sandbox` auf `false` gesetzt, ruft der Agent das Tool `run_shell` mit `cmd: "ls -l"` auf.
3. Der Konsolenoutput wird an den Benutzer zurückgegeben.

## Webseite abrufen

**Anfrage**:

```
Lade die Startseite von github.com herunter
```

**Ablauf**:

1. Der Agent ruft das Tool `fetch` mit `url: "https://github.com"` auf.
2. Die Funktion prüft, ob die Domain (`github.com`) in der Whitelist steht.
3. Der HTML‑Quelltext der Seite wird geladen und zurückgegeben (oder ein Ausschnitt davon).

## Wichtiger Hinweis

Alle Beispiele gehen davon aus, dass die entsprechenden Sicherheits‑ und Konfigurationseinstellungen korrekt gesetzt sind. Insbesondere sollte das `sandbox_path` existieren und die Whitelist den gewünschten Domainnamen enthalten. Stelle außerdem sicher, dass du die Ausführung von Shell‑Kommandos nur dann zulässt, wenn du das Risiko kennst und akzeptierst.