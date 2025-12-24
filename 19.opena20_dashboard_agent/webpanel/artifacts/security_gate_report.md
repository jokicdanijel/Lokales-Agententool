# Gate Report: security_gate

- OK: `True`
- Started (UTC): `2025-12-24T08:03:23Z`
- Finished (UTC): `2025-12-24T08:03:32Z`
- Duration: `8689 ms`

## Errors

_none_

## Violations

_none_

## Warnings

- **secret_pattern_possible** (build-and-run.sh): Secret-like pattern matched at line 64. ROTATE/INVALIDATE tokens if this is real. (file appears to be documentation/test/template/build script - verify manually).
  - evidence: `bearer\s+[A-Za-z0-9\-\._=]+ :: Bearer Token"\n        echo "  3. Click 'Health Check'"\n        echo "  4. Test Native Chat or CMD Dispatch"\n        \n   `
- **secret_pattern_possible** (index.html): Secret-like pattern matched at line 700. ROTATE/INVALIDATE tokens if this is real. (file appears to be documentation/test/template/build script - verify manually).
  - evidence: `bearer\s+[A-Za-z0-9\-\._=]+ :: Bearer Token:</label>\n                    <input type="password" id="bearerToken" class="form-control">\n                `
- **secret_pattern_possible** (README.md): Secret-like pattern matched at line 41. ROTATE/INVALIDATE tokens if this is real. (file appears to be documentation/test/template/build script - verify manually).
  - evidence: `bearer\s+[A-Za-z0-9\-\._=]+ :: Bearer Token Authentication**\n- **🩺 Health Check** - Service Status\n- **💬 Native Chat** - Direkte Chat-Kommunikation  \n-`
- **secret_pattern_possible** (telegram_index.html): Secret-like pattern matched at line 700. ROTATE/INVALIDATE tokens if this is real. (file appears to be documentation/test/template/build script - verify manually).
  - evidence: `bearer\s+[A-Za-z0-9\-\._=]+ :: Bearer Token:</label>\n                    <input type="password" id="bearerToken" class="form-control">\n                `
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
  "files_scanned": 2192,
  "hits_count": 4
}
```
