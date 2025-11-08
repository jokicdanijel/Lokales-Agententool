#!/usr/bin/env python3
"""Seed-Script: Beispiel-Prompts an OpenWebUI-Agent"""

import json
import urllib.request
import os
import sys

BASE = "http://127.0.0.1:12347"
OPENA2 = "http://127.0.0.1:12345"

def seed_prompts():
    """Sendet Beispiel-Prompts und speichert Antworten in archivp"""
    
    prompts = [
        "What is ELION Hyper-Dashboard?",
        "Describe the role of an OpenWebUI agent",
        "How do I register a new agent?"
    ]
    
    for prompt in prompts:
        print(f"\n📝 Sende Prompt: {prompt}")
        
        try:
            # POST an OpenWebUI-Agent
            payload = {
                "prompt": prompt,
                "context": {"system": "You are a helpful assistant about ELION."}
            }
            req = urllib.request.Request(
                f"{BASE}/command",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                response = json.loads(r.read().decode())
                print(f"✓ Antwort: {json.dumps(response, indent=2)}")
                
                # Speichere in archivp
                archive_payload = {
                    "op": "WRITE",
                    "path": f"2025/11/06/seed_{prompts.index(prompt)}.json",
                    "content": {
                        "strict": True,
                        "ts": "2025-11-06T12:00:00Z",
                        "prompt": prompt,
                        "response": response
                    }
                }
                
                req2 = urllib.request.Request(
                    f"{OPENA2}/store/archivp",
                    data=json.dumps(archive_payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req2, timeout=10) as r2:
                    archive_result = json.loads(r2.read().decode())
                    print(f"✓ Gespeichert in archivp: {archive_result.get('path')}")
        
        except Exception as e:
            print(f"✗ Fehler: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("ELION Seed – Beispiel-Prompts")
    print("=" * 60)
    seed_prompts()
    print("\n✅ Seeding abgeschlossen")
