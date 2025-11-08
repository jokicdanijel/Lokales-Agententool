#!/usr/bin/env bash
set -Eeuo pipefail

echo "⏹️  Alle Services stoppen..."

# Dashboard
pkill -f "uvicorn main_dashboard:app" || true
pkill -f main_dashboard.py            || true

# Phase 1
pkill -f "uvicorn main_opena1:app"    || true
pkill -f "uvicorn main_opena2:app"    || true
pkill -f "uvicorn main_kordp:app"     || true
pkill -f main_opena1.py               || true
pkill -f main_opena2.py               || true
pkill -f main_kordp.py                || true

# Phase 2
pkill -f main_opena4_telegram.py      || true
pkill -f main_opena5_browser.py       || true
pkill -f main_opena6_email.py         || true

# Phase 3
pkill -f main_opena7_whatsapp.py      || true
pkill -f main_opena8_telephone.py     || true
pkill -f main_opena9_telephonecall.py || true
pkill -f main_opena10_unlock.py       || true

# Phase 4
pkill -f main_opena11_social_media.py || true
pkill -f main_opena12_influencer.py   || true
pkill -f main_opena13_calendar.py     || true
pkill -f main_opena14_html.py         || true
pkill -f main_opena15_shop.py         || true

# Phase 5
pkill -f main_opena16_crm.py          || true
pkill -f main_opena17_analytics.py    || true
pkill -f main_opena18_dashboard.py    || true
pkill -f main_opena19_workflow.py     || true

sleep 2

echo "✅ Alle Services gestoppt."
