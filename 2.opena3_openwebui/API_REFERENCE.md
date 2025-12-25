# 📚 OpenA3 Web Dashboard - API Reference Guide

**Base URL:** `http://localhost:8000`
**Version:** 1.0
**Status:** ✅ Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Error Handling](#error-handling)
4. [GET Endpoints](#get-endpoints)
5. [POST Endpoints](#post-endpoints)
6. [Examples](#examples)
7. [Rate Limiting](#rate-limiting)
8. [Best Practices](#best-practices)

---

## Overview

### API Characteristics

- **Type:** RESTful API
- **Data Format:** JSON
- **Protocol:** HTTP/1.0
- **Port:** 8000
- **Encoding:** UTF-8
- **CORS:** Enabled (`*`)

### Response Structure

All responses follow standard JSON format:

**Success (200-299):**

```json
{
  "status": "ok",
  "data": { ... },
  "timestamp": "2025-11-24T06:10:00.000000"
}
```

**Error (400-599):**

```json
{
  "error": "Description of error",
  "status_code": 400,
  "timestamp": "2025-11-24T06:10:00.000000"
}
```

---

## Authentication

### Current Status

**No authentication required** (assumes trusted network)

### For Production

Add token-based authentication:

```bash
# Set token environment variable
export API_TOKEN="your-secret-token-here"

# Use in requests
curl -H "Authorization: Bearer $API_TOKEN" \
  http://localhost:8000/api/programs
```

---

## Error Handling

### HTTP Status Codes

| Code  | Meaning                            | Example                          |
| ----- | ---------------------------------- | -------------------------------- |
| `200` | OK - Request successful            | `GET /api/status`                |
| `201` | Created - Resource created         | `POST /api/file/write`           |
| `400` | Bad Request - Invalid input        | `{"path": "../../etc/passwd"}`   |
| `403` | Forbidden - Access denied          | `{"command": "sudo apt update"}` |
| `404` | Not Found - Resource missing       | `GET /nonexistent`               |
| `408` | Timeout - Execution exceeded limit | Long-running shell command       |
| `500` | Server Error - Unexpected error    | Malformed JSON                   |

### Error Response Format

```json
{
  "error": "Command 'sudo' not allowed",
  "allowed": ["ls", "pwd", "echo", ...],
  "status_code": 403,
  "timestamp": "2025-11-24T06:10:00.000000"
}
```

### Common Error Messages

| Error                         | Cause                   | Solution                             |
| ----------------------------- | ----------------------- | ------------------------------------ |
| `Invalid path`                | Path traversal detected | Use relative paths only              |
| `File not found`              | File doesn't exist      | Verify file path and name            |
| `Command not allowed`         | Command not whitelisted | Use allowed commands only            |
| `Program not found`           | Program not in tools/   | Check program name exists            |
| `Only voice programs allowed` | Wrong file pattern      | Use `voice_*.py` pattern             |
| `Command execution timeout`   | Took >10 seconds        | Optimize command or increase timeout |

---

## GET Endpoints

### GET / (Dashboard HTML)

Serves the main web dashboard interface.

**Request:**

```http
GET / HTTP/1.1
Host: localhost:8000
```

**Response:**

```http
HTTP/1.0 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 37191

<!DOCTYPE html>
<html lang="de">
...
</html>
```

**Use Cases:**

- Browser access to web dashboard
- Display voice programs and tools
- Interactive UI for all operations

---

### GET /api/status (System Status)

Returns current system status and running services.

**Request:**

```bash
curl http://localhost:8000/api/status
```

**Response:**

```json
{
  "status": "online",
  "timestamp": "2025-11-24T06:10:42.730576",
  "version": "1.0.0",
  "services": {
    "localaagent-pro": "running",
    "ollama": "running",
    "openwebui": "running",
    "http-server": "running"
  }
}
```

**Parameters:** None

**Error Cases:**

- `500` - If services can't be queried

---

### GET /api/programs (List Voice Programs)

Returns list of available voice programs.

**Request:**

```bash
curl http://localhost:8000/api/programs
```

**Response:**

```json
[
  {
    "name": "voice_assistant.py",
    "description": "AI-powered voice command assistant",
    "lines": 138,
    "category": "assistant"
  },
  {
    "name": "voice_command_parser.py",
    "description": "Parse and execute voice commands",
    "lines": 147,
    "category": "parser"
  },
  ...
]
```

**Parameters:** None

**Use Cases:**

- Display available programs
- Build program selection UI
- Program discovery

---

### GET /api/tools (List Tools)

Returns list of available tools and APIs.

**Request:**

```bash
curl http://localhost:8000/api/tools
```

**Response:**

```json
{
  "tools": [
    {
      "name": "File Manager",
      "endpoints": [
        "/api/file/read",
        "/api/file/write",
        "/api/file/delete",
        "/api/file/list"
      ],
      "description": "Read, write, delete, and list files"
    },
    {
      "name": "Shell Executor",
      "endpoints": ["/api/shell/exec"],
      "description": "Execute whitelisted shell commands"
    },
    {
      "name": "Program Launcher",
      "endpoints": ["/api/program/start"],
      "description": "Start voice programs in background"
    }
  ]
}
```

**Parameters:** None

---

### GET /api/file/list (File Browser)

Lists files and directories in current path.

**Request:**

```bash
curl "http://localhost:8000/api/file/list"
```

**Response:**

```json
{
  "files": [
    {
      "name": "web_dashboard.py",
      "type": "file",
      "size": 49887,
      "modified": "2025-11-24T05:58:00"
    },
    {
      "name": "tools",
      "type": "directory",
      "size": 4096,
      "modified": "2025-11-24T05:26:00"
    }
  ],
  "total_files": 8,
  "total_size": 65536
}
```

**Parameters:** None (lists current working directory)

**Error Cases:**

- `404` - If directory doesn't exist
- `500` - If permission denied

---

## POST Endpoints

### POST /api/file/read (Read File)

Reads and returns file content.

**Request:**

```bash
curl -X POST http://localhost:8000/api/file/read \
  -H "Content-Type: application/json" \
  -d '{
    "path": "tools/voice_assistant.py"
  }'
```

**Request Body:**

```json
{
  "path": "tools/voice_assistant.py"
}
```

**Response (200):**

```json
{
  "status": "ok",
  "path": "tools/voice_assistant.py",
  "content": "#!/usr/bin/env python3\n\"\"\"Voice Assistant...",
  "size": 4523,
  "encoding": "utf-8"
}
```

**Response (400):**

```json
{
  "error": "Invalid path",
  "reason": "Path traversal detected"
}
```

**Response (404):**

```json
{
  "error": "File not found",
  "path": "nonexistent.py"
}
```

**Parameters:**

- `path` (string, required): Relative file path
  - Allowed: `tools/voice_*.py`, `*.txt`, etc.
  - Blocked: Absolute paths (`/etc/...`), traversal (`../../`)

**Limitations:**

- File must be readable as text (UTF-8)
- Max 1MB files (with default config)
- Only relative paths from current directory

**Use Cases:**

- Read program source code
- Read configuration files
- Display log files
- View documentation

---

### POST /api/file/write (Write File)

Creates or overwrites file with provided content.

**Request:**

```bash
curl -X POST http://localhost:8000/api/file/write \
  -H "Content-Type: application/json" \
  -d '{
    "path": "test_file.txt",
    "content": "Hello World!"
  }'
```

**Request Body:**

```json
{
  "path": "test_file.txt",
  "content": "Hello World!"
}
```

**Response (200):**

```json
{
  "status": "ok",
  "path": "test_file.txt",
  "size": 12,
  "message": "File written successfully"
}
```

**Response (400):**

```json
{
  "error": "Invalid path",
  "reason": "Cannot write to system directory"
}
```

**Parameters:**

- `path` (string, required): Relative file path
- `content` (string, required): File content to write
  - Max 1MB with default config
  - UTF-8 encoding

**Behavior:**

- Creates parent directories automatically
- Overwrites existing files
- Creates new file if doesn't exist

**Use Cases:**

- Create configuration files
- Write logs
- Save user data
- Create test files

---

### POST /api/file/delete (Delete File)

Deletes specified file.

**Request:**

```bash
curl -X POST http://localhost:8000/api/file/delete \
  -H "Content-Type: application/json" \
  -d '{
    "path": "test_file.txt"
  }'
```

**Request Body:**

```json
{
  "path": "test_file.txt"
}
```

**Response (200):**

```json
{
  "status": "ok",
  "path": "test_file.txt",
  "message": "File deleted successfully"
}
```

**Response (404):**

```json
{
  "error": "File not found",
  "path": "nonexistent.txt"
}
```

**Parameters:**

- `path` (string, required): Relative file path to delete

**Constraints:**

- Cannot delete protected system files
- Only deletes files (not directories)
- Path traversal blocked

**Use Cases:**

- Clean up temporary files
- Remove old logs
- Housekeeping

---

### POST /api/shell/exec (Execute Shell Command)

Executes whitelisted shell command and returns output.

**Request:**

```bash
curl -X POST http://localhost:8000/api/shell/exec \
  -H "Content-Type: application/json" \
  -d '{
    "command": "ls -la"
  }'
```

**Request Body:**

```json
{
  "command": "ls -la"
}
```

**Response (200):**

```json
{
  "status": "ok",
  "command": "ls -la",
  "returncode": 0,
  "stdout": "drwxrwxr-x  3 user user 4096 Nov 24 05:50 .\n...",
  "stderr": "",
  "message": "Command executed successfully"
}
```

**Response (403):**

```json
{
  "error": "Command 'sudo' not allowed",
  "allowed": [
    "ls",
    "pwd",
    "echo",
    "cat",
    "grep",
    "find",
    "wc",
    "head",
    "tail",
    "date",
    "whoami",
    "mkdir",
    "rm",
    "cp",
    "mv",
    "touch",
    "chmod",
    "python3",
    "pip3"
  ]
}
```

**Response (408):**

```json
{
  "error": "Command execution timeout (>10s)",
  "command": "sleep 15"
}
```

**Parameters:**

- `command` (string, required): Shell command to execute
  - First word must be in whitelist
  - Examples: `echo hello`, `ls -la`, `python3 script.py`

**Whitelisted Commands:**

```
ls, pwd, echo, cat, grep, find, wc, head, tail, date,
whoami, mkdir, rm, cp, mv, touch, chmod, python3, pip3
```

**Constraints:**

- 10-second timeout maximum
- Output limited to 5000 characters (stdout + stderr)
- Shell injection not possible (array execution)

**Use Cases:**

- List directory contents
- Run Python scripts
- Check system status
- Manage files

---

### POST /api/program/start (Start Voice Program)

Starts a voice program in background.

**Request:**

```bash
curl -X POST http://localhost:8000/api/program/start \
  -H "Content-Type: application/json" \
  -d '{
    "file": "voice_assistant.py"
  }'
```

**Request Body:**

```json
{
  "file": "voice_assistant.py"
}
```

**Response (200):**

```json
{
  "status": "ok",
  "file": "voice_assistant.py",
  "filepath": "tools/voice_assistant.py",
  "pid": 637341,
  "message": "✅ Programm 'voice_assistant.py' gestartet (PID: 637341)"
}
```

**Response (403):**

```json
{
  "error": "Only voice programs allowed",
  "pattern": "voice_*.py"
}
```

**Response (404):**

```json
{
  "error": "Program not found: voice_fake.py"
}
```

**Parameters:**

- `file` (string, required): Voice program filename
  - Pattern: `voice_*.py` (e.g., `voice_assistant.py`)
  - Must exist in `tools/` directory

**Return Value:**

- `pid` (integer): Process ID of started program
- Use for monitoring or stopping process

**Execution:**

- Runs in background with isolated stdout/stderr
- Parent process returns immediately
- Program continues even if connection closes

**Available Programs:**

```
- voice_assistant.py
- voice_command_parser.py
- voice_call_system.py
- voice_note_recorder.py
- voice_transcriber.py
- voice_scheduler.py
```

**Use Cases:**

- Start voice processing
- Launch background workers
- Trigger scheduled tasks

---

## Examples

### Example 1: Read and Display File Content

```bash
#!/bin/bash

FILE="tools/voice_assistant.py"

curl -s -X POST http://localhost:8000/api/file/read \
  -H "Content-Type: application/json" \
  -d "{\"path\":\"$FILE\"}" \
  | python3 -m json.tool | head -50
```

### Example 2: Execute Command and Parse Output

```bash
#!/bin/bash

curl -s -X POST http://localhost:8000/api/shell/exec \
  -H "Content-Type: application/json" \
  -d '{"command":"ls -la tools/"}' \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Files in tools/:')
for line in data['stdout'].split('\n'):
    if line.strip():
        print('  ', line)
"
```

### Example 3: Start Multiple Programs

```bash
#!/bin/bash

for program in voice_assistant.py voice_transcriber.py; do
    echo "Starting $program..."

    response=$(curl -s -X POST http://localhost:8000/api/program/start \
      -H "Content-Type: application/json" \
      -d "{\"file\":\"$program\"}")

    pid=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['pid'])")
    echo "  ✅ Started with PID: $pid"

    sleep 1
done
```

### Example 4: Create Configuration File

```bash
#!/bin/bash

CONFIG='{"version":"1.0","debug":true,"port":8000}'

curl -s -X POST http://localhost:8000/api/file/write \
  -H "Content-Type: application/json" \
  -d "{
    \"path\": \"config.json\",
    \"content\": \"$CONFIG\"
  }" | python3 -m json.tool
```

### Example 5: Health Check Script

```bash
#!/bin/bash

echo "Health Check for OpenA3 Dashboard"
echo "=================================="

# Check API status
STATUS=$(curl -s http://localhost:8000/api/status | \
  python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('status', 'unknown'))")

if [ "$STATUS" = "online" ]; then
    echo "✅ Status: ONLINE"
else
    echo "❌ Status: OFFLINE"
    exit 1
fi

# Check programs
PROGRAMS=$(curl -s http://localhost:8000/api/programs | \
  python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d))")

echo "✅ Programs available: $PROGRAMS"

# Check shell
curl -s -X POST http://localhost:8000/api/shell/exec \
  -H "Content-Type: application/json" \
  -d '{"command":"echo test"}' > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ Shell execution: WORKING"
else
    echo "❌ Shell execution: FAILED"
    exit 1
fi

echo ""
echo "All checks passed!"
```

---

## Rate Limiting

### Current Status

**No rate limiting** (assumes trusted network)

### Recommended for Production

```python
# Add rate limiting
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, requests=5, window=60):
        self.requests = requests
        self.window = window
        self.requests_by_ip = defaultdict(list)

    def is_allowed(self, ip):
        now = time.time()
        reqs = self.requests_by_ip[ip]
        reqs = [t for t in reqs if now - t < self.window]

        if len(reqs) < self.requests:
            reqs.append(now)
            self.requests_by_ip[ip] = reqs
            return True
        return False
```

---

## Best Practices

### 1. Error Handling

```bash
# Always check response status
response=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/status)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" != "200" ]; then
    echo "Error: HTTP $http_code"
    echo "$body" | python3 -m json.tool
    exit 1
fi
```

### 2. Retry Logic

```bash
# Retry failed requests
max_attempts=3
attempt=1

while [ $attempt -le $max_attempts ]; do
    response=$(curl -s -X POST http://localhost:8000/api/program/start \
      -H "Content-Type: application/json" \
      -d '{"file":"voice_assistant.py"}')

    if [ $? -eq 0 ]; then
        echo "$response" | python3 -m json.tool
        break
    fi

    echo "Attempt $attempt failed, retrying..."
    sleep $((attempt * 2))
    ((attempt++))
done
```

### 3. Timeout Handling

```bash
# Set curl timeout
curl --connect-timeout 5 --max-time 30 \
  http://localhost:8000/api/programs

# Or for shell execution
curl -X POST http://localhost:8000/api/shell/exec \
  -H "Content-Type: application/json" \
  -d '{"command":"long_running_command"}' \
  --max-time 15
```

### 4. Path Validation

```bash
# Always use relative paths
valid_path="tools/voice_assistant.py"  # ✅ OK
invalid_path="/etc/passwd"              # ❌ Blocked
invalid_path="../../etc/passwd"         # ❌ Blocked

# Validate before sending
if [[ $path == /* ]] || [[ $path == *..* ]]; then
    echo "Invalid path!"
    exit 1
fi
```

### 5. Request Formatting

```bash
# Escape special characters in JSON
content="Line 1
Line 2
Quote: \"test\""

# Use proper JSON encoding
curl -X POST http://localhost:8000/api/file/write \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "path": "output.txt",
  "content": $(echo "$content" | python3 -c "import sys, json; print(json.dumps(sys.stdin.read()))")
}
EOF
```

### 6. Logging

```bash
# Log all API calls
log_api_call() {
    local method=$1
    local endpoint=$2
    local timestamp=$(date -Iseconds)

    echo "[$timestamp] $method $endpoint" >> api.log
}

log_api_call "GET" "/api/status"
curl http://localhost:8000/api/status
```

---

## Related Documentation

- **Security:** See `SECURITY_AUDIT_REPORT.md`
- **Testing:** See `FUNCTIONAL_TEST_REPORT.md`
- **Deployment:** See `DEPLOYMENT_GUIDE.md`
- **Source Code:** See `web_dashboard.py`

---

## Support

### Getting Help

1. Check response `error` message
2. Review status code (400=bad input, 403=forbidden, 404=not found, 500=server error)
3. Check endpoint documentation above
4. Review examples section

### Common Issues

| Issue              | Solution                                                |
| ------------------ | ------------------------------------------------------- |
| 404 Not Found      | Endpoint doesn't exist - check URL spelling             |
| 400 Bad Request    | Invalid path (use relative paths only)                  |
| 403 Forbidden      | Command/program not allowed - check whitelist           |
| 408 Timeout        | Command took >10 seconds - optimize or increase timeout |
| Connection refused | Server not running - start web_dashboard.py             |

---

**Version:** 1.0
**Last Updated:** 2025-11-24
**Status:** ✅ Production Ready
