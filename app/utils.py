from asyncio import create_subprocess_exec
from collections.abc import AsyncGenerator
from pathlib import Path
from shutil import rmtree, unpack_archive
from tempfile import TemporaryDirectory

from fastapi import HTTPException, status
from httpx import AsyncClient

from .config import HDX_URL
from .models import VectorModel

TARGET_ARCGIS_VERSION = "--layer-creation-option=TARGET_ARCGIS_VERSION="
COMPRESSION = "--layer-creation-option=COMPRESSION="
ENCODING = "--layer-creation-option=ENCODING="


def add_default_options(options: list[str], params: VectorModel) -> list[str]:
    """Add default options."""
    response = [*options]
    suffixes = Path(params.output).suffixes
    if ".gdb" in suffixes and TARGET_ARCGIS_VERSION not in "".join(options):
        response.append(f"{TARGET_ARCGIS_VERSION}ARCGIS_PRO_3_2_OR_LATER")
    if ".parquet" in suffixes and COMPRESSION not in "".join(options):
        response.append(f"{COMPRESSION}ZSTD")
    if ".shp" in suffixes and ENCODING not in "".join(options):
        response.append(f"{ENCODING}UTF-8")
    return response


async def create_sozip(input_path: Path, output_path: Path) -> Path:
    """Zip a folder."""
    output_zip = output_path.with_suffix(output_path.suffix + ".zip")
    sozip = await create_subprocess_exec(
        *["gdal", "vsi", "sozip", "create"],
        *[input_path, output_zip],
        *["--no-paths", "--quiet", "--recursive"],
    )
    await sozip.wait()
    rmtree(input_path)
    return output_zip


async def download_resource(tmp_dir: Path, resource_id: str) -> str:
    """Get the download URL for a resource."""
    async with AsyncClient(http2=True, follow_redirects=True) as client:
        r = await client.get(f"{HDX_URL}/api/3/action/resource_show?id={resource_id}")
        download_url = r.json()["result"]["download_url"]
        input_file = tmp_dir / download_url.split("/")[-1]
        with input_file.open("wb") as f:
            async with client.stream("GET", download_url) as r:
                r.raise_for_status()
                async for chunk in r.aiter_bytes():
                    f.write(chunk)
        if input_file.suffix == ".zip":
            unpack_archive(input_file, tmp_dir)
            input_file.unlink()
            return str(input_file.with_suffix(""))
        return str(input_file)


def get_options(params: VectorModel) -> list[str]:
    """Format the options."""
    options = []
    for opt_name in params.model_fields_set:
        opt = getattr(params, opt_name)
        if isinstance(opt, list):
            options.extend([f"--{opt_name.replace('_', '-')}={x}" for x in opt])
        else:
            options.append(f"--{opt_name.replace('_', '-')}={opt}")
    return add_default_options(options, params)


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
