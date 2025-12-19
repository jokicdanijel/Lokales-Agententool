#!/usr/bin/env python3
"""
AGGRESSIVE FIX: Entferne ALLE .env-Loading-Versuche aus Agent-Startskripten
Diese Skripte sollen Keys NICHT laden, sondern von ops.sh übergeben erhalten.
"""

import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)

# Pattern für alle .env-Loading-Varianten
ENV_LOAD_PATTERNS = [
    # export $(grep ...) xargs Pattern
    r'export\s+\$\(grep[^)]*\)\s+\|\s+xargs\)',
    # source .env Pattern
    r'source\s+["\']?\.\.?/?\.env["\']?',
    # . .env Pattern
    r'\.\s+["\']?\.\.?/?\.env["\']?',
    # if [ -f ... .env ]; then ... source / export ... fi Pattern
    r'if\s+\[\s+-f\s+["\'][^\]]*\.env["\']?\s*\]\s*;\s*then\s*\n.*?fi',
]

# Finde alle Start-Skripte
scripts = list(Path('.').rglob('start_*.sh')) + list(Path('.').rglob('*_start.sh'))

print(f"🔥 Entferne ALL .env-Loading aus {len(scripts)} Agent-Skripten...\n")

fixed_count = 0

for script in sorted(scripts):
    try:
        with open(script, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Entferne alle .env-Loading-Patterns
        for pattern in ENV_LOAD_PATTERNS:
            content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
        
        # Entferne leere if-Blöcke
        content = re.sub(r'if\s+\[\s+-f\s+[^\]]*\.env[^\]]*\]\s*;\s*then\s*elif.*?fi', '', content, flags=re.DOTALL)
        content = re.sub(r'if\s+\[\s+-f\s+[^\]]*\.env[^\]]*\]\s*;\s*then\s*else.*?fi', '', content, flags=re.DOTALL)
        
        # Bereinige Whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        if content != original_content:
            # Backup
            with open(f"{script}.bak", 'w') as f:
                f.write(original_content)
            
            # Speichere fix
            with open(script, 'w') as f:
                f.write(content)
            
            print(f"✅ {script}")
            fixed_count += 1
    
    except Exception as e:
        print(f"⚠️  {script}: {e}")

print(f"\n🎉 {fixed_count} Skripte bereinigt!")
print("\n💡 Umgebungsvariablen werden jetzt von ops.sh durchgereicht:")
print("   OPENAI_API_KEY_OPENA1, OPENAI_API_KEY_OPENA2, etc.")
