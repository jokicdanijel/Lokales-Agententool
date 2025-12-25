/* Call Tracking Agent PAS-6.0 | Application Logic | Port 12356 */
class CallTrackingDashboard {
  constructor(config) {
    this.config = config;
    this.state = {
      connected: false,
      calls: [],
      sources: [],
      campaigns: [],
      numbers: [],
      metrics: {
        totalCalls: 0,
        conversionRate: 0,
        activeSources: 0,
        activeCampaigns: 0,
        totalRevenue: 0,
        trackingNumbers: 0,
      },
    };
    this.refreshInterval = null;
  }

  async init() {
    console.log(
      `📊 Call Tracking Dashboard v${this.config.agent.version} initializing...`,
    );
    this.bindNavigation();
    this.bindActions();
    await this.checkHealth();
    this.startAutoRefresh();
    this.showSection("overview");
    console.log("✅ Dashboard ready");
  }

  bindNavigation() {
    document.querySelectorAll(".nav-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const section = btn.dataset.section;
        if (section) this.showSection(section);
      });
    });
  }

  showSection(sectionId) {
    document
      .querySelectorAll(".nav-btn")
      .forEach((b) => b.classList.remove("active"));
    document
      .querySelectorAll(".section")
      .forEach((s) => s.classList.remove("active"));
    document
      .querySelector(`.nav-btn[data-section="${sectionId}"]`)
      ?.classList.add("active");
    document.getElementById(sectionId)?.classList.add("active");
    this.loadSectionData(sectionId);
  }

  async loadSectionData(section) {
    switch (section) {
      case "overview":
        await this.loadOverview();
        break;
      case "tracking":
        await this.loadTracking();
        break;
      case "sources":
        await this.loadSources();
        break;
      case "campaigns":
        await this.loadCampaigns();
        break;
      case "numbers":
        await this.loadNumbers();
        break;
      case "attribution":
        await this.loadAttribution();
        break;
      case "analytics":
        await this.loadAnalytics();
        break;
      case "reports":
        await this.loadReports();
        break;
    }
  }

  bindActions() {
    document
      .getElementById("refreshBtn")
      ?.addEventListener("click", () => this.checkHealth());
    document
      .getElementById("testApiBtn")
      ?.addEventListener("click", () => this.testApi());

    document.querySelectorAll(".action-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const action = btn.dataset.action;
        if (action && typeof this[action] === "function") this[action]();
      });
    });

    document.querySelectorAll(".capability-card").forEach((card) => {
      card.addEventListener("click", () => {
        const capability = card.dataset.capability;
        this.executeCapability(capability);
      });
    });
  }

  // ==================== API CALLS ====================
  async apiCall(endpoint, method = "GET", data = null) {
    try {
      const url = `${this.config.agent.baseUrl}${endpoint}`;
      const options = {
        method,
        headers: { "Content-Type": "application/json" },
      };
      if (data) options.body = JSON.stringify(data);
      const response = await fetch(url, options);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      return { error: error.message };
    }
  }

  async checkHealth() {
    const status = await this.apiCall(this.config.api.endpoints.health);
    this.state.connected = !status.error && status.status === "ok";
    this.updateConnectionStatus();
    if (this.state.connected) {
      this.showToast("Call Tracking Agent verbunden", "success");
    }
    return status;
  }

  updateConnectionStatus() {
    const badge = document.querySelector(".status-badge");
    const text = document.querySelector(".status-text");
    if (this.state.connected) {
      badge?.classList.add("online");
      if (text) text.textContent = "Connected";
    } else {
      badge?.classList.remove("online");
      if (text) text.textContent = "Disconnected";
    }
  }

  // ==================== OVERVIEW ====================
  async loadOverview() {
    const [stats, recentCalls] = await Promise.all([
      this.apiCall(this.config.api.endpoints.callStats),
      this.apiCall(this.config.api.endpoints.calls + "?limit=20"),
    ]);

    if (!stats.error) {
      this.updateMetric("totalCalls", stats.total || 0);
      this.updateMetric("conversionRate", `${stats.conversion || 0}%`);
      this.updateMetric("activeSources", stats.sources || 0);
      this.updateMetric("activeCampaigns", stats.campaigns || 0);
      this.updateMetric(
        "totalRevenue",
        `€${(stats.revenue || 0).toLocaleString("de-DE")}`,
      );
      this.updateMetric("trackingNumbers", stats.numbers || 0);
    }

    if (!recentCalls.error && recentCalls.calls) {
      this.state.calls = recentCalls.calls;
      this.renderRecentCalls();
    }
  }

  updateMetric(id, value) {
    const el = document.getElementById(id);
    if (el)
      el.textContent =
        typeof value === "number" ? value.toLocaleString("de-DE") : value;
  }

  renderRecentCalls() {
    const container = document.getElementById("recentCallsList");
    if (!container) return;

    if (this.state.calls.length === 0) {
      container.innerHTML = '<div class="loading">Keine Anrufe</div>';
      return;
    }

    container.innerHTML = this.state.calls
      .map(
        (call) => `
            <div class="tracking-item">
                <div>
                    <strong>${call.number}</strong>
                    <span style="color: var(--text-muted);">via ${call.source || "Unknown"}</span>
                </div>
                <div>
                    <span class="badge" style="background: var(--primary); color: white; padding: 0.2rem 0.5rem; border-radius: 4px;">${call.campaign || "N/A"}</span>
                    <span style="color: var(--text-muted);">${call.duration || "0:00"}</span>
                </div>
            </div>
        `,
      )
      .join("");
  }

  // ==================== TRACKING ====================
  async loadTracking() {
    const result = await this.apiCall(this.config.api.endpoints.liveFeed);
    if (!result.error && result.calls) {
      this.renderLiveFeed(result.calls);
    }
    this.updateMetric("todaysCalls", result.today || 0);
    this.updateMetric("avgCallDuration", `${result.avgDuration || 0}m`);
    this.updateMetric("todayConversion", `${result.conversion || 0}%`);
  }

  renderLiveFeed(calls) {
    const container = document.getElementById("liveCallFeed");
    if (!container) return;
    if (calls.length === 0) {
      container.innerHTML = '<div class="loading">Keine live Calls</div>';
      return;
    }
    container.innerHTML = calls
      .map(
        (call) => `
            <div class="tracking-item">
                <div>
                    <strong>${call.number}</strong>
                    <span>${call.time}</span>
                </div>
                <div>${call.status}</div>
            </div>
        `,
      )
      .join("");
  }

  viewTracking() {
    this.showSection("tracking");
  }

  // ==================== SOURCES ====================
  async loadSources() {
    const result = await this.apiCall(this.config.api.endpoints.sources);
    if (!result.error && result.sources) {
      this.state.sources = result.sources;
      this.renderSources();
    }
  }

  renderSources() {
    const container = document.getElementById("sourcesList");
    if (!container) return;

    if (this.state.sources.length === 0) {
      container.innerHTML = '<div class="loading">Keine Sources</div>';
      return;
    }

    container.innerHTML = this.state.sources
      .map(
        (source) => `
            <div class="source-item">
                <div>
                    <strong>${source.name}</strong>
                    <span style="color: var(--text-muted);">${source.type}</span>
                </div>
                <div>
                    <span>${source.calls || 0} calls</span>
                    <button class="btn btn-sm btn-secondary" onclick="dashboard.editSource('${source.id}')">✏️</button>
                </div>
            </div>
        `,
      )
      .join("");
  }

  showAddSourceModal() {
    this.showToast("Source hinzufügen...", "info");
  }

  editSource(id) {
    this.showToast(`Source ${id} bearbeiten...`, "info");
  }

  // ==================== CAMPAIGNS ====================
  async loadCampaigns() {
    const result = await this.apiCall(this.config.api.endpoints.campaigns);
    if (!result.error && result.campaigns) {
      this.state.campaigns = result.campaigns;
      this.renderCampaigns();
    }
  }

  renderCampaigns() {
    const container = document.getElementById("campaignsList");
    if (!container) return;

    if (this.state.campaigns.length === 0) {
      container.innerHTML = '<div class="loading">Keine Campaigns</div>';
      return;
    }

    container.innerHTML = this.state.campaigns
      .map(
        (campaign) => `
            <div class="campaign-item">
                <div>
                    <strong>${campaign.name}</strong>
                    <span style="color: var(--text-muted);">${campaign.status}</span>
                </div>
                <div>
                    <span>${campaign.calls || 0} calls</span>
                    <span>ROI: ${campaign.roi || 0}%</span>
                </div>
            </div>
        `,
      )
      .join("");
  }

  showCreateCampaignModal() {
    this.showToast("Campaign erstellen...", "info");
  }

  createCampaign() {
    this.showSection("campaigns");
  }

  // ==================== NUMBERS ====================
  async loadNumbers() {
    const result = await this.apiCall(this.config.api.endpoints.numbers);
    if (!result.error && result.numbers) {
      this.state.numbers = result.numbers;
      this.renderNumbers();
    }
  }

  renderNumbers() {
    const container = document.getElementById("numbersList");
    if (!container) return;

    if (this.state.numbers.length === 0) {
      container.innerHTML = '<div class="loading">Keine Numbers</div>';
      return;
    }

    container.innerHTML = this.state.numbers
      .map(
        (num) => `
            <div class="number-item">
                <div>
                    <strong>${num.number}</strong>
                    <span style="color: var(--text-muted);">${num.source || "Unassigned"}</span>
                </div>
                <div>
                    <span>${num.calls || 0} calls</span>
                    <span class="badge" style="background: ${num.active ? "var(--success)" : "var(--error)"}; color: white; padding: 0.2rem 0.5rem; border-radius: 4px;">${num.active ? "Active" : "Inactive"}</span>
                </div>
            </div>
        `,
      )
      .join("");
  }

  showAddNumberModal() {
    this.showToast("Number hinzufügen...", "info");
  }

  // ==================== ATTRIBUTION ====================
  async loadAttribution() {
    const result = await this.apiCall(this.config.api.endpoints.attribution);
    if (!result.error && result.data) {
      this.renderAttribution(result.data);
    }
  }

  renderAttribution(data) {
    const container = document.getElementById("attributionData");
    if (!container) return;
    container.innerHTML =
      data
        .map(
          (item) => `
            <div class="tracking-item">
                <div>
                    <strong>${item.source}</strong>
                </div>
                <div>
                    <span>${item.conversions} conversions</span>
                    <span>€${item.value}</span>
                </div>
            </div>
        `,
        )
        .join("") || '<div class="loading">Keine Attribution Data</div>';
  }

  // ==================== ANALYTICS ====================
  async loadAnalytics() {
    const result = await this.apiCall(this.config.api.endpoints.analytics);
    if (!result.error) {
      this.updateMetric("weekCalls", result.weekCalls || 0);
      this.updateMetric("growthRate", `${result.growth || 0}%`);
    }
  }

  viewAnalytics() {
    this.showSection("analytics");
  }

  // ==================== REPORTS ====================
  async loadReports() {
    const result = await this.apiCall(this.config.api.endpoints.reports);
    if (!result.error && result.scheduled) {
      this.renderScheduledReports(result.scheduled);
    }
  }

  renderScheduledReports(reports) {
    const container = document.getElementById("scheduledReports");
    if (!container) return;
    if (reports.length === 0) {
      container.innerHTML = '<div class="loading">No scheduled reports</div>';
      return;
    }
    container.innerHTML = reports
      .map(
        (r) => `
            <div class="tracking-item">
                <div><strong>${r.name}</strong></div>
                <div>${r.schedule}</div>
            </div>
        `,
      )
      .join("");
  }

  viewReports() {
    this.showSection("reports");
  }

  useTemplate(type) {
    this.showToast(`Template ${type} laden...`, "info");
  }

  generateReport() {
    this.showToast("Report wird generiert...", "info");
  }

  exportData() {
    this.showToast("Export startet...", "info");
  }

  // ==================== CAPABILITIES ====================
  executeCapability(capabilityId) {
    switch (capabilityId) {
      case "call_logging":
        this.showSection("tracking");
        break;
      case "source_tracking":
        this.showSection("sources");
        break;
      case "campaign_tracking":
        this.showSection("campaigns");
        break;
      case "dynamic_numbers":
        this.showSection("numbers");
        break;
      case "roi_analysis":
        this.showSection("analytics");
        break;
      case "custom_reports":
        this.showSection("reports");
        break;
      default:
        this.showToast(`${capabilityId} aktiviert`, "info");
    }
  }

  // ==================== API CONSOLE ====================
  async testApi() {
    const endpoint = document.getElementById("apiEndpoint")?.value || "/health";
    const method = document.getElementById("apiMethod")?.value || "GET";
    let body = null;
    if (method !== "GET") {
      const bodyText = document.getElementById("apiBody")?.value;
      if (bodyText) {
        try {
          body = JSON.parse(bodyText);
        } catch (e) {
          this.showToast("Ungültiges JSON", "error");
          return;
        }
      }
    }
    const result = await this.apiCall(endpoint, method, body);
    document.getElementById("apiResponse").textContent = JSON.stringify(
      result,
      null,
      2,
    );
  }

  // ==================== UTILITIES ====================
  showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    if (!container) return;
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
  }

  startAutoRefresh() {
    this.refreshInterval = setInterval(
      () => this.checkHealth(),
      this.config.ui.refreshInterval,
    );
  }

  stopAutoRefresh() {
    if (this.refreshInterval) clearInterval(this.refreshInterval);
  }
}

let dashboard;
document.addEventListener("DOMContentLoaded", () => {
  dashboard = new CallTrackingDashboard(CallTrackingConfig);
  dashboard.init();
});
