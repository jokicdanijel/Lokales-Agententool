# 🤖 GitHub Copilot – Handoff Documentation

**System:** ELION Hyper-Dashboard
**Version:** 1.0.0
**Status:** Production Ready
**Datum:** 2025-12-22

---

## 🎯 Zweck dieses Dokuments

Dieses Dokument enthält **alle Regeln, Constraints und Workflows**, die GitHub Copilot bei der Code-Generierung für ELION Hyper-Dashboard beachten MUSS.

**Grundprinzip:** Copilot arbeitet IMMER nach Preflight-Check und nutzt AUSSCHLIESSLICH generierte Manifests als Wahrheit.

---

## 🔐 IMMUTABLE RULES (NIEMALS VERLETZEN)

### 1. Canonical Agent Registry (ABSOLUT UNVERÄNDERLICH)

```json
{
  "opena1": 12344,   "opena2": 12345,   "opena3": 12347,
  "opena4":  12346,   "opena5": 12351,   "opena6": 12352,
  "opena7": 12350,   "opena8": 12354,   "opena9": 12355,
  "opena10": 12356,  "opena11": 12357,  "opena12": 12358,
  "opena13": 12359,  "opena14": 12360,  "opena15":  12361,
  "opena16": 12362,  "opena17": 12366,  "opena18": 12363,
  "opena19":  12367,  "opena20": 12349,  "opena21": 12368
}
```

**Regeln:**
- ❌ NIEMALS einen Port ändern
- ❌ NIEMALS einen Agent-Namen ändern
- ❌ NIEMALS einen neuen Agenten hinzufügen ohne Preflight-Update
- ❌ NIEMALS Ports 8080 oder 3000 verwenden

... (vollständiges Dokument wie besprochen) ...
