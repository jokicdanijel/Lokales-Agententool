# 5.opena6_browser

Browser-Automation · Scraping · DOM-Interaktion
Local Execution Agent (Teil des Gesamtprojekts)

## Übersicht

Der Browser-Agent dient zur lokalen Automatisierung von Webseiten.
Er wird ausschließlich durch das Portier-System (`1.opena1&2_portier`) angesteuert und führt Aktionen wie Öffnen, Klicken, Schreiben und Extrahieren aus.

## Hauptfunktionen

- Webseiten öffnen
- Buttons klicken
- Formulare ausfüllen
- HTML extrahieren
- Text extrahieren
- DOM-Abfragen (Selectors)
- Scroll-Events
- Screenshots

## Datenfluss (Option-2-Flow)

```
opena1 → Decision72 → CMD → opena2 (Safepoint CMD)
→ 5.opena6_browser (Ausführung)
→ opena2 (Safepoint RESP) → opena1 → User
```

## CMD-Schema

Der Agent akzeptiert strikt das JSON-Schema `BrowserAgentCMD`.

Siehe: `CMD_SCHEMA.md`

## Sicherheit

- Keine Ausführung von nicht autorisierten Scripts
- Keine Fantasieaktionen
- Absolute Trackbarkeit via archivp_store

## config.json

Die Modulkonfiguration befindet sich unter `config.json`.
