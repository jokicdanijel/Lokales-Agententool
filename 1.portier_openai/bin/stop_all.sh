#!/usr/bin/env bash
set -euo pipefail
SYSD="$HOME/.config/systemd/user"

systemctl --user stop portier-codegen.service || true
systemctl --user stop n8n.service || true
systemctl --user stop openwebui.service || true

echo "[OK] Dienste gestoppt: portier-codegen, n8n, openwebui"

