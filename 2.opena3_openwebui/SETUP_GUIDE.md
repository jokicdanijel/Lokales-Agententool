# 🚀 OpenA3 - Complete Setup & Usage Guide

**Project:** OpenA3 - AI Agent Koordinator & Tool Execution Platform
**Version:** 1.0.0
**Status:** ✅ Production Ready
**Last Updated:** 2025-11-24

---

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [System Architecture](#system-architecture)
3. [Services Overview](#services-overview)
4. [Tools Suite](#tools-suite)
5. [Web Interfaces](#web-interfaces)
6. [API Reference](#api-reference)
7. [Security](#security)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Access the System

**Main Dashboard:**
```
http://localhost:8000
```

**Tools Panel:**
```
http://localhost:8000/tools.html
```

**OpenWebUI:**
```
http://localhost:3000
```

**LocalAgent-Pro API:**
```
http://127.0.0.1:8001/health
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     OpenA3 Complete Stack                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Frontend Layer (Port 8000)                │
├─────────────────────────────────────────────────────────────┤
│ • Dashboard (index.html)                                    │
│ • Tools Panel (tools.html)                                  │
│ • System Monitoring                                         │
│ • Live Logs                                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Backend Services Layer                         │
├─────────────────────────────────────────────────────────────┤
│ • LocalAgent-Pro (Port 8001)                               │
│   - Tool Execution Engine                                   │
│   - Sandbox Isolation                                       │
│   - Security Filtering                                      │
│   - Prometheus Metrics                                      │
│                                                             │
│ • OpenWebUI (Port 3000)                                    │
│   - Chat Interface                                          │
│   - Multi-Model Support                                     │
│   - Tool Integration                                        │
│                                                             │
│ • Ollama (Port 11434)                                      │
│   - Local LLM Engine                                        │
│   - Model Management                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Data & Resource Layer                          │
├─────────────────────────────────────────────────────────────┤
│ • /localagent_sandbox - Isolated File Storage              │
│ • SQLite Databases                                          │
│ • JSON Config Files                                         │
│ • Prometheus Metrics Storage                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Services Overview

### LocalAgent-Pro (Port 8001)
**Purpose:** Tool Execution Server with OpenAI-compatible API

**Key Features:**
- ✅ OpenAI-compatible `/v1/chat/completions` endpoint
- ✅ 8 powerful tools for file/system operations
- ✅ Sandbox isolation for security
- ✅ Prometheus metrics integration
- ✅ Request deduplication
- ✅ Command whitelisting

**Endpoints:**
```
GET  /health              - Health check
GET  /v1/models          - Available models
POST /v1/chat/completions - Execute tools/chat
GET  /metrics            - Prometheus metrics
```

**Status Check:**
```bash
curl http://127.0.0.1:8001/health | jq .
```

### OpenWebUI (Port 3000)
**Purpose:** Modern Chat Interface for AI Models

**Features:**
- Chat interface with multiple models
- Tool integration
- File upload/management
- User management
- Dark/Light mode

**Access:**
```
http://localhost:3000
```

### Ollama (Port 11434)
**Purpose:** Local LLM Engine

**Models:**
- llama3.1:8b-instruct-q4_K_M (currently loaded)

**API:**
```bash
# List models
curl http://localhost:11434/api/tags | jq .

# Check health
curl http://localhost:11434/api/health
```

---

## 🛠️ Tools Suite

🔗 **[🚀 Öffne Tools Panel](http://localhost:8000/tools.html)**

| # | Tool | Beschreibung | Link |
|---|------|-------------|------|
| 1 | 📝 write_file | Dateien erstellen/schreiben | [🔗 Öffnen](http://localhost:8000/tools.html?tool=write_file) |
| 2 | 📖 read_file | Dateien auslesen | [🔗 Öffnen](http://localhost:8000/tools.html?tool=read_file) |
| 3 | 🗑️ delete_file | Dateien löschen | [🔗 Öffnen](http://localhost:8000/tools.html?tool=delete_file) |
| 4 | 💻 shell_exec | Shell-Befehle ausführen | [🔗 Öffnen](http://localhost:8000/tools.html?tool=shell_exec) |
| 5 | 🌐 fetch_webpage | Webseiten abrufen | [🔗 Öffnen](http://localhost:8000/tools.html?tool=fetch_webpage) |
| 6 | 📊 execute_query | Datenbank-Abfragen | [🔗 Öffnen](http://localhost:8000/tools.html?tool=execute_query) |
| 7 | 🔍 list_directory | Verzeichnis auflisten | [🔗 Öffnen](http://localhost:8000/tools.html?tool=list_directory) |
| 8 | ⚡ execute_function | Funktionen ausführen | [🔗 Öffnen](http://localhost:8000/tools.html?tool=execute_function) |

---

### 1. 📝 write_file [🔗 Öffnen](http://localhost:8000/tools.html?tool=write_file)
**Create or overwrite files**

```javascript
// Via Dashboard
1. Open Tools Panel → tools.html
2. Select "write_file" Card
3. Enter filename and content
4. Click "Speichern"

// Via API
POST /v1/chat/completions
{
  "messages": [
    {"role": "user", "content": "Erstelle myfile.txt\nFile content here"}
  ]
}
```

### 2. 📖 read_file
**Read file contents**

```javascript
// Via Dashboard
1. Select "read_file" Card
2. Enter filename
3. Click "Lesen"

// Via API
POST /v1/chat/completions
{
  "messages": [
    {"role": "user", "content": "Lies myfile.txt"}
  ]
}
```

### 3. 🗑️ delete_file
**Delete files or directories**

```javascript
// Single file
POST /v1/chat/completions
{
  "messages": [
    {"role": "user", "content": "Lösche myfile.txt"}
  ]
}

// Directory (recursive)
POST /v1/chat/completions
{
  "messages": [
    {"role": "user", "content": "Lösche myfolder recursive"}
  ]
}
```

### 4. 💻 shell_exec
**Execute shell commands (whitelisted)**

```javascript
// List files
POST /v1/chat/completions
{
  "messages": [
    {"role": "user", "content": "Führe aus: ls -la /home"}
  ]
}

// Safe commands only
Whitelisted: ls, cat, grep, find, curl, wget, git, docker, python, node
```

### 5. 🌐 fetch_webpage
**Fetch and parse web content**

```javascript
// HTML parsing
POST /v1/chat/completions
{
  "messages": [
    {"role": "user", "content": "Rufe ab (html): https://example.com"}
  ]
}

// JSON API
POST /v1/chat/completions
{
  "messages": [
    {"role": "user", "content": "Rufe ab (json): https://api.example.com/users"}
  ]
}
```

### 6. 📊 execute_query
**Execute database queries**

```javascript
// SQL Query
POST /v1/chat/completions
{
  "messages": [
    {"role": "user", "content": "Führe sql aus: SELECT * FROM users WHERE active=1"}
  ]
}

// JSON Query
POST /v1/chat/completions
{
  "messages": [
    {"role": "user", "content": "Führe json aus: query for users"}
  ]
}
```

### 7. 🔍 list_directory
**List directory contents**

```javascript
// Basic listing
POST /v1/chat/completions
{
  "messages": [
    {"role": "user", "content": "Liste auf: /home/user"}
  ]
}

// With filter
POST /v1/chat/completions
{
  "messages": [
    {"role": "user", "content": "Liste auf: /home/user mit filter *.txt"}
  ]
}
```

### 8. ⚡ execute_function
**Execute Python or JavaScript**

```javascript
// Python function
POST /v1/chat/completions
{
  "messages": [
    {"role": "user", "content": "Führe python aus: def calc(a,b):\n    return a+b\nAufrufen: calc(5,3)"}
  ]
}

// JavaScript function
POST /v1/chat/completions
{
  "messages": [
    {"role": "user", "content": "Führe javascript aus: const add = (a,b) => a+b\nAufrufen: add(5,3)"}
  ]
}
```

---

## 🌐 Web Interfaces

### Dashboard (index.html)
**URL:** http://localhost:8000

**Sections:**
- Service Status Cards
- System Metrics
- Live Logs
- Quick Tools
- About Information

**Features:**
- Real-time status updates
- Auto-refresh every 30 seconds
- Log export functionality
- Smooth scrolling navigation

### Tools Panel (tools.html)
**URL:** http://localhost:8000/tools.html

**Layout:**
- 8 Tool Cards (one per tool)
- Input fields for parameters
- Real-time execution
- Result display panels
- Error handling

**Workflow:**
1. Select tool card
2. Enter parameters
3. Click "Ausführen"
4. View results in real-time

---

## 📡 API Reference

### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "sandbox": "/home/danijel-jd/localagent_sandbox",
  "timestamp": "2025-11-24T04:42:30.679151"
}
```

### Models Endpoint
```bash
GET /v1/models

Response:
{
  "object": "list",
  "data": [
    {
      "id": "local-model",
      "object": "model",
      "created": 1732380000,
      "owned_by": "local"
    }
  ]
}
```

### Chat Completions
```bash
POST /v1/chat/completions
Content-Type: application/json

Request:
{
  "messages": [
    {"role": "user", "content": "Erstelle test.txt\nHello World"}
  ],
  "model": "local",
  "temperature": 0.7
}

Response:
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1732380000,
  "model": "local",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "✅ File created successfully"
      },
      "finish_reason": "stop"
    }
  ]
}
```

### Metrics
```bash
GET /metrics

Response (Prometheus format):
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",endpoint="/v1/chat/completions"} 42

# HELP sandbox_files Total files in sandbox
# TYPE sandbox_files gauge
sandbox_files 23
```

---

## 🔒 Security

### Sandbox Isolation
All file operations are confined to `/localagent_sandbox`
```
/localagent_sandbox/
├── documents/
├── images/
├── temp/
└── [user-created files]
```

### Command Whitelisting
Only these shell commands are allowed:
```
File Operations: ls, cat, tail, head, find, grep, wc
Network: curl, wget, ssh
Development: git, docker, python, node, npm
System: echo, date, whoami, pwd
```

### Request Deduplication
Prevents duplicate execution using MD5 hashing of request content.

### Timeout Protection
```
shell_exec:      30s max
fetch_webpage:   20s max
execute_query:   60s max
```

### Input Validation
- Path sanitization (no `../` traversal)
- Command escaping (shell special characters)
- URL validation (http/https only)
- JSON schema validation

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to http://127.0.0.1:8001"
**Solution:**
1. Check if LocalAgent-Pro is running: `ps aux | grep openwebui_agent_server`
2. Restart: `cd LocalAgent-Pro && source venv/bin/activate && python src/openwebui_agent_server.py`

### Issue: Ollama connection error
**Solution:**
1. Check Ollama container: `docker ps | grep ollama`
2. Restart Docker: `docker compose restart ollama`
3. Check network: `docker network ls`

### Issue: Tools returning 500 errors
**Solution:**
1. Check server logs: `tail -f server.log`
2. Verify Ollama connection: `curl http://localhost:11434/api/tags`
3. Check sandbox permissions: `ls -la /home/danijel-jd/localagent_sandbox`

### Issue: Dashboard not loading
**Solution:**
1. Check HTTP server: `ps aux | grep http.server`
2. Restart server: `python3 -m http.server 8000`
3. Clear browser cache and reload

---

## 📈 Performance Tips

1. **For File Operations:**
   - Use absolute paths
   - Limit file sizes for read_file
   - Use filters in list_directory

2. **For Shell Commands:**
   - Keep commands simple
   - Avoid long-running operations
   - Use timeout appropriately

3. **For Web Fetching:**
   - Cache results when possible
   - Use appropriate parser (html vs text)
   - Monitor response times

4. **For Queries:**
   - Use indexes in databases
   - Limit result sets
   - Pre-optimize queries

---

## 📚 Additional Resources

- **Main Documentation:** `/README.md`
- **Tools Documentation:** `/TOOLS_DOCUMENTATION.md`
- **API Documentation:** `/LocalAgent-Pro/docs/API.md`
- **Test Suite:** `/LocalAgent-Pro/tests/test_api.py`
- **Integration Report:** `/INTEGRATION_REPORT.md`

---

## ✅ Verification Checklist

Before production deployment, verify:

- [ ] Dashboard loads: http://localhost:8000
- [ ] Tools Panel loads: http://localhost:8000/tools.html
- [ ] Health check passes: `curl http://127.0.0.1:8001/health`
- [ ] Metrics available: `curl http://127.0.0.1:8001/metrics`
- [ ] OpenWebUI running: http://localhost:3000
- [ ] Ollama available: `curl http://localhost:11434/api/tags`
- [ ] All 8 tools working
- [ ] Logging active
- [ ] Auto-refresh working
- [ ] Security features enabled

---

## 🎯 Common Use Cases

### Use Case 1: Daily Report Generation
```
1. write_file() → Create report template
2. shell_exec() → Run data collection scripts
3. execute_query() → Query database for statistics
4. fetch_webpage() → Get external data
5. write_file() → Save final report
```

### Use Case 2: System Administration
```
1. shell_exec() → Check system status
2. list_directory() → Browse file system
3. read_file() → Review log files
4. delete_file() → Clean up old files
```

### Use Case 3: Data Processing
```
1. fetch_webpage() → Get data from API
2. execute_query() → Parse CSV/JSON
3. execute_function() → Transform data
4. write_file() → Save results
```

### Use Case 4: Development Workflow
```
1. shell_exec() → Run git commands
2. shell_exec() → Execute tests
3. read_file() → Review code
4. write_file() → Create new files
```

---

## 🚀 Next Steps

1. **Explore Dashboard:** Visit http://localhost:8000
2. **Try Tools:** Open http://localhost:8000/tools.html
3. **Test API:** Use curl or Postman
4. **Integrate with OpenWebUI:** Configure at http://localhost:3000
5. **Monitor Metrics:** Check http://127.0.0.1:8001/metrics
6. **Review Logs:** View in Dashboard logs section

---

## 📞 Support & Help

For issues or questions:
1. Check Troubleshooting section above
2. Review documentation files
3. Check system logs
4. Test individual tools
5. Verify service connectivity

---

**OpenA3 © 2025 - Production Ready ✅**

Last Updated: 2025-11-24
Maintained by: OpenA3 Development Team
License: MIT
