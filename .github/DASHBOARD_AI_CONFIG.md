# 🤖 Dashboard AI Configuration (opena20)

**Version:** 1.0  
**Datum:** 28. November 2025  
**Status:** ✅ **PRODUCTION-READY**

---

## 🎯 Model Configuration (CRITICAL)

### Default Model

```
MODEL: gpt-3.5-turbo
```

**WICHTIG:** Dieses Model ist **dauerhaft für das gesamte Dashboard** festgelegt.  
**NICHT ÄNDERN** ohne explizite Freigabe.

### Token Policy

```
MAX_TOKENS: UNBEGRENZT (kein Limit)
```

**Grund:** Dashboard-AI-Responses sollen vollständig und ohne Abbruch geliefert werden.

---

## 🔒 Option-2-Flow Enforcement (HEILIGE REGEL)

### Safepoint-Struktur (UNVERÄNDERBAR)

Jeder Request durch das System **MUSS** folgende Struktur einhalten:

```json
{
  "src": "kordp",
  "dst": "archivp",
  "kind": "LOG",
  "event": "option2_flow_validation",
  "request_id": "OPT2-E2E-<timestamp>"
}
```

### Validierungskriterien

- ✅ **src:** Immer `kordp` (Koordinatport)
- ✅ **dst:** Immer `archivp` (Archivport)
- ✅ **kind:** Immer `LOG` (Safepoint-Typ)
- ✅ **event:** `option2_flow_validation` oder äquivalent
- ✅ **request_id:** Format `OPT2-E2E-<timestamp>` oder vergleichbar

### Filename Convention

```
SP<timestamp>_kordp→archivp_LOG.json
```

**Kritisch:** Unicode-Pfeil `→` (U+2192) **PFLICHT**

---

## 📊 Health Check Standards

### Erwartete Response

```json
{
  "service": "opena20",
  "status": "healthy",
  "strict": true,
  "openai_key_present": true,
  "openai_client_ready": true,
  "timestamp": "2025-11-28T..."
}
```

### Stack Health (E2E Test)

```bash
=== 1. Health Check Stack ===

🔹 opena1 (Port 12344): ✅ OK (Key present)
🔹 opena2 (Port 12345): ✅ OK (Key present, 190 entries)

=== 2. Option-2-Flow Test ===

📋 Request ID: OPT2-E2E-<timestamp>
✅ Request akzeptiert

=== 3. Safepoint Verifikation ===

📂 Letzter Safepoint: SP<timestamp>_kordp→archivp_LOG.json

🔍 Safepoint-Struktur:
   src:        kordp
   dst:        archivp
   kind:       LOG
   event:      option2_flow_validation
   request_id: OPT2-E2E-<timestamp>
```

**Alle Checks MÜSSEN bestehen.**

---

## 🚀 API Endpoint Configuration

### `/api/ai/chat` (Primary Endpoint)

```json
{
  "message": "User-Anfrage",
  "model": "gpt-3.5-turbo",     // DEFAULT (nicht überschreiben!)
  "temperature": 0.7            // Optional (default: 0.7)
}
```

**ENTFERNT:** `max_tokens` Parameter (keine Begrenzung mehr)

### Response Format

```json
{
  "strict": true,
  "message": "User-Anfrage",
  "response": "Vollständige AI-Antwort ohne Token-Limit",
  "model": "gpt-3.5-turbo",
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 1500,  // Kann unbegrenzt sein
    "total_tokens": 1525
  }
}
```

---

## 🔧 Implementation Details

### Code Location

```
src/pkg/main_dashboard.py
Funktion: ai_chat()
Zeilen: ~263-315
```

### Key Changes (28. Nov 2025)

1. **Model:** `gpt-4` → `gpt-3.5-turbo` (DEFAULT)
2. **max_tokens:** `500` → `REMOVED` (unbegrenzt)
3. **Comment:** Klarstellung "WICHTIG: Für gesamtes Dashboard vorerst merken!"

### Environment Variables

```bash
# .env
OPENAI_API_KEY_OPENA20=sk-proj-...  # REQUIRED
BEARER_TOKEN=<uuid>                  # REQUIRED
```

---

## 🧪 Testing

### AI Chat Test

```bash
scripts/test_opena20_ai.sh
```

**Erwartete Änderungen:**
- ✅ Model: `gpt-3.5-turbo` (nicht mehr `gpt-4`)
- ✅ Response: Vollständig (keine Token-Truncation)
- ✅ Usage: Zeigt tatsächlich verwendete Tokens (kann > 500 sein)

### E2E Option-2-Flow Test

```bash
bin/ops.sh e2e
```

**MUSS alle Checks bestehen:**
- ✅ Health: opena1 + opena2
- ✅ Flow: Request akzeptiert
- ✅ Safepoint: Struktur korrekt (`kordp→archivp_LOG`)

---

## 📋 Compliance Checklist

Vor jedem Deployment:

- [ ] Model ist `gpt-3.5-turbo` (nicht `gpt-4`)
- [ ] `max_tokens` Parameter ist **entfernt**
- [ ] Environment Variable `OPENAI_API_KEY_OPENA20` gesetzt
- [ ] Health-Check zeigt `openai_client_ready: true`
- [ ] E2E-Test besteht alle 3 Phasen
- [ ] Safepoint-Struktur: `src=kordp`, `dst=archivp`, `kind=LOG`
- [ ] Unicode-Pfeil `→` in Safepoint-Filename

---

## 🔒 Policy Enforcement

### NICHT ERLAUBT

- ❌ Model-Änderung ohne Freigabe
- ❌ Token-Limits hinzufügen
- ❌ Option-2-Flow umgehen
- ❌ Safepoint-Struktur ändern
- ❌ Unicode-Pfeil durch `->` ersetzen

### IMMER ERFORDERLICH

- ✅ Model: `gpt-3.5-turbo`
- ✅ Unbegrenzte Token-Response
- ✅ Option-2-Flow-Konformität
- ✅ Safepoint-Logging (`kordp→archivp_LOG`)
- ✅ Health-Check vor Production-Deployment

---

**Maintainer:** Danijel (ELION Team)  
**Last Updated:** 28. November 2025  
**Review Cycle:** Bei jedem Major-Update
