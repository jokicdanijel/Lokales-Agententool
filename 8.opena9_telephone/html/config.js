/* Telephone Agent PAS-6.0 | Configuration | Port 12355 */
const TelephoneConfig = {
  agent: {
    id: "opena9",
    name: "Telephone Agent",
    version: "6.0.0",
    port: 12355,
    baseUrl: "http://127.0.0.1:12355",
    description: "VoIP & Telephony Automation",
  },
  api: {
    endpoints: {
      health: "/health",
      status: "/status",
      // Calls
      makeCall: "/api/call/make",
      endCall: "/api/call/end",
      transferCall: "/api/call/transfer",
      holdCall: "/api/call/hold",
      incomingCalls: "/api/calls/incoming",
      outgoingCalls: "/api/calls/outgoing",
      activeCalls: "/api/calls/active",
      callHistory: "/api/calls/history",
      // Voicemail
      voicemails: "/api/voicemails",
      voicemailPlay: "/api/voicemails/play",
      voicemailDelete: "/api/voicemails/delete",
      // Recordings
      recordings: "/api/recordings",
      recordingStart: "/api/recordings/start",
      recordingStop: "/api/recordings/stop",
      // SMS
      sendSms: "/api/sms/send",
      receivedSms: "/api/sms/received",
      // IVR
      ivrConfig: "/api/ivr/config",
      ivrUpdate: "/api/ivr/update",
      // Contacts
      contacts: "/api/contacts",
      contactAdd: "/api/contacts/add",
      contactDelete: "/api/contacts/delete",
      // Analytics
      analytics: "/api/analytics",
      callStats: "/api/analytics/calls",
    },
    timeout: 30000,
  },
  capabilities: [
    {
      id: "incoming_handler",
      name: "Incoming Handler",
      icon: "📥",
      description: "Auto-answer incoming calls",
      endpoint: "/api/calls/incoming",
    },
    {
      id: "outgoing_dialer",
      name: "Outgoing Dialer",
      icon: "📤",
      description: "Automated outbound calls",
      endpoint: "/api/call/make",
    },
    {
      id: "voicemail_system",
      name: "Voicemail System",
      icon: "📧",
      description: "Record & manage voicemails",
      endpoint: "/api/voicemails",
    },
    {
      id: "ivr_menu",
      name: "IVR Menu",
      icon: "🎛️",
      description: "Interactive voice response",
      endpoint: "/api/ivr/config",
    },
    {
      id: "call_recording",
      name: "Call Recording",
      icon: "🎙️",
      description: "Record all conversations",
      endpoint: "/api/recordings",
    },
    {
      id: "stt_engine",
      name: "Speech-to-Text",
      icon: "🗣️",
      description: "Transcribe conversations",
      endpoint: "/api/stt/transcribe",
    },
    {
      id: "tts_engine",
      name: "Text-to-Speech",
      icon: "🔊",
      description: "AI voice responses",
      endpoint: "/api/tts/speak",
    },
    {
      id: "caller_id",
      name: "Caller ID",
      icon: "🆔",
      description: "Identify incoming callers",
      endpoint: "/api/callerid",
    },
    {
      id: "call_routing",
      name: "Call Routing",
      icon: "🔀",
      description: "Smart call distribution",
      endpoint: "/api/routing",
    },
    {
      id: "conference",
      name: "Conference",
      icon: "👥",
      description: "Multi-party calls",
      endpoint: "/api/conference",
    },
    {
      id: "sms_gateway",
      name: "SMS Gateway",
      icon: "💬",
      description: "Send/receive SMS",
      endpoint: "/api/sms/send",
    },
    {
      id: "ai_assistant",
      name: "AI Assistant",
      icon: "🤖",
      description: "AI-powered responses",
      endpoint: "/api/ai/response",
    },
  ],
  quickActions: [
    { id: "makeCall", icon: "📞", label: "Call", action: "showMakeCallModal" },
    { id: "sendSms", icon: "💬", label: "SMS", action: "showSmsModal" },
    {
      id: "voicemail",
      icon: "📧",
      label: "Voicemail",
      action: "showVoicemails",
    },
    {
      id: "recordings",
      icon: "🎙️",
      label: "Recordings",
      action: "showRecordings",
    },
    { id: "ivrSetup", icon: "🎛️", label: "IVR", action: "showIvrSetup" },
    {
      id: "analytics",
      icon: "📈",
      label: "Analytics",
      action: "showAnalytics",
    },
  ],
  voip: {
    sipServer: "",
    sipUsername: "",
    callerId: "",
    codecs: ["G.711", "G.729", "Opus"],
  },
  recording: {
    autoRecord: true,
    autoTranscribe: false,
    format: "wav",
    storage: "local",
  },
  coordinator: {
    host: "127.0.0.1",
    port: 12344,
    healthEndpoint: "/health",
  },
  ui: {
    theme: "telephone-orange",
    primaryColor: "#f97316",
    refreshInterval: 5000,
  },
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = TelephoneConfig;
}
