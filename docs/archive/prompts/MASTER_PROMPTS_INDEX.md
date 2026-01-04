# 📚 MASTER PROMPTS INDEX – Alle 21 Agenten

**Version:** 1.0
**Datum:** 27. November 2025
**Status:** ✅ **COMPLETE**
**Generiert:** `scripts/generate_master_prompts.py`

---

## 🎯 Übersicht

Diese Datei indexiert alle **21 Agent-spezifischen Master-Prompts** für das ELION Hyper-Dashboard.

Jeder Master-Prompt ist eine **vollständige, kopierbare Arbeitsanweisung** für VSCode Copilot, die:

- ✅ **Vollautomatisch** arbeitet (keine Rückfragen)
- ✅ **Option-2-Flow** einhält (`opena1 → opena2 → kordp → tool`)
- ✅ **Port-Policy** durchsetzt (12344-12399 Backend, 8080 UI-only)
- ✅ **Safepoint-Archivierung** garantiert (Append-only, Unicode-Pfeil `→`)
- ✅ **Strict JSON-Schemas** verwendet (`extra="forbid"`)
- ✅ **ENV-only Secrets** erzwingt (niemals hardcoded)

---

## 📋 Master-Prompt-Struktur (Standard)

Jeder Prompt folgt dieser Struktur:

1. **Rolle & Zielsetzung** – Agent-ID, Port, Domain, Scope
2. **Ablauf (vollautomatisch)** – 8 Schritte:
   - Initialisierung
   - Struktur & Setup
   - Konfliktlogik & Regeln
   - Berichte & Artefakte
   - Validierung
   - Dry-Run
   - Apply
   - Finalisierung
3. **Eingabeparameter (optional)** – JSON-Schema
4. **Ausgabe** – Success/Error-Format
5. **Spezifische Regeln** – Agent-spezifische Policies
6. **Verwendung in VSCode Copilot** – Integration-Hinweise

---

## 🗂️ Agent-Index (opena3-opena21)

| ID      | Name               | Port  | Status     | Kürzel         | Master-Prompt-Datei                                                                          |
| ------- | ------------------ | ----- | ---------- | -------------- | -------------------------------------------------------------------------------------------- |
| opena3  | OpenWebUI Terminal | 12347 | ✅ Running | `owuip`        | [`2.opena3_openwebui/MASTER_PROMPT.md`](2.opena3_openwebui/MASTER_PROMPT.md)                 |
| opena4  | Telegram Bot       | 12346 | 🟡 Planned | `telep`        | [`3.opena4_telegram/MASTER_PROMPT.md`](3.opena4_telegram/MASTER_PROMPT.md)                   |
| opena5  | VS Code Agent      | 12351 | 🟡 Planned | `vscop`        | [`4.opena5_vscode/MASTER_PROMPT.md`](4.opena5_vscode/MASTER_PROMPT.md)                       |
| opena6  | Browser Automation | 12350 | 🟡 Planned | `browsep`      | [`5.opena6_browser/MASTER_PROMPT.md`](5.opena6_browser/MASTER_PROMPT.md)                     |
| opena7  | E-Mail Client      | 12352 | 🟡 Planned | `emailp`       | [`6.opena7_email/MASTER_PROMPT.md`](6.opena7_email/MASTER_PROMPT.md)                         |
| opena8  | WhatsApp Agent     | 12353 | 🟡 Planned | `whatsappp`    | [`7.opena8_whatsapp/MASTER_PROMPT.md`](7.opena8_whatsapp/MASTER_PROMPT.md)                   |
| opena9  | Telefonie Agent    | 12354 | 🟡 Planned | `telphonep`    | [`8.opena9_telephone/MASTER_PROMPT.md`](8.opena9_telephone/MASTER_PROMPT.md)                 |
| opena10 | Call Tracking      | 12355 | 🟡 Planned | `calltrackp`   | [`9.opena10_call_tracking/MASTER_PROMPT.md`](9.opena10_call_tracking/MASTER_PROMPT.md)       |
| opena11 | Unlock Master      | 12356 | 🟡 Planned | `unlockp`      | [`10.opena11_unlock/MASTER_PROMPT.md`](10.opena11_unlock/MASTER_PROMPT.md)                   |
| opena12 | Social Media       | 12357 | 🟡 Planned | `smp`          | [`11.opena12_social_media/MASTER_PROMPT.md`](11.opena12_social_media/MASTER_PROMPT.md)       |
| opena13 | Influencer Agent   | 12358 | 🟡 Planned | `influp`       | [`12.opena13_influencer/MASTER_PROMPT.md`](12.opena13_influencer/MASTER_PROMPT.md)           |
| opena14 | Calendar Agent     | 12359 | 🟡 Planned | `calp`         | [`13.opena14_calendar/MASTER_PROMPT.md`](13.opena14_calendar/MASTER_PROMPT.md)               |
| opena15 | HTML Creator       | 12360 | 🟡 Planned | `htmlp`        | [`14.opena15_html/MASTER_PROMPT.md`](14.opena15_html/MASTER_PROMPT.md)                       |
| opena16 | Shop Agent         | 12361 | 🟡 Planned | `shopp`        | [`15.opena16_shop/MASTER_PROMPT.md`](15.opena16_shop/MASTER_PROMPT.md)                       |
| opena17 | Homepage Creator   | 12362 | 🟡 Planned | `hpcreatep`    | [`16.opena17_homepagecreator/MASTER_PROMPT.md`](16.opena17_homepagecreator/MASTER_PROMPT.md) |
| opena18 | CRM Agent          | 12363 | 🟡 Planned | `crmp`         | [`17.opena18_CMR/MASTER_PROMPT.md`](17.opena18_CMR/MASTER_PROMPT.md)                         |
| opena19 | Aktien & Crypto    | 12364 | 🟡 Planned | `stockcryptop` | [`18.opena19_Aktien&Crypto/MASTER_PROMPT.md`](18.opena19_Aktien&Crypto/MASTER_PROMPT.md)     |
| opena20 | Dashboard Agent    | 12349 | ✅ Running | `dashp`        | [`19.opena20_dashboard_agent/MASTER_PROMPT.md`](19.opena20_dashboard_agent/MASTER_PROMPT.md) |
| opena21 | Workflow Engine    | 12365 | 🟡 Planned | `workflowp`    | [`20.opena21_workflow/MASTER_PROMPT.md`](20.opena21_workflow/MASTER_PROMPT.md)               |

**Hinweis:** opena1 und opena2 haben keine eigenen Master-Prompts, da sie in `1.opena1&2_portier/` kombiniert sind.

---

## 🚀 Verwendung der Master-Prompts

### In VSCode Copilot Chat

```
# Lade Master-Prompt für opena5
@workspace Nutze den Master-Prompt aus 4.opena5_vscode/MASTER_PROMPT.md
und implementiere den VS Code Agent vollständig.
```

### Als Generator-Input

```bash
# Generiere alle Prompts neu
python3 scripts/generate_master_prompts.py
```

### Als Systemreferenz

Jeder Master-Prompt kann als **Systemreferenz** für:

- Custom GPTs (OpenAI)
- Claude Projects (Anthropic)
- GitHub Copilot Workspace Instructions
- CI/CD-Automatisierung
- Agent-Bootstrapping

---

## 🔧 Konventionen (für alle Prompts)

Alle Master-Prompts folgen diesen unveränderlichen Regeln:

| Konvention               | Wert        | Beschreibung                         |
| ------------------------ | ----------- | ------------------------------------ |
| **Snake_case**           | ✅          | Dateinamen, Variablen, Funktionen    |
| **Largest File Wins**    | ✅          | Bei Konflikten größte Datei behalten |
| **Max Depth**            | 6           | Maximale Verzeichnistiefe            |
| **Unicode Arrow**        | `→`         | Pfeil in Safepoint-Namen (U+2192)    |
| **No Hardcoded Secrets** | ✅          | Nur `.env`-basierte Secrets          |
| **Option-2-Flow**        | ✅          | `opena1 → opena2 → kordp → tool`     |
| **Ports Allowed**        | 12344-12399 | Backend-Ports                        |
| **Ports Forbidden**      | 8080        | UI-only (OpenWebUI)                  |
| **Strict JSON**          | ✅          | `extra="forbid"` in Pydantic         |

---

## 📊 Statistiken

| Metrik              | Wert                                 |
| ------------------- | ------------------------------------ |
| **Anzahl Agenten**  | 21 (opena3-opena21)                  |
| **Running**         | 2 (opena3, opena20)                  |
| **Planned**         | 19                                   |
| **Master-Prompts**  | 19 (opena3-opena21, ohne opena1&2)   |
| **Gesamt LOC**      | ~6.000 Zeilen (geschätzt)            |
| **Generiert durch** | `scripts/generate_master_prompts.py` |

---

## 🔄 Regenerierung

Falls Master-Prompts aktualisiert werden müssen:

```bash
# Generator-Skript bearbeiten
vim scripts/generate_master_prompts.py

# Neu generieren (überschreibt alle Dateien)
python3 scripts/generate_master_prompts.py

# Validierung
find . -maxdepth 2 -name "MASTER_PROMPT.md" | wc -l
# Erwartung: 19
```

---

## 📚 Verwandte Dokumentation

| Dokument                 | Pfad                                 | Zweck                      |
| ------------------------ | ------------------------------------ | -------------------------- |
| **System Overview**      | `SYSTEM_OVERVIEW.md`                 | Komplette Systemerklärung  |
| **Master Prompt**        | `.github/copilot-master-prompt.md`   | Universeller System-Prompt |
| **Completion Checklist** | `.github/copilot-instructions.md`    | Phase 1-3 Tracking         |
| **Generator-Script**     | `scripts/generate_master_prompts.py` | Prompt-Generator           |
| **Agent TODO-Listen**    | `{ordner}/TODO.md`                   | 20 Agent-TODOs             |

---

**Ende des MASTER PROMPTS INDEX.**
**Maintainer:** Danijel Jokic (ELION Team)
**Letzte Aktualisierung:** 27. November 2025
**Status:** ✅ **COMPLETE**
