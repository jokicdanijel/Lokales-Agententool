#!/usr/bin/env python3
"""
Safepoints erweitert – latest() Funktion
"""

def latest(archive_path: str, n: int = 5) -> list:
    """
    Gibt die n neusten Safepoints aus archivp zurück
    (ohne Filter, nur chronologisch sortiert)
    """
    import json
    from pathlib import Path
    from datetime import datetime
    
    archive = Path(archive_path)
    if not archive.exists():
        return []
    
    # Finde alle JSON-Dateien
    json_files = list(archive.rglob("*.json"))
    
    # Sortiere nach Änderungszeit (neueste zuerst)
    json_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    
    result = []
    for f in json_files[:n]:
        try:
            content = json.loads(f.read_text())
            result.append({
                "path": str(f.relative_to(archive)),
                "ts": content.get("ts"),
                "content": content
            })
        except Exception as e:
            print(f"Fehler beim Lesen {f}: {e}")
    
    return result


if __name__ == "__main__":
    # Test
    items = latest("archivp", 5)
    for item in items:
        print(item)
