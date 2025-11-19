#!/bin/bash
# LocalAgent-Pro Autostart Script
# Startet alle Services nach System-Reboot

LOG_FILE="/home/danijel-jd/Dokumente/Workspace/Projekte/Lokales Agententool/LocalAgent-Pro/logs/autostart.log"
echo "===========================================" >> "$LOG_FILE"
echo "$(date): Autostart gestartet" >> "$LOG_FILE"

# 1. Warte auf Ollama
echo "$(date): Warte auf Ollama..." >> "$LOG_FILE"
sleep 5
systemctl is-active ollama >> "$LOG_FILE" 2>&1

# 2. Starte Docker Container
echo "$(date): Starte Docker Container..." >> "$LOG_FILE"
docker start open-webui comfyui grafana-elion prometheus-elion watchtower >> "$LOG_FILE" 2>&1

# 3. Warte bis Container laufen
sleep 10

# 4. Aktiviere venv und starte LocalAgent-Pro Server
echo "$(date): Starte LocalAgent-Pro Server..." >> "$LOG_FILE"
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Lokales\ Agententool/LocalAgent-Pro
source /home/danijel-jd/Dokumente/Workspace/Projekte/Lokales\ Agententool/.venv/bin/activate
nohup python src/openwebui_agent_server.py >> logs/server.log 2>&1 &

# 5. Status prüfen
sleep 5
echo "$(date): Docker Status:" >> "$LOG_FILE"
docker ps --format "{{.Names}}: {{.Status}}" >> "$LOG_FILE"

echo "$(date): LocalAgent-Pro Status:" >> "$LOG_FILE"
curl -sS http://192.168.0.70:8001/health >> "$LOG_FILE" 2>&1

echo "$(date): Autostart abgeschlossen" >> "$LOG_FILE"
