#!/bin/bash

# README Update Script für PORTIER 3.0
# Aktualisiert alle Agent-READMEs mit konsistenten Header-Informationen

echo "🚀 PORTIER 3.0 README Update Script"
echo "======================================"
echo "Aktualisiere alle Agent-READMEs..."

# Define agent mapping
declare -A AGENTS=(
    ["3.opena4_telegram"]="opena4:12348:telep:Telegram Bot"
    ["4.opena5_vscode"]="opena5:12351:vscop:VS Code Agent"
    ["6.opena7_email"]="opena7:12353:emailp:E-Mail Client"
    ["7.opena8_whatsapp"]="opena8:12354:whatsappp:WhatsApp API"
    ["8.opena9_telephone"]="opena9:12355:telephonep:Telefonie Agent"
    ["9.opena10_call_tracking"]="opena10:12356:calltrackp:Call Tracking"
    ["10.opena11_unlock"]="opena11:12357:unlockp:Unlock Master"
    ["11.opena12_social_media"]="opena12:12358:smp:Social Media"
    ["12.opena13_influencer"]="opena13:12359:influp:Influencer Agent"
    ["13.opena14_calendar"]="opena14:12360:calp:Calendar Agent"
    ["14.opena15_html"]="opena15:12361:htmlp:HTML Creator"
    ["15.opena16_shop"]="opena16:12362:shopp:Shop Creator"
    ["16.opena17_homepagecreator"]="opena17:12363:hpcreatep:Homepage Creator"
    ["17.opena18_CMR"]="opena18:12364:crmp:CRM / Local Archiv"
    ["18.opena19_Aktien&Crypto"]="opena19:12365:stockcryptop:Aktien & Crypto"
)

# Get current date for updates
CURRENT_DATE=$(date +"%d. %B %Y")

# Update each agent README
for AGENT_DIR in "${!AGENTS[@]}"; do
    IFS=':' read -r AGENT_ID PORT KUERZEL DESCRIPTION <<< "${AGENTS[$AGENT_DIR]}"

    README_PATH="${AGENT_DIR}/README.md"

    if [ -f "$README_PATH" ]; then
        echo "📝 Updating: $README_PATH"

        # Create backup
        cp "$README_PATH" "${README_PATH}.backup"

        # Create new header
        cat > "${README_PATH}.tmp" << EOF
# 🤖 ${AGENT_ID} - ${DESCRIPTION}

**Agent-ID:** \`${AGENT_ID}\`
**Port:** ${PORT}
**Kürzel:** \`${KUERZEL}\`
**Version:** 3.0
**Status:** 🟡 **Planned** (PORTIER 3.0 Architecture Ready)
**Letzte Aktualisierung:** ${CURRENT_DATE}

---

## 📖 Überblick

**${AGENT_ID}** ist der **${DESCRIPTION}** im ELION Hyper-Dashboard System - ein spezialisierter Agent für die PORTIER 3.0 Multi-Agent-Architektur.

### 🎯 PORTIER 3.0 Integration

${AGENT_ID} ist architektonisch vorbereitet für die PORTIER 3.0 Integration:

- ✅ **Option-2-Flow Ready:** OpenAI → opena1 → opena2 → kordp → ${AGENT_ID}
- ✅ **Port Policy Compliant:** Port ${PORT} (Backend-Range 12344-12399)
- ✅ **Safepoint Integration:** Automatische Archivierung via opena2
- ✅ **Bearer Token Security:** Authentifizierung vorbereitet
- 🟡 **Implementation Status:** Ordnerstruktur vorhanden, Code pending

### 🚀 Zukünftige Features

- 🔄 **Multi-Agent Coordination:** Integration mit anderen Agenten
- 📊 **Real-time Monitoring:** Dashboard-Integration (opena20)
- 🛡️ **Security First:** Vollständige Bearer Token Implementation
- ⚡ **High Performance:** Async FastAPI Architecture

---

## 📡 API-Endpoints (Planned)

### \`GET /health\`

Health-Check des Agents.

\`\`\`bash
curl http://127.0.0.1:${PORT}/health | jq .
\`\`\`

### \`POST /invoke\`

Service-spezifische Aktion ausführen.

\`\`\`bash
curl -X POST http://127.0.0.1:${PORT}/invoke \\
  -H "Authorization: Bearer \$BEARER_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "action": "service_action",
    "params": {...}
  }'
\`\`\`

---

## 🚀 Quick Start (When Implemented)

### Agent starten

\`\`\`bash
cd ${AGENT_DIR}
python3 main.py

# Oder via ops.sh
cd ..
bin/ops.sh start
\`\`\`

### Health Check

\`\`\`bash
curl http://127.0.0.1:${PORT}/health | jq .
\`\`\`

---

## 🔗 Integration mit PORTIER 3.0

### Service-Registrierung

\`\`\`bash
curl -X POST http://127.0.0.1:12344/route/update \\
  -H "Authorization: Bearer \$BEARER_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "service_name": "${AGENT_ID}",
    "endpoint": "http://127.0.0.1:${PORT}",
    "program_target": "${KUERZEL}"
  }'
\`\`\`

### Action via Portier auslösen

\`\`\`bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \\
  -H "Authorization: Bearer \$BEARER_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "service_target": "${KUERZEL}",
    "action": "service_action",
    "params": {...}
  }'
\`\`\`

---

## 📁 Verzeichnisstruktur (Planned)

\`\`\`txt
${AGENT_DIR}/
├── main.py                  # FastAPI Agent Entry Point (planned)
├── config.py                # Konfiguration (planned)
├── requirements.txt         # Dependencies
├── bin/
│   └── start.sh             # Start-Script (planned)
├── tests/
│   └── test_${AGENT_ID}.py  # Unit-Tests (planned)
└── README.md                # Diese Datei
\`\`\`

---

## 🔐 Sicherheit

- ✅ **Bearer-Token** für alle Endpoints außer \`/health\`
- ✅ **Port-Policy** Enforcement (12344-12399)
- ✅ **Strict JSON** (Pydantic \`extra="forbid"\`)
- ✅ **Option-2-Flow** Compliance

---

## 🧪 Testing (Planned)

\`\`\`bash
# Unit-Tests
pytest tests/test_${AGENT_ID}.py -v

# Health-Check
curl http://127.0.0.1:${PORT}/health

# Integration-Test via Portier
python3 ../scripts/test_${AGENT_ID}_integration.py
\`\`\`

---

## 📊 Monitoring (Planned)

\`\`\`bash
# Prometheus Metrics (wenn aktiviert)
curl http://127.0.0.1:${PORT}/metrics
\`\`\`

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** Danijel Jokic (ELION Team)
**Letzte Aktualisierung:** ${CURRENT_DATE}
**Status:** 🟡 **Architecture Ready** (Implementation Pending)

EOF

        # Append original content (skip old header if exists)
        if grep -q "^## " "$README_PATH"; then
            # Find first ## heading and append from there
            sed -n '/^## /,$p' "$README_PATH" >> "${README_PATH}.tmp"
        else
            # Append everything after line 10 if no ## heading found
            tail -n +11 "$README_PATH" >> "${README_PATH}.tmp"
        fi

        # Replace original with updated version
        mv "${README_PATH}.tmp" "$README_PATH"

        echo "✅ Updated: $AGENT_ID ($PORT)"
    else
        echo "⚠️  README not found: $README_PATH"
    fi
done

echo ""
echo "🎉 README Update Complete!"
echo "📝 All agent READMEs updated to PORTIER 3.0 standards"
echo ""
echo "📋 Next Steps:"
echo "- Review updated READMEs"
echo "- Commit changes: git add . && git commit -m 'docs: Update all agent READMEs to PORTIER 3.0'"
echo "- Push to repository: git push origin main"
