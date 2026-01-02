#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# install_n8n_vhost.sh
# - Installs nginx vhost for n8n.hyperdashboard-one.de
# - Enables site and reloads nginx
# ============================================================================

DOMAIN="n8n.hyperdashboard-one.de"
SRC="infrastructure/nginx/vhosts/${DOMAIN}.conf"
AVAILABLE="/etc/nginx/sites-available/${DOMAIN}"
ENABLED="/etc/nginx/sites-enabled/${DOMAIN}"

echo "[INFO] Installing nginx vhost for: ${DOMAIN}"

if [[ ! -f "${SRC}" ]]; then
  echo "[ERROR] Missing source file: ${SRC}"
  exit 1
fi

echo "[INFO] Copying ${SRC} -> ${AVAILABLE}"
sudo cp "${SRC}" "${AVAILABLE}"

echo "[INFO] Enabling site: ${ENABLED}"
sudo ln -sf "${AVAILABLE}" "${ENABLED}"

echo "[INFO] Testing nginx config"
sudo nginx -t

echo "[INFO] Reloading nginx"
sudo systemctl reload nginx

echo "[OK] Installed. Next:"
echo "  - Ensure n8n is reachable at the configured upstream (default: 127.0.0.1:5678)"
echo "  - Test:"
echo "      curl -k https://${DOMAIN}/ | head"
echo "      curl -k -i -X POST https://${DOMAIN}/webhook/terminal-create-note -H 'Content-Type: application/json' -d '{\"content\":\"ping\"}'"
