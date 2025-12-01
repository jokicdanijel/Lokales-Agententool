// Homepage Creator Agent Configuration | PAS-6.0
const CONFIG = {
    agent: {
        id: 'opena17',
        name: 'Homepage Creator Agent',
        kuerzel: 'hpcreatep',
        port: 12360,
        version: 'PAS-6.0'
    },
    api: {
        baseUrl: 'http://127.0.0.1:12360',
        timeout: 30000
    },
    dashboard: {
        port: 12349
    },
    coordinator: {
        port: 12344
    },
    archivator: {
        port: 12345
    }
};

// Export für Module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
