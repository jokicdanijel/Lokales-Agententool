#!/bin/bash
# PORTIER 3.0 - Health Check für alle 21 Agents

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║         🔍 PORTIER 3.0 - HEALTH CHECK ALLER 21 AGENTS                   ║"
echo "╠══════════════════════════════════════════════════════════════════════════╣"

# Port-Mapping
declare -A AGENTS=(
    [12344]="opena1|Koordinator"
    [12345]="opena2|Archivator"
    [12347]="opena3|OpenWebUI"
    [12348]="opena4|Telegram"
    [12349]="opena20|Dashboard"
    [12351]="opena5|VSCode"
    [12352]="opena6|Browser"
    [12353]="opena7|Email"
    [12354]="opena8|WhatsApp"
    [12355]="opena9|Telephone"
    [12356]="opena10|CallTracking"
    [12357]="opena11|Unlock"
    [12358]="opena12|SocialMedia"
    [12359]="opena13|Influencer"
    [12360]="opena14|Calendar"
    [12361]="opena15|HTML"
    [12362]="opena16|Shop"
    [12363]="opena18|CRM"
    [12365]="opena19|Trading"
    [12366]="opena17|Homepage"
    [12367]="opena21|Workflow"
)

online=0
offline=0

printf "║ %-6s │ %-10s │ %-25s │ %-10s ║\n" "PORT" "AGENT" "NAME" "STATUS"
echo "╠══════════════════════════════════════════════════════════════════════════╣"

for port in 12344 12345 12347 12348 12349 12351 12352 12353 12354 12355 12356 12357 12358 12359 12360 12361 12362 12363 12365 12366 12367; do
    info="${AGENTS[$port]}"
    agent="${info%|*}"
    name="${info#*|}"
    
    result=$(curl -s --connect-timeout 1 "http://127.0.0.1:$port/health" 2>/dev/null)
    
    if [ -n "$result" ]; then
        status="✅ ONLINE"
        ((online++))
    else
        status="❌ OFFLINE"
        ((offline++))
    fi
    
    printf "║ %-6s │ %-10s │ %-25s │ %-10s ║\n" "$port" "$agent" "$name" "$status"
done

echo "╠══════════════════════════════════════════════════════════════════════════╣"
printf "║   ✅ Online: %-3s    ❌ Offline: %-3s    📊 Total: 21 Agents              ║\n" "$online" "$offline"
echo "╚══════════════════════════════════════════════════════════════════════════╝"

if [ "$online" -eq 21 ]; then
    echo ""
    echo "🎉 ALL 21 AGENTS RUNNING - SYSTEM FULLY OPERATIONAL!"
fi
