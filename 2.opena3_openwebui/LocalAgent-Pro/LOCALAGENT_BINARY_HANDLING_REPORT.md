# LocalAgent-Pro – Binary-Handling Fix (githubcli-archive-keyring.gpg Problem)

**Datum:** 2025-12-01
**Status:** ✅ Implementiert

---

## 1. Problembeschreibung

### IST-Zustand (vor dem Fix)

Wenn LocalAgent-Pro eine URL mit **Binärdaten** abrief (z.B. GPG-Keys, ZIP-Dateien, Bilder), wurde der **rohe Binärinhalt als Text in den Chat** ausgegeben. Das führte zu:

- Unlesbarem "Zeichensalat" (kryptische Zeichen, Base64-artiger Müll)
- Schlechter User Experience
- Unnötig großen Chat-Nachrichten
- Potentiellen Encoding-Problemen

**Beispiel-URL mit Problem:**

```
https://cli.github.com/packages/githubcli-archive-keyring.gpg
```

---

## 2. Lösung (SOLL-Zustand)

### Neues Verhalten

| Content-Type              | Behandlung                                   |
| ------------------------- | -------------------------------------------- |
| `text/*`, `*html*`        | Inhalt als Text ausgeben (max. 8000 Zeichen) |
| `application/json`        | JSON hübsch formatiert ausgeben              |
| **Alles andere (Binary)** | Datei lokal speichern, nur Metadaten im Chat |

### Binary-Download Ausgabe (neu)

```
🌐 Binary-Download erfolgreich

• URL: https://cli.github.com/packages/githubcli-archive-keyring.gpg
• MIME-Type: application/pgp-keys
• Dateiname: githubcli-archive-keyring.gpg
• Größe: 2.2 KB
• Speicherort: localagent_sandbox/downloads/githubcli-archive-keyring.gpg

Hinweis: Das ist eine Binärdatei. Der Inhalt wurde lokal gespeichert und nicht im Chat angezeigt.
```

---

## 3. Geänderte Dateien

| Datei                            | Änderung                                                     |
| -------------------------------- | ------------------------------------------------------------ |
| `src/openwebui_agent_server.py`  | `classify_content_type()` hinzugefügt                        |
| `src/openwebui_agent_server.py`  | `get_filename_from_response()` hinzugefügt                   |
| `src/openwebui_agent_server.py`  | `format_file_size()` hinzugefügt                             |
| `src/openwebui_agent_server.py`  | `fetch_webpage()` komplett überarbeitet                      |
| `src/openwebui_agent_server.py`  | `format_tool_result()` hinzugefügt                           |
| `src/openwebui_agent_server.py`  | `chat_completions()` Response-Formatting angepasst           |
| `config/config.yaml`             | Domain-Whitelist erweitert um `cli.github.com`, `github.com` |
| `tests/test_web_fetch_binary.py` | **NEU:** Unit-Tests für Binary-Handling                      |

---

## 4. Neue Funktionen

### `classify_content_type(content_type: str) -> str`

Klassifiziert Content-Type in `"text"`, `"json"` oder `"binary"`.

### `get_filename_from_response(response, url: str) -> str`

Extrahiert Dateinamen aus:

1. `Content-Disposition` Header (falls vorhanden)
2. URL-Pfad (Fallback)
3. Timestamp-basierter Name (letzter Fallback)

### `format_file_size(size_bytes: int) -> str`

Formatiert Dateigröße menschenlesbar (B, KB, MB).

### `format_tool_result(tool_result: dict) -> str`

Intelligenter Formatter für Tool-Ergebnisse:

- Binary: Nur saubere Zusammenfassung
- JSON: Hübsch formatiert mit Syntax-Highlighting
- Text: Standard mit Metadaten
- Fehler: Klare Fehlermeldung

---

## 5. Speicherort für Downloads

```
~/localagent_sandbox/downloads/
```

- Wird automatisch erstellt falls nicht vorhanden
- Bei Namenskollisionen: Timestamp wird angehängt
- Pfade sind sandbox-relativ (Sicherheit)

---

## 6. Tests

### Unit-Tests

```bash
cd LocalAgent-Pro
pytest tests/test_web_fetch_binary.py -v
```

### Manuelle Verifikation

**Vorher (IST):**

```
User: Hole https://cli.github.com/packages/githubcli-archive-keyring.gpg
Agent: Tool executed: {"status": "success", "content": "¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿...[unlesbarer Müll]"}
```

**Nachher (SOLL):**

```
User: Hole https://cli.github.com/packages/githubcli-archive-keyring.gpg
Agent: 🌐 Binary-Download erfolgreich

• URL: https://cli.github.com/packages/githubcli-archive-keyring.gpg
• MIME-Type: application/pgp-keys
• Dateiname: githubcli-archive-keyring.gpg
• Größe: 2.2 KB
• Speicherort: localagent_sandbox/downloads/githubcli-archive-keyring.gpg

Hinweis: Das ist eine Binärdatei. Der Inhalt wurde lokal gespeichert und nicht im Chat angezeigt.
```

---

## 7. Sicherheitsaspekte

- ✅ Keine neuen externen Abhängigkeiten
- ✅ Nur Standardbibliothek verwendet (`pathlib`, `json`, `re`)
- ✅ Pfade bleiben innerhalb der Sandbox
- ✅ Domain-Whitelist weiterhin aktiv
- ✅ Keine Secrets in Logs
- ✅ `shell_execution.enabled` unverändert

---

## 8. Limitierungen

| Limitation    | Beschreibung                                            |
| ------------- | ------------------------------------------------------- |
| Große Dateien | Keine spezielle Behandlung für >100MB Downloads         |
| Streaming     | Downloads erfolgen komplett in Memory vor dem Speichern |
| Cleanup       | Keine automatische Bereinigung alter Downloads          |

---

## 9. Deployment

Nach dem Fix muss der LocalAgent-Pro Server neu gestartet werden:

```bash
cd LocalAgent-Pro
./start.sh
# oder
python src/openwebui_agent_server.py
```

---

**Autor:** GitHub Copilot
**Review:** Pending
**Version:** 1.0.0
