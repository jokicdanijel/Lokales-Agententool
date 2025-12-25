/**
 * PORTIER PAS-6.0 Dashboard Application
 * Agent: opena4 - Telegram Mobile Agent
 * Version: 6.0.0
 *
 * Implements all 12 Telegram Capabilities:
 * 1. Outgoing Message Sender
 * 2. Incoming Message Listener
 * 3. Media Handling
 * 4. Contact Manager
 * 5. AI Reply Assistant
 * 6. Rate Limit Manager
 * 7. Conversation Context Engine
 * 8. Template Message Engine
 * 9. Webhook Receiver
 * 10. Chat Analytics
 * 11. Multi-Chat Routing
 * 12. Error Recovery & Retry Engine
 */

class TelegramDashboard {
  constructor() {
    this.config = CONFIG;
    this.currentSection = "overview";
    this.isOnline = false;
    this.refreshTimer = null;
    this.logs = [];
    this.contacts = [];
    this.templates = [];
    this.webhookEvents = [];
    this.messageHistory = [];
    this.retryQueue = [];

    this.init();
  }

  // ==================== INITIALIZATION ====================

  async init() {
    this.log("info", "Telegram Dashboard 6.0 initialisiert");
    this.bindEvents();
    this.loadStoredData();
    await this.checkHealth();
    this.startAutoRefresh();
    this.showSection(this.config.ui.defaultSection);
  }

  bindEvents() {
    // Navigation
    document.querySelectorAll(".nav-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const section = e.target.dataset.section;
        this.showSection(section);
      });
    });

    // Capability items click
    document.querySelectorAll(".capability-item").forEach((item) => {
      item.addEventListener("click", (e) => {
        const section = e.currentTarget.dataset.section;
        if (section) this.showSection(section);
      });
    });

    // Forms
    this.bindFormEvents();

    // Modal close
    document.querySelectorAll(".modal-close").forEach((btn) => {
      btn.addEventListener("click", () => this.closeModal());
    });

    // Close modal on backdrop click
    document.getElementById("modal")?.addEventListener("click", (e) => {
      if (e.target.classList.contains("modal")) {
        this.closeModal();
      }
    });

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") this.closeModal();
    });
  }

  bindFormEvents() {
    // Send Message Form
    document
      .getElementById("sendMessageForm")
      ?.addEventListener("submit", (e) => {
        e.preventDefault();
        this.sendMessage();
      });

    // Bulk Message Form
    document
      .getElementById("bulkMessageForm")
      ?.addEventListener("submit", (e) => {
        e.preventDefault();
        this.sendBulkMessage();
      });

    // Add Contact Form
    document
      .getElementById("addContactForm")
      ?.addEventListener("submit", (e) => {
        e.preventDefault();
        this.addContact();
      });

    // Media Send Form
    document
      .getElementById("mediaSendForm")
      ?.addEventListener("submit", (e) => {
        e.preventDefault();
        this.sendMedia();
      });

    // AI Test Form
    document.getElementById("aiTestForm")?.addEventListener("submit", (e) => {
      e.preventDefault();
      this.testAiReply();
    });

    // Webhook Config Form
    document
      .getElementById("webhookConfigForm")
      ?.addEventListener("submit", (e) => {
        e.preventDefault();
        this.updateWebhookConfig();
      });

    // Template Form
    document.getElementById("templateForm")?.addEventListener("submit", (e) => {
      e.preventDefault();
      this.saveTemplate();
    });

    // Settings Form
    document.getElementById("settingsForm")?.addEventListener("submit", (e) => {
      e.preventDefault();
      this.saveSettings();
    });

    // Upload Zone
    const uploadZone = document.getElementById("uploadZone");
    if (uploadZone) {
      uploadZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadZone.classList.add("dragover");
      });
      uploadZone.addEventListener("dragleave", () => {
        uploadZone.classList.remove("dragover");
      });
      uploadZone.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadZone.classList.remove("dragover");
        this.handleFileDrop(e.dataTransfer.files);
      });
      uploadZone.addEventListener("click", () => {
        document.getElementById("fileInput")?.click();
      });
    }

    // File Input
    document.getElementById("fileInput")?.addEventListener("change", (e) => {
      this.handleFileDrop(e.target.files);
    });

    // Contact Search
    document.getElementById("contactSearch")?.addEventListener("input", (e) => {
      this.filterContacts(e.target.value);
    });

    // Log Level Filter
    document.getElementById("logLevel")?.addEventListener("change", (e) => {
      this.filterLogs(e.target.value);
    });
  }

  loadStoredData() {
    // Load contacts from localStorage
    const storedContacts = localStorage.getItem(this.config.storage.contacts);
    if (storedContacts) {
      this.contacts = JSON.parse(storedContacts);
    }

    // Load templates
    const storedTemplates = localStorage.getItem(this.config.storage.templates);
    if (storedTemplates) {
      this.templates = JSON.parse(storedTemplates);
    }
  }

  // ==================== NAVIGATION ====================

  showSection(sectionId) {
    document
      .querySelectorAll(".section")
      .forEach((s) => s.classList.remove("active"));
    document
      .querySelectorAll(".nav-btn")
      .forEach((b) => b.classList.remove("active"));

    const section = document.getElementById(sectionId);
    const navBtn = document.querySelector(`[data-section="${sectionId}"]`);

    if (section) {
      section.classList.add("active");
      this.currentSection = sectionId;
      localStorage.setItem(this.config.storage.lastSection, sectionId);
    }
    if (navBtn) navBtn.classList.add("active");

    // Load section-specific data
    this.loadSectionData(sectionId);
  }

  async loadSectionData(sectionId) {
    switch (sectionId) {
      case "overview":
        await this.loadOverviewData();
        break;
      case "messaging":
        await this.loadMessageHistory();
        break;
      case "contacts":
        this.renderContacts();
        break;
      case "media":
        await this.loadMediaGallery();
        break;
      case "webhook":
        await this.loadWebhookStatus();
        break;
      case "analytics":
        await this.loadAnalytics();
        break;
      case "templates":
        this.renderTemplates();
        break;
      case "logs":
        this.renderLogs();
        break;
    }
  }

  // ==================== CORE API ====================

  async apiCall(endpoint, method = "GET", data = null) {
    const url = `${this.config.api.baseUrl}${endpoint}`;
    const options = {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem(this.config.storage.bearerToken) || ""}`,
      },
    };

    if (data && method !== "GET") {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || result.message || "API Error");
      }

      return result;
    } catch (error) {
      this.log("error", `API Fehler: ${error.message}`);
      // Add to retry queue (Capability 12: Error Recovery)
      if (method !== "GET") {
        this.addToRetryQueue({ endpoint, method, data });
      }
      throw error;
    }
  }

  async checkHealth() {
    try {
      const result = await this.apiCall(this.config.api.endpoints.health);
      this.setOnlineStatus(
        result.status === "healthy" || result.status === "ok",
      );
      return result;
    } catch (error) {
      this.setOnlineStatus(false);
      return null;
    }
  }

  setOnlineStatus(online) {
    this.isOnline = online;
    const badge = document.getElementById("statusBadge");
    const text = document.getElementById("statusText");

    if (badge && text) {
      badge.className = `status-badge ${online ? "online" : "offline"}`;
      text.textContent = online ? "Online" : "Offline";
    }
  }

  startAutoRefresh() {
    if (this.refreshTimer) clearInterval(this.refreshTimer);
    this.refreshTimer = setInterval(() => {
      this.checkHealth();
      if (this.currentSection === "overview") {
        this.loadOverviewData();
      }
    }, this.config.ui.refreshInterval);
  }

  // ==================== CAPABILITY 1: OUTGOING MESSAGE SENDER ====================

  async sendMessage() {
    const chatId = document.getElementById("chatId")?.value;
    const message = document.getElementById("messageText")?.value;
    const parseMode = document.getElementById("parseMode")?.value || "HTML";

    if (!chatId || !message) {
      this.showToast("Bitte Chat-ID und Nachricht eingeben", "warning");
      return;
    }

    try {
      const result = await this.apiCall(
        this.config.api.endpoints.sendMessage,
        "POST",
        { chat_id: chatId, text: message, parse_mode: parseMode },
      );

      this.showToast("Nachricht gesendet", "success");
      document.getElementById("messageText").value = "";
      this.log("info", `Nachricht an ${chatId} gesendet`);

      // Add to history
      this.addToMessageHistory({
        type: "sent",
        chat_id: chatId,
        text: message,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      this.showToast(`Fehler: ${error.message}`, "error");
    }
  }

  async sendBulkMessage() {
    const chatIds = document
      .getElementById("bulkChatIds")
      ?.value.split("\n")
      .filter((id) => id.trim());
    const message = document.getElementById("bulkMessageText")?.value;
    const delay = parseInt(document.getElementById("bulkDelay")?.value) || 1000;

    if (!chatIds.length || !message) {
      this.showToast("Bitte Chat-IDs und Nachricht eingeben", "warning");
      return;
    }

    if (chatIds.length > this.config.telegram.rateLimits.bulkLimit) {
      this.showToast(
        `Max. ${this.config.telegram.rateLimits.bulkLimit} Empfänger erlaubt`,
        "warning",
      );
      return;
    }

    try {
      const result = await this.apiCall(
        this.config.api.endpoints.sendBulk,
        "POST",
        { chat_ids: chatIds, text: message, delay_ms: delay },
      );

      this.showToast(
        `Bulk-Nachricht an ${chatIds.length} Empfänger gestartet`,
        "success",
      );
      this.log("info", `Bulk-Nachricht an ${chatIds.length} Chats`);
    } catch (error) {
      this.showToast(`Fehler: ${error.message}`, "error");
    }
  }

  // ==================== CAPABILITY 2: INCOMING MESSAGE LISTENER ====================

  async loadInbox() {
    const inboxList = document.getElementById("inboxList");
    if (!inboxList) return;

    try {
      const result = await this.apiCall("/api/inbox/recent");
      if (result.messages && result.messages.length > 0) {
        inboxList.innerHTML = result.messages
          .map(
            (msg) => `
                    <div class="inbox-item" onclick="dashboard.showMessage('${msg.id}')">
                        <div class="inbox-avatar">${msg.sender.charAt(0).toUpperCase()}</div>
                        <div class="inbox-content">
                            <div class="inbox-sender">${msg.sender}</div>
                            <div class="inbox-preview-text">${msg.text.substring(0, 50)}...</div>
                        </div>
                        <div class="inbox-time">${this.formatTime(msg.timestamp)}</div>
                    </div>
                `,
          )
          .join("");
      } else {
        inboxList.innerHTML =
          '<div class="inbox-empty">Keine neuen Nachrichten</div>';
      }
    } catch (error) {
      inboxList.innerHTML = '<div class="inbox-empty">Verbindungsfehler</div>';
    }
  }

  // ==================== CAPABILITY 3: MEDIA HANDLING ====================

  async sendMedia() {
    const chatId = document.getElementById("mediaChatId")?.value;
    const mediaType = document.getElementById("mediaType")?.value;
    const caption = document.getElementById("mediaCaption")?.value;

    if (!chatId || !this.selectedFile) {
      this.showToast("Bitte Chat-ID und Datei auswählen", "warning");
      return;
    }

    const formData = new FormData();
    formData.append("chat_id", chatId);
    formData.append("type", mediaType);
    formData.append("caption", caption);
    formData.append("file", this.selectedFile);

    try {
      const response = await fetch(
        `${this.config.api.baseUrl}${this.config.api.endpoints.uploadMedia}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem(this.config.storage.bearerToken) || ""}`,
          },
          body: formData,
        },
      );

      const result = await response.json();
      this.showToast("Media gesendet", "success");
      this.selectedFile = null;
      document.getElementById("uploadZone").innerHTML =
        "<span>📤</span><p>Drag & Drop oder klicken</p>";
    } catch (error) {
      this.showToast(`Fehler: ${error.message}`, "error");
    }
  }

  handleFileDrop(files) {
    if (files.length === 0) return;

    const file = files[0];
    if (file.size > this.config.telegram.maxMediaSize) {
      this.showToast("Datei zu groß (max. 50MB)", "warning");
      return;
    }

    this.selectedFile = file;
    const uploadZone = document.getElementById("uploadZone");
    if (uploadZone) {
      uploadZone.innerHTML = `<span>✅</span><p>${file.name}</p>`;
    }
    this.log("info", `Datei ausgewählt: ${file.name}`);
  }

  async loadMediaGallery() {
    const gallery = document.getElementById("mediaGallery");
    if (!gallery) return;

    try {
      const result = await this.apiCall(this.config.api.endpoints.mediaGallery);
      if (result.items && result.items.length > 0) {
        gallery.innerHTML = result.items
          .map(
            (item) => `
                    <div class="media-item" onclick="dashboard.previewMedia('${item.id}')">
                        ${this.getMediaIcon(item.type)}
                    </div>
                `,
          )
          .join("");
      } else {
        gallery.innerHTML = '<p class="loading">Keine Medien vorhanden</p>';
      }
    } catch (error) {
      gallery.innerHTML = '<p class="loading">Laden fehlgeschlagen</p>';
    }
  }

  getMediaIcon(type) {
    const icons = {
      photo: "🖼️",
      video: "🎥",
      document: "📄",
      audio: "🎵",
      voice: "🎤",
      sticker: "😀",
    };
    return icons[type] || "📎";
  }

  // ==================== CAPABILITY 4: CONTACT MANAGER ====================

  async addContact() {
    const name = document.getElementById("contactName")?.value;
    const chatId = document.getElementById("contactChatId")?.value;
    const tags = document
      .getElementById("contactTags")
      ?.value.split(",")
      .map((t) => t.trim())
      .filter((t) => t);

    if (!name || !chatId) {
      this.showToast("Name und Chat-ID erforderlich", "warning");
      return;
    }

    const newContact = {
      id: Date.now().toString(),
      name,
      chat_id: chatId,
      tags,
      created: new Date().toISOString(),
    };

    this.contacts.push(newContact);
    this.saveContacts();
    this.renderContacts();

    // Clear form
    document.getElementById("addContactForm").reset();
    this.showToast("Kontakt hinzugefügt", "success");
    this.log("info", `Kontakt erstellt: ${name}`);
  }

  saveContacts() {
    localStorage.setItem(
      this.config.storage.contacts,
      JSON.stringify(this.contacts),
    );
  }

  renderContacts() {
    const list = document.getElementById("contactList");
    if (!list) return;

    if (this.contacts.length === 0) {
      list.innerHTML = '<p class="loading">Keine Kontakte vorhanden</p>';
      return;
    }

    list.innerHTML = this.contacts
      .map(
        (contact) => `
            <div class="contact-item">
                <div class="contact-avatar">${contact.name.charAt(0).toUpperCase()}</div>
                <div class="contact-info">
                    <div class="contact-name">${contact.name}</div>
                    <div class="contact-id">${contact.chat_id}</div>
                </div>
                <div class="contact-tags">
                    ${contact.tags.map((tag) => `<span class="contact-tag">${tag}</span>`).join("")}
                </div>
                <div class="contact-actions">
                    <button class="btn btn-sm btn-secondary" onclick="dashboard.messageContact('${contact.chat_id}')">💬</button>
                    <button class="btn btn-sm btn-danger" onclick="dashboard.deleteContact('${contact.id}')">🗑️</button>
                </div>
            </div>
        `,
      )
      .join("");
  }

  filterContacts(query) {
    const list = document.getElementById("contactList");
    const filtered = this.contacts.filter(
      (c) =>
        c.name.toLowerCase().includes(query.toLowerCase()) ||
        c.chat_id.includes(query) ||
        c.tags.some((t) => t.toLowerCase().includes(query.toLowerCase())),
    );

    // Re-render with filtered list
    if (filtered.length === 0) {
      list.innerHTML = '<p class="loading">Keine Kontakte gefunden</p>';
    } else {
      list.innerHTML = filtered
        .map(
          (contact) => `
                <div class="contact-item">
                    <div class="contact-avatar">${contact.name.charAt(0).toUpperCase()}</div>
                    <div class="contact-info">
                        <div class="contact-name">${contact.name}</div>
                        <div class="contact-id">${contact.chat_id}</div>
                    </div>
                </div>
            `,
        )
        .join("");
    }
  }

  deleteContact(id) {
    this.contacts = this.contacts.filter((c) => c.id !== id);
    this.saveContacts();
    this.renderContacts();
    this.showToast("Kontakt gelöscht", "success");
  }

  messageContact(chatId) {
    this.showSection("messaging");
    document.getElementById("chatId").value = chatId;
  }

  exportContacts() {
    const data = JSON.stringify(this.contacts, null, 2);
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "telegram_contacts.json";
    a.click();
    URL.revokeObjectURL(url);
    this.showToast("Kontakte exportiert", "success");
  }

  // ==================== CAPABILITY 5: AI REPLY ASSISTANT ====================

  async testAiReply() {
    const input = document.getElementById("aiTestInput")?.value;
    const responseDiv = document.getElementById("aiResponse");

    if (!input) {
      this.showToast("Bitte Test-Nachricht eingeben", "warning");
      return;
    }

    responseDiv.innerHTML = '<p class="loading">Generiere Antwort...</p>';

    try {
      const result = await this.apiCall(
        this.config.api.endpoints.aiGenerate,
        "POST",
        {
          message: input,
          settings: {
            model:
              document.getElementById("aiModel")?.value || this.config.ai.model,
            temperature:
              parseFloat(document.getElementById("aiTemperature")?.value) ||
              this.config.ai.temperature,
            max_tokens:
              parseInt(document.getElementById("aiMaxTokens")?.value) ||
              this.config.ai.maxTokens,
          },
        },
      );

      responseDiv.innerHTML = `
                <p class="response-label">AI Antwort:</p>
                <p class="response-content">${result.response || result.text}</p>
            `;
      this.log("info", "AI Antwort generiert");
    } catch (error) {
      responseDiv.innerHTML = `<p class="response-content" style="color:var(--danger)">Fehler: ${error.message}</p>`;
    }
  }

  // ==================== CAPABILITY 6: RATE LIMIT MANAGER ====================

  updateRateLimits() {
    const perSecond = parseInt(document.getElementById("rateMsgPerSec")?.value);
    const perMinute = parseInt(document.getElementById("rateMsgPerMin")?.value);

    this.config.telegram.rateLimits.messagesPerSecond = perSecond;
    this.config.telegram.rateLimits.messagesPerMinute = perMinute;

    this.showToast("Rate Limits aktualisiert", "success");
    this.log("info", `Rate Limits: ${perSecond}/s, ${perMinute}/min`);
  }

  // ==================== CAPABILITY 7: CONVERSATION CONTEXT ENGINE ====================

  async loadConversationContext() {
    const contextDiv = document.getElementById("contextDisplay");
    if (!contextDiv) return;

    try {
      const result = await this.apiCall(this.config.api.endpoints.aiContext);
      contextDiv.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
    } catch (error) {
      contextDiv.innerHTML = "<p>Kontext nicht verfügbar</p>";
    }
  }

  async clearContext() {
    try {
      await this.apiCall("/api/ai/context/clear", "POST");
      this.showToast("Kontext gelöscht", "success");
      document.getElementById("contextDisplay").innerHTML =
        "<p>Kontext gelöscht</p>";
    } catch (error) {
      this.showToast(`Fehler: ${error.message}`, "error");
    }
  }

  // ==================== CAPABILITY 8: TEMPLATE MESSAGE ENGINE ====================

  saveTemplate() {
    const name = document.getElementById("templateName")?.value;
    const category = document.getElementById("templateCategory")?.value;
    const content = document.getElementById("templateContent")?.value;
    const variables = document
      .getElementById("templateVariables")
      ?.value.split(",")
      .map((v) => v.trim())
      .filter((v) => v);

    if (!name || !content) {
      this.showToast("Name und Inhalt erforderlich", "warning");
      return;
    }

    const template = {
      id: Date.now().toString(),
      name,
      category,
      content,
      variables,
      created: new Date().toISOString(),
    };

    this.templates.push(template);
    localStorage.setItem(
      this.config.storage.templates,
      JSON.stringify(this.templates),
    );
    this.renderTemplates();

    document.getElementById("templateForm").reset();
    this.showToast("Template gespeichert", "success");
    this.log("info", `Template erstellt: ${name}`);
  }

  renderTemplates() {
    const list = document.getElementById("templateList");
    if (!list) return;

    if (this.templates.length === 0) {
      list.innerHTML = '<p class="loading">Keine Templates vorhanden</p>';
      return;
    }

    list.innerHTML = this.templates
      .map(
        (tpl) => `
            <div class="template-item">
                <div class="template-header">
                    <span class="template-name">${tpl.name}</span>
                    <span class="template-category">${tpl.category}</span>
                </div>
                <div class="template-preview">${tpl.content.substring(0, 100)}...</div>
                <div class="template-actions">
                    <button class="btn btn-sm btn-primary" onclick="dashboard.useTemplate('${tpl.id}')">Verwenden</button>
                    <button class="btn btn-sm btn-secondary" onclick="dashboard.editTemplate('${tpl.id}')">Bearbeiten</button>
                    <button class="btn btn-sm btn-danger" onclick="dashboard.deleteTemplate('${tpl.id}')">Löschen</button>
                </div>
            </div>
        `,
      )
      .join("");
  }

  useTemplate(id) {
    const template = this.templates.find((t) => t.id === id);
    if (template) {
      this.showSection("messaging");
      document.getElementById("messageText").value = template.content;
      this.showToast(`Template "${template.name}" geladen`, "info");
    }
  }

  deleteTemplate(id) {
    this.templates = this.templates.filter((t) => t.id !== id);
    localStorage.setItem(
      this.config.storage.templates,
      JSON.stringify(this.templates),
    );
    this.renderTemplates();
    this.showToast("Template gelöscht", "success");
  }

  // ==================== CAPABILITY 9: WEBHOOK RECEIVER ====================

  async loadWebhookStatus() {
    try {
      const result = await this.apiCall(
        this.config.api.endpoints.webhookStatus,
      );

      document.getElementById("webhookUrl").textContent =
        result.url || "Nicht konfiguriert";
      document.getElementById("webhookActive").textContent = result.active
        ? "Aktiv"
        : "Inaktiv";
      document.getElementById("webhookLastEvent").textContent =
        result.last_event || "-";
      document.getElementById("webhookPending").textContent =
        result.pending_updates || "0";
    } catch (error) {
      this.log("error", "Webhook Status konnte nicht geladen werden");
    }
  }

  async updateWebhookConfig() {
    const url = document.getElementById("webhookUrlInput")?.value;
    const secret = document.getElementById("webhookSecret")?.value;
    const allowedUpdates = Array.from(
      document.querySelectorAll('input[name="allowedUpdates"]:checked'),
    ).map((cb) => cb.value);

    try {
      await this.apiCall(this.config.api.endpoints.webhookConfig, "POST", {
        url,
        secret,
        allowed_updates: allowedUpdates,
      });

      this.showToast("Webhook konfiguriert", "success");
      await this.loadWebhookStatus();
    } catch (error) {
      this.showToast(`Fehler: ${error.message}`, "error");
    }
  }

  async deleteWebhook() {
    try {
      await this.apiCall("/api/webhook/delete", "POST");
      this.showToast("Webhook gelöscht", "success");
      await this.loadWebhookStatus();
    } catch (error) {
      this.showToast(`Fehler: ${error.message}`, "error");
    }
  }

  // ==================== CAPABILITY 10: CHAT ANALYTICS ====================

  async loadAnalytics() {
    try {
      const result = await this.apiCall(
        this.config.api.endpoints.analyticsOverview,
      );

      // Update metric cards
      document.getElementById("analyticsSent")?.textContent &&
        (document.getElementById("analyticsSent").textContent =
          result.messages_sent || 0);
      document.getElementById("analyticsReceived")?.textContent &&
        (document.getElementById("analyticsReceived").textContent =
          result.messages_received || 0);
      document.getElementById("analyticsActiveChats")?.textContent &&
        (document.getElementById("analyticsActiveChats").textContent =
          result.active_chats || 0);
      document.getElementById("analyticsResponseTime")?.textContent &&
        (document.getElementById("analyticsResponseTime").textContent =
          (result.avg_response_time || 0) + "ms");

      // Load top users
      this.loadTopUsers();
    } catch (error) {
      this.log("error", "Analytics konnten nicht geladen werden");
    }
  }

  async loadTopUsers() {
    const list = document.getElementById("topUsersList");
    if (!list) return;

    try {
      const result = await this.apiCall("/api/analytics/top-users");
      if (result.users && result.users.length > 0) {
        list.innerHTML = result.users
          .map(
            (user, index) => `
                    <div class="top-user-item">
                        <div class="top-user-rank">#${index + 1}</div>
                        <div class="top-user-info">
                            <div class="top-user-name">${user.name}</div>
                            <div class="top-user-stats">${user.messages} Nachrichten</div>
                        </div>
                    </div>
                `,
          )
          .join("");
      } else {
        list.innerHTML = '<p class="loading">Keine Daten vorhanden</p>';
      }
    } catch (error) {
      list.innerHTML = '<p class="loading">Laden fehlgeschlagen</p>';
    }
  }

  exportAnalytics(format) {
    this.showToast(`Export als ${format.toUpperCase()} gestartet`, "info");
    // Implementation would trigger backend export
    this.log("info", `Analytics Export: ${format}`);
  }

  // ==================== CAPABILITY 11: MULTI-CHAT ROUTING ====================

  async loadMessageHistory() {
    const historyDiv = document.getElementById("messageHistory");
    if (!historyDiv) return;

    try {
      const result = await this.apiCall(
        this.config.api.endpoints.messageHistory,
      );
      if (result.messages && result.messages.length > 0) {
        this.messageHistory = result.messages;
        historyDiv.innerHTML = result.messages
          .map(
            (msg) => `
                    <div class="message-item ${msg.direction}">
                        <div><strong>${msg.direction === "sent" ? "📤 Gesendet" : "📥 Empfangen"}</strong></div>
                        <div>${msg.text}</div>
                        <div style="font-size:0.8rem;color:var(--text-muted)">${this.formatTime(msg.timestamp)}</div>
                    </div>
                `,
          )
          .join("");
      } else {
        historyDiv.innerHTML = '<p class="loading">Keine Nachrichten</p>';
      }
    } catch (error) {
      historyDiv.innerHTML = '<p class="loading">Laden fehlgeschlagen</p>';
    }
  }

  addToMessageHistory(message) {
    this.messageHistory.unshift(message);
    if (this.messageHistory.length > 100) {
      this.messageHistory.pop();
    }
  }

  // ==================== CAPABILITY 12: ERROR RECOVERY & RETRY ENGINE ====================

  addToRetryQueue(item) {
    item.attempts = 0;
    item.maxAttempts = this.config.api.retryAttempts;
    item.added = Date.now();
    this.retryQueue.push(item);
    this.log("warning", `Zur Retry-Queue hinzugefügt: ${item.endpoint}`);
    this.processRetryQueue();
  }

  async processRetryQueue() {
    if (this.retryQueue.length === 0) return;

    for (let i = this.retryQueue.length - 1; i >= 0; i--) {
      const item = this.retryQueue[i];

      if (item.attempts >= item.maxAttempts) {
        this.log("error", `Max. Versuche erreicht für: ${item.endpoint}`);
        this.retryQueue.splice(i, 1);
        continue;
      }

      item.attempts++;

      try {
        await new Promise((resolve) =>
          setTimeout(resolve, this.config.api.retryDelay * item.attempts),
        );
        await this.apiCall(item.endpoint, item.method, item.data);
        this.log("info", `Retry erfolgreich: ${item.endpoint}`);
        this.retryQueue.splice(i, 1);
      } catch (error) {
        this.log(
          "warning",
          `Retry ${item.attempts}/${item.maxAttempts} fehlgeschlagen: ${item.endpoint}`,
        );
      }
    }
  }

  // ==================== OVERVIEW ====================

  async loadOverviewData() {
    try {
      const [health, metrics] = await Promise.all([
        this.apiCall(this.config.api.endpoints.health).catch(() => null),
        this.apiCall(this.config.api.endpoints.metrics).catch(() => null),
      ]);

      if (metrics) {
        document.getElementById("metricSent")?.textContent &&
          (document.getElementById("metricSent").textContent =
            metrics.messages_sent || 0);
        document.getElementById("metricReceived")?.textContent &&
          (document.getElementById("metricReceived").textContent =
            metrics.messages_received || 0);
        document.getElementById("metricChats")?.textContent &&
          (document.getElementById("metricChats").textContent =
            metrics.active_chats || 0);
        document.getElementById("metricQueue")?.textContent &&
          (document.getElementById("metricQueue").textContent =
            metrics.queue_size || 0);
      }

      await this.loadInbox();
    } catch (error) {
      this.log("error", "Overview Daten konnten nicht geladen werden");
    }
  }

  // ==================== SETTINGS ====================

  async saveSettings() {
    const botToken = document.getElementById("botToken")?.value;
    const defaultParseMode = document.getElementById("defaultParseMode")?.value;
    const rateMsgPerSec = parseInt(
      document.getElementById("rateMsgPerSec")?.value,
    );
    const rateMsgPerMin = parseInt(
      document.getElementById("rateMsgPerMin")?.value,
    );

    const settings = {
      bot_token: botToken,
      parse_mode: defaultParseMode,
      rate_limits: {
        per_second: rateMsgPerSec,
        per_minute: rateMsgPerMin,
      },
    };

    try {
      await this.apiCall(this.config.api.endpoints.config, "POST", settings);
      this.showToast("Einstellungen gespeichert", "success");
      this.log("info", "Einstellungen aktualisiert");
    } catch (error) {
      this.showToast(`Fehler: ${error.message}`, "error");
    }
  }

  async restartAgent() {
    if (!confirm("Agent wirklich neustarten?")) return;

    try {
      await this.apiCall(this.config.api.endpoints.restart, "POST");
      this.showToast("Agent wird neugestartet...", "warning");
      this.setOnlineStatus(false);

      setTimeout(() => this.checkHealth(), 5000);
    } catch (error) {
      this.showToast(`Fehler: ${error.message}`, "error");
    }
  }

  async clearCache() {
    try {
      await this.apiCall(this.config.api.endpoints.clearCache, "POST");
      this.showToast("Cache geleert", "success");
    } catch (error) {
      this.showToast(`Fehler: ${error.message}`, "error");
    }
  }

  testPortierConnection() {
    const coordinatorUrl = this.config.portier.coordinatorUrl;
    fetch(`${coordinatorUrl}/health`)
      .then((r) => r.json())
      .then((data) => {
        this.showToast("PORTIER Verbindung OK", "success");
      })
      .catch((err) => {
        this.showToast("PORTIER nicht erreichbar", "error");
      });
  }

  // ==================== LOGGING ====================

  log(level, message) {
    const entry = {
      time: new Date().toLocaleTimeString(),
      level,
      message,
    };

    this.logs.unshift(entry);
    if (this.logs.length > this.config.ui.logMaxLines) {
      this.logs.pop();
    }

    if (this.currentSection === "logs") {
      this.renderLogs();
    }
  }

  renderLogs() {
    const output = document.getElementById("logOutput");
    if (!output) return;

    const levelFilter = document.getElementById("logLevel")?.value || "all";
    const filtered =
      levelFilter === "all"
        ? this.logs
        : this.logs.filter((l) => l.level === levelFilter);

    output.innerHTML = filtered
      .map(
        (entry) => `
            <div class="log-entry ${entry.level}">
                <span class="log-time">${entry.time}</span>
                <span class="log-level">${entry.level.toUpperCase()}</span>
                <span class="log-message">${entry.message}</span>
            </div>
        `,
      )
      .join("");
  }

  filterLogs(level) {
    this.renderLogs();
  }

  clearLogs() {
    this.logs = [];
    this.renderLogs();
    this.showToast("Logs gelöscht", "success");
  }

  downloadLogs() {
    const data = this.logs
      .map((l) => `${l.time} [${l.level}] ${l.message}`)
      .join("\n");
    const blob = new Blob([data], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `telegram_logs_${new Date().toISOString().split("T")[0]}.log`;
    a.click();
    URL.revokeObjectURL(url);
  }

  // ==================== MODAL ====================

  showModal(title, content) {
    const modal = document.getElementById("modal");
    const modalTitle = document.getElementById("modalTitle");
    const modalBody = document.getElementById("modalBody");

    if (modal && modalTitle && modalBody) {
      modalTitle.textContent = title;
      modalBody.innerHTML = content;
      modal.classList.add("active");
    }
  }

  closeModal() {
    document.getElementById("modal")?.classList.remove("active");
  }

  showMessage(msgId) {
    this.showModal("Nachricht Details", `<p>Nachricht ID: ${msgId}</p>`);
  }

  previewMedia(mediaId) {
    this.showModal("Media Preview", `<p>Media ID: ${mediaId}</p>`);
  }

  // ==================== TOAST ====================

  showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${message}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
      toast.remove();
    }, this.config.ui.toastDuration);
  }

  // ==================== UTILITIES ====================

  formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString("de-DE", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  formatDate(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleDateString("de-DE");
  }
}

// Quick Actions (Global functions for onclick handlers)
function sendQuickMessage() {
  const chatId = prompt("Chat-ID eingeben:");
  const message = prompt("Nachricht eingeben:");
  if (chatId && message) {
    dashboard
      .apiCall(CONFIG.api.endpoints.sendMessage, "POST", {
        chat_id: chatId,
        text: message,
      })
      .then(() => dashboard.showToast("Gesendet", "success"))
      .catch((err) => dashboard.showToast("Fehler", "error"));
  }
}

function refreshInbox() {
  dashboard.loadInbox();
  dashboard.showToast("Inbox aktualisiert", "info");
}

function viewAllMessages() {
  dashboard.showSection("messaging");
}

function viewWebhookEvents() {
  dashboard.showSection("webhook");
}

// Initialize dashboard when DOM is ready
let dashboard;
let app; // Alias für onclick Handler im HTML

document.addEventListener("DOMContentLoaded", () => {
  dashboard = new TelegramDashboard();
  app = dashboard; // Mache dashboard global als 'app' verfügbar für HTML onclick
  window.app = dashboard; // Auch als window.app verfügbar
  window.dashboard = dashboard; // Auch als window.dashboard verfügbar

  console.log("✅ Telegram Dashboard initialisiert");
  console.log("✅ app und dashboard global verfügbar");
});

// Export for modules
if (typeof module !== "undefined" && module.exports) {
  module.exports = TelegramDashboard;
}
