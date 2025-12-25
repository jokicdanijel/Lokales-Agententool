/**
 * 🔗 PORTIER API Client für VSCode Extension
 * Leichtgewichtiger Client für opena5_vscode Agent Integration
 */

const fetch = require("node-fetch");

class PortierAPI {
  constructor(baseUrl = "http://127.0.0.1:12348", bearerToken = "") {
    this.baseUrl = baseUrl.replace(/\/$/, ""); // Remove trailing slash
    this.bearerToken = bearerToken;
    this.timeout = 30000; // 30 seconds

    console.log(`🔌 PORTIER API Client initialized: ${this.baseUrl}`);
  }

  /**
   * Health Check
   */
  async health() {
    return await this._get("/health");
  }

  /**
   * Detailed Agent Status
   */
  async status() {
    return await this._get("/status");
  }

  /**
   * Execute Command
   */
  async command(payload) {
    return await this._post("/command", payload);
  }

  /**
   * Specialized Actions (VSCode specific)
   */
  async specialized(payload) {
    return await this._post("/specialized", payload);
  }

  /**
   * VSCode specific endpoints
   */
  async vscode_analyze(payload) {
    return await this._post("/vscode/analyze", payload);
  }

  async vscode_refactor(payload) {
    return await this._post("/vscode/refactor", payload);
  }

  async vscode_format(payload) {
    return await this._post("/vscode/format", payload);
  }

  async vscode_fix(payload) {
    return await this._post("/vscode/fix", payload);
  }

  async vscode_tests(payload) {
    return await this._post("/vscode/tests", payload);
  }

  async vscode_agents() {
    return await this._get("/vscode/agents");
  }

  async vscode_create_file(payload) {
    return await this._post("/vscode/file/create", payload);
  }

  async vscode_modify_file(payload) {
    return await this._post("/vscode/file/modify", payload);
  }

  async vscode_delete_file(path) {
    return await this._delete(`/vscode/file/${encodeURIComponent(path)}`);
  }

  /**
   * Get Logs
   */
  async logs() {
    return await this._get("/logs");
  }

  /**
   * Get Metrics
   */
  async metrics() {
    return await this._get("/metrics");
  }

  /**
   * Get Configuration
   */
  async config() {
    return await this._get("/config");
  }

  /**
   * Get Safepoints (ArchivP integration)
   */
  async safepoints() {
    return await this._get("/safepoints");
  }

  /**
   * HTTP GET Request
   */
  async _get(path) {
    const url = `${this.baseUrl}${path}`;

    try {
      const response = await fetch(url, {
        method: "GET",
        headers: this._getHeaders(),
        timeout: this.timeout,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`❌ GET ${url} failed:`, error.message);
      throw new Error(`API GET failed: ${error.message}`);
    }
  }

  /**
   * HTTP POST Request
   */
  async _post(path, payload = {}) {
    const url = `${this.baseUrl}${path}`;

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          ...this._getHeaders(),
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
        timeout: this.timeout,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`❌ POST ${url} failed:`, error.message);
      throw new Error(`API POST failed: ${error.message}`);
    }
  }

  /**
   * HTTP DELETE Request
   */
  async _delete(path) {
    const url = `${this.baseUrl}${path}`;

    try {
      const response = await fetch(url, {
        method: "DELETE",
        headers: this._getHeaders(),
        timeout: this.timeout,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`❌ DELETE ${url} failed:`, error.message);
      throw new Error(`API DELETE failed: ${error.message}`);
    }
  }

  /**
   * Get Request Headers
   */
  _getHeaders() {
    const headers = {
      "User-Agent": "PORTIER-VSCode-Extension/3.0.0",
    };

    if (this.bearerToken) {
      headers["Authorization"] = `Bearer ${this.bearerToken}`;
    }

    return headers;
  }

  /**
   * Test Connection
   */
  async testConnection() {
    try {
      const health = await this.health();
      console.log(`✅ PORTIER API connection successful:`, health);
      return true;
    } catch (error) {
      console.error(`❌ PORTIER API connection failed:`, error.message);
      return false;
    }
  }

  /**
   * Set Bearer Token
   */
  setBearerToken(token) {
    this.bearerToken = token;
    console.log(`🔑 Bearer token updated`);
  }

  /**
   * Set Base URL
   */
  setBaseUrl(url) {
    this.baseUrl = url.replace(/\/$/, "");
    console.log(`🌐 Base URL updated: ${this.baseUrl}`);
  }

  /**
   * Set Timeout
   */
  setTimeout(ms) {
    this.timeout = ms;
    console.log(`⏱️ Timeout updated: ${ms}ms`);
  }
}

module.exports = { PortierAPI };
