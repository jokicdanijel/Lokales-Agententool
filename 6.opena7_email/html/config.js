// 📧 Email Agent 6.0 - Configuration (PORTIER PAS-6.0)

const CONFIG = {
    // API Configuration
    BASE_URL: 'http://localhost:12352',
    API_VERSION: '6.0.0',

    // Authentication
    BEARER_TOKEN_KEY: 'email_agent_bearer_token',

    // Update intervals (milliseconds)
    STATUS_UPDATE_INTERVAL: 5000,      // 5 seconds
    METRICS_REFRESH_INTERVAL: 30000,   // 30 seconds
    LOGS_REFRESH_INTERVAL: 15000,      // 15 seconds

    // UI Configuration
    AUTO_SCROLL_LOGS: true,
    MAX_LOG_ENTRIES: 100,
    NOTIFICATION_DURATION: 4000,       // 4 seconds

    // Email specific settings
    DEFAULT_EMAIL_FOLDER: 'INBOX',
    MAX_EMAILS_PER_REQUEST: 50,

    // AI Configuration
    DEFAULT_AI_MODEL: 'gpt-4o-mini',
    DEFAULT_TONE: 'professional',
    DEFAULT_LANGUAGE: 'german',

    // Performance
    API_TIMEOUT: 30000,               // 30 seconds
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000,                // 1 second

    // Features
    FEATURES: {
        EMAIL_SENDING: true,
        AI_REPLIES: true,
        EMAIL_CLASSIFICATION: true,
        SENTIMENT_ANALYSIS: true,
        AUTO_RESPONSES: true,
        METRICS_TRACKING: true
    },

    // Debug mode
    DEBUG_MODE: false,

    // Color scheme
    THEME: {
        PRIMARY: '#9B59B6',
        SUCCESS: '#27AE60',
        WARNING: '#F39C12',
        ERROR: '#E74C3C',
        INFO: '#3498DB'
    }
};

// Development overrides
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    CONFIG.DEBUG_MODE = true;
    console.log('📧 Email Agent 6.0 - Development mode enabled');
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}

// Log configuration on load
console.log('📧 Email Agent 6.0 Configuration loaded:', {
    baseUrl: CONFIG.BASE_URL,
    version: CONFIG.API_VERSION,
    features: Object.keys(CONFIG.FEATURES).filter(f => CONFIG.FEATURES[f]),
    debug: CONFIG.DEBUG_MODE
});
