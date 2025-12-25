"""
localagent_pro_server.py

Ein vollwertiger LocalAgent‑Pro‑Server mit automatischer Tool‑Erkennung. Dieses
Skript kombiniert die Funktionalität aus dem ursprünglichen Server mit der
intelligenten Tool‑Auswahl. Es liest die Konfiguration und den System‑Prompt
aus den Dateien im `config`‑Verzeichnis, definiert grundlegende Tools zum
Lesen/Schreiben von Dateien, Auflisten von Verzeichnissen, Ausführen von
Shell‑Kommandos und Abrufen von Webseiten sowie eine einfache Chat‑API.

Außerdem wird ein `/health`‑Endpunkt implementiert und die korrekte
OpenWebUI‑Adresse anhand des Konfigurationswerts `open_webui_port`
ausgegeben. Standardmäßig läuft Open WebUI UI auf Port 8080 (Docker-intern,
mappbar via `-p 8080:8080`). Passe `open_webui_port` in `config/config.yaml` an,
falls du eine andere Port‑Zuordnung verwendest. Backend-Services nutzen 12344-12399.

Starten des Servers:

    python3 localagent_pro_server.py

Du kannst anschließend die Chat‑API über `/v1/chat/completions` ansprechen
oder die Tools direkt via `/test` testen. Verwende in OpenWebUI den
Custom‑Endpoint `http://127.0.0.1:<port>/v1` als API‑URL (wobei `<port>` der
Port deines Agents ist, in diesem Skript standardmäßig 8001).
"""

import os
import re
import subprocess
from typing import Any
from urllib.parse import urlparse

import requests
import yaml
from flask import Flask, jsonify, request
from openai import OpenAI

# Basisverzeichnis und Konfigurationspfad bestimmen
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.yaml")
SYSTEM_PROMPT_PATH = os.path.join(BASE_DIR, "config", "system_prompt.txt")

# Konfiguration laden
try:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    print(f"❌ Config nicht gefunden: {CONFIG_PATH}")
    exit(1)

# System‑Prompt laden
try:
    with open(SYSTEM_PROMPT_PATH, encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    SYSTEM_PROMPT = "Du bist LocalAgent-Pro, ein lokaler KI-Agent."

# Konfigurationswerte extrahieren
SANDBOX: bool = config.get("sandbox", True)
SANDBOX_PATH: str = config.get("sandbox_path", os.path.expanduser("~/localagent_sandbox"))
ALLOWED_DOMAINS = config.get("allowed_domains", [])
OPEN_WEBUI_PORT: int = config.get("open_webui_port", 8080)  # UI-only (not backend)

llm_cfg = config.get("llm", {})
LLM_BASE_URL: str = llm_cfg.get("base_url", "http://localhost:11434/v1")
LLM_MODEL: str = llm_cfg.get("model", "llama2")

# Flask‑App initialisieren
app = Flask(__name__)


# Werkzeugfunktionen
def _resolve_path(path: str) -> str:
    """Wandelt einen Pfad in einen Sandbox‑Pfad um, falls die Sandbox aktiv ist."""
    if SANDBOX:
        clean = path.lstrip("/").lstrip("\\")
        resolved = os.path.join(SANDBOX_PATH, clean)
        os.makedirs(os.path.dirname(resolved) if os.path.dirname(resolved) else SANDBOX_PATH, exist_ok=True)
        return resolved
    return os.path.abspath(path)


def read_file(path: str) -> str:
    """Liest den Inhalt einer Datei und gibt ihn zusammen mit dem Speicherort zurück."""
    try:
        rpath = _resolve_path(path)
        if not os.path.exists(rpath):
            return f"❌ Datei nicht gefunden: {rpath}"
        with open(rpath, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        location = f" (Sandbox: {rpath})" if SANDBOX else f" (Live: {rpath})"
        return f"📄 Datei gelesen{location}:\n\n{content}"
    except Exception as e:
        return f"❌ Fehler beim Lesen: {e!s}"


def write_file(path: str, content: str) -> str:
    """Schreibt den gegebenen Inhalt in eine Datei."""
    try:
        rpath = _resolve_path(path)
        with open(rpath, "w", encoding="utf-8") as f:
            f.write(content)
        location = f" (Sandbox: {rpath})" if SANDBOX else f" (Live: {rpath})"
        return f"✅ Datei erstellt{location}\n📝 {len(content)} Zeichen geschrieben"
    except Exception as e:
        return f"❌ Fehler beim Schreiben: {e!s}"


def list_files(path: str = ".") -> str:
    """Listet die Inhalte eines Verzeichnisses auf."""
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
        return f"📂 Verzeichnisinhalt{location}:\n" + "\n".join(entries)
    except Exception as e:
        return f"❌ Fehler beim Auflisten: {e!s}"


def run_shell(cmd: str) -> str:
    """Führt ein Shell‑Kommando aus, sofern nicht im Sandbox‑Modus."""
    if SANDBOX:
        return "🚫 Shell-Kommandos sind im Sandbox-Modus deaktiviert.\n💡 Setze 'sandbox: false' in config/config.yaml und starte den Server neu."
    if not cmd.strip():
        return "❌ Leeres Kommando"
    try:
        # Gefährliche Kommandos blockieren
        dangerous = ["rm -rf", "sudo", "su -", "chmod +x", "mkfs", "dd if=", "format"]
        if any(danger in cmd.lower() for danger in dangerous):
            return f"🚫 Gefährliches Kommando blockiert: {cmd}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output_parts = [f"💻 Shell-Kommando: {cmd}"]
        output_parts.append(
            "✅ Erfolgreich ausgeführt" if result.returncode == 0 else f"❌ Exit Code: {result.returncode}"
        )
        if result.stdout:
            output_parts.append(f"📤 STDOUT:\n{result.stdout}")
        if result.stderr:
            output_parts.append(f"⚠️ STDERR:\n{result.stderr}")
        return "\n\n".join(output_parts)
    except subprocess.TimeoutExpired:
        return f"⏰ Timeout nach 30s: {cmd}"
    except Exception as e:
        return f"❌ Shell-Fehler: {e!s}"


def fetch(url: str) -> str:
    """Ruft den Inhalt einer Webseite ab, sofern die Domain erlaubt ist."""
    if not url.strip():
        return "❌ Leere URL"
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        domain = urlparse(url).netloc.lower()
        allowed = any(domain == d.lower() or domain.endswith("." + d.lower()) for d in ALLOWED_DOMAINS)
        if not allowed:
            return f"🚫 Domain blockiert: {domain}\n💡 Erlaubte Domains: {', '.join(ALLOWED_DOMAINS)}"
        headers = {"User-Agent": "LocalAgent-Pro/1.0"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        content = response.text[:10000]
        if len(response.text) > 10000:
            content += f"\n\n... (auf 10KB begrenzt, Original: {len(response.text)} Zeichen)"
        return f"🌐 Webseite geladen: {url}\n📊 Status: {response.status_code}\n\n{content}"
    except Exception as e:
        return f"❌ Web-Fehler: {e!s}"


# Intelligente Tool‑Auswahl
def analyze_and_execute(prompt: str) -> str:
    """Analysiert einen Eingabe‑Prompt und ruft passende Werkzeuge auf."""
    prompt_lower = prompt.lower()
    results = []
    # Datei lesen
    if any(word in prompt_lower for word in ["lesen", "read", "zeigen", "show", "inhalt"]):
        match = re.search(r"(?:datei|file)\s+([^\s]+)", prompt, re.IGNORECASE)
        if not match:
            match = re.search(r"([^\s]+\.(?:txt|py|md|json|yaml|yml|log))", prompt, re.IGNORECASE)
        if match:
            filename = match.group(1)
            results.append(f"🔍 Datei lesen: {read_file(filename)}")
    # Datei schreiben
    if any(word in prompt_lower for word in ["schreiben", "write", "erstellen", "create", "speichern"]):
        match = re.search(r"(?:datei|file)\s+([^\s]+)", prompt, re.IGNORECASE)
        if not match:
            match = re.search(r"([^\s]+\.(?:txt|py|md|json))", prompt, re.IGNORECASE)
        content_match = None
        patterns = [
            r'(?:inhalt|content|text)[\s:]*["\']([^"\']+)["\']',
            r'mit\s+["\']([^"\']+)["\']',
            r'["\']([^"\']{10,})["\']',
        ]
        for pattern in patterns:
            content_match = re.search(pattern, prompt, re.IGNORECASE)
            if content_match:
                break
        if match and content_match:
            filename = match.group(1)
            content = content_match.group(1)
            results.append(f"✏️ Datei schreiben: {write_file(filename, content)}")
    # Verzeichnis auflisten
    if any(word in prompt_lower for word in ["liste", "list", "auflisten", "verzeichnis", "directory", "ordner"]):
        path_match = re.search(r"(?:verzeichnis|directory|ordner|in)\s+([^\s]+)", prompt, re.IGNORECASE)
        path = path_match.group(1) if path_match else "."
        results.append(f"📂 Verzeichnis auflisten: {list_files(path)}")
    # Shell
    shell_patterns = [
        r'(?:führe|execute|run)\s+["\']([^"\']+)["\']',
        r'kommando[\s:]*["\']([^"\']+)["\']',
        r"`([^`]+)`",
    ]
    for pattern in shell_patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            results.append(f"💻 Shell-Kommando: {run_shell(match.group(1))}")
            break
    # Web request
    url_patterns = [r"(https?://[^\s]+)", r"(www\.[^\s]+)", r"([a-zA-Z0-9.-]+\.(?:com|org|net|de|edu|gov))"]
    for pattern in url_patterns:
        url_match = re.search(pattern, prompt, re.IGNORECASE)
        if url_match:
            url = url_match.group(1)
            results.append(f"🌐 Web-Request: {fetch(url)}")
            break
    if not results:
        return (
            "🤔 Keine spezifischen Tools erkannt. Verwende zum Beispiel:\n"
            "• 'Lies Datei xyz.txt'\n"
            "• 'Erstelle Datei test.py mit \"print('Hallo')\"'\n"
            "• 'Liste Verzeichnis /home auf'\n"
            "• 'Führe Kommando \"ls -la\" aus'\n"
            "• 'Lade Webseite wikipedia.org'"
        )
    return "\n\n".join(results)


# LLM Client konfigurieren
client = OpenAI(base_url=LLM_BASE_URL, api_key="none")


# API Endpunkte
@app.route("/health", methods=["GET"])
def health() -> dict[str, Any]:
    return jsonify(
        {
            "status": "ok",
            "model": LLM_MODEL,
            "sandbox": SANDBOX,
            "sandbox_path": SANDBOX_PATH,
            "allowed_domains": ALLOWED_DOMAINS,
            "open_webui_port": OPEN_WEBUI_PORT,
        }
    )


@app.route("/v1/models", methods=["GET"])
def list_models() -> dict[str, Any]:
    return jsonify(
        {"object": "list", "data": [{"id": "localagent-pro", "object": "model"}, {"id": LLM_MODEL, "object": "model"}]}
    )


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions() -> dict[str, Any]:
    data = request.get_json(force=True)
    messages = data.get("messages", [])
    user_prompt = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_prompt = msg.get("content", "")
            break
    if not user_prompt:
        response_text = "Hallo! Ich bin LocalAgent-Pro. Wie kann ich dir helfen?"
    else:
        response_text = f"🤖 LocalAgent-Pro:\n\n{analyze_and_execute(user_prompt)}"
    return jsonify(
        {
            "id": "localagent-pro",
            "object": "chat.completion",
            "choices": [
                {"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": response_text}}
            ],
        }
    )


@app.route("/test", methods=["POST"])
def test_tool() -> dict[str, Any]:
    data = request.get_json(force=True)
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Kein Prompt angegeben"}), 400
    return jsonify({"result": analyze_and_execute(prompt)})


# Serverstart
if __name__ == "__main__":
    print("🚀 LocalAgent-Pro Server startet...")
    print(f"🧠 Modell: {LLM_MODEL}")
    print(f"🔒 Sandbox: {'✅ Aktiv' if SANDBOX else '❌ Deaktiviert'}")
    print(f"📁 Sandbox-Pfad: {SANDBOX_PATH}")
    print(f"🌐 Erlaubte Domains: {len(ALLOWED_DOMAINS)}")
    print("📡 Server: http://localhost:8001")
    print(f"🎯 OpenWebUI URL: http://127.0.0.1:{OPEN_WEBUI_PORT}")
    print("\n✅ Bereit für OpenWebUI!")
    app.run(host="0.0.0.0", port=8001, debug=False)
