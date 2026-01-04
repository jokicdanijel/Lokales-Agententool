#!/usr/bin/env bash
# ==============================================================================
# Setup Agent Dashboard vHosts für nginx
# Macht generierte Dashboards über nginx verfügbar (z.B. opena16.local)
# ==============================================================================

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
NGINX_SITES="/etc/nginx/sites-available"
NGINX_ENABLED="/etc/nginx/sites-enabled"

# Funktionierende Agents mit Ports
declare -A AGENTS=(
    [opena6]=12352
    [opena8]=12354
    [opena10]=12356
    [opena12]=12358
    [opena14]=12360
    [opena15]=12361
    [opena16]=12362
    [opena18]=12363
    [opena19]=12365
    [opena21]=12367
)

echo "🚀 Setup Agent Dashboard vHosts"
echo "========================================"

for agent_id in "${!AGENTS[@]}"; do
    port="${AGENTS[$agent_id]}"
    agent_dirs=("$PROJECT_ROOT"/*"$agent_id"*)

    if [ ${#agent_dirs[@]} -eq 0 ]; then
        echo "⚠️  [$agent_id] Ordner nicht gefunden"
        continue
    fi

    agent_dir="${agent_dirs[0]}"
    frontend_dir="$agent_dir/frontend"

    if [ ! -d "$frontend_dir" ]; then
        echo "⚠️  [$agent_id] Frontend-Ordner fehlt"
        continue
    fi

    vhost_file="$NGINX_SITES/${agent_id}-dashboard"

    cat > "/tmp/${agent_id}-dashboard.conf" <<EOF
server {
    listen 80;
    server_name ${agent_id}.local;

    root $frontend_dir;
    index index.html;

    location / {
        try_files \$uri \$uri/ =404;
    }

    # API Proxy zu Agent
    location /api/ {
        proxy_pass http://localhost:$port/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    location /health {
        proxy_pass http://localhost:$port/health;
    }
}
EOF

    sudo mv "/tmp/${agent_id}-dashboard.conf" "$vhost_file"
    sudo ln -sf "$vhost_file" "$NGINX_ENABLED/"

    echo "✅ [$agent_id] vHost erstellt: http://${agent_id}.local"
done

echo ""
echo "🔧 Nginx neu laden..."
sudo nginx -t && sudo systemctl reload nginx

echo ""
echo "✅ Setup abgeschlossen!"
echo ""
echo "📝 /etc/hosts Einträge hinzufügen:"
for agent_id in "${!AGENTS[@]}"; do
    echo "127.0.0.1 ${agent_id}.local"
done | sort
