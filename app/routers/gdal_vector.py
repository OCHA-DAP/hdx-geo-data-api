from asyncio import create_subprocess_exec
from pathlib import Path
from typing import Annotated
from venv import logger

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse

from ..models import ConvertModel, FilterModel, SimplifyModel, VectorModel
from ..utils import get_download_url, get_options, get_output_path, get_temp_dir

router = APIRouter(tags=["Vector Commands"])


async def gdal_vector(tmp: Path, params: VectorModel, cmds: list[str]) -> FileResponse:
    """Endpoint to convert a vector file to another format."""
    output_path = tmp / params.output
    params.output = str(output_path)
    params.input = await get_download_url(params.input)
    options = get_options(params)
    cmd = ["gdal", "vector", *cmds, *options]
    logger.info(f"Running command: {' '.join(cmd)}")
    proc = await create_subprocess_exec(*cmd)
    await proc.wait()
    output_path = await get_output_path(output_path)
    return FileResponse(output_path, filename=output_path.name)


@router.get("/gdal/vector/convert")
async def gdal_vector_convert(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    params: Annotated[ConvertModel, Query()],
) -> FileResponse:
    """Endpoint to convert a vector file to another format."""
    return await gdal_vector(tmp_dir, params, ["convert"])


@router.get("/gdal/vector/geom/simplify")
async def gdal_vector_geom_simplify(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    params: Annotated[SimplifyModel, Query()],
) -> FileResponse:
    """Endpoint to filter a vector file to another format."""
    return await gdal_vector(tmp_dir, params, ["geom", "simplify"])


@router.get("/gdal/vector/filter")
async def gdal_vector_filter(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    params: Annotated[FilterModel, Query()],
) -> FileResponse:
    """Endpoint to filter a vector file to another format."""
    return await gdal_vector(tmp_dir, params, ["filter"])
