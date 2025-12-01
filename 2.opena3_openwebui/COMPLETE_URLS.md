# 🌐 OpenA3 Web Dashboard - Complete URL Reference

**Status:** ✅ ALL PAGES AND ENDPOINTS ACTIVE
**Server:** <http://localhost:8000>
**Last Updated:** 2025-11-24

---

## 🏠 Main Pages (HTML)

### Dashboard Home

**URL:** <http://localhost:8000/>

- Main interactive dashboard
- Status indicators
- Voice programs overview
- Tool execution interface
- Responsive glasmorphism UI

### System Status Page

**URL:** <http://localhost:8000/status>

- System status display
- Service monitoring
- Timestamp information
- Status indicators (online/offline)
- Visual status grid

### Tools Page

**URL:** <http://localhost:8000/tools>

- File Manager overview
- Shell Executor description
- Program Launcher info
- Tool capabilities
- Interactive tool cards

### Voice Programs Page

**URL:** <http://localhost:8000/programs>

- All 6 voice programs listed
- Program descriptions
- Direct launch buttons (▶️ Starten)
- Real-time execution feedback
- Program management interface

---

## 🔌 API Endpoints (JSON)

### Status Information

```
GET http://localhost:8000/api/status
```

Returns:

```json
{
  "status": "online",
  "timestamp": "2025-11-24T...",
  "version": "1.0.0",
  "services": {
    "localaagent-pro": "running",
    "ollama": "running",
    "openwebui": "running",
    "http-server": "running"
  }
}
```

### Tools API

```
GET http://localhost:8000/api/tools
```

Returns: JSON array of available tools

- File Manager (read, write, delete, list)
- Shell Executor (18 whitelisted commands)
- Program Launcher (voice programs)

### Programs API

```
GET http://localhost:8000/api/programs
```

Returns: JSON array of 6 voice programs

- voice_assistant.py
- voice_command_parser.py
- voice_call_system.py
- voice_note_recorder.py
- voice_transcriber.py
- voice_scheduler.py

### File Listing

```
GET http://localhost:8000/api/file/list
```

Returns: File listing in current directory

---

## 📝 File Operations (POST)

### Read File

```
POST http://localhost:8000/api/file/read
Content-Type: application/json

{
  "path": "tools/voice_assistant.py"
}
```

### Write File

```
POST http://localhost:8000/api/file/write
Content-Type: application/json

{
  "path": "myfile.txt",
  "content": "Hello World"
}
```

### Delete File

```
POST http://localhost:8000/api/file/delete
Content-Type: application/json

{
  "path": "myfile.txt"
}
```

---

## ⚙️ Shell Execution (POST)

### Execute Command

```
POST http://localhost:8000/api/shell/exec
Content-Type: application/json

{
  "command": "ls -la"
}
```

Whitelisted commands:

- `ls`, `pwd`, `echo`, `cat`, `grep`, `find`, `wc`
- `head`, `tail`, `date`, `whoami`, `mkdir`
- `rm`, `cp`, `mv`, `touch`, `chmod`
- `python3`, `pip3`

---

## 🎤 Program Execution (POST)

### Start Voice Program

```
POST http://localhost:8000/api/program/start
Content-Type: application/json

{
  "file": "voice_assistant.py"
}
```

Available programs:

- voice_assistant.py
- voice_command_parser.py
- voice_call_system.py
- voice_note_recorder.py
- voice_transcriber.py
- voice_scheduler.py

---

## 📊 Quick Examples

### Get System Status

```bash
curl http://localhost:8000/api/status
```

### View System Status Page

```bash
# In browser:
http://localhost:8000/status

# Or via curl:
curl http://localhost:8000/status | grep "<title>"
```

### View Tools Page

```bash
http://localhost:8000/tools
```

### View Programs Page

```bash
http://localhost:8000/programs
```

### Start a Program

```bash
curl -X POST http://localhost:8000/api/program/start \
  -H "Content-Type: application/json" \
  -d '{"file":"voice_assistant.py"}'
```

### List Files

```bash
curl http://localhost:8000/api/file/list
```

### Execute Command

```bash
curl -X POST http://localhost:8000/api/shell/exec \
  -H "Content-Type: application/json" \
  -d '{"command":"ls -la"}'
```

---

## 🔗 Navigation Structure

```
http://localhost:8000/
├─ Main Dashboard
│  ├─ Status Indicators
│  ├─ Voice Programs Section
│  ├─ Tools Section
│  └─ Interactive Cards
│
├─ /status ─────────────────────── System Status Page
│  ├─ System Status Display
│  ├─ Service Monitors
│  └─ Back to Dashboard
│
├─ /tools ──────────────────────── Tools Overview Page
│  ├─ File Manager
│  ├─ Shell Executor
│  ├─ Program Launcher
│  └─ Back to Dashboard
│
├─ /programs ───────────────────── Voice Programs Page
│  ├─ All 6 Programs Listed
│  ├─ Start Buttons
│  ├─ Real-time Feedback
│  └─ Back to Dashboard
│
└─ /api/* ──────────────────────── JSON Endpoints
   ├─ /api/status ─── System status
   ├─ /api/tools ──── Tools list
   ├─ /api/programs ─ Programs list
   ├─ /api/file/list  File browser
   │
   ├─ POST /api/file/read ────── Read file
   ├─ POST /api/file/write ───── Write file
   ├─ POST /api/file/delete ──── Delete file
   ├─ POST /api/shell/exec ───── Execute command
   └─ POST /api/program/start ── Start program
```

---

## 🎯 Common Tasks & URLs

### Task: View System Status

**Option 1 (HTML):** <http://localhost:8000/status>
**Option 2 (JSON):** curl <http://localhost:8000/api/status>

### Task: Start Voice Program

**Option 1 (UI):** <http://localhost:8000/programs> → Click "▶️ Starten"
**Option 2 (API):** POST to /api/program/start

### Task: Read a File

**Option 1 (UI):** <http://localhost:8000/> → File Manager
**Option 2 (API):** POST to /api/file/read

### Task: Execute Shell Command

**Option 1 (UI):** <http://localhost:8000/> → Tool Execution
**Option 2 (API):** POST to /api/shell/exec

---

## 🔐 Security & Constraints

### File Operations

- ✅ Safe relative paths only
- ❌ Absolute paths blocked
- ❌ Path traversal (../../) blocked
- Max file size: 1MB

### Shell Commands

- ✅ 18 whitelisted commands
- ❌ Dangerous commands blocked (sudo, rm -rf, etc.)
- ⏱️ 10-second timeout limit
- 📤 Output max 5000 characters

### Program Execution

- ✅ Only voice_*.py pattern allowed
- ✅ Process isolation with pipes
- ✅ Background execution
- 📍 Subprocess I/O management

---

## 📱 Browser Compatibility

✅ Chrome/Chromium
✅ Firefox
✅ Safari
✅ Edge
✅ Mobile browsers

---

## 🚀 Deployment URLs

### Local Development

```
http://localhost:8000
```

### With Reverse Proxy (Production)

```
https://yourdomain.com/opena3
```

### Docker Container

```
http://<container-ip>:8000
```

### Systemd Service

```
http://localhost:8000
# Auto-starts on boot
```

---

## 📊 Response Examples

### Successful Status Response

```json
{
  "status": "online",
  "timestamp": "2025-11-24T06:15:30.123456",
  "version": "1.0.0",
  "services": {
    "localaagent-pro": "running",
    "ollama": "running",
    "openwebui": "running",
    "http-server": "running"
  }
}
```

### Successful Program Start

```json
{
  "status": "ok",
  "file": "voice_assistant.py",
  "filepath": "tools/voice_assistant.py",
  "pid": 648906,
  "message": "✅ Programm 'voice_assistant.py' gestartet (PID: 648906)"
}
```

### Error Response (Invalid Path)

```json
{
  "error": "Invalid path",
  "reason": "Path traversal detected"
}
```

### Error Response (Command Not Allowed)

```json
{
  "error": "Command 'sudo' not allowed",
  "allowed": ["ls", "pwd", "echo", ...]
}
```

---

## 🆘 Troubleshooting URLs

### Check if Server is Running

```bash
curl http://localhost:8000/api/status
```

### Test a Page

```bash
# Try main dashboard
http://localhost:8000/

# Or status page
http://localhost:8000/status
```

### Test API

```bash
curl http://localhost:8000/api/programs | python3 -m json.tool
```

### Check Services

```bash
curl http://localhost:8000/api/status | python3 -m json.tool
```

---

## 📚 Documentation Links

- **Quick Start:** QUICK_START.md
- **API Reference:** API_REFERENCE.md
- **Deployment:** DEPLOYMENT_GUIDE.md
- **Security:** SECURITY_AUDIT_REPORT.md
- **Tests:** FUNCTIONAL_TEST_REPORT.md

---

## 🎉 Summary

### Total URLs Available: 13

**HTML Pages (4):**

- `/` - Main dashboard
- `/status` - System status page
- `/tools` - Tools overview
- `/programs` - Voice programs page

**API Endpoints (9):**

- `/api/status` - JSON status
- `/api/tools` - JSON tools list
- `/api/programs` - JSON programs list
- `/api/file/list` - File listing
- `/api/file/read` - Read file
- `/api/file/write` - Write file
- `/api/file/delete` - Delete file
- `/api/shell/exec` - Execute command
- `/api/program/start` - Start program

**All URLs are production-ready and fully tested!** ✅

---

**Version:** 1.0
**Status:** ✅ COMPLETE & OPERATIONAL
**Last Updated:** 2025-11-24
**Ready:** YES 🚀

```bash
# Quick start:
curl http://localhost:8000/status
# or open in browser:
http://localhost:8000
```
