#!/bin/bash
echo "🚀 Starting Agent Cluster (opena4-opena19)..."
cd "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui"
for AGENT_ID in {4..19}; do
  python3 LocalAgent-Pro/opena$AGENT_ID/main.py > LocalAgent-Pro/logs/opena$AGENT_ID.log 2>&1 &
done
sleep 2
echo "✅ All agents started!"
