/* WhatsApp Agent PAS-6.0 | Configuration | Port 12352 */
const WhatsAppConfig = {
  agent: {
    id: "opena8",
    name: "WhatsApp Agent",
    version: "6.0.0",
    port: 12352,
    baseUrl: "http://127.0.0.1:12352",
    description: "Business & Personal WhatsApp Automation",
  },
  api: {
    endpoints: {
      health: "/health",
      status: "/status",
      // Messaging
      sendMessage: "/api/send",
      sendMedia: "/api/media/send",
      sendTemplate: "/api/template/send",
      receiveMessages: "/api/messages/receive",
      markRead: "/api/messages/read",
      // Contacts
      contacts: "/api/contacts",
      contactInfo: "/api/contacts/info",
      syncContacts: "/api/contacts/sync",
      // Conversations
      conversations: "/api/conversations",
      conversationHistory: "/api/conversations/history",
      deleteConversation: "/api/conversations/delete",
      // Media
      uploadMedia: "/api/media/upload",
      downloadMedia: "/api/media/download",
      mediaGallery: "/api/media/gallery",
      // Templates
      templates: "/api/templates",
      createTemplate: "/api/templates/create",
      updateTemplate: "/api/templates/update",
      // Business
      businessProfile: "/api/business/profile",
      catalog: "/api/business/catalog",
      labels: "/api/business/labels",
      // Webhooks
      webhooks: "/api/webhooks",
      webhookRegister: "/api/webhooks/register",
      webhookDelete: "/api/webhooks/delete",
      // Analytics
      analytics: "/api/analytics",
      messageStats: "/api/analytics/messages",
      engagementStats: "/api/analytics/engagement",
      // Account
      accountStatus: "/api/account/status",
      qrCode: "/api/account/qr",
      logout: "/api/account/logout",
    },
    timeout: 30000,
    retries: 3,
  },
  capabilities: [
    {
      id: "incoming_messages",
      name: "Incoming Messages",
      icon: "📥",
      description: "Receive & process WhatsApp messages",
      endpoint: "/api/messages/receive",
    },
    {
      id: "outgoing_messages",
      name: "Outgoing Messages",
      icon: "📤",
      description: "Send text messages to contacts",
      endpoint: "/api/send",
    },
    {
      id: "media_messages",
      name: "Media Messages",
      icon: "📷",
      description: "Send/receive images, videos, documents",
      endpoint: "/api/media/send",
    },
    {
      id: "contact_manager",
      name: "Contact Manager",
      icon: "👥",
      description: "Manage WhatsApp contacts",
      endpoint: "/api/contacts",
    },
    {
      id: "template_api",
      name: "Template API",
      icon: "📋",
      description: "Business message templates",
      endpoint: "/api/templates",
    },
    {
      id: "rate_control",
      name: "Rate Control",
      icon: "⚡",
      description: "Smart rate limiting & queuing",
      endpoint: "/api/rate/status",
    },
    {
      id: "account_health",
      name: "Account Health",
      icon: "💚",
      description: "Monitor connection & QR status",
      endpoint: "/api/account/status",
    },
    {
      id: "webhook_listener",
      name: "Webhook Listener",
      icon: "🎣",
      description: "Real-time message webhooks",
      endpoint: "/api/webhooks",
    },
    {
      id: "conversation_history",
      name: "Conversation History",
      icon: "📜",
      description: "Full chat history access",
      endpoint: "/api/conversations/history",
    },
    {
      id: "quick_replies",
      name: "Quick Replies",
      icon: "⚡",
      description: "Predefined response automation",
      endpoint: "/api/quick-replies",
    },
  ],
  quickActions: [
    {
      id: "send_message",
      icon: "💬",
      label: "Send",
      action: "showComposeModal",
    },
    { id: "media", icon: "📷", label: "Media", action: "showMediaModal" },
    {
      id: "template",
      icon: "📋",
      label: "Template",
      action: "showTemplateModal",
    },
    {
      id: "broadcast",
      icon: "📢",
      label: "Broadcast",
      action: "showBroadcastModal",
    },
    { id: "sync", icon: "🔄", label: "Sync", action: "syncContacts" },
    { id: "qr_code", icon: "📱", label: "QR Code", action: "showQRCode" },
  ],
  webhookEvents: [
    "messages.upsert",
    "messages.update",
    "messages.reaction",
    "chats.upsert",
    "chats.update",
    "contacts.update",
    "presence.update",
    "groups.update",
    "call.incoming",
    "connection.update",
  ],
  templates: {
    categories: ["Marketing", "Utility", "Authentication"],
    languages: ["de", "en", "es", "fr", "it", "pt"],
  },
  analytics: {
    metrics: [
      "messages_sent",
      "messages_received",
      "delivery_rate",
      "read_rate",
      "response_time",
    ],
    periods: ["today", "week", "month", "year"],
  },
  coordinator: {
    host: "127.0.0.1",
    port: 12344,
    healthEndpoint: "/health",
  },
  ui: {
    theme: "whatsapp-green",
    primaryColor: "#25d366",
    refreshInterval: 5000,
    messageLimit: 50,
    contactsPerPage: 20,
  },
  mediaTypes: {
    image: [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    video: [".mp4", ".3gp", ".mov"],
    audio: [".mp3", ".ogg", ".opus", ".m4a"],
    document: [
      ".pdf",
      ".doc",
      ".docx",
      ".xls",
      ".xlsx",
      ".ppt",
      ".pptx",
      ".txt",
    ],
  },
  rateLimits: {
    messagesPerMinute: 60,
    mediaPerMinute: 30,
    templatePerMinute: 100,
  },
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = WhatsAppConfig;
}
