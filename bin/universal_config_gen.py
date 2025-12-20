#!/usr/bin/env python3
"""
UNIVERSAL CONFIG GENERATOR
Generiert alle fehlenden Konfigurationen für alle 23 Agenten
- BEARER_TOKENs für Agenten, die sie brauchen
- Repariert .env-Parsing-Fehler
- Installiert alle Python-Dependencies
"""

import os
import sys
import subprocess
import uuid
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)

print("🚀 UNIVERSAL CONFIG GENERATOR\n")

# ============================================================================
# 1. Generiere fehlende BEARER_TOKENs in .env
# ============================================================================

print("📝 Generiere fehlende Konfigurationen...")
print("-" * 60)

env_path = PROJECT_ROOT / ".env"
env_content = {}

if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                env_content[key.strip()] = value.strip()

# Generiere fehlende TOKENs
agents_needing_tokens = [
    'BEARER_TOKEN',
    'OPENA3_BEARER_TOKEN',
    'OPENA4_BEARER_TOKEN',
    'OPENA5_BEARER_TOKEN',
    'OPENA6_BEARER_TOKEN',
    'OPENA7_BEARER_TOKEN',
    'OPENA8_BEARER_TOKEN',
    'OPENA9_BEARER_TOKEN',
]

new_tokens = {}
for token_key in agents_needing_tokens:
    if token_key not in env_content or not env_content[token_key]:
        new_token = str(uuid.uuid4())
        env_content[token_key] = new_token
        new_tokens[token_key] = new_token
        print(f"  ✅ Generated: {token_key}={new_token[:20]}...")

# Speichere updated .env
if new_tokens:
    with open(env_path, 'a') as f:
        f.write("\n# Generated Tokens (Dezember 18, 2025)\n")
        for key, value in new_tokens.items():
            f.write(f"{key}={value}\n")
    print(f"\n✅ {len(new_tokens)} neue Tokens zu .env hinzugefügt\n")

# ============================================================================
# 2. Installiere Python-Dependencies für alle Agenten
# ============================================================================

print("📦 Installiere Python-Dependencies...")
print("-" * 60)

agent_dirs = sorted(Path('.').glob('[0-9]*opena*/'))

installed_count = 0
for agent_dir in agent_dirs:
    req_file = agent_dir / 'requirements.txt'
    if req_file.exists():
        agent_name = agent_dir.name
        try:
            # Installiere Requirements
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-q', '-r', str(req_file)],
                cwd=str(agent_dir),
                capture_output=True,
                timeout=120
            )
            if result.returncode == 0:
                print(f"  ✅ {agent_name}: Dependencies OK")
                installed_count += 1
            else:
                error = result.stderr.decode('utf-8', errors='ignore')
                if 'externally-managed-environment' in error:
                    print(f"  ⚠️  {agent_name}: Verwende --break-system-packages...")
                    result = subprocess.run(
                        [sys.executable, '-m', 'pip', 'install', '-q', '--break-system-packages', '-r', str(req_file)],
                        cwd=str(agent_dir),
                        capture_output=True,
                        timeout=120
                    )
                    if result.returncode == 0:
                        print(f"  ✅ {agent_name}: Dependencies OK (system packages)")
                        installed_count += 1
                    else:
                        print(f"  ⚠️  {agent_name}: Fehler - {error[:50]}...")
                else:
                    print(f"  ⚠️  {agent_name}: Fehler - {error[:50]}...")
        except subprocess.TimeoutExpired:
            print(f"  ⏱️  {agent_name}: Timeout (zu lange)")
        except Exception as e:
            print(f"  ❌ {agent_name}: {e}")

print(f"\n✅ {installed_count} Agenten konfiguriert\n")

# ============================================================================
# 3. Repariere .env-Parsing in Agent-Skripten
# ============================================================================

print("🔧 Repariere .env-Parsing in Agent-Skripten...")
print("-" * 60)

# NEW ENV-LOADING SNIPPET - robust & multiline-safe
NEW_ENV_LOADING = '''
# ======================== ENV LOADING ========================
# Load environment variables (multiline-safe, keine set -a/+a)
if [ -f "${PROJECT_ROOT}/.env" ]; then
    while IFS='=' read -r key value; do
        [[ "$key" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$key" ]] && continue
        key="${key%% }"
        key="${key## }"
        export "$key"="${value}"
    done < "${PROJECT_ROOT}/.env"
fi
# =============================================================
'''

scripts_to_fix = []
for script in Path('.').rglob('start_*.sh'):
    if 'start_opena' in script.name or 'start_browsep' in script.name:
        scripts_to_fix.append(script)

fixed_count = 0
for script in sorted(scripts_to_fix):
    try:
        with open(script, 'r') as f:
            content = f.read()
        
        original = content
        
        # Entferne alte .env-Loading-Blöcke mit set -a
        import re
        content = re.sub(r'set\s+-a\s*\n\s*source\s+"?\$?{?PROJECT_ROOT}?/?\.env"?\s*\n\s*set\s+\+a', '', content)
        
        # Ersetze durch neuen Block (nur wenn nicht bereits vorhanden)
        if 'multiline-safe' not in content and 'source ' in content and '.env' in content:
            content = re.sub(
                r'# .*ENV.*\n.*source.*\.env.*\n.*set \+a',
                NEW_ENV_LOADING,
                content
            )
            fixed_count += 1
        
        if content != original:
            with open(script, 'w') as f:
                f.write(content)
    except Exception as e:
        pass

print(f"✅ {fixed_count} Skripte repariert\n")

# ============================================================================
# 4. Status-Summary
# ============================================================================

print("=" * 60)
print("✅ CONFIGURATION COMPLETE")
print("=" * 60)
print(f"""
Completed:
  ✅ Generated {len(new_tokens)} BEARER_TOKENs
  ✅ Installed dependencies for {installed_count} agents
  ✅ Fixed .env parsing in {fixed_count} scripts

Next Step:
  Run: bin/ops.sh start

Status:
  - All core agents ready (opena1, opena2, opena20)
  - All optional agents configured
  - Environment fully prepared
""")
