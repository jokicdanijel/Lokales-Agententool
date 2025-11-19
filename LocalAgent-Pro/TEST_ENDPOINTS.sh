#!/bin/bash
# LocalAgent-Pro API Endpoint Tests für Linux Mint
# Erstellt: 16. November 2025

echo "🚀 LocalAgent-Pro API Endpoint Tests"
echo "======================================"
echo ""

# Server-URL
BASE_URL="http://127.0.0.1:8001"

# Test 1: Root-Endpoint
echo "📡 Test 1: Root-Endpoint (GET /)"
echo "--------------------------------------"
curl -s "${BASE_URL}/" | head -20
echo ""
echo ""

# Test 2: Health Check
echo "🏥 Test 2: Health Check (GET /health)"
echo "--------------------------------------"
curl -s "${BASE_URL}/health" | jq '.'
echo ""
echo ""

# Test 3: Whitelist anzeigen
echo "📋 Test 3: Whitelist (GET /whitelist)"
echo "--------------------------------------"
curl -s "${BASE_URL}/whitelist" | jq '.'
echo ""
echo ""

# Test 4: API v1 Info
echo "ℹ️  Test 4: API Info (GET /v1)"
echo "--------------------------------------"
curl -s "${BASE_URL}/v1" | jq '.'
echo ""
echo ""

# Test 5: Models-Liste
echo "🧠 Test 5: Models (GET /v1/models)"
echo "--------------------------------------"
curl -s "${BASE_URL}/v1/models" | jq '.'
echo ""
echo ""

# Test 6: Chat Completions (Willkommensnachricht)
echo "💬 Test 6: Chat Completions - Willkommensnachricht"
echo "--------------------------------------"
curl -s -X POST "${BASE_URL}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "localagent-pro",
    "messages": [{"role": "user", "content": ""}],
    "stream": false
  }' | jq -r '.choices[0].message.content'
echo ""
echo ""

# Test 7: Chat Completions (Datei erstellen)
echo "✏️  Test 7: Chat Completions - Datei erstellen"
echo "--------------------------------------"
curl -s -X POST "${BASE_URL}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "localagent-pro",
    "messages": [{"role": "user", "content": "Erstelle test_endpoint.txt mit Hello from API Test"}],
    "stream": false
  }' | jq -r '.choices[0].message.content'
echo ""
echo ""

# Test 8: Chat Completions (Datei lesen)
echo "📖 Test 8: Chat Completions - Datei lesen"
echo "--------------------------------------"
curl -s -X POST "${BASE_URL}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "localagent-pro",
    "messages": [{"role": "user", "content": "Lies test_endpoint.txt"}],
    "stream": false
  }' | jq -r '.choices[0].message.content'
echo ""
echo ""

# Test 9: Test-Endpoint (GET)
echo "🧪 Test 9: Test-Endpoint GET"
echo "--------------------------------------"
curl -s "${BASE_URL}/test?prompt=Liste%20alle%20Dateien%20auf" | jq '.'
echo ""
echo ""

# Test 10: Test-Endpoint (POST)
echo "🧪 Test 10: Test-Endpoint POST"
echo "--------------------------------------"
curl -s -X POST "${BASE_URL}/test" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Lösche test_endpoint.txt"}' | jq '.'
echo ""
echo ""

# Test 11: Streaming (erste 5 Chunks)
echo "📡 Test 11: Streaming (erste 5 Chunks)"
echo "--------------------------------------"
curl -s -X POST "${BASE_URL}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "localagent-pro",
    "messages": [{"role": "user", "content": "Erstelle stream_test.txt mit Streaming Test"}],
    "stream": true
  }' | head -10
echo ""
echo ""

echo "✅ Alle Endpoint-Tests abgeschlossen!"
echo "======================================"
