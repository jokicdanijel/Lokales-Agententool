/**
 * opena7 Dashboard JS
 * Handles all API calls, button clicks, and UI updates
 * FIXED: Complete rewrite with proper error handling and debugging
 */

console.log("[APP] Loading opena7 dashboard...");

const state = {
    baseUrl: window.location.origin,
    token: localStorage.getItem("opena7_token") || "",
};

console.log("[APP] Base URL:", state.baseUrl);
console.log("[APP] Token loaded:", !!state.token);

/**
 * Fetch wrapper with auth + error handling
 */
async function fetchJSON(path, { method = "GET", body = null } = {}) {
    const headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    };

    if (state.token) {
        headers["Authorization"] = `Bearer ${state.token}`;
    }

    const url = `${state.baseUrl}${path}`;
    console.log(`[API] ${method} ${url}`);

    try {
        const res = await fetch(url, {
            method,
            headers,
            body: body ? JSON.stringify(body) : null,
        });

        let data = null;
        const text = await res.text();

        try {
            data = text ? JSON.parse(text) : null;
        } catch {
            data = text;
        }

        console.log(`[API] ${method} ${url} -> ${res.status}`, data);

        if (!res.ok) {
            const msg = typeof data === "string" ? data : (data?.detail || data?.error || JSON.stringify(data));
            throw new Error(`HTTP ${res.status}: ${msg}`);
        }

        return data;
    } catch (e) {
        console.error(`[API] ${method} ${url} ERROR:`, e.message);
        throw e;
    }
}

/**
 * Set status text
 */
function setStatus(text) {
    const el = document.querySelector("#connection_status");
    if (!el) {
        console.warn("[UI] #connection_status not found!");
        return;
    }
    el.textContent = text;
    el.className = "status " + (text.includes("✅") || text.includes("Connected") ? "connected" : "disconnected");
    console.log("[UI] Status:", text);
}

/**
 * Set output element
 */
function setOutput(selector, obj) {
    const el = document.querySelector(selector);
    if (!el) {
        console.warn(`[UI] ${selector} not found!`);
        return;
    }

    let text = "";
    if (typeof obj === "string") {
        text = obj;
    } else if (obj instanceof Error) {
        text = `❌ ${obj.message}`;
    } else if (obj && obj.lines && Array.isArray(obj.lines)) {
        text = obj.lines.join("\n");
    } else {
        text = JSON.stringify(obj, null, 2);
    }

    el.textContent = text;
    console.log(`[UI] Output ${selector}:`, text.substring(0, 100));
}

/**
 * Bind all event listeners
 */
function bindUI() {
    console.log("[BIND] Starting UI event binding...");

    // ===== Token / Connect =====
    const tokenInput = document.querySelector("#token_input");
    const btnConnect = document.querySelector("#btn_connect");

    if (tokenInput && btnConnect) {
        if (state.token) {
            tokenInput.value = state.token;
        }

        btnConnect.addEventListener("click", async () => {
            console.log("[CLICK] btn_connect");
            const newToken = (tokenInput?.value || "").trim();
            if (newToken) {
                state.token = newToken;
                localStorage.setItem("opena7_token", newToken);
            }

            setStatus("⏳ Connecting...");
            try {
                const h = await fetchJSON("/health");
                setStatus(`✅ Connected (${h.status || "healthy"})`);
                setOutput("#out_health", h);
            } catch (e) {
                setStatus(`❌ Connection failed: ${e.message}`);
                setOutput("#out_health", e);
            }
        });

        console.log("[BIND] ✓ btn_connect");
    } else {
        console.warn("[BIND] ✗ btn_connect or token_input missing");
    }

    // ===== Health =====
    const btnHealth = document.querySelector("#btn_health");
    if (btnHealth) {
        btnHealth.addEventListener("click", async () => {
            console.log("[CLICK] btn_health");
            try {
                const h = await fetchJSON("/health");
                setOutput("#out_health", h);
            } catch (e) {
                setOutput("#out_health", e);
            }
        });
        console.log("[BIND] ✓ btn_health");
    }

    // ===== Status =====
    const btnStatus = document.querySelector("#btn_status");
    if (btnStatus) {
        btnStatus.addEventListener("click", async () => {
            console.log("[CLICK] btn_status");
            try {
                const s = await fetchJSON("/api/status");
                setOutput("#out_status", s);
            } catch (e) {
                setOutput("#out_status", e);
            }
        });
        console.log("[BIND] ✓ btn_status");
    }

    // ===== Logs =====
    const btnLogs = document.querySelector("#btn_logs");
    if (btnLogs) {
        btnLogs.addEventListener("click", async () => {
            console.log("[CLICK] btn_logs");
            try {
                const logs = await fetchJSON("/api/logs?tail=50");
                setOutput("#out_logs", logs);
            } catch (e) {
                setOutput("#out_logs", e);
            }
        });
        console.log("[BIND] ✓ btn_logs");
    }

    // ===== Execute Command =====
    const btnExecute = document.querySelector("#btn_execute");
    if (btnExecute) {
        btnExecute.addEventListener("click", async () => {
            console.log("[CLICK] btn_execute");
            const raw = (document.querySelector("#cmd_json")?.value || "{}").trim();
            try {
                const payload = JSON.parse(raw);
                const r = await fetchJSON("/run", { method: "POST", body: payload });
                setOutput("#out_cmd", r);
            } catch (e) {
                setOutput("#out_cmd", e);
            }
        });
        console.log("[BIND] ✓ btn_execute");
    }

    // ===== AI Execute =====
    const btnAI = document.querySelector("#btn_ai_execute");
    if (btnAI) {
        btnAI.addEventListener("click", async () => {
            console.log("[CLICK] btn_ai_execute");
            const raw = (document.querySelector("#ai_json")?.value || "{}").trim();
            try {
                const payload = JSON.parse(raw);
                const r = await fetchJSON("/ai/run", { method: "POST", body: payload });
                setOutput("#out_ai", r);
            } catch (e) {
                setOutput("#out_ai", e);
            }
        });
        console.log("[BIND] ✓ btn_ai_execute");
    }

    // ===== Workflow Run =====
    const btnWorkflow = document.querySelector("#btn_workflow_run");
    if (btnWorkflow) {
        btnWorkflow.addEventListener("click", async () => {
            console.log("[CLICK] btn_workflow_run");
            const raw = (document.querySelector("#workflow_json")?.value || "{}").trim();
            try {
                const payload = JSON.parse(raw);
                const r = await fetchJSON("/workflows/run", { method: "POST", body: payload });
                setOutput("#out_workflow", r);
            } catch (e) {
                setOutput("#out_workflow", e);
            }
        });
        console.log("[BIND] ✓ btn_workflow_run");
    }

    // ===== Agent Info =====
    const btnInfo = document.querySelector("#btn_info");
    if (btnInfo) {
        btnInfo.addEventListener("click", async () => {
            console.log("[CLICK] btn_info");
            try {
                const info = await fetchJSON("/api/info");
                setOutput("#out_info", info);
            } catch (e) {
                setOutput("#out_info", e);
            }
        });
        console.log("[BIND] ✓ btn_info");
    }

    console.log("[BIND] ✅ All UI events bound successfully!");
}

// Auto-bind when DOM is ready
if (document.readyState === "loading") {
    console.log("[APP] DOM loading, waiting for DOMContentLoaded...");
    document.addEventListener("DOMContentLoaded", () => {
        console.log("[APP] DOMContentLoaded fired");
        bindUI();
    });
} else {
    console.log("[APP] DOM already loaded, binding immediately");
    bindUI();
}

console.log("[APP] opena7 dashboard initialized!");
