// Homepage Creator Agent Dashboard | PAS-6.0
class HomepageCreatorDashboard {
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

    document.querySelectorAll(".capability-card").forEach((card) => {
      card.addEventListener("click", (e) => {
        const capability = e.currentTarget.dataset.capability;
        this.showCapabilityInfo(capability);
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
        this.showToast("Agent verbunden", "success");
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
    await this.loadRecentProjects();
  }

  async loadMetrics() {
    try {
      const response = await fetch(`${this.baseUrl}/api/metrics`);
      if (response.ok) {
        const data = await response.json();
        document.getElementById("totalSites").textContent =
          data.total_sites || 0;
        document.getElementById("liveSites").textContent = data.live_sites || 0;
        document.getElementById("templates").textContent = data.templates || 0;
        document.getElementById("components").textContent =
          data.components || 0;
        document.getElementById("totalViews").textContent =
          data.total_views || 0;
        document.getElementById("drafts").textContent = data.drafts || 0;
      }
    } catch (error) {
      console.log("Metrics not available");
    }
  }

  async loadRecentProjects() {
    const container = document.getElementById("recentProjectsList");
    try {
      const response = await fetch(`${this.baseUrl}/api/projects?limit=5`);
      if (response.ok) {
        const data = await response.json();
        if (data.projects && data.projects.length > 0) {
          container.innerHTML = data.projects
            .map(
              (project) => `
                        <div class="project-item">
                            <div>
                                <strong>${project.name}</strong>
                                <span style="color: var(--text-muted); margin-left: 0.5rem;">${project.status}</span>
                            </div>
                            <button class="btn btn-secondary" onclick="dashboard.openProject('${project.id}')">Öffnen</button>
                        </div>
                    `,
            )
            .join("");
        } else {
          container.innerHTML =
            '<div class="loading">Keine Projekte vorhanden</div>';
        }
      }
    } catch (error) {
      container.innerHTML =
        '<div class="loading">Projekte werden geladen...</div>';
    }
  }

  handleAction(action) {
    const actions = {
      newSite: () => this.createProject(),
      openBuilder: () => this.navigateTo("builder"),
      browseTemplates: () => this.navigateTo("templates"),
      viewProjects: () => this.navigateTo("projects"),
      publishSite: () => this.publishSite(),
      viewAnalytics: () => this.navigateTo("analytics"),
    };
    if (actions[action]) {
      actions[action]();
    }
  }

  async createProject() {
    const name = prompt("Projektname:");
    if (!name) return;

    try {
      const response = await fetch(`${this.baseUrl}/api/projects/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      if (response.ok) {
        this.showToast("Projekt erstellt", "success");
        this.loadRecentProjects();
      }
    } catch (error) {
      this.showToast("Fehler beim Erstellen", "error");
    }
  }

  async publishSite() {
    this.showToast("Veröffentlichung gestartet...", "info");
  }

  openProject(id) {
    this.showToast(`Projekt ${id} wird geöffnet`, "info");
    this.navigateTo("builder");
  }

  filterTemplates(category) {
    this.showToast(`Filter: ${category}`, "info");
  }

  uploadTemplate() {
    this.showToast("Template-Upload wird vorbereitet", "info");
  }

  createComponent() {
    this.showToast("Component Builder wird geöffnet", "info");
  }

  showCapabilityInfo(capability) {
    const info = {
      drag_drop: "Visueller Drag & Drop Builder für einfache Seitenerstellung",
      templates: "Bibliothek mit vorgefertigten Seitentemplates",
      responsive: "Automatische Anpassung an alle Bildschirmgrößen",
      components: "Wiederverwendbare UI-Komponenten",
      seo: "Integrierte SEO-Optimierungstools",
      hosting: "One-Click Deployment und Hosting",
      forms: "Formular-Builder für Kontakt und Leads",
      media: "Medien-Manager für Bilder und Videos",
      custom_code: "Eigenen HTML/CSS/JS Code einbinden",
      analytics: "Analyse-Integration für Besucherstatistiken",
    };
    this.showToast(info[capability] || capability, "info");
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
      if (method === "POST" && body) {
        options.body = body;
      }
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

// Initialize
const dashboard = new HomepageCreatorDashboard();
