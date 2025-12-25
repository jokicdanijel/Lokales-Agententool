/* WhatsApp Agent PAS-6.0 | Application Logic | Port 12352 */
class WhatsAppDashboard {
  constructor(config) {
    this.config = config;
    this.state = {
      connected: false,
      qrVisible: false,
      conversations: [],
      contacts: [],
      templates: [],
      media: [],
      webhooks: [],
      analytics: {},
      selectedConversation: null,
      metrics: {
        sent: 0,
        received: 0,
        pending: 0,
        failed: 0,
        contacts: 0,
        templates: 0,
      },
    };
    this.refreshInterval = null;
  }

  async init() {
    console.log(
      `🟢 WhatsApp Agent Dashboard v${this.config.agent.version} initializing...`,
    );
    this.bindNavigation();
    this.bindActions();
    this.bindModals();
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
      case "inbox":
        await this.loadConversations();
        break;
      case "contacts":
        await this.loadContacts();
        break;
      case "media":
        await this.loadMedia();
        break;
      case "templates":
        await this.loadTemplates();
        break;
      case "webhooks":
        await this.loadWebhooks();
        break;
      case "analytics":
        await this.loadAnalytics();
        break;
    }
  }

  bindActions() {
    document
      .getElementById("sendMessageBtn")
      ?.addEventListener("click", () => this.showComposeModal());
    document
      .getElementById("refreshBtn")
      ?.addEventListener("click", () => this.checkHealth());
    document
      .getElementById("syncContactsBtn")
      ?.addEventListener("click", () => this.syncContacts());
    document
      .getElementById("showQrBtn")
      ?.addEventListener("click", () => this.showQRCode());
    document
      .getElementById("testApiBtn")
      ?.addEventListener("click", () => this.testApi());
    document
      .getElementById("addContactBtn")
      ?.addEventListener("click", () => this.showAddContactModal());
    document
      .getElementById("newTemplateBtn")
      ?.addEventListener("click", () => this.showNewTemplateModal());
    document
      .getElementById("registerWebhookBtn")
      ?.addEventListener("click", () => this.showWebhookModal());

    // Quick Actions
    document.querySelectorAll(".action-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const action = btn.dataset.action;
        if (action && typeof this[action] === "function") this[action]();
      });
    });

    // Capability Cards
    document.querySelectorAll(".capability-card").forEach((card) => {
      card.addEventListener("click", () => {
        const capability = card.dataset.capability;
        this.executeCapability(capability);
      });
    });
  }

  bindModals() {
    document.querySelectorAll(".modal-close").forEach((btn) => {
      btn.addEventListener("click", () => this.closeModals());
    });
    document.querySelectorAll(".modal").forEach((modal) => {
      modal.addEventListener("click", (e) => {
        if (e.target === modal) this.closeModals();
      });
    });

    // Compose Modal
    document
      .getElementById("sendComposeBtn")
      ?.addEventListener("click", () => this.sendComposedMessage());
    document
      .getElementById("attachMediaBtn")
      ?.addEventListener("click", () => this.attachMedia());
  }

  closeModals() {
    document
      .querySelectorAll(".modal")
      .forEach((m) => m.classList.remove("active"));
  }

  // ==================== API CALLS ====================
  async apiCall(endpoint, method = "GET", data = null) {
    try {
      const url = `${this.config.agent.baseUrl}${endpoint}`;
      const options = {
        method,
        headers: { "Content-Type": "application/json" },
        timeout: this.config.api.timeout,
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
      this.showToast("WhatsApp verbunden", "success");
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
    const [health, status, stats] = await Promise.all([
      this.apiCall(this.config.api.endpoints.health),
      this.apiCall(this.config.api.endpoints.accountStatus),
      this.apiCall(this.config.api.endpoints.messageStats),
    ]);

    if (!stats.error) {
      this.updateMetric("msgSent", stats.sent || 0);
      this.updateMetric("msgReceived", stats.received || 0);
      this.updateMetric("msgPending", stats.pending || 0);
      this.updateMetric("msgDelivered", stats.delivered || 0);
      this.updateMetric("contactCount", stats.contacts || 0);
      this.updateMetric("templateCount", stats.templates || 0);
    }
  }

  updateMetric(id, value) {
    const el = document.getElementById(id);
    if (el)
      el.textContent =
        typeof value === "number" ? value.toLocaleString("de-DE") : value;
  }

  // ==================== INBOX ====================
  async loadConversations() {
    const result = await this.apiCall(this.config.api.endpoints.conversations);
    if (!result.error && result.conversations) {
      this.state.conversations = result.conversations;
      this.renderConversationList();
    }
  }

  renderConversationList() {
    const container = document.getElementById("conversationList");
    if (!container) return;

    if (this.state.conversations.length === 0) {
      container.innerHTML = '<div class="loading">Keine Konversationen</div>';
      return;
    }

    container.innerHTML = this.state.conversations
      .map(
        (conv) => `
            <div class="conversation-item ${conv.id === this.state.selectedConversation ? "active" : ""}"
                 data-id="${conv.id}" onclick="dashboard.selectConversation('${conv.id}')">
                <div class="conv-avatar">${conv.name?.charAt(0) || "?"}</div>
                <div class="conv-info">
                    <div class="conv-name">${conv.name || conv.phone}</div>
                    <div class="conv-preview">${conv.lastMessage || ""}</div>
                </div>
                <div class="conv-time">${conv.time || ""}</div>
            </div>
        `,
      )
      .join("");
  }

  async selectConversation(convId) {
    this.state.selectedConversation = convId;
    this.renderConversationList();
    await this.loadMessages(convId);
  }

  async loadMessages(convId) {
    const result = await this.apiCall(
      `${this.config.api.endpoints.conversationHistory}?id=${convId}`,
    );
    if (!result.error && result.messages) {
      this.renderMessages(result.messages);
    }
  }

  renderMessages(messages) {
    const container = document.getElementById("messageList");
    if (!container) return;

    container.innerHTML = messages
      .map(
        (msg) => `
            <div class="message ${msg.fromMe ? "outgoing" : "incoming"}">
                <div class="message-text">${msg.text}</div>
                <div class="message-time">${msg.time || ""}</div>
            </div>
        `,
      )
      .join("");
    container.scrollTop = container.scrollHeight;
  }

  // ==================== CONTACTS ====================
  async loadContacts() {
    const result = await this.apiCall(this.config.api.endpoints.contacts);
    if (!result.error && result.contacts) {
      this.state.contacts = result.contacts;
      this.renderContacts();
    }
  }

  renderContacts() {
    const container = document.getElementById("contactList");
    if (!container) return;

    if (this.state.contacts.length === 0) {
      container.innerHTML = '<div class="loading">Keine Kontakte</div>';
      return;
    }

    container.innerHTML = this.state.contacts
      .map(
        (contact) => `
            <div class="contact-item" data-phone="${contact.phone}">
                <div class="contact-avatar">${contact.name?.charAt(0) || "📱"}</div>
                <div class="contact-info">
                    <div class="contact-name">${contact.name || "Unknown"}</div>
                    <div class="contact-phone">${contact.phone}</div>
                </div>
                <button class="btn btn-sm btn-primary" onclick="dashboard.sendToContact('${contact.phone}')">💬</button>
            </div>
        `,
      )
      .join("");
  }

  async syncContacts() {
    this.showToast("Kontakte synchronisieren...", "info");
    const result = await this.apiCall(
      this.config.api.endpoints.syncContacts,
      "POST",
    );
    if (!result.error) {
      this.showToast(
        `${result.synced || 0} Kontakte synchronisiert`,
        "success",
      );
      await this.loadContacts();
    } else {
      this.showToast("Sync fehlgeschlagen", "error");
    }
  }

  sendToContact(phone) {
    document.getElementById("composeRecipient").value = phone;
    this.showComposeModal();
  }

  // ==================== SEND MESSAGE ====================
  showComposeModal() {
    document.getElementById("composeModal")?.classList.add("active");
  }

  async sendComposedMessage() {
    const recipient = document.getElementById("composeRecipient")?.value;
    const message = document.getElementById("composeMessage")?.value;

    if (!recipient || !message) {
      this.showToast("Empfänger und Nachricht erforderlich", "warning");
      return;
    }

    this.showToast("Sende Nachricht...", "info");
    const result = await this.apiCall(
      this.config.api.endpoints.sendMessage,
      "POST",
      {
        to: recipient,
        message: message,
      },
    );

    if (!result.error) {
      this.showToast("Nachricht gesendet! ✅", "success");
      this.closeModals();
      document.getElementById("composeRecipient").value = "";
      document.getElementById("composeMessage").value = "";
    } else {
      this.showToast("Senden fehlgeschlagen", "error");
    }
  }

  // ==================== MEDIA ====================
  async loadMedia() {
    const result = await this.apiCall(this.config.api.endpoints.mediaGallery);
    if (!result.error && result.media) {
      this.state.media = result.media;
      this.renderMediaGallery();
    }
  }

  renderMediaGallery() {
    const container = document.getElementById("mediaGallery");
    if (!container) return;

    if (this.state.media.length === 0) {
      container.innerHTML = '<div class="loading">Keine Medien</div>';
      return;
    }

    container.innerHTML = this.state.media
      .map(
        (item) => `
            <div class="media-item" data-id="${item.id}" onclick="dashboard.viewMedia('${item.id}')">
                ${item.type === "image" ? "🖼️" : item.type === "video" ? "🎬" : item.type === "audio" ? "🎵" : "📄"}
            </div>
        `,
      )
      .join("");
  }

  showMediaModal() {
    document.getElementById("mediaModal")?.classList.add("active");
  }

  attachMedia() {
    document.getElementById("mediaFileInput")?.click();
  }

  // ==================== TEMPLATES ====================
  async loadTemplates() {
    const result = await this.apiCall(this.config.api.endpoints.templates);
    if (!result.error && result.templates) {
      this.state.templates = result.templates;
      this.renderTemplates();
    }
  }

  renderTemplates() {
    const container = document.getElementById("templatesGrid");
    if (!container) return;

    if (this.state.templates.length === 0) {
      container.innerHTML = '<div class="loading">Keine Templates</div>';
      return;
    }

    container.innerHTML = this.state.templates
      .map(
        (tpl) => `
            <div class="template-card">
                <div class="template-header">
                    <span class="template-name">${tpl.name}</span>
                    <span class="template-status ${tpl.status}">${tpl.status}</span>
                </div>
                <div class="template-content">${tpl.content}</div>
                <div class="template-actions">
                    <button class="btn btn-sm btn-primary" onclick="dashboard.useTemplate('${tpl.id}')">Verwenden</button>
                    <button class="btn btn-sm btn-secondary" onclick="dashboard.editTemplate('${tpl.id}')">Bearbeiten</button>
                </div>
            </div>
        `,
      )
      .join("");
  }

  showTemplateModal() {
    document.getElementById("templateModal")?.classList.add("active");
  }

  showNewTemplateModal() {
    document.getElementById("newTemplateModal")?.classList.add("active");
  }

  async useTemplate(templateId) {
    const template = this.state.templates.find((t) => t.id === templateId);
    if (template) {
      document.getElementById("composeMessage").value = template.content;
      this.showComposeModal();
    }
  }

  // ==================== WEBHOOKS ====================
  async loadWebhooks() {
    const result = await this.apiCall(this.config.api.endpoints.webhooks);
    if (!result.error && result.webhooks) {
      this.state.webhooks = result.webhooks;
      this.renderWebhooks();
    }
  }

  renderWebhooks() {
    const container = document.getElementById("webhookList");
    if (!container) return;

    if (this.state.webhooks.length === 0) {
      container.innerHTML =
        '<div class="loading">Keine Webhooks registriert</div>';
      return;
    }

    container.innerHTML = this.state.webhooks
      .map(
        (wh) => `
            <div class="webhook-item">
                <span class="webhook-url">${wh.url}</span>
                <span class="webhook-events">${wh.events?.join(", ") || "all"}</span>
                <button class="btn btn-sm btn-secondary" onclick="dashboard.deleteWebhook('${wh.id}')">🗑️</button>
            </div>
        `,
      )
      .join("");
  }

  showWebhookModal() {
    document.getElementById("webhookModal")?.classList.add("active");
  }

  async registerWebhook() {
    const url = document.getElementById("webhookUrl")?.value;
    const events = Array.from(
      document.querySelectorAll(".webhook-event:checked"),
    ).map((cb) => cb.value);

    if (!url) {
      this.showToast("URL erforderlich", "warning");
      return;
    }

    const result = await this.apiCall(
      this.config.api.endpoints.webhookRegister,
      "POST",
      { url, events },
    );
    if (!result.error) {
      this.showToast("Webhook registriert", "success");
      this.closeModals();
      await this.loadWebhooks();
    } else {
      this.showToast("Registrierung fehlgeschlagen", "error");
    }
  }

  async deleteWebhook(id) {
    const result = await this.apiCall(
      `${this.config.api.endpoints.webhookDelete}?id=${id}`,
      "DELETE",
    );
    if (!result.error) {
      this.showToast("Webhook gelöscht", "success");
      await this.loadWebhooks();
    }
  }

  // ==================== ANALYTICS ====================
  async loadAnalytics() {
    const result = await this.apiCall(this.config.api.endpoints.analytics);
    if (!result.error) {
      this.state.analytics = result;
      this.renderAnalytics();
    }
  }

  renderAnalytics() {
    // Update analytics displays
    const data = this.state.analytics;
    if (data.daily) {
      this.updateMetric("analyticsSent", data.daily.sent || 0);
      this.updateMetric("analyticsReceived", data.daily.received || 0);
      this.updateMetric(
        "analyticsDeliveryRate",
        `${data.daily.deliveryRate || 0}%`,
      );
      this.updateMetric("analyticsReadRate", `${data.daily.readRate || 0}%`);
    }
  }

  // ==================== QR CODE ====================
  async showQRCode() {
    const result = await this.apiCall(this.config.api.endpoints.qrCode);
    if (!result.error && result.qr) {
      document.getElementById("qrCodeImage").src = result.qr;
      document.getElementById("qrModal")?.classList.add("active");
    } else {
      this.showToast("QR-Code nicht verfügbar", "warning");
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

  // ==================== CAPABILITIES ====================
  executeCapability(capabilityId) {
    const capability = this.config.capabilities.find(
      (c) => c.id === capabilityId,
    );
    if (!capability) return;

    switch (capabilityId) {
      case "incoming_messages":
        this.showSection("inbox");
        break;
      case "outgoing_messages":
        this.showComposeModal();
        break;
      case "media_messages":
        this.showMediaModal();
        break;
      case "contact_manager":
        this.showSection("contacts");
        break;
      case "template_api":
        this.showSection("templates");
        break;
      case "webhook_listener":
        this.showSection("webhooks");
        break;
      case "conversation_history":
        this.showSection("inbox");
        break;
      case "account_health":
        this.checkHealth();
        break;
      default:
        this.showToast(`${capability.name} aktiviert`, "info");
    }
  }

  // ==================== BROADCAST ====================
  showBroadcastModal() {
    document.getElementById("broadcastModal")?.classList.add("active");
  }

  async sendBroadcast() {
    const recipients = document
      .getElementById("broadcastRecipients")
      ?.value.split("\n")
      .filter((r) => r.trim());
    const message = document.getElementById("broadcastMessage")?.value;

    if (recipients.length === 0 || !message) {
      this.showToast("Empfänger und Nachricht erforderlich", "warning");
      return;
    }

    this.showToast(`Broadcast an ${recipients.length} Empfänger...`, "info");

    let success = 0;
    for (const recipient of recipients) {
      const result = await this.apiCall(
        this.config.api.endpoints.sendMessage,
        "POST",
        {
          to: recipient.trim(),
          message: message,
        },
      );
      if (!result.error) success++;
    }

    this.showToast(
      `${success}/${recipients.length} gesendet`,
      success === recipients.length ? "success" : "warning",
    );
    this.closeModals();
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
    this.refreshInterval = setInterval(() => {
      this.checkHealth();
    }, this.config.ui.refreshInterval);
  }

  stopAutoRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }
  }

  showAddContactModal() {
    document.getElementById("addContactModal")?.classList.add("active");
  }

  viewMedia(id) {
    this.showToast(`Media ${id} öffnen...`, "info");
  }

  editTemplate(id) {
    this.showToast(`Template ${id} bearbeiten...`, "info");
  }
}

// Initialize on DOM ready
let dashboard;
document.addEventListener("DOMContentLoaded", () => {
  dashboard = new WhatsAppDashboard(WhatsAppConfig);
  dashboard.init();
});
