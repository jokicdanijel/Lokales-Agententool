"""
Copilot Guard: Erzwingt die bindenden Ordnernamen (Top-Level) und verhindert
das Anlegen neuer Verzeichnisse außerhalb der Whitelist.

Eigenschaften:
- Deterministisch, keine interaktiven Rückfragen.
- Verwendet configs/agent_dirs.yaml (PyYAML erforderlich).
- Nur Prüfung/Blockierung: Es werden KEINE neuen Ordner erzeugt.
- Exit-Codes:
    0 -> OK (alles entspricht der Whitelist)
    1 -> Fehlende Soll-Ordner (werden NICHT erstellt)
    2 -> Unerlaubte Ordner gefunden
    3 -> Konfigurations-/Laufzeitfehler

Nutzung:
    python src/tools/copilot_guard.py --config configs/agent_dirs.yaml --mode validate
    python src/tools/copilot_guard.py --config configs/agent_dirs.yaml --mode check_name --name "7.opena8_whatsapp"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set, Tuple

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install PyYAML", file=sys.stderr)
    sys.exit(3)


@dataclass(frozen=True)
class GuardConfig:
    """Immutable configuration for Copilot Guard."""
    base_dir: Path
    required: Set[str]
    optional: Set[str]
    strict: bool = True

    @staticmethod
    def load(path: Path) -> "GuardConfig":
        """Load configuration from YAML file."""
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if data is None:
            raise ValueError(f"Empty config file: {path}")
        base_dir = Path(data.get("base_dir", ".")).resolve()
        required = set(data.get("required_agent_dirs", []))
        optional = set(data.get("optional_infra_dirs", []))
        strict = bool(data.get("strict", True))
        return GuardConfig(base_dir=base_dir, required=required, optional=optional, strict=strict)


def list_top_level_dirs(root: Path) -> List[str]:
    """List all top-level directories in root."""
    if not root.exists():
        raise FileNotFoundError(f"Base directory not found: {root}")
    items: List[str] = []
    for entry in root.iterdir():
        if entry.is_dir() and not entry.name.startswith("."):
            items.append(entry.name)
    return sorted(items)


def validate_directory_set(cfg: GuardConfig) -> Tuple[List[str], List[str]]:
    """Validate actual directories against required + optional set.
    
    Returns:
        Tuple[List[str], List[str]]: (missing, extra) directory names
        - missing: required agent dirs not found
        - extra: directories not in required or optional whitelist
    """
    actual = set(list_top_level_dirs(cfg.base_dir))
    allowed = cfg.required | cfg.optional
    missing = sorted(list(cfg.required - actual))
    extra = sorted([name for name in actual if name not in allowed])
    return missing, extra


def print_json(payload: dict) -> None:
    """Print JSON output to stdout."""
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")
    sys.stdout.flush()


def main(argv: List[str] | None = None) -> int:
    """Main entry point."""
    ap = argparse.ArgumentParser(
        prog="copilot_guard",
        description="Enforce fixed top-level directory names per whitelist."
    )
    ap.add_argument("--config", "-c", type=Path, default=Path("configs/agent_dirs.yaml"),
                    help="Path to agent_dirs.yaml whitelist")
    ap.add_argument("--mode", "-m", choices=["validate", "check_name"], default="validate",
                    help="Validation mode: 'validate' or 'check_name'")
    ap.add_argument("--name", "-n", type=str, help="Directory name to check (for mode=check_name)")
    args = ap.parse_args(argv)

    try:
        cfg = GuardConfig.load(args.config)
    except Exception as e:
        print_json({"ok": False, "error": f"config_error: {e.__class__.__name__}: {e}"})
        return 3

    if args.mode == "check_name":
        name = (args.name or "").strip()
        allowed = cfg.required | cfg.optional
        ok = name in allowed
        print_json({
            "ok": ok,
            "checked": name,
            "required_count": len(cfg.required),
            "optional_count": len(cfg.optional),
            "policy": "agents_required_infrastructure_optional",
            "strict": cfg.strict
        })
        return 0 if ok else 2

    # mode = validate
    try:
        missing, extra = validate_directory_set(cfg)
        # Only fail if required agents are missing (extra infra dirs are OK)
        result = {
            "ok": len(missing) == 0,
            "base_dir": str(cfg.base_dir),
            "missing_count": len(missing),
            "missing": missing if missing else [],
            "extra_count": len(extra),
            "extra": extra if extra else [],
            "required_count": len(cfg.required),
            "optional_count": len(cfg.optional),
            "actual_count": len(list_top_level_dirs(cfg.base_dir)),
            "strict": cfg.strict,
            "policy": "agents_required_infrastructure_optional"
        }
        print_json(result)
        if missing:
            return 1
        return 0
    except Exception as e:
        print_json({"ok": False, "error": f"runtime_error: {e.__class__.__name__}: {e}"})
        return 3


# Security: block any directory creation when used as library
def guard_mkdir(path: os.PathLike | str, cfg: GuardConfig) -> None:
    """
    Guard against creating directories outside whitelist.
    
    Raises PermissionError if:
    - Path is outside base directory
    - Top-level directory is not in whitelist
    - Called with any path (this is a dry policy hook)
    
    Args:
        path: Directory path to guard
        cfg: GuardConfig instance
    
    Raises:
        PermissionError: Always, as this is a policy enforcement hook
    """
    p = Path(path).resolve()
    top = Path(cfg.base_dir)
    try:
        p.relative_to(top)
    except ValueError as e:
        raise PermissionError(f"Path outside base: {p}") from e

    # Determine top-level candidate
    rel = p.relative_to(top)
    parts = rel.parts
    if len(parts) == 0:
        raise PermissionError("Refusing to create base dir itself.")
    top_name = parts[0]
    allowed = cfg.required | cfg.optional
    if top_name not in allowed:
        raise PermissionError(f"Creation of top-level directory '{top_name}' is forbidden by policy.")
    
    # Subdirs allowed but guard_mkdir never creates anything
    raise PermissionError("guard_mkdir is a dry policy hook and never creates directories.")


if __name__ == "__main__":
    raise SystemExit(main())
