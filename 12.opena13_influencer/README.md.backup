# ⭐ opena13 - Influencer Management

**Agent-ID:** `opena13`  
**Port:** 12358  
**Kürzel:** `influp`  
**Version:** 1.0  
**Status:** ✅ RUNNING (PID: 1727022)

---

## 📖 Überblick

**opena13** ist der **Influencer Management Agent** - spezialisiert auf Influencer-Matching, Kampagnen-Management und Metriken.

### Kernfunktionen

- 👤 **Profile Management** - Influencer-Profile erstellen und verwalten (CRUD)
- 🎯 **Campaign Matching** - Algorithmus-basiertes Matching (Score-System)
- 📊 **Metrics & Analytics** - Reichweiten, Engagement-Raten, Plattform-Statistiken
- 🔍 **Multi-Platform Support** - Instagram, TikTok, YouTube, X/Twitter, LinkedIn, Facebook
- ✅ **Hard Requirements** - Follower-Threshold als nicht kompensierbare Anforderung
- 🗂️ **Campaign Management** - Kampagnen mit Budget, Zielgruppe, Nischen

---

## 🏗️ Architektur

```
Client/UI
    ↓
Portier (12344) → OpenA2 (12345)
    ↓
kordp (Dispatcher)
    ↓
opena13 (12358) ← Dieser Agent
    ↓
OpenA2 (12345) → Portier (12344)
    ↓
Client/UI
```

**Integration:** Vollständig in Option-2-Flow integriert.

---

## 📡 API-Endpoints

### `GET /health`
Health-Check des Agents.

```bash
curl http://127.0.0.1:12355/health | jq .
```

**Response:**
```json
{
  "status": "ok",
  "service": "opena13",
  "kuerzel": "influp",
  "port": 12358,
  "uptime_seconds": 542.17,
  "total_profiles": 5,
  "total_campaigns": 3,
  "total_matches": 2
}
```

### `POST /profiles/create`
Influencer-Profil erstellen.

```bash
curl -X POST http://127.0.0.1:12358/profiles/create \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "FashionInfluencer_Anna",
    "platform": "instagram",
    "followers": 250000,
    "engagement_rate": 5.2,
    "niche": "fashion",
    "contact_email": "anna@example.com",
    "avg_likes": 13000,
    "avg_comments": 450
  }'
```

### `POST /campaigns/create`
Kampagne erstellen.

```bash
curl -X POST http://127.0.0.1:12358/campaigns/create \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Spring Fashion 2025",
    "budget": 75000.0,
    "target_audience": "Women 25-40, Fashion",
    "niches": ["fashion", "lifestyle"],
    "min_followers": 150000,
    "min_engagement_rate": 3.5,
    "start_date": "2025-03-01T00:00:00Z",
    "end_date": "2025-05-31T23:59:59Z"
  }'
```

### `POST /match`
Influencer für Kampagne matchen.

```bash
curl -X POST http://127.0.0.1:12358/match \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "<campaign_id>",
    "max_results": 10,
    "min_score": 60.0
  }'
```

**Response:**
```json
{
  "campaign_id": "a0e74275-...",
  "matches": [
    {
      "match_id": "xyz123",
      "profile": { ... },
      "score": 90.0,
      "reasoning": "Niche match (fashion) | Followers sufficient (250,000 >= 150,000) | Engagement rate 5.20% | High-engagement platform (instagram)"
    }
  ],
  "total_candidates": 5,
  "matched_at": "2025-11-27T14:30:00Z"
}
```

### `POST /metrics`
Aggregierte Metriken abrufen.

```bash
curl -X POST http://127.0.0.1:12358/metrics \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "instagram",
    "niche": "fashion"
  }'
```

---

## 🚀 Quick Start

### Agent starten

```bash
cd 12.opena13_influencer
./bin/start_opena13.sh

# Oder via ops.sh (root)
cd ..
bin/ops.sh start
```

### Health Check

```bash
curl http://127.0.0.1:12358/health | jq .
```

---

## 🔗 Integration mit Portier

### Service-Registrierung

```bash
curl -X POST http://127.0.0.1:12344/route/update \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "opena13",
    "endpoint": "http://127.0.0.1:12358",
    "program_target": "influp"
  }'
```

### Action via Portier auslösen

```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "influp",
    "action": "create_profile",
    "params": {
      "name": "TechInfluencer_Max",
      "platform": "youtube",
      "followers": 500000,
      "engagement_rate": 6.8,
      "niche": "tech"
    }
  }'
```

---

## 📁 Verzeichnisstruktur

```
12.opena13_influencer/
├── main_influencer_agent.py # FastAPI Agent Entry Point (850 LOC)
├── bin/
│   ├── start_opena13.sh     # Start-Script
│   └── stop_opena13.sh      # Stop-Script
├── test_opena13.py          # Integration Tests (11 Tests, 100%)
├── data/                    # JSON Persistence
│   ├── influencer_profiles.json
│   ├── campaigns.json
│   ├── matches.json
│   └── audit.jsonl          # Append-only Audit Log
├── logs/
│   ├── opena13.pid
│   └── opena13.nohup.log
└── README.md                # Diese Datei
```

---

## 🔐 Sicherheit

- ✅ **Bearer-Token** für alle Endpoints außer `/health`
- ✅ **Port-Policy** Enforcement (12344-12399)
- ✅ **Strict JSON** (Pydantic `extra="forbid"`)
- ✅ **Option-2-Flow** Compliance

---

## 🧪 Testing

```bash
# Integration Tests (11 Tests)
python3 test_opena13.py

# Health-Check
curl http://127.0.0.1:12358/health | jq .

# Stop Service
./bin/stop_opena13.sh
```

---

## 📊 Monitoring

```bash
# Service Logs (real-time)
tail -f logs/opena13.nohup.log

# Audit Log (JSONL)
tail -f data/audit.jsonl | jq .
```

---

## 📚 Weitere Dokumentation

- [Service Matrix](../docs/SERVICE_MATRIX.md)
- [Operations Guide](../docs/OPERATIONS.md)
- [Option-2-Flow](../.github/copilot-master-prompt.md)

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 27. November 2025
