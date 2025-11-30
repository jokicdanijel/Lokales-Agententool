// 📞 OPENA9 Telephone Dashboard - Application Logic
// PORTIER PAS-6.0

class TelephoneDashboard {
    constructor() {
        this.refreshIntervals = {};
        this.activityLog = [];
        this.activeCalls = [];
        this.metrics = null;
        this.startTime = Date.now();
        
        this.init();
    }
    
    async init() {
        console.log('📞 OPENA9 Telephone Dashboard initialisiert');
        
        // Bind event handlers
        this.bindEvents();
        
        // Initial data fetch
        await this.refreshAll();
        
        // Start auto-refresh
        this.startAutoRefresh();
        
        // Update uptime display
        this.updateUptimeDisplay();
        setInterval(() => this.updateUptimeDisplay(), 1000);
    }
    
    bindEvents() {
        // Call form
        document.getElementById('call-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.makeCall();
        });
        
        // Voice form
        document.getElementById('voice-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateVoice();
        });
        
        // Hangup button
        document.getElementById('btn-hangup')?.addEventListener('click', () => {
            this.hangupCall();
        });
        
        // Speed slider
        document.getElementById('voice-speed')?.addEventListener('input', (e) => {
            document.getElementById('speed-value').textContent = `${e.target.value}x`;
        });
    }
    
    // === API Calls ===
    
    async apiCall(endpoint, options = {}) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        // Add auth token if available
        const token = localStorage.getItem(CONFIG.AUTH.TOKEN_KEY);
        if (token) {
            defaultOptions.headers['Authorization'] = `${CONFIG.AUTH.BEARER_PREFIX}${token}`;
        }
        
        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }
    
    async refreshAll() {
        await Promise.all([
            this.fetchStatus(),
            this.fetchMetrics(),
            this.fetchActiveCalls()
        ]);
    }
    
    async fetchStatus() {
        try {
            const data = await this.apiCall(CONFIG.ENDPOINTS.HEALTH);
            this.updateConnectionStatus(data.status === 'healthy');
            this.updateServiceStatus(data);
        } catch (error) {
            this.updateConnectionStatus(false);
        }
    }
    
    async fetchMetrics() {
        try {
            const data = await this.apiCall(CONFIG.ENDPOINTS.METRICS);
            this.metrics = data;
            this.updateMetricsDisplay(data);
        } catch (error) {
            console.error('Metrics fetch failed:', error);
        }
    }
    
    async fetchActiveCalls() {
        try {
            const data = await this.apiCall(CONFIG.SPECIALIZED_ENDPOINTS.ACTIVE_CALLS);
            this.activeCalls = data.calls || [];
            this.updateActiveCallsDisplay();
        } catch (error) {
            console.error('Active calls fetch failed:', error);
        }
    }
    
    // === Call Functions ===
    
    async makeCall() {
        const phoneNumber = document.getElementById('phone-number').value;
        const callerId = document.getElementById('caller-id').value;
        const voiceMessage = document.getElementById('voice-message').value;
        
        if (!phoneNumber) {
            this.showToast('Bitte Telefonnummer eingeben', 'error');
            return;
        }
        
        try {
            const response = await this.apiCall(CONFIG.SPECIALIZED_ENDPOINTS.MAKE_CALL, {
                method: 'POST',
                body: JSON.stringify({
                    to: phoneNumber,
                    from: callerId || CONFIG.TWILIO.DEFAULT_CALLER_ID,
                    voice_message: voiceMessage || null
                })
            });
            
            this.showToast(`Anruf gestartet: ${phoneNumber}`, 'success');
            this.addActivity('📞', `Anruf an ${phoneNumber} gestartet`);
            
            // Enable hangup button
            document.getElementById('btn-hangup').disabled = false;
            
            // Refresh active calls
            await this.fetchActiveCalls();
            
        } catch (error) {
            this.showToast(`Anruf fehlgeschlagen: ${error.message}`, 'error');
            this.addActivity('❌', `Anruf fehlgeschlagen: ${error.message}`);
        }
    }
    
    async hangupCall() {
        if (this.activeCalls.length === 0) {
            this.showToast('Keine aktiven Anrufe', 'info');
            return;
        }
        
        const callId = this.activeCalls[0]?.call_id;
        
        try {
            await this.apiCall(CONFIG.SPECIALIZED_ENDPOINTS.HANGUP, {
                method: 'POST',
                body: JSON.stringify({ call_id: callId })
            });
            
            this.showToast('Anruf beendet', 'success');
            this.addActivity('📴', 'Anruf beendet');
            
            document.getElementById('btn-hangup').disabled = true;
            await this.fetchActiveCalls();
            
        } catch (error) {
            this.showToast(`Auflegen fehlgeschlagen: ${error.message}`, 'error');
        }
    }
    
    // === Voice Generation ===
    
    async generateVoice() {
        const text = document.getElementById('voice-text').value;
        const voice = document.getElementById('voice-style').value;
        const speed = parseFloat(document.getElementById('voice-speed').value);
        
        if (!text) {
            this.showToast('Bitte Text eingeben', 'error');
            return;
        }
        
        try {
            const response = await this.apiCall(CONFIG.SPECIALIZED_ENDPOINTS.VOICE_GENERATE, {
                method: 'POST',
                body: JSON.stringify({
                    text: text,
                    voice: voice,
                    speed: speed
                })
            });
            
            if (response.audio_url) {
                const audioElement = document.getElementById('generated-audio');
                audioElement.src = response.audio_url;
                document.getElementById('audio-output').classList.remove('hidden');
            }
            
            this.showToast('Sprache generiert', 'success');
            this.addActivity('🎙️', `Voice generiert: "${text.substring(0, 30)}..."`);
            
        } catch (error) {
            this.showToast(`Voice-Generierung fehlgeschlagen: ${error.message}`, 'error');
        }
    }
    
    // === Display Updates ===
    
    updateConnectionStatus(connected) {
        const statusEl = document.getElementById('connection-status');
        statusEl.className = `status-indicator status-${connected ? 'ok' : 'error'}`;
        statusEl.querySelector('.status-text').textContent = connected ? 'Verbunden' : 'Offline';
    }
    
    updateServiceStatus(data) {
        const services = {
            'status-twilio': data.twilio_connected || false,
            'status-sip': data.sip_gateway_active || false,
            'status-asterisk': data.asterisk_connected || false,
            'status-openai': data.openai_connected || false
        };
        
        for (const [id, status] of Object.entries(services)) {
            const el = document.getElementById(id);
            if (el) {
                el.className = `service-status status-${status ? 'ok' : 'error'}`;
            }
        }
    }
    
    updateMetricsDisplay(data) {
        const counters = data.counters || {};
        const timings = data.timings || {};
        const rates = data.rates || {};
        
        // Status cards
        const callsMade = counters.calls_made || 0;
        const callsAnswered = counters.calls_answered || 0;
        const callsFailed = counters.calls_failed || 0;
        const activeCalls = data.status?.current_active_calls || 0;
        
        this.setElementText('calls-total', callsMade + callsAnswered);
        this.setElementText('calls-success', callsAnswered);
        this.setElementText('calls-failed', callsFailed);
        this.setElementText('active-calls', activeCalls);
        
        // Metrics panel
        this.setElementText('avg-duration', `${Math.round(timings.average_call_duration_seconds || 0)}s`);
        this.setElementText('voice-generations', counters.voice_responses_generated || 0);
        this.setElementText('transcriptions', counters.transcriptions_completed || 0);
        this.setElementText('api-response', `${Math.round(timings.average_response_time_ms || 0)}ms`);
        this.setElementText('error-rate', `${(rates.error_rate || 0).toFixed(1)}%`);
        this.setElementText('calls-per-hour', (rates.calls_per_hour || 0).toFixed(1));
    }
    
    updateActiveCallsDisplay() {
        const container = document.getElementById('active-calls-list');
        
        if (this.activeCalls.length === 0) {
            container.innerHTML = '<p class="empty-state">Keine aktiven Anrufe</p>';
            document.getElementById('btn-hangup').disabled = true;
            return;
        }
        
        container.innerHTML = this.activeCalls.map(call => `
            <div class="call-item">
                <div class="call-info">
                    <span class="call-number">${call.to || call.number || 'Unbekannt'}</span>
                    <span class="call-duration">${call.duration || '0:00'}</span>
                </div>
                <span class="call-status">${call.status || 'active'}</span>
            </div>
        `).join('');
        
        document.getElementById('btn-hangup').disabled = false;
    }
    
    updateUptimeDisplay() {
        const elapsed = Date.now() - this.startTime;
        const seconds = Math.floor(elapsed / 1000);
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        const formatted = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        this.setElementText('uptime', formatted);
        
        // Update last update time
        const now = new Date().toLocaleTimeString(CONFIG.UI.DATE_LOCALE);
        this.setElementText('last-update', `Letztes Update: ${now}`);
    }
    
    // === Activity Log ===
    
    addActivity(icon, message) {
        const time = new Date().toLocaleTimeString(CONFIG.UI.DATE_LOCALE);
        
        this.activityLog.unshift({
            time,
            icon,
            message
        });
        
        // Limit log size
        if (this.activityLog.length > CONFIG.UI.MAX_ACTIVITY_ITEMS) {
            this.activityLog = this.activityLog.slice(0, CONFIG.UI.MAX_ACTIVITY_ITEMS);
        }
        
        this.updateActivityLogDisplay();
    }
    
    updateActivityLogDisplay() {
        const container = document.getElementById('activity-log');
        
        if (this.activityLog.length === 0) {
            container.innerHTML = '<p class="empty-state">Keine Aktivitäten</p>';
            return;
        }
        
        container.innerHTML = this.activityLog.map(item => `
            <div class="activity-item">
                <span class="activity-icon">${item.icon}</span>
                <span class="activity-time">${item.time}</span>
                <span class="activity-message">${item.message}</span>
            </div>
        `).join('');
    }
    
    // === Utilities ===
    
    setElementText(id, text) {
        const el = document.getElementById(id);
        if (el) el.textContent = text;
    }
    
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, CONFIG.UI.TOAST_DURATION);
    }
    
    startAutoRefresh() {
        this.refreshIntervals.status = setInterval(
            () => this.fetchStatus(),
            CONFIG.REFRESH_INTERVALS.STATUS
        );
        
        this.refreshIntervals.metrics = setInterval(
            () => this.fetchMetrics(),
            CONFIG.REFRESH_INTERVALS.METRICS
        );
        
        this.refreshIntervals.calls = setInterval(
            () => this.fetchActiveCalls(),
            CONFIG.REFRESH_INTERVALS.ACTIVE_CALLS
        );
    }
    
    stopAutoRefresh() {
        Object.values(this.refreshIntervals).forEach(interval => {
            clearInterval(interval);
        });
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new TelephoneDashboard();
});