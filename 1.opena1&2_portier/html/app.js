/* Portier Agent PAS-6.0 | Application Logic | Ports 12344/12345 */
class PortierDashboard {
    constructor(config) {
        this.config = config;
        this.state = {
            opena1Connected: false,
            opena2Connected: false,
            agents: [],
            safepoints: [],
            logs: [],
            metrics: {
                totalRequests: 0,
                safepointsCreated: 0,
                agentsActive: 0,
                lastDispatch: null
            }
        };
        this.refreshInterval = null;
    }

    async init() {
        console.log(`🔵 Portier Dashboard v${this.config.agent.version} initializing...`);
        this.bindNavigation();
        this.bindActions();
        this.bindModals();
        await this.checkAllHealth();
        this.startAutoRefresh();
        this.showSection('overview');
        console.log('✅ Dashboard ready');
    }

    bindNavigation() {
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const section = btn.dataset.section;
                if (section) this.showSection(section);
            });
        });
    }

    showSection(sectionId) {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        document.querySelector(`.nav-btn[data-section="${sectionId}"]`)?.classList.add('active');
        document.getElementById(sectionId)?.classList.add('active');
        this.loadSectionData(sectionId);
    }

    async loadSectionData(section) {
        switch(section) {
            case 'overview': await this.loadOverview(); break;
            case 'coordinator': await this.loadCoordinatorData(); break;
            case 'archivator': await this.loadArchivatorData(); break;
            case 'safepoints': await this.loadSafepoints(); break;
            case 'agents': await this.loadAgents(); break;
            case 'flow': this.renderFlowDiagram(); break;
            case 'logs': await this.loadLogs(); break;
        }
    }

    bindActions() {
        document.getElementById('refreshBtn')?.addEventListener('click', () => this.checkAllHealth());
        document.getElementById('dispatchBtn')?.addEventListener('click', () => this.showDispatchModal());
        document.getElementById('createSafepointBtn')?.addEventListener('click', () => this.showCreateSafepointModal());
        document.getElementById('testApiBtn')?.addEventListener('click', () => this.testApi());

        // Quick Actions
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                if (action && typeof this[action] === 'function') this[action]();
            });
        });

        // Capability Cards
        document.querySelectorAll('.capability-card').forEach(card => {
            card.addEventListener('click', () => {
                const capability = card.dataset.capability;
                this.executeCapability(capability);
            });
        });
    }

    bindModals() {
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => this.closeModals());
        });
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) this.closeModals();
            });
        });

        document.getElementById('sendDispatchBtn')?.addEventListener('click', () => this.sendDispatch());
        document.getElementById('createSafepointSubmitBtn')?.addEventListener('click', () => this.createSafepoint());
    }

    closeModals() {
        document.querySelectorAll('.modal').forEach(m => m.classList.remove('active'));
    }

    // ==================== API CALLS ====================
    async apiCall(baseUrl, endpoint, method = 'GET', data = null) {
        try {
            const url = `${baseUrl}${endpoint}`;
            const options = {
                method,
                headers: { 'Content-Type': 'application/json' },
                timeout: this.config.api.timeout
            };
            if (data) options.body = JSON.stringify(data);
            const response = await fetch(url, options);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            return { error: error.message };
        }
    }

    async opena1Call(endpoint, method = 'GET', data = null) {
        return this.apiCall(this.config.opena1.baseUrl, endpoint, method, data);
    }

    async opena2Call(endpoint, method = 'GET', data = null) {
        return this.apiCall(this.config.opena2.baseUrl, endpoint, method, data);
    }

    // ==================== HEALTH CHECKS ====================
    async checkAllHealth() {
        const [health1, health2] = await Promise.all([
            this.opena1Call(this.config.api.opena1.health),
            this.opena2Call(this.config.api.opena2.health)
        ]);

        this.state.opena1Connected = !health1.error && health1.status === 'ok';
        this.state.opena2Connected = !health2.error && health2.status === 'ok';
        
        this.updateConnectionStatus();
        
        if (this.state.opena1Connected && this.state.opena2Connected) {
            this.showToast('Beide Agenten verbunden', 'success');
        } else if (!this.state.opena1Connected && !this.state.opena2Connected) {
            this.showToast('Beide Agenten offline', 'error');
        }
    }

    updateConnectionStatus() {
        // opena1 Status
        const badge1 = document.getElementById('opena1Status');
        if (badge1) {
            badge1.className = `agent-status ${this.state.opena1Connected ? 'online' : 'offline'}`;
            badge1.textContent = this.state.opena1Connected ? 'Online' : 'Offline';
        }

        // opena2 Status
        const badge2 = document.getElementById('opena2Status');
        if (badge2) {
            badge2.className = `agent-status ${this.state.opena2Connected ? 'online' : 'offline'}`;
            badge2.textContent = this.state.opena2Connected ? 'Online' : 'Offline';
        }

        // Header status
        const headerBadge = document.querySelector('.status-badge');
        if (this.state.opena1Connected && this.state.opena2Connected) {
            headerBadge?.classList.add('online');
        } else {
            headerBadge?.classList.remove('online');
        }
    }

    // ==================== OVERVIEW ====================
    async loadOverview() {
        const [status1, status2, stats] = await Promise.all([
            this.opena1Call(this.config.api.opena1.status),
            this.opena2Call(this.config.api.opena2.status),
            this.opena2Call(this.config.api.opena2.stats)
        ]);

        // Update metrics
        this.updateMetric('totalRequests', status1.total_requests || 0);
        this.updateMetric('safepointsCreated', stats.total_safepoints || 0);
        this.updateMetric('agentsActive', status1.active_agents || this.config.registeredAgents.length);
        this.updateMetric('lastDispatchTime', status1.last_dispatch || 'N/A');
    }

    updateMetric(id, value) {
        const el = document.getElementById(id);
        if (el) el.textContent = typeof value === 'number' ? value.toLocaleString('de-DE') : value;
    }

    // ==================== COORDINATOR (opena1) ====================
    async loadCoordinatorData() {
        const [status, registry] = await Promise.all([
            this.opena1Call(this.config.api.opena1.status),
            this.opena1Call(this.config.api.opena1.registry)
        ]);

        if (!status.error) {
            document.getElementById('kordpUptime')?.textContent = status.uptime || 'N/A';
            document.getElementById('kordpVersion')?.textContent = status.version || '1.0.0';
            document.getElementById('kordpRequests')?.textContent = status.total_requests || 0;
        }

        if (!registry.error && registry.tools) {
            this.renderTools(registry.tools);
        }
    }

    renderTools(tools) {
        const container = document.getElementById('toolsList');
        if (!container) return;

        container.innerHTML = tools.map(tool => `
            <div class="endpoint-item">
                <span class="method post">TOOL</span>
                <code>${tool.name}</code>
                <span class="text-muted">${tool.description || ''}</span>
            </div>
        `).join('');
    }

    // ==================== ARCHIVATOR (opena2) ====================
    async loadArchivatorData() {
        const [status, stats] = await Promise.all([
            this.opena2Call(this.config.api.opena2.status),
            this.opena2Call(this.config.api.opena2.stats)
        ]);

        if (!status.error) {
            document.getElementById('archivpUptime')?.textContent = status.uptime || 'N/A';
            document.getElementById('archivpVersion')?.textContent = status.version || '1.0.0';
        }

        if (!stats.error) {
            document.getElementById('totalSafepoints')?.textContent = stats.total || 0;
            document.getElementById('cmdCount')?.textContent = stats.cmd_count || 0;
            document.getElementById('respCount')?.textContent = stats.resp_count || 0;
            document.getElementById('archiveSize')?.textContent = stats.size || 'N/A';
        }
    }

    // ==================== SAFEPOINTS ====================
    async loadSafepoints() {
        const result = await this.opena2Call(this.config.api.opena2.safepoints + '?limit=50');
        if (!result.error && result.safepoints) {
            this.state.safepoints = result.safepoints;
            this.renderSafepoints();
        }
    }

    renderSafepoints() {
        const container = document.getElementById('safepointList');
        if (!container) return;

        if (this.state.safepoints.length === 0) {
            container.innerHTML = '<div class="loading">Keine Safepoints</div>';
            return;
        }

        container.innerHTML = this.state.safepoints.map(sp => `
            <div class="safepoint-item" onclick="dashboard.viewSafepoint('${sp.id}')">
                <div>
                    <span class="safepoint-id">${sp.id}</span>
                    <span class="text-muted">${sp.src}→${sp.dst}</span>
                </div>
                <div>
                    <span class="safepoint-type ${sp.type.toLowerCase()}">${sp.type}</span>
                    <span class="text-muted">${sp.timestamp || ''}</span>
                </div>
            </div>
        `).join('');
    }

    async viewSafepoint(id) {
        const result = await this.opena2Call(`${this.config.api.opena2.safepoints}/${id}`);
        if (!result.error) {
            document.getElementById('safepointDetailContent').textContent = JSON.stringify(result, null, 2);
            document.getElementById('safepointModal')?.classList.add('active');
        }
    }

    showCreateSafepointModal() {
        document.getElementById('createSafepointModal')?.classList.add('active');
    }

    async createSafepoint() {
        const src = document.getElementById('safepointSrc')?.value;
        const dst = document.getElementById('safepointDst')?.value;
        const type = document.getElementById('safepointType')?.value;
        const payload = document.getElementById('safepointPayload')?.value;

        if (!src || !dst || !payload) {
            this.showToast('Alle Felder erforderlich', 'warning');
            return;
        }

        let payloadJson;
        try {
            payloadJson = JSON.parse(payload);
        } catch(e) {
            this.showToast('Ungültiges JSON', 'error');
            return;
        }

        const result = await this.opena2Call(this.config.api.opena2.create, 'POST', {
            src, dst, type, payload: payloadJson
        });

        if (!result.error) {
            this.showToast(`Safepoint ${result.id} erstellt`, 'success');
            this.closeModals();
            await this.loadSafepoints();
        } else {
            this.showToast('Erstellung fehlgeschlagen', 'error');
        }
    }

    // ==================== AGENTS ====================
    async loadAgents() {
        const result = await this.opena1Call(this.config.api.opena1.agents);
        if (!result.error && result.agents) {
            this.state.agents = result.agents;
        } else {
            // Use configured agents as fallback
            this.state.agents = this.config.registeredAgents;
        }
        this.renderAgents();
    }

    renderAgents() {
        const container = document.getElementById('agentsTable');
        if (!container) return;

        container.innerHTML = `
            <table class="registry-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Port</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${this.state.agents.map(agent => `
                        <tr>
                            <td>${agent.id}</td>
                            <td>${agent.name}</td>
                            <td><span class="port-badge">${agent.port}</span></td>
                            <td><span class="agent-status ${agent.status === 'online' ? 'online' : 'offline'}">${agent.status || 'Unknown'}</span></td>
                            <td>
                                <button class="btn btn-sm btn-primary" onclick="dashboard.pingAgent('${agent.id}', ${agent.port})">Ping</button>
                                <button class="btn btn-sm btn-secondary" onclick="dashboard.viewAgentDetails('${agent.id}')">Details</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    async pingAgent(agentId, port) {
        this.showToast(`Pinging ${agentId}...`, 'info');
        try {
            const response = await fetch(`http://127.0.0.1:${port}/health`);
            const data = await response.json();
            if (data.status === 'ok') {
                this.showToast(`${agentId} ist online ✅`, 'success');
            } else {
                this.showToast(`${agentId} antwortet, aber Status: ${data.status}`, 'warning');
            }
        } catch(e) {
            this.showToast(`${agentId} nicht erreichbar`, 'error');
        }
    }

    viewAgentDetails(agentId) {
        this.showToast(`Details für ${agentId}...`, 'info');
    }

    listAgents() {
        this.showSection('agents');
    }

    // ==================== DISPATCH ====================
    showDispatchModal() {
        document.getElementById('dispatchModal')?.classList.add('active');
    }

    async sendDispatch() {
        const tool = document.getElementById('dispatchTool')?.value;
        const payload = document.getElementById('dispatchPayload')?.value;

        if (!tool || !payload) {
            this.showToast('Tool und Payload erforderlich', 'warning');
            return;
        }

        let payloadJson;
        try {
            payloadJson = JSON.parse(payload);
        } catch(e) {
            this.showToast('Ungültiges JSON', 'error');
            return;
        }

        this.showToast('Dispatching...', 'info');
        const result = await this.opena1Call(this.config.api.opena1.dispatch, 'POST', {
            tool, payload: payloadJson
        });

        if (!result.error) {
            document.getElementById('dispatchResult').textContent = JSON.stringify(result, null, 2);
            this.showToast('Dispatch erfolgreich', 'success');
        } else {
            this.showToast('Dispatch fehlgeschlagen', 'error');
        }
    }

    // ==================== FLOW DIAGRAM ====================
    renderFlowDiagram() {
        const container = document.getElementById('flowDiagram');
        if (!container) return;

        const steps = this.config.option2Flow.steps;
        container.innerHTML = `
            <div class="flow-diagram">
                ${steps.map((step, i) => `
                    <div class="flow-node ${step.id === 'opena1' || step.id === 'opena2' ? 'active' : ''}" id="flowNode_${step.id}">
                        <div style="font-size: 2rem;">${step.icon}</div>
                        <div>${step.name}</div>
                    </div>
                    ${i < steps.length - 1 ? '<div class="flow-arrow">→</div>' : ''}
                `).join('')}
            </div>
            <div class="card" style="margin-top: 1rem;">
                <h3>Option-2 Flow Beschreibung</h3>
                <p>${this.config.option2Flow.description}</p>
                <h4 style="margin-top: 1rem;">Regeln:</h4>
                <ul style="margin-left: 1.5rem; color: var(--text-secondary);">
                    <li>opena1 empfängt Request von OpenAI</li>
                    <li>opena1 wählt EIN Tool, baut Envelope</li>
                    <li>opena2 archiviert (Safepoint CMD), indexiert</li>
                    <li>Tool führt Business Logic aus</li>
                    <li>Rückweg: Tool → opena2 (Safepoint RESP)</li>
                </ul>
            </div>
        `;
    }

    showFlowDiagram() {
        this.showSection('flow');
    }

    // ==================== LOGS ====================
    async loadLogs() {
        // Simulated logs - in production würde dies von einem Log-Endpoint kommen
        const logs = [
            { time: new Date().toISOString(), level: 'INFO', message: 'Dashboard initialized' },
            { time: new Date().toISOString(), level: 'INFO', message: 'opena1 health check passed' },
            { time: new Date().toISOString(), level: 'INFO', message: 'opena2 health check passed' }
        ];
        this.state.logs = logs;
        this.renderLogs();
    }

    renderLogs() {
        const container = document.getElementById('logViewer');
        if (!container) return;

        container.innerHTML = this.state.logs.map(log => `
            <div class="log-entry">
                <span class="log-time">${new Date(log.time).toLocaleTimeString('de-DE')}</span>
                <span class="log-level ${log.level.toLowerCase()}">${log.level}</span>
                <span>${log.message}</span>
            </div>
        `).join('');
    }

    showLogs() {
        this.showSection('logs');
    }

    // ==================== CAPABILITIES ====================
    executeCapability(capabilityId) {
        const capability = this.config.capabilities.find(c => c.id === capabilityId);
        if (!capability) return;

        switch(capabilityId) {
            case 'request_routing':
            case 'tool_dispatch':
            case 'load_balancing':
                this.showSection('coordinator');
                break;
            case 'agent_registry':
            case 'health_monitor':
                this.showSection('agents');
                break;
            case 'safepoint_create':
                this.showCreateSafepointModal();
                break;
            case 'safepoint_query':
            case 'index_search':
            case 'archive_stats':
            case 'data_integrity':
                this.showSection('safepoints');
                break;
            default:
                this.showToast(`${capability.name} aktiviert`, 'info');
        }
    }

    // ==================== API CONSOLE ====================
    async testApi() {
        const agent = document.getElementById('apiAgent')?.value || 'opena1';
        const endpoint = document.getElementById('apiEndpoint')?.value || '/health';
        const method = document.getElementById('apiMethod')?.value || 'GET';
        let body = null;

        if (method !== 'GET') {
            const bodyText = document.getElementById('apiBody')?.value;
            if (bodyText) {
                try {
                    body = JSON.parse(bodyText);
                } catch(e) {
                    this.showToast('Ungültiges JSON', 'error');
                    return;
                }
            }
        }

        const baseUrl = agent === 'opena1' ? this.config.opena1.baseUrl : this.config.opena2.baseUrl;
        const result = await this.apiCall(baseUrl, endpoint, method, body);
        document.getElementById('apiResponse').textContent = JSON.stringify(result, null, 2);
    }

    showSafepoints() {
        this.showSection('safepoints');
    }

    // ==================== UTILITIES ====================
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => toast.remove(), 4000);
    }

    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            this.checkAllHealth();
        }, this.config.ui.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

// Initialize on DOM ready
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new PortierDashboard(PortierConfig);
    dashboard.init();
});
