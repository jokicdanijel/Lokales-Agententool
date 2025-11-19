#!/usr/bin/env python3
"""
Ollama-Integration Test für LocalAgent-Pro
Testet die Verbindung und Funktionen mit dem verfügbaren Modell
"""

import sys
import os

# Pfad zum src-Verzeichnis hinzufügen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ollama_integration import OllamaClient
from logging_config import get_logging_manager

# Logger erstellen
logging_manager = get_logging_manager()
logger = logging_manager.get_logger("OllamaTest")

def main():
    logger.info("=" * 80)
    logger.info("🧪 Ollama-Integration Vollständiger Test")
    logger.info("=" * 80)
    
    # 1. Client erstellen
    logger.info("\n📋 Schritt 1: Ollama-Client erstellen...")
    client = OllamaClient(
        base_url="http://127.0.0.1:11434",
        timeout=60,
        default_model="llama2:latest"  # Verfügbares Modell
    )
    
    # 2. Modelle auflisten
    logger.info("\n📋 Schritt 2: Verfügbare Modelle auflisten...")
    models = client.list_models()
    
    if models:
        print(f"\n✅ {len(models)} Modelle gefunden:")
        for model in models:
            name = model.get("name", "unknown")
            size = model.get("size", 0) / (1024**3)  # GB
            modified = model.get("modified_at", "unknown")
            print(f"  📦 {name} ({size:.2f} GB) - Modified: {modified}")
    else:
        print("\n❌ Keine Modelle gefunden!")
        return
    
    # 3. Einfache Generate-API testen
    logger.info("\n📋 Schritt 3: Generate-API testen...")
    
    # Teste mit direktem API-Call
    import requests
    
    generate_url = "http://127.0.0.1:11434/api/generate"
    generate_payload = {
        "model": "llama2:latest",
        "prompt": "Was ist Python? Antworte in einem Satz.",
        "stream": False
    }
    
    logger.info(f"🔍 Teste: POST {generate_url}")
    logger.debug(f"📦 Payload: {generate_payload}")
    
    try:
        response = requests.post(generate_url, json=generate_payload, timeout=30)
        logger.info(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get("response", "")
            print(f"\n✅ Generate-API erfolgreich!")
            print(f"💬 Antwort: {generated_text}")
            
            # Statistiken
            eval_count = result.get("eval_count", 0)
            eval_duration = result.get("eval_duration", 0) / 1e9  # ns zu s
            tokens_per_sec = eval_count / eval_duration if eval_duration > 0 else 0
            
            print(f"📊 Tokens: {eval_count}")
            print(f"⏱️  Dauer: {eval_duration:.2f}s")
            print(f"🚀 Speed: {tokens_per_sec:.1f} tokens/s")
        else:
            print(f"\n❌ Generate-API Fehler: {response.status_code}")
            print(f"📄 Response: {response.text}")
    except Exception as e:
        logger.error(f"❌ Generate-API Exception: {e}", exc_info=True)
        print(f"\n❌ Fehler: {e}")
    
    # 4. Chat-API testen
    logger.info("\n📋 Schritt 4: Chat-API testen...")
    
    chat_url = "http://127.0.0.1:11434/api/chat"
    chat_payload = {
        "model": "llama2:latest",
        "messages": [
            {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
            {"role": "user", "content": "Erkläre Docker in einem Satz."}
        ],
        "stream": False
    }
    
    logger.info(f"🔍 Teste: POST {chat_url}")
    logger.debug(f"📦 Payload: {chat_payload}")
    
    try:
        response = requests.post(chat_url, json=generate_payload, timeout=30)
        logger.info(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            message = result.get("message", {})
            chat_text = message.get("content", "")
            print(f"\n✅ Chat-API erfolgreich!")
            print(f"💬 Antwort: {chat_text}")
        else:
            print(f"\n❌ Chat-API Fehler: {response.status_code}")
            print(f"📄 Response: {response.text}")
    except Exception as e:
        logger.error(f"❌ Chat-API Exception: {e}", exc_info=True)
        print(f"\n❌ Fehler: {e}")
    
    # 5. Model-Info testen
    logger.info("\n📋 Schritt 5: Model-Info abrufen...")
    
    model_info = client.get_model_info("llama2:latest")
    if model_info:
        print(f"\n✅ Model-Info abgerufen:")
        print(f"📊 Template: {model_info.get('template', 'N/A')[:100]}...")
        print(f"📊 Parameters: {model_info.get('parameters', 'N/A')[:100]}...")
    else:
        print(f"\n⚠️  Model-Info konnte nicht abgerufen werden")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ Ollama-Integration Test abgeschlossen!")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()
