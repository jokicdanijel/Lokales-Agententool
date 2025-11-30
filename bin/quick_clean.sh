#!/bin/bash
#
# 🧹 Quick Clean & Inspect
# =======================
# 
# Schnelle Ausführung des Cleaner & Inspector Systems
#

set -e

PROJECT_ROOT="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"
PYTHON_CMD="python3"

echo "🧹 PORTIER 3.0 Quick Clean & Inspect"
echo "===================================="
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 nicht gefunden"
    exit 1
fi

echo "📋 Starte Safepoint-Client Inspektion..."

# Direkte Python-Ausführung des Cleaner-Skripts
$PYTHON_CMD - << 'EOF'
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

def check_safepoint_clients():
    """Einfacher Safepoint-Client Check."""
    project_root = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt")
    
    print("🔍 Suche Safepoint-Clients...")
    
    clients_found = []
    clients_broken = []
    
    # Alle Agent-Verzeichnisse finden
    for agent_dir in project_root.glob("[0-9]*.*"):
        if not agent_dir.is_dir():
            continue
            
        safepoint_file = agent_dir / "safepoint_client.py"
        
        if safepoint_file.exists():
            # Syntax-Check
            try:
                with open(safepoint_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, str(safepoint_file), 'exec')
                clients_found.append(agent_dir.name)
            except Exception as e:
                clients_broken.append(f"{agent_dir.name}: {str(e)}")
    
    # Ergebnisse
    print(f"\n✅ {len(clients_found)} Safepoint-Clients gefunden und OK:")
    for client in sorted(clients_found):
        print(f"   • {client}")
    
    if clients_broken:
        print(f"\n❌ {len(clients_broken)} Safepoint-Clients mit Problemen:")
        for client in clients_broken:
            print(f"   • {client}")
    
    return len(clients_found), len(clients_broken)

def cleanup_cache():
    """Einfache Cache-Bereinigung."""
    import shutil
    project_root = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt")
    
    print("\n🧽 Bereinige Python-Cache...")
    
    removed_count = 0
    
    # __pycache__ Ordner
    for pycache_dir in project_root.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache_dir)
            removed_count += 1
            print(f"   ✅ Entfernt: {pycache_dir}")
        except Exception:
            pass
    
    # .pyc Dateien
    for pyc_file in project_root.rglob("*.pyc"):
        try:
            pyc_file.unlink()
            removed_count += 1
        except Exception:
            pass
    
    print(f"🗑️  {removed_count} Cache-Elemente entfernt")
    return removed_count

# Hauptprogramm
if __name__ == "__main__":
    try:
        print("Timestamp:", datetime.now(timezone.utc).isoformat())
        print()
        
        # Safepoint-Client Check
        ok_count, broken_count = check_safepoint_clients()
        
        # Cache-Cleanup
        cleaned_count = cleanup_cache()
        
        print("\n" + "="*50)
        print("📊 ZUSAMMENFASSUNG")
        print("="*50)
        print(f"✅ Safepoint-Clients OK:      {ok_count}")
        print(f"❌ Safepoint-Clients Fehler:  {broken_count}")
        print(f"🧽 Cache-Elemente bereinigt:   {cleaned_count}")
        
        if broken_count == 0:
            print("\n🎉 Alles OK! System ist bereit.")
            exit_code = 0
        else:
            print(f"\n⚠️  {broken_count} Probleme gefunden - bitte prüfen!")
            exit_code = 1
        
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"\n❌ Fehler: {str(e)}")
        sys.exit(1)
EOF

echo