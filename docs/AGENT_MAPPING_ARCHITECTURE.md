# Agent-Mapping-Architektur – Vollständige 20-Agent-Topologie

**Status:** Finalisiert für Schritt 2 + 3 Integration
**Version:** 1.0.0
**Datum:** 2025-11-10
**Scope:** opena1 bis opena20 (Kordinator → Dashboard)

---

## 1. Port-Policy & Binding

| Eigenschaft       | Wert                        |
| ----------------- | --------------------------- |
| **Allowed Range** | 12344–12369 (26 Ports)      |
| **Forbidden**     | 8080 (exclusive für opena3) |
| **Binding**       | 127.0.0.1 (loopback only)   |
| **Protocol**      | HTTP/REST                   |
| **Services**      | 20 Agents (opena1–opena20)  |

---

## 2. Vollständiges Agent-Registry

### 2.1 Kordinator & Archivator (Infrastruktur)

| Agent      | Port  | Archiv-Kürzel | Funktion                         | Endpoint-Basis   |
| ---------- | ----- | ------------- | -------------------------------- | ---------------- |
| **opena1** | 12344 | `kordp`       | Portier-Koordinator (Routing)    | `/api/kordp`     |
| **opena2** | 12345 | `archivp`     | Archivator (Append-Only Storage) | `/store/archivp` |

### 2.2 Kommunikations-Agenten

| Agent      | Port   | Archiv-Kürzel | Funktion                       | Endpoint-Basis    |
| ---------- | ------ | ------------- | ------------------------------ | ----------------- |
| **opena3** | 8080\* | `openweb`     | OpenWebUI Terminal Interface   | `/api/openweb`    |
| **opena4** | 12347  | `telep`       | Telegram Mobile-Anbindung      | `/telegram/send`  |
| **opena5** | 12346  | `vscop`       | VS Code Programmier-Bridge     | `/vscode/task`    |
| **opena6** | 12349  | `browsp`      | Browser-Bedienung (Automation) | `/browser/action` |

\*Port 8080 ist exklusiv reserviert (Docker/OpenWebUI)

### 2.3 Chatbot-Agenten (Schrift)

| Agent      | Port  | Archiv-Kürzel | Funktion                   | Endpoint-Basis   |
| ---------- | ----- | ------------- | -------------------------- | ---------------- |
| **opena7** | 12350 | `emailp`      | Email-Chatbot (Schrift)    | `/chat/email`    |
| **opena8** | 12351 | `whatp`       | WhatsApp-Chatbot (Schrift) | `/chat/whatsapp` |

### 2.4 Chatbot-Agenten (Ton)

| Agent       | Port  | Archiv-Kürzel | Funktion                      | Endpoint-Basis   |
| ----------- | ----- | ------------- | ----------------------------- | ---------------- |
| **opena9**  | 12352 | `calp`        | Telefon-Antwort Chatbot (IVR) | `/call/answer`   |
| **opena10** | 12353 | `answp`       | Telefon-Anruf Chatbot         | `/call/initiate` |

### 2.5 Funktional-Agenten

| Agent       | Port  | Archiv-Kürzel | Funktion                    | Endpoint-Basis       |
| ----------- | ----- | ------------- | --------------------------- | -------------------- |
| **opena11** | 12354 | `onlockp`     | Unlock-Master (Decode)      | `/security/unlock`   |
| **opena12** | 12355 | `somep`       | Sozialmedia-Automatisierung | `/social/sync`       |
| **opena13** | 12356 | `infmep`      | Influencer-Manager          | `/influencer/manage` |
| **opena14** | 12357 | `kalp`        | Kalender-Agent              | `/calendar/sync`     |

### 2.6 Content-Creator-Agenten

| Agent       | Port  | Archiv-Kürzel | Funktion                   | Endpoint-Basis      |
| ----------- | ----- | ------------- | -------------------------- | ------------------- |
| **opena15** | 12358 | `htmlp`       | HTML-Creator Tool          | `/content/html`     |
| **opena16** | 12359 | `shopp`       | Shop-Creator & Service     | `/content/shop`     |
| **opena17** | 12360 | `homep`       | Homepage-Creator & Service | `/content/homepage` |

### 2.7 Datenverwaltungs-Agenten

| Agent       | Port  | Archiv-Kürzel | Funktion                      | Endpoint-Basis     |
| ----------- | ----- | ------------- | ----------------------------- | ------------------ |
| **opena18** | 12361 | `locp`        | Lokaler Archiv-Agent          | `/archive/local`   |
| **opena19** | 12362 | `aktienp`     | Trading-Agent (Aktien/Crypto) | `/trading/execute` |
| **opena20** | 12363 | `dashp`       | Dashboard-Agent (Kunden)      | `/dashboard/serve` |

---

## 3. Datenfluss-Architektur

### 3.1 OpenAI API Key → Program-Befehl (Eingang)

```
Localhost (Port 12344-12363)
    ↓
opena1 (Kordinator)
    ↓
opena2 (Archivator) ← Speicher der Anfrage
    ↓
opena[N] (Ziel-Agent)
```

**Beispiel: Telegram-Nachricht (opena4)**

```
http://127.0.0.1:12347/telegram/send
    ↓ [JSON mit API-Key + Payload]
opena1 validates & routes
    ↓
opena2 stores request as Safepoint
    ↓
opena4 processes message
```

### 3.2 Program → OpenAI API Key (Ausgang)

```
opena[N] (Ziel-Agent)
    ↓
opena2 (Archivator) ← Response speichern
    ↓
opena1 (Kordinator) ← Validierung
    ↓
Localhost (Rückgabe an Client)
```

**Beispiel: HTML-Generation (opena15)**

```
http://127.0.0.1:12358/content/html [POST]
    ↓ [Validate schema]
opena1 validates
    ↓
opena2 stores request
    ↓
opena15 generates HTML
    ↓
opena2 stores response
    ↓
http://127.0.0.1:12358/content/html [Response 200]
```

---

## 4. Routing-Tabelle (Tool-Registry Integration)

Alle 20 Agenten sind als **Tools** im `tool_registry.py` registriert:

```python
# tool_registry.py
AGENT_ROUTES = {
    "kordp": {"port": 12344, "agent_id": "opena1", "type": "infrastructure"},
    "archivp": {"port": 12345, "agent_id": "opena2", "type": "infrastructure"},
    "openweb": {"port": 8080, "agent_id": "opena3", "type": "communication"},
    "telep": {"port": 12347, "agent_id": "opena4", "type": "communication"},
    # ... (alle 20)
    "dashp": {"port": 12363, "agent_id": "opena20", "type": "dashboard"},
}

# dispatcher routes based on tool_name
tool_dispatcher.dispatch(tool_name="telep", payload={...})
    → routes to port 12347 (opena4)
```

---

## 5. Safepoint-Struktur (Schritt 3 Integration)

Jeder Agent speichert Requests/Responses als Safepoint in opena2:

```json
{
  "sp_id": "SP1731227400_opena4→opena2_REQUEST.json",
  "timestamp": "2025-11-10T12:30:00Z",
  "source": "opena4",
  "destination": "opena2",
  "kind": "REQUEST",
  "payload": {
    "strict": true,
    "tool_name": "telep",
    "command": "send_message",
    "user_id": "user_123",
    "text": "Hello from Telegram"
  },
  "hash": "sha256:abcd...1234",
  "dedupe_count": 1
}
```

**Speicherort:** `archivp/2025/11/10/index.jsonl`

---

## 6. Port-Policy Enforcement

Alle Services müssen bei Startup validieren:

```python
# config.py (alle Services)
ALLOWED_PORT_RANGE = (12344, 12369)
FORBIDDEN_PORTS = [8080]

def validate_port(port: int):
    if port in FORBIDDEN_PORTS:
        logger.error(f"❌ Port {port} forbidden by policy")
        sys.exit(1)

    if not (ALLOWED_PORT_RANGE[0] <= port <= ALLOWED_PORT_RANGE[1]):
        logger.warning(f"⚠️  Port {port} outside recommended range")

    return True
```

---

## 7. Integration mit Schritt 2 (Tool-Registry)

### 7.1 Tool-Discovery

```python
# tool_registry.py
def get_agent_by_tool(tool_name: str) -> AgentSchema:
    """Resolve tool_name → Agent port/endpoint"""
    if tool_name == "telep":
        return AgentSchema(
            agent_id="opena4",
            port=12347,
            endpoint="/telegram/send",
            type="communication"
        )
```

### 7.2 Dispatch-Routing

```python
# tool_dispatcher.py
async def dispatch(tool_name: str, payload: dict) -> dict:
    agent = registry.get_agent_by_tool(tool_name)
    safepoint = await manager.create_safepoint(
        source="coordinator",
        destination=agent.agent_id,
        kind="REQUEST",
        payload=payload
    )

    response = await forward_to_agent(
        f"http://127.0.0.1:{agent.port}{agent.endpoint}",
        payload
    )

    await manager.write_safepoint(safepoint)
    return response
```

---

## 8. Initiales Setup für alle 20 Services

### 8.1 Verzeichnisstruktur

```
1.opena1&2_portier/          (opena1 - Koordinator)
   ├── main_production.py
   ├── koordinator.py
   ├── tool_registry.py    ← Alle 20 Agenten registriert
   ├── tool_dispatcher.py  ← Routing-Engine
   └── dedupe_engine.py    ← Schritt 3

2.openwebui/               (opena3)
3.opena1_coordinator/      (deprecated)
4.opena4_telegram/         (opena4)
5.kordp_scheduler/         (opena5? - VS Code Bridge)
6.opena4_telegram/         (duplicate name?)
7.opena5_browser/          (opena6?)
...
20.opena18_dashboard/      (opena20?)
```

### 8.2 Port-Zuordnung (Recommended)

```bash
# .env oder config/ports.yaml
OPENA1_PORT=12344   # Koordinator
OPENA2_PORT=12345   # Archivator
OPENA3_PORT=8080    # OpenWebUI (exclusive)
OPENA4_PORT=12347   # Telegram
OPENA5_PORT=12346   # VS Code
OPENA6_PORT=12349   # Browser
OPENA7_PORT=12350   # Email Chatbot
OPENA8_PORT=12351   # WhatsApp
OPENA9_PORT=12352   # Call Answer
OPENA10_PORT=12353  # Call Initiate
...
OPENA20_PORT=12363  # Dashboard
```

---

## 9. Integrations-Checkliste (Nächste Schritte)

- [ ] **Schritt 2 Commit:** ✅ Already in `c5221f9` + `348cf3f`
- [ ] **Schritt 3 Dedupe:** ✅ Already in `348cf3f`
- [ ] **Agent-Registry YAML:** config/agent_registry.yaml (20 services)
- [ ] **Port-Policy Config:** Aktualisieren auf Range [12344-12369]
- [ ] **Tool-Dispatcher:** Integrieren mit allen 20 Agenten
- [ ] **Schritt 4 Test:** Integration-Test für alle Routing-Pfade
- [ ] **Documentation:** Runbook für Agenten-Deployment

---

## 10. Quick-Reference: API-Endpoints

### Health-Checks (alle Agenten)

```bash
curl http://127.0.0.1:{PORT}/health
```

### Tool-Dispatch (via Kordinator)

```bash
# Beispiel: Telegram-Nachricht
curl -X POST http://127.0.0.1:12344/api/dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "telep",
    "command": "send_message",
    "user_id": "123",
    "text": "Hello"
  }'
```

### Archiv-Query (opena2)

```bash
curl http://127.0.0.1:12345/archiv/last?n=5
```

---

## 11. Abhängigkeiten & Integration

**Schritt 1:** ✅ 7.1 Validation (koordinator.py)
**Schritt 2:** ✅ Tool-Registry & Dispatcher
**Schritt 3:** ✅ Safepoint Dedupe & Integrity
**Schritt 4:** 🟡 Vollständige Agent-Integration (20 Services)
**Schritt 5:** 🔴 VS Code Bridge Implementation

---

**Dokumentation:** Danijel – ELION Gesamtprojekt
**Letztes Update:** 2025-11-10T12:30:00Z
