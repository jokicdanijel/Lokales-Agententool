/**
 * ELION Entitlements Client
 * ==========================
 * Frontend-Integration für maschinenlesbare Entitlement-Gates
 *
 * USAGE:
 *   const entitlements = new EntitlementsClient('/build/entitlements.json');
 *   await entitlements.load();
 *
 *   if (entitlements.canClick('basic', 'opena5')) {
 *     // Agent aktivieren
 *   } else {
 *     // Upgrade-Gate anzeigen
 *   }
 */

class EntitlementsClient {
  constructor(entitlementsUrl = "/build/entitlements.json") {
    this.entitlementsUrl = entitlementsUrl;
    this.data = null;
    this.loaded = false;
  }

  /**
   * Lädt entitlements.json vom Server
   */
  async load() {
    try {
      const response = await fetch(this.entitlementsUrl);
      if (!response.ok) {
        throw new Error(`Failed to load entitlements: ${response.status}`);
      }
      this.data = await response.json();
      this.loaded = true;
      console.log("✓ Entitlements loaded:", this.data.version);
      return true;
    } catch (error) {
      console.error("✗ Failed to load entitlements:", error);
      return false;
    }
  }

  /**
   * Prüft, ob ein Agent in einem Plan sichtbar ist
   * @param {string} planId - Plan ID (basic, pro, premium, ultimum)
   * @param {string} agentId - Agent ID (opena1, opena2, ...)
   * @returns {boolean}
   */
  isVisible(planId, agentId) {
    this._ensureLoaded();
    const agent = this._getAgent(planId, agentId);
    return agent ? agent.visible : false;
  }

  /**
   * Prüft, ob ein Agent in einem Plan klickbar ist
   * @param {string} planId - Plan ID
   * @param {string} agentId - Agent ID
   * @returns {boolean}
   */
  canClick(planId, agentId) {
    this._ensureLoaded();
    const agent = this._getAgent(planId, agentId);
    return agent ? agent.clickable : false;
  }

  /**
   * Holt Limits für einen Agent in einem Plan
   * @param {string} planId - Plan ID
   * @param {string} agentId - Agent ID
   * @returns {Object} Limits object
   */
  getLimits(planId, agentId) {
    this._ensureLoaded();
    const agent = this._getAgent(planId, agentId);
    return agent ? agent.limits : {};
  }

  /**
   * Holt Gates (Blockierungsgründe) für einen Agent
   * @param {string} planId - Plan ID
   * @param {string} agentId - Agent ID
   * @returns {Array<string>} Liste von Gates
   */
  getGates(planId, agentId) {
    this._ensureLoaded();
    const agent = this._getAgent(planId, agentId);
    return agent ? agent.gates : [];
  }

  /**
   * Holt den Grund für den Zugriffssstatus
   * @param {string} planId - Plan ID
   * @param {string} agentId - Agent ID
   * @returns {string} Reason string
   */
  getReason(planId, agentId) {
    this._ensureLoaded();
    const agent = this._getAgent(planId, agentId);
    return agent ? agent.reason : "unknown";
  }

  /**
   * Holt alle klickbaren Agents für einen Plan
   * @param {string} planId - Plan ID
   * @returns {Array<string>} Liste von Agent IDs
   */
  getClickableAgents(planId) {
    this._ensureLoaded();
    const plan = this.data.plans[planId];
    if (!plan) return [];

    return Object.keys(plan.agents).filter(
      (agentId) => plan.agents[agentId].clickable,
    );
  }

  /**
   * Holt alle Agents mit "requires_upgrade" Gate
   * @param {string} planId - Plan ID
   * @returns {Array<string>} Liste von Agent IDs
   */
  getUpgradeGatedAgents(planId) {
    this._ensureLoaded();
    const plan = this.data.plans[planId];
    if (!plan) return [];

    return Object.keys(plan.agents).filter((agentId) =>
      plan.agents[agentId].gates.includes("requires_upgrade"),
    );
  }

  /**
   * Prüft, ob ein Agent Read-only Log-Zugriff hat
   * @param {string} planId - Plan ID
   * @param {string} agentId - Agent ID
   * @returns {boolean}
   */
  hasReadOnlyLogs(planId, agentId) {
    const limits = this.getLimits(planId, agentId);
    return limits.logs_access === "read_only";
  }

  /**
   * Holt Workflow-Limit für einen Agent
   * @param {string} planId - Plan ID
   * @param {string} agentId - Agent ID
   * @returns {number} -1 für unlimited, sonst Limit
   */
  getWorkflowLimit(planId, agentId) {
    const limits = this.getLimits(planId, agentId);
    return limits.workflow_limit !== undefined ? limits.workflow_limit : -1;
  }

  /**
   * Holt Agent-Daten
   * @private
   */
  _getAgent(planId, agentId) {
    if (!this.data.plans[planId]) {
      console.warn(`Plan '${planId}' not found`);
      return null;
    }

    const agent = this.data.plans[planId].agents[agentId];
    if (!agent) {
      console.warn(`Agent '${agentId}' not found in plan '${planId}'`);
      return null;
    }

    return agent;
  }

  /**
   * Stellt sicher, dass Entitlements geladen sind
   * @private
   */
  _ensureLoaded() {
    if (!this.loaded) {
      throw new Error("Entitlements not loaded. Call load() first.");
    }
  }
}

// ============================================================================
// BEISPIEL-INTEGRATION IN DASHBOARD
// ============================================================================

/**
 * Beispiel: Agent-Karte mit Entitlements rendern
 */
async function renderAgentCards() {
  const entitlements = new EntitlementsClient();
  await entitlements.load();

  const userPlan = getUserPlan(); // z.B. 'basic'
  const agents = getAllAgentIds(); // z.B. ['opena1', 'opena2', ...]

  const container = document.getElementById("agent-grid");

  agents.forEach((agentId) => {
    const card = document.createElement("div");
    card.className = "agent-card";

    const visible = entitlements.isVisible(userPlan, agentId);
    const clickable = entitlements.canClick(userPlan, agentId);
    const gates = entitlements.getGates(userPlan, agentId);
    const limits = entitlements.getLimits(userPlan, agentId);

    // Basis-HTML
    card.innerHTML = `
      <div class="agent-icon">${getAgentIcon(agentId)}</div>
      <h3>${getAgentName(agentId)}</h3>
    `;

    // Sichtbarkeit
    if (!visible) {
      card.style.display = "none";
      return;
    }

    // Klickbarkeit und Gates
    if (!clickable) {
      card.classList.add("disabled");

      if (gates.includes("requires_upgrade")) {
        // Upgrade-Badge anzeigen
        const badge = document.createElement("div");
        badge.className = "upgrade-badge";
        badge.textContent = "⬆ Upgrade";
        badge.onclick = () => showUpgradeModal(agentId);
        card.appendChild(badge);
      }

      card.onclick = (e) => {
        e.preventDefault();
        showUpgradeModal(agentId);
      };
    } else {
      // Agent aktivieren
      card.onclick = () => openAgent(agentId);

      // Limits anzeigen
      if (limits.logs_access === "read_only") {
        const logsInfo = document.createElement("div");
        logsInfo.className = "info-badge";
        logsInfo.textContent = "📖 Read-only Logs";
        card.appendChild(logsInfo);
      }

      if (limits.workflow_limit && limits.workflow_limit > 0) {
        const workflowInfo = document.createElement("div");
        workflowInfo.className = "info-badge";
        workflowInfo.textContent = `🔄 Max ${limits.workflow_limit} Workflows`;
        card.appendChild(workflowInfo);
      }
    }

    container.appendChild(card);
  });
}

/**
 * Beispiel: Upgrade-Modal anzeigen
 */
function showUpgradeModal(agentId) {
  const modal = document.createElement("div");
  modal.className = "upgrade-modal";
  modal.innerHTML = `
    <div class="modal-content">
      <h2>Upgrade erforderlich</h2>
      <p>${getAgentName(agentId)} ist in Ihrem aktuellen Plan nicht verfügbar.</p>
      <p>Upgraden Sie auf Pro, Premium oder Ultimum für vollen Zugriff.</p>
      <button onclick="window.location='/upgrade'">Jetzt upgraden</button>
      <button onclick="this.closest('.upgrade-modal').remove()">Schließen</button>
    </div>
  `;
  document.body.appendChild(modal);
}

/**
 * Beispiel: Feature-Gate für Log-Editing
 */
async function setupLogViewer(agentId) {
  const entitlements = new EntitlementsClient();
  await entitlements.load();

  const userPlan = getUserPlan();
  const readOnly = entitlements.hasReadOnlyLogs(userPlan, agentId);

  if (readOnly) {
    // Editing-Buttons deaktivieren
    document.querySelectorAll(".log-edit-btn").forEach((btn) => {
      btn.disabled = true;
      btn.title = "Nur-Lese-Zugriff im Basic Plan";
    });

    // Info-Banner anzeigen
    const banner = document.createElement("div");
    banner.className = "info-banner";
    banner.innerHTML =
      '📖 Nur-Lese-Modus. <a href="/upgrade">Upgraden</a> für vollen Zugriff.';
    document.querySelector(".log-viewer").prepend(banner);
  }
}

// ============================================================================
// UTILITY-FUNKTIONEN
// ============================================================================

// Diese Funktionen müssen in Ihrer Anwendung implementiert werden
function getUserPlan() {
  // Von Session/Auth holen
  return localStorage.getItem("user_plan") || "basic";
}

function getAllAgentIds() {
  // Von Agent-Registry holen
  return ["opena1", "opena2", "opena3" /* ... */];
}

function getAgentIcon(agentId) {
  // Icon-Mapping
  const icons = {
    opena1: "🚪",
    opena2: "📦",
    opena3: "💬",
    // ...
  };
  return icons[agentId] || "🤖";
}

function getAgentName(agentId) {
  // Name-Mapping
  const names = {
    opena1: "Portier",
    opena2: "Archivar",
    opena3: "OpenWebUI",
    // ...
  };
  return names[agentId] || agentId;
}

function openAgent(agentId) {
  window.location = `/agent/${agentId}`;
}

// ============================================================================
// EXPORT
// ============================================================================

// Für ES6 Modules
// export default EntitlementsClient;

// Für Browser Global
if (typeof window !== "undefined") {
  window.EntitlementsClient = EntitlementsClient;
}
