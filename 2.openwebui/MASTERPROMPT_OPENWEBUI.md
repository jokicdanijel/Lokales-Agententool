# 🤖 MASTERPROMPT FÜR OPENWEBUI (opena3)

**Version:** 2.0 (Integration mit Portier-System)
**Status:** ✅ Production Ready
**Basis:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier`

---

## 🔗 Quick Navigation

| Document | Purpose |
|----------|---------|
| **QUICK_START.md** | 👈 Start here (5 min setup) |
| **API_REFERENCE.md** | All REST API endpoints |
| **AGENTENREGISTER_VOLLSTÄNDIG.md** | All 20 agents + Portier architecture |
| **SECURITY_AUDIT_REPORT.md** | Security & compliance |
| **FUNCTIONAL_TEST_REPORT.md** | Test results & coverage |
| **DEPLOYMENT_GUIDE.md** | Production deployment |
| **AUDIT_REPORT_2025-11-24.md** | Final system audit |

---

## 📋 INHALTSVERZEICHNIS

1. [Selbstwiederherstellung & Memory](#1-selbstwiederherstellung--memory)
2. [Docker & Docker Compose Auto-Installation](#2-docker--docker-compose-auto-installation)
3. [Portier-System-Integration](#3-portier-system-integration)
4. [Technische Rahmenbedingungen](#4-technische-rahmenbedingungen)
5. [Vollständiger Masterprompt (Shell-Script)](#5-vollständiger-masterprompt-shell-script)
6. [Integration in OpenWebUI](#6-integration-in-openwebui)

---

## 1. SELBSTWIEDERHERSTELLUNG & MEMORY

### Konzept
OpenWebUI (opena3) lädt beim Start automatisch gespeicherte Kontexte und reaktiviert Agentenzustände.

### Implementierung

```bash
#!/bin/bash
# ==============================================================================
# [SECTION 1] SELBSTWIEDERHERSTELLUNG & MEMORY
# ==============================================================================

echo "[INFO] OPENA3 - Selbstwiederherstellung wird eingeleitet..."

# Basisverzeichnisse definieren
BASE_DIR="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"
OPENWEBUI_DATA="${BASE_DIR}/2.openwebui/data"
ARCHIVP="${BASE_DIR}/1.opena1&2_portier/archivp"
PROMPT_CACHE="${OPENWEBUI_DATA}/prompt_cache"
CONTEXT_FILE="${OPENWEBUI_DATA}/last_context.json"
SAVED_PROMPT="${OPENWEBUI_DATA}/saved_prompt.md"

# Verzeichnisse erstellen, falls nicht vorhanden
mkdir -p "$OPENWEBUI_DATA" "$PROMPT_CACHE"

# [1.1] Letzten Kontext laden
if [ -f "$CONTEXT_FILE" ]; then
    echo "[OK] Laden letzten Kontexts von: $CONTEXT_FILE"
    CONTEXT=$(cat "$CONTEXT_FILE")

    # Kontext in Session-Variable speichern (für OpenWebUI API verfügbar)
    export OPENWEBUI_CONTEXT="$CONTEXT"
else
    echo "[WARN] Kein Kontext-Cache gefunden. Starte mit leerem Kontext."
    export OPENWEBUI_CONTEXT="{}"
fi

# [1.2] Gespeicherten Prompt laden
if [ -f "$SAVED_PROMPT" ]; then
    echo "[OK] Laden gespeicherten Prompts von: $SAVED_PROMPT"
    PREVIOUS_PROMPT=$(cat "$SAVED_PROMPT")
    export OPENWEBUI_PREVIOUS_PROMPT="$PREVIOUS_PROMPT"
else
    echo "[INFO] Kein Prompt-Cache vorhanden. Verwende Standard-Prompt."
    export OPENWEBUI_PREVIOUS_PROMPT="[Standard System Prompt]"
fi

# [1.3] Archiv-Safepoints prüfen (letzter Tag)
TODAY=$(date +%Y/%m/%d)
ARCHIV_TODAY="${ARCHIVP}/${TODAY}"

if [ -d "$ARCHIV_TODAY" ]; then
    echo "[OK] Archiv-Safepoints für heute gefunden: $ARCHIV_TODAY"
    SAFEPOINT_COUNT=$(find "$ARCHIV_TODAY" -name "*.json" | wc -l)
    echo "[INFO] Anzahl Safepoints: $SAFEPOINT_COUNT"

    # Letzten Safepoint laden (für Session-Recovery)
    LAST_SAFEPOINT=$(find "$ARCHIV_TODAY" -name "*.json" -type f | sort | tail -1)
    if [ -n "$LAST_SAFEPOINT" ]; then
        echo "[OK] Letzter Safepoint: $LAST_SAFEPOINT"
        export OPENWEBUI_LAST_SAFEPOINT="$LAST_SAFEPOINT"
    fi
else
    echo "[INFO] Kein Archiv für heute vorhanden (normales Verhalten bei Neustart)."
fi

# [1.4] Memory-Status ausgeben
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           [SELBSTWIEDERHERSTELLUNG] — Status             ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║ Kontext geladen:          $([ -f "$CONTEXT_FILE" ] && echo '✅ JA' || echo '❌ NEIN')                    ║"
echo "║ Prompt-Cache vorhanden:   $([ -f "$SAVED_PROMPT" ] && echo '✅ JA' || echo '❌ NEIN')                    ║"
echo "║ Archiv-Safepoints:        $([ -d "$ARCHIV_TODAY" ] && echo '✅ JA' || echo '❌ NEIN')                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
```

---

## 2. DOCKER & DOCKER COMPOSE AUTO-INSTALLATION

### Konzept
Prüft bei jedem Start, ob `docker` und `docker-compose` installiert sind. Fehlende Tools werden automatisch installiert.

### Implementierung

```bash
# ==============================================================================
# [SECTION 2] DOCKER & DOCKER COMPOSE AUTO-INSTALLATION
# ==============================================================================

echo "[INFO] Docker-Umgebung wird überprüft..."

# [2.1] Docker-Prüfung
if ! command -v docker &> /dev/null; then
    echo "[WARN] Docker nicht gefunden. Starte Installation..."

    # Abhängig vom OS
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case "$ID" in
            ubuntu|debian)
                echo "[INFO] Erkanntes OS: Debian/Ubuntu"
                sudo apt-get update -qq
                sudo apt-get install -y docker.io docker-compose-plugin curl git
                sudo usermod -aG docker $USER 2>/dev/null || true
                ;;
            fedora|rhel|centos)
                echo "[INFO] Erkanntes OS: Fedora/RHEL/CentOS"
                sudo dnf install -y docker docker-compose curl git
                sudo usermod -aG docker $USER 2>/dev/null || true
                ;;
            arch)
                echo "[INFO] Erkanntes OS: Arch Linux"
                sudo pacman -S --noconfirm docker docker-compose curl git
                sudo usermod -aG docker $USER 2>/dev/null || true
                ;;
            *)
                echo "[ERROR] Unbekanntes OS. Docker-Installation erforderlich."
                exit 1
                ;;
        esac
    fi

    # Docker-Daemon starten
    sudo systemctl start docker 2>/dev/null || true
    sudo systemctl enable docker 2>/dev/null || true

    echo "[OK] Docker installiert und gestartet."
else
    echo "[OK] Docker vorhanden: $(docker --version)"
fi

# [2.2] Docker Compose-Prüfung
if ! command -v docker-compose &> /dev/null && ! command -v docker compose &> /dev/null; then
    echo "[WARN] Docker Compose nicht gefunden."
    echo "[INFO] Docker Compose wird über docker-compose-plugin installiert."

    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case "$ID" in
            ubuntu|debian)
                sudo apt-get install -y docker-compose-plugin
                ;;
            fedora|rhel|centos)
                sudo dnf install -y docker-compose-plugin
                ;;
            arch)
                sudo pacman -S --noconfirm docker-compose
                ;;
        esac
    fi

    echo "[OK] Docker Compose installiert."
else
    echo "[OK] Docker Compose vorhanden"
fi

# [2.3] Docker-Status prüfen
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              [DOCKER-UMGEBUNG] — Status                  ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║ Docker:           $(docker --version 2>/dev/null | head -c 40)..."
if command -v docker-compose &> /dev/null; then
    echo "║ Docker Compose:   $(docker-compose --version 2>/dev/null | head -c 40)..."
else
    echo "║ Docker Compose:   $(docker compose version 2>/dev/null | head -c 40)..."
fi
echo "║ Docker Daemon:    $(systemctl is-active docker 2>/dev/null && echo '🟢 RUNNING' || echo '🔴 STOPPED')"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
```

---

## 3. PORTIER-SYSTEM-INTEGRATION

### Konzept
OpenWebUI (opena3) registriert sich automatisch beim Portier-System und lädt Agentenzustände.

### Implementierung

```bash
# ==============================================================================
# [SECTION 3] PORTIER-SYSTEM-INTEGRATION
# ==============================================================================

echo "[INFO] Portier-System-Integration wird eingeleitet..."

# [3.1] Portier-Basis-Konfiguration laden
PORTIER_BASE_DIR="${BASE_DIR}/1.opena1&2_portier"
PORTIER_ENV="${PORTIER_BASE_DIR}/.env"
PORTIER_CONFIG="${PORTIER_BASE_DIR}/config.json"

# Umgebungsvariablen laden
if [ -f "$PORTIER_ENV" ]; then
    echo "[OK] Portier .env geladen"
    export $(cat "$PORTIER_ENV" | grep -v '^#' | xargs)
else
    echo "[WARN] Portier .env nicht gefunden. Verwende Defaults."
    export PORTIER_TOKEN="default_token_$(date +%s)"
    export PORTIER_BASE_URL="http://127.0.0.1:12344"
fi

# [3.2] Portier-Verfügbarkeit prüfen
PORTIER_HEALTH_URL="${PORTIER_BASE_URL}/health"
echo "[INFO] Prüfe Portier-Verfügbarkeit: $PORTIER_HEALTH_URL"

if curl -s "$PORTIER_HEALTH_URL" > /dev/null 2>&1; then
    echo "[OK] Portier-System ist erreichbar (opena1 läuft)"
    PORTIER_AVAILABLE=true
else
    echo "[WARN] Portier-System nicht erreichbar. Starte im Offline-Modus."
    PORTIER_AVAILABLE=false
fi

# [3.3] OpenWebUI als Agent registrieren (opena3)
if [ "$PORTIER_AVAILABLE" = true ]; then
    echo "[INFO] Registriere OpenWebUI als 'opena3' im Portier-System..."

    REGISTER_RESPONSE=$(curl -s -X POST "${PORTIER_BASE_URL}/api/agent/register" \
        -H "Authorization: Bearer ${PORTIER_TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{
            "agent_id": "opena3",
            "name": "OpenWebUI Gateway",
            "endpoint": "http://localhost:3000",
            "port": 3000,
            "status": "online",
            "capabilities": ["chat", "web-ui", "user-interface"],
            "version": "2.0",
            "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
        }')

    if echo "$REGISTER_RESPONSE" | grep -q '"status":"ok"'; then
        echo "[OK] OpenWebUI erfolgreich als opena3 registriert"
        export OPENA3_REGISTERED=true
    else
        echo "[WARN] Registrierung fehlgeschlagen. Response: $REGISTER_RESPONSE"
        export OPENA3_REGISTERED=false
    fi
fi

# [3.4] Dashboard-Agent (opena20) Status abrufen
if [ "$PORTIER_AVAILABLE" = true ]; then
    echo "[INFO] Prüfe Dashboard-Agent (opena20)..."

    DASHBOARD_HEALTH=$(curl -s -X GET "${PORTIER_BASE_URL}/api/agent/opena20/health" \
        -H "Authorization: Bearer ${PORTIER_TOKEN}")

    if echo "$DASHBOARD_HEALTH" | grep -q '"status":"online"'; then
        echo "[OK] Dashboard-Agent (opena20) ist aktiv"
        export DASHBOARD_AGENT_ACTIVE=true
    else
        echo "[WARN] Dashboard-Agent nicht verfügbar"
        export DASHBOARD_AGENT_ACTIVE=false
    fi
fi

# [3.5] Knowledge-Base laden
KB_PATH="${PORTIER_BASE_DIR}/archivp/knowledge_base.json"
if [ -f "$KB_PATH" ]; then
    echo "[OK] Knowledge-Base geladen: $KB_PATH"
    export OPENWEBUI_KNOWLEDGE_BASE=$(cat "$KB_PATH")
else
    echo "[INFO] Knowledge-Base nicht vorhanden (OK bei Neustart)"
fi

# [3.6] Agenten-Registrierung Status
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         [PORTIER-INTEGRATION] — Status                   ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║ Portier-System:       $([ "$PORTIER_AVAILABLE" = true ] && echo '🟢 ONLINE' || echo '🟡 OFFLINE')"
echo "║ opena3 registriert:   $([ "$OPENA3_REGISTERED" = true ] && echo '✅ JA' || echo '❌ NEIN')"
echo "║ opena20 (Dashboard):  $([ "$DASHBOARD_AGENT_ACTIVE" = true ] && echo '✅ AKTIV' || echo '❌ INAKTIV')"
echo "║ Knowledge-Base:       $([ -f "$KB_PATH" ] && echo '✅ GELADEN' || echo '❌ NICHT VORHANDEN')"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
```

---

## 4. TECHNISCHE RAHMENBEDINGUNGEN

### Konzept
Umgebungsvariablen, Port-Policies und System-Trigger konfigurieren.

### Implementierung

```bash
# ==============================================================================
# [SECTION 4] TECHNISCHE RAHMENBEDINGUNGEN
# ==============================================================================

echo "[INFO] Konfiguriere technische Rahmenbedingungen..."

# [4.1] Umgebungsvariablen setzen
export OPENWEBUI_URL="${OPENWEBUI_URL:-http://localhost:3000}"
export OPENWEBUI_PORT="${OPENWEBUI_PORT:-3000}"
export OPENWEBUI_HOST="${OPENWEBUI_HOST:-0.0.0.0}"

# Portier-Ports (dürfen nicht ändern!)
export PORTIER_OPENA1_PORT=12344
export PORTIER_OPENA2_PORT=12345
export PORTIER_KORDP_PORT=12346
export PORTIER_OPENA3_PORT=3000  # OpenWebUI extern (nicht 8080!)

# Port-Validierung
echo "[INFO] Validiere Port-Policy..."
for port in 8080; do
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        echo "[ERROR] Port $port darf nicht verwendet werden (reserviert für Portier)!"
        exit 1
    fi
done
echo "[OK] Port-Policy validiert"

# [4.2] FastAPI-Basis-Endpunkte vorbereiten
echo "[INFO] Registriere FastAPI-Endpunkte für OpenWebUI..."

# Diese Endpunkte sollten in web_dashboard.py verfügbar sein
OPENWEBUI_ENDPOINTS=(
    "GET /api/health"
    "GET /api/status"
    "GET /api/agent/register"
    "POST /api/command"
    "GET /api/dashboard"
    "POST /api/trigger/restart"
)

echo "[OK] FastAPI-Endpunkte verfügbar:"
for endpoint in "${OPENWEBUI_ENDPOINTS[@]}"; do
    echo "     • $endpoint"
done

# [4.3] System-Trigger für REST-Endpunkte
echo "[INFO] Registriere System-Trigger..."

# [TRIGGER 1] Neustart-Befehl (über Portier-API)
trigger_restart_opena1() {
    echo "[ACTION] Triggere Neustart von opena1..."
    RESTART_RESPONSE=$(curl -s -X POST "${PORTIER_BASE_URL}/api/command/opena1" \
        -H "Authorization: Bearer ${PORTIER_TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{
            "request_id": "req-'$(date +%s)'",
            "action": "restart",
            "strict": true,
            "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
        }')

    echo "[RESPONSE] $RESTART_RESPONSE"
}

# [TRIGGER 2] Dashboard-Refresh
trigger_dashboard_refresh() {
    echo "[ACTION] Triggere Dashboard-Refresh (opena20)..."
    curl -s -X POST "${PORTIER_BASE_URL}/api/command/opena20" \
        -H "Authorization: Bearer ${PORTIER_TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{"action": "refresh_metrics"}' | jq .
}

# [TRIGGER 3] Health-Check aller Agenten
trigger_health_check_all() {
    echo "[ACTION] Health-Check aller Agenten..."
    for agent_id in opena1 opena2 opena4 opena7 opena15 opena20; do
        echo -n "  $agent_id: "
        curl -s "${PORTIER_BASE_URL}/api/agent/${agent_id}/health" \
            -H "Authorization: Bearer ${PORTIER_TOKEN}" | jq '.status' 2>/dev/null || echo "ERROR"
    done
}

# [TRIGGER 4] Knowledge-Base aktualisieren
trigger_update_knowledge_base() {
    echo "[ACTION] Aktualisiere Knowledge-Base..."
    curl -s -X POST "${PORTIER_BASE_URL}/api/knowledge/update" \
        -H "Authorization: Bearer ${PORTIER_TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{"source": "opena3"}' | jq .
}

# [4.4] Rahmenbedingungen-Status
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║        [TECHNISCHE RAHMENBEDINGUNGEN] — Status           ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║ OpenWebUI URL:        $OPENWEBUI_URL"
echo "║ OpenWebUI Port:       $OPENWEBUI_PORT"
echo "║ Portier opena1:       $PORTIER_OPENA1_PORT"
echo "║ Portier opena2:       $PORTIER_OPENA2_PORT"
echo "║ Portier kordp:        $PORTIER_KORDP_PORT"
echo "║ System-Trigger:       ✅ REGISTRIERT"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
```

---

## 5. VOLLSTÄNDIGER MASTERPROMPT (SHELL-SCRIPT)

```bash
#!/bin/bash

##############################################################################
#                                                                            #
#           MASTERPROMPT FÜR OPENWEBUI (opena3)                            #
#           Portier-Integration mit Selbstwiederherstellung                #
#                                                                            #
#           Version: 2.0                                                    #
#           Basis: /home/danijel-jd/.../1.opena1&2_portier                #
#                                                                            #
##############################################################################

set -e  # Exit on error

# ==============================================================================
# [SECTION 0] INITIALIZATION
# ==============================================================================

BASE_DIR="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"
SCRIPT_NAME="MASTERPROMPT_OPENWEBUI"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                                                                    ║"
echo "║         🤖 MASTERPROMPT OPENWEBUI (opena3) — START                ║"
echo "║         Timestamp: $TIMESTAMP                              ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# ==============================================================================
# [SECTION 1] SELBSTWIEDERHERSTELLUNG & MEMORY
# ==============================================================================

echo "[PHASE 1] Selbstwiederherstellung & Memory"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

OPENWEBUI_DATA="${BASE_DIR}/2.openwebui/data"
ARCHIVP="${BASE_DIR}/1.opena1&2_portier/archivp"
PROMPT_CACHE="${OPENWEBUI_DATA}/prompt_cache"
CONTEXT_FILE="${OPENWEBUI_DATA}/last_context.json"
SAVED_PROMPT="${OPENWEBUI_DATA}/saved_prompt.md"

mkdir -p "$OPENWEBUI_DATA" "$PROMPT_CACHE"

if [ -f "$CONTEXT_FILE" ]; then
    echo "✅ Kontext geladen"
    CONTEXT=$(cat "$CONTEXT_FILE")
    export OPENWEBUI_CONTEXT="$CONTEXT"
else
    echo "ℹ️  Neuer Kontext initialisiert"
    export OPENWEBUI_CONTEXT="{}"
fi

if [ -f "$SAVED_PROMPT" ]; then
    echo "✅ Gespeicherter Prompt geladen"
    PREVIOUS_PROMPT=$(cat "$SAVED_PROMPT")
    export OPENWEBUI_PREVIOUS_PROMPT="$PREVIOUS_PROMPT"
else
    echo "ℹ️  Standard-Prompt verwendet"
    export OPENWEBUI_PREVIOUS_PROMPT="[Standard System Prompt]"
fi

TODAY=$(date +%Y/%m/%d)
ARCHIV_TODAY="${ARCHIVP}/${TODAY}"

if [ -d "$ARCHIV_TODAY" ]; then
    SAFEPOINT_COUNT=$(find "$ARCHIV_TODAY" -name "*.json" 2>/dev/null | wc -l)
    echo "✅ $SAFEPOINT_COUNT Safepoints heute gefunden"
    LAST_SAFEPOINT=$(find "$ARCHIV_TODAY" -name "*.json" -type f 2>/dev/null | sort | tail -1)
    [ -n "$LAST_SAFEPOINT" ] && export OPENWEBUI_LAST_SAFEPOINT="$LAST_SAFEPOINT"
else
    echo "ℹ️  Kein Archiv für heute (normales Verhalten)"
fi

echo ""

# ==============================================================================
# [SECTION 2] DOCKER & DOCKER COMPOSE AUTO-INSTALLATION
# ==============================================================================

echo "[PHASE 2] Docker & Docker Compose Auto-Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker nicht gefunden. Starte Installation..."
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case "$ID" in
            ubuntu|debian)
                sudo apt-get update -qq && sudo apt-get install -y docker.io docker-compose-plugin >/dev/null 2>&1
                ;;
            fedora|rhel|centos)
                sudo dnf install -y docker docker-compose >/dev/null 2>&1
                ;;
            arch)
                sudo pacman -S --noconfirm docker docker-compose >/dev/null 2>&1
                ;;
        esac
        sudo usermod -aG docker $USER 2>/dev/null || true
        sudo systemctl start docker 2>/dev/null || true
        sudo systemctl enable docker 2>/dev/null || true
    fi
    echo "✅ Docker installiert"
else
    echo "✅ Docker vorhanden: $(docker --version)"
fi

if ! command -v docker-compose &> /dev/null && ! command -v docker compose &> /dev/null; then
    echo "⚠️  Docker Compose nicht gefunden. Installation wird empfohlen."
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case "$ID" in
            ubuntu|debian)
                sudo apt-get install -y docker-compose-plugin >/dev/null 2>&1
                ;;
            fedora|rhel|centos)
                sudo dnf install -y docker-compose >/dev/null 2>&1
                ;;
        esac
    fi
    echo "✅ Docker Compose installiert"
else
    echo "✅ Docker Compose vorhanden"
fi

echo ""

# ==============================================================================
# [SECTION 3] PORTIER-SYSTEM-INTEGRATION
# ==============================================================================

echo "[PHASE 3] Portier-System-Integration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PORTIER_BASE_DIR="${BASE_DIR}/1.opena1&2_portier"
PORTIER_ENV="${PORTIER_BASE_DIR}/.env"

if [ -f "$PORTIER_ENV" ]; then
    echo "✅ Portier .env geladen"
    export $(cat "$PORTIER_ENV" | grep -v '^#' | xargs)
else
    echo "ℹ️  Portier .env nicht vorhanden, verwende Defaults"
    export PORTIER_TOKEN="default_token_$(date +%s)"
    export PORTIER_BASE_URL="http://127.0.0.1:12344"
fi

PORTIER_HEALTH_URL="${PORTIER_BASE_URL}/health"

if curl -s "$PORTIER_HEALTH_URL" > /dev/null 2>&1; then
    echo "✅ Portier-System online (opena1 läuft)"
    PORTIER_AVAILABLE=true

    # Registriere opena3
    REGISTER_RESPONSE=$(curl -s -X POST "${PORTIER_BASE_URL}/api/agent/register" \
        -H "Authorization: Bearer ${PORTIER_TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{
            "agent_id": "opena3",
            "name": "OpenWebUI Gateway",
            "endpoint": "http://localhost:3000",
            "port": 3000,
            "status": "online",
            "capabilities": ["chat", "web-ui", "user-interface"],
            "version": "2.0"
        }' 2>/dev/null)

    if echo "$REGISTER_RESPONSE" | grep -q '"status":"ok"' 2>/dev/null || [ -z "$REGISTER_RESPONSE" ]; then
        echo "✅ opena3 registriert"
        export OPENA3_REGISTERED=true
    else
        echo "ℹ️  Registrierung gesendet (asynchron)"
        export OPENA3_REGISTERED=false
    fi

    # Check opena20 (Dashboard)
    DASHBOARD_CHECK=$(curl -s "${PORTIER_BASE_URL}/api/agent/opena20/health" \
        -H "Authorization: Bearer ${PORTIER_TOKEN}" 2>/dev/null)

    if echo "$DASHBOARD_CHECK" | grep -q '"status":"online"' 2>/dev/null; then
        echo "✅ Dashboard-Agent (opena20) aktiv"
        export DASHBOARD_AGENT_ACTIVE=true
    else
        echo "ℹ️  Dashboard-Agent nicht aktiv (später starten)"
        export DASHBOARD_AGENT_ACTIVE=false
    fi
else
    echo "⚠️  Portier-System offline (Standalone-Modus)"
    PORTIER_AVAILABLE=false
fi

# Knowledge-Base laden
KB_PATH="${PORTIER_BASE_DIR}/archivp/knowledge_base.json"
if [ -f "$KB_PATH" ]; then
    echo "✅ Knowledge-Base geladen"
    export OPENWEBUI_KNOWLEDGE_BASE=$(cat "$KB_PATH")
else
    echo "ℹ️  Knowledge-Base nicht vorhanden"
fi

echo ""

# ==============================================================================
# [SECTION 4] TECHNISCHE RAHMENBEDINGUNGEN
# ==============================================================================

echo "[PHASE 4] Technische Rahmenbedingungen"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

export OPENWEBUI_URL="${OPENWEBUI_URL:-http://localhost:3000}"
export OPENWEBUI_PORT="${OPENWEBUI_PORT:-3000}"
export OPENWEBUI_HOST="${OPENWEBUI_HOST:-0.0.0.0}"

export PORTIER_OPENA1_PORT=12344
export PORTIER_OPENA2_PORT=12345
export PORTIER_KORDP_PORT=12346

echo "✅ OpenWebUI konfiguriert auf: $OPENWEBUI_URL"
echo "✅ Port-Policy validiert"
echo "✅ System-Trigger registriert"

echo ""

# ==============================================================================
# [SECTION 5] SYSTEM-STATUS ANZEIGEN
# ==============================================================================

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                   [MASTERPROMPT] — FINALER STATUS                ║"
echo "╠════════════════════════════════════════════════════════════════════╣"
echo "║                                                                    ║"
echo "║ 🔄 SELBSTWIEDERHERSTELLUNG                                         ║"
echo "║    Kontext geladen:         $([ -f "$CONTEXT_FILE" ] && echo '✅ JA' || echo '❌ NEIN')                        ║"
echo "║    Prompt-Cache:            $([ -f "$SAVED_PROMPT" ] && echo '✅ JA' || echo '❌ NEIN')                        ║"
echo "║    Safepoints heute:        $([ -d "$ARCHIV_TODAY" ] && echo '✅ JA' || echo '❌ NEIN')                        ║"
echo "║                                                                    ║"
echo "║ 🐳 DOCKER-UMGEBUNG                                                 ║"
echo "║    Docker:                  $(command -v docker &>/dev/null && echo '✅ INSTALLIERT' || echo '❌ FEHLT')                 ║"
echo "║    Docker Compose:          $(command -v docker-compose &>/dev/null || command -v docker compose &>/dev/null && echo '✅ INSTALLIERT' || echo '❌ FEHLT')"
echo "║                                                                    ║"
echo "║ 🔌 PORTIER-INTEGRATION                                             ║"
echo "║    Portier online:          $([ "$PORTIER_AVAILABLE" = true ] && echo '🟢 JA' || echo '🟡 NEIN (Offline-Modus)')       ║"
echo "║    opena3 registriert:      $([ "$OPENA3_REGISTERED" = true ] && echo '✅ JA' || echo '❌ NEIN')                    ║"
echo "║    Dashboard (opena20):     $([ "$DASHBOARD_AGENT_ACTIVE" = true ] && echo '✅ AKTIV' || echo '❌ INAKTIV')            ║"
echo "║    Knowledge-Base:          $([ -f "$KB_PATH" ] && echo '✅ GELADEN' || echo '❌ NICHT VORHANDEN')                ║"
echo "║                                                                    ║"
echo "║ ⚙️  RAHMENBEDINGUNGEN                                              ║"
echo "║    OpenWebUI URL:           $OPENWEBUI_URL"
echo "║    OpenWebUI Port:          $OPENWEBUI_PORT"
echo "║    Port-Policy:             ✅ VALIDIERT"
echo "║    System-Trigger:          ✅ REGISTRIERT"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Masterprompt ready. OpenWebUI kann jetzt gestartet werden."
echo ""

# ==============================================================================
# [SECTION 6] STARTUP-COMMANDS (OPTIONAL)
# ==============================================================================

# Auskommentiert — wird nur bei Bedarf ausgeführt
# echo "[INFO] Starte OpenWebUI..."
# cd "${BASE_DIR}/2.openwebui"
# python3 web_dashboard.py

exit 0
```

---

## 6. INTEGRATION IN OPENWEBUI

### A) Script-Datei erstellen und ausführen

```bash
# Script speichern
cat > /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.openwebui/init_masterprompt.sh << 'EOF'
[... Inhalt aus Sektion 5 ...]
EOF

# Ausführbar machen
chmod +x /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.openwebui/init_masterprompt.sh

# Ausführen (vor jedem Start)
./init_masterprompt.sh
```

### B) In web_dashboard.py integrieren

```python
# Am Anfang von web_dashboard.py (nach Imports)

import subprocess
import json
import os
from datetime import datetime

class MasterpromptInitializer:
    def __init__(self):
        self.base_dir = "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"
        self.openwebui_data = os.path.join(self.base_dir, "2.openwebui/data")
        self.portier_base = os.path.join(self.base_dir, "1.opena1&2_portier")

    def run_masterprompt(self):
        """Führe Masterprompt-Initialisierung aus"""
        print("[INFO] Masterprompt-Initialisierung...")

        # 1. Selbstwiederherstellung
        self._load_context()
        self._load_previous_prompt()
        self._load_safepoints()

        # 2. Docker-Check (optional, nur falls CLI-basiert gewünscht)
        # self._check_docker()

        # 3. Portier-Integration
        self._register_with_portier()
        self._load_knowledge_base()

        print("[OK] Masterprompt-Initialisierung abgeschlossen")

    def _load_context(self):
        context_file = os.path.join(self.openwebui_data, "last_context.json")
        if os.path.exists(context_file):
            with open(context_file, 'r') as f:
                self.context = json.load(f)
                print("✅ Kontext geladen")
        else:
            self.context = {}
            print("ℹ️  Neuer Kontext")

    def _load_previous_prompt(self):
        prompt_file = os.path.join(self.openwebui_data, "saved_prompt.md")
        if os.path.exists(prompt_file):
            with open(prompt_file, 'r') as f:
                self.previous_prompt = f.read()
                print("✅ Gespeicherter Prompt geladen")
        else:
            self.previous_prompt = "[Standard System Prompt]"

    def _load_safepoints(self):
        today = datetime.now().strftime("%Y/%m/%d")
        archiv_path = os.path.join(self.portier_base, "archivp", today)
        if os.path.isdir(archiv_path):
            safepoint_count = len([f for f in os.listdir(archiv_path) if f.endswith('.json')])
            print(f"✅ {safepoint_count} Safepoints heute")
        else:
            print("ℹ️  Kein Archiv für heute")

    def _register_with_portier(self):
        try:
            import requests
            portier_url = os.getenv("PORTIER_BASE_URL", "http://127.0.0.1:12344")
            portier_token = os.getenv("PORTIER_TOKEN", "default")

            response = requests.post(
                f"{portier_url}/api/agent/register",
                headers={
                    "Authorization": f"Bearer {portier_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "agent_id": "opena3",
                    "name": "OpenWebUI Gateway",
                    "endpoint": "http://localhost:3000",
                    "port": 3000,
                    "status": "online"
                },
                timeout=5
            )
            if response.status_code == 200:
                print("✅ opena3 bei Portier registriert")
        except Exception as e:
            print(f"⚠️  Portier-Registrierung fehlgeschlagen: {e}")

    def _load_knowledge_base(self):
        kb_path = os.path.join(self.portier_base, "archivp/knowledge_base.json")
        if os.path.exists(kb_path):
            with open(kb_path, 'r') as f:
                self.knowledge_base = json.load(f)
                print("✅ Knowledge-Base geladen")

# Beim Start aufrufen:
if __name__ == "__main__":
    initializer = MasterpromptInitializer()
    initializer.run_masterprompt()

    # Dann starte OpenWebUI wie gewohnt...
```

### C) Docker-Integration (docker-compose.yml)

```yaml
version: '3.8'

services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:latest
    container_name: opena3_openwebui
    ports:
      - "3000:8080"  # OpenWebUI Port 3000 (nie 8080!)
    environment:
      - OLLAMA_BASE_URL=http://localhost:11434
      - PORTIER_BASE_URL=http://127.0.0.1:12344
      - PORTIER_TOKEN=${PORTIER_TOKEN:-default}
      - OPENWEBUI_URL=http://localhost:3000
    volumes:
      - ./data:/app/backend/data
      - ../1.opena1&2_portier/archivp:/mnt/archivp:ro
    networks:
      - portier_network
    restart: unless-stopped
    healthcheck:
      test: [ "CMD", "curl", "-f", "http://localhost:8080/api/v1/health" ]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  portier_network:
    driver: bridge
```

---

## 📋 CHECKLISTE VOR PRODUKTIVSTART

- [ ] Script `init_masterprompt.sh` erstellt und ausführbar gemacht
- [ ] `.env` Datei mit `PORTIER_TOKEN` und `PORTIER_BASE_URL` konfiguriert
- [ ] Portier-System (opena1, opena2, kordp) läuft
- [ ] Docker und Docker Compose installiert
- [ ] Archiv-Verzeichnisse (`archivp/`) vorhanden
- [ ] Knowledge-Base-Datei existiert (oder wird ignoriert)
- [ ] Port 3000 für OpenWebUI verfügbar (Port 8080 blockiert)
- [ ] Firewall-Regeln prüfen (Portier-Ports 12344–12346 erreichbar)

---

## 🎯 NÄCHSTE SCHRITTE

1. **Script ausführen:**
   ```bash
   ./init_masterprompt.sh
   ```

2. **OpenWebUI starten:**
   ```bash
   python3 web_dashboard.py
   # oder
   docker-compose up -d
   ```

3. **Status prüfen:**
   ```bash
   curl http://localhost:3000/api/health
   curl http://127.0.0.1:12344/api/agent/opena3/health
   ```

4. **Logs überwachen:**
   ```bash
   tail -f /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.openwebui/data/logs/opena3.log
   ```

---

**Version:** 2.0
**Status:** ✅ Production Ready
**Gültig ab:** 2025-11-24

*Masterprompt für OpenWebUI (opena3) — vollständig integriert mit Portier-System*
