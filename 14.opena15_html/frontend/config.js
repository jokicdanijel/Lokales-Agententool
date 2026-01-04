// opena15 Frontend Configuration
const API_BASE = 'http://localhost:12360';
const API_ENDPOINTS = {
    health: `${API_BASE}/health`,
    templatesList: `${API_BASE}/templates/list`,
    generate: `${API_BASE}/generate`,
    validate: `${API_BASE}/validate`,
    preview: `${API_BASE}/preview`,
    export: `${API_BASE}/export`
};

// Bearer Token (aus localStorage oder Default)
function getBearerToken() {
    return localStorage.getItem('opena15_token') || 'c899b90d-faf8-485b-afa4-078357cf5313';
}

// API Request Helper
async function apiRequest(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    // Bearer Token nur für geschützte Endpoints (nicht /health)
    if (!endpoint.includes('/health')) {
        const token = getBearerToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
    }

    try {
        const response = await fetch(endpoint, {
            ...options,
            headers
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Request failed:', error);
        throw error;
    }
}
