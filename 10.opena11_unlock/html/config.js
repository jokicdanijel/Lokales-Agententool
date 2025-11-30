// 🔐 OPENA11 Unlock Master Dashboard - Configuration
// PORTIER PAS-6.0

const CONFIG = {
    // API Configuration
    API_BASE_URL: window.location.origin,
    API_PORT: 12357,
    
    // Endpoints
    ENDPOINTS: {
        HEALTH: '/health',
        STATUS: '/status',
        COMMAND: '/command',
        LOGS: '/logs',
        METRICS: '/metrics',
        CONFIG: '/config'
    },
    
    // Specialized Endpoints
    SPECIALIZED_ENDPOINTS: {
        QUICK_GRANT: '/specialized/quick_grant',
        QUICK_CHECK: '/specialized/quick_check',
        SUBJECT: '/specialized/subject',
        SECURITY_SCAN: '/specialized/ai_security_scan'
    },
    
    // Command Actions
    ACTIONS: {
        GRANT: 'grant',
        REVOKE: 'revoke',
        CHECK: 'check',
        LIST: 'list',
        AI_ANALYZE: 'ai_analyze',
        AI_RECOMMEND: 'ai_recommend',
        BULK_GRANT: 'bulk_grant',
        CLEAR_SUBJECT: 'clear_subject'
    },
    
    // Refresh Intervals (ms)
    REFRESH_INTERVALS: {
        STATUS: 5000,
        METRICS: 10000,
        PERMISSIONS: 15000,
        AUDIT: 10000
    },
    
    // UI Settings
    UI: {
        MAX_AUDIT_ENTRIES: 100,
        MAX_PERMISSIONS_DISPLAY: 50,
        TOAST_DURATION: 3000,
        DATE_LOCALE: 'de-DE'
    },
    
    // Authentication
    AUTH: {
        TOKEN_KEY: 'opena11_auth_token',
        BEARER_PREFIX: 'Bearer '
    }
};

// Freeze configuration
Object.freeze(CONFIG);
Object.freeze(CONFIG.ENDPOINTS);
Object.freeze(CONFIG.SPECIALIZED_ENDPOINTS);
Object.freeze(CONFIG.ACTIONS);
Object.freeze(CONFIG.REFRESH_INTERVALS);
Object.freeze(CONFIG.UI);
Object.freeze(CONFIG.AUTH);