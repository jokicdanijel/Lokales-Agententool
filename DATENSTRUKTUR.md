# 🗂️ Datenstruktur des ELION-Systems

**Detaillierte Dokumentation der Datenmodelle und Persistierung**

- 📅 **Datum:** 24. November 2025
- 🎯 **Zweck:** Referenz für Backend-Entwickler und Datenbank-Architekten
- 📍 **Scope:** Nur Abschnitt 1 aus `ELION_SYSTEM_ARCHITECTURE.md`

---

## Datenstruktur

Die Datenstruktur des OpenWebUI-Portier-Systems ist multidimensional aufgebaut und verbindet mehrere Domänen: das OpenWebUI-Frontend, den LocalAgent-Pro-Backend-Server, die Portier-Architektur (Koordinator, Archivator, Connector) sowie externe Integrationen (Telegram, GitHub).

### Persistente Datenspeicherung

Das System nutzt mehrschichtige Persistence:

- **SQLite-Datenbanken**: Strukturierte Event-Daten und Safepoints in `1.opena1&2_portier/archivp_store/`
- **JSON-Dateien**: Konfigurationsdaten und Zustandsdaten in `LocalAgent-Pro/sandbox/`
- **JSONL-Indexdateien**: Sequenzielle Safepoint-Protokollierung in `index.jsonl`
- **Audit-Logs**: Transaktions- und Prüf-Logs in `/logs/` und `audit_hashes.log`
- **Prometheus-Metriken**: Monitoring und Performance-Daten

### Kern-Datenentitäten und Beziehungen

| Entität | Beschreibung | Beziehungen | Speicherort |
|---------|------------|-----------|-----------|
| **Endpoint** (20) | Services auf Port 12344–12399 (opena1–opena20) | Hat viele HealthRecords; wird gepatcht via PatchBlock | SQLite, .env |
| **PatchBlock** | Unified-Diff-Patches für Code-Updates | Gehört zu Endpoint; wird geauditet in AuditLog | `patches/` Verzeichnis |
| **Safepoint** | Transaktions-Checkpoints (Gateway, Tool-Execution, Archive-Access) | Ist Teil von MessageRelay/GitHubWebhook-Flow | `archivp_store/index.jsonl` |
| **HealthRecord** | Zeitstempel-basierte Gesundheitsprüfungen | Ist von Endpoint; Zeitreihen-Metadaten | SQLite, `/logs/` |
| **AuditLog** | SHA-256 Hash-Ketten für alle Änderungen | Referenziert Endpoint & PatchBlock; vollständig verfolgbar | `audit_hashes.log` |
| **Voice-Program-Daten** | Notizen, Kontakte, Aufgaben, Transkripte (1.041 Zeilen, 6 Programme) | Persistent in JSON | `LocalAgent-Pro/sandbox/` |
| **MessageRelay** | Telegram → OpenWebUI Nachrichten-Routing | Wird zu Safepoint; loggt in archive.db | opena3 Bridge |
| **GitHubWebhook** | GitHub-Events (Push, PR, Release) | Wird zu Safepoint; triggert optionale Updates | opena3 Bridge |

### Datentypen und Formate

Das System arbeitet hauptsächlich mit:

- **JSON** – REST-API-Responses, Konfigurationen, Voice-Daten
- **YAML** – `config.yaml` für Konfigurationsdateien
- **Unified-Diff** – Patch-Format für Code-Updates
- **SHA-256 Hashes** – Audit-Trails und Integrität
- **SQLite** – Relational für strukturierte Daten
- **JSONL** – Log-Streaming für sequenzielle Events

Alle Daten sind **UTF-8 kodiert** und nutzen **ISO-8601 Zeitstempel**.

---

## 🔗 Weiterführende Dokumentation

- **Gesamtübersicht:** `../ELION_SYSTEM_ARCHITECTURE.md`
- **Datenpfad:** `DATENPFAD.md`
- **Projektstruktur:** `PROJEKTSTRUKTUR.md`

---

**Letztes Update:** 24. November 2025
