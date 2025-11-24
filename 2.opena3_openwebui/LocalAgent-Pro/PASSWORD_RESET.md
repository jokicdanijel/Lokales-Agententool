# 🔐 OpenWebUI Password Reset Guide

Dieses Dokument beschreibt, wie du das OpenWebUI Admin-Passwort zurücksetzen kannst.

---

## 🚨 Wann brauchst du das?

- Passwort vergessen
- Admin-Account gesperrt
- Nach initialer Installation
- Passwort-Sicherheit verbessern

---

## Methode 1: Automatisches Skript (Empfohlen)

### Schritt 1: Skript ausführen

```bash
cd LocalAgent-Pro
./update_openwebui_password.sh
```

### Schritt 2: Neues Passwort eingeben

```
🔐 OpenWebUI Password Reset
Enter new password: ********
Confirm password: ********
```

### Schritt 3: Bestätigung

```
✅ Password updated successfully!
New password hash: $2b$12$...
```

---

## Methode 2: Manuell (Docker)

### Schritt 1: Container ID finden

```bash
docker ps | grep openwebui
```

Ausgabe:
```
abc123def456  ghcr.io/open-webui/open-webui:main  Up 2 hours  0.0.0.0:3000->8080/tcp
```

### Schritt 2: In Container einloggen

```bash
docker exec -it abc123def456 bash
```

### Schritt 3: Python-Shell öffnen

```bash
python3
```

### Schritt 4: Passwort hashen

```python
import bcrypt

# Neues Passwort
new_password = "MeinNeuesPasswort123!"

# Bcrypt-Hash erstellen
password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
print(password_hash.decode('utf-8'))
```

Ausgabe:
```
$2b$12$abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOP
```

### Schritt 5: Hash kopieren

```python
# Kopiere den Hash (z.B. $2b$12$abcdef...)
exit()
```

### Schritt 6: Datenbank aktualisieren

```bash
# SQLite-Datenbank öffnen
sqlite3 /app/backend/data/webui.db

# Admin-Passwort aktualisieren
UPDATE auth SET password = '$2b$12$abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOP' WHERE id = 1;

# Prüfen
SELECT id, email, password FROM auth;

# Verlassen
.quit
```

### Schritt 7: Container neustarten

```bash
exit  # Container verlassen
docker restart abc123def456
```

---

## Methode 3: Docker Compose (Einfach)

### Schritt 1: Container stoppen

```bash
cd LocalAgent-Pro
docker-compose down
```

### Schritt 2: Volume löschen (⚠️ Achtung: Löscht alle Daten!)

```bash
docker volume rm localagent-pro_openwebui-data
```

### Schritt 3: Neu starten

```bash
docker-compose up -d
```

### Schritt 4: Neuen Admin erstellen

Öffne `http://localhost:3000` und erstelle einen neuen Admin-Account.

---

## Methode 4: Python-Skript (Host)

### Schritt 1: Skript erstellen

```bash
nano reset_password.py
```

```python
#!/usr/bin/env python3
import bcrypt
import sqlite3
import sys

def reset_password(db_path, user_id=1):
    # Neues Passwort eingeben
    new_password = input("Enter new password: ")
    confirm_password = input("Confirm password: ")
    
    if new_password != confirm_password:
        print("❌ Passwords don't match!")
        sys.exit(1)
    
    # Bcrypt-Hash erstellen
    password_hash = bcrypt.hashpw(
        new_password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    # Datenbank aktualisieren
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE auth SET password = ? WHERE id = ?",
        (password_hash, user_id)
    )
    
    conn.commit()
    conn.close()
    
    print(f"✅ Password updated successfully!")
    print(f"New hash: {password_hash}")

if __name__ == '__main__':
    # Docker Volume Pfad
    db_path = input("Database path (default: /var/lib/docker/volumes/localagent-pro_openwebui-data/_data/webui.db): ").strip()
    
    if not db_path:
        db_path = "/var/lib/docker/volumes/localagent-pro_openwebui-data/_data/webui.db"
    
    reset_password(db_path)
```

### Schritt 2: Ausführen

```bash
chmod +x reset_password.py
sudo python3 reset_password.py
```

---

## Passwort-Anforderungen

**Empfohlen:**
- Mindestens 12 Zeichen
- Groß- und Kleinbuchstaben
- Zahlen und Sonderzeichen
- Keine Wörterbuch-Wörter

**Beispiel:**
```
SecureP@ssw0rd2025!
MyLocalAgent#2025
OpenWebUI$ecure123
```

---

## Sicherheits-Tipps

### ✅ Do's

- Starke Passwörter verwenden
- Passwörter regelmäßig ändern
- 2FA aktivieren (wenn verfügbar)
- Passwort-Manager nutzen
- Bcrypt-Hashes verwenden

### ❌ Don'ts

- Passwörter in Klartext speichern
- Standard-Passwörter nutzen
- Passwörter teilen
- Schwache Hashes (MD5, SHA1)
- Passwörter in Git committen

---

## Troubleshooting

### Problem 1: Container nicht gefunden

```bash
# Alle Container anzeigen
docker ps -a

# OpenWebUI-Container finden
docker ps -a | grep openwebui
```

### Problem 2: Datenbank nicht gefunden

```bash
# Docker Volumes anzeigen
docker volume ls

# Volume inspizieren
docker volume inspect localagent-pro_openwebui-data
```

### Problem 3: Keine Berechtigung

```bash
# Mit sudo ausführen
sudo docker exec -it abc123def456 bash

# Oder Docker-Gruppe hinzufügen
sudo usermod -aG docker $USER
newgrp docker
```

### Problem 4: bcrypt nicht installiert

```bash
# In Container
pip install bcrypt

# Auf Host
pip3 install bcrypt
```

### Problem 5: SQLite-Fehler

```bash
# Datenbank-Backup erstellen
docker cp abc123def456:/app/backend/data/webui.db ./webui_backup.db

# Datenbank reparieren
sqlite3 webui_backup.db "VACUUM;"
```

---

## Automatisierung

### Cron-Job für regelmäßigen Reset (optional)

```bash
# Crontab bearbeiten
crontab -e

# Jeden Monat Passwort ändern
0 0 1 * * /path/to/LocalAgent-Pro/update_openwebui_password.sh
```

### Environment Variable

```bash
# .env
OPENWEBUI_ADMIN_PASSWORD="MySecurePassword123!"

# In docker-compose.yml
environment:
  - ADMIN_PASSWORD=${OPENWEBUI_ADMIN_PASSWORD}
```

---

## Wiederherstellung

### Backup vor Passwort-Reset

```bash
# Datenbank sichern
docker cp openwebui-container:/app/backend/data/webui.db ./backup_$(date +%Y%m%d).db

# Volume sichern
docker run --rm -v localagent-pro_openwebui-data:/data -v $(pwd):/backup ubuntu tar czf /backup/openwebui_backup.tar.gz /data
```

### Restore nach fehlgeschlagenem Reset

```bash
# Datenbank wiederherstellen
docker cp ./backup_20251121.db openwebui-container:/app/backend/data/webui.db

# Container neustarten
docker restart openwebui-container
```

---

## API-basierter Reset (Future)

**Geplant:** API-Endpoint für Passwort-Reset

```bash
curl -X POST http://localhost:3000/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "new_password": "NewSecurePassword123!"
  }'
```

---

## Weitere Ressourcen

- **Bcrypt Docs:** https://pypi.org/project/bcrypt/
- **SQLite Docs:** https://www.sqlite.org/docs.html
- **OpenWebUI GitHub:** https://github.com/open-webui/open-webui
- **Docker Exec:** https://docs.docker.com/engine/reference/commandline/exec/

---

## Beispiel-Skripte

Siehe:
- `update_openwebui_password.sh` - Automatisches Reset-Skript
- `examples/password_reset_example.sh` - Weitere Beispiele

---

**📚 Mehr:** [README.md](README.md) | [OpenWebUI Integration](OPENWEBUI_INTEGRATION.md) | [Security](SECURITY.md)
