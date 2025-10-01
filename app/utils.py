from collections.abc import AsyncGenerator
from pathlib import Path
from tempfile import TemporaryDirectory

from httpx import AsyncClient


async def get_temp_dir() -> AsyncGenerator[Path]:
    """Get a temporary directory."""
    temp_dir = TemporaryDirectory()
    try:
        yield Path(temp_dir.name)
    finally:
        del temp_dir


async def get_download_url(resource_id: str) -> str:
    """Get the download URL for a resource."""
    async with AsyncClient(http2=True) as client:
        r = await client.get(
            f"https://data.humdata.org/api/3/action/resource_show?id={resource_id}",
        )
        return r.json()["result"]["download_url"]
