# 🤖 PORTIER 3.0 - Complete Agent Registry

**Version:** 3.0
**Datum:** 28. November 2025
**Status:** ✅ **PRODUCTION-READY**
**Maintainer:** Danijel Jokic

---

## 📋 **Agent Overview**

### **Total Agents:** 20 (opena1–opena20)

### **Port Range:** 12344–12399 (Backend) + localhost:3000 (OpenWebUI)

### **Architecture:** Option-2-Flow (all routes via `kordp → archivp`)

---

## 🔌 **Agent Registry Table**

| #      | Category        | Agent Name          | Port/URL       | Port Identifier | OpenAI Key  | Description            |
| ------ | --------------- | ------------------- | -------------- | --------------- | ----------- | ---------------------- |
| **0**  | **Core**        | **Koordinator**     | **12344**      | **kordp**       | **opena1**  | Request Coordinator    |
| **1**  | **Core**        | **Archivator**      | **12345**      | **archivp**     | **opena2**  | Safepoint Storage      |
| **2**  | Integration     | OpenWebUI Terminal  | localhost:3000 | openweb         | opena3      | Terminal UI Agent      |
| **3**  | Communication   | Telegram Mobile     | 12344-12399    | telep           | opena4      | Telegram Integration   |
| **4**  | Development     | VSCode Programming  | 12344-12399    | vscop           | opena5      | IDE Automation         |
| **5**  | Automation      | Browser Control     | 12344-12399    | browsp          | opena6      | Web Automation         |
| **6**  | Chatbot (Text)  | Email Chatbot       | 12344-12399    | emailp          | opena7      | Email Agent            |
| **7**  | Chatbot (Text)  | WhatsApp Chatbot    | 12344-12399    | whatp           | opena8      | WhatsApp Agent         |
| **8**  | Chatbot (Voice) | Phone Answer Bot    | 12344-12399    | calp            | opena9      | Inbound Calls          |
| **9**  | Chatbot (Voice) | Phone Call Bot      | 12344-12399    | answp           | opena10     | Outbound Calls         |
| **10** | Security        | Unlock Master       | 12344-12399    | onlockp         | opena11     | Decode Agent           |
| **11** | Social Media    | Social Automation   | 12344-12399    | somep           | opena12     | Social Media Agent     |
| **12** | Social Media    | Influencer Agent    | 12344-12399    | infmep          | opena13     | Influencer Tools       |
| **13** | Productivity    | Calendar Agent      | 12344-12399    | kalp            | opena14     | Scheduling Agent       |
| **14** | Content         | HTML Creator        | 12344-12399    | htmlp           | opena15     | HTML Generator         |
| **15** | E-Commerce      | Shop Creator        | 12344-12399    | shopp           | opena16     | Shop Builder           |
| **16** | Content         | Homepage Creator    | 12344-12399    | homep           | opena17     | Homepage Builder       |
| **17** | Storage         | Local Archive Agent | 12344-12399    | locp            | opena18     | Local Storage          |
| **18** | Finance         | Aktien & Crypto     | 12344-12399    | aktienp         | opena19     | Trading Agent          |
| **19** | **Dashboard**   | **Dashboard Agent** | **12349**      | **dashp**       | **opena20** | **Customer Dashboard** |

---

## 🔄 **Option-2-Flow Architecture**

### **CMD Flow (OpenAI → Tool)**

```
OpenAI Request
    ↓
opena{N} (Agent receives request)
    ↓
kordp (Gateway coordination)
    ↓
archivp (Safepoint CMD logging)
    ↓
{tool}p (Tool execution: telep, vscop, browsp, etc.)
```

**All agents follow:**

```
http:12344-12399 / opena{N} / kordp / archivp / {tool}p
```

**Special case (opena3 - OpenWebUI):**

```
localhost:3000 / opena3 / kordp / archivp / openweb
```

### **RESP Flow (Tool → OpenAI)**

```
{tool}p (Tool execution complete)
    ↓
archivp (Safepoint RESP logging)
    ↓
opena{N} (Agent sends response)
    ↓
OpenAI Response
```

**All agents follow:**

```
{tool}p / archivp / opena{N}
```

---

## 📊 **Agent Categories**

### **1. Core Infrastructure (2 agents)**

- **opena1 (kordp):** Koordinator - Central request routing
- **opena2 (archivp):** Archivator - Safepoint persistence (append-only)

### **2. Integration (1 agent)**

- **opena3 (openweb):** OpenWebUI Terminal - localhost:3000

### **3. Communication (1 agent)**

- **opena4 (telep):** Telegram Mobile Integration

### **4. Development (1 agent)**

- **opena5 (vscop):** VSCode Programming Automation

### **5. Automation (1 agent)**

- **opena6 (browsp):** Browser Control & Web Automation

### **6. Chatbots - Text (2 agents)**

- **opena7 (emailp):** Email Chatbot
- **opena8 (whatp):** WhatsApp Chatbot

### **7. Chatbots - Voice (2 agents)**

- **opena9 (calp):** Phone Answer Bot (Inbound)
- **opena10 (answp):** Phone Call Bot (Outbound)

### **8. Security (1 agent)**

- **opena11 (onlockp):** Unlock Master - Decode Agent

### **9. Social Media (2 agents)**

- **opena12 (somep):** Social Media Automation
- **opena13 (infmep):** Influencer Agent

### **10. Productivity (1 agent)**

- **opena14 (kalp):** Calendar Agent

### **11. Content Creation (2 agents)**

- **opena15 (htmlp):** HTML Creator
- **opena17 (homep):** Homepage Creator

### **12. E-Commerce (1 agent)**

- **opena16 (shopp):** Shop Creator & Service Tool

### **13. Storage (1 agent)**

- **opena18 (locp):** Local Archive Agent

### **14. Finance (1 agent)**

- **opena19 (aktienp):** Aktien & Crypto Trading Agent

### **15. Dashboard (1 agent)**

- **opena20 (dashp):** Customer Dashboard (Port 12349)

---

## 🔐 **OpenAI API Key Mapping**

### **Environment Variables (.env)**

```bash
# Core Infrastructure
OPENAI_API_KEY_OPENA1=sk-proj-...  # Koordinator
OPENAI_API_KEY_OPENA2=sk-proj-...  # Archivator

# Integration
OPENAI_API_KEY_OPENA3=sk-proj-...  # OpenWebUI

# Communication
OPENAI_API_KEY_OPENA4=sk-proj-...  # Telegram

# Development
OPENAI_API_KEY_OPENA5=sk-proj-...  # VSCode

# Automation
OPENAI_API_KEY_OPENA6=sk-proj-...  # Browser

# Chatbots - Text
OPENAI_API_KEY_OPENA7=sk-proj-...  # Email
OPENAI_API_KEY_OPENA8=sk-proj-...  # WhatsApp

# Chatbots - Voice
OPENAI_API_KEY_OPENA9=sk-proj-...   # Phone Answer
OPENAI_API_KEY_OPENA10=sk-proj-...  # Phone Call

# Security
OPENAI_API_KEY_OPENA11=sk-proj-...  # Unlock Master

# Social Media
OPENAI_API_KEY_OPENA12=sk-proj-...  # Social Automation
OPENAI_API_KEY_OPENA13=sk-proj-...  # Influencer

# Productivity
OPENAI_API_KEY_OPENA14=sk-proj-...  # Calendar

# Content Creation
OPENAI_API_KEY_OPENA15=sk-proj-...  # HTML Creator
OPENAI_API_KEY_OPENA17=sk-proj-...  # Homepage Creator

# E-Commerce
OPENAI_API_KEY_OPENA16=sk-proj-...  # Shop Creator

# Storage
OPENAI_API_KEY_OPENA18=sk-proj-...  # Local Archive

# Finance
OPENAI_API_KEY_OPENA19=sk-proj-...  # Trading Agent

# Dashboard
OPENAI_API_KEY_OPENA20=sk-proj-...  # Dashboard Agent
```

---

## 🛠️ **Port Assignments**

### **Fixed Ports (Core Infrastructure)**

```
opena1 (kordp):    12344
opena2 (archivp):  12345
kordp (Gateway):   12346
opena20 (dashp):   12349
```

### **Dynamic Port Range (Agents 3-19)**

```
12344-12399 (Backend Services)
```

### **External UI**

```
opena3 (OpenWebUI): localhost:3000
```

**Port 8080:** Reserved for OpenWebUI UI ONLY (no backend services)

---

## 📝 **Safepoint Structure**

### **CMD Safepoint (Request)**

```json
{
  "timestamp": "2025-11-28T12:00:00Z",
  "src": "opena{N}",
  "dst": "kordp",
  "kind": "CMD",
  "tool": "{tool}p",
  "request_id": "REQ-{timestamp}",
  "payload": {
    "message": "User request content"
  }
}
```

**Filename:** `SP{timestamp}_opena{N}→kordp_CMD.json`

### **RESP Safepoint (Response)**

```json
{
  "timestamp": "2025-11-28T12:00:05Z",
  "src": "{tool}p",
  "dst": "archivp",
  "kind": "RESP",
  "request_id": "REQ-{timestamp}",
  "response": {
    "status": "success",
    "data": "Tool execution result"
  }
}
```

**Filename:** `SP{timestamp}_{tool}p→archivp_RESP.json`

**Critical:** Unicode arrow `→` (U+2192) is MANDATORY

---

## 🔒 **Architecture Rules (ENFORCED)**

### **Option-2-Flow (MANDATORY)**

1. All requests MUST go through: `opena{N} → kordp → archivp → {tool}p`
2. All responses MUST return via: `{tool}p → archivp → opena{N}`
3. **FORBIDDEN:** Direct calls (OpenAI → {tool}p) bypassing kordp/archivp

### **Port Policy (STRICT)**

1. Backend services: **12344-12399 ONLY**
2. Port **8080**: UI ONLY (never backend)
3. Special: localhost:3000 for OpenWebUI (opena3)

### **Safepoint Integrity (CRITICAL)**

1. **Append-only:** Never delete/modify safepoints
2. **Unicode arrow:** `→` (U+2192) in filenames
3. **Storage:** `archivp/ARCHIV/YYYY/MM/DD/`
4. **Indexing:** `archivp/index.jsonl`

---

## 🚀 **Agent Startup Commands**

### **Core Infrastructure**

```bash
# opena1 (Koordinator)
bin/start_opena1_with_key.sh

# opena2 (Archivator)
bin/start_opena2_with_key.sh
```

### **Dashboard**

```bash
# opena20 (Dashboard)
bin/start_dashboard.sh
```

### **Full Stack**

```bash
# Start all services
bin/ops.sh start

# Start specific agent (example)
bin/start_opena4.sh  # Telegram
```

---

## 🧪 **Testing & Validation**

### **E2E Option-2-Flow Test**

```bash
bin/ops.sh e2e
```

**Expected Flow:**

```
✅ opena1 health OK
✅ opena2 health OK (190+ entries)
✅ Request routed: opena1 → kordp → archivp
✅ Safepoint created: SP{ts}_kordp→archivp_LOG.json
```

### **Agent Health Checks**

```bash
# Check all agents
bin/ops.sh status

# Check specific agent
curl -sf http://127.0.0.1:12344/health | jq .  # opena1
curl -sf http://127.0.0.1:12345/health | jq .  # opena2
curl -sf http://127.0.0.1:12349/health | jq .  # opena20
```

---

## 📚 **Related Documentation**

- **Architecture:** `.github/copilot-master-prompt.md`
- **Operations:** `OPERATIONS_COMPLETE.md`
- **Security:** `SECURITY_INCIDENT_2025-11-28.md`
- **Dashboard AI:** `.github/DASHBOARD_AI_CONFIG.md`

---

## 🔄 **Change Log**

### **28. Nov 2025**

- ✅ Complete agent registry documented (opena1-opena20)
- ✅ Option-2-Flow mapping for all agents
- ✅ Port assignments clarified
- ✅ OpenAI API Key mapping defined
- ✅ Safepoint structure standardized

---

**Maintainer:** Danijel Jokic
**Last Updated:** 28. November 2025
**Review Cycle:** Bei Major Agent Changes
