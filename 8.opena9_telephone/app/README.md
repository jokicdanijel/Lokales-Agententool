# 📞 OPENA9 Telephone Agent

## PORTIER PAS-6.0 Standard

[![Version](https://img.shields.io/badge/version-6.0.0-blue.svg)](https://github.com/elion)
[![Python](https://img.shields.io/badge/python-3.12+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

---

## 🎯 Übersicht

Der **OPENA9 Telephone Agent** ist ein vollständiger Telefonie-Agent nach dem **PORTIER PAS-6.0 Standard**. Er bietet:

- 📞 **Anrufverwaltung** - Ausgehende/eingehende Anrufe über Twilio/SIP
- 🎙️ **AI Voice Generation** - Text-to-Speech via OpenAI TTS
- 🔊 **Speech-to-Text** - Transkription via OpenAI Whisper
- 📊 **IVR Flows** - AI-generierte Sprachmenüs
- 📈 **Echtzeit-Metriken** - Prometheus-kompatibel

---

## 🚀 Quick Start

### 1. Umgebung konfigurieren

```bash
# Template kopieren und anpassen
cp .env.template .env

# Wichtige Variablen setzen:
# - OPENAI_API_KEY_OPENA9
# - TWILIO_ACCOUNT_SID
# - TWILIO_AUTH_TOKEN
# - TWILIO_PHONE_NUMBER
```

### 2. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 3. Agent starten

```bash
# Via Script
./bin/start_telephone_agent.sh

# Oder direkt
uvicorn main:app --host 0.0.0.0 --port 12355
```

### 4. Dashboard öffnen

```
http://127.0.0.1:12355/html/index.html
```

---

## 📁 Projektstruktur

```
9.opena9_telephone/
├── main.py                 # FastAPI Application
├── modules/
│   ├── __init__.py
│   ├── telephony_core.py   # Zentrale Steuerung
│   ├── telephony_api.py    # Twilio/SIP Integration
│   ├── ai_voice_engine.py  # OpenAI TTS/Voice
│   ├── speech_to_text.py   # OpenAI Whisper
│   └── metrics.py          # Performance Tracking
├── html/
│   ├── index.html          # Dashboard UI
│   ├── style.css           # Styles
│   ├── config.js           # Frontend Config
│   └── app.js              # Frontend Logic
├── bin/
│   ├── start_telephone_agent.sh
│   └── stop_telephone_agent.sh
├── tests/
│   └── test_telephone_agent.py
├── requirements.txt
├── Dockerfile
├── .env.template
└── README.md
```

---

## 🔌 API Endpoints

### Health & Status

| Endpoint   | Methode | Beschreibung         |
| ---------- | ------- | -------------------- |
| `/health`  | GET     | Health Check         |
| `/status`  | GET     | Detaillierter Status |
| `/metrics` | GET     | Prometheus Metriken  |
| `/config`  | GET     | Konfiguration        |

### Commands

| Endpoint   | Methode | Beschreibung      |
| ---------- | ------- | ----------------- |
| `/command` | POST    | Befehle ausführen |

**Verfügbare Commands:**

- `make_call` - Anruf starten
- `answer_call` - Anruf annehmen
- `hangup` - Auflegen
- `transfer_call` - Weiterleiten
- `hold_call` - Halten
- `get_call_status` - Status abfragen
- `list_active_calls` - Aktive Anrufe

### Specialized Endpoints

| Endpoint                      | Methode | Beschreibung         |
| ----------------------------- | ------- | -------------------- |
| `/specialized/make_call`      | POST    | Anruf starten        |
| `/specialized/voice_generate` | POST    | Voice generieren     |
| `/specialized/transcribe`     | POST    | Audio transkribieren |
| `/specialized/ivr_flow`       | POST    | IVR Flow erstellen   |

---

## 🔧 Konfiguration

### Umgebungsvariablen

| Variable                | Beschreibung   | Default |
| ----------------------- | -------------- | ------- |
| `OPENA9_PORT`           | Agent Port     | 12355   |
| `OPENAI_API_KEY_OPENA9` | OpenAI API Key | -       |
| `TWILIO_ACCOUNT_SID`    | Twilio Account | -       |
| `TWILIO_AUTH_TOKEN`     | Twilio Token   | -       |
| `TWILIO_PHONE_NUMBER`   | Caller ID      | -       |

---

## 📊 Beispiele

### Anruf starten

```bash
curl -X POST http://127.0.0.1:12355/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "make_call",
    "params": {
      "to": "+491234567890",
      "from_number": "+490987654321",
      "voice_message": "Hallo, dies ist ein Testanruf."
    }
  }'
```

### Voice generieren

```bash
curl -X POST http://127.0.0.1:12355/specialized/voice_generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Willkommen bei unserem Service.",
    "voice": "nova",
    "speed": 1.0
  }'
```

### Metriken abrufen

```bash
curl http://127.0.0.1:12355/metrics
```

---

## 🐳 Docker

```bash
# Build
docker build -t opena9-telephone:6.0.0 .

# Run
docker run -d \
  --name opena9-telephone \
  -p 12355:12355 \
  -e OPENAI_API_KEY_OPENA9=sk-xxx \
  -e TWILIO_ACCOUNT_SID=ACxxx \
  -e TWILIO_AUTH_TOKEN=xxx \
  opena9-telephone:6.0.0
```

---

## 🧪 Tests

```bash
# Alle Tests
pytest tests/ -v

# Mit Coverage
pytest tests/ --cov=modules --cov-report=html
```

---

## 📜 Changelog

### v6.0.0 (2025-01)

- ✅ PORTIER PAS-6.0 Standard implementiert
- ✅ OpenAI TTS/Whisper Integration
- ✅ Twilio Voice API
- ✅ HTML Dashboard 6.0
- ✅ Prometheus Metriken
- ✅ Vollständige Test-Suite

---

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE)

---

**ELION Team** | **PORTIER PAS-6.0** | **Port 12355**
