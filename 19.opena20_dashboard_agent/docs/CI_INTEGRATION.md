# Production Hardening CI Integration

Die Production Hardening Checks sind vollständig in GitHub Actions integriert.

## 📋 Workflow: `production-hardening.yml`

### Jobs

**1. Preflight Gate Validation**

- Führt alle 8 Scanner sequenziell aus
- Bricht bei erstem Fehler ab (fail-fast)
- Generiert Scan-Reports als Artifacts

**2. Baseline Validation**

- Validiert `system_baseline.yaml`
- Prüft Agent-IDs und Ports
- Erkennt Duplikate und Policy-Verstöße

**3. Entitlements Validation**

- Baut Entitlements-System
- Validiert Plan-Hierarchie
- Prüft Basic-Plan (4 clickable agents)

**4. Summary**

- Sammelt alle Job-Ergebnisse
- Zeigt Gesamt-Status
- Blockiert bei Violations

## 🔧 Lokaler Test

Vor dem Push kannst du lokal testen:

```bash
# Alle Scanner ausführen
cd 19.opena20_dashboard_agent
./scripts/preflight.sh

# Einzelne Validierungen
python3 scripts/validate_baseline.py
python3 scripts/build_entitlements.py
python3 scripts/validate_entitlements.py

# Preflight Gate Self-Check
python3 scripts/preflight_gate_scanner.py
```

## 📊 Artifacts

Nach jedem CI-Run werden folgende Artifacts hochgeladen:

### `preflight-scan-reports` (30 Tage)

- `ports_ids_scan.json` + `.md`
- `folder_coverage_scan.json` + `.md`
- `secrets_vault_scan.json` + `.md`
- `html_contract_scan.json` + `.md`
- `public_site_scan.json` + `.md`
- `entitlements_consistency_scan.json` + `.md`
- `api_binding_scan.json` + `.md`
- `preflight_gate_scan.json` + `.md`

### `baseline-validation` (30 Tage)

- `baseline_validation.json`

### `entitlements-validation` (30 Tage)

- `entitlements.json`
- `entitlements_validation.json`

## ⚡ Trigger

Der Workflow läuft bei:

- **Push** auf `main`, `ci/**`, `feat/**` Branches
- **Pull Requests** gegen `main`

## 🚫 Failure-Verhalten

Bei Violations:

- ❌ Job schlägt fehl
- 🔴 PR wird als "failed" markiert
- 📊 Scan-Reports in Artifacts verfügbar
- ⚠️ Merge wird blockiert

## ✅ Success-Kriterien

- Alle 8 Scanner: **PASS**
- Baseline: **Valid**
- Entitlements: **Consistent**
- Keine CRITICAL/ERROR Violations

## 🔍 Debugging

Bei Failures:

1. **Download Artifacts** aus GitHub Actions
2. **Lies Markdown-Reports** für Details
3. **Prüfe JSON** für maschinelle Verarbeitung
4. **Fixe Violations lokal**
5. **Re-run lokal**: `./scripts/preflight.sh`
6. **Push fix**

## 📚 Verwandte Docs

- [SCANNERS.md](SCANNERS.md) - Scanner-Details
- [ENTITLEMENTS.md](ENTITLEMENTS.md) - Entitlements-System
- [Master Prompt](MASTER_PROMPT.md) - Vollständige Requirements

---

**Status:** ✅ CI Integration vollständig
**Letzte Aktualisierung:** 2025-12-23
