// Dashboard JavaScript - Live Status & Controls

const API_BASE = '/api';
let refreshInterval = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    logMessage('Dashboard loaded');
    refreshStatus();
    startAutoRefresh();
});

// Auto-refresh every 5 seconds
function startAutoRefresh() {
    refreshInterval = setInterval(refreshStatus, 5000);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// Refresh status of all services
async function refreshStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();
        updateStatusDisplay(data);
    } catch (error) {
        logMessage(`Status refresh failed: ${error.message}`, 'error');
    }
}

// Update status display
function updateStatusDisplay(data) {
    // opena1
    updateServiceCard('opena1', data.opena1);
    
    // opena2
    updateServiceCard('opena2', data.opena2);
    
    // kordp
    updateServiceCard('kordp', data.kordp);
    
    // archivp
    if (data.archivp) {
        const indicator = document.getElementById('archivp-status');
        const count = document.getElementById('archivp-count');
        
        if (data.archivp.status === 'ok') {
            indicator.textContent = '✅';
            indicator.className = 'status-indicator status-ok';
            count.textContent = `Safepoints: ${data.archivp.safepoints_today || 0}`;
        } else {
            indicator.textContent = '❌';
            indicator.className = 'status-indicator status-error';
            count.textContent = 'Error';
        }
    }
}

function updateServiceCard(service, data) {
    const indicator = document.getElementById(`${service}-status`);
    
    if (!data) {
        indicator.textContent = '❌';
        indicator.className = 'status-indicator status-error';
        return;
    }
    
    if (data.status === 'ok') {
        indicator.textContent = '✅';
        indicator.className = 'status-indicator status-ok';
    } else if (data.status === 'unreachable') {
        indicator.textContent = '🔴';
        indicator.className = 'status-indicator status-error';
    } else {
        indicator.textContent = '⚠️';
        indicator.className = 'status-indicator status-error';
    }
}

// Run E2E Test
async function runE2ETest() {
    logMessage('Starting E2E test...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/e2e`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.ok) {
            logMessage('E2E test completed successfully ✅', 'success');
            logMessage(`Result: ${JSON.stringify(data.result)}`, 'info');
        } else {
            logMessage(`E2E test failed: ${data.error}`, 'error');
        }
    } catch (error) {
        logMessage(`E2E test error: ${error.message}`, 'error');
    }
}

// Inspect Safepoints
async function inspectSafepoints() {
    logMessage('Loading safepoints...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/safepoints`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.ok) {
            displaySafepoints(data.safepoints);
            logMessage(`Loaded ${data.count} safepoints`, 'success');
        } else {
            logMessage('Failed to load safepoints', 'error');
        }
    } catch (error) {
        logMessage(`Safepoints error: ${error.message}`, 'error');
    }
}

function displaySafepoints(safepoints) {
    const section = document.getElementById('safepoints-section');
    const list = document.getElementById('safepoints-list');
    
    list.innerHTML = '';
    
    if (safepoints.length === 0) {
        list.innerHTML = '<p style="text-align: center; color: #666;">No safepoints today</p>';
    } else {
        safepoints.forEach(sp => {
            const item = document.createElement('div');
            item.className = 'safepoint-item';
            
            const filename = document.createElement('div');
            filename.className = 'safepoint-filename';
            filename.textContent = sp.filename;
            
            const meta = document.createElement('div');
            meta.className = 'safepoint-meta';
            meta.textContent = `${sp.src} → ${sp.dst} | ${sp.kind} | ${(sp.size / 1024).toFixed(2)} KB`;
            
            item.appendChild(filename);
            item.appendChild(meta);
            list.appendChild(item);
        });
    }
    
    section.style.display = 'block';
}

// Restart Stack
async function restartStack() {
    if (!confirm('Stack neu starten? Services werden kurzzeitig offline sein.')) {
        return;
    }
    
    logMessage('Restarting stack...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/restart`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.ok) {
            logMessage('Stack restart initiated ✅', 'success');
            logMessage('Waiting for services to come online...', 'info');
            
            // Wait and refresh
            setTimeout(() => {
                refreshStatus();
            }, 5000);
        } else {
            logMessage(`Restart failed: ${data.error}`, 'error');
        }
    } catch (error) {
        logMessage(`Restart error: ${error.message}`, 'error');
    }
}

// Log message to activity log
function logMessage(message, type = 'info') {
    const logOutput = document.getElementById('log-output');
    const entry = document.createElement('p');
    entry.className = `log-entry log-${type}`;
    
    const timestamp = new Date().toLocaleTimeString('de-DE');
    entry.textContent = `[${timestamp}] ${message}`;
    
    logOutput.appendChild(entry);
    logOutput.scrollTop = logOutput.scrollHeight;
    
    // Keep only last 50 entries
    while (logOutput.children.length > 50) {
        logOutput.removeChild(logOutput.firstChild);
    }
}
