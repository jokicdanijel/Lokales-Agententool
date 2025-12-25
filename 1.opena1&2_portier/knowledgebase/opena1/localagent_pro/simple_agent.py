"""
simple_agent.py

Ein vereinfachter Flask‑Server für deinen LocalAgent‑Pro. Dieses Skript liest
die Konfiguration aus `config/config.yaml`, startet ein LLM‑Endpunkt unter
`/agent` und implementiert Hilfsendpunkte wie `/tool`, `/v1/models` und `/health`.

Es gibt außerdem die korrekte URL für deine Open WebUI aus, basierend auf dem
Konfigurationswert `open_webui_port`. Standardmäßig verwendet Open WebUI den
Port 3000, wenn du den Docker‑Container mit `-p 3000:8080` gestartet hast.
Falls du Open WebUI im Host‑Netzwerkmodus ausführst, setze `open_webui_port`
entsprechend (z.B. 8080).

Verwendung:

    python3 simple_agent.py

Das Skript erwartet, dass eine LLM‑kompatible API unter `llm.base_url` in
`config/config.yaml` erreichbar ist. Für die Tests kannst du Ollama verwenden.
"""

import os
from typing import Any

import yaml
from flask import Flask, jsonify, request
from openai import OpenAI

# Konfiguration laden
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

# LLM Einstellungen
LLM_BASE_URL: str = config["llm"].get("base_url")
LLM_MODEL: str = config["llm"].get("model")

# Sandbox Einstellungen
SANDBOX_ENABLED: bool = config.get("sandbox", True)
SANDBOX_PATH: str = config.get("sandbox_path", os.path.join(os.path.expanduser("~"), "localagent_sandbox"))

# OpenWebUI Port
OPENWEBUI_PORT: int = config.get("open_webui_port", 8080)  # UI-only


# Tools definieren
def read_file(path: str) -> str:
    rpath = path
    if SANDBOX_ENABLED:
        rpath = os.path.join(SANDBOX_PATH, path.lstrip("/"))
    if not os.path.exists(rpath):
        return f"File not found: {rpath}"
    with open(rpath) as f:
        return f.read()


def write_file(path: str, content: str) -> str:
    wpath = path
    if SANDBOX_ENABLED:
        wpath = os.path.join(SANDBOX_PATH, path.lstrip("/"))
    os.makedirs(os.path.dirname(wpath), exist_ok=True)
    with open(wpath, "w") as f:
        f.write(content)
    return f"File written to {wpath}"


def list_files(path: str) -> str:
    lpath = path
    if SANDBOX_ENABLED:
        lpath = os.path.join(SANDBOX_PATH, path.lstrip("/"))
    if not os.path.exists(lpath):
        return "Directory does not exist."
    return "\n".join(os.listdir(lpath))


def run_shell(cmd: str) -> str:
    if SANDBOX_ENABLED:
        return "Shell disabled in SANDBOX mode."
    import subprocess

    return subprocess.getoutput(cmd)


def safe_fetch(url: str) -> str:
    from urllib.parse import urlparse

    import requests

    domain = urlparse(url).netloc
    allowed = set(config.get("allowed_domains", []))
    if domain not in allowed:
        return f"Access denied: {domain} is not in whitelist."
    try:
        response = requests.get(url, timeout=10)
        return response.text
    except Exception as e:
        return f"Request failed: {e!s}"


TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "run_shell": run_shell,
    "fetch": safe_fetch,
}

app = Flask(__name__)

client = OpenAI(base_url=LLM_BASE_URL, api_key="none")


@app.route("/agent", methods=["POST"])
def agent_route() -> dict[str, Any]:
    data = request.get_json(force=True)
    prompt = data.get("prompt", "")
    try:
        response = client.chat.completions.create(model=LLM_MODEL, messages=[{"role": "user", "content": prompt}])
        return jsonify({"response": response.choices[0].message["content"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/tool", methods=["POST"])
def manual_tool() -> dict[str, Any]:
    data = request.get_json(force=True)
    name = data.get("name")
    args = data.get("args", {})
    if name not in TOOLS:
        return jsonify({"error": f"Unknown tool: {name}"}), 400
    try:
        result = TOOLS[name](**args)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/v1/models", methods=["GET"])
def list_models() -> dict[str, Any]:
    return jsonify(
        {
            "object": "list",
            "data": [
                {"id": LLM_MODEL, "object": "model"},
                {"id": "localagent-pro", "object": "model"},
            ],
        }
    )


@app.route("/health", methods=["GET"])
def health() -> dict[str, Any]:
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("🚀 LocalAgent‑Pro Server startet...")
    print(f"🧠 Modell: {LLM_MODEL}")
    print(f"🔒 Sandbox: {'✅ Aktiv' if SANDBOX_ENABLED else '❌ Deaktiviert'}")
    print(f"📁 Sandbox-Pfad: {SANDBOX_PATH}")
    print(f"🌐 Erlaubte Domains: {len(config.get('allowed_domains', []))}")
    print("📡 Server: http://localhost:8001")
    print(f"🎯 OpenWebUI URL: http://127.0.0.1:{OPENWEBUI_PORT}")
    print("✅ Bereit für OpenWebUI!")
    app.run(host="0.0.0.0", port=8001, debug=False)
