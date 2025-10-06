from asyncio import create_subprocess_exec
from collections.abc import AsyncGenerator
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID

from fastapi import HTTPException, status
from httpx import AsyncClient

from .config import HDX_URL
from .models import ConvertModel, FilterModel, VectorModel

TARGET_ARCGIS_VERSION = "--layer-creation-option=TARGET_ARCGIS_VERSION="
COMPRESSION = "--layer-creation-option=COMPRESSION="
ENCODING = "--layer-creation-option=ENCODING="


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


async def get_download_url(resource_id: UUID) -> str:
    """Get the download URL for a resource."""
    async with AsyncClient(http2=True) as client:
        r = await client.get(f"{HDX_URL}/api/3/action/resource_show?id={resource_id}")
        return r.json()["result"]["download_url"]


def get_options(opts: VectorModel) -> list[str]:  # noqa: C901, PLR0912
    """Format the options."""
    suffixes = Path(opts.output).suffixes
    options = []
    if opts.config:
        options.extend([f"--config={x}" for x in opts.config])
    if opts.input_format:
        options.extend([f"--input-format={x}" for x in opts.input_format])
    if opts.output_format:
        options.append(f"--output-format={opts.output_format}")
    if opts.output_layer:
        options.append(f"--output-layer={opts.output_layer}")
    if opts.open_option:
        options.extend([f"--open-option={x}" for x in opts.open_option])
    if opts.creation_option:
        options.extend(
            [f"--creation-option={x}" for x in opts.creation_option],
        )
    if opts.layer_creation_option:
        options.extend(
            [f"--layer-creation-option={x}" for x in opts.layer_creation_option],
        )
    if isinstance(opts, ConvertModel) and opts.input_layer:
        options.extend([f"--input-layer={x}" for x in opts.input_layer])
    if isinstance(opts, FilterModel) and opts.active_layer:
        options.append(f"--active-layer={opts.active_layer}")
    if isinstance(opts, FilterModel) and opts.where:
        options.append(f"--where={opts.where}")
    if isinstance(opts, FilterModel) and opts.bbox:
        options.append(f"--bbox={opts.bbox}")
    if ".gdb" in suffixes and TARGET_ARCGIS_VERSION not in "".join(options):
        options.append(f"{TARGET_ARCGIS_VERSION}ARCGIS_PRO_3_2_OR_LATER")
    if ".parquet" in suffixes and COMPRESSION not in "".join(options):
        options.append(f"{COMPRESSION}ZSTD")
    if ".shp" in suffixes and ENCODING not in "".join(options):
        options.append(f"{ENCODING}UTF-8")
    return options


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
