#!/bin/bash
# Telegram Bot Starter Script
# Verwendung: ./start_telegram_bot.sh

set -e

BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOT_SCRIPT="$BOT_DIR/telegram_bot.py"
PID_FILE="$BOT_DIR/telegram_bot.pid"
LOG_FILE="$BOT_DIR/telegram_bot.log"

# Funktion: Bot starten
start_bot() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "❌ Bot läuft bereits (PID: $PID)"
            exit 1
        else
            echo "⚠️  Alte PID-Datei gefunden, lösche..."
            rm "$PID_FILE"
        fi
    fi

    echo "🤖 Starte Telegram Bot..."
    nohup python3 "$BOT_SCRIPT" > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"

    sleep 2

    if ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
        echo "✅ Bot erfolgreich gestartet (PID: $(cat "$PID_FILE"))"
        echo "📝 Logs: tail -f $LOG_FILE"
    else
        echo "❌ Bot konnte nicht gestartet werden"
        cat "$LOG_FILE"
        exit 1
    fi
}

# Funktion: Bot stoppen
stop_bot() {
    if [ ! -f "$PID_FILE" ]; then
        echo "❌ Bot läuft nicht (keine PID-Datei)"
        exit 1
    fi

    PID=$(cat "$PID_FILE")

    if ps -p "$PID" > /dev/null 2>&1; then
        echo "🛑 Stoppe Bot (PID: $PID)..."
        kill "$PID"
        sleep 2

        if ps -p "$PID" > /dev/null 2>&1; then
            echo "⚠️  Bot reagiert nicht, forciere Stop..."
            kill -9 "$PID"
        fi

        rm "$PID_FILE"
        echo "✅ Bot gestoppt"
    else
        echo "❌ Bot läuft nicht mehr (PID: $PID)"
        rm "$PID_FILE"
    fi
}

# Funktion: Bot-Status prüfen
status_bot() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "✅ Bot läuft (PID: $PID)"
            echo "📝 Logs: tail -f $LOG_FILE"
        else
            echo "❌ Bot läuft nicht (tote PID-Datei)"
        fi
    else
        echo "❌ Bot läuft nicht"
    fi
}

# Funktion: Bot-Logs anzeigen
logs_bot() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo "❌ Keine Logs gefunden"
    fi
}

# Funktion: Bot neustarten
restart_bot() {
    echo "🔄 Starte Bot neu..."
    if [ -f "$PID_FILE" ]; then
        stop_bot
        sleep 1
    fi
    start_bot
}

# Hauptlogik
case "${1:-start}" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    status)
        status_bot
        ;;
    restart)
        restart_bot
        ;;
    logs)
        logs_bot
        ;;
    *)
        echo "Verwendung: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Befehle:"
        echo "  start   - Startet den Bot"
        echo "  stop    - Stoppt den Bot"
        echo "  restart - Startet den Bot neu"
        echo "  status  - Zeigt den Bot-Status"
        echo "  logs    - Zeigt die Bot-Logs (live)"
        exit 1
        ;;
esac
