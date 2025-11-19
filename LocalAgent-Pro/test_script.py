#!/usr/bin/env python3
"""Test-Skript für LocalAgent-Pro File Operations"""

import sys
from datetime import datetime

def main():
    print("=" * 60)
    print("🚀 LocalAgent-Pro File Operations Test")
    print("=" * 60)
    print(f"📅 Zeitstempel: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python Version: {sys.version}")
    print("=" * 60)
    
    # Test 1: Datei erstellen
    test_file = "demo_output.txt"
    print(f"\n✏️  Test 1: Datei '{test_file}' erstellen...")
    try:
        with open(test_file, 'w') as f:
            f.write("Hello from LocalAgent-Pro!\n")
            f.write(f"Created at: {datetime.now()}\n")
        print(f"✅ Datei erstellt: {test_file}")
    except Exception as e:
        print(f"❌ Fehler beim Erstellen: {e}")
        return 1
    
    # Test 2: Datei lesen
    print(f"\n📖 Test 2: Datei '{test_file}' lesen...")
    try:
        with open(test_file, 'r') as f:
            content = f.read()
        print(f"✅ Inhalt gelesen ({len(content)} Zeichen):")
        print("-" * 40)
        print(content)
        print("-" * 40)
    except Exception as e:
        print(f"❌ Fehler beim Lesen: {e}")
        return 1
    
    # Test 3: Python Code ausführen
    print("\n🔧 Test 3: Python Code dynamisch ausführen...")
    try:
        test_code = """
result = sum([i**2 for i in range(1, 6)])
print(f"Summe der Quadrate 1-5: {result}")
"""
        exec(test_code)
        print("✅ Code erfolgreich ausgeführt")
    except Exception as e:
        print(f"❌ Fehler bei Code-Ausführung: {e}")
        return 1
    
    print("\n" + "=" * 60)
    print("✅ Alle Tests erfolgreich abgeschlossen!")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
