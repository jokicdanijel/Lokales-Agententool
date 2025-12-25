# CLI Auto-Completion für hdctl

## Overview

`hdctl` (Hyper-Dashboard Control) bash completion bietet intelligente Auto-Vervollständigung für:

- **Hauptbefehle:** `login`, `logout`, `pages`, `users`, `jobs`, `env`, `help`, `version`
- **Subcommands:** Dynamische Optionen basierend auf Kontext
- **Dynamische Werte:** Page IDs, Usernames, Job IDs aus API

## Installation

### Option 1: Benutzer-Installation (Empfohlen)

```bash
bash scripts/install_completion.sh --user
```

Installiert zu: `~/.bash_completion.d/hdctl`

Danach neue Terminal-Session starten oder in aktueller Session:

```bash
source ~/.bash_completion.d/hdctl
```

### Option 2: System-wide Installation

```bash
sudo bash scripts/install_completion.sh --system
```

Installiert zu: `/etc/bash_completion.d/hdctl`
Verfügbar für alle Benutzer nach Terminal-Neustart

### Option 3: Manuelle Installation

```bash
# Kopieren Sie die Completion-Datei manuell
cp contrib/completion/hdctl.bash ~/.bash_completion.d/hdctl

# Oder sourcing in ~/.bashrc
echo "source /path/to/contrib/completion/hdctl.bash" >> ~/.bashrc
```

## Verwendungsbeispiele

### Basis-Auto-Completion

```bash
# Listet verfügbare Befehle
$ hdctl <TAB><TAB>
login    logout   pages    users    jobs     env      help     version

# Wähle 'pages'
$ hdctl pages <TAB><TAB>
list      view      create    update    delete    search

# Wähle 'view'
$ hdctl pages view <TAB><TAB>
1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  16
```

### Dynamische Page IDs

Die Completion ruft die Agenda API ab, um aktuelle Page IDs zu holen:

```bash
$ hdctl pages view 1<TAB>
# Schlägt vor: 1, 10, 11, 12, 13, 14, 15, 16

$ hdctl pages delete 5<TAB>
# Findet: 5

$ hdctl pages update 8<TAB>
# Zeigt: 8
```

### User-Vervollständigung

```bash
$ hdctl users delete <TAB><TAB>
admin    user1    user2    developer    viewer

$ hdctl users roles admin<TAB>
# Schließt ab zu 'admin'
```

### Job-Verwaltung

```bash
$ hdctl jobs cancel <TAB><TAB>
job-001  job-002  job-003  job-004

$ hdctl jobs status <TAB><TAB>
job-001  job-002  job-003  job-004
```

### Environment-Variablen

```bash
$ hdctl env get HDCTL<TAB><TAB>
HDCTL_TOKEN   HDCTL_API   HDCTL_DEBUG

$ hdctl env set PATH<TAB>
# Schlägt aktuelle PATH vor
```

## Konfiguration

### Umgebungsvariablen

Für dynamische Completion können Sie diese Variablen setzen:

```bash
# Bearer Token für API-Authentifizierung
export HDCTL_TOKEN="250886"

# API Base URL
export HDCTL_API="http://127.0.0.1:12399"
```

Setzen Sie diese in `~/.bashrc` für permanente Konfiguration:

```bash
echo 'export HDCTL_TOKEN="250886"' >> ~/.bashrc
echo 'export HDCTL_API="http://127.0.0.1:12399"' >> ~/.bashrc
```

### Custom API Endpoint

```bash
# Einmalige Verwendung
HDCTL_API="http://api.example.com" hdctl pages <TAB><TAB>

# Oder in ~/.bashrc
export HDCTL_API="http://api.example.com"
```

## Kommandreferenz

### login

Authentifizierung mit Benutzer/Passwort

```bash
hdctl login admin
hdctl login developer
```

Auto-Completion: Listet bekannte Benutzer

### pages

Verwaltung von Agenda-Seiten

```bash
hdctl pages list              # Alle Seiten anzeigen
hdctl pages view 5            # Seite 5 ansehen
hdctl pages create            # Neue Seite erstellen
hdctl pages update 3          # Seite 3 bearbeiten
hdctl pages delete 7          # Seite 7 löschen
hdctl pages search workflow   # Nach 'workflow' suchen
```

Auto-Completion: Page IDs 1-16 (oder dynamisch von API)

### users

Benutzerverwaltung

```bash
hdctl users list              # Alle Benutzer
hdctl users create            # Neuen Benutzer erstellen
hdctl users delete admin      # Benutzer löschen
hdctl users roles admin       # Rollen anzeigen/ändern
```

Auto-Completion: Benutzernames von API

### jobs

Job-Verwaltung

```bash
hdctl jobs list               # Alle Jobs
hdctl jobs view job-001       # Job Details
hdctl jobs cancel job-002     # Job abbrechen
hdctl jobs status job-003     # Job Status
```

Auto-Completion: Job IDs von API

### env

Environment-Variablen

```bash
hdctl env list                # Alle Variablen
hdctl env get PATH            # Variable auslesen
hdctl env set DEBUG=1         # Variable setzen
hdctl env unset DEBUG         # Variable löschen
```

Auto-Completion: Umgebungsvariablen

### help

Hilfe anzeigen

```bash
hdctl help                    # Allgemeine Hilfe
hdctl help pages              # Hilfe für 'pages' Befehl
hdctl help users              # Hilfe für 'users' Befehl
```

### version

Version anzeigen

```bash
hdctl version
```

## Fehlerbehebung

### Completion funktioniert nicht

**Problem:** `hdctl <TAB>` zeigt keine Vorschläge

**Lösung:**

1. Prüfen, ob Datei installiert ist:

   ```bash
   ls -la ~/.bash_completion.d/hdctl
   ```

2. Source die Datei manuell:

   ```bash
   source ~/.bash_completion.d/hdctl
   ```

3. Prüfen Sie `~/.bashrc`:

   ```bash
   grep "bash_completion" ~/.bashrc
   ```

4. Neue Shell-Session starten:
   ```bash
   exec bash
   ```

### Dynamische Completion funktioniert nicht

**Problem:** Page IDs werden nicht vorgeschlagen

**Lösung:**

1. Prüfen Sie, ob API läuft:

   ```bash
   curl -s -H "Authorization: Bearer 250886" http://127.0.0.1:12399/health
   ```

2. Prüfen Sie Token:

   ```bash
   echo $HDCTL_TOKEN
   ```

3. Prüfen Sie API URL:

   ```bash
   echo $HDCTL_API
   ```

4. Test API-Abfrage manuell:
   ```bash
   curl -s -H "Authorization: Bearer 250886" http://127.0.0.1:12399/agenda/pages | jq '.[].id'
   ```

### "command not found: hdctl"

**Problem:** Befehl nicht gefunden

**Lösung:**

1. Prüfen Sie, ob `hdctl` im PATH ist:

   ```bash
   which hdctl
   ```

2. Registrieren Sie den Befehl:
   ```bash
   alias hdctl="bash bin/hdctl.sh"
   echo 'alias hdctl="bash bin/hdctl.sh"' >> ~/.bashrc
   ```

## Advanced: Completion anpassen

### Eigene Commands hinzufügen

Bearbeiten Sie `contrib/completion/hdctl.bash` und erweitern Sie die `commands` Variable:

```bash
local commands="login logout pages users jobs env help version custom-cmd"
```

Dann fügen Sie einen neuen case Branch hinzu:

```bash
custom-cmd)
    local subcommands="action1 action2 action3"
    if [[ $COMP_CWORD -eq 2 ]]; then
        COMPREPLY=($(compgen -W "$subcommands" -- "$cur"))
    fi
    ;;
```

### API Timeout anpassen

Standard: 2 Sekunden. Bearbeiten Sie in `hdctl.bash`:

```bash
# Von:
curl -s -m 2 \

# Zu (z.B. 5 Sekunden):
curl -s -m 5 \
```

### Statische Fallback-Liste ändern

Wenn API nicht erreichbar, fallback auf statische Liste. Bearbeiten Sie:

```bash
if [[ -z "$pages" ]]; then
    pages=$(seq 1 16)  # Anpassen Sie hier
fi
```

## Makefile Integration

Installieren Sie Completion über Makefile:

```bash
# In Makefile hinzufügen:
.PHONY: install-completion uninstall-completion

install-completion:
	@bash scripts/install_completion.sh --user
	@echo "✓ CLI completion installed"

uninstall-completion:
	@rm -f ~/.bash_completion.d/hdctl
	@echo "✓ CLI completion removed"
```

Dann verwenden Sie:

```bash
make install-completion
make uninstall-completion
```

## Performance-Tipps

1. **API-Timeout reduzieren:** Falls API schnell antwortet, reduzieren Sie timeout:

   ```bash
   curl -s -m 1 \  # 1 Sekunde statt 2
   ```

2. **Caching implementieren:** Für häufig abgerufene Daten:

   ```bash
   # Erstellen Sie einen Cache:
   CACHE_FILE="/tmp/hdctl_completion_cache"
   CACHE_AGE=$(($(date +%s) - $(stat -f%m "$CACHE_FILE" 2>/dev/null || echo 0)))
   ```

3. **Offline-Fallback:** Completion funktioniert auch ohne API (statische Liste)

## Siehe auch

- `scripts/install_completion.sh` – Installation Script
- `contrib/completion/hdctl.bash` – Completion Source
- `.github/cpp-makefile-guide.md` – Build System
- `docs/OPENWEBUI_API.md` – API Dokumentation

---

**Last Updated:** 2025-11-11
**Status:** ✅ Production Ready
