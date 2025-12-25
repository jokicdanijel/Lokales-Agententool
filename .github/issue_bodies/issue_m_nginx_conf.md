**Beschreibung**
Referenz/Commit von `config/nginx.conf` fehlt; es besteht ein Port‑Konflikt (3000 vs 8080) in den Reports.

**Aufgaben / Nächste Schritte**
- Suche `config/nginx.conf` im Repo und auf `/srv/hyper_dashboard`
- Notiere Commit SHA und prüfe `server { listen ... }`
- Bestätige Port (`8080`) oder öffne ein Issue/PR zur Korrektur

**Priority:** Medium
**Owner:** @jokicdanijel
**Akzeptanzkriterien:** Commit‑SHA im Report + Vermerk "Port=8080 (bestätigt)" oder offener PR.
