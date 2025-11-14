import subprocess
import os
import yaml

# Config laden
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

SANDBOX = config.get("sandbox", True)

def run_shell(cmd: str) -> str:
    """Führt Shell-Kommando aus (nur im Live-Modus)"""
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
        
        # Kommando ausführen
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.expanduser("~")
        )
        
        output: list[str] = []
        if result.stdout:
            output.append(f"📤 STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"⚠️ STDERR:\n{result.stderr}")
        
        status = "✅ Erfolgreich" if result.returncode == 0 else f"❌ Exit Code: {result.returncode}"
        output.insert(0, f"💻 Shell-Kommando: {cmd}\n{status}")
        
        return "\n\n".join(output) if output else "✅ Kommando ausgeführt (keine Ausgabe)"
        
    except subprocess.TimeoutExpired:
        return f"⏰ Timeout nach 30s: {cmd}"
    except Exception as e:
        return f"❌ Shell-Fehler: {str(e)}"