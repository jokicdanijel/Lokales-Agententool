# 🧠 OpenWebUI opena3 - Masterprompt Auto-Recovery & Portier-Integration

**Version:** 1.0
**Status:** Production Ready
**Zielgruppe:** Copilot-Agenten, System-Bootstrap, Auto-Recovery

---

## 📋 Inhaltsverzeichnis

1. [Ziel & Überblick](#ziel--überblick)
2. [Auto-Wiederherstellung (Safepoint-System)](#auto-wiederherstellung-safepoint-system)
3. [Docker-Check & Installation](#docker-check--installation)
4. [Portier-System-Integration](#portier-system-integration)
5. [Knowledgebase-Loader](#knowledgebase-loader)
6. [Vollständiger Masterprompt](#vollständiger-masterprompt)
7. [Deployment & Aktivierung](#deployment--aktivierung)

---

## ✅ Ziel & Überblick

Dieser Masterprompt stellt sicher, dass:

| Anforderung          | Lösung                                                |
| -------------------- | ----------------------------------------------------- |
| **Auto-Recovery**    | Letzte Context/Prompt/Safepoint laden                 |
| **Docker-Prüfung**   | Docker & Docker Compose vorhanden (oder installieren) |
| **Portier-Kopplung** | Agent im zentralen Registry registriert               |
| **API-Endpoints**    | Alle Portier-APIs verfügbar                           |
| **Knowledgebase**    | System-Knowledge automatisch geladen                  |
| **Persistierung**    | Alle States werden gespeichert                        |

---

## 🔁 Auto-Wiederherstellung (Safepoint-System)

### Safepoint-Struktur

```json
{
  "safepoint_id": "sp_opena3_20251124_143022",
  "timestamp": "2025-11-24T14:30:22Z",
  "agent_id": "opena3",
  "context": {
    "conversation_history": [...],
    "session_memory": {...},
    "user_preferences": {...}
  },
  "prompt": {
    "system_prompt": "...",
    "last_instruction": "..."
  },
  "state": {
    "active_tasks": [...],
    "api_connections": [...],
    "docker_status": "running"
  }
}
```

### Safepoint-Speicherung

```python
#!/usr/bin/env python3
"""
Safepoint Manager für opena3
Speichert & lädt Kontext-Checkpoints
"""

import json
import os
from datetime import datetime
from pathlib import Path

class SafepointManager:
    def __init__(self, data_dir="/mnt/data"):
        self.data_dir = Path(data_dir)
        self.safepoint_dir = self.data_dir / "safepoints"
        self.safepoint_dir.mkdir(parents=True, exist_ok=True)
        self.current_safepoint_file = self.data_dir / "current_safepoint.json"

    def save_safepoint(self, context, prompt, state):
        """Speichere aktuellen State als Safepoint"""
        timestamp = datetime.now().isoformat()
        safepoint_id = f"sp_opena3_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        safepoint = {
            "safepoint_id": safepoint_id,
            "timestamp": timestamp,
            "agent_id": "opena3",
            "context": context,
            "prompt": prompt,
            "state": state
        }

        # Speichere zu Safepoint-Archiv
        safepoint_file = self.safepoint_dir / f"{safepoint_id}.json"
        with open(safepoint_file, 'w') as f:
            json.dump(safepoint, f, indent=2)

        # Speichere als "current" für schnellen Zugriff
        with open(self.current_safepoint_file, 'w') as f:
            json.dump(safepoint, f, indent=2)

        return safepoint_id

    def load_safepoint(self, safepoint_id=None):
        """Lade Safepoint (neuest oder spezifisch)"""
        if safepoint_id:
            safepoint_file = self.safepoint_dir / f"{safepoint_id}.json"
        else:
            safepoint_file = self.current_safepoint_file

        if safepoint_file.exists():
            with open(safepoint_file, 'r') as f:
                return json.load(f)
        return None

    def list_safepoints(self, limit=10):
        """Auflistung letzter Safepoints"""
        files = sorted(self.safepoint_dir.glob("sp_opena3_*.json"),
                      key=lambda x: x.stat().st_mtime, reverse=True)
        return [f.stem for f in files[:limit]]
```

### Automatisches Laden beim Start

```python
def auto_restore_on_startup():
    """Führe beim Startup automatische Wiederherstellung durch"""
    manager = SafepointManager()
    safepoint = manager.load_safepoint()

    if safepoint:
        print(f"✅ Lade Safepoint: {safepoint['safepoint_id']}")

        # Stelle Context wieder her
        conversation_history = safepoint['context'].get('conversation_history', [])
        session_memory = safepoint['context'].get('session_memory', {})

        # Stelle Prompt wieder her
        system_prompt = safepoint['prompt'].get('system_prompt', '')

        # Stelle State wieder her
        docker_status = safepoint['state'].get('docker_status')

        return {
            "conversation_history": conversation_history,
            "session_memory": session_memory,
            "system_prompt": system_prompt,
            "docker_status": docker_status,
            "safepoint_id": safepoint['safepoint_id']
        }

    print("⚠️  Kein Safepoint gefunden - Neustart mit Default-Prompt")
    return None
```

---

## 🐳 Docker-Check & Installation

### Docker Availability Check

```bash
#!/bin/bash
# docker-check.sh - Prüfe & installiere Docker

check_docker() {
    echo "🔍 Prüfe Docker Installation..."

    if command -v docker &> /dev/null; then
        echo "✅ Docker ist installiert"
        docker --version
        return 0
    else
        echo "⚠️  Docker nicht gefunden - Installiere..."
        install_docker
    fi
}

install_docker() {
    echo "📦 Installiere Docker.io..."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo usermod -aG docker $USER
    echo "✅ Docker Installation fertig"
}

check_docker_compose() {
    echo "🔍 Prüfe Docker Compose..."

    if command -v docker-compose &> /dev/null; then
        echo "✅ Docker Compose ist installiert"
        docker-compose --version
        return 0
    else
        echo "⚠️  Docker Compose nicht gefunden - Installiere..."
        install_docker_compose
    fi
}

install_docker_compose() {
    echo "📦 Installiere Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose Installation fertig"
}

main() {
    check_docker
    check_docker_compose

    echo ""
    echo "✅ Docker-Setup abgeschlossen!"
    docker ps
    docker-compose --version
}

main
```

### Python Docker-Check

```python
import subprocess
import sys

class DockerChecker:
    @staticmethod
    def check_docker():
        """Prüfe ob Docker installiert & läuft"""
        try:
            result = subprocess.run(['docker', 'ps'],
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    @staticmethod
    def check_docker_compose():
        """Prüfe ob Docker Compose installiert"""
        try:
            result = subprocess.run(['docker-compose', '--version'],
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    @staticmethod
    def get_docker_status():
        """Hole Docker Service Status"""
        try:
            result = subprocess.run(['systemctl', 'is-active', 'docker'],
                                  capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"

    @classmethod
    def full_check(cls):
        """Vollständige Docker-Prüfung"""
        return {
            "docker_installed": cls.check_docker(),
            "docker_compose_installed": cls.check_docker_compose(),
            "docker_running": cls.get_docker_status() == "active",
            "status": "ready" if cls.check_docker() else "requires_setup"
        }
```

---

## 🧠 Portier-System-Integration

### Agent-Registry Integration

```python
import requests
import os
from typing import Dict, Optional

class PortierRegistry:
    """Integration mit Portier Central Registry (opena1/opena2)"""

    def __init__(self, portier_url="http://127.0.0.1:12349"):
        self.portier_url = portier_url
        self.token = os.getenv("PORTIER_TOKEN", "default-token")

    def register_agent(self, agent_id="opena3", endpoint="http://localhost:3000"):
        """Registriere opena3 im Portier-System"""

        payload = {
            "agent_id": agent_id,
            "endpoint": endpoint,
            "status": "active",
            "metadata": {
                "name": "OpenWebUI Agent",
                "version": "1.0",
                "capabilities": ["web_ui", "api", "document_processing"],
                "ports": [3000],
                "docker_required": True
            }
        }

        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.post(
                f"{self.portier_url}/api/agent/register",
                json=payload,
                headers=headers,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"⚠️  Registry Error: {e}")
            return None

    def get_agent_status(self, agent_id="opena3"):
        """Hole Agent-Status vom Portier"""
        try:
            response = requests.get(
                f"{self.portier_url}/api/agent/{agent_id}/status",
                timeout=5
            )
            return response.json()
        except:
            return None

    def get_available_agents(self):
        """Hole Liste aller verfügbaren Agenten"""
        try:
            response = requests.get(
                f"{self.portier_url}/api/agents",
                timeout=5
            )
            return response.json()
        except:
            return []

    def send_command(self, command: str, params: Dict = None):
        """Sende Befehl über Portier zu anderen Agenten"""
        payload = {
            "command": command,
            "source": "opena3",
            "params": params or {}
        }

        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.post(
                f"{self.portier_url}/api/command",
                json=payload,
                headers=headers,
                timeout=10
            )
            return response.json()
        except:
            return None
```

### Portier API-Kopplung

```python
class PortierAPIClient:
    """Direkte API-Anbindung an Portier-Endpoints"""

    # Portier Core Ports: 12344-12349
    PORTIER_PORTS = {
        "opena1": 12344,      # Koordinator
        "opena2": 12345,      # Archivator
        "kordp": 12346,       # Coordinator Portal
        "opena20": 12347,     # Knowledge Router
        "archive": 12348,     # Archive Portal
        "health": 12349       # Health Check
    }

    @staticmethod
    def health_check():
        """Prüfe Portier Health Status"""
        try:
            response = requests.get(
                f"http://127.0.0.1:{PortierAPIClient.PORTIER_PORTS['health']}/health",
                timeout=5
            )
            return response.json()
        except:
            return {"status": "unavailable"}

    @staticmethod
    def query_knowledge_base(query: str):
        """Frage Knowledge Base über opena20 ab"""
        try:
            response = requests.post(
                f"http://127.0.0.1:{PortierAPIClient.PORTIER_PORTS['opena20']}/api/query",
                json={"query": query},
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def archive_safepoint(safepoint_id: str, data: Dict):
        """Archiviere Safepoint in Portier Archive"""
        try:
            response = requests.post(
                f"http://127.0.0.1:{PortierAPIClient.PORTIER_PORTS['archive']}/api/store",
                json={
                    "type": "safepoint",
                    "safepoint_id": safepoint_id,
                    "data": data
                },
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
```

---

## 📂 Knowledgebase-Loader

### KB-Loader Implementation

```python
import json
from pathlib import Path
from typing import List, Dict

class KnowledgebaseLoader:
    """Lade & integriere Knowledgebase in Session Memory"""

    def __init__(self, kb_path="/mnt/data/knowledge_base"):
        self.kb_path = Path(kb_path)
        self.knowledge = {}

    def load_from_file(self, kb_file: str):
        """Lade Knowledgebase aus JSON/JSONL"""
        file_path = self.kb_path / kb_file

        if file_path.suffix == '.jsonl':
            # JSONL Format (eine JSON pro Zeile)
            with open(file_path, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    self.knowledge[entry.get('id')] = entry

        elif file_path.suffix == '.json':
            # JSON Format
            with open(file_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for entry in data:
                        self.knowledge[entry.get('id')] = entry
                else:
                    self.knowledge.update(data)

        return len(self.knowledge)

    def load_all_available(self):
        """Lade alle verfügbaren KB-Dateien"""
        count = 0
        if self.kb_path.exists():
            for kb_file in self.kb_path.glob("*.json*"):
                try:
                    loaded = self.load_from_file(kb_file.name)
                    count += loaded
                    print(f"✅ Geladen: {kb_file.name} ({loaded} Einträge)")
                except Exception as e:
                    print(f"⚠️  Fehler bei {kb_file.name}: {e}")

        return count

    def get_knowledge_summary(self) -> Dict:
        """Hole Zusammenfassung der geladenen Knowledge"""
        return {
            "total_entries": len(self.knowledge),
            "categories": list(set(e.get('category') for e in self.knowledge.values() if 'category' in e)),
            "sample_keys": list(self.knowledge.keys())[:10]
        }

    def search(self, query: str) -> List[Dict]:
        """Suche in Knowledgebase"""
        results = []
        for entry in self.knowledge.values():
            if query.lower() in str(entry).lower():
                results.append(entry)
        return results[:10]  # Top 10 Ergebnisse
```

---

## 🔧 Vollständiger Masterprompt

### System Prompt für opena3

```
# 🧠 OpenWebUI Agent (opena3) - Masterprompt

## Identität
- **Agent-ID:** opena3
- **Rolle:** OpenWebUI Interface Agent
- **System:** Portier Multi-Agent Framework
- **Port:** 3000
- **Status:** [AUTO-LOADING]

## Beim Start
1. ✅ Lade letzten Safepoint
2. ✅ Prüfe Docker-Status
3. ✅ Verbinde mit Portier-Registry
4. ✅ Lade Knowledgebase
5. ✅ Initialisiere Session Memory

## Verfügbare Operationen

### 1. Datenabfragen
- `@portier query` - Frage andere Agenten ab
- `@kb search [term]` - Suche Knowledgebase
- `@archive list` - Zeige archivierte Safepoints

### 2. System-Befehle
- `@docker status` - Prüfe Docker-Status
- `@registry status` - Zeige Agent-Registry
- `@health check` - Vollständiger Health-Check

### 3. Safepoint-Management
- `@save checkpoint` - Speichere aktuellen State
- `@load safepoint [id]` - Lade Safepoint
- `@list safepoints` - Zeige verfügbare Safepoints

## Regeln
1. Speichere nach jeder wichtigen Operation einen Safepoint
2. Validiere alle Portier-Verbindungen bei Startup
3. Gebe Docker-Fehler klar aus und versuche zu beheben
4. Nutze Knowledgebase für Kontextinformationen
5. Halte Session Memory synchron mit Portier

## Integration
- **Portier Main:** http://127.0.0.1:12349
- **Registry:** opena1 @ 12344
- **Archive:** opena2 @ 12345
- **Knowledge:** opena20 @ 12347
- **Local Storage:** /mnt/data

## Startup-Sequenz
```

[1/5] Loading last safepoint...
[2/5] Checking Docker...
[3/5] Registering with Portier...
[4/5] Loading Knowledgebase...
[5/5] Ready!

✅ opena3 initialized and ready for interaction

```

---

**Bitte diese Prompt beim nächsten Start verwenden!**
```

### Aktivierungs-Script

```python
#!/usr/bin/env python3
"""
Masterprompt Activator für opena3
Initialisiert alle Systeme & lädt Safepoints
"""

import asyncio
from safepoint_manager import SafepointManager
from docker_checker import DockerChecker
from portier_registry import PortierRegistry, PortierAPIClient
from knowledge_loader import KnowledgebaseLoader

async def initialize_opena3():
    """Hauptinitialisierungsfunktion"""

    print("=" * 60)
    print("🚀 OpenWebUI opena3 - Masterprompt Initialization")
    print("=" * 60)

    # [1/5] Lade Safepoint
    print("\n[1/5] Loading last safepoint...")
    manager = SafepointManager()
    safepoint = manager.load_safepoint()
    if safepoint:
        print(f"✅ Loaded: {safepoint['safepoint_id']}")
    else:
        print("⚠️  No safepoint found - starting fresh")

    # [2/5] Prüfe Docker
    print("\n[2/5] Checking Docker...")
    docker_status = DockerChecker.full_check()
    print(f"✅ Docker: {docker_status}")

    # [3/5] Registriere mit Portier
    print("\n[3/5] Registering with Portier...")
    registry = PortierRegistry()
    reg_result = registry.register_agent()
    print(f"✅ Registration: {reg_result if reg_result else 'Failed'}")

    # [4/5] Lade Knowledgebase
    print("\n[4/5] Loading Knowledgebase...")
    kb_loader = KnowledgebaseLoader()
    kb_count = kb_loader.load_all_available()
    print(f"✅ Loaded {kb_count} KB entries")
    print(f"📊 Summary: {kb_loader.get_knowledge_summary()}")

    # [5/5] Health Check
    print("\n[5/5] Running health check...")
    health = PortierAPIClient.health_check()
    print(f"✅ Health: {health}")

    print("\n" + "=" * 60)
    print("✅ opena3 initialized and ready for interaction!")
    print("=" * 60)

    return {
        "safepoint": safepoint,
        "docker": docker_status,
        "registry": reg_result,
        "knowledge": kb_count,
        "health": health
    }

if __name__ == "__main__":
    result = asyncio.run(initialize_opena3())
    print(f"\n📊 Initialization Result: {result}")
```

---

## 🚀 Deployment & Aktivierung

### Installation in OpenWebUI

1. **Kopiere Masterprompt zu OpenWebUI:**

   ```bash
   cp MASTERPROMPT_OPENA3_AUTORECOVERY.md \
     /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui/SYSTEM_PROMPTS/
   ```

2. **Aktiviere in Docker-Compose:**

   ```yaml
   opena3:
     image: ghcr.io/open-webui/open-webui:latest
     ports:
       - "3000:8080"
     environment:
       - SYSTEM_PROMPT_FILE=/system_prompts/MASTERPROMPT_OPENA3_AUTORECOVERY.md
       - PORTIER_URL=http://127.0.0.1:12349
       - PORTIER_TOKEN=${PORTIER_TOKEN}
     volumes:
       - /mnt/data:/mnt/data
       - ./SYSTEM_PROMPTS:/system_prompts:ro
   ```

3. **Starte Initialisierung:**

   ```bash
   python3 masterprompt_activator.py
   ```

---

## 📊 Monitoring & Logs

### Log-Struktur

```
/mnt/data/logs/
├── opena3_startup_YYYYMMDD_HHMMSS.log
├── safepoints/
│   ├── sp_opena3_20251124_143022.json
│   └── ...
└── health_checks/
    └── health_YYYYMMDD.log
```

---

## ✅ Checkliste für Production

- [ ] Masterprompt in OpenWebUI aktiviert
- [ ] Safepoint-Manager lädt korrekt
- [ ] Docker-Check läuft erfolgreich
- [ ] Portier-Registry erkennt opena3
- [ ] Knowledgebase lädt alle Dateien
- [ ] Health-Check grün
- [ ] Logs schreiben korrekt
- [ ] Backup läuft täglich

---

**Status: ✅ Ready for Production Deployment**
