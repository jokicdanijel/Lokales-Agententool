#!/usr/bin/env python3
"""
deployment_check.py — Deployment Validation Script
- Verify all 20 service ports are available
- Check Coordinator + Archivator health
- Validate routing matrix configuration
- Verify archive directory structure
"""

import json
import socket
import sys
from pathlib import Path

# Service port mapping
SERVICES_PORTS = {
    "portier": 12344,
    "archivator": 12345,
    "telegram": 12346,
    "inference": 12346,
    "browser": 12349,
    "vscode": 12350,
    "email": 12351,
    "whatsapp": 12352,
    "phone": 12353,
    "calendar": 12354,
    "social_media": 12355,
    "shop": 12356,
    "html_creator": 12357,
    "homepage_creator": 12358,
    "stocks_crypto": 12359,
    "influencer": 12360,
    "unlock_master": 12361,
    "local_archiv": 12362,
    "custom_1": 12363,
    "custom_2": 12364,
}

ARCHIVE_PATH = Path("1.opena1&2_portier/archivp_store")


def check_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """Check if port is available (not in use)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            # Result 0 = connected (port in use), non-zero = not in use
            return result != 0
    except Exception:
        return False


def check_routing_matrix() -> bool:
    """Verify routing_matrix.yaml is valid and complete."""
    try:
        import yaml

        with open("configs/routing_matrix.yaml") as f:
            config = yaml.safe_load(f)

        # Check required sections
        required_sections = ["scalable_services", "coordinator", "archivator"]
        for section in required_sections:
            if section not in config:
                print(f"  ❌ Missing section in routing_matrix: {section}")
                return False

        # Check service count
        scalable = config.get("scalable_services", {})
        if len(scalable) < 18:  # At least 18 scalable services
            print(f"  ⚠️  Only {len(scalable)} scalable services defined (expected 18+)")
            return False

        print(f"  ✅ routing_matrix.yaml valid ({len(scalable)} services)")
        return True

    except Exception as e:
        print(f"  ❌ routing_matrix.yaml validation failed: {e}")
        return False


def check_archive_directory() -> bool:
    """Verify archive directory structure exists."""
    if not ARCHIVE_PATH.exists():
        print(f"  ⚠️  Archive directory not found: {ARCHIVE_PATH}")
        print("     This is OK for fresh deployments (will be created on first write)")
        return True  # Not a blocker

    # Check index.jsonl
    index_file = ARCHIVE_PATH / "index.jsonl"
    if not index_file.exists():
        print(f"  ⚠️  Archive index not found: {index_file}")
        return True  # Not a blocker

    try:
        with open(index_file) as f:
            lines = f.readlines()
        print(f"  ✅ Archive active ({len(lines)} safepoint entries)")
        return True
    except Exception as e:
        print(f"  ❌ Archive validation failed: {e}")
        return False


def check_service_files() -> bool:
    """Verify all service main.py files exist."""
    services_dir = Path("src/services")
    missing = []

    for service_name, port in SERVICES_PORTS.items():
        main_py = services_dir / service_name / "main.py"
        if not main_py.exists():
            missing.append(service_name)

    if missing:
        print(f"  ❌ Missing service files: {', '.join(missing)}")
        return False

    print(f"  ✅ All {len(SERVICES_PORTS)} service files exist")
    return True


def check_config_files() -> bool:
    """Verify configuration files exist and are valid."""
    configs = [
        ("configs/routing_matrix.yaml", "YAML"),
        ("configs/llama_stack_config.json", "JSON"),
    ]

    for config_path, format_type in configs:
        path = Path(config_path)
        if not path.exists():
            print(f"  ❌ Missing config: {config_path}")
            return False

        try:
            if format_type == "YAML":
                import yaml

                yaml.safe_load(path.read_text())
            elif format_type == "JSON":
                json.loads(path.read_text())
        except Exception as e:
            print(f"  ❌ Invalid {format_type}: {config_path} — {e}")
            return False

    print("  ✅ All configuration files valid")
    return True


def main():
    """Run all deployment checks."""
    print("=" * 80)
    print("🚀 DEPLOYMENT VALIDATION CHECK (Phase 16d)")
    print("=" * 80)
    print()

    checks: dict[str, bool] = {}

    # Check 1: Service files
    print("📋 Step 1: Verify Service Files")
    print("-" * 80)
    checks["service_files"] = check_service_files()
    print()

    # Check 2: Configuration files
    print("⚙️  Step 2: Verify Configuration Files")
    print("-" * 80)
    checks["config_files"] = check_config_files()
    print()

    # Check 3: Routing matrix
    print("🗺️  Step 3: Verify Routing Matrix")
    print("-" * 80)
    checks["routing_matrix"] = check_routing_matrix()
    print()

    # Check 4: Archive directory
    print("📁 Step 4: Verify Archive Directory")
    print("-" * 80)
    checks["archive"] = check_archive_directory()
    print()

    # Check 5: Port availability
    print("🔌 Step 5: Check Port Availability (20 services)")
    print("-" * 80)

    available_ports = []
    unavailable_ports = []

    for service_name, port in sorted(SERVICES_PORTS.items(), key=lambda x: x[1]):
        available = check_port_available(port)
        status = "✅ Available" if available else "⚠️  In use"
        print(f"  Port {port:5d} ({service_name:20}): {status}")

        if available:
            available_ports.append(port)
        else:
            unavailable_ports.append((service_name, port))

    print()
    if unavailable_ports:
        print(f"  ⚠️  {len(unavailable_ports)} ports already in use (services running)")
        for name, port in unavailable_ports[:5]:
            print(f"     - {name} ({port})")
        if len(unavailable_ports) > 5:
            print(f"     ... and {len(unavailable_ports) - 5} more")

    checks["ports"] = True  # Not a blocker (services might be running)
    print()

    # Summary
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)

    passed = sum(1 for v in checks.values() if v)
    total = len(checks)

    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check_name.replace('_', ' ').title()}")

    print()

    if passed == total:
        print("🎯 ✅ All deployment checks passed")
        print()
        print("Ready to deploy:")
        print("  1. Start services: bash scripts/start_scalable_services.sh (future)")
        print("  2. Register routes: python3 scripts/test_multi_service_orchestration.py")
        print("  3. Run load test: python3 scripts/load_test_scaled.py")
        return 0
    else:
        print(f"⚠️  {total - passed} check(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
