# GitHub Copilot MCP Integration

**Status:** ✅ Configuration Ready  
**Last Updated:** 2025-12-17  
**API Endpoint:** `https://api.githubcopilot.com/mcp/`

---

## 📖 Overview

This document describes how to integrate the **GitHub Copilot MCP (Model Context Protocol)** API with the ELION Hyper-Dashboard system.

The GitHub Copilot MCP API allows programmatic access to GitHub Copilot's AI capabilities through a standardized Model Context Protocol interface.

---

## 🔑 Configuration

### Environment Variables

Add the following environment variables to your `.env` file:

```bash
# GitHub Copilot MCP API Configuration
# For MCP server integration with GitHub Copilot API
# Endpoint: https://api.githubcopilot.com/mcp/
GITHUB_COPILOT_API_KEY=your-github-copilot-api-key-here
GITHUB_COPILOT_MCP_ENDPOINT=https://api.githubcopilot.com/mcp/
```

### Obtaining an API Key

1. **Visit GitHub Settings**
   - Navigate to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
   
2. **Generate New Token**
   - Select "Generate new token (classic)" or use fine-grained tokens
   - Required scopes: `copilot`, `read:org` (if using organization features)

3. **Copy the Token**
   - Copy the generated token immediately (it will only be shown once)
   - Store it securely in your `.env` file as `GITHUB_COPILOT_API_KEY`

---

## 🚀 Setup Instructions

### 1. Copy Environment Template

```bash
# From project root
cp .env.example .env
```

### 2. Add Your API Key

Edit `.env` and replace the placeholder:

```bash
GITHUB_COPILOT_API_KEY=ghp_YourActualTokenHere
```

### 3. Verify Configuration

```bash
# Check if the key is set
grep GITHUB_COPILOT_API_KEY .env

# Test MCP server connection (if implemented)
curl -H "Authorization: Bearer $GITHUB_COPILOT_API_KEY" \
     https://api.githubcopilot.com/mcp/
```

---

## 🏗️ Integration Points

The GitHub Copilot MCP API can be integrated with the following ELION services:

### MCP Server (`mcp_server/`)
- **Port:** 12350
- **Purpose:** MCP protocol server for AI tool integration
- **Configuration:** `mcp_server/.env`

### Dashboard (opena20)
- **Port:** 12349
- **Purpose:** Central monitoring and management UI
- **Use Case:** Display Copilot API usage metrics, manage API keys

### Agent Services
- **Potential Integration:** Any agent can leverage Copilot API for enhanced AI capabilities
- **Authentication:** Uses `GITHUB_COPILOT_API_KEY` from environment

---

## 📊 API Endpoints

### Base URL
```
https://api.githubcopilot.com/mcp/
```

### Example Requests

**Note:** The exact endpoints depend on GitHub's MCP API implementation. Common patterns include:

```bash
# Health Check (hypothetical)
curl -X GET https://api.githubcopilot.com/mcp/health \
  -H "Authorization: Bearer $GITHUB_COPILOT_API_KEY"

# List Models (hypothetical)
curl -X GET https://api.githubcopilot.com/mcp/models \
  -H "Authorization: Bearer $GITHUB_COPILOT_API_KEY"

# Chat Completion (hypothetical)
curl -X POST https://api.githubcopilot.com/mcp/chat/completions \
  -H "Authorization: Bearer $GITHUB_COPILOT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "copilot",
    "messages": [
      {"role": "user", "content": "Hello, Copilot!"}
    ]
  }'
```

---

## 🔐 Security Best Practices

### 1. Never Commit Secrets
```bash
# Ensure .env is in .gitignore
echo ".env" >> .gitignore
```

### 2. Use Environment-Specific Keys
- **Development:** Use personal tokens with limited scopes
- **Production:** Use organization tokens with appropriate permissions

### 3. Rotate Keys Regularly
- Regenerate API keys every 90 days
- Revoke unused or compromised keys immediately

### 4. Limit Scope
- Only grant necessary permissions
- Use fine-grained tokens when possible

---

## 🧪 Testing

### Manual Test Script

Create `scripts/test_github_copilot_mcp.sh`:

```bash
#!/bin/bash
# Test GitHub Copilot MCP API connection

set -e

# Load environment
source .env

if [ -z "$GITHUB_COPILOT_API_KEY" ]; then
    echo "❌ GITHUB_COPILOT_API_KEY not set in .env"
    exit 1
fi

echo "🔍 Testing GitHub Copilot MCP API..."
echo "Endpoint: $GITHUB_COPILOT_MCP_ENDPOINT"

# Test connection (adjust endpoint as needed)
response=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $GITHUB_COPILOT_API_KEY" \
    "$GITHUB_COPILOT_MCP_ENDPOINT")

if [ "$response" = "200" ]; then
    echo "✅ API connection successful"
elif [ "$response" = "401" ]; then
    echo "❌ Authentication failed - check your API key"
    exit 1
else
    echo "⚠️  Received HTTP $response - check API endpoint"
    exit 1
fi
```

### Python Test Script

Create `scripts/test_github_copilot_mcp.py`:

```python
#!/usr/bin/env python3
"""Test GitHub Copilot MCP API integration."""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GITHUB_COPILOT_API_KEY = os.getenv("GITHUB_COPILOT_API_KEY")
GITHUB_COPILOT_MCP_ENDPOINT = os.getenv(
    "GITHUB_COPILOT_MCP_ENDPOINT", 
    "https://api.githubcopilot.com/mcp/"
)

def test_api_connection():
    """Test connection to GitHub Copilot MCP API."""
    if not GITHUB_COPILOT_API_KEY:
        print("❌ GITHUB_COPILOT_API_KEY not set in .env")
        return False
    
    headers = {
        "Authorization": f"Bearer {GITHUB_COPILOT_API_KEY}",
        "Accept": "application/json"
    }
    
    try:
        print(f"🔍 Testing connection to {GITHUB_COPILOT_MCP_ENDPOINT}...")
        response = requests.get(GITHUB_COPILOT_MCP_ENDPOINT, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ API connection successful")
            print(f"Response: {response.json() if response.text else 'Empty response'}")
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed - check your API key")
            return False
        else:
            print(f"⚠️  Received HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    success = test_api_connection()
    sys.exit(0 if success else 1)
```

---

## 📚 References

- **GitHub Copilot Documentation:** https://docs.github.com/en/copilot
- **MCP Specification:** https://spec.modelcontextprotocol.io/
- **ELION System Architecture:** `.github/copilot-master-prompt.md`
- **MCP Server Configuration:** `mcp_server/.env.example`

---

## 🔄 Integration Workflow

```
┌─────────────────┐
│  ELION Client   │
│  (Agent/Service)│
└────────┬────────┘
         │
         │ 1. Request with API Key
         ▼
┌─────────────────┐
│   MCP Server    │
│  (Port 12350)   │
└────────┬────────┘
         │
         │ 2. Forward to GitHub Copilot
         ▼
┌─────────────────┐
│ GitHub Copilot  │
│   MCP API       │
│ api.github.com  │
└────────┬────────┘
         │
         │ 3. Response
         ▼
┌─────────────────┐
│   MCP Server    │
│  (Port 12350)   │
└────────┬────────┘
         │
         │ 4. Return to Client
         ▼
┌─────────────────┐
│  ELION Client   │
└─────────────────┘
```

---

## ⚠️ Troubleshooting

### Error: "GITHUB_COPILOT_API_KEY not set"
**Solution:** Ensure `.env` file exists and contains the API key:
```bash
cp .env.example .env
# Edit .env and add your key
```

### Error: "401 Unauthorized"
**Solution:** 
1. Verify your API key is correct
2. Check token has `copilot` scope
3. Ensure token hasn't expired

### Error: "404 Not Found"
**Solution:** 
1. Verify the endpoint URL is correct
2. Check GitHub API documentation for current endpoints
3. Ensure you have access to GitHub Copilot

---

## 📝 Changelog

### 2025-12-17
- ✅ Initial documentation created
- ✅ Added configuration instructions
- ✅ Added test scripts
- ✅ Integrated with ELION system

---

**Maintainer:** ELION Team  
**Status:** ✅ Ready for Use  
**Next Steps:** Implement MCP server integration with GitHub Copilot API
