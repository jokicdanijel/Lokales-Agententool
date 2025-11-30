class CalendarDashboard {
    constructor() {
        this.events = [];
        this.currentMonth = new Date().getMonth();
        this.currentYear = new Date().getFullYear();
        this.startTime = Date.now();
        this.init();
    }
    async init() {
        this.bindEvents();
        this.setTodayDate();
        await this.loadHealth();
        await this.loadEvents();
        this.renderCalendar();
        this.startIntervals();
        this.updateUptime();
        setInterval(() => this.updateUptime(), 1000);
    }
    bindEvents() {
        document.getElementById('event-form')?.addEventListener('submit', e => this.createEvent(e));
    }
    setTodayDate() {
        const today = new Date();
        document.getElementById('event-date').value = today.toISOString().split('T')[0];
        document.getElementById('date-today').textContent = today.toLocaleDateString(CONFIG.UI.DATE_LOCALE);
    }
    async apiCall(endpoint, method = 'GET', body = null) {
        const opts = { method, headers: { 'Content-Type': 'application/json', 'Authorization': `${CONFIG.AUTH.BEARER_PREFIX}${localStorage.getItem(CONFIG.AUTH.TOKEN_KEY) || ''}` } };
        if (body) opts.body = JSON.stringify(body);
        try {
            const res = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, opts);
            return await res.json();
        } catch (e) { console.error('API Error:', e); return null; }
    }
    async loadHealth() {
        const data = await this.apiCall(CONFIG.ENDPOINTS.HEALTH);
        const status = document.getElementById('connection-status');
        if (data?.status === 'ok') {
            status.className = 'status-indicator status-ok';
            status.querySelector('.status-text').textContent = 'Online';
            document.getElementById('total-events').textContent = data.total_events || 0;
        } else {
            status.className = 'status-indicator status-error';
            status.querySelector('.status-text').textContent = 'Offline';
        }
    }
    async loadEvents() {
        const data = await this.apiCall(CONFIG.ENDPOINTS.EVENTS_LIST);
        if (data?.events) {
            this.events = data.events;
            this.renderTodayEvents();
            this.renderUpcomingEvents();
            this.updateMetrics();
            this.renderCalendar();
        }
    }
    async createEvent(e) {
        e.preventDefault();
        const event = {
            title: document.getElementById('event-title').value,
            description: document.getElementById('event-description').value,
            date: document.getElementById('event-date').value,
            time: document.getElementById('event-time').value,
            duration: parseInt(document.getElementById('event-duration').value) || 60,
            type: document.getElementById('event-type').value,
            location: document.getElementById('event-location').value,
            repeat: document.getElementById('event-repeat').value
        };
        const res = await this.apiCall(CONFIG.ENDPOINTS.EVENTS_CREATE, 'POST', event);
        if (res?.event_id) {
            this.toast('Event erstellt!', 'success');
            document.getElementById('event-form').reset();
            this.setTodayDate();
            await this.loadEvents();
            await this.loadHealth();
            this.addActivity(`Event "${event.title}" erstellt`);
        } else this.toast('Fehler beim Erstellen', 'danger');
    }
    renderTodayEvents() {
        const container = document.getElementById('today-list');
        const today = new Date().toISOString().split('T')[0];
        const todayEvents = this.events.filter(e => e.date === today);
        document.getElementById('today-events').textContent = todayEvents.length;
        if (!todayEvents.length) { container.innerHTML = '<p class="empty-state">Keine Events heute</p>'; return; }
        container.innerHTML = todayEvents.map(e => `
            <div class="event-item ${e.type}">
                <div><strong>${e.title}</strong><br><span class="event-time">${e.time}</span> ${e.location ? '• ' + e.location : ''}</div>
                <button class="btn btn-sm btn-secondary" onclick="calendar.deleteEvent('${e.id}')">✕</button>
            </div>
        `).join('');
    }
    renderUpcomingEvents() {
        const container = document.getElementById('upcoming-list');
        const today = new Date();
        const weekEnd = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
        const upcoming = this.events.filter(e => {
            const d = new Date(e.date);
            return d > today && d <= weekEnd;
        }).slice(0, 10);
        document.getElementById('week-events').textContent = upcoming.length;
        if (!upcoming.length) { container.innerHTML = '<p class="empty-state">Keine kommenden Events</p>'; return; }
        container.innerHTML = upcoming.map(e => `
            <div class="event-item ${e.type}">
                <div><strong>${e.title}</strong><br><small>${new Date(e.date).toLocaleDateString(CONFIG.UI.DATE_LOCALE)} ${e.time}</small></div>
            </div>
        `).join('');
    }
    updateMetrics() {
        document.getElementById('total-events').textContent = this.events.length;
    }
    renderCalendar() {
        const grid = document.getElementById('calendar-grid');
        document.getElementById('calendar-month').textContent = `${CONFIG.MONTHS[this.currentMonth]} ${this.currentYear}`;
        let html = CONFIG.WEEKDAYS.map(d => `<div class="calendar-header">${d}</div>`).join('');
        const firstDay = new Date(this.currentYear, this.currentMonth, 1).getDay();
        const daysInMonth = new Date(this.currentYear, this.currentMonth + 1, 0).getDate();
        const startDay = firstDay === 0 ? 6 : firstDay - 1;
        const prevMonth = new Date(this.currentYear, this.currentMonth, 0).getDate();
        for (let i = startDay - 1; i >= 0; i--) html += `<div class="calendar-day other-month">${prevMonth - i}</div>`;
        const today = new Date();
        for (let d = 1; d <= daysInMonth; d++) {
            const dateStr = `${this.currentYear}-${String(this.currentMonth + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
            const isToday = d === today.getDate() && this.currentMonth === today.getMonth() && this.currentYear === today.getFullYear();
            const hasEvents = this.events.some(e => e.date === dateStr);
            html += `<div class="calendar-day${isToday ? ' today' : ''}${hasEvents ? ' has-events' : ''}" onclick="calendar.selectDate('${dateStr}')">${d}</div>`;
        }
        const remaining = 42 - startDay - daysInMonth;
        for (let d = 1; d <= remaining; d++) html += `<div class="calendar-day other-month">${d}</div>`;
        grid.innerHTML = html;
    }
    selectDate(dateStr) {
        document.getElementById('event-date').value = dateStr;
        this.toast(`Datum gewählt: ${new Date(dateStr).toLocaleDateString(CONFIG.UI.DATE_LOCALE)}`, 'success');
    }
    prevMonth() { if (this.currentMonth === 0) { this.currentMonth = 11; this.currentYear--; } else this.currentMonth--; this.renderCalendar(); }
    nextMonth() { if (this.currentMonth === 11) { this.currentMonth = 0; this.currentYear++; } else this.currentMonth++; this.renderCalendar(); }
    async deleteEvent(id) {
        const res = await this.apiCall(CONFIG.ENDPOINTS.EVENTS_DELETE, 'POST', { event_id: id });
        if (res?.success) { this.toast('Event gelöscht', 'success'); await this.loadEvents(); }
    }
    addActivity(msg) {
        const log = document.getElementById('activity-log');
        const item = document.createElement('div');
        item.className = 'activity-item';
        item.textContent = `${new Date().toLocaleTimeString(CONFIG.UI.DATE_LOCALE)} - ${msg}`;
        log.insertBefore(item, log.firstChild);
        while (log.children.length > CONFIG.UI.MAX_ACTIVITY_ITEMS) log.removeChild(log.lastChild);
    }
    updateUptime() {
        const s = Math.floor((Date.now() - this.startTime) / 1000);
        document.getElementById('uptime').textContent = `${Math.floor(s/3600).toString().padStart(2,'0')}:${Math.floor((s%3600)/60).toString().padStart(2,'0')}:${(s%60).toString().padStart(2,'0')}`;
        document.getElementById('last-update').textContent = new Date().toLocaleTimeString(CONFIG.UI.DATE_LOCALE);
    }
    toast(msg, type = 'info') {
        const c = document.getElementById('toast-container');
        const t = document.createElement('div');
        t.className = `toast bg-${type}`;
        t.textContent = msg;
        c.appendChild(t);
        setTimeout(() => t.remove(), CONFIG.UI.TOAST_DURATION);
    }
    startIntervals() {
        setInterval(() => this.loadHealth(), CONFIG.REFRESH_INTERVALS.STATUS);
        setInterval(() => this.loadEvents(), CONFIG.REFRESH_INTERVALS.EVENTS);
    }
}
function saveToken() {
    const token = document.getElementById('token').value;
    if (token) { localStorage.setItem(CONFIG.AUTH.TOKEN_KEY, token); calendar.toast('Token gespeichert', 'success'); }
}
async function importIcal() {
    const file = document.getElementById('ical-file').files[0];
    if (!file) { calendar.toast('Keine Datei gewählt', 'warning'); return; }
    const text = await file.text();
    const res = await calendar.apiCall(CONFIG.ENDPOINTS.ICAL_IMPORT, 'POST', { ical_data: text });
    if (res?.imported) { calendar.toast(`${res.imported} Events importiert`, 'success'); await calendar.loadEvents(); }
}
async function exportIcal() {
    const res = await calendar.apiCall(CONFIG.ENDPOINTS.ICAL_EXPORT);
    if (res?.ical_data) {
        const blob = new Blob([res.ical_data], { type: 'text/calendar' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a'); a.href = url; a.download = 'calendar.ics'; a.click();
        calendar.toast('Kalender exportiert', 'success');
    }
}
const calendar = new CalendarDashboard();
