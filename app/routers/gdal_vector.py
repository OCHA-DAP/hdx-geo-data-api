from asyncio import create_subprocess_exec
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse

from ..models import ConvertModel, FilterModel, SimplifyModel, VectorModel
from ..utils import get_download_url, get_options, get_output_path, get_temp_dir

router = APIRouter(tags=["Vector Commands"])


async def gdal_vector(tmp: Path, opts: VectorModel, cmds: list[str]) -> FileResponse:
    """Endpoint to convert a vector file to another format."""
    download_url = await get_download_url(opts.input)
    output_path = tmp / opts.output
    options = get_options(opts)
    cmd = ["gdal", "vector", *cmds, download_url, output_path, *options]
    proc = await create_subprocess_exec(*cmd)
    await proc.wait()
    output_path = await get_output_path(output_path)
    return FileResponse(output_path, filename=output_path.name)


@router.get("/gdal/vector/convert")
async def gdal_vector_convert(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    opts: Annotated[ConvertModel, Query()],
) -> FileResponse:
    """Endpoint to convert a vector file to another format."""
    return await gdal_vector(tmp_dir, opts, ["convert"])


@router.get("/gdal/vector/geom/simplify")
async def gdal_vector_geom_simplify(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    opts: Annotated[SimplifyModel, Query()],
) -> FileResponse:
    """Endpoint to filter a vector file to another format."""
    return await gdal_vector(tmp_dir, opts, ["geom", "simplify"])


@router.get("/gdal/vector/filter")
async def gdal_vector_filter(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    opts: Annotated[FilterModel, Query()],
) -> FileResponse:
    """Endpoint to filter a vector file to another format."""
    return await gdal_vector(tmp_dir, opts, ["filter"])
