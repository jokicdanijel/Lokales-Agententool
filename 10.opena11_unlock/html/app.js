// 🔐 OPENA11 Unlock Master Dashboard - Application Logic
// PORTIER PAS-6.0

class UnlockDashboard {
  constructor() {
    this.refreshIntervals = {};
    this.permissions = {};
    this.auditLog = [];
    this.metrics = null;
    this.startTime = Date.now();

    this.init();
  }

  async init() {
    console.log("🔐 OPENA11 Unlock Master Dashboard initialisiert");

    // Load saved token
    this.loadToken();

    // Bind event handlers
    this.bindEvents();

    // Initial data fetch
    await this.refreshAll();

    // Start auto-refresh
    this.startAutoRefresh();

    // Update uptime display
    this.updateUptimeDisplay();
    setInterval(() => this.updateUptimeDisplay(), 1000);
  }

  loadToken() {
    const token = localStorage.getItem(CONFIG.AUTH.TOKEN_KEY);
    if (token) {
      document.getElementById("bearer-token").value = token;
    }
  }

  bindEvents() {
    // Grant form
    document.getElementById("grant-form")?.addEventListener("submit", (e) => {
      e.preventDefault();
      this.grantPermission();
    });

    // Check form
    document.getElementById("check-form")?.addEventListener("submit", (e) => {
      e.preventDefault();
      this.checkPermission();
    });

    // Filter input
    document
      .getElementById("filter-subject")
      ?.addEventListener("input", (e) => {
        this.filterPermissions(e.target.value);
      });
  }

  // === API Calls ===

  async apiCall(endpoint, options = {}) {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;

    const defaultOptions = {
      headers: {
        "Content-Type": "application/json",
      },
    };

    // Add auth token if available
    const token = localStorage.getItem(CONFIG.AUTH.TOKEN_KEY);
    if (token) {
      defaultOptions.headers["Authorization"] =
        `${CONFIG.AUTH.BEARER_PREFIX}${token}`;
    }

    try {
      const response = await fetch(url, { ...defaultOptions, ...options });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  async refreshAll() {
    await Promise.all([
      this.fetchStatus(),
      this.fetchMetrics(),
      this.loadPermissions(),
      this.loadAuditLog(),
    ]);
  }

  async fetchStatus() {
    try {
      const data = await this.apiCall(CONFIG.ENDPOINTS.HEALTH);
      this.updateConnectionStatus(data.status === "healthy");
      this.updateStatusCards(data);
    } catch (error) {
      this.updateConnectionStatus(false);
    }
  }

  async fetchMetrics() {
    try {
      const data = await this.apiCall(CONFIG.ENDPOINTS.METRICS);
      this.metrics = data;
      this.updateMetricsDisplay(data);
    } catch (error) {
      console.error("Metrics fetch failed:", error);
    }
  }

  // === Permission Operations ===

  async grantPermission() {
    const subject = document.getElementById("grant-subject").value;
    const resource = document.getElementById("grant-resource").value;
    const action = document.getElementById("grant-action").value;
    const expiresHours =
      parseInt(document.getElementById("grant-expires").value) || 0;

    const expires =
      expiresHours > 0
        ? Math.floor(Date.now() / 1000) + expiresHours * 3600
        : 0;

    try {
      const response = await this.apiCall(CONFIG.ENDPOINTS.COMMAND, {
        method: "POST",
        body: JSON.stringify({
          action: CONFIG.ACTIONS.GRANT,
          params: { subject, resource, action, expires },
        }),
      });

      this.showToast(
        `✅ Berechtigung erteilt: ${subject} → ${action} auf ${resource}`,
        "success",
      );

      // Clear form
      document.getElementById("grant-subject").value = "";
      document.getElementById("grant-resource").value = "";

      // Reload permissions
      await this.loadPermissions();
      await this.loadAuditLog();
    } catch (error) {
      this.showToast(`❌ Fehler: ${error.message}`, "error");
    }
  }

  async checkPermission() {
    const subject = document.getElementById("check-subject").value;
    const resource = document.getElementById("check-resource").value;
    const action = document.getElementById("check-action").value;

    const resultBox = document.getElementById("check-result");

    try {
      const response = await this.apiCall(CONFIG.ENDPOINTS.COMMAND, {
        method: "POST",
        body: JSON.stringify({
          action: CONFIG.ACTIONS.CHECK,
          params: { subject, resource, action },
        }),
      });

      const allowed = response.allowed;

      resultBox.innerHTML = `
                <div class="${allowed ? "success" : "error"}">
                    <strong>${allowed ? "✅ ERLAUBT" : "❌ VERWEIGERT"}</strong><br>
                    <small>${subject} → ${action} auf ${resource}</small>
                </div>
            `;
      resultBox.className = `result-box ${allowed ? "success" : "error"}`;
      resultBox.classList.remove("hidden");
    } catch (error) {
      resultBox.innerHTML = `<div class="error">Fehler: ${error.message}</div>`;
      resultBox.className = "result-box error";
      resultBox.classList.remove("hidden");
    }
  }

  async revokePermission(subject, resource, action) {
    if (
      !confirm(
        `Berechtigung widerrufen?\n${subject} → ${action} auf ${resource}`,
      )
    ) {
      return;
    }

    try {
      await this.apiCall(CONFIG.ENDPOINTS.COMMAND, {
        method: "POST",
        body: JSON.stringify({
          action: CONFIG.ACTIONS.REVOKE,
          params: { subject, resource, action },
        }),
      });

      this.showToast("Berechtigung widerrufen", "success");
      await this.loadPermissions();
      await this.loadAuditLog();
    } catch (error) {
      this.showToast(`Fehler: ${error.message}`, "error");
    }
  }

  // === Load Data ===

  async loadPermissions() {
    try {
      const response = await this.apiCall(CONFIG.ENDPOINTS.COMMAND, {
        method: "POST",
        body: JSON.stringify({
          action: CONFIG.ACTIONS.LIST,
          params: {},
        }),
      });

      this.permissions = response.permissions || {};
      this.renderPermissions();
    } catch (error) {
      console.error("Failed to load permissions:", error);
    }
  }

  async loadAuditLog() {
    try {
      const response = await this.apiCall(CONFIG.ENDPOINTS.LOGS);
      this.auditLog = response.logs || [];
      this.renderAuditLog();

      // Update audit count
      this.setElementText("audit-count", response.total || 0);
    } catch (error) {
      console.error("Failed to load audit log:", error);
    }
  }

  // === AI Functions ===

  async runAIAnalysis() {
    const query = document.getElementById("ai-query").value;
    const resultBox = document.getElementById("ai-result");

    resultBox.innerHTML = '<div class="loading">🔄 AI Analyse läuft...</div>';
    resultBox.classList.remove("hidden");

    try {
      const response = await this.apiCall(CONFIG.ENDPOINTS.COMMAND, {
        method: "POST",
        body: JSON.stringify({
          action: CONFIG.ACTIONS.AI_ANALYZE,
          params: { query },
        }),
      });

      resultBox.innerHTML = `
                <div class="analysis-result">
                    <h4>🤖 AI Analyse</h4>
                    <pre>${response.analysis?.analysis || response.analysis || "Keine Analyse verfügbar"}</pre>
                </div>
            `;
    } catch (error) {
      resultBox.innerHTML = `<div class="error">Fehler: ${error.message}</div>`;
      resultBox.className = "result-box error";
    }
  }

  async runSecurityScan() {
    try {
      const response = await this.apiCall(
        CONFIG.SPECIALIZED_ENDPOINTS.SECURITY_SCAN,
        {
          method: "POST",
        },
      );

      this.showModal(
        "Security Scan Ergebnis",
        `
                <div class="scan-result">
                    <h4>Risk Score: ${response.scan?.risk_score || 0}/100</h4>
                    <p>Risk Level: <strong>${response.scan?.risk_level || "unknown"}</strong></p>
                    <h5>Findings (${response.scan?.findings_count || 0}):</h5>
                    <ul>
                        ${(response.scan?.findings || [])
                          .map(
                            (f) =>
                              `<li><strong>${f.severity}:</strong> ${f.description}</li>`,
                          )
                          .join("")}
                    </ul>
                    <h5>Empfehlungen:</h5>
                    <ul>
                        ${(response.scan?.recommendations || [])
                          .map((r) => `<li>${r}</li>`)
                          .join("")}
                    </ul>
                </div>
            `,
      );
    } catch (error) {
      this.showToast(`Scan fehlgeschlagen: ${error.message}`, "error");
    }
  }

  // === Render Functions ===

  renderPermissions() {
    const container = document.getElementById("permissions-list");
    const filter =
      document.getElementById("filter-subject")?.value?.toLowerCase() || "";

    let html = "";
    let count = 0;
    let subjectCount = 0;

    for (const [subject, perms] of Object.entries(this.permissions)) {
      if (filter && !subject.toLowerCase().includes(filter)) continue;

      subjectCount++;

      for (const perm of perms) {
        count++;
        html += `
                    <div class="permission-item">
                        <div>
                            <span class="permission-subject">${subject}</span>
                            <span class="permission-details">→ ${perm.resource}</span>
                        </div>
                        <div>
                            <span class="permission-action">${perm.action}</span>
                            <button class="permission-delete" onclick="dashboard.revokePermission('${subject}', '${perm.resource}', '${perm.action}')">×</button>
                        </div>
                    </div>
                `;
      }
    }

    container.innerHTML =
      html || '<p class="empty-state">Keine Berechtigungen</p>';

    // Update counts
    this.setElementText("permissions-count", count);
    this.setElementText("subjects-count", subjectCount);
  }

  renderAuditLog() {
    const container = document.getElementById("audit-log");

    if (!this.auditLog.length) {
      container.innerHTML = '<p class="empty-state">Keine Audit-Einträge</p>';
      return;
    }

    const html = this.auditLog
      .slice(0, CONFIG.UI.MAX_AUDIT_ENTRIES)
      .map((entry) => {
        const time = new Date(entry.timestamp).toLocaleTimeString(
          CONFIG.UI.DATE_LOCALE,
        );
        const payload = JSON.stringify(entry.payload || {}).slice(0, 50);

        return `
                <div class="audit-entry">
                    <span class="audit-time">${time}</span>
                    <span class="audit-event ${entry.event}">${entry.event}</span>
                    <span class="audit-details">${payload}...</span>
                </div>
            `;
      })
      .join("");

    container.innerHTML = html;
  }

  filterPermissions(filter) {
    this.renderPermissions();
  }

  // === Display Updates ===

  updateConnectionStatus(connected) {
    const statusEl = document.getElementById("connection-status");
    statusEl.className = `status-indicator status-${connected ? "ok" : "error"}`;
    statusEl.querySelector(".status-text").textContent = connected
      ? "Verbunden"
      : "Offline";
  }

  updateStatusCards(data) {
    this.setElementText("permissions-count", data.permissions_count || 0);
  }

  updateMetricsDisplay(data) {
    const counters = data.counters || {};
    this.setElementText("checks-count", counters.permission_checks || 0);
  }

  updateUptimeDisplay() {
    const elapsed = Date.now() - this.startTime;
    const seconds = Math.floor(elapsed / 1000);
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    const formatted = `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    this.setElementText("uptime", formatted);

    // Update last update time
    const now = new Date().toLocaleTimeString(CONFIG.UI.DATE_LOCALE);
    this.setElementText("last-update", `Letztes Update: ${now}`);
  }

  // === Utilities ===

  setElementText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
      toast.remove();
    }, CONFIG.UI.TOAST_DURATION);
  }

  showModal(title, content) {
    document.getElementById("modal-title").textContent = title;
    document.getElementById("modal-body").innerHTML = content;
    document.getElementById("result-modal").classList.remove("hidden");
  }

  startAutoRefresh() {
    this.refreshIntervals.status = setInterval(
      () => this.fetchStatus(),
      CONFIG.REFRESH_INTERVALS.STATUS,
    );

    this.refreshIntervals.metrics = setInterval(
      () => this.fetchMetrics(),
      CONFIG.REFRESH_INTERVALS.METRICS,
    );

    this.refreshIntervals.permissions = setInterval(
      () => this.loadPermissions(),
      CONFIG.REFRESH_INTERVALS.PERMISSIONS,
    );

    this.refreshIntervals.audit = setInterval(
      () => this.loadAuditLog(),
      CONFIG.REFRESH_INTERVALS.AUDIT,
    );
  }
}

// Global functions for onclick handlers
function saveToken() {
  const token = document.getElementById("bearer-token").value;
  localStorage.setItem(CONFIG.AUTH.TOKEN_KEY, token);
  window.dashboard?.showToast("Token gespeichert", "success");
}

function loadPermissions() {
  window.dashboard?.loadPermissions();
}

function loadAuditLog() {
  window.dashboard?.loadAuditLog();
}

function runAIAnalysis() {
  window.dashboard?.runAIAnalysis();
}

function runSecurityScan() {
  window.dashboard?.runSecurityScan();
}

function exportPermissions() {
  const data = JSON.stringify(window.dashboard?.permissions || {}, null, 2);
  const blob = new Blob([data], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "permissions_export.json";
  a.click();
  window.dashboard?.showToast("Export erstellt", "success");
}

function verifyIntegrity() {
  window.dashboard?.showToast(
    "Integritätsprüfung: Feature in Entwicklung",
    "info",
  );
}

function closeModal() {
  document.getElementById("result-modal").classList.add("hidden");
}

// Initialize dashboard when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  window.dashboard = new UnlockDashboard();
});
