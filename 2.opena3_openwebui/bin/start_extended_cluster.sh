#!/bin/bash
# Start extended agent cluster (opena4-opena20)

echo "🚀 Starting extended cluster (17 agents)..."

for i in {4..20}; do
    port=$((12344 + i))
    nohup python3 LocalAgent-Pro/opena$i/main.py > LocalAgent-Pro/logs/opena$i.log 2>&1 &
    echo "  Starting opena$i (port $port)..."
done

sleep 2
echo "✅ Extended cluster started!"
