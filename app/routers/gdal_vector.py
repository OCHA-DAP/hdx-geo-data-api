import logging
from asyncio import create_subprocess_exec
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse

from ..auth import get_api_key
from ..models import ConvertModel, FilterModel, SimplifyModel, VectorModel
from ..utils import download_resource, get_options, get_output_path, get_temp_dir

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Vector Commands"], dependencies=[Depends(get_api_key)])


async def gdal_vector(tmp: Path, params: VectorModel, command: str) -> FileResponse:
    """Endpoint to convert a vector file to another format."""
    input_path = tmp / "input"
    input_path.mkdir()
    output_path = tmp / "output" / params.output
    output_path.parent.mkdir()
    params.output = str(output_path)
    params.input = await download_resource(input_path, params.input)
    options = get_options(params)
    cmd = ["gdal", "vector", command, "--quiet", *options]
    logger.info("Running command: %s", " ".join(cmd))
    proc = await create_subprocess_exec(*cmd)
    await proc.wait()
    output_path = await get_output_path(output_path)
    return FileResponse(output_path, filename=output_path.name)


@router.get("/gdal/vector/convert")
async def gdal_vector_convert(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    params: Annotated[ConvertModel, Query()],
) -> FileResponse:
    """Convert to another format."""
    return await gdal_vector(tmp_dir, params, "convert")


@router.get("/gdal/vector/simplify-coverage")
async def gdal_vector_geom_simplify(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    params: Annotated[SimplifyModel, Query()],
) -> FileResponse:
    """Simplify coverage geometry (maintains topology)."""
    return await gdal_vector(tmp_dir, params, "simplify-coverage")


@router.get("/gdal/vector/filter")
async def gdal_vector_filter(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    params: Annotated[FilterModel, Query()],
) -> FileResponse:
    """Filter by bbox or attribute."""
    return await gdal_vector(tmp_dir, params, "filter")
