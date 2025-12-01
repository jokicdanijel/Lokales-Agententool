async function api(path, method="GET", payload=null) {
    const token = document.getElementById("token").value.trim();
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = "Bearer " + token;

    try {
        const res = await fetch(CONFIG.BASE_URL + path, {
            method,
            headers,
            body: payload ? JSON.stringify(payload) : null
        });

        if (!res.ok) {
            throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        }

        return await res.json();
    } catch (error) {
        return { error: error.message, timestamp: new Date().toISOString() };
    }
}

const setLog = (id, data) => {
    const element = document.getElementById(id);
    element.textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
    element.scrollTop = element.scrollHeight;
};

async function checkHealth() {
    setLog("health_output", "⏳ Checking health...");
    const result = await api("/health");
    setLog("health_output", result);
}

async function sendChat() {
    setLog("chat_output", "⏳ Sending chat...");
    const prompt = document.getElementById("chat_prompt").value;
    if (!prompt.trim()) {
        setLog("chat_output", { error: "Prompt darf nicht leer sein" });
        return;
    }
    const result = await api("/native", "POST", { prompt, model: "gpt-4" });
    setLog("chat_output", result);
}

async function sendCMD() {
    setLog("cmd_output", "⏳ Sending CMD...");
    try {
        const json = JSON.parse(document.getElementById("cmd_json").value);
        const result = await api("/cmd", "POST", json);
        setLog("cmd_output", result);
    } catch (error) {
        setLog("cmd_output", { error: "Invalid JSON: " + error.message });
    }
}

async function dispatchReady() {
    setLog("dispatch_output", "⏳ Checking dispatch status...");
    const result = await api("/dispatch_ready");
    setLog("dispatch_output", result);
}

async function runSelftest() {
    setLog("selftest_output", "⏳ Running selftest...");
    const result = await api("/selftest");
    setLog("selftest_output", result);
}

// Auto-load token from localStorage
document.addEventListener('DOMContentLoaded', function() {
    const savedToken = localStorage.getItem('opena3_token');
    if (savedToken) {
        document.getElementById('token').value = savedToken;
    }
    
    // Save token on change
    document.getElementById('token').addEventListener('change', function() {
        localStorage.setItem('opena3_token', this.value);
    });
});