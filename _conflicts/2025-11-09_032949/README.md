# Konflikt-Quarantäne vom 9. November 2025 03:29:49

**Status:** Legacy-Archive  
**Grund:** Struktur-Cleanup während Phase 5  
**Datum:** 9. November 2025 03:29:49 UTC

## Zweck

Dieser Ordner diente als temporäre Quarantäne für Dateien, die während der 
automatisierten Struktur-Bereinigung von `rename_map.csv` verschoben wurden.

## Wiederherstellung

Alle **produktiv benötigten Dateien** wurden am **27. November 2025** mittels
`GOVERNANCE_FIX_TESTS.sh` in ihre korrekten Verzeichnisse zurückverschoben:

- ✅ Tests → `19.dashboard_agent/tests/`
- ✅ Scripts → `19.dashboard_agent/scripts/`
- ✅ Dokumentation → `docs/testing/`

## Verbleibende Dateien

Dateien, die hier verbleiben, sind:
- Legacy-Code ohne produktiven Einsatz
- Duplikate
- Obsolete Konfigurationen

## Archivierung

Dieser Ordner kann nach **1. Dezember 2025** vollständig archiviert oder 
gelöscht werden, sofern keine weiteren Abhängigkeiten bestehen.

---
**Erstellt durch:** `GOVERNANCE_FIX_TESTS.sh`  
**Datum:** 2025-11-27 18:07:45 UTC  
**Ausgeführt von:** danijel-jd
