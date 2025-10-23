from fastapi import FastAPI

from .config import DOCS_PREFIX, PREFIX, REDOC_PREFIX
from .routers import gdal_vector, health

routers = [health, gdal_vector]

app = FastAPI(
    docs_url=DOCS_PREFIX,
    REDOC_PREFIX=REDOC_PREFIX,
)

for router in routers:
    app.include_router(router.router, prefix=f"{PREFIX}")
