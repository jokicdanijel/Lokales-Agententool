import json, urllib.request, time

BASE = "http://127.0.0.1:12345"

def _post(path, payload):
    req = urllib.request.Request(f"{BASE}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

def _get(path):
    with urllib.request.urlopen(f"{BASE}{path}") as r:
        return json.loads(r.read().decode())

def test_write_and_last():
    ts = int(time.time())
    out = _post("/store/archivp", {"src": "kordp", "dst": "opena2", "kind": "CMD", "payload": {"msg": "hi"}})
    assert out.get("written") is True
    last = _get("/archiv/last?n=5")
    assert last.get("count", 0) >= 1
    assert any("opena2_CMD.json" in i["path"] for i in last.get("items", []))
