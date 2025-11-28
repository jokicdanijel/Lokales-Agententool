#!/bin/bash
# Automatisches Health-Monitoring mit Alerting
# Kann als systemd-Service oder Cronjob laufen

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="${LOG_FILE:-$BASE_DIR/logs/health_monitor.log}"
STATE_FILE="$BASE_DIR/.runtime/health_state.json"
ALERT_THRESHOLD="${ALERT_THRESHOLD:-3}"  # Anzahl Fehler bevor Alert
CHECK_INTERVAL="${CHECK_INTERVAL:-30}"    # Sekunden zwischen Checks

mkdir -p "$BASE_DIR/logs" "$BASE_DIR/.runtime"

# Farben für Terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

check_service() {
    local name=$1
    local port=$2
    local endpoint=${3:-/health}
    
    if RESPONSE=$(curl -s -m 5 "http://127.0.0.1:$port$endpoint" 2>/dev/null); then
        STATUS=$(echo "$RESPONSE" | jq -r '.status // .health // "unknown"' 2>/dev/null || echo "unknown")
        
        if [[ "$STATUS" == "ok" ]] || [[ "$STATUS" == "healthy" ]]; then
            echo "ok"
        else
            echo "degraded:$STATUS"
        fi
    else
        echo "down"
    fi
}

send_alert() {
    local service=$1
    local status=$2
    local message="🚨 ALERT: $service is $status"
    
    log "$message"
    
    # Webhook notification (optional)
    if [[ -n "${WEBHOOK_URL:-}" ]]; then
        curl -s -X POST "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"$message\",\"service\":\"$service\",\"status\":\"$status\"}" \
            >/dev/null 2>&1 || true
    fi
    
    # System notification
    if command -v notify-send >/dev/null 2>&1; then
        notify-send "ELION Health Alert" "$message" --urgency=critical 2>/dev/null || true
    fi
}

update_state() {
    local service=$1
    local status=$2
    
    # Load current state
    if [[ -f "$STATE_FILE" ]]; then
        STATE=$(cat "$STATE_FILE")
    else
        STATE="{}"
    fi
    
    # Update state
    PREV_STATUS=$(echo "$STATE" | jq -r ".$service.status // \"unknown\"" 2>/dev/null || echo "unknown")
    FAIL_COUNT=$(echo "$STATE" | jq -r ".$service.fail_count // 0" 2>/dev/null || echo "0")
    
    if [[ "$status" == "ok" ]]; then
        FAIL_COUNT=0
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
    
    # Trigger alert if threshold reached
    if [[ $FAIL_COUNT -ge $ALERT_THRESHOLD ]] && [[ "$PREV_STATUS" != "$status" ]]; then
        send_alert "$service" "$status"
    fi
    
    # Save new state
    STATE=$(echo "$STATE" | jq -c ".$service = {\"status\": \"$status\", \"fail_count\": $FAIL_COUNT, \"last_check\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" 2>/dev/null || echo "{\"$service\":{\"status\":\"$status\",\"fail_count\":$FAIL_COUNT}}")
    echo "$STATE" > "$STATE_FILE"
}

run_health_check() {
    log "=== Health Check Started ==="
    
    # Check opena1
    STATUS=$(check_service "opena1" 12344)
    log "opena1: $STATUS"
    update_state "opena1" "$STATUS"
    
    # Check opena2
    STATUS=$(check_service "opena2" 12345)
    log "opena2: $STATUS"
    update_state "opena2" "$STATUS"
    
    # Check Dashboard
    STATUS=$(check_service "dashboard" 12349)
    log "dashboard: $STATUS"
    update_state "dashboard" "$STATUS"
    
    # Optional: Check OpenWebUI agent
    if curl -s -m 2 http://127.0.0.1:12347/health >/dev/null 2>&1; then
        STATUS=$(check_service "opena3" 12347)
        log "opena3: $STATUS"
        update_state "opena3" "$STATUS"
    fi
    
    log "=== Health Check Complete ==="
    echo ""
}

# Main loop
if [[ "${1:-}" == "once" ]]; then
    # Single check
    run_health_check
    exit 0
elif [[ "${1:-}" == "daemon" ]]; then
    # Continuous monitoring
    log "Starting health monitor daemon (interval: ${CHECK_INTERVAL}s, alert threshold: $ALERT_THRESHOLD)"
    
    while true; do
        run_health_check
        sleep "$CHECK_INTERVAL"
    done
else
    echo "Usage: $0 {once|daemon}"
    echo ""
    echo "Options:"
    echo "  once    - Run single health check"
    echo "  daemon  - Continuous monitoring"
    echo ""
    echo "Environment variables:"
    echo "  CHECK_INTERVAL     - Seconds between checks (default: 30)"
    echo "  ALERT_THRESHOLD    - Failed checks before alert (default: 3)"
    echo "  WEBHOOK_URL        - Optional webhook for alerts"
    exit 1
fi
