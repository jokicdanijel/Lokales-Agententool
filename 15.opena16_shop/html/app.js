class ShopDashboard {
  constructor() {
    this.products = [];
    this.orders = [];
    this.startTime = Date.now();
    this.init();
  }
  async init() {
    this.bindEvents();
    await this.loadHealth();
    await this.loadProducts();
    await this.loadOrders();
    this.startIntervals();
    this.updateUptime();
    setInterval(() => this.updateUptime(), 1000);
  }
  bindEvents() {
    document
      .getElementById("product-form")
      ?.addEventListener("submit", (e) => this.createProduct(e));
    document
      .getElementById("order-form")
      ?.addEventListener("submit", (e) => this.createOrder(e));
  }
  async apiCall(endpoint, method = "GET", body = null) {
    const opts = {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `${CONFIG.AUTH.BEARER_PREFIX}${localStorage.getItem(CONFIG.AUTH.TOKEN_KEY) || ""}`,
      },
    };
    if (body) opts.body = JSON.stringify(body);
    try {
      const res = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, opts);
      return await res.json();
    } catch (e) {
      console.error("API Error:", e);
      return null;
    }
  }
  async loadHealth() {
    const data = await this.apiCall(CONFIG.ENDPOINTS.HEALTH);
    const status = document.getElementById("connection-status");
    if (data?.status === "ok") {
      status.className = "status-indicator status-ok";
      status.querySelector(".status-text").textContent = "Online";
      document.getElementById("total-products").textContent =
        data.total_products || 0;
      document.getElementById("total-orders").textContent =
        data.total_orders || 0;
    } else {
      status.className = "status-indicator status-error";
      status.querySelector(".status-text").textContent = "Offline";
    }
  }
  async loadProducts() {
    const data = await this.apiCall(CONFIG.ENDPOINTS.PRODUCTS_LIST, "POST", {
      max_results: 100,
    });
    if (data?.products) {
      this.products = data.products;
      this.renderProducts();
      this.updateProductSelect();
      this.updateMetrics();
    }
  }
  async loadOrders() {
    const data = await this.apiCall(CONFIG.ENDPOINTS.ORDERS_LIST, "POST", {
      max_results: 50,
    });
    if (data?.orders) {
      this.orders = data.orders;
      this.renderOrders();
      this.updateMetrics();
    }
  }
  async createProduct(e) {
    e.preventDefault();
    const product = {
      title: document.getElementById("product-title").value,
      description: document.getElementById("product-description").value,
      sku: document.getElementById("product-sku").value,
      price: parseFloat(document.getElementById("product-price").value) || 0,
      stock: parseInt(document.getElementById("product-stock").value) || 0,
      category: document.getElementById("product-category").value,
      status: document.getElementById("product-status").value,
      currency: CONFIG.CURRENCY,
    };
    const res = await this.apiCall(
      CONFIG.ENDPOINTS.PRODUCTS_CREATE,
      "POST",
      product,
    );
    if (res?.product_id) {
      this.toast("Produkt erstellt!", "success");
      document.getElementById("product-form").reset();
      await this.loadProducts();
      await this.loadHealth();
      this.addActivity(`Produkt "${product.title}" erstellt`);
    } else this.toast("Fehler beim Erstellen", "danger");
  }
  async createOrder(e) {
    e.preventDefault();
    const productSku = document.getElementById("order-product").value;
    if (!productSku) {
      this.toast("Bitte Produkt wählen", "warning");
      return;
    }
    const order = {
      customer_name: document.getElementById("order-customer").value,
      customer_email: document.getElementById("order-email").value,
      items: [
        {
          sku: productSku,
          quantity:
            parseInt(document.getElementById("order-quantity").value) || 1,
        },
      ],
      shipping_address: document.getElementById("order-address").value,
      currency: CONFIG.CURRENCY,
    };
    const res = await this.apiCall(
      CONFIG.ENDPOINTS.ORDERS_CREATE,
      "POST",
      order,
    );
    if (res?.order_id) {
      this.toast("Bestellung erstellt!", "success");
      document.getElementById("order-form").reset();
      await this.loadOrders();
      await this.loadHealth();
      this.addActivity(`Bestellung für "${order.customer_name}" erstellt`);
    } else this.toast("Fehler beim Bestellen", "danger");
  }
  renderProducts() {
    const container = document.getElementById("products-list");
    document.getElementById("products-count").textContent =
      this.products.length;
    if (!this.products.length) {
      container.innerHTML = '<p class="empty-state">Keine Produkte</p>';
      return;
    }
    container.innerHTML = this.products
      .slice(0, 20)
      .map(
        (p) => `
            <div class="product-item">
                <div><strong>${p.title}</strong><br><small>${p.sku} • ${p.category} • Stock: ${p.stock || 0}</small></div>
                <span class="product-price">€${(p.price || 0).toFixed(2)}</span>
            </div>
        `,
      )
      .join("");
  }
  renderOrders() {
    const container = document.getElementById("orders-list");
    if (!this.orders.length) {
      container.innerHTML = '<p class="empty-state">Keine Bestellungen</p>';
      return;
    }
    container.innerHTML = this.orders
      .slice(0, 15)
      .map(
        (o) => `
            <div class="order-item">
                <div><strong>${o.customer_name}</strong><br><small>${new Date(o.created_at).toLocaleDateString(CONFIG.UI.DATE_LOCALE)}</small></div>
                <span class="order-status ${o.status || "pending"}">${o.status || "pending"}</span>
            </div>
        `,
      )
      .join("");
  }
  updateProductSelect() {
    const select = document.getElementById("order-product");
    select.innerHTML =
      '<option value="">-- Produkt wählen --</option>' +
      this.products
        .filter((p) => p.status === "active")
        .map(
          (p) => `<option value="${p.sku}">${p.title} (€${p.price})</option>`,
        )
        .join("");
  }
  updateMetrics() {
    const active = this.products.filter((p) => p.status === "active").length;
    const draft = this.products.filter((p) => p.status === "draft").length;
    const pending = this.orders.filter((o) => o.status === "pending").length;
    const shipped = this.orders.filter((o) => o.status === "shipped").length;
    const totalRevenue = this.orders.reduce((s, o) => s + (o.total || 0), 0);
    const avgPrice = this.products.length
      ? this.products.reduce((s, p) => s + (p.price || 0), 0) /
        this.products.length
      : 0;
    const totalStock = this.products.reduce((s, p) => s + (p.stock || 0), 0);
    const categories = new Set(this.products.map((p) => p.category)).size;
    document.getElementById("active-products").textContent = active;
    document.getElementById("draft-products").textContent = draft;
    document.getElementById("pending-orders").textContent = pending;
    document.getElementById("shipped-orders").textContent = shipped;
    document.getElementById("avg-price").textContent =
      `€${avgPrice.toFixed(2)}`;
    document.getElementById("total-categories").textContent = categories;
    document.getElementById("total-revenue").textContent =
      `€${totalRevenue.toFixed(0)}`;
    document.getElementById("total-inventory").textContent = totalStock;
  }
  addActivity(msg) {
    const log = document.getElementById("activity-log");
    const item = document.createElement("div");
    item.className = "activity-item";
    item.textContent = `${new Date().toLocaleTimeString(CONFIG.UI.DATE_LOCALE)} - ${msg}`;
    log.insertBefore(item, log.firstChild);
    while (log.children.length > CONFIG.UI.MAX_ACTIVITY_ITEMS)
      log.removeChild(log.lastChild);
  }
  updateUptime() {
    const s = Math.floor((Date.now() - this.startTime) / 1000);
    document.getElementById("uptime").textContent = `${Math.floor(s / 3600)
      .toString()
      .padStart(2, "0")}:${Math.floor((s % 3600) / 60)
      .toString()
      .padStart(2, "0")}:${(s % 60).toString().padStart(2, "0")}`;
    document.getElementById("last-update").textContent =
      new Date().toLocaleTimeString(CONFIG.UI.DATE_LOCALE);
  }
  toast(msg, type = "info") {
    const c = document.getElementById("toast-container");
    const t = document.createElement("div");
    t.className = `toast bg-${type}`;
    t.textContent = msg;
    c.appendChild(t);
    setTimeout(() => t.remove(), CONFIG.UI.TOAST_DURATION);
  }
  startIntervals() {
    setInterval(() => this.loadHealth(), CONFIG.REFRESH_INTERVALS.STATUS);
    setInterval(() => this.loadProducts(), CONFIG.REFRESH_INTERVALS.PRODUCTS);
    setInterval(() => this.loadOrders(), CONFIG.REFRESH_INTERVALS.ORDERS);
  }
}
function saveToken() {
  const token = document.getElementById("token").value;
  if (token) {
    localStorage.setItem(CONFIG.AUTH.TOKEN_KEY, token);
    shop.toast("Token gespeichert", "success");
  }
}
const shop = new ShopDashboard();
