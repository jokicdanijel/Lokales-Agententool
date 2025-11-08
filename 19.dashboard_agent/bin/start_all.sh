#!/usr/bin/env bash
set -Eeuo pipefail
BASE="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.dashboard_agent"
cd "$BASE"

chmod +x bin/*.sh || true

# Activate venv if needed
if [ -d "../1.portier_openai/venv313" ]; then
  source ../1.portier_openai/venv313/bin/activate
fi

echo "🚀 Phase 1-5 Services starten..."

# Phase 1
echo "📍 Phase 1: Dashboard (12349), Archivator (12345), Koordinator (12346), Agent (12344)"
nohup python3 main_dashboard.py  > logs/dashboard.nohup.log  2>&1 &
sleep 2
nohup python3 main_opena2.py     > logs/opena2.nohup.log     2>&1 &
sleep 1
nohup python3 main_kordp.py      > logs/kordp.nohup.log      2>&1 &
sleep 1
nohup python3 main_opena1.py     > logs/opena1.nohup.log     2>&1 &
sleep 1

# Phase 2
echo "📍 Phase 2: Agents 4-6 (12347-12348, 12349...)"
nohup python3 main_opena4_telegram.py > logs/opena4.nohup.log 2>&1 &
sleep 1
nohup python3 main_opena5_browser.py  > logs/opena5.nohup.log 2>&1 &
sleep 1
nohup python3 main_opena6_email.py    > logs/opena6.nohup.log 2>&1 &
sleep 1

# Phase 3
echo "📍 Phase 3: Agents 7-10 (12350-12353)"
nohup python3 main_opena7_whatsapp.py    > logs/opena7.nohup.log    2>&1 &
sleep 1
nohup python3 main_opena8_telephone.py   > logs/opena8.nohup.log    2>&1 &
sleep 1
nohup python3 main_opena9_telephonecall.py > logs/opena9.nohup.log  2>&1 &
sleep 1
nohup python3 main_opena10_unlock.py     > logs/opena10.nohup.log   2>&1 &
sleep 1

# Phase 4
echo "📍 Phase 4: Agents 11-15 (12359-12363)"
nohup python3 main_opena11_social_media.py > logs/opena11.nohup.log    2>&1 &
sleep 1
nohup python3 main_opena12_influencer.py   > logs/opena12.nohup.log    2>&1 &
sleep 1
nohup python3 main_opena13_calendar.py     > logs/opena13.nohup.log    2>&1 &
sleep 1
nohup python3 main_opena14_html.py         > logs/opena14.nohup.log    2>&1 &
sleep 1
nohup python3 main_opena15_shop.py         > logs/opena15.nohup.log    2>&1 &
sleep 1

# Phase 5
echo "📍 Phase 5: Agents 16-19 (12364-12367)"
nohup python3 main_opena16_crm.py       > logs/opena16.nohup.log       2>&1 &
sleep 1
nohup python3 main_opena17_analytics.py > logs/opena17.nohup.log       2>&1 &
sleep 1
nohup python3 main_opena18_dashboard.py > logs/opena18.nohup.log       2>&1 &
sleep 1
nohup python3 main_opena19_workflow.py  > logs/opena19_workflow.nohup.log 2>&1 &
sleep 1

echo "✅ Alle Services gestartet! Logs: $BASE/logs/*.nohup.log"
echo "   Dashboard: http://127.0.0.1:12349"
echo "   Token: $(cat .env 2>/dev/null || echo 'MISSING')"

