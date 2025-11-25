import logging
from json import loads
from pathlib import Path

from content_types import get_content_type
from fastapi import HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from httpx import HTTPStatusError
from magic import from_file as magic_from_file

from ..models import Info, VectorFile
from ..utils import (
    download_resource,
    get_options,
    get_output_path,
    run_command_and_check,
)

logger = logging.getLogger(__name__)


def add_default_options(options: list[str], params: VectorFile) -> list[str]:
    """Add default options."""
    compression = "--layer-creation-option=COMPRESSION="
    compression_level = "--layer-creation-option=COMPRESSION_LEVEL="
    encoding = "--layer-creation-option=ENCODING="
    target_arcgis_version = "--layer-creation-option=TARGET_ARCGIS_VERSION="
    response = [*options]
    suffixes = Path(params.output).suffixes
    output_format = params.output_format
    if (
        ".gdb" in suffixes or output_format == "OpenFileGDB"
    ) and target_arcgis_version not in "".join(options):
        response.append(f"{target_arcgis_version}ARCGIS_PRO_3_2_OR_LATER")
    if ".parquet" in suffixes or output_format == "Parquet":
        if compression not in "".join(options):
            response.append(f"{compression}ZSTD")
        if compression_level not in "".join(options):
            response.append(f"{compression_level}15")
    if (
        ".shp" in suffixes or output_format == "ESRI Shapefile"
    ) and encoding not in "".join(options):
        response.append(f"{encoding}UTF-8")
    return response


def get_media_type(output_path: Path) -> str:
    """Get the media type of a file."""
    geo_content_types = {
        ".fgb": "application/flatgeobuf",
        ".geojson": "application/geo+json",
        ".gpx": "application/gpx+xml",
        ".kml": "application/vnd.google-earth.kml+xml",
        ".kmz": "application/vnd.google-earth.kmz",
    }
    media_type = get_content_type(output_path)
    if media_type == "application/octet-stream":
        media_type = geo_content_types.get(
            output_path.suffix,
            "application/octet-stream",
        )
    if media_type == "application/octet-stream":
        media_type = magic_from_file(output_path, mime=True)
    return media_type


async def vector_json(tmp: Path, params: Info, command: str) -> JSONResponse:
    """Endpoint to convert a vector file to another format."""
    try:
        params.input = await download_resource(tmp, params.input)
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
    output_path = tmp / "output" / params.output
    output_path.parent.mkdir()
    params.output = str(output_path)
    try:
        params.input = await download_resource(tmp, params.input)
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
    media_type = get_media_type(output_path)
    return FileResponse(output_path, media_type=media_type, filename=output_path.name)
