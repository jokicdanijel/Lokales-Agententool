import requests
from urllib.parse import urlparse
import os
import yaml

# Config laden
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

ALLOWED_DOMAINS = config.get("allowed_domains", [])

def fetch(url: str) -> str:
    """Lädt Webseiteninhalte ab (nur erlaubte Domains)"""
    if not url.strip():
        return "❌ Leere URL"
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        domain = urlparse(url).netloc.lower()
        
        # Domain-Check gegen Whitelist
        allowed = False
        for allowed_domain in ALLOWED_DOMAINS:
            if domain == allowed_domain.lower() or domain.endswith('.' + allowed_domain.lower()):
                allowed = True
                break
        
        if not allowed:
            return f"🚫 Domain blockiert: {domain}\n" \
                   f"💡 Erlaubte Domains: {', '.join(ALLOWED_DOMAINS)}\n" \
                   f"🔧 Erweitere 'allowed_domains' in config/config.yaml"
        
        # Request durchführen
        headers = {
            'User-Agent': 'LocalAgent-Pro/1.0 (Educational Purpose)',
            'Accept': 'text/html,application/xhtml+xml,text/plain,*/*',
        }
        
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        # Content begrenzen (max 10KB für Performance)
        content = response.text[:10000]
        if len(response.text) > 10000:
            content += f"\n\n... (Inhalt auf 10KB begrenzt, Original: {len(response.text)} Zeichen)"
        
        return f"🌐 Webseite geladen: {url}\n" \
               f"📊 Status: {response.status_code} | Größe: {len(content)} Zeichen\n\n" \
               f"{content}"
        
    except requests.exceptions.Timeout:
        return f"⏰ Timeout bei Anfrage: {url}"
    except requests.exceptions.ConnectionError:
        return f"🔌 Verbindungsfehler: {url}"
    except requests.exceptions.HTTPError as e:
        return f"📡 HTTP-Fehler {e.response.status_code}: {url}"
    except Exception as e:
        return f"❌ Web-Fehler: {str(e)}"