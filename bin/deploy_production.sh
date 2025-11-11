#!/usr/bin/env bash
# bin/deploy_production.sh — Production Deployment Orchestrator
# Start 20 services via Docker Compose with monitoring
# Usage: bash bin/deploy_production.sh [start|stop|status|logs]

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT/docker compose.prod.yml"
LOG_DIR="$ROOT/logs"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ====================================================================
# FUNCTIONS
# ====================================================================

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

deploy_start() {
    log_info "Starting ELION Production Deployment (20 services)..."
    
    # Verify checks first
    log_info "Running deployment validation..."
    cd "$ROOT"
    python3 scripts/deployment_check.py > /dev/null || {
        log_error "Deployment validation failed"
        exit 1
    }
    
    mkdir -p "$LOG_DIR"
    
    # Start Docker Compose
    log_info "Starting Docker Compose stack..."
    cd "$ROOT"
    docker compose -f "$COMPOSE_FILE" up -d
    
    log_success "Docker Compose stack started"
    
    # Wait for services
    log_info "Waiting for services to be ready (60s timeout)..."
    sleep 3
    
    # Health checks
    log_info "Checking service health..."
    
    HEALTHY=0
    for i in {1..12}; do
        HEALTHY=$(docker ps | grep -E 'portier|archivator|prometheus|grafana' | wc -l)
        if [ "$HEALTHY" -ge 4 ]; then
            log_success "Core services healthy ($HEALTHY/4 containers)"
            break
        fi
        echo -n "."
        sleep 5
    done
    
    echo ""
    
    if [ "$HEALTHY" -lt 4 ]; then
        log_warn "Some services may still be starting. Check with: docker ps"
    fi
    
    log_info "Production deployment complete!"
    log_info ""
    log_info "Access points:"
    log_info "  🏠 Grafana (Dashboards):  http://127.0.0.1:3001 (admin/admin)"
    log_info "  📊 Prometheus (Metrics):  http://127.0.0.1:9090"
    log_info "  🔧 Portier (API):         http://127.0.0.1:12344/health"
    log_info ""
    log_info "Next steps:"
    log_info "  1. View dashboards: http://127.0.0.1:3001/dashboards"
    log_info "  2. Scale services: docker compose -f $COMPOSE_FILE up -d service_name"
    log_info "  3. Run tests: python3 scripts/test_multi_service_orchestration.py"
    log_info "  4. Load test: python3 scripts/load_test_scaled.py"
}

deploy_stop() {
    log_info "Stopping ELION Production Deployment..."
    
    cd "$ROOT"
    docker compose -f "$COMPOSE_FILE" down
    
    log_success "All services stopped"
}

deploy_status() {
    log_info "ELION Production Status:"
    echo ""
    
    cd "$ROOT"
    docker compose -f "$COMPOSE_FILE" ps
    
    echo ""
    log_info "Health Check Results:"
    
    # Portier
    if curl -s http://127.0.0.1:12344/health > /dev/null 2>&1; then
        log_success "Portier (12344) ✓"
    else
        log_warn "Portier (12344) ✗"
    fi
    
    # Archivator
    if curl -s http://127.0.0.1:12345/health > /dev/null 2>&1; then
        log_success "Archivator (12345) ✓"
    else
        log_warn "Archivator (12345) ✗"
    fi
    
    # Prometheus
    if curl -s http://127.0.0.1:9090/-/healthy > /dev/null 2>&1; then
        log_success "Prometheus (9090) ✓"
    else
        log_warn "Prometheus (9090) ✗"
    fi
    
    # Grafana
    if curl -s http://127.0.0.1:3001/api/health > /dev/null 2>&1; then
        log_success "Grafana (3001) ✓"
    else
        log_warn "Grafana (3001) ✗"
    fi
}

deploy_logs() {
    log_info "Production Logs (last 50 lines):"
    echo ""
    
    cd "$ROOT"
    docker compose -f "$COMPOSE_FILE" logs --tail=50 -f
}

deploy_scale() {
    SERVICE=$1
    COUNT=${2:-1}
    
    log_info "Scaling $SERVICE to $COUNT instance(s)..."
    
    cd "$ROOT"
    docker compose -f "$COMPOSE_FILE" up -d --scale "$SERVICE=$COUNT"
    
    log_success "Scaling complete"
}

# ====================================================================
# MAIN
# ====================================================================

case "${1:-help}" in
    start)
        deploy_start
        ;;
    stop)
        deploy_stop
        ;;
    status)
        deploy_status
        ;;
    logs)
        deploy_logs
        ;;
    scale)
        if [ -z "${2:-}" ]; then
            log_error "Usage: bash bin/deploy_production.sh scale SERVICE [COUNT]"
            exit 1
        fi
        deploy_scale "$2" "${3:-1}"
        ;;
    *)
        echo "🚀 ELION Production Deployment Orchestrator"
        echo ""
        echo "Usage: bash bin/deploy_production.sh [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  start              Start 20-service production deployment"
        echo "  stop               Stop all services"
        echo "  status             Check health of all services"
        echo "  logs               Follow production logs"
        echo "  scale SERVICE N    Scale service to N instances"
        exit 0
        ;;
esac
