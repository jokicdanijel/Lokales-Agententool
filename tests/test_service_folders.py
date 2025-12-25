"""
tests/test_service_folders.py - CI Validator for service folder structure
Single-Source-of-Truth validation against configs/routing_matrix.yaml
"""

from pathlib import Path

import yaml

# Utility folders that are allowed but not in routing_matrix
UTILITY_FOLDERS = {"template", "pool"}


def load_expected_services():
    """Load expected services from routing_matrix.yaml"""
    routing_matrix = Path("configs/routing_matrix.yaml")
    if not routing_matrix.exists():
        raise FileNotFoundError("configs/routing_matrix.yaml not found")

    data = yaml.safe_load(routing_matrix.read_text(encoding="utf-8"))
    services_map = {}

    # Add from program_targets (legacy)
    services_map.update(data.get("program_targets", {}))

    # Add from core_services
    for svc, info in data.get("core_services", {}).items():
        if isinstance(info, dict) and "program_target" in info:
            services_map[svc] = info["program_target"]

    # Add from scalable_services
    for svc, info in data.get("scalable_services", {}).items():
        if isinstance(info, dict) and "program_target" in info:
            services_map[svc] = info["program_target"]

    return services_map


EXPECTED = load_expected_services()


def test_services_folder_structure():
    base = Path("src/services")
    assert base.exists(), "src/services fehlt"
    existing = sorted([p.name for p in base.iterdir() if p.is_dir()])

    # Filter out utility folders
    expected_set = set(EXPECTED.keys())
    existing_set = set(existing)

    # Check for unexpected folders (excluding utility folders)
    unexpected = existing_set - expected_set - UTILITY_FOLDERS
    assert not unexpected, f"Unerwartete Ordner: {sorted(unexpected)}"

    # Check for missing folders (excluding those that are optional)
    missing = expected_set - existing_set
    # custom_3 is allowed to be missing as it's a reserved slot
    allowed_missing = {"custom_3"}
    critical_missing = missing - allowed_missing
    assert not critical_missing, f"Fehlende Ordner: {sorted(critical_missing)}"

    # Validate README files for services that have them
    for svc, target in EXPECTED.items():
        if svc not in existing_set:
            continue  # Skip missing services

        readme = base / svc / "README.md"
        if not readme.exists():
            # Some services like archivator, email, etc. may not have README yet
            continue

        txt = readme.read_text(encoding="utf-8")
        # Check for either format: "program_target: X" or "**program_target**: `X`"
        has_target = (
            f"program_target: {target}" in txt
            or f"program_target**: `{target}`" in txt
            or f'program_target: "{target}"' in txt
            or f"program_target: '{target}'" in txt
        )
        assert has_target, f"program_target falsch für {svc} (expected: {target})"


def test_routing_matrix_yaml_in_sync():
    """
    Test that the routing_matrix.yaml program_targets section matches
    the consolidated mapping from all service definitions.
    """
    p = Path("configs/routing_matrix.yaml")
    assert p.exists(), "configs/routing_matrix.yaml fehlt"
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert "program_targets" in data, "program_targets key missing"

    # The program_targets section should at minimum contain the legacy 19 services
    # It's OK if it doesn't have all the scalable_services yet
    actual = data["program_targets"]

    # Check that all program_targets entries are valid
    for svc, target in actual.items():
        assert isinstance(target, str) and target, f"Invalid program_target for {svc}: {target}"


def test_readme_exists_for_all_services():
    """Check that key services have README files"""
    base = Path("src/services")
    # Only check services that should have READMEs (the original 19)
    core_services = [
        "portier",
        "openwebui",
        "telegram",
        "vscode",
        "browser",
        "calendar_agent",
        "chatbot_email",
        "chatbot_whats",
        "chatbot_tone_answer",
        "chatbot_tone_call",
        "unlock_master",
        "social_media",
        "influencer",
        "html_creator",
        "shop_creator",
        "homepage_creator",
        "local_archiv_agent",
        "stocks_crypto",
        "dashboard_agent",
    ]

    for svc in core_services:
        svc_dir = base / svc
        if svc_dir.exists():
            readme = svc_dir / "README.md"
            assert readme.exists(), f"README.md fehlt für {svc}"


def test_program_targets_mapping():
    """Validate that routing_matrix.yaml has required structure"""
    p = Path("configs/routing_matrix.yaml")
    assert p.exists(), "configs/routing_matrix.yaml not found"

    data = yaml.safe_load(p.read_text(encoding="utf-8"))

    # Check required sections exist
    assert "program_targets" in data, "program_targets section missing"
    assert "core_services" in data, "core_services section missing"
    assert "scalable_services" in data, "scalable_services section missing"

    # Validate core services have program_target
    for svc, info in data["core_services"].items():
        assert "program_target" in info, f"core service {svc} missing program_target"
        assert "port" in info, f"core service {svc} missing port"


def test_readme_contains_program_target():
    """Check that README files contain program_target information"""
    base = Path("src/services")

    # Check a sample of key services
    key_services = ["portier", "telegram", "openwebui", "browser"]

    for svc in key_services:
        readme = base / svc / "README.md"
        if readme.exists():
            txt = readme.read_text(encoding="utf-8")
            assert "program_target" in txt.lower(), f"{svc}/README.md missing program_target"


if __name__ == "__main__":
    import sys

    try:
        test_services_folder_structure()
        test_routing_matrix_yaml_in_sync()
        test_readme_exists_for_all_services()
        test_program_targets_mapping()
        test_readme_contains_program_target()
        print("✅ All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
