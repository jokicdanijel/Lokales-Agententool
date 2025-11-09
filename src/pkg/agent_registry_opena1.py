""""""
Client-/Registry-Modul für opena1.
- Liest Token aus gemeinsamer .env im Dashboard-Ordner
- Registriert sich beim Dashboard
- Periodischer Status-Sync (optional)
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional

import httpx
from security import _read_env_token  # nutzt dasselbe Token-Format wie Dashboard

class OpenA1RegistryClient:
    def __init__(self,
                 dashboard_url: str = "http://127.0.0.1:12349",
                 self_id: str = "opena1",
                 self_endpoint: str = "http://127.0.0.1:12344",
                 timeout_s: float = 5.0):
        self.dashboard_url = dashboard_url.rstrip("/")
        self.self_id = self_id
        self.self_endpoint = self_endpoint
        self.timeout = timeout_s
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def _headers(self) -> Dict[str, str]:
        token = _read_env_token()
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async def register_once(self) -> Dict[str, Any]:
        """
        Registriert opena1 beim Dashboard über den konfliktfreien Pfad.
        Rückgabe: {"strict": True, "status": "registered", "agent": {...}}
        """
        url = f"{self.dashboard_url}/api/agent/register"
        data = {"agent_id": self.self_id, "endpoint": self.self_endpoint}
        r = await self._client.post(url, headers=await self._headers(), json=data)
        # Fehler explizit weiterreichen (damit Logs klar sind)
        r.raise_for_status()
        return r.json()

    async def get_all_status(self) -> Dict[str, Any]:
        url = f"{self.dashboard_url}/api/status/all"
        r = await self._client.get(url, headers=await self._headers())
        r.raise_for_status()
        return r.json()

    async def periodic_sync(self, interval_s: float = 30.0):
        """
        Optionaler Endlossync: versucht Register, holt Status, schläft.
        Brich mit CancelError (Task cancel) ab.
        """
        while True:
            try:
                # versuche Registrierung – idempotent aus Sicht des Dashboards
                try:
                    await self.register_once()
                except httpx.HTTPStatusError as e:
                    # 409/400/401/500 etc. – nicht fatal, Logs genügen
                    print(f"[opena1.registry] Register: {e.response.status_code} {e.response.text}")

                st = await self.get_all_status()
                print("[opena1.registry] Status-Sync ok.", st)
            except Exception as e:
                print(f"[opena1.registry] Fehler im periodic_sync: {e}")
            await asyncio.sleep(interval_s)

    async def aclose(self):
        await self._client.aclose()


# Manuell testbar:
# python -m agent_registry_opena1
if __name__ == "__main__":
    async def _main():
        client = OpenA1RegistryClient()
        try:
            res = await client.register_once()
            print(json.dumps(res, indent=2, ensure_ascii=False))
            st = await client.get_all_status()
            print(json.dumps(st, indent=2, ensure_ascii=False))
        finally:
            await client.aclose()
    asyncio.run(_main())


