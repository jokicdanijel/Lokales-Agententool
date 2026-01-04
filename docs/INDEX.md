# 📚 ELION Hyper-Dashboard – Documentation Index

## 🚀 Quick Start

- 📖 **[Agent Startanleitung](./agent_startanleitung.html)** - Interaktive Anleitung für alle 22 Agenten (lokal)
- 🚀 **[Production Deployment Steps](./PRODUCTION_DEPLOYMENT_STEPS.md)** - Schritt-für-Schritt Guide für `https://hyperdashboard-one.de`
- ✅ **[Deployment Checklist](./DEPLOYMENT_CHECKLIST.md)** - Vollständige Deployment-Checkliste (Phase 5)

</html></body>    </script>        document.addEventListener('DOMContentLoaded', loadWorkflows);        // Initial load                });            });                }                    closeModal(modal.id);                if (e.target === modal) {            modal.addEventListener('click', (e) => {        document.querySelectorAll('.modal').forEach(modal => {        // Close modals on background click                }            document.getElementById('total-workflows').textContent = '2';            // Demo data        function loadWorkflows() {                }            openModal('examplesModal');        function showExamples() {                }            alert('📊 Analytics:\nMessages Today: 0\nWorkflows Triggered: 0\nAverage Response Time: --');        function viewAnalytics() {                }            alert('🤖 Registered Bots:\n\n1. browser_opena6_bot\n   Status: Active\n   \n2. open2tele_bot\n   Status: Active');        function viewBots() {                }            alert('📋 View all workflows:\ncurl http://127.0.0.1:12346/workflows | jq .');        function listWorkflows() {                }            loadWorkflows();            closeModal('workflowModal');            alert('✅ Workflow created successfully!');            e.preventDefault();        function handleCreateWorkflow(e) {                }            }                actionField.innerHTML = '<label class="form-label">Webhook URL</label><input type="url" class="form-input" id="action-response" placeholder="http://127.0.0.1:12344/log/opena1">';            } else if (type === 'webhook') {                actionField.innerHTML = '<label class="form-label">Response Message</label><textarea class="form-input" id="action-response" placeholder="Your response..." style="min-height: 80px;"></textarea>';            if (type === 'auto_reply') {                        const actionField = document.getElementById('action-field');            const type = document.getElementById('workflow-type').value;        function updateFields() {                }            openModal('workflowModal');            updateFields();            document.getElementById('workflow-type').value = type;        function createWorkflow(type) {                }            document.getElementById(modalId).classList.remove('active');        function closeModal(modalId) {                }            document.getElementById(modalId).classList.add('active');        function openModal(modalId) {    <script>        </div>        </div>            </div>}  "enabled": true  "action": {"message": "📌 Daily reminder: Check your tasks!"},  "trigger": {"schedule": "0 09 * * *"},  "type": "scheduled",  "name": "Daily Notification",  "bot_key": "open2tele_bot",{            <div class="code-block">            <h4 style="color: #e0e0e0; margin-bottom: 10px; margin-top: 15px;">Example 3: Daily Reminder</h4>                        </div>}  }    }      "source": "opena4"      "user_query": "$message_text",    "body_template": {    "webhook_url": "http://127.0.0.1:12344/log/opena1",  "action": {  "trigger": {"keywords": ["ask", "tell", "question"]},  "type": "webhook",  "name": "AI Processing",  "bot_key": "browser_opena6_bot",{            <div class="code-block">            <h4 style="color: #e0e0e0; margin-bottom: 10px; margin-top: 15px;">Example 2: Forward to AI Service</h4>                        </div>}  "enabled": true  "action": {"response": "👋 Welcome! Our team will help you shortly."},  "trigger": {"keywords": ["hello", "hi", "support"]},  "type": "auto_reply",  "name": "Support Greeting",  "bot_key": "browser_opena6_bot",{            <div class="code-block">            <h4 style="color: #e0e0e0; margin-bottom: 10px;">Example 1: Customer Support Auto-Reply</h4>                        </div>                Copy & modify these examples to create your own workflows!            <div class="alert info">                        <div class="modal-header">💡 Workflow Examples</div>            <button class="close-btn" onclick="closeModal('examplesModal')">&times;</button>        <div class="modal-content">    <div id="examplesModal" class="modal">    <!-- Examples Modal -->        </div>        </div>            </form>                </div>                    <button type="submit" class="btn btn-primary">Create</button>                    <button type="button" class="btn btn-secondary" onclick="closeModal('workflowModal')">Cancel</button>                <div class="modal-footer">                                </div>                    </label>                        <span style="color: #e0e0e0; font-size: 14px;">Enable workflow</span>                        <input type="checkbox" id="workflow-enabled" checked>                    <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">                <div class="form-group">                                </div>                    <textarea class="form-input" id="action-response" placeholder="👋 Hello! How can I help?" style="min-height: 80px;"></textarea>                    <label class="form-label">Response Message</label>                <div class="form-group" id="action-field">                                </div>                    <input type="text" class="form-input" id="trigger-keywords" placeholder="hello, hi, hey (comma-separated)">                    <label class="form-label">Trigger Keywords</label>                <div class="form-group">                                </div>                    </select>                        <option value="scheduled">Scheduled</option>                        <option value="webhook">Webhook</option>                        <option value="forward">Forward</option>                        <option value="auto_reply">Auto-Reply</option>                    <select class="form-input" id="workflow-type" onchange="updateFields()" required>                    <label class="form-label">Workflow Type</label>                <div class="form-group">                                </div>                    <input type="text" class="form-input" id="workflow-name" placeholder="e.g., Auto-Reply Greeting" required>                    <label class="form-label">Workflow Name</label>                <div class="form-group">                                </div>                    </select>                        <option value="open2tele_bot">open2tele_bot</option>                        <option value="browser_opena6_bot">browser_opena6_bot</option>                        <option value="">-- Select Bot --</option>                    <select class="form-input" id="bot-select" required>                    <label class="form-label">Bot Selection</label>                <div class="form-group">            <form onsubmit="handleCreateWorkflow(event)">                        <div class="modal-header">✨ Create Workflow</div>            <button class="close-btn" onclick="closeModal('workflowModal')">&times;</button>        <div class="modal-content">    <div id="workflowModal" class="modal">    <!-- Create Workflow Modal -->        </div>        </div>            </div>                </div>                    <button class="btn btn-secondary" onclick="showExamples()">View Examples</button>                    <p>Ready-to-use workflow examples and code snippets</p>                    <h3>💻 Examples</h3>                <div class="card">                </div>                    <button class="btn btn-secondary" onclick="window.open('http://127.0.0.1:12346/docs', '_blank')">View API</button>                    <p>Swagger UI and REST API documentation</p>                    <h3>🔌 API Reference</h3>                <div class="card">                </div>                    <button class="btn btn-secondary" onclick="window.open('../opena4_telegram.md', '_blank')">Read Docs</button>                    <p>Complete documentation on workflows, APIs, and configuration</p>                    <h3>📖 Full Guide</h3>                <div class="card">            <div class="grid">            <div class="section-title">📚 Documentation</div>        <div class="section">        <!-- Documentation -->                </div>            </div>                </div>                    <p>No workflows configured. Create one to get started!</p>                <div style="text-align: center; color: #888; padding: 20px;">            <div class="workflow-list" id="workflows-list">            <div class="section-title">⚙️ Active Workflows</div>        <div class="section">        <!-- Active Workflows -->                </div>            </div>                </div>                    <button class="btn btn-secondary" onclick="createWorkflow('scheduled')">Use Template</button>                    <p>Send messages at specific times or intervals</p>                    <h3>Scheduled Task</h3>                <div class="card">                </div>                    <button class="btn btn-secondary" onclick="createWorkflow('webhook')">Use Template</button>                    <p>Send messages to external services (opena1, APIs)</p>                    <h3>Webhook Trigger</h3>                <div class="card">                </div>                    <button class="btn btn-secondary" onclick="createWorkflow('forward')">Use Template</button>                    <p>Forward messages to another chat or group</p>                    <h3>Forward Messages</h3>                <div class="card">                </div>                    <button class="btn btn-secondary" onclick="createWorkflow('auto_reply')">Use Template</button>                    <p>Automatically respond to messages containing specific keywords</p>                    <h3>Auto-Reply</h3>                <div class="card">            <div class="grid">            <div class="section-title">🎨 Workflow Templates</div>        <div class="section">        <!-- Workflow Templates -->                </div>            </div>                <button class="btn btn-secondary" onclick="viewAnalytics()">View Analytics</button>                <p>View metrics and activity for all workflows</p>                <h3>📊 Analytics</h3>            <div class="card">                        </div>                <button class="btn btn-primary" onclick="viewBots()">Manage Bots</button>                <p>Manage registered Telegram bots and their configurations</p>                <h3>🤖 Bots</h3>            <div class="card">                        </div>                <button class="btn btn-secondary" onclick="listWorkflows()">View All</button>                <button class="btn btn-primary" onclick="openModal('workflowModal')">Create Workflow</button>                <p>Create and manage bot workflows for automatic message handling</p>                <h3>📋 Workflows</h3>            <div class="card">        <div class="grid">        <!-- Quick Actions -->                </div>            </div>                </div>                    <div class="stat-value" style="font-size: 24px;">✅</div>                    <div class="stat-label">API Status</div>                <div class="stat-card">                </div>                    <div class="stat-value" id="messages-today">0</div>                    <div class="stat-label">Messages Today</div>                <div class="stat-card">                </div>                    <div class="stat-value" id="total-workflows">0</div>                    <div class="stat-label">Total Workflows</div>                <div class="stat-card">                </div>                    <div class="stat-value" id="active-bots">2</div>                    <div class="stat-label">Active Bots</div>                <div class="stat-card">            <div class="stats-grid">            <div class="section-title">📊 Overview</div>        <div class="section">        <!-- Statistics -->                </div>            <p>Multi-Bot Orchestration & Workflow Management (Port 12346)</p>            <h1>🚀 opena4 – Telegram Workflows</h1>        <div class="header">    <div class="container"><body></head>    </style>        }            }                font-size: 24px;            .header h1 {        @media (max-width: 768px) {                }            color: #8b5cf6;            font-weight: 700;            font-size: 28px;        .stat-value {                }            text-transform: uppercase;            margin-bottom: 8px;            color: #888;            font-size: 12px;        .stat-label {                }            text-align: center;            padding: 15px;            border-radius: 8px;            border: 1px solid #404050;            background: #262635;        .stat-card {                }            margin-bottom: 20px;            gap: 15px;            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));            display: grid;        .stats-grid {                }            margin: 10px 0;            overflow-x: auto;            color: #8b5cf6;            font-size: 12px;            font-family: monospace;            padding: 12px;            border-radius: 6px;            border: 1px solid #404050;            background: #1a1a25;        .code-block {                }            border-left: 4px solid #4ade80;            color: #4ade80;            background: #1a3a1a;        .alert.success {                }            border-left: 4px solid #60a5fa;            color: #60a5fa;            background: #1e3a5f;        .alert.info {                }            font-size: 14px;            margin-bottom: 15px;            border-radius: 6px;            padding: 12px 16px;        .alert {                }            border-top: 1px solid #404050;            padding-top: 15px;            margin-top: 20px;            justify-content: flex-end;            gap: 10px;            display: flex;        .modal-footer {                }            box-shadow: 0 0 10px rgba(139, 92, 246, 0.2);            border-color: #8b5cf6;            outline: none;        .form-input:focus {                }            font-size: 14px;            color: #e0e0e0;            border-radius: 6px;            border: 1px solid #404050;            background: #1a1a25;            padding: 10px 12px;            width: 100%;        .form-input {                }            text-transform: uppercase;            color: #e0e0e0;            margin-bottom: 6px;            font-weight: 600;            font-size: 12px;            display: block;        .form-label {                }            margin-bottom: 15px;        .form-group {                }            color: #e0e0e0;        .close-btn:hover {                }            color: #888;            border: none;            background: none;            cursor: pointer;            font-size: 28px;            right: 20px;            top: 20px;            position: absolute;        .close-btn {                }            color: #e0e0e0;            margin-bottom: 20px;            font-weight: 700;            font-size: 22px;        .modal-header {                }            overflow-y: auto;            max-height: 80vh;            width: 90%;            max-width: 600px;            padding: 30px;            border-radius: 12px;            border: 1px solid #404050;            background: #262635;        .modal-content {                }            justify-content: center;            align-items: center;            display: flex;        .modal.active {                }            backdrop-filter: blur(4px);            background-color: rgba(0, 0, 0, 0.7);            height: 100%;            width: 100%;            top: 0;            left: 0;            z-index: 1000;            position: fixed;            display: none;        .modal {                }            border-color: #ef4444;            color: #ef4444;            background: rgba(239, 68, 68, 0.1);        .badge.disabled {                }            border-color: #10b981;            color: #10b981;            background: rgba(16, 185, 129, 0.1);        .badge.enabled {                }            margin-right: 8px;            border: 1px solid #8b5cf6;            color: #8b5cf6;            background: #1a1a25;            font-weight: 600;            font-size: 12px;            border-radius: 20px;            padding: 4px 12px;            display: inline-block;        .badge {                }            font-size: 12px;            color: #888;        .workflow-info p {                }            color: #e0e0e0;            margin-bottom: 5px;        .workflow-info h4 {                }            align-items: center;            justify-content: space-between;            display: flex;            padding: 15px;            border-radius: 8px;            border-left: 4px solid #8b5cf6;            background: #262635;        .workflow-item {                }            gap: 12px;            flex-direction: column;            display: flex;        .workflow-list {                }            border-bottom: 2px solid #404050;            padding-bottom: 10px;            margin-bottom: 15px;            font-weight: 700;            font-size: 20px;        .section-title {                }            margin-bottom: 30px;        .section {                }            color: #e0e0e0;            background: #404050;        .btn-secondary {                }            box-shadow: 0 10px 20px rgba(139, 92, 246, 0.3);            transform: translateY(-2px);        .btn-primary:hover {                }            color: white;            background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);        .btn-primary {                }            transition: all 0.3s ease;            font-size: 14px;            font-weight: 600;            cursor: pointer;            border-radius: 6px;            border: none;            padding: 10px 16px;        .btn {                }            margin-bottom: 15px;            font-size: 14px;            color: #888;        .card p {                }            font-size: 16px;            color: #e0e0e0;            margin-bottom: 10px;        .card h3 {                }            box-shadow: 0 0 20px rgba(139, 92, 246, 0.1);            border-color: #8b5cf6;        .card:hover {                }            transition: all 0.3s ease;            padding: 20px;            border-radius: 12px;            border: 1px solid #404050;            background: #262635;        .card {                }            margin-bottom: 30px;            gap: 20px;            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));            display: grid;        .grid {                }            font-size: 14px;            color: #999;        .header p {                }            margin-bottom: 5px;            font-size: 32px;        .header h1 {                }            margin-bottom: 30px;            background-clip: text;            -webkit-text-fill-color: transparent;            -webkit-background-clip: text;            background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);        .header {                }            margin: 0 auto;            max-width: 1400px;        .container {                }            padding: 20px;            min-height: 100vh;            color: #e0e0e0;            background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;        body {                }            box-sizing: border-box;            padding: 0;            margin: 0;        * {    <style>    <title>opena4 – Telegram Workflows</title>    <meta name="viewport" content="width=device-width, initial-scale=1.0">    <meta charset="UTF-8"><head>## Core Services

### Telegram Multi-Bot (opena4)

- 📖 **[Comprehensive Guide](./opena4_telegram.md)** - Architecture, workflows, API, troubleshooting
- � **[Production Deployment](./DEPLOYMENT_OPENA4.md)** - Nginx proxy, SSL, webhooks, monitoring
  - External URL: **https://hyperdashboard-one.de/opena4**
- 🤖 **[Workflows Reference](./opena4_telegram.md#workflows)** - Auto-reply, forward, webhook, scheduled workflows
- 📖 **[Operations Guide](../telegram_multi/OPERATIONS_TELEGRAM.md)** - Docker setup, health checks, logging
- 🔧 **[Quick Start](../bin/quickstart_telegram_bots.sh)** - Automated setup script
- 📝 **[Registration Script](../scripts/register_bots.sh)** - Bot registration & webhook setup

### OpenWebUI Integration

- 📖 **[OpenWebUI API Documentation](./OPENWEBUI_API.md)**
- 🐛 **[Troubleshooting Guide](./TROUBLESHOOTING.md)**
- 📋 **[Integration Backlog](./OPENWEBUI_TODO.md)**

## Observability & Monitoring

### OpenTelemetry Tracing

- 🔍 **[Tracing Guide](./TRACING_GUIDE.md)** - Complete tracing setup with Grafana & Tempo
  - Quick start collector
  - Trace querying
  - Troubleshooting
  - Performance impact analysis
- ✅ **[Check Tracing](../tracing/check_tracing.py)** - Verification script
- 🚀 **[Start Collector](../bin/start_tracing_collector.sh)** - Launch OTLP collector
- 🐘 **[Collector Config](../docker-compose.otel.yml)** - Docker-Compose OTLP stack

## Infrastructure & Operations

### General Operations

- 🔄 **[Operations Guide](./OPERATIONS.md)** - Service ports, common errors, tracing basics
- 🛠️ **[Makefile Targets](../Makefile)** - Build, deploy, scan tasks

### Project Structure

- 📁 **[Complete Project Overview](../COMPLETE_PROJECT_OVERVIEW.md)** - Full architecture
- 📊 **[System Documentation](../PORTIER_SYSTEM_DOCS.md)** - PORTIER system details

## User Interfaces

### 🌐 Web Dashboards

- **[Dashboard UI](../19.dashboard_agent/ui_dashboard.html)** - Main system overview & monitoring
  - Service status & health checks
  - Telegram bot overview
  - OpenTelemetry tracing integration
  - Quick actions & settings

- **[Telegram Bot Manager](../telegram_multi/ui_telegram_bots.html)** - Bot-specific management
  - Add/edit/delete bots
  - Bot statistics & activity
  - Webhook configuration
  - Active/inactive status tracking

- **[opena4 Workflows Dashboard](../telegram_multi/ui_opena4_workflows.html)** - Workflow management
  - Create & manage workflows (auto-reply, forward, webhook, scheduled)
  - Workflow templates & examples
  - Bot coordination
  - Analytics & monitoring

## Quick Commands

### Access Web UIs

```bash
# Dashboard (after starting services)
open file:///$(pwd)/19.dashboard_agent/ui_dashboard.html

# Telegram Bot Manager
open file:///$(pwd)/telegram_multi/ui_telegram_bots.html
```

### Start Everything

```bash
# Services
cd telegram_multi && docker-compose up -d

# Tracing (optional)
./bin/start_tracing_collector.sh

# Register bots
bash scripts/register_bots.sh http://127.0.0.1:8000

# Verify
curl http://127.0.0.1:8000/health | jq .
```

### Monitoring

```bash
# Health check
./bin/quickstart_telegram_bots.sh

# View logs
cd telegram_multi && docker-compose logs -f

# Tracing verification
python3 tracing/check_tracing.py

# Access Grafana (if OTEL running)
# http://localhost:3000
```

### Troubleshooting

```bash
# Check service status
docker-compose ps

# Inspect database
docker-compose exec postgres psql -U telegram_user -d telegram_multi_db

# Monitor Redis
docker-compose exec redis redis-cli
```

## By Use Case

### 🤖 "I want to add a new Telegram bot"

1. Get bot token from [@BotFather](https://t.me/BotFather)
2. Add to `.env` → `BOT_TOKENS_MAPPING`
3. Run: `bash scripts/register_bots.sh https://api.your-domain.com`
4. See: [Registration Script](../scripts/register_bots.sh)

### 🔍 "I want to debug request flows"

1. Enable tracing: `OTEL_ENABLED=true` in `.env`
2. Start collector: `./bin/start_tracing_collector.sh`
3. Access Grafana: `http://localhost:3000`
4. See: [Tracing Guide](./TRACING_GUIDE.md)

### 🚀 "I want to deploy to production"

1. Prepare environment: Read [Operations Guide](./OPERATIONS.md)
2. Use real bot tokens (not test)
3. Set up domain + SSL certificate
4. Configure OpenTelemetry (optional)
5. Deploy containers
6. Register bots: `bash scripts/register_bots.sh https://api.your-domain.com`

### 🐛 "Services won't start"

1. Check logs: `docker-compose logs -f`
2. See: [Troubleshooting Guide](./TROUBLESHOOTING.md)
3. Common: Port in use, missing packages, invalid tokens

### 📊 "I want monitoring & observability"

1. **Option A (Development):** Use local tracing → [Tracing Guide](./TRACING_GUIDE.md)
2. **Option B (Production):** Set up Prometheus + Grafana (future)
3. **Option C (Quick):** Use health endpoints + log monitoring

## File Locations

| File                                      | Purpose                       | Type         |
| ----------------------------------------- | ----------------------------- | ------------ |
| `docs/OPERATIONS.md`                      | General operations            | 📖 Reference |
| `docs/TRACING_GUIDE.md`                   | OpenTelemetry setup           | 📖 Guide     |
| `telegram_multi/OPERATIONS_TELEGRAM.md`   | Telegram-specific             | 📖 Reference |
| `docs/TROUBLESHOOTING.md`                 | Error solutions               | 🔧 Reference |
| `bin/start_tracing_collector.sh`          | Start OTLP                    | 🚀 Script    |
| `bin/quickstart_telegram_bots.sh`         | Quick setup                   | 🚀 Script    |
| `scripts/register_bots.sh`                | Bot registration              | 🚀 Script    |
| `telegram_multi/ui_opena4_workflows.html` | Workflow management UI        | 🎨 Web UI    |
| `docs/opena4_telegram.md`                 | Complete opena4 documentation | 📖 Reference |
| `docker-compose.otel.yml`                 | OTLP stack                    | ⚙️ Config    |
| `tracing/check_tracing.py`                | Verify tracing                | ✅ Test      |

## Version & Status

- **Version:** 1.0.0
- **Status:** ✅ Production Ready
- **Last Updated:** 2025-12-17
- **Components:**
  - ✅ Telegram Multi-Bot API
  - ✅ OpenTelemetry Tracing
  - ✅ Docker containerization
  - ✅ PostgreSQL + Redis
  - ✅ Health & monitoring
  - ⚠️ OpenWebUI integration (optional)

## Support

For issues, check:

1. Service logs: `docker-compose logs -f {service}`
2. [Troubleshooting Guide](./TROUBLESHOOTING.md)
3. [Tracing Guide](./TRACING_GUIDE.md) for debugging
4. Health endpoints: `curl http://127.0.0.1:8000/health`

---

**📚 Documentation Hub**
Start here for any ELION Hyper-Dashboard task!
