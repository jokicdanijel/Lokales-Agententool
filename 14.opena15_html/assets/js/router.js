// assets/js/router.js
import { loadPage } from "./state.js";

export const routes = {
  "/agents/opena5": () => loadPage("agent_opena5"),
  "/agents/opena5/logs": () => loadPage("agent_opena5_logs"),
  "/agents/opena5/config": () => loadPage("agent_opena5_config"),
};

function handleRoute() {
  const path = location.hash.replace("#", "") || "/agents/opena5";
  const fn = routes[path] || routes["/agents/opena5"];
  fn();
}

window.addEventListener("hashchange", handleRoute);
window.addEventListener("DOMContentLoaded", handleRoute);
