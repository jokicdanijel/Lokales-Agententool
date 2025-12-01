// 🔥 Browser Agent 6.0 - Core API & Application Logic

let isConnected = false;
let authToken = '';
let statusUpdateTimer = null;

// ===============================================
// Authentication & Connection
// ===============================================

async function authenticate() {
    const tokenInput = document.getElementById('token');
    const token = tokenInput.value.trim();
    
    if (!token) {
        showNotification('Please enter a Bearer token', 'error');
        return;
    }
    
    authToken = token;
    localStorage.setItem(CONFIG.BEARER_TOKEN_KEY, token);
    
    try {
        const response = await api('/health');
        if (response.status === 'ok') {
            isConnected = true;
            updateConnectionStatus(true);
            startStatusUpdates();
            showNotification('Connected successfully!', 'success');
        } else {
            throw new Error('Health check failed');
        }
    } catch (error) {
        isConnected = false;
        updateConnectionStatus(false);
        showNotification(`Connection failed: ${error.message}`, 'error');
    }
}

function updateConnectionStatus(connected) {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    const connectionStatus = document.getElementById('connectionStatus');
    const footerStatus = document.getElementById('footerStatus');
    
    if (connected) {
        statusDot.className = 'status-dot connected';
        statusText.textContent = 'Connected';
        connectionStatus.textContent = 'Connected';
        footerStatus.textContent = 'Connected';
    } else {
        statusDot.className = 'status-dot';
        statusText.textContent = 'Disconnected';
        connectionStatus.textContent = 'Disconnected';  
        footerStatus.textContent = 'Disconnected';
    }
}

function startStatusUpdates() {
    if (statusUpdateTimer) {
        clearInterval(statusUpdateTimer);
    }
    
    statusUpdateTimer = setInterval(async () => {
        try {
            const response = await api('/health');
            if (response.status !== 'ok') {
                throw new Error('Health check failed');
            }
            updateLastUpdated();
        } catch (error) {
            isConnected = false;
            updateConnectionStatus(false);
            clearInterval(statusUpdateTimer);
            showNotification('Connection lost', 'warning');
        }
    }, CONFIG.STATUS_UPDATE_INTERVAL);
}

function updateLastUpdated() {
    const lastUpdated = document.getElementById('lastUpdated');
    if (lastUpdated) {
        lastUpdated.textContent = new Date().toLocaleTimeString();
    }
}

// ===============================================
// API Helper Functions
// ===============================================

async function api(path, method = 'GET', payload = null) {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const options = {
        method,
        headers
    };
    
    if (payload) {
        options.body = JSON.stringify(payload);
    }
    
    try {
        const response = await fetch(`${CONFIG.BASE_URL}${path}`, options);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else {
            return await response.text();
        }
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

function log(elementId, data, clear = false) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    if (clear) {
        element.textContent = '';
    }
    
    let content;
    if (typeof data === 'object') {
        content = JSON.stringify(data, null, 2);
    } else {
        content = String(data);
    }
    
    if (clear) {
        element.textContent = content;
    } else {
        element.textContent += (element.textContent ? '\n' : '') + content;
    }
    
    // Auto-scroll to bottom if enabled
    if (CONFIG.AUTO_SCROLL_LOGS) {
        element.scrollTop = element.scrollHeight;
    }
}

// ===============================================
// Command Functions
// ===============================================

async function runCommand() {
    const payloadText = document.getElementById('cmd_payload').value.trim();
    
    if (!payloadText) {
        showNotification('Please enter a command payload', 'warning');
        return;
    }
    
    try {
        const payload = JSON.parse(payloadText);
        log('cmd_output', `🚀 Executing command: ${payload.command || 'unknown'}`, true);
        
        const response = await api('/command', 'POST', payload);
        log('cmd_output', '✅ Command executed successfully:');
        log('cmd_output', response);
        
        showNotification('Command executed successfully', 'success');
    } catch (error) {
        log('cmd_output', `❌ Command failed: ${error.message}`);
        showNotification(`Command failed: ${error.message}`, 'error');
    }
}

async function runSpecialized() {
    const payloadText = document.getElementById('spec_payload').value.trim();
    
    if (!payloadText) {
        showNotification('Please enter a specialized action payload', 'warning');
        return;
    }
    
    try {
        const payload = JSON.parse(payloadText);
        log('spec_output', `🚀 Executing specialized action: ${payload.action || 'unknown'}`, true);
        
        const response = await api('/specialized', 'POST', payload);
        log('spec_output', '✅ Specialized action executed successfully:');
        log('spec_output', response);
        
        showNotification('Specialized action executed successfully', 'success');
    } catch (error) {
        log('spec_output', `❌ Specialized action failed: ${error.message}`);
        showNotification(`Specialized action failed: ${error.message}`, 'error');
    }
}

// ===============================================
// Template Functions
// ===============================================

function loadTemplate(type) {
    const templates = {
        goto: {
            command: "goto",
            args: {
                url: "https://example.com",
                waitFor: "networkidle"
            }
        },
        click: {
            command: "click",
            args: {
                selector: "#button",
                waitFor: "element"
            }
        },
        type: {
            command: "type",
            args: {
                selector: "#input",
                text: "Hello World",
                delay: 100
            }
        },
        screenshot: {
            command: "screenshot",
            args: {
                fullPage: true,
                format: "png"
            }
        },
        scroll: {
            command: "scroll",
            args: {
                x: 0,
                y: 500
            }
        }
    };
    
    const template = templates[type];
    if (template) {
        document.getElementById('cmd_payload').value = JSON.stringify(template, null, 2);
    }
}

function loadSpecTemplate(type) {
    const templates = {
        js: {
            action: "execute_js",
            source: "document.title",
            context: "main"
        },
        extract: {
            action: "extract_data",
            selectors: {
                title: "h1",
                links: "a[href]"
            }
        },
        pdf: {
            action: "generate_pdf",
            options: {
                format: "A4",
                margin: "1cm"
            }
        },
        cookies: {
            action: "manage_cookies",
            operation: "list"
        }
    };
    
    const template = templates[type];
    if (template) {
        document.getElementById('spec_payload').value = JSON.stringify(template, null, 2);
    }
}

// ===============================================
// Validation Functions
// ===============================================

function validateCommand() {
    const payloadText = document.getElementById('cmd_payload').value.trim();
    
    try {
        const payload = JSON.parse(payloadText);
        
        if (!payload.command) {
            throw new Error('Missing required "command" field');
        }
        
        if (!payload.args) {
            throw new Error('Missing required "args" field');
        }
        
        showNotification('✅ Command payload is valid', 'success');
        log('cmd_output', '✅ Validation passed', true);
        
    } catch (error) {
        showNotification(`❌ Invalid JSON: ${error.message}`, 'error');
        log('cmd_output', `❌ Validation failed: ${error.message}`, true);
    }
}

function validateSpecialized() {
    const payloadText = document.getElementById('spec_payload').value.trim();
    
    try {
        const payload = JSON.parse(payloadText);
        
        if (!payload.action) {
            throw new Error('Missing required "action" field');
        }
        
        showNotification('✅ Specialized payload is valid', 'success');
        log('spec_output', '✅ Validation passed', true);
        
    } catch (error) {
        showNotification(`❌ Invalid JSON: ${error.message}`, 'error');
        log('spec_output', `❌ Validation failed: ${error.message}`, true);
    }
}

// ===============================================
// Clear Functions
// ===============================================

function clearCommand() {
    document.getElementById('cmd_payload').value = '';
    log('cmd_output', '', true);
}

function clearSpecialized() {
    document.getElementById('spec_payload').value = '';
    log('spec_output', '', true);
}

// ===============================================
// Notification System
// ===============================================

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '6px',
        color: 'white',
        fontWeight: '500',
        zIndex: '9999',
        transition: 'all 0.3s ease',
        transform: 'translateX(100%)',
        maxWidth: '400px'
    });
    
    // Set background color based on type
    const colors = {
        success: '#238636',
        error: '#da3633',
        warning: '#d29922',
        info: '#1f6feb'
    };
    
    notification.style.background = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// ===============================================
// Initialization
// ===============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔥 Browser Agent 6.0 Dashboard Loaded');
    
    // Load saved token
    const savedToken = localStorage.getItem(CONFIG.BEARER_TOKEN_KEY);
    if (savedToken) {
        document.getElementById('token').value = savedToken;
        authToken = savedToken;
    }
    
    // Update last updated time
    updateLastUpdated();
    
    // Initialize connection status
    updateConnectionStatus(false);
    
    console.log('✅ Dashboard initialized successfully');
});