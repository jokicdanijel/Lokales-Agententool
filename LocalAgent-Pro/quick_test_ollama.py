#!/usr/bin/env python3
"""
Schnelltest der Ollama-Integration
"""

import sys
import os

# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ollama_integration import create_ollama_client

def main():
    print("\n" + "="*70)
    print("  OLLAMA-INTEGRATION SCHNELLTEST")
    print("="*70 + "\n")
    
    # Client initialisieren
    print("1️⃣  Initialisiere Ollama-Client...")
    client = create_ollama_client()
    
    # Verbindung testen
    print("2️⃣  Teste Verbindung...")
    if not client._test_connection(): # type: ignore
        print("❌ Verbindung fehlgeschlagen!")
        return 1
    print("✅ Verbindung erfolgreich!\n")
    
    # Modelle auflisten
    print("3️⃣  Liste verfügbare Modelle...")
    models = client.list_models()
    if models:
        print(f"✅ {len(models)} Modell(e) gefunden:")
        for model in models:
            size_mb = model.get('size', 0) / (1024**3)  # Bytes zu GB
            print(f"   📦 {model['name']} ({size_mb:.2f} GB)")
    else:
        print("❌ Keine Modelle gefunden!")
        return 1
    print()
    
    # Kurze Text-Generierung testen (mit Timeout-Schutz)
    print("4️⃣  Teste Text-Generierung (kurzer Prompt)...")
    print("   ⏳ Bitte warten (kann 10-30 Sekunden dauern)...\n")
    
    try:
        response = client.generate(
            prompt="Zähle von 1 bis 3.",
            model="llama2",
            temperature=0.5,
            max_tokens=50  # Begrenzt die Response
        )
        
        if response:
            print(f"✅ Response erhalten:")
            print(f"   💬 {response[:200]}")
            if len(response) > 200:
                print(f"   ... ({len(response)} Zeichen total)")
        else:
            print("⚠️  Keine Response erhalten (Timeout oder Fehler)")
            print("   💡 Tipp: CPU-Inferenz ist sehr langsam!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Test abgebrochen (Ctrl+C)")
        print("   💡 Tipp: Generate-Requests dauern 20-60s im CPU-Modus!")
        return 1
    
    print("\n" + "="*70)
    print("  ✅ ALLE TESTS ERFOLGREICH!")
    print("="*70 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
