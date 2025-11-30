const CONFIG = {
    API_BASE_URL: window.location.origin,
    API_PORT: 12358,
    ENDPOINTS: {
        HEALTH: '/health',
        PROFILES_CREATE: '/profiles/create',
        PROFILES_LIST: '/profiles/list',
        PROFILES_DELETE: '/profiles/delete',
        CAMPAIGNS_CREATE: '/campaigns/create',
        CAMPAIGNS_LIST: '/campaigns/list',
        MATCH: '/match',
        METRICS: '/metrics'
    },
    PLATFORMS: ['instagram', 'tiktok', 'youtube', 'x', 'linkedin', 'facebook'],
    NICHES: ['fashion', 'tech', 'lifestyle', 'fitness', 'food', 'travel', 'gaming', 'beauty'],
    REFRESH_INTERVALS: { STATUS: 5000, METRICS: 15000, PROFILES: 30000 },
    UI: { MAX_ACTIVITY_ITEMS: 50, TOAST_DURATION: 3000, DATE_LOCALE: 'de-DE' },
    AUTH: { TOKEN_KEY: 'opena13_auth_token', BEARER_PREFIX: 'Bearer ' }
};
Object.freeze(CONFIG);
