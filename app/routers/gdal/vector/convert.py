from asyncio import create_subprocess_exec
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from ....config import VECTOR_COMMANDS
from ....utils import get_download_url, get_temp_dir

router = APIRouter()


@router.get(
    "/gdal/vector/convert/{resource_id}/{output_name}",
    description="gdal vector convert",
    tags=[VECTOR_COMMANDS],
)
async def main(
    resource_id: str,
    output_name: str,
    temp_dir: Annotated[Path, Depends(get_temp_dir)],
) -> FileResponse:
    """Endpoint to convert a vector file to another format."""
    download_url = get_download_url(resource_id)
    output_path = temp_dir / output_name
    gdal = await create_subprocess_exec(
        *["gdal", "vector", "convert"],
        *[download_url, output_path],
    )
    await gdal.wait()
    if output_path.stat().st_size == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unprocessable Content",
        )
    return FileResponse(output_path, filename=output_path.name)
