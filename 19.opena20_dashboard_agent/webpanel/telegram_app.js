// Telegram Mobile Agent Application
class TelegramAgent {
  constructor() {
    this.statusInterval = null;
    this.init();
  }

  init() {
    console.log("🚀 Telegram Agent initializing...");
    this.setupNavigation();
    this.startStatusMonitoring();
    this.checkConnection();
  }

  // Navigation
  setupNavigation() {
    const navBtns = document.querySelectorAll(".nav-btn");
    navBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        const section = btn.dataset.section;
        this.showSection(section);

        navBtns.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
      });
    });
  }

  showSection(sectionId) {
    const sections = document.querySelectorAll(".section");
    sections.forEach((section) => {
      section.classList.remove("active");
    });

    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
      targetSection.classList.add("active");
    }
  }

  // Status Monitoring
  startStatusMonitoring() {
    this.updateStatus();
    this.statusInterval = setInterval(
      () => this.updateStatus(),
      CONFIG.UPDATE_INTERVAL,
    );
  }

  async updateStatus() {
    try {
      const response = await fetch(`${CONFIG.API_BASE}/api/status`);
      const data = await response.json();

      if (data.success) {
        this.updateStatusBadge(data.services?.telegram_bot === "online");
        this.updateBotInfo(data);
        this.updateMetrics(data);
      }

      this.updateLastUpdate();
    } catch (error) {
      console.error("Status update failed:", error);
      this.updateStatusBadge(false);
    }
  }

  updateStatusBadge(online) {
    const badge = document.getElementById("statusBadge");
    if (online) {
      badge.classList.remove("offline");
      badge.querySelector(".status-text").textContent = "Online";
    } else {
      badge.classList.add("offline");
      badge.querySelector(".status-text").textContent = "Offline";
    }
  }

  updateBotInfo(data) {
    if (data.services) {
      document.getElementById("botStatus").textContent =
        data.services.telegram_bot || "unknown";
    }
    if (data.system) {
      document.getElementById("botCPU").textContent =
        `${data.system.cpu_percent}%`;
      document.getElementById("botRAM").textContent =
        `${data.system.memory_percent}%`;
      if (data.system.uptime_hours) {
        document.getElementById("botUptime").textContent =
          `${data.system.uptime_hours}h`;
      }
    }
  }

  updateMetrics(data) {
    // Update metrics - mock data for now
    document.getElementById("messagesSent").textContent = Math.floor(
      Math.random() * 1000,
    );
    document.getElementById("messagesReceived").textContent = Math.floor(
      Math.random() * 500,
    );
    document.getElementById("activeChats").textContent = Math.floor(
      Math.random() * 50,
    );
    document.getElementById("responseTime").textContent =
      `${Math.floor(Math.random() * 100)}ms`;
  }

  updateLastUpdate() {
    const now = new Date();
    const time = now.toLocaleTimeString("de-DE");
    document.getElementById("lastUpdate").textContent =
      `Letzte Aktualisierung: ${time}`;
  }

  // Bot Control
  async startBot() {
    this.showToast("info", "Bot wird gestartet...");
    try {
      const response = await fetch(`${CONFIG.API_BASE}/api/bot/start`, {
        method: "POST",
      });
      const data = await response.json();

      if (data.success) {
        this.showToast("success", "✅ Bot erfolgreich gestartet!");
        setTimeout(() => this.updateStatus(), 2000);
      } else {
        this.showToast("error", `❌ Fehler: ${data.error}`);
      }
    } catch (error) {
      this.showToast("error", `❌ Verbindungsfehler: ${error.message}`);
    }
  }

  async stopBot() {
    this.showToast("warning", "Bot wird gestoppt...");
    try {
      const response = await fetch(`${CONFIG.API_BASE}/api/bot/stop`, {
        method: "POST",
      });
      const data = await response.json();

      if (data.success) {
        this.showToast("success", "✅ Bot gestoppt!");
        setTimeout(() => this.updateStatus(), 2000);
      } else {
        this.showToast("error", `❌ Fehler: ${data.error}`);
      }
    } catch (error) {
      this.showToast("error", `❌ Verbindungsfehler: ${error.message}`);
    }
  }

  async restartBot() {
    this.showToast("info", "Bot wird neugestartet...");
    try {
      const response = await fetch(`${CONFIG.API_BASE}/api/bot/restart`, {
        method: "POST",
      });
      const data = await response.json();

      if (data.success) {
        this.showToast("success", "✅ Bot neugestartet!");
        setTimeout(() => this.updateStatus(), 3000);
      } else {
        this.showToast("error", `❌ Fehler: ${data.error}`);
      }
    } catch (error) {
      this.showToast("error", `❌ Verbindungsfehler: ${error.message}`);
    }
  }

  async getBotDetails() {
    this.showToast("info", "Lade Details...");
    try {
      const response = await fetch(`${CONFIG.API_BASE}/api/status`);
      const data = await response.json();

      if (data.success) {
        const details = JSON.stringify(data, null, 2);
        this.showToast("success", "✅ Details geladen!");
        console.log("Bot Details:", data);

        // Zeige Details in Alert (später durch Modal ersetzen)
        alert(`🤖 Bot Details:\n\n${details}`);
      } else {
        this.showToast("error", `❌ Fehler beim Laden der Details`);
      }
    } catch (error) {
      this.showToast("error", `❌ Verbindungsfehler: ${error.message}`);
    }
  }

  // Messaging
  async sendMessage() {
    const chatId = document.getElementById("msgChatId").value;
    const text = document.getElementById("msgText").value;

    if (!chatId || !text) {
      this.showToast("warning", "⚠️ Bitte Chat ID und Nachricht eingeben");
      return;
    }

    this.showToast("info", "Nachricht wird gesendet...");

    try {
      const response = await fetch(`${CONFIG.API_BASE}/api/chat/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: `Chat ${chatId}: ${text}`,
          user_id: chatId,
        }),
      });

      const data = await response.json();

      if (data.success) {
        this.showToast("success", "✅ Nachricht gesendet!");
        document.getElementById("msgText").value = "";
      } else {
        this.showToast("error", "❌ Fehler beim Senden");
      }
    } catch (error) {
      this.showToast("error", `❌ Verbindungsfehler: ${error.message}`);
    }
  }

  // Quick Actions
  async sendTestMessage() {
    this.showToast("info", "Teste Nachricht...");
    this.showToast("success", "✅ Test-Funktion - bitte Chat ID konfigurieren");
  }

  async checkBotStatus() {
    await this.updateStatus();
    this.showToast("success", "✅ Status aktualisiert!");
  }

  async getUpdates() {
    this.showToast("info", "📥 Rufe Updates ab...");
    try {
      const response = await fetch(`${CONFIG.API_BASE}/api/workflows`);
      const data = await response.json();

      if (data.success) {
        this.showToast(
          "success",
          `✅ ${data.summary?.total || 0} Workflows geladen`,
        );
      }
    } catch (error) {
      this.showToast("error", `❌ Fehler: ${error.message}`);
    }
  }

  async viewWebhookInfo() {
    this.showSection("webhook");
    this.showToast("info", "🔗 Webhook-Sektion geöffnet");
  }

  // Settings
  async saveSettings() {
    const token = document.getElementById("botToken").value;
    const url = document.getElementById("agentUrl").value;

    if (token) {
      CONFIG.TELEGRAM_TOKEN = token;
      localStorage.setItem("telegram_token", token);
    }

    if (url) {
      CONFIG.API_BASE = url;
    }

    saveConfig();
    this.showToast("success", "✅ Einstellungen gespeichert!");
  }

  async testConnection() {
    this.showToast("info", "Teste Verbindung...");
    try {
      const response = await fetch(`${CONFIG.API_BASE}/api/health`);
      const data = await response.json();

      if (data.status === "healthy") {
        this.showToast("success", "✅ Verbindung erfolgreich!");
      } else {
        this.showToast("warning", "⚠️ Backend antwortet, aber Status unklar");
      }
    } catch (error) {
      this.showToast("error", `❌ Verbindung fehlgeschlagen: ${error.message}`);
    }
  }

  async checkConnection() {
    try {
      const response = await fetch(`${CONFIG.API_BASE}/api/health`);
      const data = await response.json();

      if (data.status === "healthy") {
        console.log("✅ Backend verbunden");
      }
    } catch (error) {
      console.error("❌ Backend nicht erreichbar:", error);
    }
  }

  // Refresh All
  async refreshAll() {
    this.showToast("info", "🔄 Aktualisiere...");
    await this.updateStatus();
    this.showToast("success", "✅ Daten aktualisiert!");
  }

  // Toast Notifications
  showToast(type, message) {
    const container = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = "slideOut 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }
}

// Initialize App
const app = new TelegramAgent();

// Cleanup on page unload
window.addEventListener("beforeunload", () => {
  if (app.statusInterval) {
    clearInterval(app.statusInterval);
  }
});
