import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse, JSONResponse

from ..auth import get_api_key
from ..models import ConvertModel, FilterModel, InfoModel, SimplifyModel
from ..utils import get_temp_dir
from .vector_utils import vector_file, vector_json

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Vector Commands"], dependencies=[Depends(get_api_key)])


@router.get("/vector/convert")
async def vector_convert(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    params: Annotated[ConvertModel, Query()],
) -> FileResponse:
    """Convert to another format."""
    return await vector_file(tmp_dir, params, "convert")


@router.get("/vector/filter")
async def vector_filter(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    params: Annotated[FilterModel, Query()],
) -> FileResponse:
    """Filter by bbox or attribute."""
    return await vector_file(tmp_dir, params, "filter")


@router.get("/vector/info")
async def vector_info(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    params: Annotated[InfoModel, Query()],
) -> JSONResponse:
    """Convert to another format."""
    return await vector_json(tmp_dir, params, "info")


@router.get("/vector/simplify-coverage")
async def vector_geom_simplify(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    params: Annotated[SimplifyModel, Query()],
) -> FileResponse:
    """Simplify coverage geometry (maintains topology)."""
    return await vector_file(tmp_dir, params, "simplify-coverage")
