"""
Safepoint-Manager (lesen/suchen)
- Arbeitet direkt auf dem archivp-Baum:
  /home/danijel-jd/.../Gesamtprojekt/1.portier_openai/archivp/YYYY/MM/DD/SP...json
- Bietet query() für einfache Filter und get_content() für Dateiinhalt.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


BASE_ROOT = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt").resolve()
ARCHIVP_ROOT = (BASE_ROOT / "1.portier_openai" / "archivp").resolve()


class SafepointManager:
    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = (root or ARCHIVP_ROOT).resolve()

    async def query(self, q: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        q: { "date":"2025-11-05", "kind":"CMD|RESP|ERR", "src":"...", "dst":"..." }
        Es wird nur nach Dateinamen (SP.._src→dst_kind.json) und Datumspfad gefiltert.
        """
        date = (q or {}).get("date")  # 'YYYY-MM-DD'
        kind = (q or {}).get("kind")
        src = (q or {}).get("src")
        dst = (q or {}).get("dst")

        root = self.root
        if date:
            try:
                y, m, d = date.split("-")
                root = root / y / m / d
            except Exception:
                # ungültiges Datum -> leer zurück
                return []

        out: List[Dict[str, Any]] = []
        if not root.exists():
            return out

        for p in root.rglob("SP*_*.json"):
            name = p.name
            # Name: SP{epoch}_{src}→{dst}_{kind}.json
            if kind and not name.endswith(f"_{kind}.json"):
                continue
            if src and f"_{src}→" not in name:
                continue
            if dst and f"→{dst}_" not in name:
                continue
            out.append({
                "path": str(p.relative_to(self.root)),
                "abs": str(p),
                "name": name
            })
        return sorted(out, key=lambda x: x["name"])

    async def get_content(self, rel_path: str) -> Dict[str, Any]:
        p = (self.root / rel_path.lstrip("/")).resolve()
        if not str(p).startswith(str(self.root)):
            raise FileNotFoundError("Pfad außerhalb von archivp")
        if not p.exists() or not p.is_file():
            raise FileNotFoundError("Safepoint nicht gefunden")

        raw = p.read_text(encoding="utf-8")
        try:
            obj = json.loads(raw)
        except Exception:
            obj = {"raw": raw}
        return {"path": str(p), "content": obj}

