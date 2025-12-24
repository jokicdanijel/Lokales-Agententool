[PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]

# Phase 4.1 Architecture Diagram & File Structure

**Purpose:** Visual reference for team + system architecture overview
**Format:** ASCII + Text Descriptions
**Target:** All stakeholders, developers, QA, DevOps

---

## 📐 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ELION Hyper-Dashboard v1.0                   │
│                         (Phase 4.1)                             │
└─────────────────────────────────────────────────────────────────┘

                        ┌─────────────────┐
                        │  VS Code IDE    │
                        │  + Extension    │ ← Pos. 14
                        └────────┬────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
            ┌───────▼──────┐  ┌──▼─────┐  ┌──▼────────┐
            │  Bridge      │  │Monitor │  │Extension  │
            │  Service     │  │ Queue  │  │  (Chat)   │
            │  Port 12351  │  │Port UI │  │Port 12352 │
            │  (Pos. 01)   │  │(Pos3)  │  │(Pos. 14)  │
            └───────┬──────┘  └──┬─────┘  └──┬────────┘
                    │            │           │
         ┌──────────┼────────────┼───────────┤
         │          │            │           │
    ┌────▼──┐  ┌───▼───┐  ┌────▼────┐  ┌───▼────┐
    │ Auth  │  │ Queue │  │ DLQ     │  │Sandbox │
    │ RBAC  │  │Mgmt   │  │Handler  │  │ Check  │
    │(Pos01)│  │(Pos05)│  │(Pos15)  │  │(Pos06) │
    └───────┘  └───────┘  └─────────┘  └────────┘
         │          │            │           │
         └──────────┼────────────┼───────────┘
                    │            │
         ┌──────────▼────────────▼───────────┐
         │                                   │
         │   Dashboard API (12349)           │
         │   - OpenAPI Schema (Pos. 02)      │
         │   - Rate Limiting (Pos. 07)       │
         │   - Audit Logging (Pos. 17)       │
         │   - E2E Test (Pos. 11)            │
         │                                   │
         └──────────┬────────────┬───────────┘
                    │            │
         ┌──────────▼──┐  ┌──────▼───────┐
         │ opena1 Agent│  │ opena2 Archiv│
         │ (12344)     │  │ (12345)      │
         │ GPT Mode    │  │ Storage      │
         └─────────────┘  └──────────────┘
```

---

## 📁 Complete File Structure (Phase 4.1)

```
Gesamtprojekt/
│
├── 📄 PHASE_4_1_FINAL_STATUS_REPORT.md (THIS OVERVIEW)
├── 📄 PHASE_4_1_EXECUTIVE_SUMMARY.md
├── 📄 PHASE_4_1_DEPLOYMENT_CHECKLIST.md
│
├── .github/
│   ├── 📄 copilot-instructions.md (Phase 3 – AI guidance)
│   ├── 📄 SYSTEM_ANALYSIS_BYPASS_MECHANISMS.md (Phase 4.0 – Governance)
│   ├── 📄 COMPLETION_CHECKLIST.md (Phase 3 summary)
│   └── workflows/ (TODO – Phase 4.1, Pos. 20)
│
├── bin/ (ROOT WRAPPERS)
│   ├── 📄 system_mode_switch.sh ⭐ [NEW – TASK 01]
│   ├── 📄 ops.sh (Phase 3)
│   ├── 📄 start_all.sh (Phase 3)
│   └── [12 more orchestration scripts]
│
├── 19.dashboard_agent/
│   │
│   ├── .vscode/
│   │   ├── portier-bridge/
│   │   │   └── 📄 BOOTSTRAP_PDI_PROMPT.md ⭐ [NEW – Copilot Init]
│   │   ├── 📄 launch.json (Debug configs)
│   │   └── 📄 tasks.json (VS Code tasks)
│   │
│   ├── docs/
│   │   ├── PDI/
│   │   │   ├── 📄 README.md (Navigation center)
│   │   │   ├── 📄 project_manifest.md (Master doc – 293 lines)
│   │   │   ├── 📄 glossary.md (40+ terms – 600+ lines)
│   │   │   ├── 📄 VALIDATION_FRAMEWORK.md (QA guide)
│   │   │   ├── 📄 PHASE_4_QUICKSTART.md (Week 1 daily plan)
│   │   │   ├── 📄 DEV_PROD_SWITCH_BLUEPRINT.md (Implementation)
│   │   │   │
│   │   │   ├── chapters/
│   │   │   │   ├── 📄 00_kapitelplan.md (20 positions – 332 lines)
│   │   │   │   ├── 📄 01_pipeline_automation.md (8-stage process)
│   │   │   │   ├── 📄 PHASE_4_1_TASK_PROGRESS.md (Task tracking)
│   │   │   │   └── [Future: 02–20_*.md]
│   │   │   │
│   │   │   └── validation/
│   │   │       ├── 📄 consistency_report.md (10-point check)
│   │   │       ├── 📄 structure_check.json (Machine-readable)
│   │   │       └── 📄 validation_log.csv (27 audit entries)
│   │   │
│   │   ├── 📄 OPENWEBUI_API.md (Phase 3)
│   │   ├── 📄 TROUBLESHOOTING.md (Phase 3)
│   │   └── 📄 OPENWEBUI_TODO.md (Phase 3)
│   │
│   ├── bin/ (DASHBOARD-SPECIFIC)
│   │   ├── 📄 start_all.sh
│   │   ├── 📄 stop_all.sh
│   │   ├── 📄 verify_stack.sh
│   │   └── [15 more scripts]
│   │
│   ├── scripts/
│   │   ├── 📄 test_openwebui.py (Phase 3)
│   │   └── [Future: 02_audit_security.py, 06_rotate_tokens.sh, etc.]
│   │
│   ├── tests/
│   │   ├── 📄 test_archivator.py (Phase 3)
│   │   ├── 📄 test_openwebui_agent.py (Phase 3)
│   │   └── [Future: test_pipeline_e2e.py (Pos. 07)]
│   │
│   ├── 📄 main_dashboard.py (Central API)
│   ├── 📄 main_opena1.py (AI Agent)
│   ├── 📄 main_opena2.py (Archivator)
│   ├── 📄 main_kordp.py (Coordinator)
│   ├── 📄 main_openwebui_agent.py (OpenWebUI adapter)
│   ├── 📄 config.py (Config + env handling)
│   ├── 📄 security.py (Auth + RBAC)
│   ├── 📄 sse_bus.py (Event streaming)
│   ├── 📄 requirements.txt (Dependencies)
│   │
│   └── templates/
│       ├── 📄 dashboard.html
│       ├── 📄 agent.html
│       └── 📄 base.html
│
├── 1.opena1&2_portier/
│   ├── 📁 venv313/ (Python environment – Phase 1)
│   ├── 📄 setup_venv313.sh
│   └── 📁 archivp/ (Data storage)
│
├── 2.openwebui/
│   ├── 📄 docker-compose.yml (Phase 3)
│   └── 📄 docker-agent.sh
│
├── docker/ (FUTURE – Phase 4.1)
│   ├── 📄 Dockerfile.bridge (Pos. 12)
│   ├── 📄 docker-compose.yml (Pos. 13)
│   └── 📄 docker-compose.prod.yml
│
├── systemd/ (FUTURE – Phase 4.1)
│   ├── 📄 bridge.service (Pos. 18)
│   ├── 📄 dashboard.service (Pos. 19)
│   └── 📄 adapter.service (Pos. 20)
│
├── .env (Token storage – auto-generated)
├── .env.development (NEW – Phase 4.1 Pos. 01)
├── .env.staging (NEW – Phase 4.1 Pos. 06)
├── .env.production (NEW – Phase 4.1 Pos. 01)
│
└── logs/
    ├── 📄 system_mode_audit.log (NEW – Pos. 01)
    ├── 📄 dashboard.nohup.log
    ├── 📄 opena1.nohup.log
    ├── 📄 opena2.nohup.log
    └── 📄 kordp.nohup.log
```

**Legend:**
- ⭐ = NEW (just created Nov 6)
- 📄 = File
- 📁 = Directory
- Phase 3 = Operational
- Phase 4.1 = In development

---

## 🔄 Data Flow Diagram (Phase 4.1)

```
┌──────────────────────────────────────────────────────┐
│                 VS Code User                         │
│              (writes chat message)                   │
└──────────────────┬───────────────────────────────────┘
                   │
                   │ (1) POST /chat (with Bearer token)
                   ▼
┌──────────────────────────────────────────────────────┐
│        VS Code Extension (Port 12352)                │
│        - Auth Handler (Pos. 01)                      │
│        - Task Serializer                             │
│        - Streaming Result Receiver                   │
└──────────┬───────────────────────────────────────────┘
           │
           │ (2) POST /api/execute (Bearer token)
           ▼
┌──────────────────────────────────────────────────────┐
│      Dashboard API (Port 12349)                      │
│      - Token Validation (RBAC)                       │
│      - Request Router                               │
│      - Response Formatter                           │
└──────────┬───────────────────────────────────────────┘
           │
           │ (3) Dispatch to Queue (Pos. 05)
           ▼
┌──────────────────────────────────────────────────────┐
│      Bridge Queue Service (Port 12351) [NEW]        │
│      - Queue Management (Pos. 05)                   │
│      - Retry/Backoff Logic (Pos. 04)               │
│      - DLQ Handling (Pos. 15)                      │
│      - Task Streaming (Pos. 15)                    │
└──────────┬───────────────────────────────────────────┘
           │
           │ (4) Execute Task
           │
    ┌──────┴──────┬──────────────┬──────────┐
    │             │              │          │
    ▼             ▼              ▼          ▼
┌────────┐  ┌─────────┐  ┌────────────┐ ┌─────────┐
│opena1  │  │opena2   │  │Sandboxed   │ │External │
│(Chat)  │  │(Storage)│  │Cmd Exec    │ │API Call │
└────────┘  └─────────┘  │(Pos. 06)   │ │(Pos. 06)│
                         └────────────┘ └─────────┘
    │             │              │          │
    │             │    Write     │          │
    │             │    State     │          │
    └──────────┬──────────────────┬─────────┘
               │                  │
               │ Archive Results  │
               ▼                  ▼
        ┌──────────────────────────────────┐
        │  Archivator (opena2, Port 12345) │
        │  Immutable Audit Trail           │
        │  (Safepoints)                    │
        └──────────────────────────────────┘
               │
               │ Return Results
               ▼
        ┌──────────────────────────────────┐
        │  SSE Stream → VS Code Extension  │
        │  (Pos. 15 – Task Execution)      │
        └──────────────────────────────────┘
               │
               │ Display in Chat
               ▼
        ┌──────────────────────────────────┐
        │  User sees live result stream    │
        │  (typed character by character)  │
        └──────────────────────────────────┘
```

---

## ⚙️ Mode Switching (DEV ↔ PROD)

```
┌─────────────────────────────────────────────────────────┐
│            bin/system_mode_switch.sh                    │
│           (TASK 01 – Executable)                        │
└─────────────────────────────────────────────────────────┘

COMMAND: bin/system_mode_switch.sh switch production

                    │
                    ▼
        ┌───────────────────────┐
        │ Read Current Mode     │
        │ (from .env.current)   │
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │ Validate Target Env   │
        │ (check ports, files)  │
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │ Confirm (PROD only)   │
        │ "Type 'yes' to proceed"│
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │ Stop All Services     │
        │ (bin/ops.sh stop)     │
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │ Apply Config          │
        │ - Enable/Disable      │
        │   Bypasses            │
        │ - Set Token Storage   │
        │ - Set Log Level       │
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │ Log Audit Entry       │
        │ (logs/system_mode_    │
        │  audit.log)           │
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │ ✅ Mode Switched      │
        │ (ready to restart)    │
        └───────────────────────┘
```

---

## 🏗️ Build Pipeline (Phase 4.1)

```
Developer writes code (Task 02–20)
          │
          ▼
┌─────────────────────┐
│ Local Tests         │
│ pytest tests/ -q    │
│ (>80% coverage req) │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Code Linting        │
│ pylint *.py         │
│ (score ≥9.0)       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Format Check        │
│ black --check .     │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Security Audit      │
│ audit_security.py   │
│ (check for bypasses)│
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Git Commit          │
│ PDI-GEN: Task XX    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ GitHub Actions      │
│ (CI/CD Checks)      │
│ - Lint              │
│ - Build             │
│ - Test              │
│ - Security Scan     │
└─────────┬───────────┘
          │
    ┌─────┴──────┐
    │             │
   ✅ PASS       ❌ FAIL
    │             │
    ▼             ▼
┌──────────┐  ┌──────────────┐
│ Approve  │  │ Request      │
│ for      │  │ Changes      │
│ Merge    │  │ (Retry)      │
└─────┬────┘  └──────────────┘
      │
      ▼
┌──────────────────────────┐
│ Merge to feature branch  │
│ (feature/phase-4-bridge) │
└──────────────────────────┘
      │
      ▼
┌──────────────────────────┐
│ Task marked DONE         │
│ Progress board updated   │
│ (PHASE_4_1_TASK_         │
│  PROGRESS.md)            │
└──────────────────────────┘
```

---

## 📊 Week 1 Schedule (Nov 7–14)

```
MON (7):  ├─ 09:00 Kickoff Meeting
          ├─ 10:00 Task 02 Intro (audit_security.py)
          ├─ 11:00 Coding starts
          └─ 17:00 Standup

TUE (8):  ├─ 09:00 Task 02 code review
          ├─ 11:00 Task 03 Intro (config_report.md)
          └─ 17:00 Standup

WED (9):  ├─ 09:00 Task 03 review
          ├─ 11:00 Task 04 Intro (Governance_Policy.md)
          └─ 17:00 Standup

THU (10): ├─ 09:00 Task 04 review
          ├─ 11:00 Task 05 Intro (release.sh)
          └─ 17:00 Standup

FRI (11): ├─ 09:00 Task 05 review
          ├─ 10:00 Buffer / Testing
          └─ 14:00 Week 1 Retrospective

TOTAL: 5 tasks → Target: 80%+ complete by Fri night
```

---

## 🎯 Success Indicators

### Week 1 (Nov 7–14) ✅
```
[ ] Task 01 ✅ (already done)
[ ] Task 02 implemented
[ ] Task 03 implemented
[ ] Task 04 implemented
[ ] Task 05 implemented
[ ] All tests pass (>80% coverage)
[ ] All lint checks pass (score ≥9.0)
[ ] No security findings
[ ] Code reviews approved
```

### By Dec 5 (Phase 4.1 Complete) 🚀
```
[ ] 20/20 tasks complete
[ ] v1.0 tagged on GitHub
[ ] Docker image published
[ ] CI/CD pipeline green
[ ] >50 tasks/min benchmark met
[ ] Zero critical bugs
[ ] Deployment documented
[ ] Team trained
[ ] Handoff ready
```

---

**[PDI-FOOTER: Architecture Overview | Status: FINAL | Version: 1.0 | For: All Stakeholders | Date: 2025-11-06]**
