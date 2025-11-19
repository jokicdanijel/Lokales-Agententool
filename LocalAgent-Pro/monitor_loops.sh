#!/bin/bash

# ========================================
# LocalAgent-Pro Loop-Detector
# Monitort Server-Logs auf Loop-Muster
# ========================================

LOG_FILE="logs/server.log"
ALERT_FILE="logs/loop_alerts.log"
CHECK_INTERVAL=5  # Sekunden

echo "🔍 LocalAgent-Pro Loop-Detector gestartet"
echo "📁 Logfile: $LOG_FILE"
echo "⏰ Check-Interval: ${CHECK_INTERVAL}s"
echo "================================================"

# Erstelle Alert-Log falls nicht vorhanden
touch "$ALERT_FILE"

# Zähler
loop_count=0
last_check_time=$(date +%s)

while true; do
    current_time=$(date +%s)
    
    # Lese letzte 50 Zeilen des Logs
    recent_logs=$(tail -50 "$LOG_FILE")
    
    # === CHECK 1: Shell-Command-Loops ===
    shell_errors=$(echo "$recent_logs" | grep -c "Exit Code: 2")
    if [ "$shell_errors" -ge 3 ]; then
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        alert_msg="[$timestamp] 🚨 LOOP ERKANNT: $shell_errors Shell-Fehler in letzten 50 Zeilen"
        echo "$alert_msg"
        echo "$alert_msg" >> "$ALERT_FILE"
        
        # Zeige betroffene Commands
        echo "$recent_logs" | grep "Shell-Kommando:" | tail -3
        
        loop_count=$((loop_count + 1))
    fi
    
    # === CHECK 2: Identische Requests ===
    # Zähle identische "Chat Completion Request" IDs
    request_pattern=$(echo "$recent_logs" | grep "Chat Completion Request" | awk '{print $NF}' | sort | uniq -c | sort -rn | head -1)
    request_count=$(echo "$request_pattern" | awk '{print $1}')
    
    if [ ! -z "$request_count" ] && [ "$request_count" -ge 3 ]; then
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        alert_msg="[$timestamp] 🔁 WIEDERHOLTE REQUESTS: $request_count identische Requests"
        echo "$alert_msg"
        echo "$alert_msg" >> "$ALERT_FILE"
        
        loop_count=$((loop_count + 1))
    fi
    
    # === CHECK 3: Ollama API Fehler ===
    ollama_errors=$(echo "$recent_logs" | grep -c "404 Client Error.*api/chat")
    if [ "$ollama_errors" -ge 2 ]; then
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        alert_msg="[$timestamp] ⚠️ OLLAMA API FEHLER: $ollama_errors Fehler (404 /api/chat)"
        echo "$alert_msg"
        echo "$alert_msg" >> "$ALERT_FILE"
    fi
    
    # === STATUS UPDATE (alle 30 Sekunden) ===
    time_diff=$((current_time - last_check_time))
    if [ "$time_diff" -ge 30 ]; then
        echo "✅ Status: $loop_count Loops erkannt seit Start"
        last_check_time=$current_time
    fi
    
    # Warte
    sleep "$CHECK_INTERVAL"
done
