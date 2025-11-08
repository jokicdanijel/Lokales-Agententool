# PLAN: Agent opena5 – Browser Integration
**Status:** Production-Ready Plan | **Port:** 12348 | **Modul:** 4.browser_opena5

---

## 📋 Zielsetzung (Stufe 1)

Errichte einen **Browser-Automation-Agenten**, der:
- UI-Templates generiert und bereitstellt
- Patch-Delivery-Logik verwaltet
- Audit-Tracking für OpenWebUI-Änderungen
- Cross-Platform-Browser-Support

**Akzeptanzkriterium:** Health-Endpunkt antwortet, Patch-Delivery-Path simuliert testbar, Audit-Logs vorhanden.

---

## 🔗 Eingaben & Abhängigkeiten (Stufe 2)

### Eingaben
- UI-Anforderungen (JSON Schema 7.1)
- Patch-Blöcke (Unified Diff)
- Patch-Templates aus Registry
- Audit-Trigger-Events

### Abhängigkeiten
- ✅ Koordinator (opena1)
- ✅ Archivator (opena2) – Audit
- ✅ OpenWebUI-Server aktiv
- ✅ Patch-Delivery-System

---

## 🏗️ Architektur & Interfaces (Stufe 3)

### Module
```
2.openwebui/
├── openwebui_opena5.py
├── ui_template_provider.py
├── patch_delivery_opena5.py
└── tests/test_opena5.py
```

### Endpunkte
- `GET /opena5/health` – Status
- `GET /opena5/info` – Service-Info
- `POST /opena5/generate-ui` – UI-Template-Generator
- `GET /opena5/audit` – Audit-Logs

### Datenfluss
```
UI-Request → Schema-Validierung → Template-Engine → Audit-Log → Response
```

---

## ⚙️ Umsetzung & Validierung (Stufe 4)

### Tasks
- [ ] Erstelle `openwebui_opena5.py` (FastAPI Router)
- [ ] Health-Endpunkt: `GET /opena5/health`
- [ ] UI-Template-Generator: `POST /opena5/generate-ui`
- [ ] Archivator-Integration für Audit
- [ ] Request/Response Schemas (strict)
- [ ] Tests (9/9 minimum)
- [ ] Registrierung in OpenWebUI-Server

### Tests
```python
def test_health():
    response = client.get("/opena5/health")
    assert response.json()["status"] == "ok"

def test_generate_ui_template():
    payload = {"component": "button", "label": "Submit", "strict": True}
    response = client.post("/opena5/generate-ui", json=payload)
    assert response.status_code == 200
    assert response.json()["html"] is not None
```

---

## 📦 Release & Betrieb (Stufe 5)

### Deliverables
- `PLAN_opena5_Browser.md`
- `2.openwebui/openwebui_opena5.py`
- `tests/test_opena5.py`
- `Runbooks/Runbook_opena5_Browser.md`

### Akzeptanzkriterien
- ✅ Endpunkte erreichbar
- ✅ Patch-Blöcke testbar
- ✅ Audit-Logs vorhanden
- ✅ 100% Test-Pass-Rate

---

**Plan erstellt:** 2025-11-08 | **Version:** 1.0
