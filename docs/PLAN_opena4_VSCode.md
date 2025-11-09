# PLAN: Agent opena4 – VSCode Integration
**Status:** Production-Ready Plan | **Port:** 12348 | **Modul:** 4.browser_opena5

---

## 📋 Zielsetzung (Stufe 1)

Errichte einen vollständig funktionsfähigen **VSCode-Integrator-Agenten**, der:
- Code-Snippets generiert und kontextuell hilft
- Patch-Delivery-Suggestions im OpenWebUI-Portier-Stack bietet
- Health-Endpunkte + Info-Endpunkte liefert
- Audit-Logs erzeugt für alle Patch-Aktivitäten

**Akzeptanzkriterium:** Agent liefert in Testanfrage nachvollziehbare Code-Empfehlung inkl. Patch-Vorschlag. Health-Endpunkt antwortet mit `{"status": "ok", "service": "opena4"}`.

---

## 🔗 Eingaben & Abhängigkeiten (Stufe 2)

### Eingaben
- Patch-Blöcke aus Patch-Flow (Unified Diff Format)
- OpenWebUI/OpenAI-Kontext via Gateway
- Relevante Konfig-Dateien (patch-templates, schemas)
- User-Requests via REST `/api/opena4/generate-patch`

### Abhängigkeiten
- ✅ Koordinator (opena1) – Routing
- ✅ Archivator (opena2) – Audit-Logging
- ✅ OpenWebUI Server (Port 3000)
- ✅ Patch-Flow Framework etabliert
- ✅ Health-Check System aktiv

### No-Ask-Vorgaben
- Standardisiertes Input-Schema; keine Abfrage bei eindeutiger Anforderung
- Master-Prompt: `NoClarifyMode=true`
- Env-basierte Secrets nur; keine Keys im Code

---

## 🏗️ Architektur & Interfaces (Stufe 3)

### Module & Dateipfade
```
2.openwebui/
├── openwebui_opena4.py          # Main VSCode Agent (Health, Info, Generate)
├── patch_delivery_opena4.py      # Patch-Delivery-Engine
├── audit_logger_opena4.py        # Audit-Logging Integration
└── tests/
    └── test_opena4.py           # pytest Test Suite

schemas/
├── opena4_request.json          # Input Schema
└── opena4_response.json         # Output Schema

archivp/
└── 2025/11/08/                  # Safepoint Storage
```

### REST-Schnittstellen
| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/opena4/health` | GET | Health-Check | Bearer Token |
| `/opena4/info` | GET | Service-Info | Bearer Token |
| `/opena4/generate-patch` | POST | Patch-Generator | Bearer Token |
| `/opena4/audit` | GET | Audit-Log Query | Bearer Token |

### Datenfluss
```
User Request → /opena4/generate-patch
                    ↓
            Schema-Validierung (strict: true)
                    ↓
            Patch-Block-Generation
                    ↓
            Archivator Integration (CMD-Envelope)
                    ↓
            Response mit Patch-Path + Audit-ID
                    ↓
            Client-Response (7.2 Schema)
```

---

## ⚙️ Umsetzung & Validierung (Stufe 4)

### Implementation Tasks
- [ ] **Step 1:** Erstelle `openwebui_opena4.py` mit FastAPI-Routern
- [ ] **Step 2:** Implementiere Health-Endpunkt: `GET /opena4/health` → `{"status": "ok"}`
- [ ] **Step 3:** Implementiere Patch-Generator: `POST /opena4/generate-patch`
- [ ] **Step 4:** Integriere Archivator-Calls für CMD/RESP Logging
- [ ] **Step 5:** Erstelle Request/Response JSON-Schemas (strict mode)
- [ ] **Step 6:** Schreibe pytest Tests (9/9 minimum)
- [ ] **Step 7:** Registriere in OpenWebUI Server

### Test-Cases
```python
# test_opena4.py
def test_health_ok():
    response = client.get("/opena4/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_generate_patch_valid_input():
    payload = {
        "request_id": "test-001",
        "command": "GENERATE_PATCH",
        "target_file": "src/example.py",
        "changes": {"line_5": "new content"},
        "strict": True
    }
    response = client.post("/opena4/generate-patch", json=payload)
    assert response.status_code == 200
    assert "patch_id" in response.json()
    assert response.json()["strict"] is True

def test_audit_log_written():
    # Verify that Archivator received CMD/RESP
    # Check archivp/ for SP*_opena4→opena2_CMD.json
```

### Validierung
- ✅ Health-Endpunkt antwortet
- ✅ Patch-Blöcke generieren korrekt
- ✅ Archivator empfängt CMD-Envelope
- ✅ Audit-Logs in `archivp/YYYY/MM/DD/` vorhanden
- ✅ Response-Schema validiert (additionalProperties: false)
- ✅ 9/9 Tests passing

---

## 📦 Release & Betrieb (Stufe 5)

### Deliverables
- ✅ `PLAN_opena4_VSCode.md` (diese Datei)
- ✅ `2.openwebui/openwebui_opena4.py` (Main Module)
- ✅ `2.openwebui/patch_delivery_opena4.py` (Patch-Engine)
- ✅ `2.openwebui/audit_logger_opena4.py` (Audit Integration)
- ✅ `tests/test_opena4.py` (Test Suite)
- ✅ `schemas/opena4_request.json` (Input Schema)
- ✅ `schemas/opena4_response.json` (Output Schema)
- ✅ `Runbooks/Runbook_opena4_VSCode.md` (Operations Guide)

### Akzeptanzkriterien
- ✅ Endpunkte erreichbar unter `http://127.0.0.1:12349/opena4/*`
- ✅ Patch-Blöcke simuliert anwendbar
- ✅ Audit-Logs im archivp/ vorhanden
- ✅ Tests 100% passing
- ✅ Health-Check grün
- ✅ CI/CD-Integration optional (GitHub Actions)

### Betrieb
- **Start:** `python bootstrap_starter.py --tool opena4` (falls Bootstrap-Integration)
- **Health:** `curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:12349/opena4/health`
- **Logs:** `tail -f logs/opena4.log`
- **Restart:** `pkill -f opena4; python -m 2.openwebui.openwebui_opena4`

---

## 🔒 Security & Compliance

- **Keys:** Nur via `.env` + Umgebungsvariablen (OPENAI_API_KEY_VSCODE, etc.)
- **Logging:** Alle Keys maskiert in Logs
- **TLS:** Vorbereitet (optional für Production)
- **RBAC:** Bearer-Token Validation auf allen Endpunkten
- **Audit:** SHA-256 Hashes für CMD/RESP in audit_hashes.log

---

## 📊 Status

| Item | Status |
|------|--------|
| Zielsetzung definiert | ✅ |
| Dependencies verfügbar | ✅ |
| Architektur-Design | ✅ |
| Implementation-Ready | ⏳ (Step 1-7) |
| Tests geschrieben | ⏳ |
| Production-Release | ⏳ (Nach Validation) |

**Geschätzte Implementierungszeit:** 1-2 Stunden (1 Developer)

---

## 📋 Nächste Schritte

1. ✅ Diesen Plan reviewen
2. ⏳ Implementierung Step 1-7 durchführen
3. ⏳ Tests lokal ausführen
4. ⏳ In CI/CD integrieren
5. ⏳ Production-Release (Nov 9)

---

**Plan erstellt:** 2025-11-08 | **Version:** 1.0 | **Owner:** GitHub Copilot
