// 🔥 Browser Agent 6.0 Configuration
const CONFIG = {
  BASE_URL: "http://127.0.0.1:12350",
  STREAM_URL: "ws://127.0.0.1:12350/stream",
  DOM_URL: "http://127.0.0.1:12350/dom",
  WEBRTC_URL: "http://127.0.0.1:12350/stream",
  RECORDING_URL: "http://127.0.0.1:12350/record",
  TIMELINE_URL: "http://127.0.0.1:12350/timeline",

  // Authentication
  BEARER_TOKEN_KEY: "portier_browser_token",

  // Stream Settings
  STREAM_CONFIG: {
    video: {
      width: { ideal: 1920 },
      height: { ideal: 1080 },
      frameRate: { ideal: 30 },
    },
    audio: false,
  },

  // Polling Intervals (ms)
  STATUS_UPDATE_INTERVAL: 5000,
  DOM_REFRESH_INTERVAL: 2000,
  TIMELINE_UPDATE_INTERVAL: 10000,

  // UI Settings
  MAX_LOG_ENTRIES: 100,
  AUTO_SCROLL_LOGS: true,
  ANIMATION_DURATION: 300,
};
