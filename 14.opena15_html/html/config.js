const CONFIG = {
    API_PORT: 12360,
    API_BASE_URL: 'http://127.0.0.1:12360',
    
    ENDPOINTS: {
        HEALTH: '/health',
        TEMPLATES_LIST: '/templates/list',
        GENERATE: '/generate',
        VALIDATE: '/validate',
        PREVIEW: '/preview',
        EXPORT: '/export'
    },
    
    AUTH: {
        TOKEN_KEY: 'opena15_bearer_token',
        BEARER_PREFIX: 'Bearer '
    },
    
    CSS_FRAMEWORKS: ['none', 'bootstrap', 'tailwind', 'bulma'],
    VALIDATION_LEVELS: ['basic', 'standard', 'strict'],
    EXPORT_FORMATS: ['html', 'base64', 'zip'],
    
    DEFAULT_TEMPLATES: [
        { name: 'default.html', icon: '📄', description: 'Standard HTML Template' },
        { name: 'landing.html', icon: '🚀', description: 'Landing Page Template' },
        { name: 'dashboard.html', icon: '📊', description: 'Dashboard Template' },
        { name: 'form.html', icon: '📝', description: 'Formular Template' }
    ],
    
    REFRESH_INTERVALS: {
        STATUS: 30000,
        TEMPLATES: 120000
    },
    
    UI: {
        DATE_LOCALE: 'de-DE',
        TOAST_DURATION: 4000,
        MAX_ACTIVITY_ITEMS: 25,
        MAX_HISTORY_ITEMS: 20
    },
    
    PREVIEW: {
        DEFAULT_WIDTH: 1280,
        DEFAULT_HEIGHT: 720,
        MIN_WIDTH: 320,
        MAX_WIDTH: 1920,
        MIN_HEIGHT: 240,
        MAX_HEIGHT: 1080
    }
};
