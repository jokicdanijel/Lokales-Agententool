import httpx

from .config import get_settings
from .models import Safepoint

settings = get_settings()


async def write_safepoint(sp: Safepoint) -> None:
    url = f"{settings.OPENA2_URL}/store/archivp"
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(url, json=sp.model_dump())
