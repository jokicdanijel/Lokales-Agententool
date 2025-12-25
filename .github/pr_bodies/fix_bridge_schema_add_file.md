## PR: fix(bridge_schema): add minimal configs/bridge_schema.json and re-enable check-json

**Branch:** fix/bridge_schema-add-minimal
**Commit:** chore: add minimal bridge schema + re-enable check-json

### Problem
CI `check-json` hook failed on `configs/bridge_schema.json` with `Expecting value` because the file was present but empty (0 bytes).

### Lösung
- Füge `configs/bridge_schema.json` mit einem minimal gültigen JSON Schema hinzu (see below).
- Entferne die enge `exclude` für `configs/bridge_schema.json` aus `.pre-commit-config.yaml` (wieder aktivieren der Prüfung).

Minimal Schema:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "bridge_schema.json",
  "title": "Bridge Schema",
  "type": "object",
  "additionalProperties": false,
  "properties": {}
}
```

### Verifikation
- CI: `pre-commit run --all-files` should now pass the `check-json` step for this file.
- Locally: `python -m json.tool configs/bridge_schema.json` validates.

### Risiko & Rollback
- Risiko: Sehr gering (nur Dokument/Schemadatei). Rollback durch Entfernen der Datei oder Revert des Commit.

### Relates
- Relates to PR #104 (previous attempt to exclude file during triage)
