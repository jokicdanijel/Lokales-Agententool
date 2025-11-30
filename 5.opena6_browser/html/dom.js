// 🔍 Browser Agent 6.0 - DOM Inspector & Navigation

let domInspectorEnabled = false;
let selectedElement = null;
let highlightOverlay = null;

// ===============================================
// DOM Inspector Core Functions
// ===============================================

function toggleDOMInspector() {
    domInspectorEnabled = !domInspectorEnabled;
    
    const button = document.querySelector('[onclick="toggleDOMInspector()"]');
    const domPanel = document.getElementById('domInspector');
    const domTree = document.getElementById('domTree');
    const elementInfo = document.getElementById('elementInfo');
    
    if (domInspectorEnabled) {
        button.textContent = '🔍 Stop Inspection';
        button.className = 'btn btn-danger btn-sm';
        domPanel.style.display = 'block';
        
        // Load initial DOM structure
        loadDOMStructure();
        
        showNotification('DOM Inspector activated - Click elements to inspect', 'info');
    } else {
        button.textContent = '🔍 DOM Inspector';
        button.className = 'btn btn-primary btn-sm';
        domPanel.style.display = 'none';
        
        // Clear selections
        clearElementHighlight();
        selectedElement = null;
        domTree.innerHTML = '';
        elementInfo.innerHTML = '';
        
        showNotification('DOM Inspector deactivated', 'info');
    }
}

async function loadDOMStructure() {
    const domTree = document.getElementById('domTree');
    
    try {
        // Simulate loading DOM structure from browser API
        domTree.innerHTML = '<div class="loading">Loading DOM structure...</div>';
        
        const response = await api('/dom/structure');
        
        if (response && response.html) {
            renderDOMTree(response.html);
        } else {
            // Fallback: render current page structure
            renderCurrentPageDOM();
        }
        
    } catch (error) {
        console.error('Failed to load DOM structure:', error);
        renderCurrentPageDOM();
    }
}

function renderDOMTree(htmlString) {
    const domTree = document.getElementById('domTree');
    
    try {
        // Parse HTML and create tree structure
        const parser = new DOMParser();
        const doc = parser.parseFromString(htmlString, 'text/html');
        
        const treeHtml = buildDOMTreeHTML(doc.documentElement, 0);
        domTree.innerHTML = treeHtml;
        
    } catch (error) {
        console.error('Failed to render DOM tree:', error);
        domTree.innerHTML = '<div class="error">Failed to render DOM structure</div>';
    }
}

function renderCurrentPageDOM() {
    const domTree = document.getElementById('domTree');
    
    // Use current page structure as fallback
    const treeHtml = buildDOMTreeHTML(document.documentElement, 0);
    domTree.innerHTML = treeHtml;
}

function buildDOMTreeHTML(element, depth) {
    const indent = '  '.repeat(depth);
    const tagName = element.tagName.toLowerCase();
    const id = element.id ? ` id="${element.id}"` : '';
    const classes = element.className ? ` class="${element.className}"` : '';
    
    let html = `${indent}<div class="dom-node" data-tag="${tagName}" onclick="selectDOMElement(this, '${tagName}${id}${classes}')">\n`;
    html += `${indent}  <span class="tag-name">&lt;${tagName}${id}${classes}&gt;</span>\n`;
    
    // Add children if any
    const children = Array.from(element.children);
    if (children.length > 0) {
        html += `${indent}  <div class="dom-children">\n`;
        for (const child of children.slice(0, 50)) { // Limit to 50 children for performance
            html += buildDOMTreeHTML(child, depth + 2);
        }
        if (children.length > 50) {
            html += `${indent}    <div class="dom-node truncated">... ${children.length - 50} more elements</div>\n`;
        }
        html += `${indent}  </div>\n`;
    }
    
    html += `${indent}</div>\n`;
    return html;
}

function selectDOMElement(nodeElement, selector) {
    // Clear previous selection
    document.querySelectorAll('.dom-node.selected').forEach(node => {
        node.classList.remove('selected');
    });
    
    // Select new element
    nodeElement.classList.add('selected');
    selectedElement = selector;
    
    // Show element info
    showElementInfo(selector);
    
    // Highlight element in page (if possible)
    highlightElement(selector);
}

async function showElementInfo(selector) {
    const elementInfo = document.getElementById('elementInfo');
    
    try {
        // Try to get element info from API
        const response = await api(`/dom/element?selector=${encodeURIComponent(selector)}`);
        
        if (response && response.element) {
            renderElementInfo(response.element);
        } else {
            // Fallback: show basic info
            renderBasicElementInfo(selector);
        }
        
    } catch (error) {
        console.error('Failed to get element info:', error);
        renderBasicElementInfo(selector);
    }
}

function renderElementInfo(elementData) {
    const elementInfo = document.getElementById('elementInfo');
    
    const html = `
        <div class="element-details">
            <h6>Element Information</h6>
            <div class="info-group">
                <strong>Tag:</strong> ${elementData.tagName || 'Unknown'}
            </div>
            <div class="info-group">
                <strong>ID:</strong> ${elementData.id || 'None'}
            </div>
            <div class="info-group">
                <strong>Classes:</strong> ${elementData.className || 'None'}
            </div>
            <div class="info-group">
                <strong>Text:</strong> ${elementData.textContent ? elementData.textContent.substring(0, 100) : 'None'}
            </div>
            <div class="info-group">
                <strong>Attributes:</strong>
                <div class="attributes-list">
                    ${Object.entries(elementData.attributes || {}).map(([key, value]) => 
                        `<div><code>${key}</code>: <code>${value}</code></div>`
                    ).join('')}
                </div>
            </div>
            <div class="info-group">
                <strong>Position:</strong> 
                x: ${elementData.x || 0}, y: ${elementData.y || 0}
            </div>
            <div class="info-group">
                <strong>Size:</strong> 
                ${elementData.width || 0} × ${elementData.height || 0}
            </div>
        </div>
    `;
    
    elementInfo.innerHTML = html;
}

function renderBasicElementInfo(selector) {
    const elementInfo = document.getElementById('elementInfo');
    
    const html = `
        <div class="element-details">
            <h6>Element Information</h6>
            <div class="info-group">
                <strong>Selector:</strong> ${selector}
            </div>
            <div class="info-group">
                <strong>Status:</strong> Selected for inspection
            </div>
            <p class="text-muted mt-2">
                <small>Connect to browser agent to get detailed element information.</small>
            </p>
        </div>
    `;
    
    elementInfo.innerHTML = html;
}

function highlightElement(selector) {
    // This would typically send a command to the browser to highlight the element
    // For now, we'll just log it
    console.log('Highlighting element:', selector);
    
    // Show visual feedback in DOM tree
    showNotification(`Selected: ${selector}`, 'info');
}

function clearElementHighlight() {
    if (highlightOverlay) {
        highlightOverlay.remove();
        highlightOverlay = null;
    }
}

// ===============================================
// DOM Actions
// ===============================================

async function clickSelectedElement() {
    if (!selectedElement) {
        showNotification('Please select an element first', 'warning');
        return;
    }
    
    try {
        const payload = {
            command: "click",
            args: {
                selector: selectedElement,
                waitFor: "element"
            }
        };
        
        const response = await api('/command', 'POST', payload);
        showNotification(`Clicked element: ${selectedElement}`, 'success');
        log('cmd_output', `✅ Clicked element: ${selectedElement}`);
        
    } catch (error) {
        showNotification(`Failed to click element: ${error.message}`, 'error');
    }
}

async function getElementText() {
    if (!selectedElement) {
        showNotification('Please select an element first', 'warning');
        return;
    }
    
    try {
        const payload = {
            action: "execute_js",
            source: `document.querySelector('${selectedElement}').textContent`,
            context: "main"
        };
        
        const response = await api('/specialized', 'POST', payload);
        showNotification('Text extracted successfully', 'success');
        log('spec_output', `Text from ${selectedElement}: ${response.result || 'No text'}`);
        
    } catch (error) {
        showNotification(`Failed to get text: ${error.message}`, 'error');
    }
}

async function getElementHTML() {
    if (!selectedElement) {
        showNotification('Please select an element first', 'warning');
        return;
    }
    
    try {
        const payload = {
            action: "execute_js",
            source: `document.querySelector('${selectedElement}').outerHTML`,
            context: "main"
        };
        
        const response = await api('/specialized', 'POST', payload);
        showNotification('HTML extracted successfully', 'success');
        log('spec_output', `HTML from ${selectedElement}:`);
        log('spec_output', response.result || 'No HTML');
        
    } catch (error) {
        showNotification(`Failed to get HTML: ${error.message}`, 'error');
    }
}

// ===============================================
// Navigation Functions
// ===============================================

async function navigateToURL() {
    const url = prompt('Enter URL to navigate to:');
    if (!url) return;
    
    try {
        const payload = {
            command: "goto",
            args: {
                url: url,
                waitFor: "networkidle"
            }
        };
        
        const response = await api('/command', 'POST', payload);
        showNotification(`Navigated to: ${url}`, 'success');
        log('cmd_output', `✅ Navigated to: ${url}`);
        
        // Refresh DOM structure after navigation
        if (domInspectorEnabled) {
            setTimeout(() => loadDOMStructure(), 1000);
        }
        
    } catch (error) {
        showNotification(`Navigation failed: ${error.message}`, 'error');
    }
}

async function refreshPage() {
    try {
        const payload = {
            action: "execute_js",
            source: "location.reload()",
            context: "main"
        };
        
        const response = await api('/specialized', 'POST', payload);
        showNotification('Page refreshed', 'success');
        
        // Refresh DOM structure after reload
        if (domInspectorEnabled) {
            setTimeout(() => loadDOMStructure(), 2000);
        }
        
    } catch (error) {
        showNotification(`Refresh failed: ${error.message}`, 'error');
    }
}

async function goBack() {
    try {
        const payload = {
            action: "execute_js",
            source: "history.back()",
            context: "main"
        };
        
        const response = await api('/specialized', 'POST', payload);
        showNotification('Navigated back', 'success');
        
        if (domInspectorEnabled) {
            setTimeout(() => loadDOMStructure(), 1000);
        }
        
    } catch (error) {
        showNotification(`Navigation failed: ${error.message}`, 'error');
    }
}

async function goForward() {
    try {
        const payload = {
            action: "execute_js",
            source: "history.forward()",
            context: "main"
        };
        
        const response = await api('/specialized', 'POST', payload);
        showNotification('Navigated forward', 'success');
        
        if (domInspectorEnabled) {
            setTimeout(() => loadDOMStructure(), 1000);
        }
        
    } catch (error) {
        showNotification(`Navigation failed: ${error.message}`, 'error');
    }
}

// ===============================================
// Search & Filter Functions
// ===============================================

function searchDOM() {
    const searchTerm = document.getElementById('domSearch').value.toLowerCase().trim();
    const domNodes = document.querySelectorAll('.dom-node');
    
    if (!searchTerm) {
        // Show all nodes
        domNodes.forEach(node => {
            node.style.display = '';
        });
        return;
    }
    
    domNodes.forEach(node => {
        const tagName = node.querySelector('.tag-name');
        if (tagName && tagName.textContent.toLowerCase().includes(searchTerm)) {
            node.style.display = '';
        } else {
            node.style.display = 'none';
        }
    });
}

// ===============================================
// Export Functions
// ===============================================

function exportDOMStructure() {
    const domTree = document.getElementById('domTree');
    const content = domTree.textContent || domTree.innerText;
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `dom-structure-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    URL.revokeObjectURL(url);
    showNotification('DOM structure exported', 'success');
}