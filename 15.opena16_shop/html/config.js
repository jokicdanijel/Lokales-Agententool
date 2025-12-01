const CONFIG = {
    API_BASE_URL: window.location.origin,
    API_PORT: 12361,
    ENDPOINTS: {
        HEALTH: '/health',
        PRODUCTS_CREATE: '/products/create',
        PRODUCTS_LIST: '/products/list',
        PRODUCTS_UPDATE: '/products/update',
        PRODUCTS_DELETE: '/products/delete',
        ORDERS_CREATE: '/orders/create',
        ORDERS_LIST: '/orders/list',
        INVENTORY_UPDATE: '/inventory/update'
    },
    CATEGORIES: ['electronics', 'clothing', 'home', 'food', 'other'],
    PRODUCT_STATUS: ['active', 'draft', 'archived'],
    ORDER_STATUS: ['pending', 'processing', 'shipped', 'delivered', 'cancelled'],
    CURRENCY: 'EUR',
    REFRESH_INTERVALS: { STATUS: 5000, PRODUCTS: 30000, ORDERS: 15000 },
    UI: { MAX_ACTIVITY_ITEMS: 50, TOAST_DURATION: 3000, DATE_LOCALE: 'de-DE' },
    AUTH: { TOKEN_KEY: 'opena16_auth_token', BEARER_PREFIX: 'Bearer ' }
};
Object.freeze(CONFIG);
