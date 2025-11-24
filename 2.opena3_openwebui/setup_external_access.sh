#!/bin/bash
#
# setup_external_access.sh
# Schnelle Einrichtung für externe Server-Freigabe
#

set -e

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Konfiguration
PORT=8765
HOST="0.0.0.0"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║ Browser Agent - External Access Setup                      ║"
echo "║ Mache lokale Server für externe Geräte zugänglich         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Menü
show_menu() {
    echo ""
    echo -e "${YELLOW}Wähle Zugriffsmethode:${NC}"
    echo ""
    echo "1) LAN-Zugriff (Firewall - nur lokales Netzwerk)"
    echo "2) Internet-Zugriff (ngrok - weltweit)"
    echo "3) SSH Tunneling (sicher - zu Remote Server)"
    echo "4) Konfiguration überprüfen"
    echo "5) Alle Services neu starten"
    echo "6) Logs ansehen"
    echo "0) Beenden"
    echo ""
    read -p "Eingabe (0-6): " choice
}

# ============================================================
# Funktion: LAN Setup
# ============================================================
setup_lan() {
    echo -e "\n${BLUE}=== LAN-Zugriff Setup ===${NC}\n"

    # Lokale IP ermitteln
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        LOCAL_IP=$(hostname -I | awk '{print $1}')
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
    else
        LOCAL_IP="127.0.0.1"
    fi

    echo -e "${GREEN}✓ Lokale IP: ${LOCAL_IP}${NC}"
    echo ""

    # Überprüfe ob Port offen ist
    if ss -tlnp 2>/dev/null | grep -q ":$PORT"; then
        echo -e "${GREEN}✓ Port $PORT ist offen${NC}"
    else
        echo -e "${YELLOW}⚠ Port $PORT ist nicht offen${NC}"
    fi

    # Firewall freigeben
    echo ""
    echo -e "${BLUE}Firewall Konfiguration:${NC}"

    if command -v ufw &> /dev/null; then
        echo "UFW gefunden. Freigabe Port $PORT..."
        sudo ufw allow $PORT/tcp 2>/dev/null && \
            echo -e "${GREEN}✓ Port $PORT in UFW freigegeben${NC}" || \
            echo -e "${YELLOW}⚠ UFW Freigabe fehlgeschlagen (möglicherweise nicht aktiv)${NC}"
    fi

    # Service starten
    echo ""
    echo -e "${BLUE}Starte Tool Server...${NC}"
    echo ""
    echo "Befehl:"
    echo -e "${YELLOW}python3 $PROJECT_ROOT/LocalAgent-Pro/opena6/tool_server.py --host $HOST --port $PORT${NC}"
    echo ""

    read -p "Jetzt starten? (j/n): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Jj]$ ]]; then
        cd "$PROJECT_ROOT"
        python3 LocalAgent-Pro/opena6/tool_server.py --host "$HOST" --port "$PORT" &
        SERVER_PID=$!
        echo -e "${GREEN}✓ Server gestartet (PID: $SERVER_PID)${NC}"

        sleep 2

        # Test
        echo ""
        echo -e "${BLUE}Teste Zugriff...${NC}"
        if curl -s http://localhost:$PORT/health > /dev/null; then
            echo -e "${GREEN}✓ Lokaler Zugriff funktioniert${NC}"
            echo ""
            echo -e "${GREEN}Zugriff von anderen Geräten:${NC}"
            echo -e "  Browser:  ${YELLOW}http://$LOCAL_IP:$PORT${NC}"
            echo -e "  Terminal: ${YELLOW}curl http://$LOCAL_IP:$PORT/health${NC}"
        else
            echo -e "${RED}✗ Zugriff fehlgeschlagen${NC}"
        fi

        echo ""
        echo -e "${YELLOW}Drücke Ctrl+C um den Server zu stoppen${NC}"
    fi
}

# ============================================================
# Funktion: ngrok Setup
# ============================================================
setup_ngrok() {
    echo -e "\n${BLUE}=== ngrok Setup ===${NC}\n"

    # Überprüfe ob ngrok installiert ist
    if ! command -v ngrok &> /dev/null; then
        echo -e "${YELLOW}ngrok nicht installiert.${NC}"
        echo ""

        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "Installation:"
            echo -e "${YELLOW}brew install ngrok${NC}"
        else
            echo "Installation:"
            echo -e "${YELLOW}curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null${NC}"
            echo -e "${YELLOW}echo 'deb https://ngrok-agent.s3.amazonaws.com buster main' | sudo tee /etc/apt/sources.list.d/ngrok.list${NC}"
            echo -e "${YELLOW}sudo apt update && sudo apt install ngrok${NC}"
        fi

        read -p "Installieren? (j/n): " -n 1 -r
        echo ""

        if [[ ! $REPLY =~ ^[Jj]$ ]]; then
            return
        fi

        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install ngrok
        else
            sudo apt install -y ngrok
        fi
    fi

    echo -e "${GREEN}✓ ngrok ist installiert${NC}"
    echo ""

    # Auth Token
    if grep -q "authtoken" ~/.ngrok2/ngrok.yml 2>/dev/null; then
        echo -e "${GREEN}✓ ngrok ist authentifiziert${NC}"
    else
        echo -e "${YELLOW}ngrok ist nicht authentifiziert${NC}"
        echo ""
        echo "1. Kostenlos Account erstellen:"
        echo "   https://dashboard.ngrok.com/signup"
        echo ""
        echo "2. Auth Token abrufen:"
        echo "   https://dashboard.ngrok.com/auth/your-authtoken"
        echo ""

        read -p "Auth Token eingeben: " AUTH_TOKEN

        if [ -n "$AUTH_TOKEN" ]; then
            ngrok config add-authtoken "$AUTH_TOKEN"
            echo -e "${GREEN}✓ Token konfiguriert${NC}"
        fi
    fi

    echo ""
    echo -e "${BLUE}Starte Services...${NC}"
    echo ""

    # Starte Tool Server
    echo "Terminal 1 (Tool Server):"
    echo -e "${YELLOW}python3 $PROJECT_ROOT/LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port $PORT${NC}"
    echo ""

    read -p "Starten in Terminal 1? (j/n): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Jj]$ ]]; then
        cd "$PROJECT_ROOT"
        python3 LocalAgent-Pro/opena6/tool_server.py --host "0.0.0.0" --port "$PORT" > /tmp/tool_server.log 2>&1 &
        sleep 2
        echo -e "${GREEN}✓ Tool Server gestartet${NC}"
    fi

    # Starte ngrok
    echo ""
    echo "Terminal 2 (ngrok):"
    echo -e "${YELLOW}ngrok http $PORT${NC}"
    echo ""

    read -p "Starten in Terminal 2? (j/n): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Jj]$ ]]; then
        ngrok http $PORT &
        sleep 3

        # Zeige Tunnel URL
        TUNNEL_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | grep -o '"public_url":"[^"]*' | cut -d'"' -f4)

        if [ -n "$TUNNEL_URL" ]; then
            echo -e "${GREEN}✓ Tunnel aktiv!${NC}"
            echo ""
            echo -e "${GREEN}Public URL: ${YELLOW}$TUNNEL_URL${NC}"
            echo ""
            echo "Zugriff:"
            echo -e "  ${YELLOW}curl $TUNNEL_URL/health${NC}"
            echo -e "  Browser: ${YELLOW}$TUNNEL_URL${NC}"
        fi
    fi

    echo ""
    echo -e "${BLUE}ngrok Dashboard: ${YELLOW}http://127.0.0.1:4040${NC}"
    echo ""
    echo -e "${YELLOW}Drücke Ctrl+C um zu beenden${NC}"
}

# ============================================================
# Funktion: SSH Tunneling
# ============================================================
setup_ssh() {
    echo -e "\n${BLUE}=== SSH Tunneling Setup ===${NC}\n"

    echo "SSH Tunnel-Typen:"
    echo ""
    echo "1) Forward Tunnel  - Lokal → Remote (remote nutzt deine Services)"
    echo "2) Reverse Tunnel  - Remote → Lokal (du nutzt remote Services)"
    echo ""

    read -p "Wähle (1-2): " tunnel_type
    echo ""

    read -p "Remote Host (user@example.com): " remote_host
    read -p "Local Port [8765]: " local_port
    local_port=${local_port:-8765}
    read -p "Remote Port [8765]: " remote_port
    remote_port=${remote_port:-8765}

    if [ "$tunnel_type" = "1" ]; then
        echo ""
        echo -e "${BLUE}Forward Tunnel:${NC}"
        echo "  localhost:$local_port → $remote_host:$remote_port"
        echo ""
        echo "Befehl:"
        echo -e "${YELLOW}ssh -L $local_port:localhost:$remote_port $remote_host -N${NC}"
        echo ""

        read -p "Starten? (j/n): " -n 1 -r
        echo ""

        if [[ $REPLY =~ ^[Jj]$ ]]; then
            ssh -L $local_port:localhost:$remote_port $remote_host -N
        fi
    else
        echo ""
        echo -e "${BLUE}Reverse Tunnel:${NC}"
        echo "  $remote_host:$remote_port → localhost:$local_port"
        echo ""
        echo "Befehl:"
        echo -e "${YELLOW}ssh -R $remote_port:localhost:$local_port $remote_host -N${NC}"
        echo ""

        read -p "Starten? (j/n): " -n 1 -r
        echo ""

        if [[ $REPLY =~ ^[Jj]$ ]]; then
            ssh -R $remote_port:localhost:$local_port $remote_host -N
        fi
    fi
}

# ============================================================
# Funktion: Konfiguration überprüfen
# ============================================================
check_config() {
    echo -e "\n${BLUE}=== Konfiguration überprüfen ===${NC}\n"

    echo -e "${BLUE}System-Info:${NC}"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "  OS: Linux"
        LOCAL_IP=$(hostname -I | awk '{print $1}')
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  OS: macOS"
        LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
    else
        LOCAL_IP="127.0.0.1"
    fi
    echo "  Lokale IP: $LOCAL_IP"

    # Public IP
    PUBLIC_IP=$(curl -s https://api.ipify.org 2>/dev/null || echo "N/A")
    echo "  Öffentliche IP: $PUBLIC_IP"

    echo ""
    echo -e "${BLUE}Services:${NC}"

    # Tool Server
    if ss -tlnp 2>/dev/null | grep -q ":$PORT"; then
        echo -e "  ${GREEN}✓${NC} Port $PORT ist offen"

        if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} Tool Server läuft"
        fi
    else
        echo -e "  ${RED}✗${NC} Port $PORT ist nicht offen"
    fi

    # ngrok
    if command -v ngrok &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} ngrok installiert"
        if grep -q "authtoken" ~/.ngrok2/ngrok.yml 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} ngrok authentifiziert"
        fi
    else
        echo -e "  ${RED}✗${NC} ngrok nicht installiert"
    fi

    # SSH
    if ssh-keygen -F github.com > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} SSH konfiguriert"
    fi

    echo ""
    echo -e "${BLUE}Firewall:${NC}"

    if command -v ufw &> /dev/null; then
        UFW_STATUS=$(sudo ufw status 2>/dev/null | head -1)
        echo "  UFW: $UFW_STATUS"
    fi

    echo ""
    echo -e "${BLUE}Zugriff Test:${NC}"

    if curl -s http://localhost:$PORT/health > /dev/null; then
        echo -e "  ${GREEN}✓${NC} Lokal (127.0.0.1): OK"

        if curl -s http://$LOCAL_IP:$PORT/health > /dev/null; then
            echo -e "  ${GREEN}✓${NC} Lokal LAN ($LOCAL_IP): OK"
        fi
    else
        echo -e "  ${RED}✗${NC} Service nicht erreichbar"
    fi
}

# ============================================================
# Funktion: Services neu starten
# ============================================================
restart_services() {
    echo -e "\n${BLUE}=== Services neu starten ===${NC}\n"

    # Beende alte Prozesse
    echo "Beende alte Tool Server Prozesse..."
    pkill -f "tool_server.py" 2>/dev/null || true
    sleep 1

    echo -e "${GREEN}✓ Beendet${NC}"
    echo ""

    # Starte neue
    echo "Starte Tool Server..."
    cd "$PROJECT_ROOT"
    python3 LocalAgent-Pro/opena6/tool_server.py --host "0.0.0.0" --port "$PORT" &

    sleep 2

    if curl -s http://localhost:$PORT/health > /dev/null; then
        echo -e "${GREEN}✓ Tool Server läuft${NC}"
    else
        echo -e "${RED}✗ Fehler beim Starten${NC}"
    fi
}

# ============================================================
# Funktion: Logs ansehen
# ============================================================
view_logs() {
    echo -e "\n${BLUE}=== Logs ===${NC}\n"

    echo "1) Tool Server Logs"
    echo "2) System Logs"
    echo "3) SSH Logs"
    echo "0) Zurück"
    echo ""

    read -p "Wähle (0-3): " log_choice

    case $log_choice in
        1)
            if [ -f /tmp/tool_server.log ]; then
                tail -f /tmp/tool_server.log
            else
                echo -e "${YELLOW}Keine Logs vorhanden${NC}"
            fi
            ;;
        2)
            sudo journalctl -u python3 -f 2>/dev/null || echo "Keine Logs verfügbar"
            ;;
        3)
            sudo tail -f /var/log/auth.log 2>/dev/null || echo "Keine Zugriff auf SSH Logs"
            ;;
        *)
            return
            ;;
    esac
}

# ============================================================
# Hauptschleife
# ============================================================
while true; do
    show_menu

    case $choice in
        1) setup_lan ;;
        2) setup_ngrok ;;
        3) setup_ssh ;;
        4) check_config ;;
        5) restart_services ;;
        6) view_logs ;;
        0)
            echo -e "\n${GREEN}Auf Wiedersehen!${NC}\n"
            exit 0
            ;;
        *)
            echo -e "${RED}Ungültige Eingabe${NC}"
            ;;
    esac
done
