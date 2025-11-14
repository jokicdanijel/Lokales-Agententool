import os
import yaml

# Config laden
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

SANDBOX = config.get("sandbox", True)
SANDBOX_PATH = config.get("sandbox_path", os.path.expanduser("~/localagent_sandbox"))

def _resolve_path(path: str) -> str:
    """Wandelt Pfad in Sandbox-Pfad um, falls Sandbox aktiv"""
    if SANDBOX:
        # Entferne führende Slashes und füge zum Sandbox-Pfad hinzu
        clean_path = path.lstrip("/").lstrip("\\")
        resolved = os.path.join(SANDBOX_PATH, clean_path)
        # Stelle sicher, dass Verzeichnis existiert
        os.makedirs(os.path.dirname(resolved) if os.path.dirname(resolved) else SANDBOX_PATH, exist_ok=True)
        return resolved
    return os.path.abspath(path)

def read_file(path: str) -> str:
    """Liest den Inhalt einer Datei"""
    try:
        rpath = _resolve_path(path)
        if not os.path.exists(rpath):
            return f"❌ Datei nicht gefunden: {rpath}"
        
        with open(rpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        sandbox_info = f" (Sandbox: {rpath})" if SANDBOX else f" (Live: {rpath})"
        return f"📄 Datei gelesen{sandbox_info}:\n\n{content}"
        
    except Exception as e:
        return f"❌ Fehler beim Lesen: {str(e)}"

def write_file(path: str, content: str) -> str:
    """Schreibt Inhalt in eine Datei"""
    try:
        rpath = _resolve_path(path)
        
        with open(rpath, "w", encoding="utf-8") as f:
            f.write(content)
        
        sandbox_info = f" (Sandbox: {rpath})" if SANDBOX else f" (Live: {rpath})"
        return f"✅ Datei erstellt{sandbox_info}\n📝 {len(content)} Zeichen geschrieben"
        
    except Exception as e:
        return f"❌ Fehler beim Schreiben: {str(e)}"

def list_files(path: str = ".") -> str:
    """Listet Dateien und Verzeichnisse auf"""
    try:
        rpath = _resolve_path(path)
        
        if not os.path.exists(rpath):
            return f"❌ Verzeichnis nicht gefunden: {rpath}"
        
        if not os.path.isdir(rpath):
            return f"❌ Kein Verzeichnis: {rpath}"
        
        entries: list[str] = []
        for item in sorted(os.listdir(rpath)):
            item_path = os.path.join(rpath, item)
            if os.path.isdir(item_path):
                entries.append(f"📁 {item}/")
            else:
                size = os.path.getsize(item_path)
                entries.append(f"📄 {item} ({size} bytes)")
        
        if not entries:
            sandbox_info = f" (Sandbox: {rpath})" if SANDBOX else f" (Live: {rpath})"
            return f"📂 Verzeichnis leer{sandbox_info}"
        
        sandbox_info = f" (Sandbox: {rpath})" if SANDBOX else f" (Live: {rpath})"
        return f"📂 Verzeichnisinhalt{sandbox_info}:\n" + "\n".join(entries)
        
    except Exception as e:
        return f"❌ Fehler beim Auflisten: {str(e)}"