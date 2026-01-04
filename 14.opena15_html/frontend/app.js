// opena15 Frontend Logic
let currentHTML = '';
let templates = [];

// DOM Elements
const statusBadge = document.getElementById('status-badge');
const tokenInput = document.getElementById('token-input');
const templateSelect = document.getElementById('template-select');
const generateForm = document.getElementById('generate-form');
const resultSection = document.getElementById('result-section');
const htmlOutput = document.getElementById('html-output');
const templatesCount = document.getElementById('templates-count');
const lastChecked = document.getElementById('last-checked');
const portNumber = document.getElementById('port-number');
const templateUsed = document.getElementById('template-used');

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    loadTokenFromStorage();
    checkHealth();
    loadTemplates();
    setupEventListeners();
});

// Token Management
function loadTokenFromStorage() {
    const savedToken = localStorage.getItem('opena15_token');
    if (savedToken) {
        tokenInput.value = savedToken;
        console.log('Token geladen aus localStorage');
    } else {
        // Default Token setzen
        tokenInput.value = 'c899b90d-faf8-485b-afa4-078357cf5313';
    }
}

function saveToken() {
    const token = tokenInput.value.trim();
    if (token) {
        localStorage.setItem('opena15_token', token);
        alert('✅ Token gespeichert!');
        console.log('Token gespeichert in localStorage');
    } else {
        alert('⚠️ Bitte Token eingeben');
    }
}

function clearToken() {
    localStorage.removeItem('opena15_token');
    tokenInput.value = '';
    alert('🗑️ Token gelöscht');
    console.log('Token aus localStorage entfernt');
}

// Health Check
async function checkHealth() {
    try {
        const data = await apiRequest(API_ENDPOINTS.health);
        statusBadge.textContent = `✅ ${data.status.toUpperCase()}`;
        statusBadge.classList.remove('offline');
        statusBadge.classList.add('online');

        // Populate additional status fields
        if (portNumber) portNumber.textContent = data.port || portNumber.textContent;
        if (templatesCount && typeof data.templates_available !== 'undefined') templatesCount.textContent = data.templates_available;
        if (lastChecked) lastChecked.textContent = new Date().toLocaleString();

        console.log('Agent Status:', data);
    } catch (error) {
        statusBadge.textContent = '❌ OFFLINE';
        statusBadge.classList.remove('online');
        statusBadge.classList.add('offline');
        console.error('Health check failed:', error);
    }
}

// Load Templates
async function loadTemplates() {
    try {
        const data = await apiRequest(API_ENDPOINTS.templatesList);
        templates = data.templates || [];

        templateSelect.innerHTML = '<option value="">-- Template auswählen --</option>';
        templates.forEach(tpl => {
            const option = document.createElement('option');
            option.value = tpl;
            option.textContent = tpl;
            templateSelect.appendChild(option);
        });

        // Update templates count in header
        if (templatesCount) templatesCount.textContent = templates.length;
        console.log('Templates geladen:', templates);
    } catch (error) {
        templateSelect.innerHTML = '<option value="">❌ Fehler beim Laden</option>';
        console.error('Templates laden fehlgeschlagen:', error);
    }
}

// Setup Event Listeners
function setupEventListeners() {
    document.getElementById('save-token').addEventListener('click', saveToken);
    document.getElementById('clear-token').addEventListener('click', clearToken);
    document.getElementById('refresh-templates').addEventListener('click', loadTemplates);
    generateForm.addEventListener('submit', handleGenerate);
    document.getElementById('copy-html').addEventListener('click', copyToClipboard);
    document.getElementById('download-html').addEventListener('click', downloadHTML);
    document.getElementById('preview-html').addEventListener('click', previewHTML);
}

// Generate HTML
async function handleGenerate(e) {
    e.preventDefault();

    const templateName = templateSelect.value || 'default.html';
    const title = document.getElementById('title').value;
    const heading = document.getElementById('heading').value;
    const content = document.getElementById('content').value;
    const cssFramework = document.getElementById('css-framework').value;

    try {
        const data = await apiRequest(API_ENDPOINTS.generate, {
            method: 'POST',
            body: JSON.stringify({
                template_name: templateName,
                variables: {
                    title: title,
                    heading: heading || title,
                    content: content || 'Generiert mit opena15'
                },
                css_framework: cssFramework,
                title: title,
                description: `Generiert mit opena15 HTML Creator`,
                keywords: ['html', 'opena15', cssFramework]
            })
        });

        currentHTML = data.html;
        showResult(currentHTML);
        // Display which template was used
        if (templateUsed) templateUsed.textContent = data.template_used || templateSelect.value || '—';
        console.log('HTML generiert:', data);
    } catch (error) {
        alert(`Fehler: ${error.message}`);
        console.error('Generierung fehlgeschlagen:', error);
    }
}

// Show Result
function showResult(html) {
    htmlOutput.textContent = html;
    resultSection.style.display = 'block';
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

// Copy to Clipboard
async function copyToClipboard() {
    try {
        await navigator.clipboard.writeText(currentHTML);
        alert('✅ HTML in Zwischenablage kopiert!');
    } catch (error) {
        console.error('Kopieren fehlgeschlagen:', error);
    }
}

// Download HTML
function downloadHTML() {
    const blob = new Blob([currentHTML], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'generated.html';
    a.click();
    URL.revokeObjectURL(url);
}

// Preview HTML
function previewHTML() {
    const newWindow = window.open('', '_blank');
    newWindow.document.write(currentHTML);
    newWindow.document.close();
}

// Periodic Health Check (every 30s)
setInterval(checkHealth, 30000);
