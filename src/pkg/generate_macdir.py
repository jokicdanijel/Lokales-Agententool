#!/usr/bin/env python3
import json
from pathlib import Path

MAC = {
    "system": "Portier / ELION Hyper-Dashboard 2.0",
    "version": "1.0",
    "generated_by": "generate_macdir.py",
}

p = Path("MAC_DIR_SYSTEM.json")
with p.open("w", encoding="utf-8") as f:
    json.dump(MAC, f, ensure_ascii=False, indent=2)

print(f"Wrote {p.resolve()}")
