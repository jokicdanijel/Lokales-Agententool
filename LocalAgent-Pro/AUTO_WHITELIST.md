# 🌐 Auto-Whitelist System - LocalAgent-Pro

**Version:** 1.2  
**Datum:** 16. November 2025

---

## 🎯 Überblick

Das Auto-Whitelist-System erlaubt **alle Domains** mit Wildcard `*` und speichert automatisch jede aufgerufene Domain in einer Whitelist-Datei. So kannst du später:

1. **Schnell arbeiten** - Keine Einschränkungen während der Nutzung
2. **Nachträglich prüfen** - Welche Domains wurden aufgerufen?
3. **Blocklist erstellen** - Basierend auf den gespeicherten Domains
4. **Whitelist verwenden** - Einfach Wildcard `*` entfernen

---

## ⚙️ Konfiguration

### Aktuelle Einstellung (config/config.yaml)

```yaml
allowed_domains:
  - "*"  # Erlaubt ALLE Domains

# Auto-Whitelist: Domains automatisch zur Whitelist hinzufügen
auto_whitelist_enabled: true
auto_whitelist_file: "config/domain_whitelist.yaml"

# Rückfrage bei neuen Domains
ask_before_new_domain: false  # false = alle erlauben, true = nachfragen
```

---

## 🚀 Funktionsweise

### 1. **Wildcard aktiv** (`allowed_domains: ["*"]`)
- ✅ Alle Domains sind erlaubt
- ✅ Keine Blockierung
- ✅ Sofortiger Zugriff

### 2. **Auto-Whitelist speichert**
Jede aufgerufene Domain wird automatisch in `config/domain_whitelist.yaml` gespeichert:

```yaml
approved_domains:
  - 127.0.0.1
  - example.com
  - github.com
  - wikipedia.org
```

### 3. **Whitelist abrufen**
```bash
curl http://127.0.0.1:8001/whitelist
```

**Response:**
```json
{
  "auto_whitelist_enabled": true,
  "wildcard_active": true,
  "approved_domains": [
    "127.0.0.1",
    "example.com",
    "github.com",
    "wikipedia.org"
  ],
  "count": 4,
  "file": "config/domain_whitelist.yaml"
}
```

---

## 📋 Verwendungs-Szenarien

### Szenario 1: **Freies Arbeiten** (aktuell aktiv)

```yaml
# config/config.yaml
allowed_domains:
  - "*"
auto_whitelist_enabled: true
```

**Verhalten:**
- ✅ Alle Domains erlaubt
- ✅ Domains werden automatisch geloggt
- ✅ Keine Unterbrechungen

**Beispiel:**
```bash
# Irgendeine Domain aufrufen
curl -X POST http://127.0.0.1:8001/test \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Lade https://news.ycombinator.com"}'

# Ergebnis: Domain wird geladen UND in domain_whitelist.yaml gespeichert
```

---

### Szenario 2: **Nachträgliche Einschränkung**

Nach dem Arbeiten kannst du die Whitelist prüfen und Wildcard deaktivieren:

1. **Whitelist prüfen:**
   ```bash
   curl http://127.0.0.1:8001/whitelist | jq '.approved_domains'
   ```

2. **Unerwünschte Domains entfernen:**
   ```bash
   # Editiere config/domain_whitelist.yaml
   vim config/domain_whitelist.yaml
   
   # Entferne z.B.:
   # - suspicious-domain.com
   ```

3. **Wildcard deaktivieren:**
   ```yaml
   # config/config.yaml
   allowed_domains:
     - "example.com"
     - "github.com"
     # ... oder Domains aus domain_whitelist.yaml kopieren
   ```

4. **Server neu starten:**
   ```bash
   cd /path/to/LocalAgent-Pro
   ps aux | grep openwebui_agent_server | awk '{print $2}' | xargs kill
   source venv/bin/activate
   nohup python src/openwebui_agent_server.py > logs/server.log 2>&1 &
   ```

**Jetzt:** Nur noch explizit gelistete Domains erlaubt

---

### Szenario 3: **Blocklist erstellen**

Basierend auf der Auto-Whitelist kannst du eine Blocklist erstellen:

1. **Whitelist exportieren:**
   ```bash
   curl http://127.0.0.1:8001/whitelist | jq -r '.approved_domains[]' > all_domains.txt
   ```

2. **Unerwünschte Domains markieren:**
   ```bash
   # Erstelle blocklist.yaml
   cat > config/blocklist.yaml << EOF
   blocked_domains:
     - suspicious-domain.com
     - ads-network.com
     - tracking-site.com
   EOF
   ```

3. **In config.yaml einbinden:**
   ```yaml
   # config/config.yaml
   allowed_domains:
     - "*"
   
   blocked_domains_file: "config/blocklist.yaml"
   block_mode: true  # Blocklist statt Whitelist
   ```

*Hinweis: Blocklist-Modus muss noch im Code implementiert werden - aktuell nur Whitelist*

---

## 🔧 API-Endpoints

### 1. Health Check (mit Whitelist-Info)
```bash
curl http://127.0.0.1:8001/health
```

**Response:**
```json
{
  "status": "ok",
  "allowed_domains": ["*"],
  "auto_whitelist_enabled": true,
  "auto_whitelist_count": 4,
  ...
}
```

### 2. Whitelist abrufen
```bash
curl http://127.0.0.1:8001/whitelist
```

**Response:**
```json
{
  "auto_whitelist_enabled": true,
  "wildcard_active": true,
  "approved_domains": ["127.0.0.1", "example.com", ...],
  "count": 4,
  "file": "config/domain_whitelist.yaml"
}
```

### 3. Test-Endpoint (Domain wird automatisch gespeichert)
```bash
curl -X POST http://127.0.0.1:8001/test \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Lade https://neue-domain.com"}'
```

**Ergebnis:**
- Domain wird geladen
- Domain wird in `domain_whitelist.yaml` gespeichert
- Whitelist-Count erhöht sich

---

## 📊 Monitoring

### Whitelist-Größe überwachen
```bash
# Anzahl Domains in Whitelist
curl -s http://127.0.0.1:8001/whitelist | jq '.count'

# Alle Domains anzeigen
curl -s http://127.0.0.1:8001/whitelist | jq -r '.approved_domains[]'

# Whitelist-Datei direkt lesen
cat config/domain_whitelist.yaml
```

### Logs checken
```bash
# Auto-Whitelist-Aktivitäten
tail -f logs/tool_executions.log | grep "Domain automatisch zur Whitelist"

# Beispiel-Output:
# 2025-11-16 08:30:15 | INFO | LocalAgent-Pro.Tools | fetch | 📝 Domain automatisch zur Whitelist hinzugefügt: github.com
```

---

## 🔒 Sicherheitshinweise

### ⚠️ Wildcard-Modus
- **Aktuell aktiv:** Alle Domains erlaubt
- **Risiko:** Potenziell unsichere Domains können aufgerufen werden
- **Empfehlung:** Nur für Entwicklung/Testing verwenden

### ✅ Produktiv-Modus
Für Produktiv-Umgebungen:

1. **Wildcard deaktivieren:**
   ```yaml
   allowed_domains:
     - "example.com"
     - "github.com"
     - "vertrauenswürdige-domain.com"
   ```

2. **Auto-Whitelist optional:**
   ```yaml
   auto_whitelist_enabled: false  # Keine automatische Speicherung
   ```

3. **Regelmäßig prüfen:**
   ```bash
   # Jeden Tag prüfen welche Domains aufgerufen wurden
   curl http://127.0.0.1:8001/whitelist | jq '.approved_domains'
   ```

---

## 🛠️ Erweiterte Konfiguration

### Whitelist-Datei wechseln
```yaml
# config/config.yaml
auto_whitelist_file: "config/custom_whitelist.yaml"
```

### Rückfrage-Modus (geplant)
```yaml
ask_before_new_domain: true
```

**Verhalten (wenn implementiert):**
- Neue Domain wird erkannt
- System fragt: "Domain XYZ aufrufen? (ja/nein)"
- Bei "ja": Domain wird geladen UND gespeichert
- Bei "nein": Domain wird blockiert

*Hinweis: Aktuell noch nicht implementiert - alle Domains werden direkt erlaubt*

---

## 📝 Workflow-Beispiel

### Tag 1: Freies Arbeiten
```bash
# 1. Config prüfen
cat config/config.yaml | grep "allowed_domains" -A3
# Output: allowed_domains: ["*"]

# 2. Arbeiten - verschiedene Domains aufrufen
# ... über OpenWebUI oder API ...

# 3. Abends: Whitelist prüfen
curl http://127.0.0.1:8001/whitelist | jq '.approved_domains'
# Output: ["127.0.0.1", "github.com", "stackoverflow.com", "wikipedia.org", ...]
```

### Tag 2: Einschränken
```bash
# 1. Whitelist exportieren
curl http://127.0.0.1:8001/whitelist | jq -r '.approved_domains[]' > domains.txt

# 2. Unerwünschte Domains entfernen
vim domains.txt
# Entferne z.B. "ads-domain.com"

# 3. Config aktualisieren
cat domains.txt | awk '{print "  - \""$1"\""}' > temp_domains.txt
# Kopiere Output in config.yaml unter allowed_domains

# 4. Server neu starten
ps aux | grep openwebui_agent_server | awk '{print $2}' | xargs kill
source venv/bin/activate
nohup python src/openwebui_agent_server.py > logs/server.log 2>&1 &

# 5. Test: Nur noch gelistete Domains erlaubt
curl -X POST http://127.0.0.1:8001/test \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Lade https://neue-nicht-gelistete-domain.com"}'
# Output: "🚫 Domain blockiert"
```

---

## 🔄 Zusammenfassung

| Modus | Config | Verhalten |
|-------|--------|-----------|
| **Wildcard + Auto-Whitelist** (aktuell) | `allowed_domains: ["*"]`<br>`auto_whitelist_enabled: true` | Alle Domains erlaubt<br>Automatische Speicherung |
| **Nur Wildcard** | `allowed_domains: ["*"]`<br>`auto_whitelist_enabled: false` | Alle Domains erlaubt<br>Keine Speicherung |
| **Strikte Whitelist** | `allowed_domains: ["domain1.com", ...]`<br>`auto_whitelist_enabled: false` | Nur gelistete Domains<br>Keine Speicherung |
| **Whitelist + Auto-Expand** | `allowed_domains: ["domain1.com", ...]`<br>`auto_whitelist_enabled: true` | Nur gelistete + gespeicherte<br>Neue Domains werden gespeichert |

---

## 💡 Best Practices

1. **Development:** Wildcard + Auto-Whitelist (aktuell)
2. **Testing:** Whitelist aus Auto-Whitelist übernehmen
3. **Production:** Strikte Whitelist ohne Wildcard
4. **Audit:** Regelmäßig `domain_whitelist.yaml` prüfen

---

**Status:** ✅ Auto-Whitelist aktiv  
**Whitelist-Datei:** `config/domain_whitelist.yaml`  
**API-Endpoint:** `GET /whitelist`

