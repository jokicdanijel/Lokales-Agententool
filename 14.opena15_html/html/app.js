class HTMLCreatorDashboard {
  constructor() {
    this.templates = CONFIG.DEFAULT_TEMPLATES;
    this.history = [];
    this.stats = {
      bootstrap: 0,
      tailwind: 0,
      bulma: 0,
      plain: 0,
      valid: 0,
      invalid: 0,
      exports: 0,
      totalSize: 0,
      count: 0,
    };
    this.startTime = Date.now();
    this.init();
  }
  async init() {
    this.bindEvents();
    await this.loadHealth();
    this.renderTemplates();
    this.startIntervals();
    this.updateUptime();
    setInterval(() => this.updateUptime(), 1000);
  }
  bindEvents() {
    document
      .getElementById("generate-form")
      ?.addEventListener("submit", (e) => this.generateHTML(e));
    document
      .getElementById("validate-form")
      ?.addEventListener("submit", (e) => this.validateHTML(e));
    document
      .getElementById("preview-form")
      ?.addEventListener("submit", (e) => this.previewHTML(e));
    document
      .getElementById("export-form")
      ?.addEventListener("submit", (e) => this.exportHTML(e));
  }
  async apiCall(endpoint, method = "GET", body = null) {
    const opts = {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `${CONFIG.AUTH.BEARER_PREFIX}${localStorage.getItem(CONFIG.AUTH.TOKEN_KEY) || ""}`,
      },
    };
    if (body) opts.body = JSON.stringify(body);
    try {
      const res = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, opts);
      return await res.json();
    } catch (e) {
      console.error("API Error:", e);
      return null;
    }
  }
  async loadHealth() {
    const data = await this.apiCall(CONFIG.ENDPOINTS.HEALTH);
    const status = document.getElementById("connection-status");
    if (data?.status === "ok") {
      status.className = "status-indicator status-ok";
      status.querySelector(".status-text").textContent = "Online";
      document.getElementById("total-templates").textContent =
        data.templates_available || this.templates.length;
    } else {
      status.className = "status-indicator status-error";
      status.querySelector(".status-text").textContent = "Offline";
    }
  }
  async generateHTML(e) {
    e.preventDefault();
    const payload = {
      template_name: document.getElementById("template-select").value,
      variables: {
        title: document.getElementById("page-title").value,
        heading: document.getElementById("page-heading").value,
        content: document.getElementById("page-content").value,
      },
      css_framework: document.getElementById("css-framework").value,
      title: document.getElementById("page-title").value,
      description: document.getElementById("meta-description").value,
      keywords: document
        .getElementById("meta-keywords")
        .value.split(",")
        .map((k) => k.trim())
        .filter((k) => k),
    };
    const res = await this.apiCall(CONFIG.ENDPOINTS.GENERATE, "POST", payload);
    if (res?.html || res?.success) {
      this.toast("HTML erfolgreich generiert!", "success");
      this.updateFrameworkStats(payload.css_framework);
      this.addHistory("generate", payload.template_name, true);
      this.addActivity(
        `HTML generiert: ${payload.template_name} (${payload.css_framework})`,
      );
      document.getElementById("total-generated").textContent =
        parseInt(document.getElementById("total-generated").textContent) + 1;
      if (res.html) {
        document.getElementById("preview-html").value = res.html;
        document.getElementById("export-html").value = res.html;
        document.getElementById("validate-html").value = res.html;
      }
    } else {
      this.toast("Fehler beim Generieren", "danger");
      this.addHistory("generate", payload.template_name, false);
    }
  }
  async validateHTML(e) {
    e.preventDefault();
    const html = document.getElementById("validate-html").value;
    if (!html.trim()) {
      this.toast("Bitte HTML eingeben", "warning");
      return;
    }
    const payload = {
      html,
      validation_level: document.getElementById("validation-level").value,
    };
    const res = await this.apiCall(CONFIG.ENDPOINTS.VALIDATE, "POST", payload);
    const resultBox = document.getElementById("validation-result");
    if (res?.valid || res?.is_valid) {
      resultBox.className = "result-box success";
      resultBox.innerHTML = `<strong>✅ Validierung erfolgreich!</strong><br>Level: ${payload.validation_level}`;
      this.stats.valid++;
      this.addHistory("validate", payload.validation_level, true);
    } else {
      resultBox.className = "result-box error";
      const errors = res?.errors || res?.issues || ["Unbekannter Fehler"];
      resultBox.innerHTML = `<strong>❌ Validierungsfehler:</strong><br>${errors.join("<br>")}`;
      this.stats.invalid++;
      this.addHistory("validate", payload.validation_level, false);
    }
    document.getElementById("total-validations").textContent =
      this.stats.valid + this.stats.invalid;
    this.updateStats();
    this.addActivity(
      `Validierung: ${res?.valid || res?.is_valid ? "OK" : "Fehler"} (${payload.validation_level})`,
    );
  }
  async previewHTML(e) {
    e.preventDefault();
    const html = document.getElementById("preview-html").value;
    if (!html.trim()) {
      this.toast("Bitte HTML eingeben", "warning");
      return;
    }
    const payload = {
      html,
      width:
        parseInt(document.getElementById("preview-width").value) ||
        CONFIG.PREVIEW.DEFAULT_WIDTH,
      height:
        parseInt(document.getElementById("preview-height").value) ||
        CONFIG.PREVIEW.DEFAULT_HEIGHT,
    };
    const container = document.getElementById("preview-container");
    const iframe = document.createElement("iframe");
    iframe.style.width = "100%";
    iframe.style.height = `${Math.min(payload.height, 400)}px`;
    container.innerHTML = "";
    container.appendChild(iframe);
    iframe.contentDocument.open();
    iframe.contentDocument.write(html);
    iframe.contentDocument.close();
    this.toast("Vorschau gerendert", "info");
    this.addActivity(`Vorschau gerendert (${payload.width}x${payload.height})`);
  }
  async exportHTML(e) {
    e.preventDefault();
    const html = document.getElementById("export-html").value;
    if (!html.trim()) {
      this.toast("Bitte HTML eingeben", "warning");
      return;
    }
    const payload = {
      html,
      filename:
        document.getElementById("export-filename").value || "export.html",
      format: document.getElementById("export-format").value,
    };
    const res = await this.apiCall(CONFIG.ENDPOINTS.EXPORT, "POST", payload);
    if (res?.success || res?.file_path || res?.data) {
      this.toast(`Export erfolgreich: ${payload.filename}`, "success");
      this.stats.exports++;
      this.stats.totalSize += html.length;
      this.stats.count++;
      document.getElementById("total-exports").textContent = this.stats.exports;
      this.addHistory("export", payload.filename, true);
      this.addActivity(`Export: ${payload.filename} (${payload.format})`);
      this.updateStats();
      if (res.data && payload.format === "base64") {
        const blob = new Blob([atob(res.data)], { type: "text/html" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = payload.filename;
        a.click();
      }
    } else {
      this.toast("Export fehlgeschlagen", "danger");
      this.addHistory("export", payload.filename, false);
    }
  }
  updateFrameworkStats(framework) {
    if (framework === "bootstrap") this.stats.bootstrap++;
    else if (framework === "tailwind") this.stats.tailwind++;
    else if (framework === "bulma") this.stats.bulma++;
    else this.stats.plain++;
    this.updateStats();
  }
  updateStats() {
    document.getElementById("stat-bootstrap").textContent =
      this.stats.bootstrap;
    document.getElementById("stat-tailwind").textContent = this.stats.tailwind;
    document.getElementById("stat-bulma").textContent = this.stats.bulma;
    document.getElementById("stat-plain").textContent = this.stats.plain;
    document.getElementById("stat-valid").textContent = this.stats.valid;
    document.getElementById("stat-invalid").textContent = this.stats.invalid;
    document.getElementById("stat-total-exports").textContent =
      this.stats.exports;
    const avgSize =
      this.stats.count > 0
        ? (this.stats.totalSize / this.stats.count / 1024).toFixed(1)
        : 0;
    document.getElementById("stat-avg-size").textContent = `${avgSize} KB`;
  }
  renderTemplates() {
    const container = document.getElementById("templates-list");
    document.getElementById("templates-count").textContent =
      this.templates.length;
    container.innerHTML = this.templates
      .map(
        (t) => `
            <div class="template-item" onclick="htmlCreator.selectTemplate('${t.name}')">
                <div class="icon">${t.icon}</div>
                <div class="name">${t.name}</div>
            </div>
        `,
      )
      .join("");
  }
  selectTemplate(name) {
    document.getElementById("template-select").value = name;
    this.toast(`Template gewählt: ${name}`, "info");
  }
  addHistory(type, detail, success) {
    const item = { type, detail, success, time: new Date() };
    this.history.unshift(item);
    if (this.history.length > CONFIG.UI.MAX_HISTORY_ITEMS) this.history.pop();
    this.renderHistory();
  }
  renderHistory() {
    const container = document.getElementById("history-list");
    if (!this.history.length) {
      container.innerHTML = '<p class="empty-state">Kein Verlauf</p>';
      return;
    }
    const typeLabels = {
      generate: "🚀 Generate",
      validate: "✅ Validate",
      export: "💾 Export",
    };
    container.innerHTML = this.history
      .map(
        (h) => `
            <div class="history-item">
                <div class="info">
                    <div class="type">${typeLabels[h.type] || h.type}</div>
                    <div class="time">${h.detail} • ${h.time.toLocaleTimeString(CONFIG.UI.DATE_LOCALE)}</div>
                </div>
                <span class="status ${h.success ? "success" : "error"}">${h.success ? "OK" : "Fehler"}</span>
            </div>
        `,
      )
      .join("");
  }
  addActivity(msg) {
    const log = document.getElementById("activity-log");
    const item = document.createElement("div");
    item.className = "activity-item";
    item.textContent = `${new Date().toLocaleTimeString(CONFIG.UI.DATE_LOCALE)} - ${msg}`;
    log.insertBefore(item, log.firstChild);
    while (log.children.length > CONFIG.UI.MAX_ACTIVITY_ITEMS)
      log.removeChild(log.lastChild);
  }
  updateUptime() {
    const s = Math.floor((Date.now() - this.startTime) / 1000);
    document.getElementById("uptime").textContent = `${Math.floor(s / 3600)
      .toString()
      .padStart(2, "0")}:${Math.floor((s % 3600) / 60)
      .toString()
      .padStart(2, "0")}:${(s % 60).toString().padStart(2, "0")}`;
    document.getElementById("last-update").textContent =
      new Date().toLocaleTimeString(CONFIG.UI.DATE_LOCALE);
  }
  toast(msg, type = "info") {
    const c = document.getElementById("toast-container");
    const t = document.createElement("div");
    t.className = `toast bg-${type}`;
    t.textContent = msg;
    c.appendChild(t);
    setTimeout(() => t.remove(), CONFIG.UI.TOAST_DURATION);
  }
  startIntervals() {
    setInterval(() => this.loadHealth(), CONFIG.REFRESH_INTERVALS.STATUS);
  }
}
function saveToken() {
  const token = document.getElementById("token").value;
  if (token) {
    localStorage.setItem(CONFIG.AUTH.TOKEN_KEY, token);
    htmlCreator.toast("Token gespeichert", "success");
  }
}
const htmlCreator = new HTMLCreatorDashboard();
