// ============= OPENA20 FRONTEND ENGINE =============
// Module Pattern - Private Scope mit globalen Exports

const opena20 = (function() {
    'use strict';
    
    const API_BASE = window.location.origin;
    let healthCheckInterval;
    let logs = [];
    
    // ===== LOGGER SYSTEM =====
    const Logger = {
        info: (msg) => log(msg, 'info'),
        success: (msg) => log(msg, 'success'),
        warning: (msg) => log(msg, 'warning'),
        error: (msg) => log(msg, 'error')
    };
    
    function log(message, type = 'info') {
        const entry = { timestamp: new Date(), type, message };
        logs.push(entry);
        if (logs.length > 500) logs.shift();
        
        const console_color = {
            info: '%c[INFO]',
            success: '%c[✅ SUCCESS]',
            warning: '%c[⚠️ WARNING]',
            error: '%c[❌ ERROR]'
        };
        
        window.console.log(console_color[type], 'color: ' + 
            (type === 'success' ? '#00ff88' :
             type === 'error' ? '#ff6b6b' :
             type === 'warning' ? '#ffd93d' : '#00d4ff'), message);
    }
    
    // ===== API CLIENT =====
    const API = {
        async get(path) {
            try {
                const response = await fetch(`${API_BASE}${path}`);
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return await response.json();
            } catch (e) {
                Logger.error(`GET ${path}: ${e.message}`);
                throw e;
            }
        },
        
        async post(path, data = {}) {
            try {
                const response = await fetch(`${API_BASE}${path}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return await response.json();
            } catch (e) {
                Logger.error(`POST ${path}: ${e.message}`);
                throw e;
            }
        }
    };
    
    // ===== HEALTH MONITOR =====
    const HealthMonitor = {
        async check() {
            try {
                const data = await API.get('/health');
                updateDashboard(data);
                Logger.info('✅ Health check OK');
                return data;
            } catch (e) {
                Logger.error(`Health check failed: ${e.message}`);
                return null;
            }
        },
        
        startMonitoring() {
            this.check();
            healthCheckInterval = setInterval(() => this.check(), 5000);
            Logger.success('Health monitoring started (5s interval)');
        },
        
        stopMonitoring() {
            if (healthCheckInterval) clearInterval(healthCheckInterval);
            Logger.warning('Health monitoring stopped');
        }
    };
    
    // ===== DASHBOARD UPDATE =====
    function updateDashboard(data) {
        if (!data) return;
        
        // Agents
        const grid = document.getElementById('agents_grid');
        if (grid && data.agents) {
            grid.innerHTML = data.agents.map(agent => `
                <div class="agent_card">
                    <h3>
                        <span class="agent_status"></span>
                        ${agent.name}
                    </h3>
                    <div class="agent_info">
                        <div><strong>Port:</strong> ${agent.port}</div>
                        <div><strong>Status:</strong> ${agent.status}</div>
                        <div><strong>Uptime:</strong> ${agent.uptime || '-'}</div>
                        <div><strong>Requests:</strong> ${agent.requests || 0}</div>
                    </div>
                </div>
            `).join('');
        }
        
        // Safepoints
        if (data.safepoints) {
            const sps = data.safepoints;
            
            if (sps.gateway) {
                document.getElementById('gw_status').textContent = sps.gateway.status || '-';
                document.getElementById('gw_last').textContent = sps.gateway.last_checkpoint || '-';
                document.getElementById('gw_time').textContent = sps.gateway.timestamp || '-';
            }
            
            if (sps.tool_exec) {
                document.getElementById('tool_status').textContent = sps.tool_exec.status || '-';
                document.getElementById('tool_last').textContent = sps.tool_exec.last_checkpoint || '-';
                document.getElementById('tool_time').textContent = sps.tool_exec.timestamp || '-';
            }
            
            if (sps.archive) {
                document.getElementById('arch_status').textContent = sps.archive.status || '-';
                document.getElementById('arch_last').textContent = sps.archive.last_checkpoint || '-';
                document.getElementById('arch_time').textContent = sps.archive.timestamp || '-';
            }
        }
    }
    
    // ===== E2E TESTER =====
    const E2ETester = {
        async run() {
            const panel = document.getElementById('control_status');
            if (!panel) return;
            
            panel.className = 'status_panel';
            panel.textContent = '🔄 Running E2E test...';
            Logger.info('▶️ E2E test started');
            
            try {
                const data = await API.post('/e2e');
                
                if (data.success) {
                    panel.className = 'status_panel success';
                    panel.textContent = `✅ E2E Test PASSED (${data.duration_ms.toFixed(0)}ms)\n\n${
                        Object.entries(data.results)
                            .map(([k, v]) => `${k}: ${v}`)
                            .join('\n')
                    }`;
                    Logger.success(`E2E test passed (${data.duration_ms.toFixed(0)}ms)`);
                } else {
                    panel.className = 'status_panel error';
                    panel.textContent = `❌ E2E Test FAILED\n${data.error || 'Unknown error'}`;
                    Logger.error('E2E test failed');
                }
            } catch (e) {
                panel.className = 'status_panel error';
                panel.textContent = `❌ Error: ${e.message}`;
                Logger.error(`E2E error: ${e.message}`);
            }
        }
    };
    
    // ===== SYSTEM CONTROL =====
    const SystemControl = {
        async restart() {
            if (!window.confirm('🚨 Wirklich den System neu starten? Dies unterbricht aktive Operationen!')) return;
            
            const panel = document.getElementById('control_status');
            if (!panel) return;
            
            panel.className = 'status_panel';
            panel.textContent = '🔄 Restarting system...';
            Logger.warning('⏳ System restart initiated');
            
            try {
                const data = await API.post('/restart');
                
                panel.className = 'status_panel success';
                panel.textContent = `✅ System restarted\n${data.message}`;
                Logger.success('System restart successful');
                
                setTimeout(() => location.reload(), 3000);
            } catch (e) {
                panel.className = 'status_panel error';
                panel.textContent = `❌ Error: ${e.message}`;
                Logger.error(`Restart error: ${e.message}`);
            }
        }
    };
    
    // ===== UI CONTROLLER =====
    const UI = {
        init() {
            this.setupNavigation();
            this.setupButtons();
            Logger.success('UI initialized');
        },
        
        setupNavigation() {
            document.querySelectorAll('.nav-link').forEach(link => {
                link.addEventListener('click', (e) => {
                    if (link.getAttribute('href').startsWith('#')) {
                        e.preventDefault();
                        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                        link.classList.add('active');
                        
                        const target = document.querySelector(link.getAttribute('href'));
                        if (target) {
                            target.scrollIntoView({ behavior: 'smooth' });
                        }
                    }
                });
            });
        },
        
        setupButtons() {
            const e2eBtn = document.querySelector('[onclick="window.runE2E()"]');
            const restartBtn = document.querySelector('[onclick="window.restartSystem()"]');
            
            if (e2eBtn) e2eBtn.addEventListener('click', (e) => {
                e.preventDefault();
                E2ETester.run();
            });
            
            if (restartBtn) restartBtn.addEventListener('click', (e) => {
                e.preventDefault();
                SystemControl.restart();
            });
        }
    };
    
    // ===== PUBLIC API =====
    return {
        Logger,
        API,
        HealthMonitor,
        E2ETester,
        SystemControl,
        UI,
        
        init() {
            Logger.info('🚀 opena20 Frontend Engine initializing...');
            UI.init();
            HealthMonitor.startMonitoring();
            Logger.success('✅ opena20 ready');
        },
        
        getLogs() { return logs; }
    };
})();

// ===== GLOBAL FUNCTIONS =====
function runE2E() {
    opena20.E2ETester.run();
}

function restartSystem() {
    opena20.SystemControl.restart();
}

function addLog(msg, type = 'info') {
    opena20.Logger[type](msg);
}

// ===== INITIALIZATION =====
window.addEventListener('load', () => {
    opena20.init();
});
