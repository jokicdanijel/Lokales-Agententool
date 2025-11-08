#!/usr/bin/env python3
"""Migration-Script: Migriert Safepoints in neues Format"""

import json
from pathlib import Path
from datetime import datetime

def migrate_data(archive_path: str = "archiv"):
    """
    Migriert bestehende Safepoints:
    - Fügt 'migrated': true hinzu
    - Speichert mit neuem Namen (*_migrated.json)
    """
    archive = Path(archive_path)
    
    if not archive.exists():
        print(f"Archiv nicht gefunden: {archive_path}")
        return
    
    migrated_count = 0
    
    for json_file in archive.rglob("*.json"):
        if "_migrated" in json_file.name:
            continue  # Bereits migriert
        
        try:
            content = json.loads(json_file.read_text())
            
            # Füge migrated-Flag hinzu
            content["migrated"] = True
            content["migrated_at"] = datetime.utcnow().isoformat()
            
            # Neuer Dateiname
            new_name = json_file.stem + "_migrated.json"
            new_path = json_file.parent / new_name
            
            # Schreibe neue Datei
            new_path.write_text(json.dumps(content, indent=2))
            print(f"✓ Migriert: {json_file.name} → {new_name}")
            migrated_count += 1
            
        except Exception as e:
            print(f"✗ Fehler bei {json_file.name}: {e}")
    
    print(f"\n✅ Insgesamt {migrated_count} Dateien migriert")


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "archiv"
    migrate_data(path)
