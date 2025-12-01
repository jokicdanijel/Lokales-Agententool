const CONFIG = {
    API_BASE_URL: window.location.origin,
    API_PORT: 12358,
    ENDPOINTS: { HEALTH: '/health', STATUS: '/status', COMMAND: '/command', SPECIALIZED: '/specialized', METRICS: '/metrics', QUEUE: '/queue' },
    PLATFORMS: {
        linkedin: { name: 'LinkedIn', color: '#0A66C2', charLimit: 3000 },
        x: { name: 'X', color: '#1DA1F2', charLimit: 280 },
        facebook: { name: 'Facebook', color: '#1877F2', charLimit: 63206 },
        instagram: { name: 'Instagram', color: '#E4405F', charLimit: 2200 }
    },
    REFRESH_INTERVALS: { STATUS: 5000, METRICS: 10000, QUEUE: 10000 },
    UI: { MAX_ACTIVITY_ITEMS: 30, TOAST_DURATION: 3000, DATE_LOCALE: 'de-DE' },
    AUTH: { TOKEN_KEY: 'opena12_auth_token', BEARER_PREFIX: 'Bearer ' }
};
Object.freeze(CONFIG);
