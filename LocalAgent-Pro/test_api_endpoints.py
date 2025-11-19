#!/usr/bin/env python3
"""
API-Endpoint Test Suite für LocalAgent-Pro Backend
Testet: Health, Models, Chat/Completions
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8001"

def print_header(text: str):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_test(name: str):
    print(f"🧪 Test: {name}")

def print_success(msg: str):
    print(f"   ✅ {msg}")

def print_error(msg: str):
    print(f"   ❌ {msg}")

def print_info(msg: str):
    print(f"   ℹ️  {msg}")

def test_health() -> bool:
    """Test /health Endpoint"""
    print_test("Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_success(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Body: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_models() -> bool:
    """Test /v1/models Endpoint"""
    print_test("List Models")
    
    try:
        response = requests.get(f"{BASE_URL}/v1/models", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            
            if "data" in data:
                models = data["data"]
                print_success(f"Modelle gefunden: {len(models)}")
                
                for model in models[:3]:  # Erste 3 anzeigen
                    print_info(f"  • {model.get('id', 'unknown')}")
                
                if len(models) > 3:
                    print_info(f"  ... und {len(models) - 3} weitere")
                    
                return True
            else:
                print_error("Keine 'data' in Response")
                return False
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Body: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_chat_simple() -> bool:
    """Test /v1/chat/completions mit einfacher Message"""
    print_test("Chat Completions (Einfach)")
    
    payload = {
        "model": "tinyllama",
        "messages": [
            {"role": "user", "content": "Sag nur: Hallo!"}
        ],
        "temperature": 0.5,
        "max_tokens": 10
    }
    
    try:
        print_info(f"Request: {json.dumps(payload, indent=2)}")
        
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=30
        )
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_success(f"Duration: {duration:.2f}s")
            
            if "choices" in data and len(data["choices"]) > 0:
                message = data["choices"][0].get("message", {})
                content = message.get("content", "")
                
                print_success("Response erhalten:")
                print_info(f"  Content: {content[:100]}")
                
                if "usage" in data:
                    usage = data["usage"]
                    print_info(f"  Tokens: prompt={usage.get('prompt_tokens', 0)}, "
                             f"completion={usage.get('completion_tokens', 0)}, "
                             f"total={usage.get('total_tokens', 0)}")
                
                return True
            else:
                print_error("Keine 'choices' in Response")
                print_error(f"Body: {json.dumps(data, indent=2)}")
                return False
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Body: {response.text[:500]}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_chat_with_tools() -> bool:
    """Test /v1/chat/completions mit Tool-Call"""
    print_test("Chat Completions (Mit Tool-Call)")
    
    payload = {
        "model": "tinyllama",
        "messages": [
            {"role": "user", "content": "Erstelle eine Datei test.txt mit Inhalt 'Hallo GPU'"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        print_info(f"Request: User will Datei erstellen")
        
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=60
        )
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_success(f"Duration: {duration:.2f}s")
            
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                message = choice.get("message", {})
                
                # Prüfe auf Tool-Calls
                if "tool_calls" in message and message["tool_calls"]:
                    print_success(f"Tool-Calls gefunden: {len(message['tool_calls'])}")
                    
                    for tc in message["tool_calls"]:
                        func = tc.get("function", {})
                        print_info(f"  Tool: {func.get('name', 'unknown')}")
                        print_info(f"  Args: {func.get('arguments', {})}")
                else:
                    content = message.get("content", "")
                    print_info(f"Antwort ohne Tool-Call: {content[:150]}")
                
                return True
            else:
                print_error("Keine 'choices' in Response")
                return False
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Body: {response.text[:500]}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_streaming() -> bool:
    """Test Streaming Chat Completions"""
    print_test("Chat Completions (Streaming)")
    
    payload = {
        "model": "tinyllama",
        "messages": [
            {"role": "user", "content": "Zähle von 1 bis 3"}
        ],
        "stream": True,
        "max_tokens": 30
    }
    
    try:
        print_info("Starte Streaming-Request...")
        
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            stream=True,
            timeout=30
        )
        
        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            print_info("Stream-Chunks:")
            
            chunk_count = 0
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        chunk_count += 1
                        if chunk_count <= 3:  # Erste 3 Chunks anzeigen
                            print_info(f"  Chunk {chunk_count}: {decoded[:80]}...")
            
            print_success(f"Stream abgeschlossen: {chunk_count} Chunks empfangen")
            return chunk_count > 0
        else:
            print_error(f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def main():
    print_header("LOCALAGENT-PRO API ENDPOINT TESTS")
    
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"🕐 Start: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {}
    
    # Test 1: Health
    print_header("Test 1: Health Endpoint")
    results['health'] = test_health()
    
    # Test 2: Models
    print_header("Test 2: Models Endpoint")
    results['models'] = test_models()
    
    # Test 3: Simple Chat
    print_header("Test 3: Chat Completions (Simple)")
    results['chat_simple'] = test_chat_simple()
    
    # Test 4: Chat with Tools
    print_header("Test 4: Chat Completions (Tool Call)")
    results['chat_tools'] = test_chat_with_tools()
    
    # Test 5: Streaming
    print_header("Test 5: Streaming Chat Completions")
    results['streaming'] = test_streaming()
    
    # Zusammenfassung
    print_header("TESTERGEBNISSE")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name:20s} {status}")
    
    print(f"\n   Gesamt: {passed}/{total} Tests erfolgreich")
    
    if passed == total:
        print("\n   🎉 ALLE TESTS BESTANDEN!")
    else:
        print(f"\n   ⚠️  {total - passed} Test(s) fehlgeschlagen")
    
    print("\n" + "="*70 + "\n")
    
    return passed == total

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
