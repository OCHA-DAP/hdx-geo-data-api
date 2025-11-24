import logging
from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from collections.abc import AsyncGenerator
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from httpx import AsyncClient
from pydantic import BaseModel

from .config import HDX_URL, TIMEOUT

logger = logging.getLogger(__name__)

SEGMENTATION_FAULT = -11


async def create_sozip(input_path: Path, output_path: Path) -> Path:
    """Zip a folder."""
    output_zip = output_path.with_suffix(output_path.suffix + ".zip")
    sozip = await create_subprocess_exec(
        *["gdal", "vsi", "sozip", "create"],
        *[input_path, output_zip],
        *["--no-paths", "--quiet", "--recursive"],
    )
    await sozip.wait()
    return output_zip


async def download_resource(tmp_dir: Path, resource_id: str) -> str:
    """Get the download URL for a resource."""
    async with AsyncClient(
        http2=True,
        timeout=TIMEOUT,
        follow_redirects=True,
    ) as client:
        r = await client.get(f"{HDX_URL}/api/3/action/resource_show?id={resource_id}")
        download_url = r.json()["result"]["download_url"]
        input_file = tmp_dir / download_url.split("/")[-1]
        with input_file.open("wb") as f:
            async with client.stream("GET", download_url) as r:
                r.raise_for_status()
                async for chunk in r.aiter_bytes():
                    f.write(chunk)
        if input_file.suffix == ".zip":
            unzip_dir = input_file.with_suffix("")
            unzip_flat(input_file, unzip_dir)
            return str(unzip_dir)
        return str(input_file)


def get_options(params: BaseModel) -> list[str]:
    """Format the options."""
    options = []
    for opt_name in params.model_fields_set:
        cli_name = opt_name.replace("_", "-")
        value = getattr(params, opt_name)
        if isinstance(value, list):
            options.extend([f"--{cli_name}={x}" for x in value])
        elif isinstance(value, bool) and value:
            options.append(f"--{cli_name}")
        else:
            options.append(f"--{cli_name}={value}")
    return options


async def get_output_path(output_path: Path) -> Path:
    """Get the output path."""
    if output_path.stat().st_size == 0:
        error = "Output file does not exist."
        logger.error(error)
        raise RuntimeError(error)
    if output_path.is_dir():
        output_path = await create_sozip(output_path, output_path)
    elif len(list(output_path.parent.glob("*"))) > 1:
        output_path = await create_sozip(output_path.parent, output_path)
    return output_path


async def get_temp_dir() -> AsyncGenerator[Path]:
    """Get a temporary directory."""
    temp_dir = TemporaryDirectory()
    yield Path(temp_dir.name)


async def run_command_and_check(cmd: list[str]) -> str:
    """Execute a command, captures stdout, and raises a detailed Exception."""
    proc = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
    stdout_data, stderr_data = await proc.communicate()
    stdout_str = stdout_data.decode().strip()
    stderr_str = stderr_data.decode().strip()
    if proc.returncode != 0:
        if proc.returncode == SEGMENTATION_FAULT and not stderr_str:
            stderr_str = "segmentation fault"
        error = (
            f"Command failed with exit code: {proc.returncode}. "
            f"Command: {' '.join(cmd)}. "
            f"Stderr: {stderr_str}"
        )
        logger.error(error)
        raise RuntimeError(error)
    return stdout_str


def unzip_flat(input_file: Path, output_dir: Path) -> None:
    """Unzip a file to a flat directory."""
    with ZipFile(input_file) as z:
        for member in z.infolist():
            if Path(member.filename).name:
                member.filename = Path(member.filename).name
                z.extract(member=member, path=output_dir)
