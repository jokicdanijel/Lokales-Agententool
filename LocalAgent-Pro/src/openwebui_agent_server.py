#!/usr/bin/env python3
"""
LocalAgent-Pro Server - Komplett OpenAI-SDK-frei für OpenWebUI
Mit umfassendem Logging für Backend und Ollama-Integration
"""

from flask import Flask, request, jsonify, Response
import os
import yaml
import re
import json
import requests
import subprocess
import time
import uuid
from urllib.parse import urlparse
import logging
from typing import Dict, Any, List, Optional
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Logging-System importieren
from logging_config import get_logging_manager, mask_sensitive_data, truncate_long_content # pyright: ignore[reportUnknownVariableType]

# Import Ollama integration
from ollama_integration import create_ollama_client

# Logging-Manager initialisieren (früh initialisieren!)
logging_manager = get_logging_manager(
    app_name="LocalAgent-Pro",
    log_level="DEBUG",  # Kann auf INFO/WARNING für production gesetzt werden
    console_output=True
)

# Spezielle Logger erstellen
main_logger = logging_manager.get_logger("Main")
api_logger = logging_manager.get_logger("API")
tool_logger = logging_manager.create_tool_logger()
ollama_logger = logging_manager.create_ollama_logger()
request_logger = logging_manager.create_request_logger()

main_logger.info("🚀 LocalAgent-Pro Server wird initialisiert...")

# Ollama-Client initialisieren
main_logger.info("🤖 Initialisiere Ollama-Client...")
ollama_client = create_ollama_client()
main_logger.info("✅ Ollama-Client bereit")

# Config laden
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.yaml")

try:
    main_logger.debug(f"📄 Lade Konfiguration von: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    main_logger.info("✅ Konfiguration erfolgreich geladen")
except FileNotFoundError:
    main_logger.critical(f"❌ Config nicht gefunden: {CONFIG_PATH}")
    print(f"❌ Config nicht gefunden: {CONFIG_PATH}")
    exit(1)
except Exception as e:
    main_logger.critical(f"❌ Fehler beim Laden der Config: {e}")
    print(f"❌ Fehler beim Laden der Config: {e}")
    exit(1)

# Konfiguration
SANDBOX = config.get("sandbox", True)
SANDBOX_PATH = config.get("sandbox_path", os.path.expanduser("~/localagent_sandbox"))
ALLOWED_DOMAINS = config.get("allowed_domains", ["example.com", "github.com", "ubuntu.com", "wikipedia.org"])
OPEN_WEBUI_PORT = config.get("open_webui_port", 3000)

# Auto-Whitelist-Konfiguration
AUTO_WHITELIST_ENABLED = config.get("auto_whitelist_enabled", False)
AUTO_WHITELIST_FILE = config.get("auto_whitelist_file", "config/domain_whitelist.yaml")
ASK_BEFORE_NEW_DOMAIN = config.get("ask_before_new_domain", False)

llm_cfg = config.get("llm", {})
LLM_MODEL = llm_cfg.get("model", "llama3.1")

# Logging-Konfiguration
main_logger.info(f"🔒 Sandbox-Modus: {'✅ Aktiv' if SANDBOX else '❌ Deaktiviert'}")
main_logger.info(f"📁 Sandbox-Pfad: {SANDBOX_PATH}")
main_logger.info(f"🌐 Erlaubte Domains: {len(ALLOWED_DOMAINS)} ({', '.join(str(d) for d in ALLOWED_DOMAINS[:3])}...)")
if "*" in ALLOWED_DOMAINS:
    main_logger.warning(f"⚠️ WILDCARD AKTIV - Alle Domains erlaubt!")
    if AUTO_WHITELIST_ENABLED:
        main_logger.info(f"✅ Auto-Whitelist aktiviert: {AUTO_WHITELIST_FILE}")
main_logger.info(f"🧠 LLM-Modell: {LLM_MODEL}")
main_logger.info(f"📱 OpenWebUI Port: {OPEN_WEBUI_PORT}")

app = Flask(__name__)

# Flask-Logging deaktivieren (nutzen unser eigenes)
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

# === PROMETHEUS METRICS ===
request_count = Counter('localagent_requests_total', 'Total API requests', ['endpoint', 'status'])
request_duration = Histogram('localagent_request_duration_seconds', 'Request duration', ['endpoint'])
active_requests = Gauge('localagent_active_requests', 'Currently active requests')
ollama_calls = Counter('localagent_ollama_calls_total', 'Ollama API calls', ['model', 'status'])
shell_executions = Counter('localagent_shell_executions_total', 'Shell command executions', ['status'])
loop_detections = Counter('localagent_loop_detections_total', 'Loop protection activations')
tool_executions = Counter('localagent_tool_executions_total', 'Tool executions', ['tool', 'status'])
sandbox_operations = Counter('localagent_sandbox_operations_total', 'Sandbox file operations', ['operation'])

# Session-Tracking für Rückfragen (einfache In-Memory-Lösung)
pending_confirmations: Dict[str, Any] = {}

# === LOOP-PROTECTION: REQUEST TRACKING ===
import hashlib
recent_requests: Dict[str, Dict[str, Any]] = {}  # {prompt_hash: {"count": int, "last_time": float}}
MAX_REQUEST_REPEATS = 1  # Max. Wiederholungen
LOOP_DETECTION_WINDOW = 2  # Sekunden

# === LOOP-PROTECTION: REQUEST TRACKING ===
import hashlib
recent_requests: Dict[str, Dict[str, Any]] = {}  # {prompt_hash: {"count": int, "last_time": float}}
MAX_REQUEST_REPEATS = 1  # Max. Wiederholungen
LOOP_DETECTION_WINDOW = 2  # Sekunden

# Domain-Whitelist Cache (für Auto-Whitelist)
domain_whitelist_cache: set = set()

# =================
# HELPER FUNCTIONS
# =================

def load_domain_whitelist():
    """Lädt gespeicherte Domain-Whitelist aus Datei"""
    global domain_whitelist_cache
    
    if not AUTO_WHITELIST_ENABLED:
        return
    
    whitelist_path = os.path.join(BASE_DIR, AUTO_WHITELIST_FILE)
    
    try:
        if os.path.exists(whitelist_path):
            with open(whitelist_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                domain_whitelist_cache = set(data.get('approved_domains', []))
                main_logger.info(f"📋 Domain-Whitelist geladen: {len(domain_whitelist_cache)} Domains")
    except Exception as e:
        main_logger.error(f"❌ Fehler beim Laden der Whitelist: {e}")

def save_domain_to_whitelist(domain: str):
    """Speichert Domain in Whitelist-Datei"""
    if not AUTO_WHITELIST_ENABLED:
        return
    
    whitelist_path = os.path.join(BASE_DIR, AUTO_WHITELIST_FILE)
    
    try:
        # Lade existierende Whitelist
        if os.path.exists(whitelist_path):
            with open(whitelist_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {'approved_domains': []}
        
        # Füge Domain hinzu (wenn noch nicht vorhanden)
        if domain not in data['approved_domains']:
            data['approved_domains'].append(domain)
            data['approved_domains'].sort()
            
            # Speichere
            os.makedirs(os.path.dirname(whitelist_path), exist_ok=True)
            with open(whitelist_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            
            # Update Cache
            domain_whitelist_cache.add(domain)
            
            tool_logger.info(f"✅ Domain zur Whitelist hinzugefügt: {domain}")
            main_logger.info(f"📝 Whitelist aktualisiert: {len(domain_whitelist_cache)} Domains")
    except Exception as e:
        tool_logger.error(f"❌ Fehler beim Speichern der Domain: {e}")

# Lade Whitelist beim Start
load_domain_whitelist()

# =================
# TOOL FUNKTIONEN
# =================

def _resolve_path(path: str) -> str:
    """Wandelt Pfad in Sandbox-Pfad um, falls Sandbox aktiv"""
    tool_logger.debug(f"🔍 Pfadauflösung: {path} (Sandbox: {SANDBOX})")
    
    if SANDBOX:
        clean_path = path.lstrip("/").lstrip("\\")
        resolved = os.path.join(SANDBOX_PATH, clean_path)
        os.makedirs(os.path.dirname(resolved) if os.path.dirname(resolved) else SANDBOX_PATH, exist_ok=True)
        tool_logger.debug(f"📁 Aufgelöster Sandbox-Pfad: {resolved}")
        return resolved
    
    resolved = os.path.abspath(path)
    tool_logger.debug(f"📁 Aufgelöster absoluter Pfad: {resolved}")
    return resolved

def read_file(path: str) -> str:
    """Liest Dateiinhalt"""
    tool_logger.info(f"📖 Tool 'read_file' aufgerufen: path={path}")
    
    try:
        rpath = _resolve_path(path)
        tool_logger.debug(f"🔍 Prüfe Existenz: {rpath}")
        
        if not os.path.exists(rpath):
            tool_logger.warning(f"⚠️ Datei nicht gefunden: {rpath}")
            return f"❌ Datei nicht gefunden: {rpath}"
        
        file_size = os.path.getsize(rpath)
        tool_logger.debug(f"📊 Dateigröße: {file_size} bytes")
        
        with open(rpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        tool_logger.info(f"✅ Datei erfolgreich gelesen: {rpath} ({len(content)} Zeichen)")
        tool_logger.debug(f"📄 Content-Vorschau: {truncate_long_content(content, 200)}")
        
        location = f" (Sandbox: {rpath})" if SANDBOX else f" (Live: {rpath})"
        return f"📄 Datei gelesen{location}:\n\n{content}"
        
    except Exception as e:
        tool_logger.error(f"❌ Fehler beim Lesen von {path}: {str(e)}", exc_info=True)
        return f"❌ Fehler beim Lesen: {str(e)}"

def write_file(path: str, content: str) -> str:
    """Schreibt Dateiinhalt"""
    tool_logger.info(f"✏️ Tool 'write_file' aufgerufen: path={path}, content_length={len(content)}")
    
    try:
        rpath = _resolve_path(path)
        tool_logger.debug(f"📝 Schreibe nach: {rpath}")
        tool_logger.debug(f"📄 Content-Vorschau: {truncate_long_content(content, 200)}")
        
        with open(rpath, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Metrics
        sandbox_operations.labels(operation='write').inc()
        tool_executions.labels(tool='write_file', status='success').inc()
        
        tool_logger.info(f"✅ Datei erfolgreich geschrieben: {rpath} ({len(content)} Zeichen)")
        
        location = f" (Sandbox: {rpath})" if SANDBOX else f" (Live: {rpath})"
        return f"✅ Datei erstellt{location}\n📝 {len(content)} Zeichen geschrieben"
        
    except Exception as e:
        tool_executions.labels(tool='write_file', status='error').inc()
        tool_logger.error(f"❌ Fehler beim Schreiben nach {path}: {str(e)}", exc_info=True)
        return f"❌ Fehler beim Schreiben: {str(e)}"

def delete_file(path: str) -> str:
    """Löscht eine Datei"""
    tool_logger.info(f"🗑️ Tool 'delete_file' aufgerufen: path={path}")
    
    try:
        rpath = _resolve_path(path)
        tool_logger.debug(f"🔍 Prüfe Datei: {rpath}")
        
        if not os.path.exists(rpath):
            tool_logger.warning(f"⚠️ Datei nicht gefunden: {rpath}")
            return f"❌ Datei nicht gefunden: {rpath}"
        
        if os.path.isdir(rpath):
            tool_logger.warning(f"⚠️ Ist ein Verzeichnis: {rpath}")
            return f"❌ Ist ein Verzeichnis (nutze Shell-Kommando für Verzeichnisse): {rpath}"
        
        # Lösche Datei
        os.remove(rpath)
        tool_logger.info(f"✅ Datei erfolgreich gelöscht: {rpath}")
        
        location = f" (Sandbox: {rpath})" if SANDBOX else f" (Live: {rpath})"
        return f"✅ Datei gelöscht{location}"
        
    except Exception as e:
        tool_logger.error(f"❌ Fehler beim Löschen von {path}: {str(e)}", exc_info=True)
        return f"❌ Fehler beim Löschen: {str(e)}"

def list_files(path: str = ".") -> str:
    """Listet Verzeichnisinhalt auf"""
    tool_logger.info(f"📂 Tool 'list_files' aufgerufen: path={path}")
    
    try:
        rpath = _resolve_path(path)
        tool_logger.debug(f"🔍 Liste Verzeichnis: {rpath}")
        
        if not os.path.exists(rpath):
            tool_logger.warning(f"⚠️ Verzeichnis nicht gefunden: {rpath}")
            return f"❌ Verzeichnis nicht gefunden: {rpath}"
        
        if not os.path.isdir(rpath):
            tool_logger.warning(f"⚠️ Kein Verzeichnis: {rpath}")
            return f"❌ Kein Verzeichnis: {rpath}"
        
        entries: list[str] = []
        total_size = 0
        file_count = 0
        dir_count = 0
        
        for item in sorted(os.listdir(rpath)):
            item_path = os.path.join(rpath, item)
            if os.path.isdir(item_path):
                entries.append(f"📁 {item}/")
                dir_count += 1
            else:
                size = os.path.getsize(item_path)
                entries.append(f"📄 {item} ({size} bytes)")
                total_size += size
                file_count += 1
        
        tool_logger.info(
            f"✅ Verzeichnis aufgelistet: {rpath} "
            f"({file_count} Dateien, {dir_count} Ordner, {total_size} bytes)"
        )
        
        location = f" (Sandbox: {rpath})" if SANDBOX else f" (Live: {rpath})"
        if not entries:
            return f"📂 Verzeichnis leer{location}"
        
        return f"📂 Verzeichnisinhalt{location}:\n" + "\n".join(entries)
        
    except Exception as e:
        tool_logger.error(f"❌ Fehler beim Auflisten von {path}: {str(e)}", exc_info=True)
        return f"❌ Fehler beim Auflisten: {str(e)}"

def run_shell(cmd: str) -> str:
    """Führt Shell-Kommando aus"""
    tool_logger.info(f"💻 Tool 'run_shell' aufgerufen: cmd={cmd}")
    
    if SANDBOX:
        tool_logger.warning("🚫 Shell-Kommando blockiert (Sandbox-Modus aktiv)")
        shell_executions.labels(status='blocked_sandbox').inc()
        return "🚫 Shell-Kommandos sind im Sandbox-Modus deaktiviert.\n" \
               "💡 Setze 'sandbox: false' in config/config.yaml und starte den Server neu."
    
    if not cmd.strip():
        tool_logger.warning("⚠️ Leeres Shell-Kommando")
        shell_executions.labels(status='empty_command').inc()
        return "❌ Leeres Kommando"
    
    try:
        # Sicherheitsprüfungen
        dangerous_cmds = ['rm -rf', 'sudo', 'su -', 'chmod +x', 'mkfs', 'dd if=', 'format']
        if any(danger in cmd.lower() for danger in dangerous_cmds):
            tool_logger.warning(f"🚫 Gefährliches Kommando blockiert: {cmd}")
            shell_executions.labels(status='blocked_dangerous').inc()
            return f"🚫 Gefährliches Kommando blockiert: {cmd}"
        
        tool_logger.debug(f"⚙️ Führe aus: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        # Metrics
        if result.returncode == 0:
            shell_executions.labels(status='success').inc()
        else:
            shell_executions.labels(status='failed').inc()
        
        tool_logger.info(
            f"✅ Shell-Kommando ausgeführt: exit_code={result.returncode}, "
            f"stdout_length={len(result.stdout)}, stderr_length={len(result.stderr)}"
        )
        tool_logger.debug(f"📤 STDOUT: {truncate_long_content(result.stdout, 500)}")
        if result.stderr:
            tool_logger.debug(f"⚠️ STDERR: {truncate_long_content(result.stderr, 500)}")
        
        output_parts = [f"💻 Shell-Kommando: {cmd}"]
        
        if result.returncode == 0:
            output_parts.append("✅ Erfolgreich ausgeführt")
        else:
            output_parts.append(f"❌ Exit Code: {result.returncode}")
        
        if result.stdout:
            output_parts.append(f"📤 STDOUT:\n{result.stdout}")
        if result.stderr:
            output_parts.append(f"⚠️ STDERR:\n{result.stderr}")
        
        return "\n\n".join(output_parts)
        
    except subprocess.TimeoutExpired:
        tool_logger.error(f"⏰ Timeout nach 30s: {cmd}")
        shell_executions.labels(status='timeout').inc()
        return f"⏰ Timeout nach 30s: {cmd}"
    except Exception as e:
        tool_logger.error(f"❌ Shell-Fehler bei '{cmd}': {str(e)}", exc_info=True)
        shell_executions.labels(status='error').inc()
        return f"❌ Shell-Fehler: {str(e)}"

def fetch(url: str) -> str:
    """Lädt Webseiteninhalte"""
    tool_logger.info(f"🌐 Tool 'fetch' aufgerufen: url={url}")
    
    if not url.strip():
        tool_logger.warning("⚠️ Leere URL")
        return "❌ Leere URL"
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        tool_logger.debug(f"🔧 URL ergänzt zu: {url}")
    
    try:
        parsed_url = urlparse(url)
        domain_with_port = parsed_url.netloc.lower()
        # Extrahiere Domain ohne Port (z.B. "127.0.0.1:8001" -> "127.0.0.1")
        domain = domain_with_port.split(':')[0] if ':' in domain_with_port else domain_with_port
        
        tool_logger.debug(f"🔍 Extrahierte Domain: {domain} (Original: {domain_with_port})")
        
        # === DOMAIN-CHECK MIT AUTO-WHITELIST ===
        allowed = False
        
        # 1. Wildcard-Check
        if "*" in ALLOWED_DOMAINS:
            allowed = True
            tool_logger.debug(f"✅ Wildcard aktiv - Domain erlaubt: {domain}")
            
            # Auto-Whitelist: Speichere Domain automatisch
            if AUTO_WHITELIST_ENABLED and domain not in domain_whitelist_cache:
                save_domain_to_whitelist(domain)
                tool_logger.info(f"📝 Domain automatisch zur Whitelist hinzugefügt: {domain}")
        
        # 2. Explizite Whitelist-Check
        else:
            allowed = any(domain == d.lower() or domain.endswith('.' + d.lower()) 
                         for d in ALLOWED_DOMAINS)
        
        # 3. Auto-Whitelist-Cache-Check
        if not allowed and AUTO_WHITELIST_ENABLED:
            if domain in domain_whitelist_cache:
                allowed = True
                tool_logger.debug(f"✅ Domain aus Auto-Whitelist: {domain}")
        
        if not allowed:
            tool_logger.warning(f"🚫 Domain blockiert: {domain} (nicht in Whitelist)")
            return f"""🚫 **Domain blockiert: {domain}**

⚠️ Diese Domain ist nicht in der Whitelist erlaubt.

� **Erlaubte Domains:**
{chr(10).join(f'   • {d}' for d in ALLOWED_DOMAINS)}

💡 **Um eine Domain hinzuzufügen:**
   1. Öffne `config/config.yaml`
   2. Füge Domain zur `allowed_domains` Liste hinzu
   3. Starte den Server neu

🔒 **Sicherheitshinweis:**
   Nur vertrauenswürdige Domains zur Whitelist hinzufügen!
"""
        
        tool_logger.debug(f"✅ Domain erlaubt: {domain}")
        headers = {'User-Agent': 'LocalAgent-Pro/1.0'}
        
        tool_logger.debug(f"📡 Sende HTTP GET Request an: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        content_length = len(response.text)
        tool_logger.info(
            f"✅ Web-Request erfolgreich: {url} "
            f"(Status: {response.status_code}, Größe: {content_length} Zeichen)"
        )
        tool_logger.debug(f"📊 Response Headers: {dict(response.headers)}")
        
        content = response.text[:10000]
        if len(response.text) > 10000:
            content += f"\n\n... (auf 10KB begrenzt, Original: {len(response.text)} Zeichen)"
            tool_logger.debug(f"✂️ Content auf 10KB gekürzt (Original: {content_length} Zeichen)")
        
        return f"🌐 Webseite geladen: {url}\n📊 Status: {response.status_code}\n\n{content}"
        
    except requests.exceptions.Timeout:
        tool_logger.error(f"⏰ Timeout bei Web-Request: {url}")
        return f"❌ Web-Fehler: Timeout nach 15s"
    except requests.exceptions.RequestException as e:
        tool_logger.error(f"❌ Web-Request-Fehler bei {url}: {str(e)}", exc_info=True)
        return f"❌ Web-Fehler: {str(e)}"
    except Exception as e:
        tool_logger.error(f"❌ Unerwarteter Fehler bei Web-Request {url}: {str(e)}", exc_info=True)
        return f"❌ Web-Fehler: {str(e)}"

# =================
# TOOL-AUSWAHL LOGIK
# =================

def _is_valid_command(cmd: str) -> bool:
    """
    Prüft ob String ein gültiger Shell-Command ist
    (nicht nur ein Pfad oder Dateiname)
    """
    tool_logger.debug(f"🔍 Validiere Command: {cmd}")
    
    # Nur Pfad? → KEIN Command
    if cmd.startswith('/') and ' ' not in cmd:
        tool_logger.debug(f"❌ Nur Pfad, kein Command: {cmd}")
        return False
    
    # Nur Dateiname? → KEIN Command
    if '.' in cmd and ' ' not in cmd and not any(c in cmd for c in ['|', '>', '<', '&']):
        tool_logger.debug(f"❌ Nur Dateiname, kein Command: {cmd}")
        return False
    
    # Valide Command-Patterns
    valid_patterns = [
        r'^(ls|pwd|cat|echo|grep|find|date|whoami|df|du|free|top|ps)\s',  # Standard-Commands mit Argumenten
        r'^(ls|pwd|date|whoami)$',  # Standard-Commands ohne Argumente
        r'\|',  # Pipes
        r'>',   # Redirects
        r'&&',  # Chain
    ]
    
    is_valid = any(re.search(pattern, cmd) for pattern in valid_patterns)
    tool_logger.debug(f"{'✅' if is_valid else '❌'} Command-Validierung: {cmd} → {is_valid}")
    return is_valid

# =================
# TOOL-AUSWAHL LOGIK
# =================

def _is_valid_command(cmd: str) -> bool:
    """
    Prüft ob String ein gültiger Shell-Command ist
    (nicht nur ein Pfad oder Dateiname)
    """
    tool_logger.debug(f"🔍 Validiere Command: {cmd}")
    
    # Nur Pfad? → KEIN Command
    if cmd.startswith('/') and ' ' not in cmd:
        tool_logger.debug(f"❌ Nur Pfad, kein Command: {cmd}")
        return False
    
    # Nur Dateiname? → KEIN Command
    if '.' in cmd and ' ' not in cmd and not any(c in cmd for c in ['|', '>', '<', '&']):
        tool_logger.debug(f"❌ Nur Dateiname, kein Command: {cmd}")
        return False
    
    # Valide Command-Patterns
    valid_patterns = [
        r'^(ls|pwd|cat|echo|grep|find|date|whoami|df|du|free|top|ps)\s',  # Standard-Commands mit Argumenten
        r'^(ls|pwd|date|whoami)$',  # Standard-Commands ohne Argumente
        r'\|',  # Pipes
        r'>',   # Redirects
        r'&&',  # Chain
    ]
    
    is_valid = any(re.search(pattern, cmd) for pattern in valid_patterns)
    tool_logger.debug(f"{'✅' if is_valid else '❌'} Command-Validierung: {cmd} → {is_valid}")
    return is_valid

def analyze_and_execute(prompt: str) -> str:
    """
    Analysiert Prompt und führt Tools aus - MIT LOOP-PROTECTION
    
    Unterstützt Marker-Pattern für exakte Content-Übergabe:
    "Erstelle DATEI mit <<<CONTENT\n...\n<<<END"
    """
    prompt_lower = prompt.lower()
    results: list[str] = []
    
    # === MARKER-PATTERN FÜR EXAKTE CONTENT-ÜBERGABE ===
    # Prüfe auf <<<CONTENT ... <<<END Marker
    marker_pattern = r'<<<CONTENT\s*\n(.*?)\n<<<END'
    marker_match = re.search(marker_pattern, prompt, re.DOTALL)
    
    if marker_match:
        # Exakter Content zwischen Markern gefunden
        exact_content = marker_match.group(1)
        
        # Extrahiere Dateinamen aus dem Teil VOR den Markern
        pre_marker_text = prompt[:marker_match.start()]
        filename_patterns = [
            r'(?:erstelle?|create|schreibe?)\s+(?:datei\s+)?([a-zA-Z0-9_.\-/]+\.[\w]+)',
            r'\b([a-zA-Z0-9_.\-/]+\.(?:txt|py|md|json|yaml|yml|sh|conf|cfg))\b',
        ]
        
        filename = None
        for pattern in filename_patterns:
            file_match = re.search(pattern, pre_marker_text, re.IGNORECASE)
            if file_match:
                filename = file_match.group(1).strip()
                break
        
        if filename and exact_content:
            result = write_file(filename, exact_content)
            return f"✏️ Datei schreiben (Marker-Mode):\n{result}"
        else:
            return "❌ Marker-Pattern erkannt, aber Dateiname fehlt oder Content ist leer"
    
    # Prüfe zuerst auf exklusive Trigger (WRITE/DELETE haben Vorrang vor READ)
    write_triggers = ['schreiben', 'schreib', 'write', 'erstellen', 'erstelle', 'create', 'speichern', 'speichere', 'save']
    delete_triggers = ['löschen', 'lösche', 'lösch', 'delete', 'remove', 'entfernen', 'entferne']
    
    has_write_trigger = any(word in prompt_lower for word in write_triggers)
    has_delete_trigger = any(word in prompt_lower for word in delete_triggers)
    
    # === DATEI LESEN === (nur wenn KEIN WRITE/DELETE-Trigger)
    read_triggers = ['lesen', 'lies', 'read', 'zeigen', 'zeige', 'show', 'inhalt', 'anzeigen', 'öffne', 'open', 'cat']
    if any(word in prompt_lower for word in read_triggers) and not has_write_trigger and not has_delete_trigger:
        # Suche nach Dateinamen (nur alphanumerische Zeichen, Punkte, Unterstriche, Bindestriche)
        file_patterns = [
            r'\b([a-zA-Z0-9_.\-/]+\.(?:txt|py|md|json|yaml|yml|log|sh|conf|cfg))\b',  # Dateiendungen mit Wortgrenzen (PRIO!)
            r'(?:datei|file)[\s:]+([a-zA-Z0-9_.\-/]+)',  # "Datei: test.txt" oder "Datei test.txt"
            r'(?:von|of|from)[\s:]+([a-zA-Z0-9_.\-/]+\.[\w]+)',  # "inhalt von test.txt"
            r'(?:lies|lesen|zeige?|show|read|open|cat)[\s:]+([a-zA-Z0-9_.\-/]+)',  # "Lies: test.txt"
        ]
        
        file_match = None
        for pattern in file_patterns:
            file_match = re.search(pattern, prompt, re.IGNORECASE)
            if file_match:
                break
        
        if file_match:
            filename = file_match.group(1).strip()
            # Bereinige JSON-Artefakte falls vorhanden
            filename = filename.rstrip('"}\']')
            result = read_file(filename)
            results.append(f"🔍 Datei lesen:\n{result}")
    
    # Datei schreiben - VERBESSERTE ERKENNUNG (nur bei WRITE-Trigger)
    if has_write_trigger:
        # Suche nach Dateinamen (nur bei WRITE-Kontext, nicht bei READ)
        file_patterns = [
            r'(?:erstelle?|create|schreibe?|speichere?)\s+(?:eine?\s+)?(?:datei\s+)?([a-zA-Z0-9_.\-/]+\.[\w]+)',  # "Erstelle test.py"
            r'\b([a-zA-Z0-9_.\-/]+\.(?:txt|py|md|json|yaml|yml|sh|conf|cfg))\b',  # Standalone filename
        ]
        
        file_match = None
        for pattern in file_patterns:
            file_match = re.search(pattern, prompt, re.IGNORECASE)
            if file_match:
                break
        
        # Suche nach Inhalt - INTELLIGENTE ERKENNUNG (JSON-sicher)
        content_patterns = [
            r'mit\s+(.+?)"\s*}',  # "mit CODE"} - JSON-Ende
            r'(?:inhalt|content|text)[\s:]*(.+?)"\s*}',  # "inhalt: CODE"}
            r':\s*(.+?)"\s*}',  # ": CODE"}
            r'mit\s+(.+)$',  # Fallback: gesamter Rest bei einfachen Befehlen
        ]
        
        content_match = None
        for pattern in content_patterns:
            content_match = re.search(pattern, prompt, re.IGNORECASE)
            if content_match:
                break
        
        if file_match and content_match:
            filename = file_match.group(1).strip().rstrip('"}\']')
            content = content_match.group(1).strip()
            # Entferne umgebende Anführungszeichen und escape-Sequenzen
            content = content.strip('"\'')
            # Ersetze escaped quotes
            content = content.replace('\\"', '"').replace("\\'", "'")
            result = write_file(filename, content)
            results.append(f"✏️ Datei schreiben:\n{result}")
    
    # Datei löschen - VERBESSERTE ERKENNUNG
    if has_delete_trigger:
        # Suche nach Dateinamen (nur alphanumerische Zeichen, Punkte, Unterstriche, Bindestriche)
        file_patterns = [
            r'(?:datei|file)\s+([a-zA-Z0-9_.\-/]+)',
            r'\b([a-zA-Z0-9_.\-/]+\.(?:txt|py|md|json|yaml|yml|sh|conf|cfg|log))\b',
            r'(?:lösche?|delete|remove|entferne?)\s+(?:datei\s+)?([a-zA-Z0-9_.\-/]+\.[\w]+)'
        ]
        
        file_match = None
        for pattern in file_patterns:
            file_match = re.search(pattern, prompt, re.IGNORECASE)
            if file_match:
                break
        
        if file_match:
            filename = file_match.group(1).strip().rstrip('"}\']')
            result = delete_file(filename)
            results.append(f"🗑️ Datei löschen:\n{result}")
    
    # Verzeichnis auflisten - VERBESSERTE ERKENNUNG (nur bei explizitem Trigger)
    list_triggers = ['liste', 'list', 'auflisten', 'aufliste', 'verzeichnis', 'directory', 'ordner', 'folder', 'dateien', 'files', 'zeige dateien', 'show files', 'ls']
    # Aber NICHT triggern wenn DELETE/READ/WRITE aktiv ist
    if any(word in prompt_lower for word in list_triggers) and not (has_delete_trigger or has_write_trigger or any(word in prompt_lower for word in read_triggers)):
        # Suche nach Pfad (nur alphanumerische Zeichen, Punkte, Unterstriche, Bindestriche, Slashes)
        path_patterns = [
            r'(?:verzeichnis|directory|ordner|folder|in)\s+([a-zA-Z0-9_.\-/]+)',  # "Verzeichnis workspace"
            r'(?:von|of|at)\s+([a-zA-Z0-9_.\-/]+)',  # "dateien von workspace"
        ]
        
        path = "."  # Default: aktuelles Verzeichnis
        for pattern in path_patterns:
            path_match = re.search(pattern, prompt, re.IGNORECASE)
            if path_match:
                path = path_match.group(1).strip().rstrip('"}\']')
                break
        
        result = list_files(path)
        results.append(f"📂 Verzeichnis auflisten:\n{result}")
    
    # === SHELL-KOMMANDO MIT STRENGER VALIDIERUNG ===
    # Lade Shell-Execution Config
    shell_config = config.get("shell_execution", {})
    shell_enabled = shell_config.get("enabled", SANDBOX == False)  # Default: nur wenn Sandbox aus
    require_trigger = shell_config.get("require_explicit_trigger", True)
    
    # Explizite Shell-Trigger
    shell_triggers = ['führe aus', 'execute', 'run command', 'kommando ausführen', 'shell']
    has_shell_trigger = any(trigger in prompt_lower for trigger in shell_triggers)
    
    if shell_enabled and (has_shell_trigger or not require_trigger):
        # Nur bei EXPLIZITEN Triggern oder wenn Trigger-Requirement deaktiviert
        cmd_patterns = [
            r'(?:führe|execute|run)\s+(?:kommando\s+)?["\']([^"\']+)["\']',
            r'kommando[\s:]*["\']([^"\']+)["\']',
        ]
        
        # Backticks NUR wenn expliziter Trigger vorhanden
        if has_shell_trigger:
            cmd_patterns.append(r'`([^`]+)`')
        
        for pattern in cmd_patterns:
            cmd_match = re.search(pattern, prompt, re.IGNORECASE)
            if cmd_match:
                cmd = cmd_match.group(1)
                
                # === COMMAND-VALIDIERUNG ===
                if _is_valid_command(cmd):
                    result = run_shell(cmd)
                    results.append(f"💻 Shell-Kommando:\n{result}")
                    tool_logger.info(f"✅ Shell-Command validiert und ausgeführt: {cmd}")
                else:
                    tool_logger.warning(f"🚫 Ungültiges Kommando blockiert: {cmd}")
                    results.append(f"🚫 Ungültiges Kommando blockiert: {cmd}\n💡 Nur valide Shell-Commands werden ausgeführt.")
                break
    elif not shell_enabled:
        # Prüfe ob User ein Shell-Command wollte
        if has_shell_trigger:
            tool_logger.info("🔒 Shell-Command angefordert, aber deaktiviert")
            results.append(
                "🔒 Shell-Kommandos sind deaktiviert.\n"
                "💡 Aktiviere in config/config.yaml: shell_execution.enabled = true"
            )
    
    # Web-Request (nur wenn explizit angefordert, nicht automatisch bei URLs)
    # AUSSCHLUSS: Localhost/127.0.0.1 URLs (interne Server-Aufrufe)
    web_triggers = ['hole', 'hol', 'fetch', 'lade', 'laden', 'abrufen', 'download', 'webseite', 'website']
    if any(word in prompt_lower for word in web_triggers):
        url_patterns = [
            r'(https?://(?!127\.0\.0\.1|localhost)[^\s]+)',  # NICHT localhost/127.0.0.1
            r'(www\.[^\s]+)',
            r'(?:hole|fetch|lade)\s+([a-zA-Z0-9.-]+\.(?:com|org|net|de|edu|gov|io|co))'
        ]
        
        for pattern in url_patterns:
            url_match = re.search(pattern, prompt, re.IGNORECASE)
            if url_match:
                url = url_match.group(1)
                # Zusätzliche Sicherheit: Ignoriere localhost auch in anderen Formen
                if '127.0.0.1' in url or 'localhost' in url.lower():
                    continue
                result = fetch(url)
                results.append(f"🌐 Web-Request:\n{result}")
                break
    
    if not results:
        return """🤔 Keine spezifischen Tools erkannt. 

📋 **Verfügbare Tools mit Beispielen:**

• **Datei lesen:**
  - "Lies Datei config.yaml"
  - "Zeige test123.txt"
  - "Zeige inhalt von test.txt"
  - "Zeige mir hello.py"

• **Datei schreiben:**
  - "Erstelle Datei hello.txt mit Hallo Welt"
  - "Schreibe test.py mit 'print(hello)'"
  - "Erstelle eine Datei readme.md mit Text"

• **Verzeichnis:**
  - "Liste alle Dateien auf"
  - "Zeige Dateien im workspace"
  - "Liste Verzeichnis /tmp auf"
  - "Ordner . anzeigen"

• **Shell:**
  - "Führe Kommando 'ls -la' aus"
  - "Execute 'pwd'"

• **Web:**
  - "Hole github.com"
  - "Lade Webseite example.com"

🔒 **Sandbox-Modus aktiv** - Dateien werden sicher in der Sandbox erstellt."""
    
    return "\n\n".join(results)

# =================
# API ENDPOINTS
# =================

@app.route("/", methods=["GET"])
def root():
    """Root-Endpoint mit Übersicht"""
    return f"""
    <html>
    <head>
        <title>🤖 LocalAgent-Pro Server</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .status {{ color: green; font-weight: bold; }}
            .endpoint {{ background: #f5f5f5; padding: 10px; margin: 5px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>🤖 LocalAgent-Pro Server</h1>
        <div class="status">✅ Server läuft erfolgreich!</div>
        
        <h2>📋 Konfiguration</h2>
        <ul>
            <li><strong>Modell:</strong> {LLM_MODEL}</li>
            <li><strong>Sandbox:</strong> {"✅ Aktiv" if SANDBOX else "❌ Deaktiviert"}</li>
            <li><strong>Sandbox-Pfad:</strong> {SANDBOX_PATH}</li>
            <li><strong>Erlaubte Domains:</strong> {len(ALLOWED_DOMAINS)}</li>
            <li><strong>OpenWebUI Port:</strong> {OPEN_WEBUI_PORT}</li>
        </ul>
        
        <h2>🔗 API Endpoints</h2>
        <div class="endpoint"><strong>GET /health</strong> - Server Status</div>
        <div class="endpoint"><strong>GET /v1/models</strong> - Verfügbare Modelle</div>
        <div class="endpoint"><strong>POST /v1/chat/completions</strong> - Chat API (OpenAI-kompatibel)</div>
        <div class="endpoint"><strong>POST /test</strong> - Tool-Test Endpoint</div>
        
        <h2>🎯 OpenWebUI Integration</h2>
        <p><strong>API Base URL für OpenWebUI:</strong></p>
        <div class="endpoint">http://127.0.0.1:8001/v1</div>
        
        <p>Füge diese URL in OpenWebUI unter "Settings → Connections → OpenAI API" ein.</p>
    </body>
    </html>
    """

@app.route("/metrics", methods=["GET"])
def metrics():
    """Prometheus Metrics Endpoint"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route("/health", methods=["GET"])
def health():
    """Health Check Endpoint"""
    api_logger.debug("📡 Health Check angefordert")
    request_count.labels(endpoint='/health', status='success').inc()
    
    health_data = {
        "status": "ok",
        "server_time": int(time.time()),
        "model": LLM_MODEL,
        "sandbox": SANDBOX,
        "sandbox_path": SANDBOX_PATH,
        "allowed_domains": ALLOWED_DOMAINS,
        "auto_whitelist_enabled": AUTO_WHITELIST_ENABLED,
        "auto_whitelist_count": len(domain_whitelist_cache) if AUTO_WHITELIST_ENABLED else 0,
        "open_webui_port": OPEN_WEBUI_PORT
    }
    
    api_logger.info("✅ Health Check erfolgreich")
    return jsonify(health_data)

@app.route("/whitelist", methods=["GET"])
def get_whitelist():
    """Zeigt Auto-Whitelist an"""
    api_logger.debug("📡 Whitelist angefordert")
    
    whitelist_data = {
        "auto_whitelist_enabled": AUTO_WHITELIST_ENABLED,
        "wildcard_active": "*" in ALLOWED_DOMAINS,
        "approved_domains": sorted(list(domain_whitelist_cache)) if AUTO_WHITELIST_ENABLED else [],
        "count": len(domain_whitelist_cache) if AUTO_WHITELIST_ENABLED else 0,
        "file": AUTO_WHITELIST_FILE if AUTO_WHITELIST_ENABLED else None
    }
    
    api_logger.info(f"✅ Whitelist gesendet: {whitelist_data['count']} Domains")
    return jsonify(whitelist_data)

@app.route("/v1", methods=["GET"])
def api_v1_info():
    """API v1 Info Endpoint"""
    api_logger.debug("📡 /v1 Info angefordert")
    
    info_data = {
        "version": "1.0",
        "endpoints": {
            "health": "GET /health",
            "models": "GET /v1/models",
            "chat_completions": "POST /v1/chat/completions"
        },
        "server": "LocalAgent-Pro",
        "ollama": "active",
        "gpu_acceleration": "enabled"
    }
    
    return jsonify(info_data)

@app.route("/v1/models", methods=["GET"])
def list_models():
    """OpenAI-kompatible Models API"""
    api_logger.debug("📡 Models-Liste angefordert")
    
    models_data = {
        "object": "list",
        "data": [
            {
                "id": "localagent-pro",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "localagent-pro"
            },
            {
                "id": LLM_MODEL,
                "object": "model", 
                "created": int(time.time()),
                "owned_by": "localagent-pro"
            }
        ]
    }
    
    api_logger.info(f"✅ Models-Liste gesendet: 2 Modelle (localagent-pro, {LLM_MODEL})")
    return jsonify(models_data)

@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    """OpenAI-kompatible Chat Completions API - MIT LOOP-PROTECTION"""
    request_id = str(uuid.uuid4())[:8]
    api_logger.info(f"📨 Chat Completion Request [{request_id}] empfangen")
    
    # Metrics
    active_requests.inc()
    start_time = time.time()
    
    try:
        data: Dict[str, Any] = request.get_json(force=True)
        api_logger.debug(f"📦 Request Data [{request_id}]: {truncate_long_content(str(data), 500)}")
        
        messages: List[Dict[str, str]] = data.get("messages", [])
        model: str = data.get("model", "localagent-pro")
        
        api_logger.debug(f"💬 Anzahl Messages: {len(messages)}, Modell: {model}")
        
        # === LOOP-PROTECTION: Extrahiere User-Prompt für Tracking ===
        user_prompt_for_tracking = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_prompt_for_tracking = msg.get("content", "")
                break
        
        if user_prompt_for_tracking:
            prompt_hash = hashlib.md5(user_prompt_for_tracking.encode()).hexdigest()
            current_time = time.time()
            
            if prompt_hash in recent_requests:
                req_data = recent_requests[prompt_hash]
                time_diff = current_time - req_data["last_time"]
                
                # Selber Request innerhalb Loop-Detection-Window?
                if time_diff < LOOP_DETECTION_WINDOW:
                    req_data["count"] += 1
                    
                    # Mehr als erlaubte Wiederholungen? → BLOCK
                    if req_data["count"] > MAX_REQUEST_REPEATS:
                        api_logger.warning(
                            f"🚫 Loop erkannt [{request_id}]: "
                            f"'{user_prompt_for_tracking[:50]}...' ({req_data['count']}x in {time_diff:.1f}s)"
                        )
                        
                        # Metrics
                        loop_detections.inc()
                        request_count.labels(endpoint='/v1/chat/completions', status='loop_blocked').inc()
                        active_requests.dec()
                        
                        return jsonify({
                            "id": f"chatcmpl-{request_id}",
                            "object": "chat.completion",
                            "created": int(current_time),
                            "model": model,
                            "choices": [{
                                "index": 0,
                                "finish_reason": "stop",
                                "message": {
                                    "role": "assistant",
                                    "content": (
                                        "🚫 **Loop Protection aktiviert**\n\n"
                                        "Deine Anfrage wurde mehrfach innerhalb kurzer Zeit wiederholt.\n"
                                        "Bitte formuliere deine Anfrage anders oder warte 2 Sekunden."
                                    )
                                }
                            }]
                        })
                else:
                    # Reset counter nach Loop-Detection-Window
                    req_data["count"] = 1
                
                req_data["last_time"] = current_time
            else:
                # Neuer Request
                recent_requests[prompt_hash] = {"count": 1, "last_time": current_time}
            
            # Cleanup alte Requests (älter als 60 Sekunden)
            old_hashes = [h for h, d in recent_requests.items() if current_time - d["last_time"] > 60]
            for h in old_hashes:
                del recent_requests[h]
        
        # === SYSTEM-PROMPT: Strikte Tool-Ausführung ohne Kreativität ===
        SYSTEM_PROMPT = """Du bist ein strikt funktionaler Werkzeug-Agent für LocalAgent-Pro.

WICHTIG - EXAKTE CONTENT-ÜBERNAHME:
- Wenn der User schreibt: "Erstelle DATEI mit <<<CONTENT...<<<END", dann ist ALLES zwischen den Markern der exakte Dateiinhalt.
- Du darfst diesen Inhalt NIEMALS: umformulieren, kürzen, ergänzen, erklären oder in eigene Worte fassen.
- Zeilenumbrüche, Leerzeichen, Anführungszeichen, f-Strings, Klammern usw. MÜSSEN unverändert bleiben.
- Ohne Marker: Alles NACH "mit" ist der Dateiinhalt - ohne Kommentare oder Formatierung.

DATEI-OPERATIONEN:
- "Erstelle/Schreibe DATEI..." → write_file(path, content) 
- "Lies/Zeige DATEI..." → read_file(path)
- "Lösche/Entferne DATEI..." → delete_file(path)

REGELN:
1. Du antwortest NIEMALS mit ausführlichem Text - nur Tool-Actions.
2. Du erfindest KEINE weiteren Schritte.
3. Content wird 1:1 übernommen - KEINE Kreativität!"""
        
        # Letzten User-Prompt extrahieren
        user_prompt = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_prompt = msg.get("content", "")
                break
        
        api_logger.info(f"👤 User Prompt [{request_id}]: {truncate_long_content(user_prompt, 200)}")
        
        if not user_prompt:
            response_text = """Hallo! Ich bin LocalAgent-Pro. 👋

🔒 **Sicherheitsmodus aktiv:**
   - Sandbox isoliert alle Dateioperationen
   - Shell-Kommandos sind deaktiviert
   - Nur erlaubte Domains können abgerufen werden

📋 **Ich kann dir helfen mit:**
   • Dateien lesen/schreiben (in Sandbox)
   • Verzeichnisse auflisten
   • Webseiten abrufen (nur erlaubte Domains)
   • Fragen beantworten (via TinyLlama)

💡 **Beispiel-Anfragen:**
   - "Erstelle Datei test.txt mit Hello World"
   - "Liste alle Dateien auf"
   - "Lies Datei test.txt"
   - "Zeige mir die erlaubten Domains"

**Wie kann ich dir helfen?**
"""
            api_logger.debug(f"💬 Keine User-Eingabe, sende Willkommensnachricht [{request_id}]")
        else:
            # === INTELLIGENTE RÜCKFRAGE bei unklaren Anfragen ===
            uncertainty_indicators = [
                'vielleicht', 'möglicherweise', 'eventuell', 'nicht sicher',
                'denke ich', 'glaube ich', 'könnte', 'würde'
            ]
            
            is_uncertain = any(indicator in user_prompt.lower() for indicator in uncertainty_indicators)
            
            # Prüfe ob Tools erkannt werden
            tool_results = analyze_and_execute(user_prompt)
            
            # Falls Tools erkannt wurden, nutze Tool-Ergebnisse
            if not tool_results.startswith("🤔 Keine spezifischen Tools erkannt"):
                response_text = f"🤖 LocalAgent-Pro hat deine Anfrage bearbeitet:\n\n{tool_results}"
                api_logger.debug(f"🛠️ Tool-Ergebnis [{request_id}]: {truncate_long_content(tool_results, 300)}")
            else:
                # Keine Tools → Nutze Ollama für generative Antwort
                api_logger.info(f"🤖 Generiere Antwort mit Ollama [{request_id}]")
                
                ollama_start = time.time()
                ollama_response = ollama_client.generate(
                    prompt=user_prompt,
                    temperature=data.get("temperature", 0.7),
                    max_tokens=data.get("max_tokens", 500)
                )
                ollama_duration = time.time() - ollama_start
                
                if ollama_response:
                    response_text = ollama_response
                    ollama_calls.labels(model=LLM_MODEL, status='success').inc()
                    api_logger.info(f"✅ Ollama-Antwort generiert [{request_id}]: {len(response_text)} Zeichen in {ollama_duration:.2f}s")
                else:
                    response_text = "Es tut mir leid, ich konnte keine Antwort generieren. Bitte versuche es erneut."
                    ollama_calls.labels(model=LLM_MODEL, status='failed').inc()
                    api_logger.warning(f"⚠️ Ollama-Antwort leer [{request_id}]")
        
        # Streaming-Support prüfen
        stream = data.get("stream", False)
        
        if stream:
            # Streaming-Response generieren
            api_logger.info(f"📡 Streaming aktiviert [{request_id}]")
            
            def generate_stream():
                # Sende Response als Stream-Chunks
                chunks = response_text.split()
                
                for i, word in enumerate(chunks):
                    chunk_data = {
                        "id": f"chatcmpl-{request_id}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": model,
                        "choices": [{
                            "index": 0,
                            "delta": {"content": word + " "} if i < len(chunks) - 1 else {"content": word},
                            "finish_reason": None if i < len(chunks) - 1 else "stop"
                        }]
                    }
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                
                # Final chunk
                yield "data: [DONE]\n\n"
            
            api_logger.info(f"✅ Stream gestartet [{request_id}]: {len(response_text.split())} Chunks")
            return Response(generate_stream(), mimetype='text/event-stream')
        
        # Non-streaming Response
        
        response_obj = {
            "id": f"chatcmpl-{str(uuid.uuid4())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "finish_reason": "stop",
                "message": {
                    "role": "assistant", 
                    "content": response_text
                }
            }],
            "usage": {
                "prompt_tokens": len(user_prompt.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens": len(user_prompt.split()) + len(response_text.split())
            }
        }
        
        api_logger.info(
            f"✅ Chat Completion erfolgreich [{request_id}]: "
            f"prompt_tokens={len(user_prompt.split())}, "
            f"completion_tokens={len(response_text.split())}"
        )
        
        # Metrics
        request_duration.labels(endpoint='/v1/chat/completions').observe(time.time() - start_time)
        request_count.labels(endpoint='/v1/chat/completions', status='success').inc()
        active_requests.dec()
        
        return jsonify(response_obj)
        
    except Exception as e:
        api_logger.error(f"❌ Chat Completion Fehler [{request_id}]: {str(e)}", exc_info=True)
        
        # Metrics
        request_count.labels(endpoint='/v1/chat/completions', status='error').inc()
        active_requests.dec()
        
        return jsonify({
            "error": {
                "message": f"Fehler bei der Anfrage: {str(e)}",
                "type": "internal_server_error"
            }
        }), 500

@app.route("/test", methods=["GET", "POST"])
def test_tool():
    """Test-Endpoint für direkte Tool-Tests (GET & POST)"""
    api_logger.info("🧪 Test-Endpoint aufgerufen")
    
    try:
        # Unterstütze sowohl GET (?prompt=...) als auch POST (JSON)
        prompt: str = ""
        if request.method == "GET":
            prompt = request.args.get("prompt", "")
        else:
            # POST: Versuche JSON zu parsen, falls vorhanden
            try:
                data: Dict[str, Any] = request.get_json(silent=True) or {}
                prompt = data.get("prompt", "")
            except Exception:
                # Fallback: Kein JSON oder ungültiges Format
                prompt = ""
        
        api_logger.debug(f"🧪 Test-Prompt: {prompt}")
        
        if not prompt:
            api_logger.warning("⚠️ Test-Request ohne Prompt")
            return jsonify({
                "error": "Kein Prompt angegeben",
                "hint": "Sende GET mit ?prompt=... oder POST mit {\"prompt\": \"...\"}",
                "examples": {
                    "GET": "/test?prompt=Lies%20demo.py",
                    "POST": "{\"prompt\": \"Erstelle demo.py mit print('Hello')\"}"
                }
            }), 400
        
        result = analyze_and_execute(prompt)
        
        test_result = {
            "prompt": prompt,
            "result": result,
            "timestamp": int(time.time())
        }
        
        api_logger.info(f"✅ Test erfolgreich: prompt_length={len(prompt)}, result_length={len(result)}")
        return jsonify(test_result)
        
    except Exception as e:
        api_logger.error(f"❌ Test-Fehler: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# =================
# SERVER START
# =================

if __name__ == "__main__":
    # Sandbox-Verzeichnis erstellen
    if SANDBOX and not os.path.exists(SANDBOX_PATH):
        os.makedirs(SANDBOX_PATH, exist_ok=True)
        print(f"📁 Sandbox erstellt: {SANDBOX_PATH}")
    
    print("🚀 LocalAgent-Pro Server (OpenWebUI-kompatibel) startet...")
    print(f"🧠 Modell: {LLM_MODEL}")
    print(f"🔒 Sandbox: {'✅ Aktiv' if SANDBOX else '❌ Deaktiviert'}")
    print(f"📁 Sandbox-Pfad: {SANDBOX_PATH}")
    print(f"🌐 Erlaubte Domains: {len(ALLOWED_DOMAINS)} ({', '.join(ALLOWED_DOMAINS[:2])}...)")
    print(f"📡 Agent-Server: http://localhost:8001")
    print(f"🌐 Browser-Interface: http://127.0.0.1:8001")
    print(f"🎯 OpenWebUI API: http://127.0.0.1:8001/v1")
    print(f"📱 OpenWebUI läuft auf Port: {OPEN_WEBUI_PORT}")
    print("\n" + "="*60)
    print("✅ BEREIT FÜR OPENWEBUI!")
    print("💡 API Base URL: http://127.0.0.1:8001/v1")
    print("💡 Füge diese URL in OpenWebUI → Settings → Connections ein")
    print("="*60)
    
    app.run(host="0.0.0.0", port=8001, debug=False)