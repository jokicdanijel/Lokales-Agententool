# C++ Build System & Makefile Reference für ELION Hyper-Dashboard

## 1. Project Overview

**Projekt:** ELION Hyper-Dashboard  
**Typ:** C++ / Multi-Language Microservices  
**Build System:** GNU Make + Custom Scripts  
**Primary Language:** C++ (utilities) + Python (services)  
**Target OS:** Linux (Ubuntu 25.04)  

### Key Architecture
- **Core:** Makefile-based build orchestration
- **Services:** 20+ Python-based agents (FastAPI, nohup-managed)
- **Monitoring:** Prometheus + Grafana (port 3001)
- **Infrastructure:** docker-compose.prod.yml (22 containers)
- **API Gateway:** Portier (port 12344)

---

## 2. Build System Fundamentals

### Makefile Structure
```makefile
# Location: /path/to/Gesamtprojekt/Makefile
# Root orchestrator for all build, test, deploy operations

# Key Targets:
make build              # Compile all C++ utilities
make test               # Run complete test suite
make install            # Install binaries + dependencies
make clean              # Remove build artifacts
make docker-build       # Build docker-compose stack
make docker-up          # Start all services
make docker-down        # Stop all services
```

### Standard Targets Pattern
```makefile
.PHONY: target-name
target-name:
	@echo "Description"
	@command1 && command2
```

### Variable Definitions
```makefile
# Common patterns
SHELL := /bin/bash
CC := g++
CFLAGS := -std=c++17 -Wall -O2
PYTHON := python3
VENV := venv313
```

---

## 3. Build Commands

### Full Build Cycle
```bash
# From project root
make clean                 # Remove build artifacts
make build                 # Compile C++ binaries
make test                  # Run unit tests
make install               # Install binaries to bin/
```

### Component Builds
```bash
# Build specific service group
make build-services        # Rebuild all 20 services
make build-monitoring      # Prometheus + Grafana configs
make build-apis            # FastAPI applications

# Partial builds (if supported)
make build-utils           # C++ utilities only
make build-connectors      # Connector modules
```

### Testing
```bash
# Test patterns
make test                  # All tests
make test-unit             # Unit tests only
make test-integration      # Integration tests
make test-load             # Load/stress testing
make test-coverage         # Coverage report

# Example test file: tests/test_portier.cpp
g++ -std=c++17 -Wall tests/test_portier.cpp -o /tmp/test_portier && /tmp/test_portier
```

---

## 4. Makefile Patterns & Conventions

### Variable Scoping
```makefile
# Global variables (top of file)
VERSION := 1.0.0
BUILD_DIR := build
BIN_DIR := bin

# Local variables (within target)
target-name:
	$(eval LOCAL_VAR = value)
	@echo $(LOCAL_VAR)
```

### Conditional Logic
```makefile
# Check if variable set
ifeq ($(VAR),)
	VAR := default_value
endif

# Check file existence
ifeq ($(wildcard Makefile),)
	$(error Makefile not found)
endif

# Platform detection
ifeq ($(OS),Windows_NT)
	RM := del
else
	RM := rm -f
endif
```

### Include Pattern
```makefile
# Include other Makefiles
-include make/rules.mk
-include make/docker.mk
-include make/deploy.mk

# Allows modular organization without breaking if file missing
```

### Phony Targets
```makefile
# Declare non-file targets
.PHONY: clean build test install deploy
# Ensures make doesn't check for files named clean, build, etc.
```

---

## 5. Python Integration

### Python in Makefile
```makefile
# Using Python for complex tasks
test-python:
	@$(PYTHON) -m pytest tests/ -v --cov

# Running scripts
setup-env:
	@$(PYTHON) scripts/env_setup.py

# Version check
check-python:
	@$(PYTHON) --version | grep "3\."
```

### Virtual Environment Pattern
```makefile
# In ELION Dashboard context
setup-venv:
	@python3 -m venv venv313
	@source venv313/bin/activate && pip install -r requirements.txt
	@echo "✓ venv313 ready"

# Running with venv
run-service:
	@source venv313/bin/activate && python3 src/services/agenda_api.py
```

---

## 6. Docker Integration

### Docker Targets
```makefile
# Build patterns
docker-build:
	docker compose -f docker-compose.prod.yml build

docker-up:
	docker compose -f docker-compose.prod.yml up -d

docker-down:
	docker compose -f docker-compose.prod.yml down

docker-logs:
	docker compose -f docker-compose.prod.yml logs -f

# Service-specific
docker-logs-service:
	docker compose -f docker-compose.prod.yml logs -f service_name
```

### Health Checks in Makefile
```makefile
docker-health:
	@for port in 12344 12345 12346 12348 12399; do \
		echo -n "Port $$port: "; \
		curl -s http://127.0.0.1:$$port/health | jq .status || echo "DOWN"; \
	done
```

---

## 7. Critical Workflows

### Full Stack Deployment
```makefile
# Production deployment workflow
deploy-prod: clean build test docker-build docker-up verify
	@echo "✓ Production deployment complete"

# Verification step
verify:
	@bash bin/verify_stack.sh
	@curl -s http://127.0.0.1:12349/api/status/all | jq .
```

### Development Workflow
```makefile
# Quick rebuild + restart
dev-rebuild: clean build
	@pkill -f "python3 src/services" || true
	@bash bin/start_all.sh
	@sleep 2 && make docker-health
```

### Continuous Integration Pattern
```makefile
ci: clean build test lint security-check
	@echo "✓ CI checks passed"

lint:
	@python3 -m flake8 src/ --max-line-length=120

security-check:
	@python3 -m bandit -r src/ -q
```

---

## 8. Debugging & Troubleshooting

### Makefile Debugging
```bash
# Show variables
make -n build                    # Dry-run (show commands, don't execute)
make --debug=b build             # Verbose debug output
make --trace build               # Show execution trace

# Check if target exists
make --just-print build          # Show what would be executed

# Print specific variable
make --debug=b 2>&1 | grep VARIABLE
```

### Common Issues
```makefile
# Issue: "missing separator" error
# Cause: Leading spaces instead of TAB in target commands
# Fix: Use Ctrl+V followed by Tab key

# Issue: "recipe for target failed"
# Cause: Command returned non-zero exit code
# Fix: Add - prefix to ignore errors (dangerous!)
# Better: Fix underlying command

# Example: Allow failures in some targets
clean:
	-rm -rf build/
	-pkill -f agenda_api
```

### Conditional Output
```makefile
# Suppress output
target-name:
	@command_here             # @ suppresses echo of command
	
# Show only on failure
target-name:
	@command_here > /tmp/out 2>&1 || (cat /tmp/out && exit 1)

# Progress indicators
deploy:
	@echo "Step 1/3: Building..."
	@make build
	@echo "Step 2/3: Testing..."
	@make test
	@echo "Step 3/3: Deploying..."
	@make docker-up
	@echo "✓ Complete"
```

---

## 9. VS Code C++ Setup

### Required Extensions
```json
{
  "recommendations": [
    "ms-vscode.cpptools",           // Microsoft C++ extension
    "ms-vscode.makefile-tools",     // Makefile support
    "ms-vscode-remote.remote-ssh",  // Remote development
    "GitHub.copilot",                // GitHub Copilot
    "GitHub.copilot-chat",           // Copilot chat
    "eamodio.gitlens"               // Git integration
  ]
}
```

### settings.json (C++ Makefile Project)
```json
{
  // C++ Extension Configuration
  "[cpp]": {
    "editor.defaultFormatter": "ms-vscode.cpptools",
    "editor.formatOnSave": true,
    "editor.formatOnPaste": true,
    "editor.tabSize": 4,
    "editor.insertSpaces": true
  },
  
  // Makefile Tools
  "makefile.configureOnOpen": true,
  "makefile.configureOnSave": true,
  "makefile.dryRunAfterConfigure": false,
  "makefile.launchConfiguration": [
    {
      "cwd": "${workspaceFolder}",
      "binaryPath": "${workspaceFolder}/bin/portier",
      "binaryArgs": ["--debug"]
    }
  ],

  // C++ IntelliSense
  "C_Cpp.intelliSenseEngine": "Tag Parser",
  "C_Cpp.intelliSenseEngineFallback": "Disabled",
  "C_Cpp.codeAnalysis.enabled": true,
  "C_Cpp.codeAnalysis.clangTidy.enabled": true,
  
  // Build/Debug
  "code-runner.executorMap": {
    "cpp": "cd $dir && make build && ./bin/portier"
  },
  
  // Python Integration (for mixed projects)
  "[python]": {
    "editor.defaultFormatter": "ms-python.python",
    "editor.formatOnSave": true,
    "editor.tabSize": 4
  },
  "python.analysis.typeCheckingMode": "strict",
  
  // Git Configuration
  "git.autorefresh": true,
  "git.autofetch": true,
  "git.ignoreLimitWarning": true,
  
  // General Settings
  "editor.wordWrap": "on",
  "editor.rulers": [80, 120],
  "editor.renderWhitespace": "trailing",
  "editor.trimAutoWhitespace": true,
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/build": true,
    "**/*.o": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/venv*": true,
    "**/.git": true
  }
}
```

### launch.json (C++ Debugging)
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Portier",
      "type": "cppdbg",
      "request": "launch",
      "program": "${workspaceFolder}/bin/portier",
      "args": ["--debug"],
      "stopAtEntry": false,
      "cwd": "${workspaceFolder}",
      "environment": [],
      "externalConsole": false,
      "MIMode": "gdb",
      "setupCommands": [
        {
          "description": "Enable pretty-printing for gdb",
          "text": "-enable-pretty-printing",
          "ignoreFailures": true
        }
      ]
    },
    {
      "name": "Debug Make Target",
      "type": "cppdbg",
      "request": "launch",
      "program": "${workspaceFolder}/bin/agenda_api",
      "args": [],
      "stopAtEntry": false,
      "cwd": "${workspaceFolder}",
      "MIMode": "gdb",
      "preLaunchTask": "build"
    }
  ],
  "compounds": []
}
```

### tasks.json (Build Tasks)
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "build",
      "type": "shell",
      "command": "make",
      "args": ["build"],
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      }
    },
    {
      "label": "test",
      "type": "shell",
      "command": "make",
      "args": ["test"],
      "group": "test",
      "presentation": {
        "reveal": "always"
      }
    },
    {
      "label": "clean",
      "type": "shell",
      "command": "make",
      "args": ["clean"],
      "presentation": {
        "reveal": "always"
      }
    },
    {
      "label": "run",
      "type": "shell",
      "command": "bash",
      "args": ["bin/start_all.sh"],
      "dependsOn": ["build"]
    }
  ]
}
```

---

## 10. Testing & Code Quality

### Testing Patterns
```bash
# Unit testing (C++)
g++ -std=c++17 -Wall tests/test_portier.cpp -o /tmp/test && /tmp/test

# Unit testing (Python)
python3 -m pytest tests/ -v --tb=short

# Integration testing
python3 -m pytest tests/integration/ -v --tb=short -s

# Coverage reporting
python3 -m pytest tests/ --cov=src --cov-report=html
```

### Code Quality Tools
```bash
# C++ linting
clang-tidy src/*.cpp -- -std=c++17

# Python linting
python3 -m flake8 src/ --max-line-length=120

# Python formatting
python3 -m black src/ --line-length=120

# Security checks
python3 -m bandit -r src/ -q
```

---

## 11. Key Files Reference

| File | Purpose | Type |
|------|---------|------|
| `Makefile` | Root build orchestrator | Build |
| `docker-compose.prod.yml` | Service stack definition | Config |
| `bin/ops.sh` | Central operations script | Script |
| `src/services/agenda_api.py` | Agenda API service | Python |
| `.github/copilot-instructions.md` | Completion checklist | Docs |
| `requirements.txt` | Python dependencies | Config |
| `Dockerfile.openwebui` | OpenWebUI container | Config |

---

## 12. Common Commands Cheatsheet

```bash
# Build & Deploy
make build                    # Compile all
make clean build test         # Full cycle
make docker-build docker-up   # Docker deployment

# Operations
bash bin/ops.sh start         # Start all services
bash bin/ops.sh stop          # Stop services
bash bin/ops.sh health        # Health check

# Testing
make test                     # All tests
python3 scripts/test_openwebui.py  # Specific test
curl -s http://127.0.0.1:12399/agenda/pages | jq .

# Debugging
make --debug=b build          # Debug make
docker compose logs -f        # Follow service logs
curl http://127.0.0.1:12349/api/status/all | jq .
```

---

## 13. Integration Points

### Portier (API Gateway)
- **Port:** 12344
- **Endpoints:** `/health`, `/metrics`
- **Makefile:** `make docker-health` to check

### Prometheus Metrics
- **Port:** 9090
- **Configuration:** `prometheus.yml`
- **Scrape Targets:** 22 configured

### Grafana Dashboards
- **Port:** 3001
- **Credentials:** admin/250886
- **Dashboards:** 6 configured (IDs 1-6)

---

## 14. Best Practices

1. **Always use `.PHONY`** for non-file targets
2. **Tab vs Spaces:** Makefile commands MUST start with TAB
3. **Error Handling:** Use `&&` for sequential commands, `||` for fallbacks
4. **Output:** Use `@` prefix to suppress command echo
5. **Documentation:** Comment complex targets clearly
6. **Idempotency:** Targets should be safe to run multiple times
7. **Variables:** Use uppercase for user-configurable values
8. **Scripts:** Keep complex logic in shell scripts, not Makefile

---

**Last Updated:** 2025-11-11  
**Project:** ELION Hyper-Dashboard  
**Status:** ✅ Active Development
