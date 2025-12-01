// 📞 OPENA9 Telephone Dashboard - Configuration
// PORTIER PAS-6.0

const CONFIG = {
    // API Configuration
    API_BASE_URL: window.location.origin,
    API_PORT: 12355,
    
    // Endpoints
    ENDPOINTS: {
        HEALTH: '/health',
        STATUS: '/status',
        COMMAND: '/command',
        SPECIALIZED: '/specialized',
        METRICS: '/metrics',
        CONFIG: '/config',
        LOGS: '/logs'
    },
    
    // Specialized Endpoints
    SPECIALIZED_ENDPOINTS: {
        MAKE_CALL: '/specialized/make_call',
        ANSWER_CALL: '/specialized/answer_call',
        HANGUP: '/specialized/hangup',
        TRANSFER: '/specialized/transfer',
        HOLD: '/specialized/hold',
        ACTIVE_CALLS: '/specialized/active_calls',
        VOICE_GENERATE: '/specialized/voice_generate',
        TRANSCRIBE: '/specialized/transcribe',
        IVR_FLOW: '/specialized/ivr_flow'
    },
    
    // Refresh Intervals (ms)
    REFRESH_INTERVALS: {
        STATUS: 5000,      // 5 seconds
        METRICS: 10000,    // 10 seconds
        ACTIVE_CALLS: 3000, // 3 seconds
        ACTIVITY_LOG: 5000  // 5 seconds
    },
    
    // Twilio Configuration (from environment)
    TWILIO: {
        ENABLED: true,
        DEFAULT_CALLER_ID: '+49123456789'
    },
    
    // Voice Settings
    VOICE: {
        DEFAULT_VOICE: 'alloy',
        DEFAULT_SPEED: 1.0,
        VOICES: ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
    },
    
    // UI Settings
    UI: {
        MAX_ACTIVITY_ITEMS: 50,
        MAX_CALLS_DISPLAY: 20,
        TOAST_DURATION: 3000,
        DATE_LOCALE: 'de-DE'
    },
    
    // Authentication
    AUTH: {
        TOKEN_KEY: 'opena9_auth_token',
        BEARER_PREFIX: 'Bearer '
    }
};

// Freeze configuration
Object.freeze(CONFIG);
Object.freeze(CONFIG.ENDPOINTS);
Object.freeze(CONFIG.SPECIALIZED_ENDPOINTS);
Object.freeze(CONFIG.REFRESH_INTERVALS);
Object.freeze(CONFIG.TWILIO);
Object.freeze(CONFIG.VOICE);
Object.freeze(CONFIG.UI);
Object.freeze(CONFIG.AUTH);