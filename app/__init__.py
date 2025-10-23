from fastapi import FastAPI

from .config import DOCS_URL, OPENAPI_URL, PREFIX, REDOC_URL
from .routers import gdal_vector, health

routers = [health, gdal_vector]

app = FastAPI(
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
    openapi_url=OPENAPI_URL,
)

for router in routers:
    app.include_router(router.router, prefix=f"{PREFIX}")
