"""
LocalAgent-Pro - Automatische Agenten-Erstellung
Dieses Skript erstellt automatisch einen lokalen Agenten mit allen Tools
"""

import json
import requests
import sys

# OpenWebUI Konfiguration
OPENWEBUI_URL = "http://127.0.0.1:3000"
LOCALAGENT_API = "http://127.0.0.1:8001/v1"

# Agent-Konfiguration
AGENT_CONFIG = {
    "name": "LocalAgent-Pro",
    "description": "Lokaler KI-Agent mit Dateizugriff, Shell-Befehlen und Web-Zugriff",
    "version": "1.0.0",
    "tags": ["lokal", "filesystem", "web", "shell"],
    "visibility": "private",
    
    # System Prompt
    "system_prompt": """Du bist LocalAgent-Pro, ein lokaler KI-Agent mit erweiterten Fähigkeiten.

VERFÜGBARE TOOLS:
1. **Datei lesen**: "Zeige mir config.yaml" oder "Lies test.txt"
2. **Datei schreiben**: "Erstelle Datei hello.txt mit Hallo Welt"
3. **Verzeichnis**: "Liste alle Dateien auf" oder "Zeige Dateien im workspace"
4. **Web-Zugriff**: "Hole github.com" oder "Lade example.com"
5. **Shell**: "Führe Kommando 'ls -la' aus" (nur im Live-Modus)

SICHERHEIT:
- Sandbox-Modus: AKTIV
- Erlaubte Domains: github.com, example.com, ubuntu.com, archlinux.org
- Alle Dateien werden in /home/danijel-jd/localagent_sandbox gespeichert

ANTWORT-STIL:
- Präzise und handlungsorientiert
- Nutze Emojis für bessere Lesbarkeit
- Zeige immer die verwendeten Tools an
- Bei Fehlern: Klare Fehlermeldung + Alternative vorschlagen

BEISPIELE:
User: "Liste alle Dateien auf"
Agent: 📂 Verzeichnisinhalt: [Liste der Dateien]

User: "Erstelle eine Datei notes.md"
Agent: ✅ Datei notes.md wurde erstellt in der Sandbox
""",
    
    # Modell-Parameter
    "model_params": {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 2048,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0
    },
    
    # Prompt-Vorschläge
    "prompt_suggestions": [
        "Liste alle Dateien im workspace auf",
        "Erstelle eine Datei README.md mit einer Projektbeschreibung",
        "Zeige mir den Inhalt von config.yaml",
        "Hole die Webseite github.com",
        "Führe 'pwd' aus und zeige das aktuelle Verzeichnis"
    ],
    
    # Fähigkeiten
    "capabilities": {
        "file_operations": True,
        "web_access": True,
        "shell_commands": True,
        "image_recognition": False,
        "code_interpreter": True,
        "web_search": True
    },
    
    # API-Verbindung
    "api": {
        "base_url": LOCALAGENT_API,
        "model": "llama3.1",
        "api_key": "dummy"
    }
}

def create_openwebui_agent_json():
    """Erstellt JSON für OpenWebUI Agent Import"""
    
    openwebui_config = {
        "id": "localagent-pro-v1",
        "name": AGENT_CONFIG["name"],
        "description": AGENT_CONFIG["description"],
        "meta": {
            "profile_image_url": "",
            "tags": AGENT_CONFIG["tags"],
            "capabilities": AGENT_CONFIG["capabilities"]
        },
        "base_model_id": "llama3.1",
        "params": {
            "system": AGENT_CONFIG["system_prompt"],
            **AGENT_CONFIG["model_params"]
        },
        "access_control": {
            "read": {"group_ids": [], "user_ids": []},
            "write": {"group_ids": [], "user_ids": []}
        }
    }
    
    return openwebui_config

def create_standalone_agent_config():
    """Erstellt eigenständige Agent-Konfiguration"""
    
    config = {
        "agent": {
            "name": AGENT_CONFIG["name"],
            "version": AGENT_CONFIG["version"],
            "description": AGENT_CONFIG["description"]
        },
        
        "api": AGENT_CONFIG["api"],
        
        "system_prompt": AGENT_CONFIG["system_prompt"],
        
        "tools": [
            {
                "name": "read_file",
                "description": "Liest den Inhalt einer Datei",
                "parameters": {
                    "path": {
                        "type": "string",
                        "description": "Pfad zur Datei"
                    }
                },
                "examples": [
                    "Lies Datei config.yaml",
                    "Zeige mir test.txt"
                ]
            },
            {
                "name": "write_file",
                "description": "Schreibt Inhalt in eine Datei",
                "parameters": {
                    "path": {
                        "type": "string",
                        "description": "Pfad zur Datei"
                    },
                    "content": {
                        "type": "string",
                        "description": "Dateiinhalt"
                    }
                },
                "examples": [
                    "Erstelle Datei hello.txt mit Hallo Welt",
                    "Schreibe notes.md mit Meine Notizen"
                ]
            },
            {
                "name": "list_files",
                "description": "Listet Dateien in einem Verzeichnis auf",
                "parameters": {
                    "path": {
                        "type": "string",
                        "description": "Verzeichnispfad",
                        "default": "."
                    }
                },
                "examples": [
                    "Liste alle Dateien auf",
                    "Zeige Dateien im workspace"
                ]
            },
            {
                "name": "fetch",
                "description": "Lädt Webseiteninhalte",
                "parameters": {
                    "url": {
                        "type": "string",
                        "description": "URL der Webseite"
                    }
                },
                "examples": [
                    "Hole github.com",
                    "Lade example.com"
                ]
            },
            {
                "name": "run_shell",
                "description": "Führt Shell-Befehle aus (nur Live-Modus)",
                "parameters": {
                    "command": {
                        "type": "string",
                        "description": "Shell-Befehl"
                    }
                },
                "examples": [
                    "Führe 'ls -la' aus",
                    "Execute 'pwd'"
                ]
            }
        ],
        
        "prompt_suggestions": AGENT_CONFIG["prompt_suggestions"],
        
        "security": {
            "sandbox": True,
            "sandbox_path": "/home/danijel-jd/localagent_sandbox",
            "allowed_domains": ["github.com", "example.com", "ubuntu.com", "archlinux.org"],
            "dangerous_commands_blocked": True
        }
    }
    
    return config

def test_agent_connection():
    """Testet die Verbindung zum LocalAgent-Pro Backend"""
    try:
        response = requests.get(f"{LOCALAGENT_API.replace('/v1', '')}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend-Verbindung erfolgreich!")
            print(f"   Modell: {data.get('model')}")
            print(f"   Sandbox: {data.get('sandbox')}")
            print(f"   Erlaubte Domains: {len(data.get('allowed_domains', []))}")
            return True
        else:
            print(f"❌ Backend antwortet mit Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Verbindungsfehler: {e}")
        return False

def main():
    print("=" * 60)
    print("LocalAgent-Pro - Automatische Agenten-Erstellung")
    print("=" * 60)
    print()
    
    # 1. Backend-Verbindung testen
    print("1️⃣ Teste Backend-Verbindung...")
    if not test_agent_connection():
        print("\n⚠️  Starte zuerst den LocalAgent-Pro Server:")
        print("   cd LocalAgent-Pro && ./start_server.sh")
        sys.exit(1)
    print()
    
    # 2. Konfigurationen erstellen
    print("2️⃣ Erstelle Agent-Konfigurationen...")
    
    # OpenWebUI-Import
    openwebui_config = create_openwebui_agent_json()
    with open("openwebui_agent_import.json", "w", encoding="utf-8") as f:
        json.dump(openwebui_config, f, indent=2, ensure_ascii=False)
    print("   ✅ openwebui_agent_import.json erstellt")
    
    # Standalone Config
    standalone_config = create_standalone_agent_config()
    with open("agent_config.json", "w", encoding="utf-8") as f:
        json.dump(standalone_config, f, indent=2, ensure_ascii=False)
    print("   ✅ agent_config.json erstellt")
    
    print()
    
    # 3. Anweisungen
    print("3️⃣ Nächste Schritte:")
    print()
    print("📋 METHODE 1: OpenWebUI (Empfohlen)")
    print("   1. Öffne http://127.0.0.1:3000")
    print("   2. Gehe zu: Workspace → Agents → Create Agent")
    print("   3. Oder: Einstellungen → Models → Add Model")
    print("   4. Importiere: openwebui_agent_import.json")
    print()
    print("📋 METHODE 2: Manuelle Konfiguration")
    print("   1. Öffne http://127.0.0.1:3000")
    print("   2. Settings → Connections → OpenAI API")
    print("   3. API Base URL: http://127.0.0.1:8001/v1")
    print("   4. API Key: dummy")
    print("   5. Model: llama3.1")
    print()
    print("📋 METHODE 3: CLI verwenden")
    print("   ./chat-local.sh \"Liste alle Dateien auf\"")
    print()
    print("=" * 60)
    print("✅ Agent-Konfiguration abgeschlossen!")
    print("=" * 60)

if __name__ == "__main__":
    main()
