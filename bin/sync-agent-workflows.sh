#!/bin/bash
# ============================================================================
# AGENT WORKFLOW GENERATOR
# ============================================================================
# Generiert alle .github/workflows/<agent>.yml aus Template + agent_directories.json
# Nutzt deterministische Struktur, verhindert Drift
# ============================================================================

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORKFLOWS_DIR="${REPO_ROOT}/.github/workflows"
TEMPLATE_FILE="${WORKFLOWS_DIR}/_agent-template.yml"
REGISTRY_FILE="${REPO_ROOT}/agent_directories.json"

echo "🔧 Agent Workflow Generator"
echo "   Repo: $REPO_ROOT"
echo "   Template: $TEMPLATE_FILE"
echo "   Registry: $REGISTRY_FILE"
echo ""

# Validiere Template existiert
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "❌ Template nicht gefunden: $TEMPLATE_FILE"
    exit 1
fi

# Validiere Registry existiert
if [ ! -f "$REGISTRY_FILE" ]; then
    echo "❌ Agent Registry nicht gefunden: $REGISTRY_FILE"
    exit 1
fi

# Zähle Agents
AGENT_COUNT=$(jq '.agents | length' "$REGISTRY_FILE")
echo "📊 Gefunden: $AGENT_COUNT Agents"
echo ""

# Iteriere über alle Agents
GENERATED=0
SKIPPED=0

jq -r '.agents[] | "\(.name)|\(.port)|\(.folder)"' "$REGISTRY_FILE" | while IFS='|' read -r AGENT_NAME AGENT_PORT AGENT_FOLDER; do
    AGENT_DIR="${AGENT_FOLDER%/*}"  # Get parent dir, e.g., 4.opena5_vscode
    AGENT_NUM=$(echo "$AGENT_NAME" | sed 's/opena//')

    # Determine category (simple heuristic)
    case "$AGENT_NAME" in
        opena1|opena2) AGENT_CATEGORY="auth" ;;
        opena3) AGENT_CATEGORY="interface" ;;
        opena4) AGENT_CATEGORY="messaging" ;;
        opena5) AGENT_CATEGORY="connector" ;;
        opena6) AGENT_CATEGORY="browser" ;;
        opena7) AGENT_CATEGORY="email" ;;
        opena8) AGENT_CATEGORY="messaging" ;;
        opena9) AGENT_CATEGORY="voice" ;;
        opena10) AGENT_CATEGORY="tracking" ;;
        opena20) AGENT_CATEGORY="dashboard" ;;
        *) AGENT_CATEGORY="workflow" ;;
    esac

    OUTPUT_FILE="${WORKFLOWS_DIR}/${AGENT_NAME}.yml"

    # Skip if main workflows already exist (optional)
    if [ "$AGENT_NAME" = "opena7" ]; then
        echo "⏭️  Skipping $AGENT_NAME (already customized)"
        ((SKIPPED++))
        continue
    fi

    echo "▶️  Generating: $OUTPUT_FILE"
    echo "   Name: $AGENT_NAME | Port: $AGENT_PORT | Dir: $AGENT_DIR | Category: $AGENT_CATEGORY"

    # Generate workflow from template
    sed \
        -e "s|{{AGENT_NAME}}|${AGENT_NAME}|g" \
        -e "s|{{AGENT_NUM}}|${AGENT_NUM}|g" \
        -e "s|{{AGENT_DIR}}|${AGENT_DIR}|g" \
        -e "s|{{AGENT_PORT}}|${AGENT_PORT}|g" \
        -e "s|{{AGENT_CATEGORY}}|${AGENT_CATEGORY}|g" \
        "$TEMPLATE_FILE" > "$OUTPUT_FILE"

    echo "   ✅ Generated $(wc -l < "$OUTPUT_FILE") lines"
    ((GENERATED++))
done

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   Generation Complete                 ║"
echo "╠════════════════════════════════════════╣"
echo "│ Generated: $GENERATED workflows        │"
echo "│ Skipped:   $SKIPPED (pre-existing)     │"
echo "╚════════════════════════════════════════╝"
echo ""
echo "✅ All agent workflows generated in: $WORKFLOWS_DIR"
echo ""
echo "Next: Commit and push to GitHub"
echo "  git add .github/workflows/opena*.yml"
echo "  git commit -m 'ci: auto-generate agent workflows'"
echo "  git push origin main"
