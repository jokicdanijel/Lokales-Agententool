#!/usr/bin/env bash
# generate_scalable_services.sh — Bulk Service Generation
# Creates 16 services (12349-12364) from template

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE_FILE="${ROOT}/src/services/template/main.py"
SERVICES_DIR="${ROOT}/src/services"

# Service mapping (port, program_target, service_name)
declare -a SERVICES=(
  "12349:browsp:browser"
  "12350:vscop:vscode"
  "12351:emailp:email"
  "12352:whatp:whatsapp"
  "12353:phonep:phone"
  "12354:kalp:calendar"
  "12355:somep:social_media"
  "12356:shopp:shop"
  "12357:htmlp:html_creator"
  "12358:homep:homepage_creator"
  "12359:aktienp:stocks_crypto"
  "12360:infmep:influencer"
  "12361:onlockp:unlock_master"
  "12362:locp:local_archiv"
  "12363:cust1:custom_1"
  "12364:cust2:custom_2"
)

echo "════════════════════════════════════════════════════════════════"
echo "🔄 Bulk Service Generation (16 Services: 12349-12364)"
echo "════════════════════════════════════════════════════════════════"
echo

count=0
for service_spec in "${SERVICES[@]}"; do
  IFS=':' read -r port target service_name <<< "$service_spec"

  SERVICE_DIR="${SERVICES_DIR}/${service_name}"

  # Skip if already exists
  if [ -d "$SERVICE_DIR" ]; then
    echo "✅ ${service_name} (${port}) — Already exists"
    continue
  fi

  # Create directory
  mkdir -p "$SERVICE_DIR"

  # Copy template
  cp "$TEMPLATE_FILE" "${SERVICE_DIR}/main.py"

  # Create wrapper for environment variables
  cat > "${SERVICE_DIR}/run.sh" << EOF
#!/usr/bin/env bash
export SERVICE_NAME="${service_name}"
export PROGRAM_TARGET="${target}"
export PORT="${port}"
exec python3 "\$(dirname "\${BASH_SOURCE[0]}")/main.py" "\$@"
EOF
  chmod +x "${SERVICE_DIR}/run.sh"

  # Create requirements.txt
  cat > "${SERVICE_DIR}/requirements.txt" << 'EOF'
fastapi==0.121.0
uvicorn==0.30.0
pydantic==2.12.4
pydantic-settings==2.12.0
httpx==0.27.2
python-multipart==0.0.7
EOF

  echo "✨ ${service_name:0:15:}... (${port}, ${target:0:6}...)"
  ((count++))
done

echo
echo "════════════════════════════════════════════════════════════════"
echo "✅ Generated ${count} services"
echo "════════════════════════════════════════════════════════════════"
echo
echo "📝 To start a service:"
echo "   cd src/services/\<service_name\>"
echo "   source .venv/bin/activate"
echo "   ./run.sh"
echo
echo "📋 Start all 16 services (background):"
echo "   for svc in browser vscode email whatsapp phone calendar social_media shop html_creator homepage_creator stocks_crypto influencer unlock_master local_archiv custom_1 custom_2; do"
echo "     (cd src/services/\$svc && ./run.sh) &"
echo "   done"
