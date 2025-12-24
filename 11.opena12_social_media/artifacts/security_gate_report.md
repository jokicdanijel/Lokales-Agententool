# Gate Report: security_gate

- OK: `False`
- Started (UTC): `2025-12-24T07:51:51Z`
- Finished (UTC): `2025-12-24T07:51:59Z`
- Duration: `8200 ms`

## Errors

_none_

## Violations

- **secret_pattern_found** (.env): Secret-like pattern matched at line 137. ROTATE/INVALIDATE tokens if this is real.
  - evidence: `\bghp_[A-Za-z0-9]{20,}\b :: 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\nJAEGER_ENDPOINT=http://localhost:14268/api/traces\nJAEGER_UI_URL=http://localhos`
- **secret_pattern_found** (.env): Secret-like pattern matched at line 142. ROTATE/INVALIDATE tokens if this is real.
  - evidence: `\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b :: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiMjFhMTk1NS0wMTFkLTQzOTctYmNiMi03YTlmY2M2ZDkwNjkiLCJpc3MiOiJuOG4iLCJhdWQ`
- **secret_pattern_found** (main_socialmedia_agent.py): Secret-like pattern matched at line 358. ROTATE/INVALIDATE tokens if this is real.
  - evidence: `bearer\s+[A-Za-z0-9\-\._=]+ :: Bearer token"""\n    if not BEARER_TOKEN:\n        logger.warning("BEARER_TOKEN not set - authentication disabled!")\n     `
- **secret_pattern_found** (security.py): Secret-like pattern matched at line 59. ROTATE/INVALIDATE tokens if this is real.
  - evidence: `bearer\s+[A-Za-z0-9\-\._=]+ :: Bearer Token erforderlich",\n            headers={"WWW-Authenticate": "Bearer"}\n        )\n    \n    if credentials.credent`

## Warnings

- **secret_pattern_possible** (html/index.html): Secret-like pattern matched at line 66. ROTATE/INVALIDATE tokens if this is real. (file appears to be documentation/test/template - verify manually).
  - evidence: `bearer\s+[A-Za-z0-9\-\._=]+ :: Bearer Token...">\n                        <button onclick="saveToken()" class="btn btn-sm">Speichern</button>\n          `
- **secret_pattern_possible** (html/index.v2.html): Secret-like pattern matched at line 303. ROTATE/INVALIDATE tokens if this is real. (file appears to be documentation/test/template - verify manually).
  - evidence: `bearer\s+[A-Za-z0-9\-\._=]+ :: Bearer Token..." autocomplete="off">\n                        <button onclick="saveToken()" class="btn btn-sm btn-primary`
- **secret_pattern_possible** (html/index_broken.html): Secret-like pattern matched at line 54. ROTATE/INVALIDATE tokens if this is real. (file appears to be documentation/test/template - verify manually).
  - evidence: `bearer\s+[A-Za-z0-9\-\._=]+ :: Bearer Token...">\n                        <button onclick="saveToken()" class="btn btn-sm">Speichern</button>\n          `
- **secret_pattern_possible** (MASTER_PROMPT.md): Secret-like pattern matched at line 35. ROTATE/INVALIDATE tokens if this is real. (file appears to be documentation/test/template - verify manually).
  - evidence: `bearer\s+[A-Za-z0-9\-\._=]+ :: Bearer Token)\n- ✅ Strict JSON-Schemas (`extra="forbid"`)\n\n### 3. Konfliktlogik & Regeln\n\n- ✅ **Option-2-Flow:** `opena1 `
- **secret_pattern_possible** (README.md): Secret-like pattern matched at line 23. ROTATE/INVALIDATE tokens if this is real. (file appears to be documentation/test/template - verify manually).
  - evidence: `bearer\s+[A-Za-z0-9\-\._=]+ :: Bearer Token Security:** Authentifizierung vorbereitet\n- 🟡 **Implementation Status:** Ordnerstruktur vorhanden, Code pen`
- **secret_pattern_possible** (test_opena12.py): Secret-like pattern matched at line 399. ROTATE/INVALIDATE tokens if this is real. (file appears to be documentation/test/template - verify manually).
  - evidence: `bearer\s+[A-Za-z0-9\-\._=]+ :: Bearer Token: {'SET' if BEARER_TOKEN else 'NOT SET'}")\n    print(f"{BLUE}{'='*70}{RESET}\n")\n    \n    if not BEARER_TOKE`
- **secret_pattern_possible** (TODO.md): Secret-like pattern matched at line 14. ROTATE/INVALIDATE tokens if this is real. (file appears to be documentation/test/template - verify manually).
  - evidence: `bearer\s+[A-Za-z0-9\-\._=]+ :: Bearer Token) einrichten\n- [ ] OAuth-Clients für jede Plattform integrieren\n- [ ] Post-Queue-System (Redis/SQLite) für S`
- **git_history_scan_skipped**: scan_git_history enabled but .git or git executable not found.

## Info

_none_

## Stats

```json
{
  "patterns": [
    "bearer\\s+[A-Za-z0-9\\-\\._=]+",
    "authorization\\s*:\\s*bearer\\s+[A-Za-z0-9\\-\\._=]+",
    "BEGIN\\s+PRIVATE\\s+KEY",
    "\\bsk-[A-Za-z0-9]{20,}\\b",
    "\\bghp_[A-Za-z0-9]{20,}\\b",
    "\\bgithub_pat_[A-Za-z0-9_]{20,}\\b",
    "\\bAIza[0-9A-Za-z\\-_]{20,}\\b",
    "\\bAKIA[0-9A-Z]{16}\\b",
    "\\beyJ[A-Za-z0-9_-]{10,}\\.[A-Za-z0-9_-]{10,}\\.[A-Za-z0-9_-]{10,}\\b"
  ],
  "scan_git_history": true,
  "files_scanned": 1776,
  "hits_count": 11
}
```
