import logging
from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from collections.abc import AsyncGenerator
from pathlib import Path
from re import IGNORECASE, findall, search
from tempfile import TemporaryDirectory
from zipfile import ZipFile, is_zipfile

from httpx import AsyncClient
from pydantic import BaseModel
from ua_generator import generate as ua_generate

from .config import HDX_URL, TIMEOUT

logger = logging.getLogger(__name__)


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


async def get_filename(client: AsyncClient, download_url: str) -> str:
    """Get the filename from the response headers."""
    r = await client.head(download_url)
    content_disposition = r.headers.get("Content-Disposition")
    if content_disposition:
        filename_match = search(r'filename="?([^"]+)"?', content_disposition)
        if filename_match:
            return filename_match.group(1)
    return download_url.split("/")[-1]


async def download_resource(tmp_dir: Path, resource_id: str) -> str:
    """Get the download URL for a resource."""
    async with AsyncClient(
        http2=True,
        timeout=TIMEOUT,
        follow_redirects=True,
    ) as client:
        input_path = tmp_dir / "input"
        input_path.mkdir()
        uuid = get_last_uuid_v4(resource_id)
        r1 = await client.get(f"{HDX_URL}/api/3/action/resource_show?id={uuid}")
        r1.raise_for_status()
        download_url = r1.json()["result"]["download_url"]
        filename = await get_filename(client, download_url)
        input_file = input_path / filename
        with input_file.open("wb") as f:
            headers = ua_generate().headers.get()
            async with client.stream("GET", download_url, headers=headers) as r2:
                r2.raise_for_status()
                async for chunk in r2.aiter_bytes():
                    f.write(chunk)
        if is_zipfile(input_file):
            unzip_dir = tmp_dir / "unzip"
            unzip_dir.mkdir()
            unzip_flat(input_file, unzip_dir)
            return str(unzip_dir)
        return str(input_file)


def get_last_uuid_v4(text: str) -> str | None:
    """Find and returns the last instance of a UUID v4 string in the given text."""
    uuid_v4_pattern = (
        r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"
    )
    all_matches = findall(uuid_v4_pattern, text, IGNORECASE)
    if all_matches:
        return all_matches[-1]
    return None


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
    segmentation_fault = -11
    proc = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
    stdout_data, stderr_data = await proc.communicate()
    stdout_str = stdout_data.decode().strip()
    stderr_str = stderr_data.decode().strip()
    if proc.returncode != 0:
        if proc.returncode == segmentation_fault and not stderr_str:
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
