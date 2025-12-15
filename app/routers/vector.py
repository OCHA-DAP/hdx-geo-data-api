import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse, JSONResponse

from .. import models
from ..auth import get_api_key
from ..utils import get_temp_dir
from .vector_utils import vector_file, vector_json

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Vector Commands"], dependencies=[Depends(get_api_key)])


@router.get("/vector/convert")
async def vector_convert(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    params: Annotated[models.Convert, Query()],
) -> FileResponse:
    """Convert a vector dataset to another format.

    [Original documentation](https://gdal.org/en/stable/programs/gdal_vector_convert.html)
    """
    return await vector_file(tmp_dir, params, "convert")


@router.get("/vector/filter")
async def vector_filter(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    params: Annotated[models.Filter, Query()],
) -> FileResponse:
    """Filter a vector dataset with a spatial extent (bbox) or a SQL WHERE clause.

    [Original documentation](https://gdal.org/en/stable/programs/gdal_vector_filter.html)
    """
    return await vector_file(tmp_dir, params, "filter")


@router.get("/vector/info")
async def vector_info(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    params: Annotated[models.Info, Query()],
) -> JSONResponse:
    """Return various information about a GDAL supported vector dataset.

    [Original documentation](https://gdal.org/en/stable/programs/gdal_vector_info.html)
    """
    return await vector_json(tmp_dir, params, "info")


@router.get("/vector/simplify")
async def vector_simplify(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    params: Annotated[models.Simplify, Query()],
) -> FileResponse:
    """Simplify geometries of a vector dataset (for lines and polygons).

    Ensures that the result is a valid geometry having the same dimension and number of
    components as the input.

    The simplification uses a maximum distance difference algorithm similar to the one
    used in the Douglas-Peucker algorithm.

    This done by a method which preserves the topology per feature, but not for a whole
    layer. Thus gaps or overlaps between geometries that were initially contiguous may
    happen. To perform simplification that preserves shared boundaries between
    geometries, see [gdal vector simplify-coverage](https://gdal.org/en/stable/programs/gdal_vector_simplify_coverage.html).

    [Original documentation](https://gdal.org/en/stable/programs/gdal_vector_simplify.html)
    """
    return await vector_file(tmp_dir, params, "simplify")


@router.get("/vector/simplify-coverage")
async def vector_simplify_coverage(
    tmp_dir: Annotated[Path, Depends(get_temp_dir)],
    params: Annotated[models.SimplifyCoverage, Query()],
) -> FileResponse:
    """Simplify boundaries of a polygonal vector dataset (will give errors for lines).

    Shared boundaries are preserved without introducing gaps or overlaps between
    features. Gaps or overlaps already present in the input dataset will not be
    corrected.

    This requires loading the entire dataset into memory at once. If preservation of
    shared boundaries is not needed, [gdal vector simplify](https://gdal.org/en/stable/programs/gdal_vector_simplify.html)
    provides an alternative that can process geometries in a streaming manner.

    Simplification is performed using the Visvalingam-Whyatt algorithm.

    [Original documentation](https://gdal.org/en/stable/programs/gdal_vector_simplify_coverage.html)
    """
    return await vector_file(tmp_dir, params, "simplify-coverage")
