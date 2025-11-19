#!/usr/bin/env python3
"""
Ollama-Integration für LocalAgent-Pro
Umfassendes Logging für Ollama-API-Calls
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any

# Dynamischer Import je nach Kontext
try:
    from src.logging_config import get_logging_manager, truncate_long_content, mask_sensitive_data
except ImportError:
    from logging_config import get_logging_manager, truncate_long_content, mask_sensitive_data

# Logger erstellen
logging_manager = get_logging_manager()
ollama_logger = logging_manager.create_ollama_logger()


class OllamaClient:
    """Client für Ollama-API mit umfassendem Logging"""
    
    def __init__(
        self, 
        base_url: str = "http://127.0.0.1:11434",
        timeout: int = 60,
        default_model: str = "llama3.1:8b-instruct-q4_K_M"
    ):
        """
        Initialisiert Ollama-Client
        
        Args:
            base_url: Basis-URL der Ollama-API
            timeout: Request-Timeout in Sekunden
            default_model: Standard-Modell
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.default_model = default_model
        
        ollama_logger.info("=" * 80)
        ollama_logger.info("🤖 Ollama-Client initialisiert")
        ollama_logger.info(f"🔗 Base URL: {self.base_url}")
        ollama_logger.info(f"⏱️ Timeout: {self.timeout}s")
        ollama_logger.info(f"🧠 Default Model: {self.default_model}")
        ollama_logger.info("=" * 80)
        
        # Verbindungstest
        self._test_connection()
    
    def _test_connection(self) -> bool:
        """
        Testet Verbindung zur Ollama-API
        
        Returns:
            True wenn Verbindung erfolgreich
        """
        try:
            ollama_logger.debug("🔍 Teste Verbindung zu Ollama...")
            url = f"{self.base_url}/api/tags"
            
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            ollama_logger.info(f"✅ Ollama-Verbindung erfolgreich (Status: {response.status_code})")
            return True
            
        except requests.exceptions.ConnectionError:
            ollama_logger.error(
                f"❌ Keine Verbindung zu Ollama auf {self.base_url}. "
                "Stelle sicher, dass Ollama läuft (systemctl status ollama)"
            )
            return False
        except Exception as e:
            ollama_logger.error(f"❌ Verbindungstest fehlgeschlagen: {str(e)}", exc_info=True)
            return False
    
    def list_models(self) -> Optional[List[Dict[str, Any]]]:
        """
        Listet verfügbare Ollama-Modelle auf
        
        Returns:
            Liste von Modellen oder None bei Fehler
        """
        ollama_logger.info("📋 Liste Ollama-Modelle auf...")
        
        try:
            url = f"{self.base_url}/api/tags"
            ollama_logger.debug(f"📡 GET {url}")
            
            start_time = time.time()
            response = requests.get(url, timeout=self.timeout)
            duration = time.time() - start_time
            
            response.raise_for_status()
            
            data = response.json()
            models = data.get("models", [])
            
            ollama_logger.info(
                f"✅ Modelle abgerufen: {len(models)} Modelle in {duration:.2f}s"
            )
            
            for model in models:
                model_name = model.get("name", "unknown")
                model_size = model.get("size", 0)
                ollama_logger.debug(f"  📦 {model_name} ({model_size / 1024 / 1024:.1f} MB)")
            
            return models
            
        except requests.exceptions.Timeout:
            ollama_logger.error(f"⏰ Timeout beim Abrufen der Modelle (>{self.timeout}s)")
            return None
        except requests.exceptions.RequestException as e:
            ollama_logger.error(f"❌ Fehler beim Abrufen der Modelle: {str(e)}", exc_info=True)
            return None
        except Exception as e:
            ollama_logger.error(f"❌ Unerwarteter Fehler: {str(e)}", exc_info=True)
            return None
    
    def generate(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Optional[str]:
        """
        Generiert Text mit Ollama
        
        Args:
            prompt: User-Prompt
            model: Modell-Name (None = default_model)
            system: System-Prompt
            temperature: Temperatur (0.0 - 2.0)
            max_tokens: Max. Tokens (None = unbegrenzt)
        
        Returns:
            Generierter Text oder None bei Fehler
        """
        model = model or self.default_model
        request_id = str(time.time())[-8:]
        
        ollama_logger.info(f"🧠 Generate Request [{request_id}] gestartet")
        ollama_logger.info(f"📝 Model: {model}, Temperature: {temperature}")
        ollama_logger.debug(f"👤 Prompt [{request_id}]: {truncate_long_content(prompt, 300)}")
        
        if system:
            ollama_logger.debug(f"⚙️ System [{request_id}]: {truncate_long_content(system, 200)}")
        
        try:
            url = f"{self.base_url}/api/chat"
            
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
            
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            ollama_logger.debug(f"📦 Payload [{request_id}]: {truncate_long_content(str(payload), 500)}")
            ollama_logger.debug(f"📡 POST {url}")
            
            start_time = time.time()
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            duration = time.time() - start_time
            
            ollama_logger.debug(f"📊 Response Status [{request_id}]: {response.status_code}")
            
            response.raise_for_status()
            
            result = response.json()
            message = result.get("message", {})
            generated_text = message.get("content", "")
            
            # Statistiken loggen
            total_duration = result.get("total_duration", 0) / 1e9  # Nanosekunden zu Sekunden
            load_duration = result.get("load_duration", 0) / 1e9
            prompt_eval_count = result.get("prompt_eval_count", 0)
            eval_count = result.get("eval_count", 0)
            eval_duration = result.get("eval_duration", 0) / 1e9
            
            ollama_logger.info(
                f"✅ Generate erfolgreich [{request_id}]: "
                f"{eval_count} tokens in {duration:.2f}s "
                f"({eval_count / eval_duration:.1f} tokens/s)"
            )
            
            ollama_logger.debug(
                f"📊 Details [{request_id}]: "
                f"load={load_duration:.2f}s, "
                f"prompt_tokens={prompt_eval_count}, "
                f"response_tokens={eval_count}, "
                f"total={total_duration:.2f}s"
            )
            
            ollama_logger.debug(f"💬 Response [{request_id}]: {truncate_long_content(generated_text, 500)}")
            
            return generated_text
            
        except requests.exceptions.Timeout:
            ollama_logger.error(f"⏰ Generate Timeout [{request_id}] (>{self.timeout}s)")
            return None
        except requests.exceptions.RequestException as e:
            ollama_logger.error(f"❌ Generate Request-Fehler [{request_id}]: {str(e)}", exc_info=True)
            return None
        except Exception as e:
            ollama_logger.error(f"❌ Generate unerwarteter Fehler [{request_id}]: {str(e)}", exc_info=True)
            return None
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Optional[str]:
        """
        Chat mit Ollama (OpenAI-kompatibel)
        
        Args:
            messages: Liste von Messages (role + content)
            model: Modell-Name
            temperature: Temperatur
            stream: Streaming aktivieren
        
        Returns:
            Chat-Response oder None bei Fehler
        """
        model = model or self.default_model
        request_id = str(time.time())[-8:]
        
        ollama_logger.info(f"💬 Chat Request [{request_id}] gestartet")
        ollama_logger.info(f"📝 Model: {model}, Messages: {len(messages)}, Temperature: {temperature}")
        
        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            ollama_logger.debug(f"💬 Message {i+1} [{request_id}] ({role}): {truncate_long_content(content, 200)}")
        
        try:
            url = f"{self.base_url}/api/chat"
            
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream,
                "options": {
                    "temperature": temperature
                }
            }
            
            ollama_logger.debug(f"📦 Payload [{request_id}]: {truncate_long_content(str(payload), 500)}")
            ollama_logger.debug(f"📡 POST {url}")
            
            start_time = time.time()
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            duration = time.time() - start_time
            
            ollama_logger.debug(f"📊 Response Status [{request_id}]: {response.status_code}")
            
            response.raise_for_status()
            
            result = response.json()
            message = result.get("message", {})
            response_text = message.get("content", "")
            
            # Statistiken
            total_duration = result.get("total_duration", 0) / 1e9
            eval_count = result.get("eval_count", 0)
            eval_duration = result.get("eval_duration", 0) / 1e9
            
            tokens_per_sec = eval_count / eval_duration if eval_duration > 0 else 0
            
            ollama_logger.info(
                f"✅ Chat erfolgreich [{request_id}]: "
                f"{eval_count} tokens in {duration:.2f}s "
                f"({tokens_per_sec:.1f} tokens/s)"
            )
            
            ollama_logger.debug(f"💬 Response [{request_id}]: {truncate_long_content(response_text, 500)}")
            
            return response_text
            
        except requests.exceptions.Timeout:
            ollama_logger.error(f"⏰ Chat Timeout [{request_id}] (>{self.timeout}s)")
            return None
        except requests.exceptions.RequestException as e:
            ollama_logger.error(f"❌ Chat Request-Fehler [{request_id}]: {str(e)}", exc_info=True)
            return None
        except Exception as e:
            ollama_logger.error(f"❌ Chat unerwarteter Fehler [{request_id}]: {str(e)}", exc_info=True)
            return None
    
    def pull_model(self, model: str) -> bool:
        """
        Lädt ein Modell von Ollama herunter
        
        Args:
            model: Modell-Name (z.B. "llama3.1")
        
        Returns:
            True wenn erfolgreich
        """
        ollama_logger.info(f"📥 Pulling Model: {model}")
        
        try:
            url = f"{self.base_url}/api/pull"
            
            payload = {
                "name": model,
                "stream": False
            }
            
            ollama_logger.debug(f"📡 POST {url}")
            ollama_logger.debug(f"📦 Payload: {payload}")
            
            # Längerer Timeout für Downloads
            response = requests.post(
                url,
                json=payload,
                timeout=600  # 10 Minuten
            )
            
            response.raise_for_status()
            
            result = response.json()
            status = result.get("status", "")
            
            ollama_logger.info(f"✅ Model Pull erfolgreich: {model} ({status})")
            return True
            
        except requests.exceptions.Timeout:
            ollama_logger.error(f"⏰ Model Pull Timeout: {model}")
            return False
        except requests.exceptions.RequestException as e:
            ollama_logger.error(f"❌ Model Pull Fehler: {str(e)}", exc_info=True)
            return False
        except Exception as e:
            ollama_logger.error(f"❌ Unerwarteter Fehler beim Model Pull: {str(e)}", exc_info=True)
            return False
    
    def get_model_info(self, model: str) -> Optional[Dict[str, Any]]:
        """
        Holt Informationen zu einem Modell
        
        Args:
            model: Modell-Name
        
        Returns:
            Model-Info oder None bei Fehler
        """
        ollama_logger.debug(f"ℹ️ Hole Model-Info: {model}")
        
        try:
            url = f"{self.base_url}/api/show"
            
            payload = {"name": model}
            
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            info = response.json()
            
            ollama_logger.debug(f"✅ Model-Info abgerufen: {model}")
            ollama_logger.debug(f"📊 Info: {truncate_long_content(str(info), 500)}")
            
            return info
            
        except Exception as e:
            ollama_logger.error(f"❌ Fehler beim Abrufen der Model-Info: {str(e)}")
            return None


# =================
# CONVENIENCE FUNCTIONS
# =================

def create_ollama_client(**kwargs) -> OllamaClient:
    """
    Erstellt einen Ollama-Client
    
    Returns:
        Konfigurierter OllamaClient
    """
    return OllamaClient(**kwargs)


def quick_generate(prompt: str, model: str = "llama3.1") -> Optional[str]:
    """
    Schnelle Text-Generierung mit Ollama
    
    Args:
        prompt: User-Prompt
        model: Modell-Name
    
    Returns:
        Generierter Text
    """
    client = create_ollama_client(default_model=model)
    return client.generate(prompt)


def quick_chat(messages: List[Dict[str, str]], model: str = "llama3.1") -> Optional[str]:
    """
    Schneller Chat mit Ollama
    
    Args:
        messages: Chat-Messages
        model: Modell-Name
    
    Returns:
        Chat-Response
    """
    client = create_ollama_client(default_model=model)
    return client.chat(messages)


# =================
# EXAMPLE USAGE
# =================

if __name__ == "__main__":
    # Beispiel-Nutzung
    ollama_logger.info("🧪 Starte Ollama-Integration Test...")
    
    # Client erstellen
    client = create_ollama_client()
    
    # Modelle auflisten
    models = client.list_models()
    if models:
        print(f"\n✅ {len(models)} Modelle verfügbar:")
        for model in models:
            print(f"  - {model.get('name')}")
    
    # Text generieren
    print("\n🧠 Teste Text-Generierung...")
    response = client.generate(
        prompt="Was ist Python? Antworte in einem Satz.",
        temperature=0.7
    )
    
    if response:
        print(f"✅ Response: {response}")
    
    # Chat
    print("\n💬 Teste Chat...")
    chat_response = client.chat(
        messages=[
            {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
            {"role": "user", "content": "Erkläre Docker in einem Satz."}
        ]
    )
    
    if chat_response:
        print(f"✅ Chat Response: {chat_response}")
    
    print("\n✅ Ollama-Integration Test abgeschlossen!")
