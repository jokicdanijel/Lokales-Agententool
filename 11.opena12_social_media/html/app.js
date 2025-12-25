class SocialMediaDashboard {
  constructor() {
    this.platforms = Object.keys(CONFIG.PLATFORMS);
    this.scheduledPosts = [];
    this.metrics = {};
    this.init();
  }
  async init() {
    this.bindEvents();
    await this.loadStatus();
    await this.loadMetrics();
    await this.loadQueue();
    this.startIntervals();
  }
  bindEvents() {
    document
      .getElementById("postForm")
      ?.addEventListener("submit", (e) => this.handlePost(e));
    document
      .getElementById("aiGenBtn")
      ?.addEventListener("click", () => this.generateAIText());
    document
      .getElementById("scheduleBtn")
      ?.addEventListener("click", () => this.schedulePost());
    this.platforms.forEach((p) => {
      document
        .getElementById(`${p}Check`)
        ?.addEventListener("change", () => this.updateCharCount());
    });
    document
      .getElementById("postContent")
      ?.addEventListener("input", () => this.updateCharCount());
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
  async loadStatus() {
    const data = await this.apiCall(CONFIG.ENDPOINTS.HEALTH);
    this.platforms.forEach((p) => {
      const card = document.getElementById(`${p}Card`);
      if (card)
        card.classList.toggle(
          "connected",
          data?.platforms?.[p]?.connected || false,
        );
    });
    document.getElementById("agentStatus").textContent =
      data?.status || "offline";
    document.getElementById("agentStatus").className =
      `badge ${data?.status === "ok" ? "bg-success" : "bg-danger"}`;
  }
  async loadMetrics() {
    const data = await this.apiCall(CONFIG.ENDPOINTS.METRICS);
    if (data) {
      document.getElementById("totalPosts").textContent = data.total_posts || 0;
      document.getElementById("scheduledCount").textContent =
        data.scheduled_count || 0;
      document.getElementById("aiGenerations").textContent =
        data.ai_generations || 0;
      document.getElementById("engagementRate").textContent =
        (data.engagement_rate || 0).toFixed(1) + "%";
    }
  }
  async loadQueue() {
    const data = await this.apiCall(CONFIG.ENDPOINTS.QUEUE);
    const tbody = document.getElementById("queueTable")?.querySelector("tbody");
    if (tbody && data?.queue) {
      tbody.innerHTML = data.queue
        .map(
          (item) =>
            `<tr><td>${this.formatDate(item.scheduled_time)}</td><td>${item.platforms?.join(", ")}</td><td><span class="badge bg-secondary">${item.status}</span></td><td><button class="btn btn-sm btn-outline-danger" onclick="dashboard.cancelPost('${item.id}')">×</button></td></tr>`,
        )
        .join("");
    }
  }
  async handlePost(e) {
    e.preventDefault();
    const content = document.getElementById("postContent").value;
    const platforms = this.platforms.filter(
      (p) => document.getElementById(`${p}Check`)?.checked,
    );
    if (!content || !platforms.length) {
      this.toast(
        "Inhalt und mindestens eine Plattform erforderlich",
        "warning",
      );
      return;
    }
    const res = await this.apiCall(CONFIG.ENDPOINTS.COMMAND, "POST", {
      action: "post_now",
      content,
      platforms,
    });
    if (res?.success) {
      this.toast("Erfolgreich gepostet!", "success");
      document.getElementById("postForm").reset();
      await this.loadMetrics();
    } else this.toast("Fehler beim Posten", "danger");
  }
  async schedulePost() {
    const content = document.getElementById("postContent").value;
    const platforms = this.platforms.filter(
      (p) => document.getElementById(`${p}Check`)?.checked,
    );
    const time = document.getElementById("scheduleTime")?.value;
    if (!content || !platforms.length || !time) {
      this.toast("Alle Felder erforderlich", "warning");
      return;
    }
    const res = await this.apiCall(CONFIG.ENDPOINTS.COMMAND, "POST", {
      action: "schedule",
      content,
      platforms,
      scheduled_time: time,
    });
    if (res?.success) {
      this.toast("Geplant!", "success");
      await this.loadQueue();
    }
  }
  async generateAIText() {
    const topic = document.getElementById("aiTopic")?.value || "allgemein";
    const res = await this.apiCall(CONFIG.ENDPOINTS.SPECIALIZED, "POST", {
      action: "generate_text",
      topic,
    });
    if (res?.text) document.getElementById("postContent").value = res.text;
  }
  async cancelPost(id) {
    await this.apiCall(CONFIG.ENDPOINTS.COMMAND, "POST", {
      action: "cancel",
      post_id: id,
    });
    await this.loadQueue();
  }
  updateCharCount() {
    const content = document.getElementById("postContent")?.value || "";
    const active = this.platforms.filter(
      (p) => document.getElementById(`${p}Check`)?.checked,
    );
    const minLimit = Math.min(
      ...active.map((p) => CONFIG.PLATFORMS[p]?.charLimit || 9999),
    );
    const counter = document.getElementById("charCount");
    if (counter) {
      counter.textContent = `${content.length} / ${minLimit}`;
      counter.className =
        content.length > minLimit ? "text-danger" : "text-muted";
    }
  }
  formatDate(iso) {
    return new Date(iso).toLocaleString(CONFIG.UI.DATE_LOCALE);
  }
  toast(msg, type = "info") {
    const c = document.getElementById("toastContainer");
    if (c) {
      const t = document.createElement("div");
      t.className = `toast show bg-${type}`;
      t.innerHTML = `<div class="toast-body text-white">${msg}</div>`;
      c.appendChild(t);
      setTimeout(() => t.remove(), CONFIG.UI.TOAST_DURATION);
    }
  }
  startIntervals() {
    setInterval(() => this.loadStatus(), CONFIG.REFRESH_INTERVALS.STATUS);
    setInterval(() => this.loadMetrics(), CONFIG.REFRESH_INTERVALS.METRICS);
    setInterval(() => this.loadQueue(), CONFIG.REFRESH_INTERVALS.QUEUE);
  }
}
const dashboard = new SocialMediaDashboard();
