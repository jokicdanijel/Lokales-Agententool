#!/usr/bin/env python3
"""
Vollständiger Ollama-Integration Test für LocalAgent-Pro
"""

import sys
sys.path.insert(0, 'src')

from ollama_integration import create_ollama_client

print("=" * 80)
print("🧪 OLLAMA-INTEGRATION TEST")
print("=" * 80)
print()

# Client erstellen
client = create_ollama_client(
    base_url="http://127.0.0.1:11434",
    default_model="llama2"
)

print("\n📋 Test 1: Modelle auflisten")
print("-" * 80)
models = client.list_models()
if models:
    print(f"✅ {len(models)} Modelle gefunden:")
    for model in models:
        name = model.get("name", "unknown")
        size = model.get("size", 0)
        print(f"  • {name} ({size / 1024 / 1024 / 1024:.2f} GB)")
else:
    print("❌ Keine Modelle gefunden")

print("\n🧠 Test 2: Text-Generierung (Generate)")
print("-" * 80)
response = client.generate(
    prompt="Was ist Docker? Antworte in maximal 2 Sätzen auf Deutsch.",
    temperature=0.7
)

if response:
    print(f"✅ Antwort erhalten:")
    print(f"  {response}")
else:
    print("❌ Keine Antwort erhalten")

print("\n💬 Test 3: Chat")
print("-" * 80)
chat_response = client.chat(
    messages=[
        {"role": "system", "content": "Du bist ein hilfreicher deutscher Assistent. Antworte kurz und präzise."},
        {"role": "user", "content": "Erkläre Python in einem Satz."}
    ],
    temperature=0.7
)

if chat_response:
    print(f"✅ Chat-Antwort erhalten:")
    print(f"  {chat_response}")
else:
    print("❌ Keine Chat-Antwort erhalten")

print("\n" + "=" * 80)
print("✅ OLLAMA-INTEGRATION TEST ABGESCHLOSSEN")
print("=" * 80)
print("\n📊 Log-Dateien prüfen:")
print("  tail -50 logs/ollama_integration.log")
print("  ./analyze_logs.sh")
