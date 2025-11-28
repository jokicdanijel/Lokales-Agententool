# 📚 README-Struktur des Gesamtprojekts

**Letzte Aktualisierung:** 28. November 2025  
**Status:** ✅ Konsolidiert

---

## 🎯 Übersicht

Dieses Dokument zeigt die **offizielle README-Struktur** für alle Agent-Module des ELION/PORTIER 2.0 Systems.

**Regel:** Jedes Hauptverzeichnis hat **genau eine gültige README.md**. Alle anderen README-Dateien sind als `_DEPRECATED` markiert.

---

## 📖 Gültige README-Dateien

### Kern-Infrastructure

| Verzeichnis | Gültige README | Beschreibung |
|-------------|----------------|--------------|
| **`/`** (Root) | [`README.md`](./README.md) | Haupt-Projektübersicht (PORTIER 3.0) |
| **`1.opena1&2_portier/`** | [`README.md`](./1.opena1&2_portier/README.md) | opena1 (Koordinator) + opena2 (Archivator) |
| **`2.opena3_openwebui/`** | [`README.md`](./2.opena3_openwebui/README.md) | OpenWebUI Terminal Agent (✅ Production) |
| **`3.opena4_telegram/`** | [`README.md`](./3.opena4_telegram/README.md) | Telegram Bot Agent |
| **`4.opena5_vscode/`** | [`README.md`](./4.opena5_vscode/README.md) | VS Code Integration |
| **`5.opena6_browser/`** | [`README.md`](./5.opena6_browser/README.md) | Browser Automation |
| **`6.opena7_email/`** | [`README.md`](./6.opena7_email/README.md) | E-Mail Client |
| **`7.opena8_whatsapp/`** | [`README.md`](./7.opena8_whatsapp/README.md) | WhatsApp API |
| **`8.opena9_telephone/`** | [`README.md`](./8.opena9_telephone/README.md) | Telefonie Agent |
| **`9.opena10_call_tracking/`** | [`README.md`](./9.opena10_call_tracking/README.md) | Call Tracking |
| **`10.opena11_unlock/`** | [`README.md`](./10.opena11_unlock/README.md) | Unlock Master |
| **`11.opena12_social_media/`** | [`README.md`](./11.opena12_social_media/README.md) | Social Media |
| **`12.opena13_influencer/`** | [`README.md`](./12.opena13_influencer/README.md) | Influencer |
| **`13.opena14_calendar/`** | [`README.md`](./13.opena14_calendar/README.md) | Calendar Agent |
| **`14.opena15_html/`** | [`README.md`](./14.opena15_html/README.md) | HTML Creator |
| **`15.opena16_shop/`** | [`README.md`](./15.opena16_shop/README.md) | Shop Creator |
| **`16.opena17_homepagecreator/`** | [`README.md`](./16.opena17_homepagecreator/README.md) | Homepage Creator |
| **`17.opena18_CMR/`** | [`README.md`](./17.opena18_CMR/README.md) | CRM Agent |
| **`18.opena19_Aktien&Crypto/`** | [`README.md`](./18.opena19_Aktien&Crypto/README.md) | Aktien & Crypto |
| **`19.opena20_dashboard_agent/`** | [`README.md`](./19.opena20_dashboard_agent/README.md) | Dashboard Agent |
| **`20.opena21_workflow/`** | [`README.md`](./20.opena21_workflow/README.md) | Workflow Engine (✅ Production) |

---

## ⚠️ Veraltete README-Dateien (Deprecated)

Diese Dateien sind **nicht mehr aktuell** und wurden umbenannt:

| Veraltete Datei | Status | Verweis auf |
|-----------------|--------|-------------|
| `1.opena1&2_portier/README_APIS_DEPRECATED.md` | ❌ Veraltet | [`README.md`](./1.opena1&2_portier/README.md) |
| `2.opena3_openwebui/README_COMPLETE_DEPRECATED.md` | ❌ Veraltet | [`README.md`](./2.opena3_openwebui/README.md) |

**Hinweis:** Alle `_DEPRECATED.md` Dateien enthalten einen Header mit Verweis auf die aktuelle README.

---

## 📁 Spezielle Dokumentation

### Root-Level Dokumente

| Datei | Zweck |
|-------|-------|
| [`README.md`](./README.md) | Haupt-Projektübersicht (PORTIER 3.0) |
| [`README_ENTERPRISE.md`](./README_ENTERPRISE.md) | Enterprise-Dokumentation (vollständig) |
| [`README_STRUCTURE.md`](./README_STRUCTURE.md) | Diese Datei (README-Übersicht) |
| [`.github/copilot-master-prompt.md`](./.github/copilot-master-prompt.md) | Vollständiges System-Wissen |
| [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) | AI Integration Guide |

### Dokumentationsordner

| Verzeichnis | Inhalt |
|-------------|--------|
| **`docs/`** | Operations, API-Docs, Troubleshooting |
| **`reports/`** | Security Audits, GitHub Reviews |
| **`configs/`** | Konfigurationsdateien (Agenda, Tools) |

---

## 🔄 Wartung & Updates

### Regel für neue README-Dateien

1. **Ein README pro Hauptverzeichnis:** Jedes Agent-Verzeichnis (`X.openaY_name/`) hat genau **eine** `README.md`
2. **Keine Duplikate:** Alte oder zusätzliche READMEs werden als `*_DEPRECATED.md` markiert
3. **Deprecation-Header:** Jede deprecated Datei enthält:

   ```markdown
   # ⚠️ VERALTET / DEPRECATED
   **Diese Datei ist veraltet und wird nicht mehr aktualisiert.**
   **Bitte verwende stattdessen:** [`README.md`](./README.md)
   ```

### Update-Workflow

Wenn du eine README aktualisieren willst:

1. **Öffne die gültige README.md** im entsprechenden Verzeichnis
2. **Bearbeite nur diese Datei**
3. **Ignoriere alle `_DEPRECATED.md` Dateien**
4. **Aktualisiere das Datum** im Header (z.B. "Letzte Aktualisierung: 27. November 2025")

---

## 🚀 Quick Navigation

### Für Entwickler

- **Backend-Architektur:** [`1.opena1&2_portier/README.md`](./1.opena1&2_portier/README.md)
- **OpenWebUI Integration:** [`2.opena3_openwebui/README.md`](./2.opena3_openwebui/README.md)
- **Dashboard:** [`19.opena20_dashboard_agent/README.md`](./19.opena20_dashboard_agent/README.md)

### Für AI/Copilot

- **Vollständiges Wissen:** [`.github/copilot-master-prompt.md`](./.github/copilot-master-prompt.md)
- **Integration Guide:** [`.github/copilot-instructions.md`](./.github/copilot-instructions.md)

### Für Operations

- **Stack starten:** [`docs/OPERATIONS.md`](./docs/OPERATIONS.md)
- **Troubleshooting:** [`docs/TROUBLESHOOTING.md`](./docs/TROUBLESHOOTING.md)

---

## 📊 Statistik

| Kategorie | Anzahl |
|-----------|--------|
| **Gültige READMEs** | 22 (1 Root + 21 Agents) |
| **Deprecated READMEs** | 2 |
| **Zusätzliche Docs** | 5+ (docs/, reports/, configs/) |
| **Gesamt Markdown-Dateien** | 100+ |

---

## ✅ Validierung

**Letzte Prüfung:** 28. November 2025 (aktuell)

```bash
# Alle gültigen READMEs prüfen
for i in {1..21}; do
  if [ -d "${i}.*" ]; then
    ls -la ${i}.*/README.md 2>/dev/null || echo "❌ Missing: ${i}.*"
  fi
done

# Deprecated READMEs prüfen
find . -maxdepth 2 -name "*_DEPRECATED.md" -type f
```

**Status:** ✅ Alle gültigen READMEs vorhanden, Deprecated-Dateien markiert

---

**Maintainer:** ELION Team  
**Letzte Aktualisierung:** 28. November 2025  
**Version:** 1.1
