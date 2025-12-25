#!/usr/bin/env bash
set -euo pipefail

echo "="
echo "OpenWebUI Status"
echo "="

echo -e "\n🔹 OpenWebUI (Port 8080):"
curl -s http://127.0.0.1:8080/health | jq . || echo "Nicht erreichbar"

echo -e "\n🔹 OpenWebUI Agent (opena3, Port 12347):"
curl -s http://127.0.0.1:12347/health | jq . || echo "Nicht erreichbar"

echo -e "\n🔹 OpenWebUI Adapter (Port 12350):"
curl -s http://127.0.0.1:12350/health | jq . || echo "Nicht erreichbar"

echo -e "\n✓ Status-Check abgeschlossen"
