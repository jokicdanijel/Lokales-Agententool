// CRM Agent Dashboard | PAS-6.0
class CRMDashboard {
  constructor() {
    this.baseUrl = CONFIG.api.baseUrl;
    this.init();
  }

  init() {
    this.setupNavigation();
    this.setupEventListeners();
    this.checkHealth();
    this.loadInitialData();
  }

  setupNavigation() {
    document.querySelectorAll(".nav-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const section = e.target.dataset.section;
        this.navigateTo(section);
      });
    });
  }

  navigateTo(section) {
    document
      .querySelectorAll(".nav-btn")
      .forEach((b) => b.classList.remove("active"));
    document
      .querySelectorAll(".section")
      .forEach((s) => s.classList.remove("active"));
    document
      .querySelector(`[data-section="${section}"]`)
      .classList.add("active");
    document.getElementById(section).classList.add("active");
  }

  setupEventListeners() {
    document
      .getElementById("refreshBtn")
      .addEventListener("click", () => this.refresh());
    document
      .getElementById("testApiBtn")
      ?.addEventListener("click", () => this.testApi());

    document.querySelectorAll(".action-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const action = e.currentTarget.dataset.action;
        this.handleAction(action);
      });
    });
  }

  async checkHealth() {
    const badge = document.getElementById("statusBadge");
    try {
      const response = await fetch(`${this.baseUrl}/health`, { timeout: 5000 });
      if (response.ok) {
        badge.classList.add("online");
        badge.querySelector(".status-text").textContent = "Online";
        this.showToast("CRM Agent verbunden", "success");
      } else {
        throw new Error("Health check failed");
      }
    } catch (error) {
      badge.classList.remove("online");
      badge.querySelector(".status-text").textContent = "Offline";
      this.showToast("Agent nicht erreichbar", "error");
    }
  }

  async loadInitialData() {
    await this.loadMetrics();
    await this.loadRecentActivity();
  }

  async loadMetrics() {
    try {
      const response = await fetch(`${this.baseUrl}/api/metrics`);
      if (response.ok) {
        const data = await response.json();
        document.getElementById("totalContacts").textContent =
          data.total_contacts || 0;
        document.getElementById("activeLeads").textContent =
          data.active_leads || 0;
        document.getElementById("openDeals").textContent = data.open_deals || 0;
        document.getElementById("companies").textContent = data.companies || 0;
        document.getElementById("revenue").textContent =
          "€" + (data.pipeline_value || 0);
        document.getElementById("pendingTasks").textContent =
          data.pending_tasks || 0;
      }
    } catch (error) {
      console.log("Metrics not available");
    }
  }

  async loadRecentActivity() {
    const container = document.getElementById("recentActivityList");
    try {
      const response = await fetch(`${this.baseUrl}/api/activity?limit=10`);
      if (response.ok) {
        const data = await response.json();
        if (data.activities && data.activities.length > 0) {
          container.innerHTML = data.activities
            .map(
              (a) => `
                        <div class="activity-item" style="padding: 0.75rem; border-bottom: 1px solid var(--border-color);">
                            <span>${a.icon || "📝"}</span> ${a.description}
                            <small style="color: var(--text-muted); margin-left: 0.5rem;">${a.time}</small>
                        </div>
                    `,
            )
            .join("");
        } else {
          container.innerHTML = '<div class="loading">Keine Aktivitäten</div>';
        }
      }
    } catch (error) {
      container.innerHTML =
        '<div class="loading">Aktivitäten werden geladen...</div>';
    }
  }

  handleAction(action) {
    const actions = {
      addContact: () => this.showAddContactModal(),
      createLead: () => this.showAddLeadModal(),
      createDeal: () => this.showAddDealModal(),
      addTask: () => this.showAddTaskModal(),
      viewPipeline: () => this.navigateTo("pipeline"),
      exportData: () => this.exportData(),
    };
    if (actions[action]) actions[action]();
  }

  showAddContactModal() {
    const name = prompt("Kontaktname:");
    const email = prompt("E-Mail:");
    if (name && email) {
      this.createContact({ name, email });
    }
  }

  async createContact(data) {
    try {
      const response = await fetch(`${this.baseUrl}/api/contacts/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (response.ok) {
        this.showToast("Kontakt erstellt", "success");
        this.loadMetrics();
      }
    } catch (error) {
      this.showToast("Fehler beim Erstellen", "error");
    }
  }

  showAddLeadModal() {
    this.showToast("Lead-Formular wird geöffnet", "info");
  }
  showAddDealModal() {
    this.showToast("Deal-Formular wird geöffnet", "info");
  }
  showAddTaskModal() {
    this.showToast("Task-Formular wird geöffnet", "info");
  }
  showAddCompanyModal() {
    this.showToast("Firmen-Formular wird geöffnet", "info");
  }

  exportData() {
    this.showToast("Export wird vorbereitet...", "info");
  }
  generateReport() {
    this.showToast("Report wird generiert...", "info");
  }
  useTemplate(template) {
    this.showToast(`Template: ${template}`, "info");
  }

  async testApi() {
    const endpoint = document.getElementById("apiEndpoint").value;
    const method = document.getElementById("apiMethod").value;
    const body = document.getElementById("apiBody").value;
    const responseEl = document.getElementById("apiResponse");

    try {
      const options = {
        method,
        headers: { "Content-Type": "application/json" },
      };
      if (method === "POST" && body) options.body = body;
      const response = await fetch(`${this.baseUrl}${endpoint}`, options);
      const data = await response.json();
      responseEl.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
      responseEl.textContent = `Error: ${error.message}`;
    }
  }

  refresh() {
    this.checkHealth();
    this.loadInitialData();
    this.showToast("Daten aktualisiert", "success");
  }

  showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
  }
}

const dashboard = new CRMDashboard();
