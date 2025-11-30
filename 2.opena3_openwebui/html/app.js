/**
 * OPENA3 - OpenWebUI Terminal Agent | Application Logic
 * PAS-6.0 Enterprise Dashboard
 * Port: 12347 | 12 Capabilities
 */

class OpenWebUIDashboard {
    constructor() {
        this.config = CONFIG;
        this.currentSection = 'overview';
        this.isOnline = false;
        this.chatHistory = [];
        this.currentModel = CONFIG.settings.defaultModel;
        this.sseConnection = null;
        this.logs = [];
        this.init();
    }

    init() {
        this.setupNavigation();
        this.loadToken();
        this.checkHealth();
        this.loadOverviewData();
        this.startHealthMonitor();
        console.log('🌐 OpenWebUI Dashboard initialized');
    }

    // ==================== NAVIGATION ====================
    setupNavigation() {
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const section = e.target.dataset.section;
                this.showSection(section);
            });
        });
    }

    showSection(sectionId) {
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        
        const section = document.getElementById(sectionId);
        const btn = document.querySelector(`[data-section="${sectionId}"]`);
        
        if (section) section.classList.add('active');
        if (btn) btn.classList.add('active');
        
        this.currentSection = sectionId;
        this.onSectionChange(sectionId);
    }

    onSectionChange(section) {
        switch(section) {
            case 'chat': this.initChat(); break;
            case 'models': this.loadModels(); break;
            case 'history': this.loadHistory(); break;
            case 'tools': this.loadTools(); break;
            case 'files': this.loadFiles(); break;
            case 'stream': this.initSSE(); break;
            case 'logs': this.loadLogs(); break;
        }
    }

    // ==================== API CALLS ====================
    async apiCall(endpoint, method = 'GET', data = null) {
        const url = `${this.config.api.baseUrl}${endpoint}`;
        const token = this.getToken();
        
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        };
        
        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(url, options);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`API Error: ${endpoint}`, error);
            throw error;
        }
    }

    // ==================== HEALTH CHECK ====================
    async checkHealth() {
        try {
            const data = await this.apiCall('/health');
            this.setOnlineStatus(true, data);
            return data;
        } catch (error) {
            this.setOnlineStatus(false);
            return null;
        }
    }

    setOnlineStatus(online, data = null) {
        this.isOnline = online;
        const badge = document.getElementById('statusBadge');
        const text = document.getElementById('statusText');
        
        if (badge && text) {
            badge.className = `status-badge ${online ? 'online' : 'offline'}`;
            text.textContent = online ? 'Online' : 'Offline';
        }
        
        if (online && data) {
            this.updateLastUpdate();
        }
    }

    startHealthMonitor() {
        setInterval(() => this.checkHealth(), this.config.settings.refreshInterval);
    }

    // ==================== OVERVIEW ====================
    async loadOverviewData() {
        try {
            // Load metrics
            const health = await this.checkHealth();
            const status = await this.apiCall('/status').catch(() => ({}));
            
            // Update metrics
            this.updateMetric('metricChats', status.active_chats || 0);
            this.updateMetric('metricResponses', status.total_responses || 0);
            this.updateMetric('metricModels', status.available_models || this.config.models.length);
            this.updateMetric('metricTools', status.registered_tools || 0);
            this.updateMetric('metricFiles', status.uploaded_files || 0);
            this.updateMetric('metricUptime', this.formatUptime(status.uptime_seconds || 0));
            
            // Load capabilities
            this.renderCapabilities();
            
        } catch (error) {
            console.error('Failed to load overview:', error);
        }
    }

    updateMetric(id, value) {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    }

    formatUptime(seconds) {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        return `${h}h ${m}m`;
    }

    renderCapabilities() {
        const container = document.getElementById('capabilitiesGrid');
        if (!container) return;
        
        container.innerHTML = this.config.capabilities.map(cap => `
            <div class="capability-card" onclick="dashboard.testCapability('${cap.id}')">
                <span class="capability-icon">${cap.icon}</span>
                <div class="capability-info">
                    <h4>${cap.name}</h4>
                    <p>${cap.description}</p>
                </div>
            </div>
        `).join('');
    }

    async testCapability(capId) {
        const cap = this.config.capabilities.find(c => c.id === capId);
        if (!cap) return;
        
        this.showToast(`Testing ${cap.name}...`, 'info');
        
        try {
            const result = await this.apiCall(cap.endpoint);
            this.showModal(`${cap.icon} ${cap.name}`, JSON.stringify(result, null, 2));
            this.showToast(`${cap.name} working!`, 'success');
        } catch (error) {
            this.showToast(`${cap.name} failed: ${error.message}`, 'error');
        }
    }

    // ==================== CHAT ====================
    initChat() {
        this.renderModelSelector();
        this.loadChatHistory();
    }

    renderModelSelector() {
        const selector = document.getElementById('modelSelector');
        if (!selector) return;
        
        selector.innerHTML = this.config.models.map(m => 
            `<option value="${m.id}" ${m.id === this.currentModel ? 'selected' : ''}>${m.name} (${m.provider})</option>`
        ).join('');
        
        selector.onchange = (e) => {
            this.currentModel = e.target.value;
            this.showToast(`Model changed to ${e.target.value}`, 'info');
        };
    }

    async sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input?.value?.trim();
        
        if (!message) return;
        
        // Add user message
        this.addChatMessage('user', message);
        input.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await this.apiCall('/api/chat', 'POST', {
                model: this.currentModel,
                messages: [{ role: 'user', content: message }],
                stream: false
            });
            
            this.hideTypingIndicator();
            this.addChatMessage('assistant', response.choices?.[0]?.message?.content || response.response || 'No response');
            
        } catch (error) {
            this.hideTypingIndicator();
            this.addChatMessage('assistant', `Error: ${error.message}`, true);
        }
    }

    addChatMessage(role, content, isError = false) {
        const container = document.getElementById('chatMessages');
        if (!container) return;
        
        const msg = document.createElement('div');
        msg.className = `message ${role} ${isError ? 'error' : ''}`;
        msg.innerHTML = `
            <div class="message-header">
                <span>${role === 'user' ? '👤 You' : '🤖 AI'}</span>
                <span>${new Date().toLocaleTimeString()}</span>
            </div>
            <div class="message-content">${this.escapeHtml(content)}</div>
        `;
        
        container.appendChild(msg);
        container.scrollTop = container.scrollHeight;
        
        this.chatHistory.push({ role, content, timestamp: new Date().toISOString() });
    }

    showTypingIndicator() {
        const container = document.getElementById('chatMessages');
        if (!container) return;
        
        const indicator = document.createElement('div');
        indicator.id = 'typingIndicator';
        indicator.className = 'message assistant typing';
        indicator.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
        container.appendChild(indicator);
        container.scrollTop = container.scrollHeight;
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) indicator.remove();
    }

    clearChat() {
        const container = document.getElementById('chatMessages');
        if (container) container.innerHTML = '';
        this.chatHistory = [];
        this.showToast('Chat cleared', 'info');
    }

    // ==================== MODELS ====================
    async loadModels() {
        const container = document.getElementById('modelsGrid');
        if (!container) return;
        
        try {
            const data = await this.apiCall('/api/models').catch(() => ({ models: this.config.models }));
            const models = data.models || this.config.models;
            
            container.innerHTML = models.map(m => `
                <div class="tool-card">
                    <div class="tool-header">
                        <span class="tool-icon">🤖</span>
                        <span class="tool-name">${m.name || m.id}</span>
                    </div>
                    <div class="tool-desc">${m.provider || 'Unknown'}</div>
                    <button class="btn btn-sm btn-primary" onclick="dashboard.selectModel('${m.id}')">Select</button>
                </div>
            `).join('');
        } catch (error) {
            container.innerHTML = '<p>Failed to load models</p>';
        }
    }

    selectModel(modelId) {
        this.currentModel = modelId;
        this.showToast(`Model selected: ${modelId}`, 'success');
    }

    // ==================== HISTORY ====================
    async loadHistory() {
        const container = document.getElementById('historyList');
        if (!container) return;
        
        try {
            const data = await this.apiCall('/api/chat/history').catch(() => ({ conversations: [] }));
            const conversations = data.conversations || [];
            
            if (conversations.length === 0) {
                container.innerHTML = '<p class="text-muted">No conversation history</p>';
                return;
            }
            
            container.innerHTML = conversations.map((c, i) => `
                <div class="history-item" onclick="dashboard.loadConversation('${c.id || i}')">
                    <div>
                        <div class="history-title">${c.title || `Conversation ${i + 1}`}</div>
                        <div class="history-meta">${c.messages?.length || 0} messages</div>
                    </div>
                    <span class="history-meta">${new Date(c.created_at || Date.now()).toLocaleDateString()}</span>
                </div>
            `).join('');
        } catch (error) {
            container.innerHTML = '<p>Failed to load history</p>';
        }
    }

    async loadConversation(convId) {
        this.showToast(`Loading conversation ${convId}...`, 'info');
        // Implementation would load specific conversation
    }

    // ==================== TOOLS ====================
    async loadTools() {
        const container = document.getElementById('toolsGrid');
        if (!container) return;
        
        try {
            const data = await this.apiCall('/api/tools').catch(() => ({ tools: [] }));
            const tools = data.tools || [];
            
            // Add default tools if none
            const allTools = tools.length > 0 ? tools : [
                { id: 'search', name: 'Web Search', icon: '🔍', description: 'Search the web' },
                { id: 'code', name: 'Code Interpreter', icon: '💻', description: 'Run Python code' },
                { id: 'image', name: 'Image Generation', icon: '🎨', description: 'Generate images' },
                { id: 'analysis', name: 'Data Analysis', icon: '📊', description: 'Analyze data' }
            ];
            
            container.innerHTML = allTools.map(t => `
                <div class="tool-card">
                    <div class="tool-header">
                        <span class="tool-icon">${t.icon || '🔧'}</span>
                        <span class="tool-name">${t.name}</span>
                    </div>
                    <div class="tool-desc">${t.description}</div>
                    <div style="margin-top: 1rem;">
                        <button class="btn btn-sm btn-secondary" onclick="dashboard.testTool('${t.id}')">Test</button>
                        <button class="btn btn-sm btn-primary" onclick="dashboard.configureTool('${t.id}')">Configure</button>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            container.innerHTML = '<p>Failed to load tools</p>';
        }
    }

    async testTool(toolId) {
        this.showToast(`Testing tool: ${toolId}`, 'info');
        try {
            const result = await this.apiCall(`/api/tools/${toolId}/test`, 'POST');
            this.showModal('Tool Test Result', JSON.stringify(result, null, 2));
        } catch (error) {
            this.showToast(`Tool test failed: ${error.message}`, 'error');
        }
    }

    configureTool(toolId) {
        this.showToast(`Configure tool: ${toolId}`, 'info');
    }

    // ==================== FILES ====================
    async loadFiles() {
        const container = document.getElementById('filesList');
        if (!container) return;
        
        try {
            const data = await this.apiCall('/api/files').catch(() => ({ files: [] }));
            const files = data.files || [];
            
            if (files.length === 0) {
                container.innerHTML = '<p class="text-muted">No files uploaded</p>';
                return;
            }
            
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Size</th>
                            <th>Uploaded</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${files.map(f => `
                            <tr>
                                <td>${f.name}</td>
                                <td>${f.type || 'Unknown'}</td>
                                <td>${this.formatBytes(f.size || 0)}</td>
                                <td>${new Date(f.uploaded_at || Date.now()).toLocaleDateString()}</td>
                                <td>
                                    <button class="btn btn-sm" onclick="dashboard.viewFile('${f.id}')">👁️</button>
                                    <button class="btn btn-sm btn-danger" onclick="dashboard.deleteFile('${f.id}')">🗑️</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } catch (error) {
            container.innerHTML = '<p>Failed to load files</p>';
        }
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async uploadFile() {
        const input = document.getElementById('fileUpload');
        if (!input?.files?.length) {
            this.showToast('Please select a file', 'warning');
            return;
        }
        
        const file = input.files[0];
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch(`${this.config.api.baseUrl}/api/files/upload`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${this.getToken()}` },
                body: formData
            });
            
            if (!response.ok) throw new Error('Upload failed');
            
            this.showToast('File uploaded successfully', 'success');
            this.loadFiles();
        } catch (error) {
            this.showToast(`Upload failed: ${error.message}`, 'error');
        }
    }

    // ==================== SSE STREAM ====================
    initSSE() {
        if (this.sseConnection) {
            this.sseConnection.close();
        }
        
        const container = document.getElementById('sseOutput');
        if (!container) return;
        
        container.innerHTML = '<div class="stream-event">Connecting to SSE...</div>';
        
        try {
            const token = this.getToken();
            this.sseConnection = new EventSource(`${this.config.api.baseUrl}/sse/events?token=${token}`);
            
            this.sseConnection.onopen = () => {
                this.addSSEEvent('Connected to SSE stream', 'success');
            };
            
            this.sseConnection.onmessage = (event) => {
                this.addSSEEvent(event.data);
            };
            
            this.sseConnection.onerror = () => {
                this.addSSEEvent('SSE connection error', 'error');
            };
        } catch (error) {
            this.addSSEEvent(`SSE failed: ${error.message}`, 'error');
        }
    }

    addSSEEvent(message, type = 'info') {
        const container = document.getElementById('sseOutput');
        if (!container) return;
        
        const event = document.createElement('div');
        event.className = `stream-event ${type}`;
        event.innerHTML = `<span class="log-time">${new Date().toLocaleTimeString()}</span> ${message}`;
        container.appendChild(event);
        container.scrollTop = container.scrollHeight;
    }

    disconnectSSE() {
        if (this.sseConnection) {
            this.sseConnection.close();
            this.sseConnection = null;
            this.addSSEEvent('Disconnected from SSE', 'warning');
        }
    }

    // ==================== OPTION-2 FLOW ====================
    async testOption2Flow() {
        const targetSelect = document.getElementById('o2Target');
        const actionInput = document.getElementById('o2Action');
        const paramsInput = document.getElementById('o2Params');
        
        const target = targetSelect?.value || 'kordp';
        const action = actionInput?.value || 'health_check';
        let params = {};
        
        try {
            params = JSON.parse(paramsInput?.value || '{}');
        } catch (e) {
            this.showToast('Invalid JSON parameters', 'error');
            return;
        }
        
        this.showToast('Testing Option-2-Flow...', 'info');
        
        try {
            const result = await this.apiCall('/api/option2_flow', 'POST', {
                target,
                action,
                params
            });
            
            this.showModal('Option-2-Flow Result', JSON.stringify(result, null, 2));
            this.showToast('Option-2-Flow successful!', 'success');
        } catch (error) {
            this.showToast(`Option-2-Flow failed: ${error.message}`, 'error');
        }
    }

    // ==================== LOGS ====================
    async loadLogs() {
        const container = document.getElementById('logOutput');
        if (!container) return;
        
        try {
            const data = await this.apiCall('/logs').catch(() => ({ entries: [] }));
            const entries = data.entries || [];
            
            if (entries.length === 0) {
                container.innerHTML = '<div class="log-entry info"><span class="log-time">--:--:--</span> No logs available</div>';
                return;
            }
            
            container.innerHTML = entries.slice(-100).map(log => `
                <div class="log-entry ${log.level || 'info'}">
                    <span class="log-time">${new Date(log.timestamp || Date.now()).toLocaleTimeString()}</span>
                    <span class="log-level">[${(log.level || 'INFO').toUpperCase()}]</span>
                    ${log.message}
                </div>
            `).join('');
            
            container.scrollTop = container.scrollHeight;
        } catch (error) {
            container.innerHTML = '<div class="log-entry error">Failed to load logs</div>';
        }
    }

    clearLogs() {
        const container = document.getElementById('logOutput');
        if (container) container.innerHTML = '';
        this.showToast('Logs cleared', 'info');
    }

    // ==================== COMMANDS ====================
    async executeCommand() {
        const actionSelect = document.getElementById('cmdAction');
        const paramsInput = document.getElementById('cmdParams');
        
        const action = actionSelect?.value;
        let params = {};
        
        try {
            params = JSON.parse(paramsInput?.value || '{}');
        } catch (e) {
            this.showToast('Invalid JSON parameters', 'error');
            return;
        }
        
        try {
            const result = await this.apiCall('/command', 'POST', { action, params });
            this.showModal('Command Result', JSON.stringify(result, null, 2));
            this.showToast('Command executed', 'success');
        } catch (error) {
            this.showToast(`Command failed: ${error.message}`, 'error');
        }
    }

    // ==================== SETTINGS ====================
    loadToken() {
        const saved = localStorage.getItem(this.config.auth.tokenKey);
        if (saved) {
            const input = document.getElementById('bearerToken');
            if (input) input.value = saved;
        }
    }

    getToken() {
        const input = document.getElementById('bearerToken');
        return input?.value || localStorage.getItem(this.config.auth.tokenKey) || '';
    }

    saveSettings() {
        const token = document.getElementById('bearerToken')?.value;
        if (token) {
            localStorage.setItem(this.config.auth.tokenKey, token);
        }
        
        const baseUrl = document.getElementById('apiBaseUrl')?.value;
        if (baseUrl) {
            this.config.api.baseUrl = baseUrl;
        }
        
        this.showToast('Settings saved', 'success');
        this.checkHealth();
    }

    // ==================== UI HELPERS ====================
    showModal(title, content) {
        const modal = document.getElementById('responseModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalContent = document.getElementById('modalContent');
        
        if (modal && modalTitle && modalContent) {
            modalTitle.textContent = title;
            modalContent.textContent = content;
            modal.classList.add('active');
        }
    }

    closeModal() {
        const modal = document.getElementById('responseModal');
        if (modal) modal.classList.remove('active');
    }

    copyResponse() {
        const content = document.getElementById('modalContent')?.textContent;
        if (content) {
            navigator.clipboard.writeText(content);
            this.showToast('Copied to clipboard', 'success');
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `<span>${this.getToastIcon(type)}</span> ${message}`;
        container.appendChild(toast);
        
        setTimeout(() => toast.remove(), 3000);
    }

    getToastIcon(type) {
        const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
        return icons[type] || icons.info;
    }

    updateLastUpdate() {
        const el = document.getElementById('lastUpdate');
        if (el) el.textContent = `Last update: ${new Date().toLocaleTimeString()}`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ==================== QUICK ACTIONS ====================
    openMainDashboard() {
        window.open(this.config.portier.dashboard, '_blank');
    }

    openOpenWebUI() {
        window.open(this.config.api.openwebui, '_blank');
    }
}

// Initialize Dashboard
const dashboard = new OpenWebUIDashboard();

// Global keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        dashboard.sendMessage();
    }
    if (e.key === 'Escape') {
        dashboard.closeModal();
    }
});
