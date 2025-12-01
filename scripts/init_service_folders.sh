#!/usr/bin/env bash
# path: scripts/init_service_folders.sh
# Single-Source-of-Truth Generator: Ordnerstruktur + READMEs + routing_matrix.yaml
# Deterministic, idempotent, CI-safe
# Usage: bash scripts/init_service_folders.sh

set -euo pipefail

# === SINGLE SOURCE OF TRUTH ===
declare -A MAP=(
  [portier]=kordp
  [openwebui]=openweb
  [telegram]=telep
  [vscode]=vscop
  [browser]=browsp
  [chatbot_email]=emailp
  [chatbot_whats]=whatp
  [chatbot_tone_answer]=calp
  [chatbot_tone_call]=answp
  [unlock_master]=onlockp
  [social_media]=somep
  [influencer]=infmep
  [calendar_agent]=kalp
  [html_creator]=htmlp
  [shop_creator]=shopp
  [homepage_creator]=homep
  [local_archiv_agent]=locp
  [stocks_crypto]=aktienp
  [dashboard_agent]=dashp
)

BASE="src/services"

mkdir -p "$BASE"

echo "🔧 Initializing service folders from Single-Source MAP..."

# === GENERATE FOLDERS & READMES ===
for svc in "${!MAP[@]}"; do
  ptarget="${MAP[$svc]}"
  svc_dir="$BASE/$svc"
  mkdir -p "$svc_dir"
  
  readme="$svc_dir/README.md"
  if [ ! -f "$readme" ]; then
    cat > "$readme" <<EOF
# $svc

- **program_target**: $ptarget
- **endpoint_base**: http://localhost:12344-12399/$ptarget
- **purpose**: Service module for $svc (program target: $ptarget)

## Integration

This service connects to the Port-Policy 12344-12399 gateway.
Safepoints are logged via archivp (OpenA2 Archivator).

EOF
    echo "  ✅ $svc/README.md created"
  fi
done

# === GENERATE routing_matrix.yaml FROM SAME SOURCE ===
confdir="configs"
mkdir -p "$confdir"
rout="$confdir/routing_matrix.yaml"

{
  echo "# Auto-generated from scripts/init_service_folders.sh"
  echo "# DO NOT EDIT MANUALLY — re-run init_service_folders.sh to sync"
  echo ""
  echo "program_targets:"
  # sort by key for stable diffs
  for svc in $(printf "%s\n" "${!MAP[@]}" | sort); do
    echo "  $svc: ${MAP[$svc]}"
  done
} > "$rout"

echo "  ✅ configs/routing_matrix.yaml generated ($(wc -l < "$rout") lines)"

echo ""
echo "✅ Service initialization complete:"
echo "   Folders: $BASE (19 services)"
echo "   Routing: $rout"
