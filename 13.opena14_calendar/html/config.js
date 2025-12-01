const CONFIG = {
    API_BASE_URL: window.location.origin,
    API_PORT: 12359,
    ENDPOINTS: {
        HEALTH: '/health',
        EVENTS_CREATE: '/events/create',
        EVENTS_LIST: '/events/list',
        EVENTS_UPDATE: '/events/update',
        EVENTS_DELETE: '/events/delete',
        EVENTS_TODAY: '/events/today',
        EVENTS_UPCOMING: '/events/upcoming',
        ICAL_IMPORT: '/ical/import',
        ICAL_EXPORT: '/ical/export'
    },
    EVENT_TYPES: ['meeting', 'appointment', 'reminder', 'task', 'birthday'],
    REPEAT_OPTIONS: ['none', 'daily', 'weekly', 'monthly', 'yearly'],
    WEEKDAYS: ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'],
    MONTHS: ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
    REFRESH_INTERVALS: { STATUS: 5000, EVENTS: 30000 },
    UI: { MAX_ACTIVITY_ITEMS: 50, TOAST_DURATION: 3000, DATE_LOCALE: 'de-DE' },
    AUTH: { TOKEN_KEY: 'opena14_auth_token', BEARER_PREFIX: 'Bearer ' }
};
Object.freeze(CONFIG);
