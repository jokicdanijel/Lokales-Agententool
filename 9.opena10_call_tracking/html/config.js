/* Call Tracking Agent PAS-6.0 | Configuration | Port 12356 */
const CallTrackingConfig = {
    agent: {
        id: 'opena10',
        name: 'Call Tracking Agent',
        version: '6.0.0',
        port: 12356,
        baseUrl: 'http://127.0.0.1:12356',
        description: 'Analytics & Attribution System'
    },
    api: {
        endpoints: {
            health: '/health',
            status: '/status',
            // Calls
            calls: '/api/calls',
            callDetail: '/api/calls/detail',
            liveFeed: '/api/calls/live',
            // Sources
            sources: '/api/sources',
            sourceAdd: '/api/sources/add',
            sourceUpdate: '/api/sources/update',
            sourceDelete: '/api/sources/delete',
            // Campaigns
            campaigns: '/api/campaigns',
            campaignCreate: '/api/campaigns/create',
            campaignUpdate: '/api/campaigns/update',
            // Numbers
            numbers: '/api/numbers',
            numberAdd: '/api/numbers/add',
            numberPool: '/api/numbers/pool',
            // Attribution
            attribution: '/api/attribution',
            attributionModel: '/api/attribution/model',
            // Analytics
            analytics: '/api/analytics',
            callStats: '/api/analytics/calls',
            sourceStats: '/api/analytics/sources',
            // Reports
            reports: '/api/reports',
            reportGenerate: '/api/reports/generate',
            reportSchedule: '/api/reports/schedule',
            // Export
            export: '/api/export'
        },
        timeout: 30000
    },
    capabilities: [
        { id: 'call_logging', name: 'Call Logging', icon: '📝', description: 'Track all call events', endpoint: '/api/calls' },
        { id: 'source_tracking', name: 'Source Tracking', icon: '📡', description: 'Identify call origins', endpoint: '/api/sources' },
        { id: 'campaign_tracking', name: 'Campaign Tracking', icon: '🎯', description: 'UTM & campaign attribution', endpoint: '/api/campaigns' },
        { id: 'dynamic_numbers', name: 'Dynamic Numbers', icon: '🔢', description: 'Per-source phone numbers', endpoint: '/api/numbers' },
        { id: 'conversion_tracking', name: 'Conversion Tracking', icon: '💰', description: 'Call-to-sale attribution', endpoint: '/api/conversions' },
        { id: 'keyword_tracking', name: 'Keyword Tracking', icon: '🔑', description: 'PPC keyword attribution', endpoint: '/api/keywords' },
        { id: 'roi_analysis', name: 'ROI Analysis', icon: '📈', description: 'Marketing ROI calculation', endpoint: '/api/roi' },
        { id: 'webhook_integration', name: 'Webhook Integration', icon: '🔗', description: 'Real-time data push', endpoint: '/api/webhooks' },
        { id: 'crm_sync', name: 'CRM Sync', icon: '🔄', description: 'Auto-sync to CRM', endpoint: '/api/crm/sync' },
        { id: 'custom_reports', name: 'Custom Reports', icon: '📋', description: 'Scheduled reporting', endpoint: '/api/reports' }
    ],
    quickActions: [
        { id: 'viewTracking', icon: '🔍', label: 'Tracking', action: 'viewTracking' },
        { id: 'addSource', icon: '➕', label: 'Add Source', action: 'showAddSourceModal' },
        { id: 'createCampaign', icon: '🎯', label: 'Campaign', action: 'showCreateCampaignModal' },
        { id: 'viewReports', icon: '📋', label: 'Reports', action: 'viewReports' },
        { id: 'exportData', icon: '📤', label: 'Export', action: 'exportData' },
        { id: 'viewAnalytics', icon: '📈', label: 'Analytics', action: 'viewAnalytics' }
    ],
    attribution: {
        models: ['first', 'last', 'linear', 'position'],
        defaultWindow: 30
    },
    sources: {
        types: ['google_ads', 'facebook', 'organic', 'direct', 'referral', 'email', 'other']
    },
    reports: {
        templates: ['daily', 'weekly', 'campaign', 'roi'],
        formats: ['pdf', 'csv', 'xlsx']
    },
    coordinator: {
        host: '127.0.0.1',
        port: 12344,
        healthEndpoint: '/health'
    },
    ui: {
        theme: 'tracking-indigo',
        primaryColor: '#6366f1',
        refreshInterval: 10000
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = CallTrackingConfig;
}
