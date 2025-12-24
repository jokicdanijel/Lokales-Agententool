# Production Hardening Scanners

Diese 8 Scanner implementieren die **1000% Compliance**-Anforderungen des EDEN/PORTIER Hyper-Dashboards. Jeder Scanner führt spezifische Fail-Fast-Checks durch und bricht die CI bei Verstößen ab.

## 📋 Scanner-Übersicht

### 1. Ports & IDs Compliance Scanner
**Datei:** `ports_ids_compliance_scanner.py`
**Zweck:** 1000% Enforcement von Port- und Agent-ID-Richtlinien

**Prüft:**
- Exakt opena1-opena21 existieren (keine Variationen)
- Port-Einzigartigkeit und Baseline-Matching
- Verbotene Ports (8080, 3000)
- Ungültige Agent-Referenzen
- Port-Range-Policy (12344-12399)

**Exit 1 bei:**
- Fehlende oder zusätzliche Agents
- Port-Duplikate oder Abweichungen
- Verbotene Port-Nutzung

---

### 2. Folder Coverage Scanner
**Datei:** `folder_coverage_scanner.py`
**Zweck:** Vollständige rekursive Ordneranalyse verifizieren

**Prüft:**
- Jeder Agent-Ordner existiert und ist nicht leer
- Rekursive File-Enumeration durchgeführt (count > 0)
- Inventory enthält File-Hashes (Beweis der Analyse)
- Stabile Sortierung (deterministische Scans)

**Exit 1 bei:**
- Leere oder fehlende Agent-Ordner
- Unvollständige Inventardaten
- Fehlende File-Hashes

---

### 3. Secrets & Vault Scanner
**Datei:** `secrets_vault_scanner.py`
**Zweck:** Cleartext-Secrets außerhalb opena11 erkennen

**Prüft:**
- KEINE Cleartext-Secrets außerhalb opena11
- KEINE API-Keys, Tokens, Private Keys in Non-Vault-Code
- KEINE plaintext/decrypted Endpoints außerhalb opena11
- Vault-Endpoints existieren NUR unter opena11

**Detection-Patterns:**
- API Keys (api_key, apikey, API_KEY)
- Tokens (token, access_token, auth_token)
- Private Keys (BEGIN PRIVATE KEY)
- OAuth Secrets (client_secret)
- SMTP/DB Passwords

**Exit 1 bei:**
- Secrets außerhalb Vault gefunden
- Vault-Policy-Verstöße

---

### 4. HTML Contract Scanner
**Datei:** `html_contract_scanner.py`
**Zweck:** Strikte HTML-Vertrags-Regeln durchsetzen

**Prüft:**
- KEINE `<script>` Tags
- KEINE inline `style=""` Attribute
- KEINE `<link rel="stylesheet">` (CSS-Dateien)
- Semantische HTML5-Struktur (header/nav/main/footer)
- Forms haben `data-action` + `data-api`
- Error-Pages existieren (403.html, 404.html, 500.html)

**Exit 1 bei:**
- CSS/JS in HTML gefunden
- Fehlende semantische Struktur
- Ungültige Form-Contracts

---

### 5. Public Website Scanner
**Datei:** `public_website_scanner.py`
**Zweck:** hyperdashboard-one.de Vollständigkeit prüfen

**Prüft:**
- Alle erforderlichen Routes existieren
- Content-Density (Mindestwortanzahl)
  - Landing: 800+ Wörter
  - Plan-Pages: 300+ Wörter
  - Legal: 500+ Wörter
- Plan-Page-Similarity (<85% Threshold)
- Landing-Page Sections vorhanden

**Erforderliche Routes:**
- Root: `/` (Landing)
- Auth: `/login`, `/register`, `/forgot-password`
- Plans: `/basic`, `/pro`, `/premium`, `/ultimum`
- Legal: `/legal/privacy`, `/legal/terms`, `/legal/imprint`

**Exit 1 bei:**
- Fehlende Routes
- Zu wenig Content
- Zu ähnliche Plan-Pages (>85%)

---

### 6. Entitlements Consistency Scanner
**Datei:** `entitlements_consistency_scanner.py`
**Zweck:** HTML enthält KEINE hardcoded Entitlement-Logik

**Prüft:**
- KEINE hardcoded Plan-Logik in HTML (z.B. `if plan=="basic"`)
- KEINE inline Agent enable/disable
- Basic Plan: Exakt 4 clickable via entitlements.json
- Plan-Hierarchie erhalten (HTML liest JSON, berechnet nicht)
- KEINE Agent-Unlock-Logik in JS/HTML

**Exit 1 bei:**
- Hardcoded Plan-Checks gefunden
- Agent-Enable/Disable-Logik in Code
- Clickable-Array-Definitionen

---

### 7. API Binding Scanner
**Datei:** `api_binding_scanner.py`
**Zweck:** KEINE direkten agent:PORT Calls in HTML/JS

**Prüft:**
- KEINE direkten URLs wie `http://localhost:12345`
- KEINE `agent:PORT` hardcoded Endpoints
- ALLE API-Calls gehen durch Control-Plane (opena1)
- KEINE direkte Agent-zu-Agent-Kommunikation
- Koordination via opena1 ONLY

**Akzeptable Patterns:**
- `/api/*` (geroutet via Control-Plane)
- Relative Paths: `/status`, `/health`
- `data-api` Attribute

**Verbotene Patterns:**
- `http://localhost:12344`
- `agent://opena5:12348`
- Direkte Port-Referenzen

**Exit 1 bei:**
- Direkte Bindings gefunden
- Bypass des Control-Planes

---

### 8. Preflight Gate Scanner
**Datei:** `preflight_gate_scanner.py`
**Zweck:** Exakte Schritt-Reihenfolge und Blocking-Verhalten prüfen

**Prüft:**
- Alle 8 Scanner werden in Preflight aufgerufen
- EXAKTE ORDER enforced (kein Parallel, kein Reordering)
- Jeder Scanner MUSS blocken bei Failure (exit 1)
- Keine Schritte übersprungen
- CI-Config ruft preflight.sh auf

**Erwartete Order:**
1. ports_ids_compliance_scanner.py
2. folder_coverage_scanner.py
3. secrets_vault_scanner.py
4. html_contract_scanner.py
5. public_website_scanner.py
6. entitlements_consistency_scanner.py
7. api_binding_scanner.py
8. preflight_gate_scanner.py (Self-Check)

**Exit 1 bei:**
- Fehlende Scanner-Dateien
- Falsche Reihenfolge
- Fehlendes Blocking (`|| exit 1`)
- CI ruft Preflight nicht auf

---

## 🚀 Verwendung

### Einzelner Scanner

```bash
python3 scripts/ports_ids_compliance_scanner.py
```

### Alle Scanner (Preflight)

```bash
./scripts/preflight.sh
```

### In CI integrieren

**.github/workflows/production-hardening.yml:**

```yaml
name: Production Hardening

on: [push, pull_request]

jobs:
  preflight:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install pyyaml

      - name: Run Preflight Gate
        run: |
          ./scripts/preflight.sh
```

---

## 📊 Ausgaben

Jeder Scanner generiert **zwei Reports**:

### JSON Report
`artifacts/scans/<scanner_name>_scan.json`

Maschinelles Format für weitere Verarbeitung.

### Markdown Report
`artifacts/scans/<scanner_name>_scan.md`

Menschenlesbares Format mit Details zu Verstößen.

---

## ⚠️ Fail-Fast Verhalten

Alle Scanner implementieren **Fail-Fast**:

```
EXIT CODE 0 = Alle Checks bestanden
EXIT CODE 1 = Verstöße gefunden → CI MUSS brechen
```

Wenn ein Scanner fehlschlägt:

1. **Preflight stoppt sofort** (kein Weiterlaufen)
2. **CI-Build bricht ab** (keine Deployment)
3. **Violations sind in Reports dokumentiert**
4. **Fix erforderlich vor Merge**

---

## 🔍 Scanner-Details

### Severity Levels

- **CRITICAL**: Muss sofort behoben werden (Exit 1)
- **ERROR**: Schwerwiegender Verstoß (Exit 1)
- **WARNING**: Sollte behoben werden (kein Exit 1)

### Context Information

Jeder Violation-Report enthält:

- **Datei + Zeilennummer**: Exakte Position
- **Violation-Typ**: Was wurde verletzt
- **Context**: Code-Snippet (bis 120 Zeichen)
- **Severity**: critical/error/warning

---

## 📁 Datei-Struktur

```
scripts/
├── preflight.sh                              # Master-Script (alle 8 Scanner)
├── ports_ids_compliance_scanner.py          # Scanner #1
├── folder_coverage_scanner.py               # Scanner #2
├── secrets_vault_scanner.py                 # Scanner #3
├── html_contract_scanner.py                 # Scanner #4
├── public_website_scanner.py                # Scanner #5
├── entitlements_consistency_scanner.py      # Scanner #6
├── api_binding_scanner.py                   # Scanner #7
└── preflight_gate_scanner.py                # Scanner #8

artifacts/
└── scans/                                    # Generierte Reports
    ├── ports_ids_scan.json
    ├── ports_ids_scan.md
    ├── folder_coverage_scan.json
    ├── folder_coverage_scan.md
    ├── secrets_vault_scan.json
    ├── secrets_vault_scan.md
    ├── html_contract_scan.json
    ├── html_contract_scan.md
    ├── public_site_scan.json
    ├── public_site_scan.md
    ├── entitlements_consistency_scan.json
    ├── entitlements_consistency_scan.md
    ├── api_binding_scan.json
    ├── api_binding_scan.md
    ├── preflight_gate_scan.json
    └── preflight_gate_scan.md
```

---

## 🎯 Compliance-Matrix

| Scanner                | Compliance-Bereich       | Kritisch für |
|------------------------|-------------------------|--------------|
| Ports & IDs            | Foundation              | Baseline     |
| Folder Coverage        | Completeness            | Discovery    |
| Secrets & Vault        | Security                | Production   |
| HTML Contract          | Structure               | Generation   |
| Public Website         | Content                 | Marketing    |
| Entitlements           | Logic                   | Monetization |
| API Binding            | Routing                 | Architecture |
| Preflight Gate         | CI/CD                   | Deployment   |

---

## 🛠️ Troubleshooting

### Scanner schlägt fehl

1. **JSON/MD Reports prüfen**: `artifacts/scans/`
2. **Violations lesen**: Exakte Datei + Zeile angegeben
3. **Fixes anwenden**
4. **Scanner erneut ausführen**

### Preflight bricht ab

Der Scanner, der fehlschlug, ist der letzte, der Ausgabe produziert hat. Dessen Report enthält alle Details.

### CI schlägt fehl

```bash
# Lokal reproduzieren:
./scripts/preflight.sh

# Einzelne Scanner debuggen:
python3 scripts/<scanner_name>.py
```

---

## 📚 Weitere Dokumentationen

- [System Baseline](../system_baseline.yaml) - Agent/Port-Definitionen
- [Entitlements](../docs/ENTITLEMENTS.md) - Plan-Hierarchie
- [Master Prompt](../docs/MASTER_PROMPT.md) - Vollständige Requirements

---

## ✅ Success Criteria

Preflight gilt als **bestanden**, wenn:

1. ✅ Alle 8 Scanner exit 0 zurückgeben
2. ✅ Keine CRITICAL/ERROR Violations
3. ✅ Warnings sind dokumentiert (optional)
4. ✅ Alle Reports generiert
5. ✅ CI-Integration funktioniert

Dann ist das System **bereit für Production Deployment** 🚀
