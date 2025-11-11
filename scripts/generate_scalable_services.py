#!/usr/bin/env python3
"""
generate_scalable_services.py — Bulk Service Generation
Creates 16 services (12349-12364) from template
"""

import os
import shutil
from pathlib import Path

# Service mapping (port, program_target, service_name)
SERVICES = [
    (12349, "browsp", "browser"),
    (12350, "vscop", "vscode"),
    (12351, "emailp", "email"),
    (12352, "whatp", "whatsapp"),
    (12353, "phonep", "phone"),
    (12354, "kalp", "calendar"),
    (12355, "somep", "social_media"),
    (12356, "shopp", "shop"),
    (12357, "htmlp", "html_creator"),
    (12358, "homep", "homepage_creator"),
    (12359, "aktienp", "stocks_crypto"),
    (12360, "infmep", "influencer"),
    (12361, "onlockp", "unlock_master"),
    (12362, "locp", "local_archiv"),
    (12363, "cust1", "custom_1"),
    (12364, "cust2", "custom_2"),
]

TEMPLATE_FILE = Path(__file__).parent.parent / "src" / "services" / "template" / "main.py"
SERVICES_DIR = Path(__file__).parent.parent / "src" / "services"

print("=" * 70)
print("🔄 Bulk Service Generation (16 Services: 12349-12364)")
print("=" * 70)
print()

count = 0
for port, target, service_name in SERVICES:
    service_dir = SERVICES_DIR / service_name
    
    # Skip if already exists
    if service_dir.exists():
        print(f"✅ {service_name:20} ({port}) — Already exists")
        continue
    
    # Create directory
    service_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy template
    main_py = service_dir / "main.py"
    shutil.copy(TEMPLATE_FILE, main_py)
    
    # Create wrapper script
    run_sh = service_dir / "run.sh"
    run_sh.write_text(f"""#!/usr/bin/env bash
export SERVICE_NAME="{service_name}"
export PROGRAM_TARGET="{target}"
export PORT="{port}"
exec python3 "$(dirname "${{BASH_SOURCE[0]}}")/main.py" "$@"
""")
    run_sh.chmod(0o755)
    
    # Create requirements.txt
    req_txt = service_dir / "requirements.txt"
    req_txt.write_text("""fastapi==0.121.0
uvicorn==0.30.0
pydantic==2.12.4
pydantic-settings==2.12.0
httpx==0.27.2
python-multipart==0.0.7
""")
    
    print(f"✨ {service_name:20} ({port}, {target:8})")
    count += 1

print()
print("=" * 70)
print(f"✅ Generated {count} services")
print("=" * 70)
print()
print("📝 To start a service:")
print("   cd src/services/<service_name>")
print("   source ../../.venv/bin/activate")
print("   ./run.sh")
print()
print("📋 Start all 16 services (background):")
print("   bash scripts/start_scalable_services.sh")
