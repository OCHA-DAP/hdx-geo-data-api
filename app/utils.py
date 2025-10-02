from asyncio import create_subprocess_exec
from collections.abc import AsyncGenerator
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import HTTPException, status
from httpx import AsyncClient

from .config import HDX_URL


async def create_sozip(input_path: Path, output_path: Path) -> Path:
    """Zip a folder."""
    output_zip = output_path.with_suffix(output_path.suffix + ".zip")
    sozip = await create_subprocess_exec(
        *["gdal", "vsi", "sozip", "create"],
        *[input_path, output_zip],
        "--no-paths",
        "--quiet",
        "--recursive",
    )
    await sozip.wait()
    return output_zip


async def get_download_url(resource_id: str) -> str:
    """Get the download URL for a resource."""
    async with AsyncClient(http2=True) as client:
        r = await client.get(f"{HDX_URL}/api/3/action/resource_show?id={resource_id}")
        return r.json()["result"]["download_url"]


def get_recommended_options(suffixes: list[str]) -> list[str]:
    """Get recommended options for output formats."""
    if ".gdb" in suffixes:
        return ["--lco=TARGET_ARCGIS_VERSION=ARCGIS_PRO_3_2_OR_LATER"]
    if ".parquet" in suffixes:
        return ["--lco=COMPRESSION=ZSTD"]
    if ".shp" in suffixes:
        return ["--lco=ENCODING=UTF-8"]
    return []


async def get_output_path(output_path: Path) -> Path:
    """Get the output path."""
    if output_path.stat().st_size == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unprocessable Content",
        )
    if output_path.is_dir():
        output_path = await create_sozip(output_path, output_path)
    elif len(list(output_path.parent.glob("*"))) > 1:
        output_path = await create_sozip(output_path.parent, output_path)
    return output_path


async def get_temp_dir() -> AsyncGenerator[Path]:
    """Get a temporary directory."""
    temp_dir = TemporaryDirectory()
    yield Path(temp_dir.name)
