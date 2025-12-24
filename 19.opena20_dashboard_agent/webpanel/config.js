/**
 * PORTIER PAS-6.0 Dashboard Configuration
 * Agent: opena4 - Telegram Mobile Agent
 * Version: 6.0.0
 */

const CONFIG = {
    // Agent Identity
    agent: {
        id: 'opena4',
        name: 'Telegram Mobile Agent',
        version: '6.0.0',
        port: 12348,
        type: 'messaging'
    },

    // API Endpoints
    api: {
        baseUrl: 'http://127.0.0.1:12348',
        timeout: 30000,
        retryAttempts: 3,
        retryDelay: 1000,
        endpoints: {
            // Core Endpoints
            health: '/health',
            status: '/status',
            metrics: '/metrics',
            logs: '/logs',
            config: '/config',

            // Messaging
            sendMessage: '/api/message/send',
            sendBulk: '/api/message/bulk',
            messageHistory: '/api/message/history',

            // Contacts
            contactsList: '/api/contacts/list',
            contactAdd: '/api/contacts/add',
            contactDelete: '/api/contacts/delete',
            contactExport: '/api/contacts/export',
            contactImport: '/api/contacts/import',

            // Media
            sendMedia: '/api/media/send',
            uploadMedia: '/api/media/upload',
            mediaGallery: '/api/media/gallery',

            // AI Reply
            aiGenerate: '/api/ai/generate',
            aiSettings: '/api/ai/settings',
            aiContext: '/api/ai/context',

            // Webhook
            webhookStatus: '/api/webhook/status',
            webhookConfig: '/api/webhook/config',
            webhookEvents: '/api/webhook/events',

            // Analytics
            analyticsOverview: '/api/analytics/overview',
            analyticsMessages: '/api/analytics/messages',
            analyticsExport: '/api/analytics/export',

            // Templates
            templatesList: '/api/templates/list',
            templateSave: '/api/templates/save',
            templateDelete: '/api/templates/delete',

            // System
            restart: '/api/system/restart',
            clearCache: '/api/system/clear-cache'
        }
    },

    // PORTIER Integration
    portier: {
        coordinatorUrl: 'http://127.0.0.1:12344',
        archivatorUrl: 'http://127.0.0.1:12345',
        dashboardUrl: 'http://127.0.0.1:12349',
        option2Flow: true
    },

    // Telegram Bot Configuration
    telegram: {
        apiUrl: 'https://api.telegram.org',
        defaultParseMode: 'HTML',
        maxMessageLength: 4096,
        maxMediaSize: 50 * 1024 * 1024, // 50MB
        supportedMediaTypes: ['photo', 'video', 'document', 'audio', 'voice', 'sticker'],
        rateLimits: {
            messagesPerSecond: 30,
            messagesPerMinute: 20,
            bulkLimit: 100
        }
    },

    // 12 Capabilities
    capabilities: [
        {
            id: 'outgoing_sender',
            name: 'Outgoing Message Sender',
            icon: '📤',
            section: 'messaging',
            enabled: true
        },
        {
            id: 'incoming_listener',
            name: 'Incoming Message Listener',
            icon: '📥',
            section: 'overview',
            enabled: true
        },
        {
            id: 'media_handling',
            name: 'Media Handling',
            icon: '🖼️',
            section: 'media',
            enabled: true
        },
        {
            id: 'contact_manager',
            name: 'Contact Manager',
            icon: '👥',
            section: 'contacts',
            enabled: true
        },
        {
            id: 'ai_reply',
            name: 'AI Reply Assistant',
            icon: '🤖',
            section: 'ai-reply',
            enabled: true
        },
        {
            id: 'rate_limiter',
            name: 'Rate Limit Manager',
            icon: '⏱️',
            section: 'settings',
            enabled: true
        },
        {
            id: 'context_engine',
            name: 'Conversation Context Engine',
            icon: '🧠',
            section: 'ai-reply',
            enabled: true
        },
        {
            id: 'template_engine',
            name: 'Template Message Engine',
            icon: '📝',
            section: 'templates',
            enabled: true
        },
        {
            id: 'webhook_receiver',
            name: 'Webhook Receiver',
            icon: '🔗',
            section: 'webhook',
            enabled: true
        },
        {
            id: 'chat_analytics',
            name: 'Chat Analytics',
            icon: '📊',
            section: 'analytics',
            enabled: true
        },
        {
            id: 'multi_chat_routing',
            name: 'Multi-Chat Routing',
            icon: '🔀',
            section: 'messaging',
            enabled: true
        },
        {
            id: 'error_recovery',
            name: 'Error Recovery & Retry Engine',
            icon: '🔄',
            section: 'settings',
            enabled: true
        }
    ],

    // UI Settings
    ui: {
        refreshInterval: 5000,
        logMaxLines: 500,
        toastDuration: 3000,
        animationsEnabled: true,
        defaultSection: 'overview',
        theme: 'telegram-blue'
    },

    // Default AI Settings
    ai: {
        model: 'gpt-4',
        temperature: 0.7,
        maxTokens: 500,
        systemPrompt: 'Du bist ein freundlicher Telegram-Bot-Assistent.',
        language: 'de'
    },

    // Storage Keys
    storage: {
        bearerToken: 'telegram_bearer_token',
        lastSection: 'telegram_last_section',
        contacts: 'telegram_contacts',
        templates: 'telegram_templates',
        settings: 'telegram_settings'
    }
};

// Freeze config to prevent modifications
Object.freeze(CONFIG);
Object.freeze(CONFIG.agent);
Object.freeze(CONFIG.api);
Object.freeze(CONFIG.api.endpoints);
Object.freeze(CONFIG.portier);
Object.freeze(CONFIG.telegram);
Object.freeze(CONFIG.ui);
Object.freeze(CONFIG.ai);
Object.freeze(CONFIG.storage);

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
