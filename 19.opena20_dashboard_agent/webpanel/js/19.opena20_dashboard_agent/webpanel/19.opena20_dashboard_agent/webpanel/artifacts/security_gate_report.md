# Gate Report: security_gate

- OK: `True`
- Started (UTC): `2025-12-24T07:57:16Z`
- Finished (UTC): `2025-12-24T07:57:16Z`
- Duration: `4 ms`

## Errors

_none_

## Violations

_none_

## Warnings

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
  "files_scanned": 0,
  "hits_count": 0
}
```
