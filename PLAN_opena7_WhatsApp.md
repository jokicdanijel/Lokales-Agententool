# PLAN: Agent opena7 – WhatsApp Chatbot
**Status:** Production-Ready Plan | **Port:** 12348 | **Modul:** 7.chatbot_schrift_opena7

## 📋 Zielsetzung
WhatsApp-Chatbot mit Webhook-Handler, Patch-Benachrichtigungen und Threading.

## 🔗 Eingaben & Abhängigkeiten
- WhatsApp-API-Tokens
- Webhook-URLs
- Patch-Blöcke
- Audit-Logs

## 🏗️ Architektur
```
2.openwebui/
├── openwebui_opena7.py
├── webhook_handler_opena7.py
├── patch_delivery_opena7.py
└── tests/test_opena7.py
```

## Endpunkte
- `GET /opena7/health`
- `POST /opena7/webhook` – WhatsApp-Webhook-Handler
- `POST /opena7/send-message` – Nachricht senden
- `GET /opena7/audit`

## ⚙️ Umsetzung
- [ ] Erstelle `openwebui_opena7.py`
- [ ] Webhook-Verarbeitung
- [ ] Message-Routing zu Finance/Archive
- [ ] Patch-Delivery-Integration
- [ ] Tests (9/9)
- [ ] Archivator-Integration

## 📦 Release
- `PLAN_opena7_WhatsApp.md`
- `2.openwebui/openwebui_opena7.py`
- `tests/test_opena7.py`

**Plan erstellt:** 2025-11-08 | **Version:** 1.0
