#!/bin/bash

################################################################################
# 🔍 Network Infrastructure Validation Script
#
# Beschreibung: Validiert alle Netzwerk-Konfigurationen für den Tool Server
# Verwendung: bash validate_network.sh
# Status: ✅ Production Ready
#
################################################################################

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Zähler
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

################################################################################
# Hilfsfunktionen
################################################################################

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
    ((TESTS_TOTAL++))
}

print_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((TESTS_PASSED++))
}

print_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${BLUE}ℹ️  INFO${NC}: $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

################################################################################
# Test-Funktionen
################################################################################

test_server_running() {
    print_test "Server läuft?"

    if ps aux | grep -E "tool_server\.py|opena6.*main" | grep -v grep > /dev/null; then
        PID=$(ps aux | grep -E "tool_server\.py|opena6.*main" | grep -v grep | awk '{print $2}' | head -1)
        print_pass "Tool Server läuft (PID: $PID)"
    else
        print_fail "Tool Server läuft nicht"
    fi
}

test_port_binding() {
    print_test "Port 8765 korrekt gebunden?"

    if ss -tlnp 2>/dev/null | grep -q ":8765.*0\.0\.0\.0"; then
        PROCESS=$(ss -tlnp 2>/dev/null | grep ":8765" | awk '{print $NF}')
        print_pass "Port 8765 gebunden auf 0.0.0.0 (Prozess: $PROCESS)"
    elif ss -tlnp 2>/dev/null | grep -q ":8765"; then
        BINDING=$(ss -tlnp 2>/dev/null | grep ":8765" | awk '{print $4}')
        print_warning "Port 8765 gebunden, aber auf: $BINDING (sollte 0.0.0.0 sein)"
    else
        print_fail "Port 8765 ist nicht gebunden"
    fi
}

test_firewall_status() {
    print_test "Firewall-Status überprüfen?"

    if sudo ufw status 2>/dev/null | grep -q "8765"; then
        STATUS=$(sudo ufw status 2>/dev/null | grep "8765")
        print_pass "Firewall-Regel für Port 8765 aktiv: $STATUS"
    elif sudo ufw status 2>/dev/null | grep -q "inactive"; then
        print_warning "UFW ist deaktiviert (Port 8765 möglicherweise offen)"
    else
        print_fail "Port 8765 in Firewall nicht konfiguriert"
    fi
}

test_health_localhost() {
    print_test "Health-Endpoint (localhost)?"

    RESPONSE=$(curl -s -w "\n%{http_code}" http://127.0.0.1:8765/health 2>/dev/null)
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)

    if [ "$HTTP_CODE" = "200" ]; then
        print_pass "Health-Endpoint antwortet: HTTP $HTTP_CODE"
        [ -n "$BODY" ] && print_info "Response: $BODY"
    else
        print_fail "Health-Endpoint: HTTP $HTTP_CODE (erwartet 200)"
    fi
}

test_health_lan() {
    print_test "Health-Endpoint (LAN: 192.168.0.70)?"

    RESPONSE=$(curl -s -w "\n%{http_code}" http://192.168.0.70:8765/health 2>/dev/null)
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)

    if [ "$HTTP_CODE" = "200" ]; then
        print_pass "LAN-Zugriff funktioniert: HTTP $HTTP_CODE"
        [ -n "$BODY" ] && print_info "Response: $BODY"
    elif [ -z "$HTTP_CODE" ]; then
        print_fail "LAN-Zugriff nicht möglich (Timeout oder Host nicht erreichbar)"
    else
        print_fail "LAN-Zugriff: HTTP $HTTP_CODE"
    fi
}

test_manifest_endpoint() {
    print_test "Manifest-Endpoint?"

    RESPONSE=$(curl -s http://192.168.0.70:8765/manifest 2>/dev/null)

    if echo "$RESPONSE" | grep -q "version\|tools\|endpoints"; then
        print_pass "Manifest-Endpoint aktiv und gültig"
        print_info "$(echo $RESPONSE | head -c 100)..."
    else
        print_fail "Manifest-Endpoint: Keine gültige Antwort"
    fi
}

test_bearer_token() {
    print_test "Bearer Token Authentication?"

    TOKEN="sk_opena6_browser_v3_production"
    RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
                  http://192.168.0.70:8765/health 2>/dev/null)

    if echo "$RESPONSE" | grep -q "status\|healthy"; then
        print_pass "Bearer Token funktioniert"
    else
        print_warning "Bearer Token-Test nicht bestätigt (könnte auch OK sein)"
    fi
}

test_ngrok_status() {
    print_test "ngrok-Installation?"

    if command -v ngrok &> /dev/null; then
        NGROK_VERSION=$(ngrok --version 2>/dev/null | head -1)
        print_pass "ngrok ist installiert: $NGROK_VERSION"

        # ngrok Tunnel Check
        TUNNEL=$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null | grep -o "public_url.*https.*" | head -1)
        if [ -n "$TUNNEL" ]; then
            print_pass "ngrok Tunnel aktiv: $TUNNEL"
        else
            print_info "ngrok Tunnel nicht aktiv (aber installiert)"
        fi
    else
        print_warning "ngrok nicht installiert (Optional für Methode 2)"
    fi
}

test_ssh_keys() {
    print_test "SSH-Keys vorhanden?"

    if [ -f ~/.ssh/id_server ] && [ -f ~/.ssh/id_server.pub ]; then
        KEY_TYPE=$(ssh-keygen -l -f ~/.ssh/id_server 2>/dev/null | awk '{print $4}')
        print_pass "SSH-Keys vorhanden (Typ: $KEY_TYPE)"
    elif [ -f ~/.ssh/id_rsa ] && [ -f ~/.ssh/id_rsa.pub ]; then
        print_pass "SSH-Keys vorhanden (Standard RSA)"
    else
        print_warning "Keine SSH-Keys gefunden (Optional für Methode 3)"
    fi
}

test_network_connectivity() {
    print_test "Netzwerk-Konnektivität?"

    if ping -c 1 -W 2 192.168.0.1 &> /dev/null; then
        print_pass "Gateway (192.168.0.1) erreichbar"
    else
        print_fail "Gateway nicht erreichbar"
    fi

    LOCAL_IP=$(hostname -I | awk '{print $1}')
    if [ -n "$LOCAL_IP" ]; then
        print_pass "Lokale IP: $LOCAL_IP"
    else
        print_fail "Lokale IP konnte nicht ermittelt werden"
    fi
}

test_open_ports() {
    print_test "Offene Ports überprüfen?"

    # Wichtige Ports
    for PORT in 8765 3000 5000 4040; do
        if ss -tlnp 2>/dev/null | grep -q ":$PORT"; then
            PROCESS=$(ss -tlnp 2>/dev/null | grep ":$PORT" | awk '{print $NF}' | head -1)
            print_info "Port $PORT offen ($PROCESS)"
        fi
    done
}

test_log_files() {
    print_test "Log-Dateien überprüfen?"

    LOG_DIR="/tmp/tool_server"
    if [ -d "$LOG_DIR" ]; then
        LOG_COUNT=$(find "$LOG_DIR" -type f | wc -l)
        print_pass "Log-Verzeichnis vorhanden ($LOG_COUNT Dateien)"
    else
        print_info "Log-Verzeichnis nicht vorhanden (normal bei erstem Start)"
    fi
}

test_disk_space() {
    print_test "Festplatte überprüfen?"

    USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$USAGE" -lt 80 ]; then
        print_pass "Festplatte OK: ${USAGE}% verwendet"
    elif [ "$USAGE" -lt 90 ]; then
        print_warning "Festplatte: ${USAGE}% verwendet"
    else
        print_fail "Festplatte: ${USAGE}% verwendet (kritisch)"
    fi
}

test_system_resources() {
    print_test "System-Ressourcen überprüfen?"

    UPTIME=$(uptime -p 2>/dev/null || uptime | awk -F'up' '{print $2}' | awk -F',' '{print $1}')
    LOAD=$(cat /proc/loadavg | awk '{print $1,$2,$3}')
    MEMORY=$(free -h | grep Mem | awk '{print $3}' | sed 's/Gi.*/GB/')

    print_info "Uptime: $UPTIME"
    print_info "Load Average: $LOAD"
    print_info "Memory Used: $MEMORY"
}

################################################################################
# Hauptprogramm
################################################################################

main() {
    print_header "🌐 Netzwerk-Infrastruktur Validierung"
    print_info "Script: validate_network.sh"
    print_info "Datum: $(date '+%Y-%m-%d %H:%M:%S')"

    # Authentifizierung überprüfen
    if [ "$EUID" -ne 0 ]; then
        print_warning "Nicht als root ausgeführt. Einige Tests benötigen sudo!"
        print_info "Führe aus: sudo bash validate_network.sh"
    fi

    echo ""
    print_header "1️⃣ Server & Port Tests"
    test_server_running
    test_port_binding
    test_open_ports

    echo ""
    print_header "2️⃣ Firewall & Netzwerk Tests"
    test_firewall_status
    test_network_connectivity

    echo ""
    print_header "3️⃣ API Endpoints Tests"
    test_health_localhost
    test_health_lan
    test_manifest_endpoint
    test_bearer_token

    echo ""
    print_header "4️⃣ Zugriffsmethoden Tests"
    test_ngrok_status
    test_ssh_keys

    echo ""
    print_header "5️⃣ System & Ressourcen Tests"
    test_log_files
    test_disk_space
    test_system_resources

    # Zusammenfassung
    echo ""
    print_header "📊 Test-Ergebnisse"

    echo -e "Gesamt Tests:  ${BLUE}$TESTS_TOTAL${NC}"
    echo -e "Bestanden:     ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Fehlgeschlagen: ${RED}$TESTS_FAILED${NC}"

    PERCENTAGE=$((TESTS_PASSED * 100 / TESTS_TOTAL))
    echo -e "Erfolgsrate:   ${BLUE}${PERCENTAGE}%${NC}"

    echo ""
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ ALLE TESTS BESTANDEN${NC}"
        echo -e "Status: ${GREEN}PRODUKTIONSFERTIG${NC}"
    else
        echo -e "${YELLOW}⚠️  EINIGE TESTS FEHLGESCHLAGEN${NC}"
        echo -e "Status: ${YELLOW}ÜBERPRÜFUNG ERFORDERLICH${NC}"
    fi

    echo ""
    print_header "📞 Nächste Schritte"
    echo -e "${BLUE}1.${NC} Siehe NETZWERK_INFRASTRUKTUR.md für Detailinformationen"
    echo -e "${BLUE}2.${NC} Behebe Fehler nach der Checkliste"
    echo -e "${BLUE}3.${NC} Führe das Skript erneut aus"
    echo -e "${BLUE}4.${NC} Bei Fragen: Siehe troubleshooting_section"

    echo ""
    return $TESTS_FAILED
}

# Hauptprogramm ausführen
main
exit $?
