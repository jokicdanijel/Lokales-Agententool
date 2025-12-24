#!/usr/bin/env python3
"""
🚀 opena12 Social Media Agent Starter
Aktiviert venv, lädt .env und startet mit Uvicorn
"""

import os
from pathlib import Path

# Stelle sicher, dass wir im richtigen Verzeichnis sind
BASE_DIR = Path(__file__).parent
os.chdir(BASE_DIR)

# Lade .env
from dotenv import load_dotenv

load_dotenv(BASE_DIR / ".env")

# Zeige Config
print("=" * 60)
print("🚀 OPENA12 Social Media Agent Starting...")
print("=" * 60)
print(f"📂 Working Dir: {BASE_DIR}")
print(f"🔑 OpenAI Key: {os.getenv('OPENAI_API_KEY_OPENA12', 'NOT SET')[:20]}...")
print(f"🌐 Port: {os.getenv('OPENA12_PORT', '12357')}")
print("=" * 60)

# Starte Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host="0.0.0.0", port=int(os.getenv("OPENA12_PORT", "12357")), reload=False, log_level="info"
    )
