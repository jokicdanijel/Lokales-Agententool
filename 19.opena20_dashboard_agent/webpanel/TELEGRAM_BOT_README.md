# Telegram Bot - Dokumentation

## 🤖 Übersicht

Einfacher Telegram-Bot für das OpenA20 Dashboard-Projekt.

**Bot Token:** `8520488903:AAFwH0XNHk-YPsc_1z1xuqbqrH7BV3Z0tZY`

## 📦 Installation

### Voraussetzungen

```bash
# Python 3.8+ erforderlich
python3 --version

# Telegram-Bibliothek installieren
pip install python-telegram-bot --upgrade
```

### Dependencies

```bash
pip install python-telegram-bot>=20.0
```

## 🚀 Verwendung

### Methode 1: Mit Start-Script (empfohlen)

```bash
# Ausführbar machen
chmod +x start_telegram_bot.sh

# Bot starten
./start_telegram_bot.sh start

# Bot-Status prüfen
./start_telegram_bot.sh status

# Logs anzeigen (live)
./start_telegram_bot.sh logs

# Bot stoppen
./start_telegram_bot.sh stop

# Bot neustarten
./start_telegram_bot.sh restart
```

### Methode 2: Direkt mit Python

```bash
# Im Vordergrund
python3 telegram_bot.py

# Im Hintergrund
nohup python3 telegram_bot.py > telegram_bot.log 2>&1 &

# Prozess finden
ps aux | grep telegram_bot

# Stoppen
pkill -f telegram_bot.py
```

### Methode 3: Als Systemd-Service

```bash
# Service-Datei erstellen
sudo nano /etc/systemd/system/telegram-bot.service
```

```ini
[Unit]
Description=Telegram Bot für OpenA20 Dashboard
After=network.target

[Service]
Type=simple
User=danijel-jd
WorkingDirectory=/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.opena20_dashboard_agent/webpanel
ExecStart=/usr/bin/python3 /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.opena20_dashboard_agent/webpanel/telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Service aktivieren und starten
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

# Status prüfen
sudo systemctl status telegram-bot

# Logs anzeigen
sudo journalctl -u telegram-bot -f
```

## 📱 Bot-Befehle

Der Bot unterstützt folgende Befehle in Telegram:

- `/start` - Startet den Bot und zeigt Willkommensnachricht
- `/help` - Zeigt Hilfe und verfügbare Befehle
- `/info` - Zeigt Bot-Informationen (Chat-ID, User-ID)

Zusätzlich:

- Jede Text-Nachricht wird als Echo zurückgesendet

## 🔧 Konfiguration

### Token ändern

Bearbeiten Sie `telegram_bot.py`:

```python
TELEGRAM_BOT_TOKEN = "IHR_NEUER_TOKEN"
```

### Weitere Handler hinzufügen

Beispiel für einen neuen Befehl:

```python
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler für /status Kommando"""
    await update.message.reply_text("🟢 Bot läuft einwandfrei!")

# In main() hinzufügen:
application.add_handler(CommandHandler("status", status_command))
```

## 🐛 Troubleshooting

### Bot startet nicht

```bash
# Prüfen ob Port belegt ist
netstat -tuln | grep 8443

# Python-Dependencies prüfen
pip list | grep telegram

# Token validieren
curl https://api.telegram.org/bot8520488903:AAFwH0XNHk-YPsc_1z1xuqbqrH7BV3Z0tZY/getMe
```

### Bot reagiert nicht

```bash
# Logs prüfen
cat telegram_bot.log

# Oder mit Systemd:
sudo journalctl -u telegram-bot -n 50

# Webhook-Status prüfen
curl https://api.telegram.org/bot8520488903:AAFwH0XNHk-YPsc_1z1xuqbqrH7BV3Z0tZY/getWebhookInfo
```

### Prozess hängt

```bash
# Bot forciert stoppen
pkill -9 -f telegram_bot.py

# Neu starten
./start_telegram_bot.sh start
```

## 📊 Monitoring

### Logs überwachen

```bash
# Live-Logs
tail -f telegram_bot.log

# Letzte 100 Zeilen
tail -n 100 telegram_bot.log

# Nach Fehlern suchen
grep -i error telegram_bot.log
```

### Prozess-Status

```bash
# Läuft der Bot?
./start_telegram_bot.sh status

# Oder manuell:
ps aux | grep telegram_bot.py
```

## 🔐 Sicherheit

⚠️ **WICHTIG:**

- Token NIEMALS in Git committen
- Verwenden Sie `.env`-Dateien oder Umgebungsvariablen
- Setzen Sie restrictive Dateiberechtigungen: `chmod 600 telegram_bot.py`

### Empfohlene Konfiguration mit .env

```bash
# .env erstellen
echo "TELEGRAM_BOT_TOKEN=8520488903:AAFwH0XNHk-YPsc_1z1xuqbqrH7BV3Z0tZY" > .env

# In .gitignore aufnehmen
echo ".env" >> .gitignore
```

```python
# Im Bot laden:
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
```

## 📚 Weitere Ressourcen

- [python-telegram-bot Dokumentation](https://docs.python-telegram-bot.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [BotFather](https://t.me/botfather) - Bot-Verwaltung

## 🆘 Support

Bei Problemen:

1. Logs prüfen (`telegram_bot.log`)
2. Token validieren
3. Python-Dependencies aktualisieren: `pip install -U python-telegram-bot`

## 📝 Changelog

### v1.0.0 - 23.12.2025

- ✅ Initiale Version
- ✅ Basis-Befehle (/start, /help, /info)
- ✅ Echo-Handler für Nachrichten
- ✅ Error-Handler
- ✅ Start-Script mit Management-Funktionen
