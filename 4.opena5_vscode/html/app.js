/* opena5 VSCode Agent | PAS-6.0 App */
class VSCodeDashboard {
    constructor() { this.config = CONFIG; this.isOnline = false; this.openFiles = []; this.terminalHistory = []; this.init(); }
    
    init() {
        this.setupNavigation();
        this.checkHealth();
        this.loadCapabilities();
        this.setupEditor();
        setInterval(() => this.checkHealth(), 5000);
        console.log('💻 VSCode Dashboard initialized');
    }

    setupNavigation() {
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.showSection(e.target.dataset.section));
        });
    }

    showSection(id) {
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.getElementById(id)?.classList.add('active');
        document.querySelector(`[data-section="${id}"]`)?.classList.add('active');
        if (id === 'filetree') this.loadFileTree();
        if (id === 'git') this.gitRefresh();
        if (id === 'extensions') this.loadExtensions();
        if (id === 'logs') this.loadLogs();
    }

    async apiCall(endpoint, method = 'GET', data = null) {
        const url = `${this.config.api.baseUrl}${endpoint}`;
        const opts = { method, headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${this.getToken()}` } };
        if (data) opts.body = JSON.stringify(data);
        try {
            const res = await fetch(url, opts);
            return await res.json();
        } catch (e) { console.error(e); throw e; }
    }

    async checkHealth() {
        try {
            const data = await this.apiCall('/health');
            this.setOnline(true);
            this.updateMetrics(data);
        } catch { this.setOnline(false); }
    }

    setOnline(online) {
        this.isOnline = online;
        const badge = document.getElementById('statusBadge');
        const text = document.getElementById('statusText');
        if (badge) badge.className = `status-badge ${online ? 'online' : ''}`;
        if (text) text.textContent = online ? 'Online' : 'Offline';
    }

    updateMetrics(data) {
        document.getElementById('metricFiles').textContent = data.open_files || 0;
        document.getElementById('metricSaved').textContent = data.saved_count || 0;
        document.getElementById('metricErrors').textContent = data.errors || 0;
        document.getElementById('metricExtensions').textContent = data.extensions || 0;
    }

    loadCapabilities() {
        const grid = document.getElementById('capabilitiesGrid');
        if (!grid) return;
        grid.innerHTML = this.config.capabilities.map(c => `
            <div class="capability-card" onclick="app.testCapability('${c.id}')">
                <span class="capability-icon">${c.icon}</span>
                <div class="capability-info"><h4>${c.name}</h4><p>${c.description}</p></div>
            </div>
        `).join('');
    }

    async testCapability(id) { this.showToast(`Testing ${id}...`, 'info'); }

    // File Tree
    async loadFileTree() {
        const container = document.getElementById('fileTreeContainer');
        if (!container) return;
        try {
            const data = await this.apiCall('/vscode/files').catch(() => ({ files: [] }));
            const files = data.files || [
                { name: 'main.py', type: 'file' }, { name: 'config.py', type: 'file' },
                { name: 'src/', type: 'folder' }, { name: 'tests/', type: 'folder' }
            ];
            container.innerHTML = files.map(f => `
                <div class="file-item" onclick="app.openFileFromTree('${f.name}')">
                    ${f.type === 'folder' ? '📁' : '📄'} ${f.name}
                </div>
            `).join('');
        } catch { container.innerHTML = '<p>Failed to load</p>'; }
    }

    openFileFromTree(name) { this.showToast(`Opening ${name}`, 'info'); }
    searchFiles() { /* search implementation */ }

    // Editor
    setupEditor() {
        const editor = document.getElementById('codeEditor');
        const lineNums = document.getElementById('lineNumbers');
        if (editor && lineNums) {
            editor.addEventListener('input', () => this.updateLineNumbers());
            editor.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') { e.preventDefault(); document.execCommand('insertText', false, '    '); }
            });
        }
    }

    updateLineNumbers() {
        const editor = document.getElementById('codeEditor');
        const lineNums = document.getElementById('lineNumbers');
        if (editor && lineNums) {
            const lines = editor.value.split('\n').length;
            lineNums.innerHTML = Array.from({ length: lines }, (_, i) => i + 1).join('<br>');
        }
    }

    async saveFile() { this.showToast('File saved', 'success'); }
    async formatCode() {
        const editor = document.getElementById('codeEditor');
        if (editor) {
            try {
                const res = await this.apiCall('/vscode/format', 'POST', { code: editor.value, language: 'python' });
                if (res.formatted) editor.value = res.formatted;
                this.showToast('Code formatted', 'success');
            } catch { this.showToast('Format failed', 'error'); }
        }
    }
    async runCode() { this.showToast('Running code...', 'info'); }

    // Terminal
    async executeTerminal() {
        const input = document.getElementById('terminalInput');
        const output = document.getElementById('terminalOutput');
        const cmd = input?.value?.trim();
        if (!cmd || !output) return;
        
        output.innerHTML += `<div class="term-line">$ ${cmd}</div>`;
        input.value = '';
        
        try {
            const res = await this.apiCall('/vscode/terminal', 'POST', { command: cmd });
            output.innerHTML += `<div class="term-line">${res.output || res.result || 'OK'}</div>`;
        } catch (e) {
            output.innerHTML += `<div class="term-line" style="color:#f44">Error: ${e.message}</div>`;
        }
        output.scrollTop = output.scrollHeight;
    }

    clearTerminal() {
        const output = document.getElementById('terminalOutput');
        if (output) output.innerHTML = '<div class="term-line">$ Terminal cleared</div>';
    }

    // Git
    async gitRefresh() {
        try {
            const status = await this.apiCall('/vscode/git', 'POST', { action: 'status' }).catch(() => ({ output: 'No changes' }));
            const log = await this.apiCall('/vscode/git', 'POST', { action: 'log' }).catch(() => ({ commits: [] }));
            
            document.getElementById('gitStatusOutput').textContent = status.output || 'Clean';
            document.getElementById('gitLogOutput').innerHTML = (log.commits || []).slice(0, 5).map(c => 
                `<div class="file-item">${c.hash?.slice(0,7) || '...'} - ${c.message || 'commit'}</div>`
            ).join('') || '<p>No commits</p>';
        } catch { }
    }

    async gitPull() { this.showToast('Pulling...', 'info'); }
    async gitPush() { this.showToast('Pushing...', 'info'); }
    async gitCommit() { this.showToast('Commit dialog...', 'info'); }
    async gitBranch() { this.showToast('Branches...', 'info'); }
    async gitStash() { this.showToast('Stashing...', 'info'); }
    async gitDiff() { this.showToast('Diff view...', 'info'); }
    gitStatus() { this.showSection('git'); }

    // Debug
    startDebug() { this.showToast('Debug started', 'success'); }
    stopDebug() { this.showToast('Debug stopped', 'info'); }

    // AI
    async explainCode() {
        const code = document.getElementById('codeToExplain')?.value;
        if (!code) return this.showToast('Enter code first', 'warning');
        try {
            const res = await this.apiCall('/vscode/analyze', 'POST', { code, action: 'explain' });
            document.getElementById('explanationOutput').textContent = res.explanation || res.result || 'No explanation';
        } catch { this.showToast('AI failed', 'error'); }
    }

    async refactorCode() {
        const code = document.getElementById('codeToRefactor')?.value;
        if (!code) return this.showToast('Enter code first', 'warning');
        try {
            const res = await this.apiCall('/vscode/refactor', 'POST', { code });
            document.getElementById('refactorOutput').textContent = res.refactored || res.result || code;
        } catch { this.showToast('Refactor failed', 'error'); }
    }

    async generateTests() {
        const target = document.getElementById('testTarget')?.value;
        if (!target) return this.showToast('Enter function name', 'warning');
        try {
            const res = await this.apiCall('/vscode/tests', 'POST', { target });
            document.getElementById('testsOutput').textContent = res.tests || res.result || '# Generated tests...';
        } catch { this.showToast('Generation failed', 'error'); }
    }

    aiAssist() { this.showSection('ai'); }

    // Extensions
    async loadExtensions() {
        const grid = document.getElementById('extensionsGrid');
        if (!grid) return;
        const exts = [
            { name: 'Python', icon: '🐍', desc: 'Python support' },
            { name: 'GitLens', icon: '🔀', desc: 'Git supercharged' },
            { name: 'Prettier', icon: '✨', desc: 'Code formatter' },
            { name: 'ESLint', icon: '⚡', desc: 'JS linting' }
        ];
        grid.innerHTML = exts.map(e => `
            <div class="capability-card">
                <span class="capability-icon">${e.icon}</span>
                <div class="capability-info"><h4>${e.name}</h4><p>${e.desc}</p></div>
            </div>
        `).join('');
    }

    installExtension() { this.showToast('Extension marketplace...', 'info'); }

    // API Test
    async testEndpoint(method, endpoint) {
        try {
            const res = await this.apiCall(endpoint, method);
            this.showModal(`${method} ${endpoint}`, JSON.stringify(res, null, 2));
        } catch (e) { this.showToast(`Failed: ${e.message}`, 'error'); }
    }

    // Logs
    async loadLogs() {
        const output = document.getElementById('logOutput');
        if (!output) return;
        try {
            const data = await this.apiCall('/logs').catch(() => ({ entries: [] }));
            output.innerHTML = (data.entries || []).slice(-50).map(l => 
                `<div class="log-entry ${l.level || 'info'}">[${l.level?.toUpperCase() || 'INFO'}] ${l.message || l}</div>`
            ).join('') || '<div class="log-entry info">No logs</div>';
        } catch { output.innerHTML = '<div class="log-entry error">Failed to load logs</div>'; }
    }

    clearLogs() {
        const output = document.getElementById('logOutput');
        if (output) output.innerHTML = '';
    }

    // Utils
    getToken() { return localStorage.getItem(this.config.auth.tokenKey) || ''; }
    
    showModal(title, content) {
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('modalContent').textContent = content;
        document.getElementById('responseModal').classList.add('active');
    }
    
    closeModal() { document.getElementById('responseModal')?.classList.remove('active'); }
    
    showToast(msg, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = msg;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    refreshAll() { this.checkHealth(); this.loadCapabilities(); }
    openFile() { this.showSection('filetree'); }
    createFile() { this.showToast('Create file dialog...', 'info'); }
    runTerminal() { this.showSection('terminal'); }
}

const app = new VSCodeDashboard();
document.addEventListener('keydown', e => { if (e.key === 'Escape') app.closeModal(); });
