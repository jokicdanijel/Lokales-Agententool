/**
 * OPENA3 - OpenWebUI Terminal Agent | Configuration
 * PAS-6.0 Enterprise Dashboard
 * Port: 12347
 */

const CONFIG = {
    // Agent Info
    agent: {
        id: 'opena3',
        name: 'OpenWebUI Terminal Agent',
        shortName: 'openwebuip',
        port: 12347,
        version: '6.0.0',
        type: 'ai_chat'
    },
    
    // API Endpoints
    api: {
        baseUrl: 'http://127.0.0.1:12347',
        openwebui: 'http://127.0.0.1:8080',
        endpoints: {
            health: '/health',
            status: '/status',
            command: '/command',
            invoke: '/invoke',
            metrics: '/metrics',
            logs: '/logs',
            config: '/config',
            // Chat Endpoints
            chat: '/api/chat',
            chatComplete: '/api/chat/completions',
            chatHistory: '/api/chat/history',
            // Model Endpoints
            models: '/api/models',
            modelInfo: '/api/models/{id}',
            // Tool Endpoints
            tools: '/api/tools',
            toolRegistry: '/api/tools/registry',
            // File Endpoints
            files: '/api/files',
            fileUpload: '/api/files/upload',
            // SSE
            sse: '/sse/events',
            // Option-2
            option2: '/api/option2_flow'
        }
    },
    
    // PORTIER Integration
    portier: {
        opena1: 'http://127.0.0.1:12344',
        opena2: 'http://127.0.0.1:12345',
        dashboard: 'http://127.0.0.1:12349',
        kordp: 'http://127.0.0.1:12346'
    },
    
    // 12 Core Capabilities
    capabilities: [
        {
            id: 'chat_window',
            name: 'Chat Window',
            icon: '💬',
            description: 'Interactive AI Chat Interface',
            endpoint: '/api/chat'
        },
        {
            id: 'model_selector',
            name: 'Model Selector',
            icon: '🤖',
            description: 'Multi-Model Selection & Routing',
            endpoint: '/api/models'
        },
        {
            id: 'message_history',
            name: 'Message History',
            icon: '📜',
            description: 'Conversation History & Context',
            endpoint: '/api/chat/history'
        },
        {
            id: 'sse_stream',
            name: 'SSE Live Stream',
            icon: '📡',
            description: 'Real-time Server-Sent Events',
            endpoint: '/sse/events'
        },
        {
            id: 'multi_model',
            name: 'Multi-Model Routing',
            icon: '🔀',
            description: 'Route to different AI models',
            endpoint: '/api/models/route'
        },
        {
            id: 'file_upload',
            name: 'File Upload',
            icon: '📁',
            description: 'Upload documents for analysis',
            endpoint: '/api/files/upload'
        },
        {
            id: 'native_commands',
            name: 'Native Commands',
            icon: '⚡',
            description: 'Execute terminal commands',
            endpoint: '/command'
        },
        {
            id: 'option2_flow',
            name: 'Option-2-Flow',
            icon: '🔄',
            description: 'PORTIER compliant routing',
            endpoint: '/api/option2_flow'
        },
        {
            id: 'tool_registry',
            name: 'Tool Registry',
            icon: '🔧',
            description: 'Manage AI tools & functions',
            endpoint: '/api/tools/registry'
        },
        {
            id: 'ui_notifications',
            name: 'UI Notifications',
            icon: '🔔',
            description: 'Real-time alerts & notifications',
            endpoint: '/api/notifications'
        },
        {
            id: 'prompt_templates',
            name: 'Prompt Templates',
            icon: '📝',
            description: 'Pre-built prompt library',
            endpoint: '/api/templates'
        },
        {
            id: 'ai_personas',
            name: 'AI Personas',
            icon: '🎭',
            description: 'Custom AI personality profiles',
            endpoint: '/api/personas'
        }
    ],
    
    // Available Models
    models: [
        { id: 'gpt-4', name: 'GPT-4', provider: 'openai' },
        { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'openai' },
        { id: 'claude-3-opus', name: 'Claude 3 Opus', provider: 'anthropic' },
        { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet', provider: 'anthropic' },
        { id: 'llama-3-70b', name: 'Llama 3 70B', provider: 'meta' },
        { id: 'mistral-large', name: 'Mistral Large', provider: 'mistral' }
    ],
    
    // Default Settings
    settings: {
        autoScroll: true,
        streamResponses: true,
        showTimestamps: true,
        maxHistoryItems: 50,
        refreshInterval: 5000,
        defaultModel: 'gpt-4',
        theme: 'cyan'
    },
    
    // Auth
    auth: {
        tokenKey: 'opena3_bearer_token',
        defaultToken: ''
    }
};

// Freeze config
Object.freeze(CONFIG);
