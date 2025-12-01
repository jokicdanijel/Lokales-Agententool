# Browser Agent - OpenWebUI Tool Installation

## 🎯 Schnellstart (3 Schritte)

### 1️⃣ Tool Server starten
```bash
cd LocalAgent-Pro/opena6
python3 tool_server.py --host 0.0.0.0 --port 8765
```

### 2️⃣ OpenWebUI öffnen
```
http://192.168.0.70:3000
```

### 3️⃣ Tool importieren
```
Admin → Settings → Tools → "+" → URL eingeben:
http://192.168.0.70:8765/manifest
```

✅ **Fertig!** Browser Agent ist jetzt in deinen Chats verfügbar.

---

## 📦 Dateien

| Datei | Zweck |
|-------|-------|
| `tool_server.py` | HTTP Server (Port 8765) |
| `start_tool_server.sh` | Start Script |
| `browser_agent_tool.py` | OpenWebUI-kompatibles Tool |
| `openapi.json` | OpenAPI 3.0 Spezifikation |
| `tool_manifest.json` | Tool Definition (JSON) |

---

## 🔗 URLs

```
Dashboard:    http://192.168.0.70:8765/
Manifest:     http://192.168.0.70:8765/manifest
Health:       http://192.168.0.70:8765/health
OpenAPI:      http://192.168.0.70:8765/openapi.json
```

---

## 💻 Test Commands

```bash
# Health check
curl http://192.168.0.70:8765/health | jq

# Manifest
curl http://192.168.0.70:8765/manifest | jq

# Test action
curl -X POST http://192.168.0.70:8765/execute \
  -H "Content-Type: application/json" \
  -d '{"action":"open","url":"https://example.com"}'
```

---

## 🎨 9 Browser Actions

```
1. open            - Website öffnen
2. click           - Element klicken
3. type            - Text eingeben
4. extract_text    - Text extrahieren
5. extract_html    - HTML extrahieren
6. query_selector  - DOM analysieren
7. screenshot      - Screenshot
8. scroll          - Scrolle Seite
9. wait_for        - Warte auf Element
```

---

## 📚 Beispiel Prompts in OpenWebUI

```
1. "Öffne https://example.com"
2. "Zeige mir den Text von der h1 auf der Seite"
3. "Mache einen Screenshot von https://github.com"
4. "Klicke auf den Submit Button"
5. "Extrahiere alle Links von der Seite"
```

---

## ✅ Checkliste

- [ ] Tool Server läuft (`http://192.168.0.70:8765/health` antwortet)
- [ ] Browser Agent online (`http://192.168.0.70:12350/health` antwortet)
- [ ] OpenWebUI verfügbar (`http://192.168.0.70:3000`)
- [ ] Tool in OpenWebUI importiert
- [ ] Test-Prompt funktioniert

---

**Status**: 🟢 PRODUCTION READY
