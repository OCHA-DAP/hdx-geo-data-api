import logging
from json import loads
from pathlib import Path

from fastapi import HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from httpx import HTTPStatusError

from ..models import Info, VectorFile
from ..utils import (
    download_resource,
    get_options,
    get_output_path,
    run_command_and_check,
)

logger = logging.getLogger(__name__)

COMPRESSION = "--layer-creation-option=COMPRESSION="
COMPRESSION_LEVEL = "--layer-creation-option=COMPRESSION_LEVEL="
ENCODING = "--layer-creation-option=ENCODING="
TARGET_ARCGIS_VERSION = "--layer-creation-option=TARGET_ARCGIS_VERSION="


def add_default_options(options: list[str], params: VectorFile) -> list[str]:
    """Add default options."""
    response = [*options]
    suffixes = Path(params.output).suffixes
    output_format = params.output_format
    if (
        ".gdb" in suffixes or output_format == "OpenFileGDB"
    ) and TARGET_ARCGIS_VERSION not in "".join(options):
        response.append(f"{TARGET_ARCGIS_VERSION}ARCGIS_PRO_3_2_OR_LATER")
    if ".parquet" in suffixes or output_format == "Parquet":
        if COMPRESSION not in "".join(options):
            response.append(f"{COMPRESSION}ZSTD")
        if COMPRESSION_LEVEL not in "".join(options):
            response.append(f"{COMPRESSION_LEVEL}15")
    if (
        ".shp" in suffixes or output_format == "ESRI Shapefile"
    ) and ENCODING not in "".join(options):
        response.append(f"{ENCODING}UTF-8")
    return response


async def vector_json(tmp: Path, params: Info, command: str) -> JSONResponse:
    """Endpoint to convert a vector file to another format."""
    input_path = tmp / "input"
    input_path.mkdir()
    try:
        params.input = await download_resource(input_path, params.input)
    except HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
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


async def vector_file(tmp: Path, params: VectorFile, command: str) -> FileResponse:
    """Endpoint to convert a vector file to another format."""
    input_path = tmp / "input"
    input_path.mkdir()
    output_path = tmp / "output" / params.output
    output_path.parent.mkdir()
    params.output = str(output_path)
    try:
        params.input = await download_resource(input_path, params.input)
    except HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    options = get_options(params)
    options = add_default_options(options, params)
    cmd = ["gdal", "vector", command, *options]
    try:
        await run_command_and_check(cmd)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    try:
        output_path = await get_output_path(output_path)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    return FileResponse(output_path, filename=output_path.name)
