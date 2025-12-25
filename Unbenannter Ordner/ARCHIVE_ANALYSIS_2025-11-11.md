# Archive Analysis & Cleanup Report

**Generated:** 2025-11-11 05:35 UTC
**Location:** `1.opena1&2_portier/archivp_store/`

---

## 📊 Archive Status Overview

| Metric                  | Value                   |
| ----------------------- | ----------------------- |
| **Total Entries**       | 172                     |
| **Storage Size**        | 644 KB                  |
| **Index File**          | `index.jsonl` (55 KB)   |
| **Date Range**          | 2025-11-10 → 2025-11-11 |
| **Partition Structure** | `YYYY/MM/DD/` (daily)   |

---

## 📈 Entry Breakdown by Type

```
Type               Count   Percentage   Source
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHAT_COMPLETION    102     59.3%       infer
MODEL_LIST         41      23.8%       infer
ECHO               10      5.8%        Services (echo endpoint)
MESSAGE_OUT        10      5.8%        Telegram
DISPATCH           4       2.3%        kordp (orchestrator)
ROUTE              4       2.3%        kordp (orchestrator)
INIT               1       0.6%        bootstrap
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL              172     100%
```

---

## 📁 Temporal Distribution

**Date Partitions:**

- `2025/11/10/` – First batch (setup phase)
- `2025/11/11/` – Current batch (load testing)

**Timeline:**

- First Entry: `2025-11-10T16:59:52Z` (INIT from bootstrap)
- Last Entry: `2025-11-11T04:22:33Z` (CHAT_COMPLETION from inference)
- Duration: ~11.4 hours

---

## 🔍 Source Services Distribution

| Service                | Entries | Primary Types                          |
| ---------------------- | ------- | -------------------------------------- |
| **infer**              | 143     | CHAT_COMPLETION (102), MODEL_LIST (41) |
| **kordp**              | 8       | DISPATCH (4), ROUTE (4)                |
| **telegram**           | 10      | MESSAGE_OUT (10)                       |
| **bootstrap**          | 1       | INIT (1)                               |
| **Services (generic)** | 10      | ECHO (10)                              |

**Note:** Inference service (Port 12348) generates 83% of archive traffic (143/172 entries).

---

## 💾 Storage Efficiency Analysis

| Category           | Size    | Notes                                |
| ------------------ | ------- | ------------------------------------ |
| Index File         | 55 KB   | Append-only JSONL metadata           |
| Data Files         | ~589 KB | Compressed JSON (200-270 bytes each) |
| Average Entry Size | 3.74 KB | (644 KB ÷ 172)                       |
| Overhead           | ~55 KB  | Index duplication (~8.5%)            |

**Efficiency:** ✅ Good compression ratio (200 bytes per safepoint)

---

## 🧹 Cleanup Options

### **Option 1: Keep All (Conservative)**

- **Action:** No deletion
- **Rationale:** Archive size < 1 MB, excellent for audit trails
- **Recommendation:** ✅ RECOMMENDED for production systems

### **Option 2: Archive by Date (Selective)**

- **Action:** Delete entries older than 24 hours
- **Impact:** Would remove ~50% (entries from 2025-11-10)
- **New Size:** ~320 KB
- **Use Case:** When storage limited

### **Option 3: Prune by Type (Targeted)**

- **Action:** Delete low-value safepoints (ECHO, excess MODEL_LIST)
- **Impact:** Remove 51 entries (ECHO: 10, excess MODEL_LIST: 41)
- **New Size:** ~400 KB
- **Use Case:** For development environments

### **Option 4: Reset (Nuclear)**

- **Action:** Delete entire archive
- **Impact:** Total reset to 0 entries
- **New Size:** ~4 KB (empty index)
- **Use Case:** When starting fresh (not recommended)

---

## 🔧 Recommended Action Plan

### **Immediate (No Risk)**

1. ✅ Archive size is healthy (644 KB)
2. ✅ No cleanup needed at this time
3. ✅ Continue monitoring daily

### **If Storage Exceeds 10 MB**

1. Delete entries older than 7 days
2. Keep high-value types (CHAT_COMPLETION, DISPATCH, ROUTE, MESSAGE_OUT)
3. Retain INIT for bootstrap tracking

### **Best Practice**

```bash
# Monthly archive rotation
bin/ops.sh archiv:backup   # Backup current state
bin/ops.sh archiv:prune    # Prune old entries
bin/ops.sh archiv:verify   # Verify integrity
```

---

## 📋 Detailed Entry Samples

### Sample 1: Inference Chat Completion

```json
{
  "sp": "SP1762834944_infer→archivp_CHAT_COMPLETION.json",
  "ts": "2025-11-11T04:22:24.696554Z",
  "src": "infer",
  "dst": "archivp",
  "kind": "CHAT_COMPLETION",
  "path": "2025/11/11/SP1762834944_infer→archivp_CHAT_COMPLETION.json"
}
```

### Sample 2: Orchestrator Dispatch

```json
{
  "sp": "SP1762832955_kordp→archivp_DISPATCH.json",
  "ts": "2025-11-11T03:49:15.214249Z",
  "src": "kordp",
  "dst": "archivp",
  "kind": "DISPATCH",
  "path": "2025/11/11/SP1762832955_kordp→archivp_DISPATCH.json"
}
```

### Sample 3: Bootstrap Init

```json
{
  "sp": "SP1762793992_bootstrap→archivp_INIT.json",
  "ts": "2025-11-10T16:59:52.461268Z",
  "src": "bootstrap",
  "dst": "archivp",
  "kind": "INIT",
  "path": "2025/11/10/SP1762793992_bootstrap→archivp_INIT.json"
}
```

---

## 🎯 Key Findings

✅ **Archive Integrity:** All 172 entries well-formed JSON
✅ **No Corruption:** All safepoint files readable
✅ **Balanced Growth:** Steady rate (~15 entries/hour during tests)
✅ **Service Coverage:** All active services logging correctly
⚠️ **High Inference Load:** 83% from inference service (expected for llama-stack)
⚠️ **Duplicate MODEL_LIST:** 41 entries (refresh every ~2.5 minutes)

---

## 🚀 Next Steps

### To Inspect Specific Entries:

```bash
# View last N entries
tail -10 1.opena1\&2_portier/archivp_store/index.jsonl | jq .

# Filter by service
jq 'select(.src=="infer")' 1.opena1\&2_portier/archivp_store/index.jsonl | head -5

# Filter by date
jq 'select(.ts | startswith("2025-11-11"))' 1.opena1\&2_portier/archivp_store/index.jsonl | wc -l
```

### To Clean Up:

```bash
# Option A: Backup before cleanup
cp -r 1.opena1\&2_portier/archivp_store 1.opena1\&2_portier/archivp_store.backup.2025-11-11

# Option B: Delete entries older than 24h
find 1.opena1\&2_portier/archivp_store/2025/11/10 -delete

# Option C: Regenerate index after deletion
python3 scripts/rebuild_archive_index.py
```

---

## 📌 Storage Quota Recommendations

| Environment     | Quota  | Cleanup Trigger |
| --------------- | ------ | --------------- |
| **Development** | 50 MB  | Every 1 week    |
| **Staging**     | 500 MB | Every 1 month   |
| **Production**  | 5 GB   | Every 3 months  |

**Current Status:** ✅ Development (644 KB / 50 MB = 1.3%)

---

**Generated by:** Archive Analysis Tool
**Next Review:** 2025-11-12 (24h)
**Archive Path:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/archivp_store/`
