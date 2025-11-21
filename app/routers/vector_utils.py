import logging
from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from json import loads
from pathlib import Path

from fastapi import HTTPException, status
from fastapi.responses import FileResponse, JSONResponse

from ..models import InfoModel, VectorFileModel
from ..utils import download_resource, get_options, get_output_path

logger = logging.getLogger(__name__)


async def run_command_and_check(cmd: list[str]) -> str:
    """Execute a command, captures stdout, and raises a detailed Exception."""
    proc = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
    stdout_data, stderr_data = await proc.communicate()
    stdout_str = stdout_data.decode().strip()
    stderr_str = stderr_data.decode().strip()
    if proc.returncode != 0:
        error = (
            f"Command failed with exit code: {proc.returncode}. "
            f"Command: {' '.join(cmd)}. "
            f"Stderr: {stderr_str}"
        )
        logger.error(error)
        raise RuntimeError(error)
    return stdout_str


async def vector_json(tmp: Path, params: InfoModel, command: str) -> JSONResponse:
    """Endpoint to convert a vector file to another format."""
    input_path = tmp / "input"
    input_path.mkdir()
    params.input = await download_resource(input_path, params.input)
    options = get_options(params)
    cmd = ["gdal", "vector", command, "--output-format=json", *options]
    try:
        stdout_string = await run_command_and_check(cmd)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    return JSONResponse(loads(stdout_string))


async def vector_file(tmp: Path, params: VectorFileModel, command: str) -> FileResponse:
    """Endpoint to convert a vector file to another format."""
    input_path = tmp / "input"
    input_path.mkdir()
    output_path = tmp / "output" / params.output
    output_path.parent.mkdir()
    params.output = str(output_path)
    params.input = await download_resource(input_path, params.input)
    options = get_options(params)
    cmd = ["gdal", "vector", command, *options]
    try:
        await run_command_and_check(cmd)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    output_path = await get_output_path(output_path)
    return FileResponse(output_path, filename=output_path.name)
