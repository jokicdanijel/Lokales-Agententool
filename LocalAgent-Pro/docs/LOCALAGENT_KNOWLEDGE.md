# LocalAgent-Pro – Wissensbasis & Systemzustand

Dieser Stand beschreibt den aktuell bekannten Zustand von **LocalAgent-Pro**
inkl. Integration in das ELION / Hyper-Dashboard Ökosystem.

---

## 1. Runtime-Snapshot (/health)

**Quelle:**

```bash
cd "/home/danijel-jd/Dokumente/Workspace/Projekte/Lokales Agententool/LocalAgent-Pro" \
  && curl -s http://127.0.0.1:8001/health | jq .
```

**Aktueller Response:**

```json
{
  "allowed_domains": [
    "*"
  ],
  "auto_whitelist_count": 24,
  "auto_whitelist_enabled": true,
  "model": "llama3.1",
  "open_webui_port": 3000,
  "sandbox": true,
  "sandbox_path": "/home/danijel-jd/localagent_sandbox",
  "server_time": 1763522128,
  "status": "ok"
}
```

**Interpretation:**

- **Status:** `ok` → LocalAgent-Pro ist aus Sicht des Health-Endpunkts betriebsbereit.
- **Modell:** `llama3.1` (lokale Inferenz)
- **Sandbox-Modus:** `true`
  - Alle Datei-Operationen laufen über: `/home/danijel-jd/localagent_sandbox`
- **Web-Zugriff:**
  - `allowed_domains: ["*"]` → aktuell effektiv „alle Domains", aber überwacht durch Auto-Whitelist
  - `auto_whitelist_enabled: true`
  - `auto_whitelist_count: 24` → bisher 24 Domains automatisch freigeschaltet
- **OpenWebUI-Port (Upstream UI/Backend):** `3000`
- **Serverzeit (Epoch):** `1763522128` (nur für Tracing wichtig)

---

## 2. Prozessstatus

**Quelle:**

```bash
ps aux | grep "python.*openwebui_agent_server" | grep -v grep
```

**Aktueller Prozess:**

```text
danijel+  219253  0.0  0.1 199332 39568 pts/6    S    03:54   0:00 python src/openwebui_agent_server.py
```

**Interpretation:**

Der Agent-Server läuft als:

- **User:** `danijel-jd`
- **Command:** `python src/openwebui_agent_server.py`

LocalAgent-Pro ist damit aktiv und lauscht auf seinen internen Ports (Health/Metrics/API).

---

## 3. Konfigurationsstände (config/)

**Quelle:**

```bash
cd "/home/danijel-jd/Dokumente/Workspace/Projekte/Lokales Agententool/LocalAgent-Pro" \
  && ls -la config/
```

**Aktuelle Files:**

- `config_safe.yaml`
- `config.yaml`
- `domain_whitelist.yaml`
- `grafana_dashboard_localagent.json`
- `prometheus_localagent.yml`
- `system_prompt.txt`
- (zusätzlich: `vscode-icons-12.15.0.tar.gz` – nur Asset / Icon-Pack)

### 3.1. Rollen der Konfigurationsdateien

#### `config.yaml`

Primäre Laufzeitkonfiguration von LocalAgent-Pro (Ports, Sandbox-Flag, Tools, etc.).

#### `config_safe.yaml`

Bereinigte/sanitized Version für Doku/Sharing (z.B. ohne Secrets, Tokens, interne Pfade).

#### `domain_whitelist.yaml`

Steuerung der erlaubten Domains für Web-Zugriffe.
Ergänzt bzw. überschreibt dynamische Auto-Whitelist-Einträge.

#### `grafana_dashboard_localagent.json`

Fertiges Grafana-Dashboard für Monitoring von LocalAgent-Pro
(Panels: Health, Latenzen, Error-Rates, Tool-Usage, Sandbox vs. Live).

#### `prometheus_localagent.yml`

Prometheus-Scrape-Config für LocalAgent-Pro-Metriken.

#### `system_prompt.txt`

Systemverhalten / Personality / Betriebslogik für den lokalen Agenten.
Wird beim Start in den LLM-Kontext injiziert.

---

## 4. Monitoring & Observability

### 4.1. Metrics-Endpunkt

**Check:**

```bash
curl -s http://127.0.0.1:8001/metrics | grep "localagent_" | wc -l \
  && echo "Metriken verfügbar"
```

**Beobachteter Output:**

```text
33
Metriken verfügbar
```

**Interpretation:**

LocalAgent-Pro exportiert aktuell **33 projektbezogene Metriken** mit Präfix `localagent_`.

### 4.2. Prometheus-Target

**Check:**

```bash
curl -s http://localhost:9090/api/v1/targets \
  | jq '.data.activeTargets[] | select(.labels.job=="localagent-pro") | .health'
```

**Beobachteter Output:**

```text
"up"
```

**Interpretation:**

- Prometheus scrape't LocalAgent-Pro erfolgreich.
- **Job-Name:** `localagent-pro`
- **Health:** `up` → Metriken werden regelmäßig eingesammelt.

### 4.3. Einbindung in ELION Dashboard (opena20)

`opena20` (Dashboard-Agent) konsumiert:

- `localagent_`-Metriken über Prometheus
- kombiniert Health von LocalAgent-Pro mit anderen Agenten
- generiert ggf. Alerts (ALERT-Events → opena2 → opena1)

---

## 5. Rolle in der ELION-Architektur (opena21)

LocalAgent-Pro ist als dedizierter Agent in der ELION-Agentenlandschaft vorgesehen.

- **Agent-ID:** `opena21`
- **Port (ELION-Seite):** `12364`
- **Rolle:** AI-Inferenz- / Tool-Agent (LLM-Core)
- **Upstream-Endpoint:** `http://127.0.0.1:8001` (LocalAgent-Pro API)

### 5.1. Verantwortlichkeiten

- LLM-Inferenz (Text, Planung, Analyse)
- Dateioperationen im Sandbox-Modus
- Optional Shell-Ausführung (Live-Modus; default: deaktiviert)
- Web-Fetch auf whitelisten Domains
- **Kein eigener Safepoint-Writer** – arbeitet ausschließlich als „Exec-Engine"

### 5.2. Request-Flow in ELION

1. **User-Input** (z.B. Telegram, UI, später: Mail/WhatsApp/Calls)
2. **Eingang über Channel-Agent:**
   - `opena3` (OpenWebUI) oder
   - `opena4` (Telegram-Bot)
3. **Persistenz / Wahrheitsanker:**
   - opena4/opena3 → `opena2` (Archivator, `MSG_IN` Safepoint)
4. **Orchestrierung:**
   - `opena1` (Koordinator) liest neuen Safepoint
   - Entscheidet, ob `opena21` (LocalAgent-Pro) involviert werden soll
5. **Ausführung:**
   - opena1 → opena21: strukturierter Job (Tool-Call / Inferenzauftrag)
   - opena21 ruft intern LocalAgent-Pro auf (Port 8001)
6. **Ergebnis:**
   - opena21 → opena1: Resultat (z.B. Tool-Result, Auswertung)
   - opena1 schreibt Response als Safepoint nach opena2 (`MSG_OUT`)
   - Channel-Agent sendet Antwort an den Benutzer.

**Prinzip:**

> ELION entscheidet → LocalAgent-Pro arbeitet → opena2 bleibt Wahrheit.

---

## 6. Sicherheit & Policies

### Sandbox = true

Alle Dateiinteraktionen laufen über `/home/danijel-jd/localagent_sandbox`

### Shell-Commands

Live-Ausführung ist standardmäßig **deaktiviert** (Konfig-Ebene).

### Web-Zugriff

Grundsätzlich erlaubt, aber durch Auto-Whitelist + `domain_whitelist.yaml` gesteuert.
Aktuell **24 Domains** automatisch whitelisted.

### Auditierbarkeit

Kritische Aktionen sind in ELION über **Safepoints** nachverfolgbar (opena2 Archiv).

---

## 7. Quick-Checks (Operational Runbook)

### Health prüfen

```bash
cd "/home/danijel-jd/Dokumente/Workspace/Projekte/Lokales Agententool/LocalAgent-Pro"
curl -s http://127.0.0.1:8001/health | jq .
```

### Metriken zählen

```bash
curl -s http://127.0.0.1:8001/metrics | grep "localagent_" | wc -l
```

### Prometheus-Target-Health

```bash
curl -s http://localhost:9090/api/v1/targets \
  | jq '.data.activeTargets[] | select(.labels.job=="localagent-pro") | .health'
```

### Agent-Server Prozess prüfen

```bash
ps aux | grep "python.*openwebui_agent_server" | grep -v grep
```

---

## 8. Status: Wissensstand

- ✅ **Lokaler Agent (LocalAgent-Pro):** läuft, Status `ok`
- ✅ **Monitoring:** aktiv, 33 projektbezogene Metriken, Prometheus-Target `up`
- ✅ **Konfiguration:** zentral in `config/` abgelegt, inkl. Whitelist, Prometheus, Grafana
- ✅ **Integration in ELION:** als `opena21` (Port 12364) vorgesehen/integriert
- ✅ **Sicherheitsmodell:** Sandbox aktiv, Web kontrolliert, Shell nur explizit

---

**Dieses Dokument fungiert als Single Source of Truth für den aktuellen
Wissensstand von LocalAgent-Pro innerhalb des Hyper-Dashboard Systems.**
