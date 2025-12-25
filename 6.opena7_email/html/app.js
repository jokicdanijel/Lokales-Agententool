// 📧 Email Agent 6.0 - Dashboard JavaScript (PORTIER PAS-6.0)

let isConnected = false;
let authToken = "";
let statusUpdateTimer = null;

// ===============================================
// 🔐 Authentication & Connection
// ===============================================

async function authenticate() {
  const tokenInput = document.getElementById("token");
  const token = tokenInput.value.trim();

  if (!token) {
    showNotification("Please enter a Bearer token", "warning");
    return;
  }

  authToken = token;
  localStorage.setItem(CONFIG.BEARER_TOKEN_KEY, token);

  try {
    const response = await api("/health");
    if (response.status === "ok") {
      isConnected = true;
      updateConnectionStatus(true);
      startStatusUpdates();
      showNotification("Connected to Email Agent successfully!", "success");
    } else {
      throw new Error("Health check failed");
    }
  } catch (error) {
    isConnected = false;
    updateConnectionStatus(false);
    showNotification(`Connection failed: ${error.message}`, "error");
  }
}

function updateConnectionStatus(connected) {
  const statusDot = document.getElementById("statusDot");
  const statusText = document.getElementById("statusText");
  const connectionStatus = document.getElementById("connectionStatus");
  const footerStatus = document.getElementById("footerStatus");

  if (connected) {
    statusDot.className = "status-dot connected";
    statusText.textContent = "Connected";
    connectionStatus.textContent = "Connected";
    footerStatus.textContent = "Connected";
  } else {
    statusDot.className = "status-dot";
    statusText.textContent = "Disconnected";
    connectionStatus.textContent = "Disconnected";
    footerStatus.textContent = "Disconnected";
  }
}

function startStatusUpdates() {
  if (statusUpdateTimer) {
    clearInterval(statusUpdateTimer);
  }

  statusUpdateTimer = setInterval(async () => {
    try {
      const response = await api("/health");
      if (response.status !== "ok") {
        throw new Error("Health check failed");
      }
      updateLastUpdated();
    } catch (error) {
      isConnected = false;
      updateConnectionStatus(false);
      clearInterval(statusUpdateTimer);
      showNotification("Connection lost", "warning");
    }
  }, CONFIG.STATUS_UPDATE_INTERVAL);
}

function updateLastUpdated() {
  const lastUpdated = document.getElementById("lastUpdated");
  if (lastUpdated) {
    lastUpdated.textContent = new Date().toLocaleTimeString();
  }
}

// ===============================================
// 🌐 API Helper Functions
// ===============================================

async function api(path, method = "GET", payload = null) {
  const headers = {
    "Content-Type": "application/json",
  };

  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }

  const options = {
    method,
    headers,
  };

  if (payload) {
    options.body = JSON.stringify(payload);
  }

  try {
    const response = await fetch(`${CONFIG.BASE_URL}${path}`, options);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      return await response.json();
    } else {
      return await response.text();
    }
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
}

function log(elementId, data, clear = false) {
  const element = document.getElementById(elementId);
  if (!element) return;

  if (clear) {
    element.textContent = "";
  }

  let content;
  if (typeof data === "object") {
    content = JSON.stringify(data, null, 2);
  } else {
    content = String(data);
  }

  if (clear) {
    element.textContent = content;
  } else {
    element.textContent += (element.textContent ? "\n" : "") + content;
  }

  // Auto-scroll to bottom
  element.scrollTop = element.scrollHeight;
}

// ===============================================
// 🩺 Core Functions
// ===============================================

async function runHealth() {
  try {
    log("health_output", "🔄 Checking agent health...", true);
    const response = await api("/health");
    log("health_output", "✅ Health check successful:", true);
    log("health_output", response);

    showNotification("Health check completed", "success");
  } catch (error) {
    log("health_output", `❌ Health check failed: ${error.message}`, true);
    showNotification(`Health check failed: ${error.message}`, "error");
  }
}

async function runStatus() {
  try {
    log("status_output", "🔄 Getting agent status...", true);
    const response = await api("/status");
    log("status_output", "✅ Status retrieved successfully:", true);
    log("status_output", response);

    showNotification("Status retrieved successfully", "success");
  } catch (error) {
    log("status_output", `❌ Status retrieval failed: ${error.message}`, true);
    showNotification(`Status failed: ${error.message}`, "error");
  }
}

// ===============================================
// 📧 Email Commands
// ===============================================

async function runCommand() {
  const payloadText = document.getElementById("cmd_payload").value.trim();

  if (!payloadText) {
    showNotification("Please enter a command payload", "warning");
    return;
  }

  try {
    const payload = JSON.parse(payloadText);
    log(
      "cmd_output",
      `🚀 Executing email command: ${payload.command || "unknown"}`,
      true,
    );

    const response = await api("/command", "POST", payload);
    log("cmd_output", "✅ Email command executed successfully:");
    log("cmd_output", response);

    showNotification("Email command executed successfully", "success");
  } catch (error) {
    log("cmd_output", `❌ Email command failed: ${error.message}`);
    showNotification(`Command failed: ${error.message}`, "error");
  }
}

function loadCommandTemplate(type) {
  const templates = {
    check_inbox: {
      command: "check_inbox",
      args: {
        folder: "INBOX",
        limit: 10,
      },
    },
    send_email: {
      command: "send_email",
      args: {
        to: "recipient@example.com",
        subject: "Test Email",
        body: "This is a test email from Email Agent 6.0",
      },
    },
    get_email: {
      command: "get_email",
      args: {
        id: "1",
      },
    },
    search_emails: {
      command: "search_emails",
      args: {
        query: "important",
        folder: "INBOX",
        limit: 20,
      },
    },
    mark_read: {
      command: "mark_read",
      args: {
        id: "1",
        read: true,
      },
    },
  };

  const template = templates[type];
  if (template) {
    document.getElementById("cmd_payload").value = JSON.stringify(
      template,
      null,
      2,
    );
    showNotification(`Template loaded: ${type}`, "info");
  }
}

function validateCommand() {
  const payloadText = document.getElementById("cmd_payload").value.trim();

  try {
    const payload = JSON.parse(payloadText);

    if (!payload.command) {
      throw new Error('Missing required "command" field');
    }

    if (!payload.args) {
      throw new Error('Missing required "args" field');
    }

    showNotification("✅ Command payload is valid", "success");
    log("cmd_output", "✅ Validation passed", true);
  } catch (error) {
    showNotification(`❌ Invalid JSON: ${error.message}`, "error");
    log("cmd_output", `❌ Validation failed: ${error.message}`, true);
  }
}

function clearCommand() {
  document.getElementById("cmd_payload").value = "";
  log("cmd_output", "", true);
  showNotification("Command editor cleared", "info");
}

// ===============================================
// 🤖 AI Functions
// ===============================================

async function runSpecialized() {
  const payloadText = document.getElementById("spec_payload").value.trim();

  if (!payloadText) {
    showNotification("Please enter an AI function payload", "warning");
    return;
  }

  try {
    const payload = JSON.parse(payloadText);
    log(
      "spec_output",
      `🤖 Executing AI function: ${payload.action || "unknown"}`,
      true,
    );

    const response = await api("/specialized", "POST", payload);
    log("spec_output", "✅ AI function executed successfully:");
    log("spec_output", response);

    showNotification("AI function executed successfully", "success");
  } catch (error) {
    log("spec_output", `❌ AI function failed: ${error.message}`);
    showNotification(`AI function failed: ${error.message}`, "error");
  }
}

function loadAITemplate(type) {
  const templates = {
    generate_reply: {
      action: "generate_reply",
      email_text:
        "Hallo, ich habe eine Frage zu Ihrem Service. Können Sie mir bitte weiterhelfen?",
      tone: "professional",
      language: "german",
    },
    classify_email: {
      action: "classify_email",
      email_text: "Urgent: Server down, please help immediately!",
      subject: "Server Issue",
    },
    extract_info: {
      action: "extract_info",
      email_text:
        "Hi, my name is John Doe from Acme Corp. I need help with project deadline on Friday.",
      fields: ["contact", "company", "intent", "deadline"],
    },
    sentiment_analysis: {
      action: "sentiment_analysis",
      email_text:
        "I am very disappointed with your service. This is unacceptable!",
    },
    priority_score: {
      action: "priority_score",
      email_text: "URGENT: System outage affecting all customers",
      subject: "Critical System Issue",
      sender: "admin@company.com",
    },
    auto_response: {
      action: "auto_response",
      email_text: "Hello, I would like to know more about your pricing plans.",
    },
  };

  const template = templates[type];
  if (template) {
    document.getElementById("spec_payload").value = JSON.stringify(
      template,
      null,
      2,
    );
    showNotification(`AI template loaded: ${type}`, "info");
  }
}

function validateSpecialized() {
  const payloadText = document.getElementById("spec_payload").value.trim();

  try {
    const payload = JSON.parse(payloadText);

    if (!payload.action) {
      throw new Error('Missing required "action" field');
    }

    showNotification("✅ AI payload is valid", "success");
    log("spec_output", "✅ Validation passed", true);
  } catch (error) {
    showNotification(`❌ Invalid JSON: ${error.message}`, "error");
    log("spec_output", `❌ Validation failed: ${error.message}`, true);
  }
}

function clearSpecialized() {
  document.getElementById("spec_payload").value = "";
  log("spec_output", "", true);
  showNotification("AI editor cleared", "info");
}

// ===============================================
// 📊 Metrics & Monitoring
// ===============================================

async function loadMetrics() {
  try {
    log("metrics_output", "🔄 Loading performance metrics...", true);
    const response = await api("/metrics");

    // Update metric displays
    updateMetricDisplay(
      "emails_processed",
      (response.statistics?.emails_received || 0) +
        (response.statistics?.emails_sent || 0),
    );
    updateMetricDisplay(
      "ai_replies",
      response.statistics?.ai_replies_generated || 0,
    );
    updateMetricDisplay("uptime", response.uptime_formatted || "--");
    updateMetricDisplay(
      "success_rate",
      response.performance
        ? `${100 - response.performance.error_rate_percent}%`
        : "--",
    );

    log("metrics_output", "✅ Metrics loaded successfully:");
    log("metrics_output", response);

    showNotification("Metrics refreshed", "success");
  } catch (error) {
    log("metrics_output", `❌ Metrics loading failed: ${error.message}`, true);
    showNotification(`Metrics failed: ${error.message}`, "error");
  }
}

function updateMetricDisplay(metricId, value) {
  const element = document.getElementById(metricId);
  if (element) {
    element.textContent = value;
  }
}

// ===============================================
// 📜 Logs & Configuration
// ===============================================

async function loadLogs() {
  try {
    log("logs_output", "🔄 Loading system logs...", true);
    const response = await api("/logs");

    if (response.logs && Array.isArray(response.logs)) {
      log("logs_output", "📜 System Logs:", true);
      response.logs.forEach((logEntry) => {
        log(
          "logs_output",
          `[${logEntry.timestamp}] ${logEntry.level}: ${logEntry.message}`,
        );
      });
    } else {
      log("logs_output", response, true);
    }

    showNotification("Logs refreshed", "success");
  } catch (error) {
    log("logs_output", `❌ Logs loading failed: ${error.message}`, true);
    showNotification(`Logs failed: ${error.message}`, "error");
  }
}

function clearLogs() {
  log("logs_output", "", true);
  showNotification("Log display cleared", "info");
}

async function loadConfig() {
  try {
    log("config_output", "🔄 Loading agent configuration...", true);
    const response = await api("/config");
    log("config_output", "⚙️ Agent Configuration:", true);
    log("config_output", response);

    showNotification("Configuration loaded", "success");
  } catch (error) {
    log(
      "config_output",
      `❌ Configuration loading failed: ${error.message}`,
      true,
    );
    showNotification(`Configuration failed: ${error.message}`, "error");
  }
}

// ===============================================
// 🔔 Notification System
// ===============================================

function showNotification(message, type = "info") {
  // Create notification element
  const notification = document.createElement("div");
  notification.className = `notification notification-${type}`;
  notification.textContent = message;

  // Style the notification
  Object.assign(notification.style, {
    position: "fixed",
    top: "20px",
    right: "20px",
    padding: "12px 20px",
    borderRadius: "8px",
    color: "white",
    fontWeight: "500",
    zIndex: "9999",
    transition: "all 0.3s ease",
    transform: "translateX(100%)",
    maxWidth: "400px",
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
  });

  // Set background color based on type
  const colors = {
    success: "#27AE60",
    error: "#E74C3C",
    warning: "#F39C12",
    info: "#3498DB",
  };

  notification.style.background = colors[type] || colors.info;

  document.body.appendChild(notification);

  // Animate in
  setTimeout(() => {
    notification.style.transform = "translateX(0)";
  }, 10);

  // Auto remove after 4 seconds
  setTimeout(() => {
    notification.style.transform = "translateX(100%)";
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }, 4000);
}

// ===============================================
// 🎯 Initialization
// ===============================================

document.addEventListener("DOMContentLoaded", function () {
  console.log("📧 Email Agent 6.0 Dashboard Loading...");

  // Load saved token
  const savedToken = localStorage.getItem(CONFIG.BEARER_TOKEN_KEY);
  if (savedToken) {
    document.getElementById("token").value = savedToken;
    authToken = savedToken;
  }

  // Update initial timestamp
  updateLastUpdated();

  // Initialize connection status
  updateConnectionStatus(false);

  console.log("✅ Email Agent 6.0 Dashboard initialized successfully");
});

// Auto-refresh metrics every 30 seconds when connected
setInterval(() => {
  if (isConnected) {
    loadMetrics();
  }
}, 30000);
