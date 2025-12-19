#!/usr/bin/env python3
"""
FINAL FIX: Clean all agent start scripts of .env-loading logic.
- Remove all .env sourcing patterns
- Keep only venv activation
- Agents get env vars from ops.sh
"""

import os
import re
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

SCRIPTS = [
    "3.opena4_telegram/bin/start_opena4.sh",
    "4.opena5_vscode/bin/start_opena5.sh",
    "9.opena10_call_tracking/bin/start_opena10.sh",
    "10.opena11_unlock/bin/start_opena11.sh",
    "11.opena12_social_media/bin/start_opena12.sh",
    "12.opena13_influencer/bin/start_opena13.sh",
    "13.opena14_calendar/bin/start_opena14.sh",
    "14.opena15_html/bin/start_opena15.sh",
    "15.opena16_shop/bin/start_opena16.sh",
    "16.opena17_homepagecreator/bin/start_opena17.sh",
    "17.opena18_CMR/bin/start_opena18.sh",
    "18.opena19_Aktien&Crypto/bin/start_opena19.sh",
    "20.opena21_workflow/bin/start_opena21.sh",
]

def clean_env_loading(content):
    """Remove all .env loading logic."""
    lines = content.split('\n')
    result = []
    skip_until_fi = False
    
    for i, line in enumerate(lines):
        # Skip .env loading blocks
        if re.search(r'if\s+\[\[\s*-f.*\.env', line):
            skip_until_fi = True
            continue
        elif re.search(r'if\s+\[\s*-f.*\.env', line):
            skip_until_fi = True
            continue
        
        # End of block
        if skip_until_fi and re.match(r'^\s*fi\s*$', line):
            skip_until_fi = False
            continue
        
        if skip_until_fi:
            continue
        
        # Remove orphan set +a / set -a lines
        if re.match(r'^\s*set\s*[+-]a\s*$', line):
            continue
        
        # Remove source lines that load .env
        if re.search(r'source\s+.*\.env', line) or re.search(r'\.\s+.*\.env', line):
            continue
        
        result.append(line)
    
    # Remove consecutive blank lines
    final = []
    prev_blank = False
    for line in result:
        is_blank = line.strip() == ''
        if is_blank and prev_blank:
            continue
        final.append(line)
        prev_blank = is_blank
    
    return '\n'.join(final)


print("🔥 FINAL FIX: Cleaning .env-loading logic from agent scripts\n")

fixed_count = 0
for script in SCRIPTS:
    if not os.path.exists(script):
        print(f"⏭️  {script} - NOT FOUND")
        continue
    
    try:
        with open(script, 'r') as f:
            original = f.read()
        
        cleaned = clean_env_loading(original)
        
        with open(script, 'w') as f:
            f.write(cleaned)
        
        print(f"✅ {script}")
        fixed_count += 1
    except Exception as e:
        print(f"❌ {script}: {e}")

print(f"\n✅ Fixed {fixed_count}/{len(SCRIPTS)} scripts")
print("\nNext: bin/ops.sh start")
