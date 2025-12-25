// Agent Fleet Observatory - Frontend Logic

let fleetData = null;

/**
 * Load and display fleet data
 */
async function loadFleetData() {
  try {
    const response = await fetch("/artifacts/agent_fleet/agent_inventory.json");
    if (!response.ok) {
      throw new Error("Failed to fetch inventory");
    }

    fleetData = await response.json();
    updateStats();
    renderServices();
    hideError();
  } catch (error) {
    console.error("Error loading fleet data:", error);
    showError();
  }
}

/**
 * Update statistics bar
 */
function updateStats() {
  if (!fleetData) return;

  document.getElementById("total-services").textContent =
    fleetData.total_services;
  document.getElementById("total-compose-files").textContent =
    fleetData.compose_files_scanned.length;

  const totalPorts = fleetData.services.reduce(
    (sum, service) => sum + service.ports.length,
    0,
  );
  document.getElementById("total-ports").textContent = totalPorts;

  // Port conflicts
  const conflictCount = Object.keys(fleetData.port_conflicts || {}).length;
  document.getElementById("port-conflicts").textContent = conflictCount;
  document.getElementById("port-conflicts").style.color =
    conflictCount > 0 ? "#dc3545" : "#28a745";

  // Count running/stopped containers
  const runningCount = fleetData.services.filter(
    (s) => s.live_status && s.live_status.status === "running",
  ).length;
  const stoppedCount = fleetData.services.filter(
    (s) =>
      s.live_status &&
      (s.live_status.status === "exited" || s.live_status.status === "stopped"),
  ).length;

  // Add status count to display
  const statusText =
    runningCount > 0 || stoppedCount > 0
      ? ` (🟢 ${runningCount} running, 🔴 ${stoppedCount} stopped)`
      : "";
  document.getElementById("total-services").textContent =
    fleetData.total_services + statusText;

  const scanTime = new Date(fleetData.scanned_at);
  document.getElementById("last-scan").textContent =
    scanTime.toLocaleString("de-DE");

  // Display changes banner
  if (fleetData.changes) {
    displayChanges(fleetData.changes);
  }
}

/**
 * Display changes summary
 */
function displayChanges(changes) {
  const banner = document.getElementById("changes-banner");
  const hasChanges =
    changes.added.length > 0 ||
    changes.removed.length > 0 ||
    changes.modified.length > 0;

  if (!hasChanges) {
    banner.style.display = "none";
    return;
  }

  banner.style.display = "flex";

  if (changes.added.length > 0) {
    document.getElementById("added-services").innerHTML =
      `<strong>✅ Added:</strong> ${changes.added.length} service(s)`;
  }
  if (changes.removed.length > 0) {
    document.getElementById("removed-services").innerHTML =
      `<strong>❌ Removed:</strong> ${changes.removed.length} service(s)`;
  }
  if (changes.modified.length > 0) {
    document.getElementById("modified-services").innerHTML =
      `<strong>🔄 Modified:</strong> ${changes.modified.length} service(s)`;
  }
}

/**
 * Render service cards
 */
function renderServices(filter = {}) {
  const grid = document.getElementById("fleet-grid");
  grid.innerHTML = "";

  if (!fleetData || !fleetData.services) return;

  let services = fleetData.services;

  // Apply search filter
  if (filter.search) {
    const searchLower = filter.search.toLowerCase();
    services = services.filter(
      (service) =>
        service.service_name.toLowerCase().includes(searchLower) ||
        service.image.toLowerCase().includes(searchLower) ||
        service.compose_file.toLowerCase().includes(searchLower) ||
        service.ports.some((port) =>
          String(port.host_port).includes(searchLower),
        ),
    );
  }

  // Apply restart policy filter
  if (filter.restart) {
    services = services.filter((service) => service.restart === filter.restart);
  }

  // Render filtered services
  services.forEach((service) => {
    const card = createServiceCard(service);
    grid.appendChild(card);
  });
}

/**
 * Create service card DOM element
 */
function createServiceCard(service) {
  const card = document.createElement("div");
  card.className = "service-card";

  const header = document.createElement("div");
  header.className = "service-header";

  const name = document.createElement("div");
  name.className = "service-name";
  name.textContent = service.service_name;

  const status = document.createElement("div");

  // Use live status if available, otherwise fall back to restart policy
  if (service.live_status) {
    const liveStatus = service.live_status.status.toLowerCase();
    if (liveStatus === "running") {
      status.className = "service-status status-running";
      status.textContent = "🟢 RUNNING";
    } else if (liveStatus === "exited" || liveStatus === "stopped") {
      status.className = "service-status status-stopped";
      status.textContent = "🔴 " + service.live_status.status.toUpperCase();
    } else if (liveStatus === "not_found") {
      status.className = "service-status status-unknown";
      status.textContent = "⚪ NOT FOUND";
    } else {
      status.className = "service-status status-unknown";
      status.textContent = "⚠️ " + service.live_status.status.toUpperCase();
    }
  } else {
    // Fallback to restart policy indication
    status.className = `service-status ${service.restart !== "no" ? "status-running" : "status-stopped"}`;
    status.textContent = service.restart !== "no" ? "AUTO" : "MANUAL";
  }

  header.appendChild(name);
  header.appendChild(status);

  const info = document.createElement("div");
  info.className = "service-info";

  // Image info
  info.appendChild(createInfoRow("Image", `<code>${service.image}</code>`));

  // Container name
  info.appendChild(
    createInfoRow("Container", `<code>${service.container_name}</code>`),
  );

  // Live status details (if available)
  if (service.live_status && service.live_status.id) {
    info.appendChild(
      createInfoRow("Container ID", `<code>${service.live_status.id}</code>`),
    );
    if (service.live_status.health && service.live_status.health !== "none") {
      const healthEmoji =
        service.live_status.health === "healthy" ? "✅" : "❌";
      info.appendChild(
        createInfoRow("Health", `${healthEmoji} ${service.live_status.health}`),
      );
    }
    // Resource stats
    if (service.live_status.resources) {
      const res = service.live_status.resources;
      const cpuClass =
        res.cpu_percent > 80
          ? "resource-high"
          : res.cpu_percent > 50
            ? "resource-medium"
            : "resource-low";
      const memClass =
        res.memory_percent > 80
          ? "resource-high"
          : res.memory_percent > 50
            ? "resource-medium"
            : "resource-low";
      info.appendChild(
        createInfoRow(
          "CPU",
          `<span class="${cpuClass}">${res.cpu_percent.toFixed(1)}%</span>`,
        ),
      );
      info.appendChild(
        createInfoRow(
          "Memory",
          `<span class="${memClass}">${res.memory_usage_mb.toFixed(0)} MB (${res.memory_percent.toFixed(1)}%)</span>`,
        ),
      );
    }
  }

  // Ports
  if (service.ports.length > 0) {
    const portsDiv = document.createElement("div");
    portsDiv.className = "info-row";

    const label = document.createElement("div");
    label.className = "info-label";
    label.textContent = "Ports";

    const portsList = document.createElement("div");
    portsList.className = "ports-list";

    service.ports.forEach((port) => {
      const badge = document.createElement("span");
      badge.className = "port-badge";
      badge.textContent = `${port.host_port}:${port.container_port}`;
      portsList.appendChild(badge);
    });

    portsDiv.appendChild(label);
    portsDiv.appendChild(portsList);
    info.appendChild(portsDiv);
  }

  // Networks
  if (service.networks.length > 0) {
    const networksDiv = document.createElement("div");
    networksDiv.className = "info-row";

    const label = document.createElement("div");
    label.className = "info-label";
    label.textContent = "Networks";

    const networksList = document.createElement("div");
    networksList.className = "networks-list";

    service.networks.forEach((network) => {
      const badge = document.createElement("span");
      badge.className = "network-badge";
      badge.textContent = network;
      networksList.appendChild(badge);
    });

    networksDiv.appendChild(label);
    networksDiv.appendChild(networksList);
    info.appendChild(networksDiv);
  }

  // Restart policy
  const restartDiv = document.createElement("div");
  restartDiv.className = "info-row";

  const restartLabel = document.createElement("div");
  restartLabel.className = "info-label";
  restartLabel.textContent = "Restart";

  const restartValue = document.createElement("span");
  restartValue.className = "restart-policy";
  restartValue.textContent = service.restart;

  restartDiv.appendChild(restartLabel);
  restartDiv.appendChild(restartValue);
  info.appendChild(restartDiv);

  // Compose file (shortened path)
  const composePath = service.compose_file.split("/").slice(-3).join("/");
  info.appendChild(createInfoRow("Source", `<code>${composePath}</code>`));

  card.appendChild(header);
  card.appendChild(info);

  return card;
}

/**
 * Helper: Create info row
 */
function createInfoRow(label, value) {
  const row = document.createElement("div");
  row.className = "info-row";

  const labelEl = document.createElement("div");
  labelEl.className = "info-label";
  labelEl.textContent = label;

  const valueEl = document.createElement("div");
  valueEl.className = "info-value";
  valueEl.innerHTML = value;

  row.appendChild(labelEl);
  row.appendChild(valueEl);

  return row;
}

/**
 * Show error message
 */
function showError() {
  document.getElementById("error-message").style.display = "block";
  document.getElementById("fleet-grid").style.display = "none";
}

/**
 * Hide error message
 */
function hideError() {
  document.getElementById("error-message").style.display = "none";
  document.getElementById("fleet-grid").style.display = "grid";
}

/**
 * Event listeners
 */
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("search-input").addEventListener("input", (e) => {
    renderServices({
      search: e.target.value,
      restart: document.getElementById("filter-restart").value,
    });
  });

  document.getElementById("filter-restart").addEventListener("change", (e) => {
    renderServices({
      search: document.getElementById("search-input").value,
      restart: e.target.value,
    });
  });

  document.getElementById("refresh-btn").addEventListener("click", () => {
    location.reload();
  });

  // Load data on page load
  loadFleetData();
});
