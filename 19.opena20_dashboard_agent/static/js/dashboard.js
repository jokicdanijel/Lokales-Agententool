// ELION Dashboard - Main JavaScript
const AGENTS_CONFIG = [
  {
    id: "opena1",
    name: "Koordinator",
    kuerzel: "kordp",
    port: 12344,
    icon: "🎯",
    color: "blue",
  },
  {
    id: "opena2",
    name: "Archivator",
    kuerzel: "archivp",
    port: 12345,
    icon: "📦",
    color: "purple",
  },
  {
    id: "opena3",
    name: "OpenWebUI Terminal",
    kuerzel: "owuip",
    port: 12347,
    icon: "🖥️",
    color: "cyan",
  },
  {
    id: "opena4",
    name: "Telegram Agent",
    kuerzel: "telep",
    port: 12348,
    icon: "📱",
    color: "blue",
  },
  {
    id: "opena5",
    name: "VS Code Agent",
    kuerzel: "vscop",
    port: 12351,
    icon: "💻",
    color: "blue",
  },
  {
    id: "opena6",
    name: "Browser Agent",
    kuerzel: "browsep",
    port: 12352,
    icon: "🌐",
    color: "orange",
  },
  {
    id: "opena7",
    name: "Email Agent",
    kuerzel: "emailp",
    port: 12353,
    icon: "📧",
    color: "red",
  },
  {
    id: "opena8",
    name: "WhatsApp Agent",
    kuerzel: "whatsappp",
    port: 12354,
    icon: "💬",
    color: "green",
  },
  {
    id: "opena9",
    name: "Telefonie Agent",
    kuerzel: "telephonep",
    port: 12355,
    icon: "📞",
    color: "blue",
  },
  {
    id: "opena10",
    name: "Call Tracking Agent",
    kuerzel: "calltrackp",
    port: 12356,
    icon: "📊",
    color: "purple",
  },
  {
    id: "opena11",
    name: "Unlock Agent",
    kuerzel: "unlockp",
    port: 12357,
    icon: "🔓",
    color: "yellow",
  },
  {
    id: "opena12",
    name: "Social Media Agent",
    kuerzel: "smp",
    port: 12358,
    icon: "📣",
    color: "pink",
  },
  {
    id: "opena13",
    name: "Influencer Agent",
    kuerzel: "influp",
    port: 12359,
    icon: "⭐",
    color: "purple",
  },
  {
    id: "opena14",
    name: "Calendar Agent",
    kuerzel: "calp",
    port: 12360,
    icon: "📅",
    color: "green",
  },
  {
    id: "opena15",
    name: "HTML Creator",
    kuerzel: "htmlp",
    port: 12361,
    icon: "🎨",
    color: "pink",
  },
  {
    id: "opena16",
    name: "Shop Agent",
    kuerzel: "shopp",
    port: 12362,
    icon: "🛒",
    color: "orange",
  },
  {
    id: "opena17",
    name: "Homepage Creator",
    kuerzel: "hpcreatep",
    port: 12363,
    icon: "🏠",
    color: "blue",
  },
  {
    id: "opena18",
    name: "CRM Agent",
    kuerzel: "crmp",
    port: 12364,
    icon: "👥",
    color: "cyan",
  },
  {
    id: "opena19",
    name: "Stocks & Crypto",
    kuerzel: "stockcryptop",
    port: 12365,
    icon: "📈",
    color: "green",
  },
  {
    id: "opena20",
    name: "Dashboard",
    kuerzel: "dashp",
    port: 12349,
    icon: "🚀",
    color: "purple",
  },
];

class ELIONDashboard {
  constructor() {
    this.agents = new Map();
    this.activities = [];
    this.startTime = Date.now();
    this.init();
  }

  async init() {
    this.renderSidebar();
    this.bindEvents();
    await this.refreshAllAgents();
    this.startAutoRefresh();
    this.updateClock();
    setInterval(() => this.updateClock(), 1000);
  }

  renderSidebar() {
    const nav = document.getElementById("agents-nav");
    if (!nav) return;
    nav.innerHTML = AGENTS_CONFIG.map(
      (agent) => `
            <a href="/agent/${agent.id}" class="nav-item" data-agent="${agent.id}">
                <span>${agent.icon}</span>
                <span>${agent.name}</span>
                <span class="status-dot unknown" id="nav-status-${agent.id}"></span>
            </a>
        `,
    ).join("");
  }

  bindEvents() {
    document
      .getElementById("refresh-btn")
      ?.addEventListener("click", () => this.refreshAllAgents());
    document
      .getElementById("start-all-btn")
      ?.addEventListener("click", () => this.startAllAgents());
    document
      .getElementById("stop-all-btn")
      ?.addEventListener("click", () => this.stopAllAgents());
    document
      .getElementById("api-send-btn")
      ?.addEventListener("click", () => this.sendApiRequest());
    document
      .getElementById("api-endpoint")
      ?.addEventListener("keypress", (e) => {
        if (e.key === "Enter") this.sendApiRequest();
      });
  }

  async checkAgentHealth(agent) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 3000);
      const res = await fetch(`http://127.0.0.1:${agent.port}/health`, {
        signal: controller.signal,
      });
      clearTimeout(timeout);
      if (res.ok) {
        const data = await res.json();
        return {
          ...agent,
          online: true,
          data,
          uptime: data.uptime_seconds || 0,
        };
      }
    } catch (e) {}
    return { ...agent, online: false, data: null, uptime: 0 };
  }

  async refreshAllAgents() {
    const results = await Promise.all(
      AGENTS_CONFIG.map((a) => this.checkAgentHealth(a)),
    );
    results.forEach((r) => this.agents.set(r.id, r));
    this.updateStats();
    this.renderAgentsGrid();
    this.updateSidebarStatus();
    this.addActivity("info", "Status aller Agenten aktualisiert");
  }

  updateStats() {
    const online = [...this.agents.values()].filter((a) => a.online).length;
    const offline = this.agents.size - online;
    document.getElementById("stat-total").textContent = this.agents.size;
    document.getElementById("stat-online").textContent = online;
    document.getElementById("stat-offline").textContent = offline;
  }

  updateSidebarStatus() {
    this.agents.forEach((agent, id) => {
      const dot = document.getElementById(`nav-status-${id}`);
      if (dot) {
        dot.className = `status-dot ${agent.online ? "online" : "offline"}`;
      }
    });
  }

  renderAgentsGrid() {
    const grid = document.getElementById("agents-grid");
    if (!grid) return;
    grid.innerHTML = [...this.agents.values()]
      .map(
        (agent) => `
            <div class="agent-card ${agent.online ? "online" : "offline"}" data-agent="${agent.id}">
                <div class="agent-header">
                    <div class="agent-info">
                        <h3>${agent.icon} ${agent.name}</h3>
                        <div class="agent-id">ID: ${agent.id} | Kürzel: ${agent.kuerzel}</div>
                    </div>
                    <span class="agent-status ${agent.online ? "online" : "offline"}">
                        <span>●</span> ${agent.online ? "Online" : "Offline"}
                    </span>
                </div>
                <div class="agent-meta">
                    <div class="meta-item">
                        <span class="label">Port</span>
                        <span class="value">${agent.port}</span>
                    </div>
                    <div class="meta-item">
                        <span class="label">Uptime</span>
                        <span class="value">${this.formatUptime(agent.uptime)}</span>
                    </div>
                </div>
                <div class="agent-actions">
                    <button class="btn btn-outline" onclick="dashboard.openAgentPage('${agent.id}')">📊 Details</button>
                    <button class="btn btn-outline" onclick="dashboard.pingAgent('${agent.id}')">🔍 Health</button>
                    ${
                      agent.online
                        ? `<button class="btn btn-danger" onclick="dashboard.stopAgent('${agent.id}')">⏹ Stop</button>`
                        : `<button class="btn btn-success" onclick="dashboard.startAgent('${agent.id}')">▶ Start</button>`
                    }
                </div>
            </div>
        `,
      )
      .join("");
  }

  formatUptime(seconds) {
    if (!seconds) return "--:--:--";
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  }

  async pingAgent(agentId) {
    const agent = AGENTS_CONFIG.find((a) => a.id === agentId);
    if (!agent) return;
    try {
      const res = await fetch(`http://127.0.0.1:${agent.port}/health`);
      const data = await res.json();
      this.toast(
        `${agent.name}: ${res.ok ? "Online ✅" : "Fehler"}`,
        res.ok ? "success" : "error",
      );
      this.addActivity(
        res.ok ? "success" : "error",
        `Health-Check: ${agent.name}`,
      );
      document.getElementById("api-response").textContent = JSON.stringify(
        data,
        null,
        2,
      );
    } catch (e) {
      this.toast(`${agent.name}: Nicht erreichbar ❌`, "error");
      this.addActivity("error", `Health-Check fehlgeschlagen: ${agent.name}`);
    }
  }

  async startAgent(agentId) {
    const agent = AGENTS_CONFIG.find((a) => a.id === agentId);
    if (!agent) return;
    this.toast(`Starte ${agent.name}...`, "info");
    this.addActivity("info", `Agent wird gestartet: ${agent.name}`);
    // In production: API call to start agent
    setTimeout(() => this.refreshAllAgents(), 2000);
  }

  async stopAgent(agentId) {
    const agent = AGENTS_CONFIG.find((a) => a.id === agentId);
    if (!agent) return;
    this.toast(`Stoppe ${agent.name}...`, "warning");
    this.addActivity("info", `Agent wird gestoppt: ${agent.name}`);
    // In production: API call to stop agent
    setTimeout(() => this.refreshAllAgents(), 2000);
  }

  async startAllAgents() {
    this.toast("Starte alle Agenten...", "info");
    this.addActivity("info", "Alle Agenten werden gestartet");
    // In production: API call to start all
    setTimeout(() => this.refreshAllAgents(), 3000);
  }

  async stopAllAgents() {
    this.toast("Stoppe alle Agenten...", "warning");
    this.addActivity("info", "Alle Agenten werden gestoppt");
    // In production: API call to stop all
    setTimeout(() => this.refreshAllAgents(), 3000);
  }

  openAgentPage(agentId) {
    window.location.href = `/agent/${agentId}`;
  }

  async sendApiRequest() {
    const method = document.getElementById("api-method").value;
    const endpoint = document.getElementById("api-endpoint").value;
    const responseEl = document.getElementById("api-response");
    if (!endpoint) {
      this.toast("Bitte Endpoint eingeben", "warning");
      return;
    }
    try {
      responseEl.textContent = "Sende Anfrage...";
      const res = await fetch(endpoint, { method });
      const data = await res.json();
      responseEl.textContent = JSON.stringify(data, null, 2);
      this.addActivity("success", `API-Anfrage: ${method} ${endpoint}`);
    } catch (e) {
      responseEl.textContent = `Fehler: ${e.message}`;
      this.addActivity("error", `API-Fehler: ${endpoint}`);
    }
  }

  addActivity(type, message) {
    const activity = { type, message, time: new Date() };
    this.activities.unshift(activity);
    if (this.activities.length > 50) this.activities.pop();
    this.renderActivities();
  }

  renderActivities() {
    const list = document.getElementById("activity-list");
    if (!list) return;
    list.innerHTML = this.activities
      .slice(0, 20)
      .map(
        (a) => `
            <div class="activity-item">
                <div class="activity-icon ${a.type}">
                    ${a.type === "success" ? "✅" : a.type === "error" ? "❌" : "ℹ️"}
                </div>
                <div class="activity-content">
                    <div class="title">${a.message}</div>
                    <div class="time">${a.time.toLocaleTimeString("de-DE")}</div>
                </div>
            </div>
        `,
      )
      .join("");
  }

  updateClock() {
    const el = document.getElementById("current-time");
    if (el) el.textContent = new Date().toLocaleString("de-DE");
  }

  startAutoRefresh() {
    setInterval(() => this.refreshAllAgents(), 30000);
  }

  toast(message, type = "info") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${type === "success" ? "✅" : type === "error" ? "❌" : type === "warning" ? "⚠️" : "ℹ️"}</span> ${message}`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
  }
}

const dashboard = new ELIONDashboard();
