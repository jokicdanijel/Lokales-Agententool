

````markdown
# 🖥️ OpenWebUI – Docker-Bundle mit Ollama‑Integration

Dieses Bundle startet OpenWebUI via Docker Compose und bindet automatisch die lokale Ollama-API (`http://127.0.0.1:11434`) ein.

---

## 📦 Voraussetzungen

- **Docker Engine** und **Docker Compose Plugin**
  ```bash
  sudo apt install docker.io docker-compose-plugin
````

* **Ollama muss lokal laufen**:

  ```bash
  systemctl status ollama
  ```

---

## 🚀 Schnellstart

```bash
./start.sh
```

* Danach im Browser öffnen: [http://localhost:3000](http://localhost:3000)
* Alternativ kannst du den Port in `docker-compose.yml` anpassen (`3000:8080` → z. B. `8080:8080`)

---

## 🛠️ Wichtige Dateien

| Datei                | Zweck                                 |
| -------------------- | ------------------------------------- |
| `start.sh`           | Startet den Container im Hintergrund  |
| `status.sh`          | Zeigt den aktuellen Status an         |
| `stop.sh`            | Stoppt und entfernt den Container     |
| `docker-compose.yml` | Konfiguration von OpenWebUI und Ports |

---

## 🔧 Anpassungen

* **Port ändern** in `docker-compose.yml`:

  ```yaml
  ports:
    - "8080:8080"  # oder "3000:8080", je nach Wunsch
  ```

* **Authentifizierung abschalten** (bereits gesetzt in `environment`):

  ```yaml
  - WEBUI_AUTH=False
  ```

* **Persistente Daten** liegen im Docker-Volume:

  ```
  openwebui_data
  ```

---

## 🧪 Test & Fehlerhilfe

* **Logs anzeigen:**

  ```bash
  docker logs -f open-webui
  ```

* **Erreichbarkeit prüfen:**

  * `http://localhost:3000` oder `http://localhost:8080` (je nach Konfiguration)
  * Container läuft? → `docker ps`

* **Image-Fehler?**
  Falls beim Start ein „repository does not exist“ erscheint:
  → Stelle sicher, dass in `docker-compose.yml` folgendes Image verwendet wird:

  ```yaml
  image: ghcr.io/open-webui/open-webui:main
  ```

---

## ✅ Beispiel für korrekte `docker-compose.yml`

```yaml
version: "3.8"

services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - "3000:8080"
    environment:
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
      - WEBUI_AUTH=False
    volumes:
      - openwebui_data:/app/backend/data
    restart: unless-stopped

volumes:
  openwebui_data:
```

---

Wenn du den Port auf `8080` umstellst und keinen Proxy verwendest, kannst du direkt unter [http://localhost:8080](http://localhost:8080) zugreifen.



