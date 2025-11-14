#!/usr/bin/env python3
"""
LocalAgent-Pro Server mit automatischer Tool-Auswahl
"""

from flask import Flask, request, jsonify
import os
import yaml
import re
import requests
import subprocess
from urllib.parse import urlparse

# Config laden
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.yaml")

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    print(f"❌ Config nicht gefunden: {CONFIG_PATH}")
    exit(1)

# System-Prompt laden
SYSTEM_PROMPT_PATH = os.path.join(BASE_DIR, "config", "system_prompt.txt")
try:
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    SYSTEM_PROMPT = "Du bist LocalAgent-Pro, ein lokaler KI-Agent."

# Konfiguration
SANDBOX = config.get("sandbox", True)
SANDBOX_PATH = config.get("sandbox_path", os.path.expanduser("~/localagent_sandbox"))
ALLOWED_DOMAINS = config.get("allowed_domains", [])
OPEN_WEBUI_PORT = config.get("open_webui_port", 3000)

llm_cfg = config.get("llm", {})
LLM_BASE_URL = llm_cfg.get("base_url", "http://localhost:11434/v1")  
LLM_MODEL = llm_cfg.get("model", "llama2")

app = Flask(__name__)

# =================
# TOOL FUNKTIONEN
# =================

def _resolve_path(path: str) -> str:
    """Wandelt Pfad in Sandbox-Pfad um, falls Sandbox aktiv"""
    if SANDBOX:
        clean_path = path.lstrip("/").lstrip("\\")
        resolved = os.path.join(SANDBOX_PATH, clean_path)
        os.makedirs(os.path.dirname(resolved) if os.path.dirname(resolved) else SANDBOX_PATH, exist_ok=True)
        return resolved
    return os.path.abspath(path)

def read_file(path: str) -> str:
    """Liest Dateiinhalt"""
    try:
        rpath = _resolve_path(path)
        if not os.path.exists(rpath):
            return f"❌ Datei nicht gefunden: {rpath}"
        
        with open(rpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        location = f" (Sandbox: {rpath})" if SANDBOX else f" (Live: {rpath})"
        return f"📄 Datei gelesen{location}:\n\n{content}"
    except Exception as e:
        return f"❌ Fehler beim Lesen: {str(e)}"

def write_file(path: str, content: str) -> str:
    """Schreibt Dateiinhalt"""
    try:
        rpath = _resolve_path(path)
        
        with open(rpath, "w", encoding="utf-8") as f:
            f.write(content)
        
        location = f" (Sandbox: {rpath})" if SANDBOX else f" (Live: {rpath})"
        return f"✅ Datei erstellt{location}\n📝 {len(content)} Zeichen geschrieben"
    except Exception as e:
        return f"❌ Fehler beim Schreiben: {str(e)}"

def list_files(path: str = ".") -> str:
    """Listet Verzeichnisinhalt auf"""
    try:
        rpath = _resolve_path(path)
        
        if not os.path.exists(rpath):
            return f"❌ Verzeichnis nicht gefunden: {rpath}"
        
        if not os.path.isdir(rpath):
            return f"❌ Kein Verzeichnis: {rpath}"
        
        entries = []
        for item in sorted(os.listdir(rpath)):
            item_path = os.path.join(rpath, item)
            if os.path.isdir(item_path):
                entries.append(f"📁 {item}/")
            else:
                size = os.path.getsize(item_path)
                entries.append(f"📄 {item} ({size} bytes)")
        
        location = f" (Sandbox: {rpath})" if SANDBOX else f" (Live: {rpath})"
        if not entries:
            return f"📂 Verzeichnis leer{location}"
        
        return f"📂 Verzeichnisinhalt{location}:\n" + "\n".join(entries)
    except Exception as e:
        return f"❌ Fehler beim Auflisten: {str(e)}"

def run_shell(cmd: str) -> str:
    """Führt Shell-Kommando aus"""
    if SANDBOX:
        return "🚫 Shell-Kommandos sind im Sandbox-Modus deaktiviert.\n" \
               "💡 Setze 'sandbox: false' in config/config.yaml und starte den Server neu."
    
    if not cmd.strip():
        return "❌ Leeres Kommando"
    
    try:
        # Sicherheitsprüfungen
        dangerous_cmds = ['rm -rf', 'sudo', 'su -', 'chmod +x', 'mkfs', 'dd if=', 'format']
        if any(danger in cmd.lower() for danger in dangerous_cmds):
            return f"🚫 Gefährliches Kommando blockiert: {cmd}"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
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
        return f"⏰ Timeout nach 30s: {cmd}"
    except Exception as e:
        return f"❌ Shell-Fehler: {str(e)}"

def fetch(url: str) -> str:
    """Lädt Webseiteninhalte"""
    if not url.strip():
        return "❌ Leere URL"
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        domain = urlparse(url).netloc.lower()
        
        # Domain-Check
        allowed = any(domain == d.lower() or domain.endswith('.' + d.lower()) 
                     for d in ALLOWED_DOMAINS)
        
        if not allowed:
            return f"🚫 Domain blockiert: {domain}\n" \
                   f"💡 Erlaubte Domains: {', '.join(ALLOWED_DOMAINS)}"
        
        headers = {'User-Agent': 'LocalAgent-Pro/1.0'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        content = response.text[:10000]
        if len(response.text) > 10000:
            content += f"\n\n... (auf 10KB begrenzt, Original: {len(response.text)} Zeichen)"
        
        return f"🌐 Webseite geladen: {url}\n📊 Status: {response.status_code}\n\n{content}"
        
    except Exception as e:
        return f"❌ Web-Fehler: {str(e)}"

# =================
# INTELLIGENTE TOOL-AUSWAHL
# =================

def analyze_and_execute(prompt: str) -> str:
    """
    Analysiert einen natürlichsprachigen Prompt und führt passende Tools aus.
    
    Args:
        prompt (str): Natürlichsprachige Eingabe
    Returns:
        str: Formatierte Ergebnisse der ausgeführten Operationen
    """
    prompt_lower = prompt.lower()
    results = []
    
    # Datei lesen
    if any(word in prompt_lower for word in ['lesen', 'read', 'zeigen', 'show', 'inhalt']):
        file_match = re.search(r'(?:datei|file)\s+([^\s]+)', prompt, re.IGNORECASE)
        if not file_match:
            file_match = re.search(r'([^\s]+\.(?:txt|py|md|json|yaml|yml|log))', prompt, re.IGNORECASE)
        
        if file_match:
            filename = file_match.group(1)
            result = read_file(filename)
            results.append(f"🔍 Datei lesen: {result}")
    
    # Datei schreiben  
    if any(word in prompt_lower for word in ['schreiben', 'write', 'erstellen', 'create', 'speichern']):
        file_match = re.search(r'(?:datei|file)\s+([^\s]+)', prompt, re.IGNORECASE)
        if not file_match:
            file_match = re.search(r'([^\s]+\.(?:txt|py|md|json))', prompt, re.IGNORECASE)
        
        content_patterns = [
            r'(?:inhalt|content|text)[\s:]*["\']([^"\']+)["\']',
            r'mit\s+["\']([^"\']+)["\']',
            r'["\']([^"\']{10,})["\']'  # Längere Texte in Anführungszeichen
        ]
        
        content_match = None
        for pattern in content_patterns:
            content_match = re.search(pattern, prompt, re.IGNORECASE)
            if content_match:
                break
        
        if file_match and content_match:
            filename = file_match.group(1)
            content = content_match.group(1)
            result = write_file(filename, content)
            results.append(f"✏️ Datei schreiben: {result}")
    
    # Verzeichnis auflisten
    if any(word in prompt_lower for word in ['liste', 'list', 'auflisten', 'verzeichnis', 'directory', 'ordner']):
        path_match = re.search(r'(?:verzeichnis|directory|ordner|in)\s+([^\s]+)', prompt, re.IGNORECASE)
        path = path_match.group(1) if path_match else "."
        
        result = list_files(path)
        results.append(f"📂 Verzeichnis auflisten: {result}")
    
    # Shell-Kommando
    cmd_patterns = [
        r'(?:führe|execute|run)\s+["\']([^"\']+)["\']',
        r'kommando[\s:]*["\']([^"\']+)["\']', 
        r'`([^`]+)`'
    ]
    
    for pattern in cmd_patterns:
        cmd_match = re.search(pattern, prompt, re.IGNORECASE)
        if cmd_match:
            cmd = cmd_match.group(1)
            result = run_shell(cmd)
            results.append(f"💻 Shell-Kommando: {result}")
            break
    
    # Web-Request
    url_patterns = [
        r'(https?://[^\s]+)',
        r'(www\.[^\s]+)',
        r'([a-zA-Z0-9.-]+\.(?:com|org|net|de|edu|gov))'
    ]
    
    for pattern in url_patterns:
        url_match = re.search(pattern, prompt, re.IGNORECASE)
        if url_match:
            url = url_match.group(1)
            result = fetch(url)
            results.append(f"🌐 Web-Request: {result}")
            break
    
    if not results:
        return "🤔 Keine spezifischen Tools erkannt. Verwende natürliche Sprache:\n" \
               "• 'Lies Datei xyz.txt'\n" \
               "• 'Erstelle Datei test.py mit \"print('Hello')\"'\n" \
               "• 'Liste Verzeichnis workspace auf'\n" \
               "• 'Führe Kommando \"ls -la\" aus'\n" \
               "• 'Lade Webseite wikipedia.org'"
    
    return "\n\n".join(results)

# =================
# API ENDPOINTS
# =================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model": LLM_MODEL,
        "sandbox": SANDBOX,
        "sandbox_path": SANDBOX_PATH,
        "allowed_domains": ALLOWED_DOMAINS,
        "open_webui_port": OPEN_WEBUI_PORT
    })

@app.route("/v1/models", methods=["GET"])  
def list_models():
    return jsonify({
        "object": "list",
        "data": [
            {"id": "localagent-pro", "object": "model"},
            {"id": LLM_MODEL, "object": "model"}
        ]
    })

@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    """OpenAI-kompatible Chat-API"""
    data = request.get_json(force=True)
    messages = data.get("messages", [])
    
    # Letzter User-Prompt extrahieren
    user_prompt = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_prompt = msg.get("content", "")
            break
    
    if not user_prompt:
        response_text = "Hallo! Ich bin LocalAgent-Pro. Wie kann ich dir helfen?"
    else:
        # Tool-Analyse und Ausführung
        tool_results = analyze_and_execute(user_prompt)
        
        # Direkte Antwort mit Tool-Ergebnissen
        response_text = f"🤖 LocalAgent-Pro:\n\n{tool_results}"
    
    return jsonify({
        "id": "localagent-pro",
        "object": "chat.completion",
        "choices": [{
            "index": 0,
            "finish_reason": "stop", 
            "message": {
                "role": "assistant",
                "content": response_text
            }
        }]
    })

@app.route("/test", methods=["POST"])
def test_tool():
    """Test-Endpoint für direkte Tool-Aufrufe"""
    data = request.get_json(force=True)
    prompt = data.get("prompt", "")
    
    if not prompt:
        return jsonify({"error": "Kein Prompt angegeben"})
    
    result = analyze_and_execute(prompt)
    return jsonify({"result": result})

# =================
# SERVER START
# =================

if __name__ == "__main__":
    print("🚀 LocalAgent-Pro Server startet...")
    print(f"🧠 Modell: {LLM_MODEL}")
    print(f"🔒 Sandbox: {'✅ Aktiv' if SANDBOX else '❌ Deaktiviert'}")
    print(f"📁 Sandbox-Pfad: {SANDBOX_PATH}")
    print(f"🌐 Erlaubte Domains: {len(ALLOWED_DOMAINS)}")
    print(f"📡 Server: http://localhost:8001")
    print(f"🎯 OpenWebUI URL: http://127.0.0.1:8001/v1")
    print("\n✅ Bereit für OpenWebUI!")
    
    app.run(host="0.0.0.0", port=8001, debug=False)