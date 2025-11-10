"""
tests/test_service_folders.py - CI Validator for service folder structure
Single-Source-of-Truth validation against scripts/init_service_folders.sh MAP
"""
from pathlib import Path
import yaml

EXPECTED = {
  "portier":"kordp","openwebui":"openweb","telegram":"telep","vscode":"vscop","browser":"browsp",
  "chatbot_email":"emailp","chatbot_whats":"whatp","chatbot_tone_answer":"calp","chatbot_tone_call":"answp",
  "unlock_master":"onlockp","social_media":"somep","influencer":"infmep","calendar_agent":"kalp",
  "html_creator":"htmlp","shop_creator":"shopp","homepage_creator":"homep","local_archiv_agent":"locp",
  "stocks_crypto":"aktienp","dashboard_agent":"dashp",
}


def test_services_folder_structure():
  base = Path("src/services")
  assert base.exists(), "src/services fehlt"
  existing = sorted([p.name for p in base.iterdir() if p.is_dir()])
  assert existing == sorted(EXPECTED.keys()), f"Ordnerabweichung: {existing} != {sorted(EXPECTED.keys())}"
  
  for svc, target in EXPECTED.items():
    readme = base / svc / "README.md"
    assert readme.exists(), f"README.md fehlt für {svc}"
    txt = readme.read_text(encoding="utf-8")
    assert f"program_target: {target}" in txt, f"program_target falsch für {svc}"
    assert f"endpoint_base: http://localhost:12344-12399/{target}" in txt, f"endpoint_base falsch für {svc}"


def test_routing_matrix_yaml_in_sync():
  p = Path("configs/routing_matrix.yaml")
  assert p.exists(), "configs/routing_matrix.yaml fehlt"
  data = yaml.safe_load(p.read_text(encoding="utf-8"))
  assert "program_targets" in data, "program_targets key missing"
  actual = data["program_targets"]
  assert actual == EXPECTED, f"routing_matrix.yaml Drift: {actual} != {EXPECTED}"


if __name__ == "__main__":
    import sys
    try:
        test_services_folder_structure()
        test_routing_matrix_yaml_in_sync()
        print("✅ All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
