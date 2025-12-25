class InfluencerDashboard {
  constructor() {
    this.profiles = [];
    this.campaigns = [];
    this.startTime = Date.now();
    this.init();
  }
  async init() {
    this.bindEvents();
    await this.loadHealth();
    await this.loadProfiles();
    await this.loadCampaigns();
    this.startIntervals();
    this.updateUptime();
    setInterval(() => this.updateUptime(), 1000);
  }
  bindEvents() {
    document
      .getElementById("profile-form")
      ?.addEventListener("submit", (e) => this.createProfile(e));
    document
      .getElementById("campaign-form")
      ?.addEventListener("submit", (e) => this.createCampaign(e));
    document
      .getElementById("match-form")
      ?.addEventListener("submit", (e) => this.runMatching(e));
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
      document.getElementById("total-profiles").textContent =
        data.total_profiles || 0;
      document.getElementById("total-campaigns").textContent =
        data.total_campaigns || 0;
      document.getElementById("total-matches").textContent =
        data.total_matches || 0;
    } else {
      status.className = "status-indicator status-error";
      status.querySelector(".status-text").textContent = "Offline";
    }
  }
  async loadProfiles() {
    const data = await this.apiCall(CONFIG.ENDPOINTS.PROFILES_LIST);
    if (data?.profiles) {
      this.profiles = data.profiles;
      this.renderProfiles();
      this.updatePlatformMetrics();
    }
  }
  async loadCampaigns() {
    const data = await this.apiCall(CONFIG.ENDPOINTS.CAMPAIGNS_LIST);
    if (data?.campaigns) {
      this.campaigns = data.campaigns;
      this.updateCampaignSelect();
    }
  }
  async createProfile(e) {
    e.preventDefault();
    const profile = {
      name: document.getElementById("profile-name").value,
      platform: document.getElementById("profile-platform").value,
      followers:
        parseInt(document.getElementById("profile-followers").value) || 0,
      engagement_rate:
        parseFloat(document.getElementById("profile-engagement").value) || 0,
      niche: document.getElementById("profile-niche").value,
      contact_email: document.getElementById("profile-email").value,
    };
    const res = await this.apiCall(
      CONFIG.ENDPOINTS.PROFILES_CREATE,
      "POST",
      profile,
    );
    if (res?.profile_id) {
      this.toast("Profil erstellt!", "success");
      document.getElementById("profile-form").reset();
      await this.loadProfiles();
      await this.loadHealth();
      this.addActivity(`Profil "${profile.name}" erstellt`);
    } else this.toast("Fehler beim Erstellen", "danger");
  }
  async createCampaign(e) {
    e.preventDefault();
    const campaign = {
      name: document.getElementById("campaign-name").value,
      budget: parseFloat(document.getElementById("campaign-budget").value) || 0,
      min_followers:
        parseInt(document.getElementById("campaign-min-followers").value) || 0,
      target_audience: document.getElementById("campaign-audience").value,
      start_date: document.getElementById("campaign-start").value,
      end_date: document.getElementById("campaign-end").value,
    };
    const res = await this.apiCall(
      CONFIG.ENDPOINTS.CAMPAIGNS_CREATE,
      "POST",
      campaign,
    );
    if (res?.campaign_id) {
      this.toast("Kampagne erstellt!", "success");
      document.getElementById("campaign-form").reset();
      await this.loadCampaigns();
      await this.loadHealth();
      this.addActivity(`Kampagne "${campaign.name}" gestartet`);
    } else this.toast("Fehler beim Erstellen", "danger");
  }
  async runMatching(e) {
    e.preventDefault();
    const campaignId = document.getElementById("match-campaign").value;
    if (!campaignId) {
      this.toast("Bitte Kampagne wählen", "warning");
      return;
    }
    const matchReq = {
      campaign_id: campaignId,
      max_results: parseInt(document.getElementById("match-max").value) || 10,
      min_score:
        parseFloat(document.getElementById("match-min-score").value) || 60,
    };
    const res = await this.apiCall(CONFIG.ENDPOINTS.MATCH, "POST", matchReq);
    if (res?.matches) {
      this.renderMatches(res.matches);
      this.toast(`${res.matches.length} Matches gefunden!`, "success");
      this.addActivity(
        `Matching durchgeführt: ${res.matches.length} Ergebnisse`,
      );
    } else this.toast("Keine Matches gefunden", "warning");
  }
  renderProfiles() {
    const container = document.getElementById("profiles-list");
    document.getElementById("profiles-count").textContent =
      this.profiles.length;
    if (!this.profiles.length) {
      container.innerHTML = '<p class="empty-state">Keine Profile</p>';
      return;
    }
    container.innerHTML = this.profiles
      .slice(0, 20)
      .map(
        (p) => `
            <div class="profile-item">
                <div><strong>${p.name}</strong><br><small>${p.platform} • ${this.formatNumber(p.followers)} Follower • ${p.engagement_rate}%</small></div>
                <button class="btn btn-sm btn-secondary" onclick="dashboard.deleteProfile('${p.id}')">✕</button>
            </div>
        `,
      )
      .join("");
  }
  renderMatches(matches) {
    const container = document.getElementById("match-results");
    if (!matches.length) {
      container.innerHTML = '<p class="empty-state">Keine Matches</p>';
      return;
    }
    container.innerHTML = matches
      .map(
        (m) => `
            <div class="match-item">
                <div><strong>${m.profile?.name || "Unknown"}</strong><br><small>${m.reasoning || ""}</small></div>
                <span class="match-score">${m.score}%</span>
            </div>
        `,
      )
      .join("");
  }
  updateCampaignSelect() {
    const select = document.getElementById("match-campaign");
    select.innerHTML =
      '<option value="">-- Kampagne wählen --</option>' +
      this.campaigns
        .map((c) => `<option value="${c.id}">${c.name}</option>`)
        .join("");
  }
  updatePlatformMetrics() {
    const counts = {};
    CONFIG.PLATFORMS.forEach((p) => (counts[p] = 0));
    let totalEng = 0;
    this.profiles.forEach((p) => {
      counts[p.platform] = (counts[p.platform] || 0) + 1;
      totalEng += p.engagement_rate || 0;
    });
    document.getElementById("instagram-count").textContent =
      counts.instagram || 0;
    document.getElementById("tiktok-count").textContent = counts.tiktok || 0;
    document.getElementById("youtube-count").textContent = counts.youtube || 0;
    document.getElementById("x-count").textContent = counts.x || 0;
    document.getElementById("linkedin-count").textContent =
      counts.linkedin || 0;
    document.getElementById("avg-engagement").textContent = this.profiles.length
      ? (totalEng / this.profiles.length).toFixed(1) + "%"
      : "0%";
    document.getElementById("total-reach").textContent = this.formatNumber(
      this.profiles.reduce((s, p) => s + (p.followers || 0), 0),
    );
  }
  async deleteProfile(id) {
    const res = await this.apiCall(CONFIG.ENDPOINTS.PROFILES_DELETE, "POST", {
      profile_id: id,
    });
    if (res?.success) {
      this.toast("Profil gelöscht", "success");
      await this.loadProfiles();
      await this.loadHealth();
    }
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
  formatNumber(n) {
    return n >= 1e6
      ? (n / 1e6).toFixed(1) + "M"
      : n >= 1e3
        ? (n / 1e3).toFixed(1) + "K"
        : n.toString();
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
    setInterval(() => this.loadProfiles(), CONFIG.REFRESH_INTERVALS.PROFILES);
  }
}
function saveToken() {
  const token = document.getElementById("token").value;
  if (token) {
    localStorage.setItem(CONFIG.AUTH.TOKEN_KEY, token);
    dashboard.toast("Token gespeichert", "success");
  }
}
const dashboard = new InfluencerDashboard();
