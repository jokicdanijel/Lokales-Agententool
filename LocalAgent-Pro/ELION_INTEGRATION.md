# LocalAgent-Pro ↔ ELION Hyper-Dashboard Integration

## 🎯 Architektur-Positionierung

**LocalAgent-Pro** kann als **opena21** in das ELION-System integriert werden oder als eigenständiger **Inference-Service** auf Port 8001 parallel laufen.

### Integration-Optionen

#### Option 1: Als opena21 (Inference-Agent) - Port 12364
```yaml
Agent: opena21 (AI-Inference)
Port: 12364
Rolle: LLM-basierter Inference-Service
Status: Online
Beschreibung: Lokaler AI-Agent mit Ollama (llama3.1), Tool-Execution, Sandbox
Verknüpfungen: 
  - Empfängt Aufträge von opena1 (Koordinator)
  - Schreibt Ergebnisse via opena2 (Archivator)
  - Stellt /metrics für opena20 (Dashboard) bereit
```

#### Option 2: Eigenständig - Port 8001 (Aktuell)
```yaml
Service: LocalAgent-Pro (Standalone)
Port: 8001
Rolle: OpenWebUI-kompatibler AI-Agent
Status: Online
Beschreibung: Unabhängiger LLM-Service mit direkter OpenWebUI-Integration
Integration:
  - Prometheus-Metriken für opena20 (Dashboard)
  - Kann von opena3 (OpenWebUI) direkt angesprochen werden
  - Läuft parallel zum ELION-System
```

---

## 🔗 Integration in ELION-Architektur

### 1. Kommunikation mit Koordinator (opena1)

**LocalAgent-Pro → opena1 (Request Flow):**
```python
# LocalAgent empfängt Chat-Request
POST /v1/chat/completions
↓
# Tool-Execution + LLM-Inference
analyze_and_execute(prompt)
↓
# Ergebnis an Koordinator melden (optional)
POST http://localhost:12344/api/task/complete
{
    "task_id": "uuid",
    "result": "...",
    "safepoint": true
}
```

**opena1 → LocalAgent-Pro (Dispatch):**
```python
# Koordinator dispatched AI-Aufgabe
POST http://localhost:8001/v1/chat/completions
{
    "messages": [
        {"role": "system", "content": "Du bist ein Tool-Agent..."},
        {"role": "user", "content": "Erstelle Datei report.txt mit..."}
    ],
    "metadata": {
        "dispatcher": "opena1",
        "task_id": "uuid",
        "archive_to": "opena2"
    }
}
```

### 2. Archivierung über opena2

**Safepoint-Integration:**
```python
# Nach erfolgreicher Tool-Execution
def archive_result_to_opena2(result):
    safepoint = {
        "type": "AI_INFERENCE",
        "agent": "localagent-pro",
        "timestamp": int(time.time()),
        "input": user_prompt,
        "output": result,
        "tools_used": ["write_file", "read_file"],
        "sandbox_path": "/home/danijel-jd/localagent_sandbox"
    }
    
    requests.post(
        "http://localhost:12345/api/safepoint",
        json=safepoint
    )
```

**Deduplizierung:** opena2 prüft, ob identische Requests bereits existieren (via MD5-Hash).

### 3. Dashboard-Integration (opena20)

**Metriken-Export:**
- LocalAgent-Pro stellt bereits `/metrics` bereit
- opena20 kann diese scrapen für:
  - Request Rate
  - Error Rate
  - Ollama Performance
  - Loop Detections
  - Tool Usage

**Dashboard-Queries:**
```promql
# LocalAgent-Pro Performance
rate(localagent_requests_total{job="localagent-pro"}[5m])

# Fehlerrate
rate(localagent_requests_total{status="error"}[5m]) / rate(localagent_requests_total[5m])

# Loop-Protection Aktivierungen
increase(localagent_loop_detections_total[1h])
```

### 4. OpenWebUI-Integration (opena3)

**Direkte Anbindung:**
```
OpenWebUI (opena3:8080)
    ↓
    API Base URL: http://localhost:8001/v1
    ↓
LocalAgent-Pro (Port 8001)
    ↓
    Ollama (llama3.1)
```

**Vorteile:**
- ✅ OpenWebUI kann LocalAgent-Pro als "Custom API" nutzen
- ✅ Alle Tool-Executions laufen über Sandbox
- ✅ Volle OpenAI-Kompatibilität

---

## 🛠️ Implementierungs-Schritte

### Schritt 1: Registry-Eintrag erstellen

**Datei:** `configs/agent_registry.yaml` (im ELION-Projekt)

```yaml
agents:
  # ... bestehende Agenten ...
  
  opena21:
    name: "AI-Inference (LocalAgent-Pro)"
    port: 12364  # ODER 8001 für Standalone
    host: "localhost"
    role: "inference"
    status: "online"
    health_endpoint: "/health"
    metrics_endpoint: "/metrics"
    capabilities:
      - "llm_inference"
      - "tool_execution"
      - "file_operations"
      - "web_fetch"
      - "sandbox_isolation"
    dependencies:
      - "opena1"  # Koordinator
      - "opena2"  # Archivator
    integration:
      protocol: "http"
      api_version: "openai_v1"
      model: "llama3.1"
```

### Schritt 2: Koordinator-Routing konfigurieren

**opena1 Dispatch-Rules:**

```python
# In opena1 (Koordinator)
AGENT_ROUTES = {
    "ai_inference": "http://localhost:8001/v1/chat/completions",
    "tool_execution": "http://localhost:8001/test",
    # ...
}

def dispatch_ai_task(task):
    """Leitet AI-Aufgaben an LocalAgent-Pro"""
    response = requests.post(
        AGENT_ROUTES["ai_inference"],
        json={
            "messages": task["messages"],
            "metadata": {
                "task_id": task["id"],
                "dispatcher": "opena1"
            }
        }
    )
    
    # Ergebnis an Archivator
    if response.ok:
        archive_to_opena2(task["id"], response.json())
    
    return response.json()
```

### Schritt 3: Prometheus-Scraping erweitern

**Bereits erledigt!** LocalAgent-Pro ist bereits in Prometheus konfiguriert:

```yaml
# /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/configs/prometheus.yaml
scrape_configs:
  - job_name: 'localagent-pro'
    metrics_path: '/metrics'
    scrape_interval: 15s
    static_configs:
      - targets: ['172.17.0.1:8001']
        labels:
          service: 'localagent-pro'
          environment: 'production'
```

**opena20 (Dashboard) kann diese Metriken nutzen!**

### Schritt 4: Telegram-Bot Integration (opena4)

**LocalAgent-Pro via Telegram nutzen:**

```python
# In opena4 (Telegram-Bot)
def handle_ai_request(message):
    """Leitet Telegram-Nachricht an LocalAgent-Pro"""
    
    # 1. Schreibe in Archiv (opena2)
    msg_id = archive_message(message)
    
    # 2. Rufe LocalAgent-Pro
    response = requests.post(
        "http://localhost:8001/v1/chat/completions",
        json={
            "messages": [
                {"role": "user", "content": message.text}
            ],
            "metadata": {
                "source": "telegram",
                "chat_id": message.chat.id,
                "msg_id": msg_id
            }
        }
    )
    
    # 3. Archiviere Antwort (opena2)
    archive_response(msg_id, response.json())
    
    # 4. Sende an Telegram zurück
    bot.send_message(message.chat.id, response.json()["choices"][0]["message"]["content"])
```

---

## 📊 Monitoring & Health-Checks

### Dashboard-Integration (opena20)

**LocalAgent-Pro Metriken in ELION-Dashboard:**

```javascript
// opena20 Dashboard-Panel
{
  "title": "AI-Inference Performance",
  "panels": [
    {
      "query": "rate(localagent_requests_total[5m])",
      "title": "LocalAgent Request Rate"
    },
    {
      "query": "localagent_active_requests",
      "title": "Active Requests"
    },
    {
      "query": "rate(localagent_ollama_calls_total{status='success'}[5m])",
      "title": "Ollama Success Rate"
    },
    {
      "query": "localagent_loop_detections_total",
      "title": "Loop Protection (Critical!)"
    }
  ]
}
```

### Health-Check-Routing

**opena20 → LocalAgent-Pro:**
```bash
# Periodischer Health-Check
curl http://localhost:8001/health

# Response:
{
  "status": "ok",
  "model": "llama3.1",
  "sandbox": true,
  "sandbox_path": "/home/danijel-jd/localagent_sandbox"
}
```

**Alert-Regeln:**
```yaml
# In opena20 oder Prometheus
- alert: LocalAgentDown
  expr: up{job="localagent-pro"} == 0
  for: 1m
  annotations:
    summary: "LocalAgent-Pro ist offline!"

- alert: LocalAgentHighErrorRate
  expr: rate(localagent_requests_total{status="error"}[5m]) > 0.1
  for: 5m
  annotations:
    summary: "LocalAgent Error Rate > 10%"
```

---

## 🔐 Security-Integration

### Sandbox-Isolation

**LocalAgent-Pro nutzt bereits Sandbox:**
```yaml
sandbox: true
sandbox_path: /home/danijel-jd/localagent_sandbox
```

**Für ELION-Integration:**
- Alle File-Operationen laufen in Sandbox
- Shell-Commands sind blockiert (sandbox-mode)
- Nur whitelisted Domains erlaubt

### Unlock-Master Integration (opena11)

**Verschlüsselte Secrets via opena11:**
```python
# LocalAgent-Pro ruft opena11 für Credentials
def get_api_key(service):
    response = requests.post(
        "http://localhost:12354/api/unlock",
        json={"service": service, "requester": "localagent-pro"}
    )
    return response.json()["key"]

# Nutzung in LocalAgent
api_key = get_api_key("openai")  # Falls externe APIs genutzt werden
```

---

## 🚀 Deployment-Szenarien

### Szenario 1: Standalone (Aktuell)

```
LocalAgent-Pro (Port 8001)
    ├── Prometheus Monitoring ✅
    ├── OpenWebUI Integration ✅
    └── Läuft parallel zu ELION

ELION-System (Ports 12344-12363)
    ├── opena1 (Koordinator)
    ├── opena2 (Archivator)
    ├── opena3 (OpenWebUI)
    ├── opena4 (Telegram)
    └── opena20 (Dashboard) → scraped LocalAgent Metrics
```

**Vorteile:**
- ✅ Unabhängige Skalierung
- ✅ Keine Abhängigkeiten zu ELION
- ✅ Einfache Wartung

### Szenario 2: Full Integration (opena21)

```
ELION-System
    ├── opena1 (Koordinator) → dispatched an opena21
    ├── opena2 (Archivator) → empfängt Safepoints von opena21
    ├── opena21 (LocalAgent-Pro auf 12364)
    │       ├── Ollama Integration
    │       ├── Tool Execution
    │       └── Sandbox Isolation
    ├── opena3 (OpenWebUI) → nutzt opena21 via Koordinator
    ├── opena4 (Telegram) → leitet AI-Requests an opena21
    └── opena20 (Dashboard) → monitored opena21 Metriken
```

**Vorteile:**
- ✅ Zentrale Orchestrierung via opena1
- ✅ Alle Aktionen protokolliert in opena2
- ✅ Einheitliches Routing
- ✅ Vollständige ELION-Integration

### Szenario 3: Hybrid

LocalAgent-Pro läuft auf Port 8001, aber:
- opena1 kann bei Bedarf AI-Tasks dorthin routen
- opena4 (Telegram) nutzt LocalAgent für Chat
- opena20 scraped Metriken
- Safepoints werden optional an opena2 gesendet

---

## 📝 Beispiel-Workflows

### Workflow 1: Telegram → AI → Archiv

```
1. User sendet Telegram-Nachricht
   ↓
2. opena4 empfängt → schreibt in opena2
   ↓
3. opena4 ruft LocalAgent-Pro (POST /v1/chat/completions)
   ↓
4. LocalAgent führt Tools aus (Sandbox)
   ↓
5. LocalAgent sendet Antwort zurück
   ↓
6. opena4 archiviert Antwort in opena2
   ↓
7. opena4 sendet Telegram-Reply
```

### Workflow 2: OpenWebUI → Direct

```
1. User chattet in OpenWebUI (opena3)
   ↓
2. OpenWebUI → http://localhost:8001/v1/chat/completions
   ↓
3. LocalAgent-Pro verarbeitet
   ↓
4. Antwort direkt an OpenWebUI
   
(Optional: LocalAgent sendet Safepoint an opena2)
```

### Workflow 3: Koordinator-Dispatch

```
1. opena1 erhält komplexen Auftrag
   ↓
2. opena1 erkennt: "Braucht AI-Inference"
   ↓
3. opena1 → POST http://localhost:8001/v1/chat/completions
   ↓
4. LocalAgent führt aus + sendet Ergebnis
   ↓
5. opena1 → schreibt Safepoint in opena2
   ↓
6. opena1 orchestriert weitere Schritte
```

---

## 🎯 Empfehlung

**Für dein Setup:**

1. **Behalte Port 8001** (Standalone) → Einfachste Integration
2. **Erweitere opena20** → Scraped bereits LocalAgent-Metriken ✅
3. **Optional: opena4 Integration** → Telegram-Bot nutzt LocalAgent für AI
4. **Später: Als opena21 registrieren** → Für vollständige ELION-Integration

**Nächste Schritte:**
1. ✅ Prometheus-Integration läuft bereits
2. 📊 Grafana-Dashboard für LocalAgent erstellen
3. 🤖 opena4 (Telegram) mit LocalAgent verbinden
4. 📋 Safepoint-Integration in opena2 implementieren

**Dein System ist bereits production-ready mit vollem Monitoring!** 🚀
