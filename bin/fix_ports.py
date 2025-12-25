#!/usr/bin/env python3
"""
Fix all PORT conflicts: Reassign agents 3-21 to unique ports 12347-12367.
Use ports: core (1-2) = 12344-12345, dashboard = 12349, agents 3-21 = 12347-12348, 12350-12348, 12351-12367
"""

import os
import re

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Port assignment (no conflicts!)
PORT_MAP = {
    "opena3": 12347,
    "opena4": 12348,
    "opena5": 12350,
    "opena6": 12351,
    "opena7": 12352,
    "opena8": 12353,
    "opena9": 12354,
    "opena10": 12355,
    "opena11": 12356,
    "opena12": 12357,
    "opena13": 12358,
    "opena14": 12359,
    "opena15": 12360,
    "opena16": 12361,
    "opena17": 12362,
    "opena18": 12363,
    "opena19": 12364,
    "opena20": 12365,  # dashboard on 12349
    "opena21": 12366,
}


def fix_file(filepath, agent_name):
    """Fix PORT in a Python file."""
    if not os.path.exists(filepath):
        return False

    with open(filepath) as f:
        content = f.read()

    port = PORT_MAP.get(agent_name, 12367)

    # Replace PORT = <number>
    content = re.sub(r"PORT = \d{5}", f"PORT = {port}", content)

    # Replace PORT = int(os.getenv(..., "<number>"))
    content = re.sub(
        r'PORT = int\(os\.getenv\([^)]*,\s*"?\d{5}"?\)',
        f'PORT = int(os.getenv("OPENA{agent_name[5:]}_PORT", "{port}"))',
        content,
    )

    with open(filepath, "w") as f:
        f.write(content)

    return True


def fix_bash_script(filepath, agent_name):
    """Fix PORT in a bash start script."""
    if not os.path.exists(filepath):
        return False

    with open(filepath) as f:
        content = f.read()

    port = PORT_MAP.get(agent_name, 12367)

    # Replace PORT=<number>
    content = re.sub(r"PORT=\d{5}", f"PORT={port}", content)

    with open(filepath, "w") as f:
        f.write(content)

    return True


print("🔧 Fixing PORT conflicts...\n")

for agent in sorted(PORT_MAP.keys()):
    port = PORT_MAP[agent]
    num = agent[5:]  # "opena3" -> "3"

    # Find agent directory
    agent_dirs = [d for d in os.listdir(".") if d.lower().endswith(f"opena{num}_") or f"_opena{num}" in d.lower()]
    if not agent_dirs:
        print(f"⏭️  {agent}: Directory not found")
        continue

    agent_dir = agent_dirs[0]

    # Fix main Python files
    main_py = os.path.join(agent_dir, "main_*.py")
    import glob

    for py_file in glob.glob(main_py):
        if fix_file(py_file, agent):
            print(f"✅ {agent}: Fixed {py_file} -> PORT {port}")

    # Fix start scripts
    start_script = os.path.join(agent_dir, "bin", f"start_opena{num}.sh")
    if fix_bash_script(start_script, agent):
        print(f"✅ {agent}: Fixed {start_script} -> PORT {port}")

print("\n✅ All PORT conflicts fixed!")
print("Next: bin/ops.sh stop && bin/ops.sh start")
