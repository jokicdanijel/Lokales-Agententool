// Telegram Mobile Agent Configuration
const CONFIG = {
  API_BASE: "http://localhost:12348",
  TELEGRAM_TOKEN: localStorage.getItem("telegram_token") || "",
  UPDATE_INTERVAL: 5000, // 5 seconds
  AUTO_REFRESH: true,
  PORTIER_AGENTS: {
    opena1: "http://127.0.0.1:12344", // Koordinator
    opena2: "http://127.0.0.1:12345", // Archivator
    opena3: "http://127.0.0.1:12347", // OpenWebUI Terminal
    opena4: "http://127.0.0.1:12348", // Telegram Agent (this)
  },
};

// Speichere Config
function saveConfig() {
  localStorage.setItem("telegram_config", JSON.stringify(CONFIG));
}

// Lade Config
function loadConfig() {
  const saved = localStorage.getItem("telegram_config");
  if (saved) {
    Object.assign(CONFIG, JSON.parse(saved));
  }
}

loadConfig();
