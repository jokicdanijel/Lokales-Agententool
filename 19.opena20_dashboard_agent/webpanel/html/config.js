/**
 * opena20 Dashboard Configuration
 * ================================
 */

const CONFIG = {
    // Backend service
    api: {
        baseUrl: window.location.origin,
        timeout: 10000,
    },

    // UI defaults
    ui: {
        refreshInterval: 30000, // 30s
        pageTitle: 'opena20 Dashboard',
    },

    // Paths
    paths: {
        fleetData: '/artifacts/agent_fleet/agent_inventory.json',
        fleetStatus: '/api/fleet/status',
        agentInfo: '/api/info',
    },

    // Logging
    logging: {
        enabled: true,
        level: 'info', // 'debug', 'info', 'warn', 'error'
    },
};

/**
 * Simple logger
 */
const logger = {
    debug: (msg, data) => CONFIG.logging.enabled && console.debug(`[DEBUG] ${msg}`, data || ''),
    info: (msg, data) => CONFIG.logging.enabled && console.log(`[INFO] ${msg}`, data || ''),
    warn: (msg, data) => CONFIG.logging.enabled && console.warn(`[WARN] ${msg}`, data || ''),
    error: (msg, data) => CONFIG.logging.enabled && console.error(`[ERROR] ${msg}`, data || ''),
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CONFIG, logger };
}
