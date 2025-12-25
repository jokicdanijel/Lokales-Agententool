// CRM Agent Configuration | PAS-6.0
const CONFIG = {
  agent: {
    id: "opena18",
    name: "CRM Agent",
    kuerzel: "crmp",
    port: 12364,
    version: "PAS-6.0",
  },
  api: {
    baseUrl: "http://127.0.0.1:12364",
    timeout: 30000,
  },
  dashboard: { port: 12349 },
  coordinator: { port: 12344 },
  archivator: { port: 12345 },
};
if (typeof module !== "undefined" && module.exports) {
  module.exports = CONFIG;
}
