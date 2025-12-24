/**
 * opena7 Dashboard JS
 * Handles all API calls, button clicks, and UI updates
 */

const state = {
    baseUrl: window.location.origin,
    token: localStorage.getItem("opena7_token") || "",
};

/**
 * Fetch wrapper with auth + error handling
 */
async function fetchJSON(path, { method = "GET", body = null } = {}) {
    const headers = {
        "Accept": "application/json",
    };

    if (body) {
        headers["Content-Type"] = "application/json";
    }

    if (state.token) {
        headers["Authorization"] = `Bearer ${state.token}`;
    }

    try {
        const res = await fetch(`${state.baseUrl}${path}`, {
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

        if (!res.ok) {
            const msg = typeof data === "string" ? data : JSON.stringify(data);
            throw new Error(`HTTP ${res.status} - ${msg}`);
        }

        return data;
    } catch (e) {
        console.error("fetchJSON error:", e);
        throw e;
    }
}

/**
 * Set status text
 */
function setStatus(text) {
    const el = document.querySelector("#connection_status");
    if (el) {
        el.textContent = text;
        el.className = "status " + (text.includes("Connected") ? "connected" : "disconnected");
    }
}

/**
 * Set output element
 */
function setOutput(selector, obj) {
    const el = document.querySelector(selector);
    if (!el) return;

    if (typeof obj === "string") {
        el.textContent = obj;
    } else if (obj && obj.lines && Array.isArray(obj.lines)) {
        // Special handling for logs
        el.textContent = obj.lines.join("\n");
    } else {
        el.textContent = JSON.stringify(obj, null, 2);
    }
}

/**
 * Bind all event listeners
 */
function bindUI() {
    // ===== Token / Connect =====
    const tokenInput = document.querySelector("#token_input");
    if (tokenInput) {
        tokenInput.value = state.token;
    }

    document.querySelector("#btn_connect")?.addEventListener("click", async () => {
        const newToken = tokenInput?.value?.trim() || "";
        state.token = newToken;
        localStorage.setItem("opena7_token", newToken);

        setStatus("Connecting...");
        try {
            const h = await fetchJSON("/health");
            setStatus(`✅ Connected (${h.status || "healthy"})`);
            setOutput("#out_health", h);
        } catch (e) {
            setStatus(`❌ Disconnected (${e.message})`);
        }
    });

    // ===== Health =====
    document.querySelector("#btn_health")?.addEventListener("click", async () => {
        try {
            const h = await fetchJSON("/health");
            setOutput("#out_health", h);
        } catch (e) {
            setOutput("#out_health", { error: e.message });
        }
    });

    // ===== Status =====
    document.querySelector("#btn_status")?.addEventListener("click", async () => {
        try {
            const s = await fetchJSON("/api/status");
            setOutput("#out_status", s);
        } catch (e) {
            setOutput("#out_status", { error: e.message });
        }
    });

    // ===== Logs =====
    document.querySelector("#btn_logs")?.addEventListener("click", async () => {
        try {
            const logs = await fetchJSON("/api/logs?tail=50");
            setOutput("#out_logs", logs);
        } catch (e) {
            setOutput("#out_logs", { error: e.message });
        }
    });

    // ===== Execute Command =====
    document.querySelector("#btn_execute")?.addEventListener("click", async () => {
        const raw = document.querySelector("#cmd_json")?.value || "{}";
        try {
            const payload = JSON.parse(raw);
            const r = await fetchJSON("/run", { method: "POST", body: payload });
            setOutput("#out_cmd", r);
        } catch (e) {
            setOutput("#out_cmd", { error: e.message });
        }
    });

    // ===== AI Execute =====
    document.querySelector("#btn_ai_execute")?.addEventListener("click", async () => {
        const raw = document.querySelector("#ai_json")?.value || "{}";
        try {
            const payload = JSON.parse(raw);
            const r = await fetchJSON("/ai/run", { method: "POST", body: payload });
            setOutput("#out_ai", r);
        } catch (e) {
            setOutput("#out_ai", { error: e.message });
        }
    });

    // ===== Workflow Run =====
    document.querySelector("#btn_workflow_run")?.addEventListener("click", async () => {
        const raw = document.querySelector("#workflow_json")?.value || "{}";
        try {
            const payload = JSON.parse(raw);
            const r = await fetchJSON("/workflows/run", { method: "POST", body: payload });
            setOutput("#out_workflow", r);
        } catch (e) {
            setOutput("#out_workflow", { error: e.message });
        }
    });

    // ===== Agent Info =====
    document.querySelector("#btn_info")?.addEventListener("click", async () => {
        try {
            const info = await fetchJSON("/api/info");
            setOutput("#out_info", info);
        } catch (e) {
            setOutput("#out_info", { error: e.message });
        }
    });
}

// Auto-bind when DOM is ready
document.addEventListener("DOMContentLoaded", bindUI);
