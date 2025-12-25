# Systemdaten: hyper_dashboard — 2025-12-24 (Europe/Vienna)

## METADATA
- **System:** hyper_dashboard
- **Env:** prod
- **Owner:** Dani
- **Repo/Path:** /srv/hyper_dashboard
- **Datum:** 2025-12-24 (Europe/Vienna)

## QUICK STATUS
- **Open Items**
  - (H) Pfad/Ort der `routing_event_matrix.md`
  - (M) Ref/Ort/Commit von `config/nginx.conf`
  - (L) Artefakt/Logpfad oder Incident‑Snippet (ohne Secrets)

## INDEX / INVENTORY
- Components/Services/Hosts:
  - OpenWebUI (upstream)
- Docs/Artefakte/Refs:
  - routing_event_matrix.md
  - config/nginx.conf
  - Vault kv/hyper_dashboard/api_token (REDACTED)
  - /srv/hyper_dashboard

## FACTS (ACTIVE ONLY)
- system_name : **hyper_dashboard**
- env : **prod**
- owner : **Dani**
- API_PORT : **8080** (basis=P1, ref=config/nginx.conf)
- upstream_service : **OpenWebUI**
- incident_window : 03:10–03:12
- token_store : Vault kv/hyper_dashboard/api_token (REDACTED)
- validation_status : healthcheck ok; api calls ok

## LOGS / CHANGE / INCIDENT / DECISIONS
- **CHANGE LOG**
  - CHG-001 Port-Policy Hinweis ergänzt (count=2)

- **INCIDENT LOG**
  - INC-001 UI hing gelegentlich ~2 Minuten; upstream OpenWebUI (count=2)

- **DECISION LOG**
  - DEC-001 CORRECT: API_PORT=8080 (count=1)

- **SECURITY LOG**
  - SEC-001 API Token rotiert; alter invalidiert; validation ok (count=2)
  - SEC-002 Rechte für bot_user angepasst (count=1)

- **OBS / DOC**
  - DOC-001 routing_event_matrix.md verlinkt (count=1)
  - OBS-001 Warn-Log "timeout upstream" gesehen (count=1)

## CONFLICTS
- API_PORT | 3000 vs 8080 | ACTIVE=8080 | basis=P1 | ref=config/nginx.conf

## OPEN ITEMS (ACTIONS)
1. (H) **Pfad/Ort von `routing_event_matrix.md`**
   - Aktion: Repo + `/srv/hyper_dashboard` durchsuchen, Pfad/Commit dokumentieren oder Vorlage erstellen.
   - Owner: @Dani
   - Aufwand: 15–60 min

2. (M) **Ref/Ort/Commit von `config/nginx.conf`**
   - Aktion: Commit SHA notieren, server listen prüfen (Port), bei Abweichung Issue eröffnen.
   - Owner: Infra / @Dani
   - Aufwand: 15–60 min

3. (L) **Artefakt/Logpfad oder Incident‑Snippet**
   - Aktion: anonymisierten Log‑Snippet (03:10–03:12) sammeln und in `logs/` ablegen oder im Report verlinken.
   - Owner: On‑Call / @Dani
   - Aufwand: 30–120 min

---

## APPENDIX
- Referenzen:
  - /srv/hyper_dashboard
  - config/nginx.conf
  - Vault kv/hyper_dashboard/api_token (REDACTED)

*Erstellt automatisch — bitte Issues anlegen oder die oben genannten Aufgaben zuweisen, falls gewünscht.*
