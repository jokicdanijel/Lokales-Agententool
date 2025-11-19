#!/usr/bin/env python3
"""
LocalAgent-Pro Knowledge DB Auto-Update Script

Aktualisiert config/localagent_knowledge_db.json automatisch mit dem aktuellen Runtime-Status.
Kann als VSCode Task oder Cronjob ausgeführt werden.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Pfade
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent
CONFIG_DIR = REPO_ROOT / "config"
KNOWLEDGE_DB_PATH = CONFIG_DIR / "localagent_knowledge_db.json"

# LocalAgent-Pro Endpoints
HEALTH_ENDPOINT = "http://127.0.0.1:8001/health"
METRICS_ENDPOINT = "http://127.0.0.1:8001/metrics"
PROMETHEUS_TARGETS_ENDPOINT = "http://localhost:9090/api/v1/targets"


def run_command(cmd: str, shell: bool = True) -> Optional[str]:
    """Führt Shell-Befehl aus und gibt Output zurück."""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"⚠️ Command failed: {cmd}", file=sys.stderr)
            print(f"   Error: {result.stderr}", file=sys.stderr)
            return None
    except subprocess.TimeoutExpired:
        print(f"⚠️ Command timeout: {cmd}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"⚠️ Command error: {cmd} - {e}", file=sys.stderr)
        return None


def fetch_health_data() -> Optional[Dict[str, Any]]:
    """Holt aktuellen Health-Status von LocalAgent-Pro."""
    output = run_command(f"curl -s {HEALTH_ENDPOINT}")
    if output:
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            print(f"⚠️ Invalid JSON from {HEALTH_ENDPOINT}", file=sys.stderr)
    return None


def fetch_metrics_count() -> Optional[int]:
    """Zählt verfügbare LocalAgent-Metriken."""
    output = run_command(f"curl -s {METRICS_ENDPOINT} | grep 'localagent_' | wc -l")
    if output:
        try:
            return int(output)
        except ValueError:
            print(f"⚠️ Invalid metrics count: {output}", file=sys.stderr)
    return None


def fetch_prometheus_target_status() -> Optional[str]:
    """Prüft Prometheus Target Health."""
    cmd = f'curl -s {PROMETHEUS_TARGETS_ENDPOINT} | jq -r \'.data.activeTargets[] | select(.labels.job=="localagent-pro") | .health\''
    output = run_command(cmd)
    return output if output else None


def fetch_process_info() -> Optional[str]:
    """Holt laufenden Prozess-Info."""
    output = run_command("ps aux | grep 'python.*openwebui_agent_server' | grep -v grep")
    return output if output else None


def load_knowledge_db() -> Dict[str, Any]:
    """Lädt aktuelle Knowledge DB."""
    if KNOWLEDGE_DB_PATH.exists():
        with open(KNOWLEDGE_DB_PATH, 'r') as f:
            return json.load(f)
    else:
        print(f"⚠️ Knowledge DB not found: {KNOWLEDGE_DB_PATH}", file=sys.stderr)
        return {"localagent_pro": {}}


def update_knowledge_db(data: Dict[str, Any]) -> None:
    """Speichert aktualisierte Knowledge DB."""
    with open(KNOWLEDGE_DB_PATH, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Knowledge DB updated: {KNOWLEDGE_DB_PATH}")


def main():
    """Hauptfunktion: Aktualisiert Knowledge DB mit aktuellem Runtime-Status."""
    print("🔄 LocalAgent-Pro Knowledge DB Auto-Update")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    print()

    # Lade bestehende Knowledge DB
    knowledge_db = load_knowledge_db()
    localagent = knowledge_db.get("localagent_pro", {})

    # Health-Daten abrufen
    print("📡 Fetching health data...")
    health_data = fetch_health_data()
    if health_data:
        print(f"   ✅ Status: {health_data.get('status', 'unknown')}")
        print(f"   ✅ Model: {health_data.get('model', 'unknown')}")
        print(f"   ✅ Sandbox: {health_data.get('sandbox', False)}")
        
        # Runtime-Sektion aktualisieren
        if "runtime" not in localagent:
            localagent["runtime"] = {}
        
        localagent["runtime"]["status"] = health_data.get("status", "unknown")
        localagent["runtime"]["model"] = health_data.get("model", "unknown")
        localagent["runtime"]["sandbox_enabled"] = health_data.get("sandbox", False)
        localagent["runtime"]["sandbox_path"] = health_data.get("sandbox_path", "")
        localagent["runtime"]["open_webui_port"] = health_data.get("open_webui_port", 3000)
        localagent["runtime"]["health_raw"] = {
            "allowed_domains": health_data.get("allowed_domains", []),
            "auto_whitelist_count": health_data.get("auto_whitelist_count", 0),
            "auto_whitelist_enabled": health_data.get("auto_whitelist_enabled", False),
            "server_time": health_data.get("server_time", 0)
        }
    else:
        print("   ⚠️ Health data unavailable (is LocalAgent-Pro running?)")

    # Metriken zählen
    print("📊 Counting metrics...")
    metrics_count = fetch_metrics_count()
    if metrics_count is not None:
        print(f"   ✅ Metrics: {metrics_count}")
        
        if "monitoring" not in localagent:
            localagent["monitoring"] = {}
        
        localagent["monitoring"]["metrics_count_observed"] = metrics_count
    else:
        print("   ⚠️ Metrics count unavailable")

    # Prometheus Target Status
    print("🎯 Checking Prometheus target...")
    target_status = fetch_prometheus_target_status()
    if target_status:
        print(f"   ✅ Target health: {target_status}")
        
        if "monitoring" not in localagent:
            localagent["monitoring"] = {}
        if "prometheus" not in localagent["monitoring"]:
            localagent["monitoring"]["prometheus"] = {}
        
        localagent["monitoring"]["prometheus"]["target_status"] = target_status
    else:
        print("   ⚠️ Prometheus target status unavailable")

    # Prozess-Info
    print("⚙️ Checking process info...")
    process_info = fetch_process_info()
    if process_info:
        print(f"   ✅ Process running")
        # Prozess-Info könnte hier weiter geparst werden
    else:
        print("   ⚠️ Process not found")

    # Meta-Informationen aktualisieren
    if "meta" not in localagent:
        localagent["meta"] = {}
    
    localagent["meta"]["last_updated"] = datetime.now().isoformat()
    localagent["meta"]["last_updated_by"] = "auto_update_script"

    # Knowledge DB speichern
    knowledge_db["localagent_pro"] = localagent
    update_knowledge_db(knowledge_db)

    print()
    print("✅ Knowledge DB update complete!")
    print(f"📄 File: {KNOWLEDGE_DB_PATH}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Update cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Update failed: {e}", file=sys.stderr)
        sys.exit(1)
