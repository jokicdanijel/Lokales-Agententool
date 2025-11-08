# PLAN: Agent opena9 – Telefon-Anruf Chatbot
**Status:** Production-Ready Plan | **Port:** 12348 | **Modul:** 8.chatbot_ton_opena9

## 📋 Zielsetzung
Erweiterte Telefon-Integration mit Anruf-Flow, Callback-Handling, IVR-Menu und Patch-Delivery.

## 🔗 Eingaben & Abhängigkeiten
- Call-Trigger-Events
- Callback-URLs
- Patch-Blöcke
- STT/TTS-Service (von opena8)

## 🏗️ Architektur
```
2.openwebui/
├── openwebui_opena9.py
├── call_handler_opena9.py
├── patch_log_opena9.py
└── tests/test_opena9.py
```

## Endpunkte
- `GET /opena9/health`
- `POST /opena9/initiate-call` – Anruf starten
- `POST /opena9/callback-handler` – Callback-Handling
- `GET /opena9/audit`

## ⚙️ Umsetzung
- [ ] Erstelle `openwebui_opena9.py`
- [ ] Call-Handler-Logik
- [ ] Callback-URL-Verarbeitung
- [ ] Patch-Delivery-Integration
- [ ] Tests (9/9)

## 📦 Release
- `PLAN_opena9_TelephoneCall.md`
- `2.openwebui/openwebui_opena9.py`
- `tests/test_opena9.py`

**Plan erstellt:** 2025-11-08 | **Version:** 1.0
